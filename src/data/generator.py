import argparse
import os
import random
import sys
from typing import Dict, List

import pandas as pd
from tqdm import tqdm

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from augmentation import (  # noqa: E402
    OptionalAugmenters,
    Paraphraser,
    add_social_flavor,
    normalize_elongation,
    synonym_replace,
)
from config import load_config  # noqa: E402
from paths import ensure_dirs  # noqa: E402

SENTIMENTS = ["positive", "negative", "neutral"]

EN_TOPICS = [
    "the product", "the service", "the app", "the delivery", "the restaurant",
    "the movie", "the news", "the article", "the customer support",
    "the university course", "the phone", "the laptop", "the hotel",
    "the online store", "the subscription", "the update",
]

AR_TOPICS_FUSHA = [
    "المنتج", "الخدمة", "التطبيق", "التوصيل", "المطعم", "الفيلم", "الخبر",
    "المقال", "خدمة العملاء", "المقرر الجامعي", "الهاتف", "الحاسوب المحمول",
    "الفندق", "المتجر الإلكتروني", "الاشتراك", "التحديث",
]

AR_TOPICS_SHAMI = [
    "المنتج", "الخدمة", "الابليكيشن", "التوصيل", "المطعم", "الفيلم", "الخبر",
    "المقال", "الدعم", "المادة", "الموبايل", "اللابتوب", "الفندق",
    "المتجر أونلاين", "الاشتراك", "الابديت",
]

EN_POS = [
    "I genuinely loved {topic}; it exceeded my expectations.",
    "{topic} is awesome, smooth, and surprisingly reliable.",
    "Honestly, great experience with {topic}. Would recommend.",
    "This is exactly what I needed. {topic} is fantastic.",
    "So happy with {topic} 😊",
    "I love {topic}. It just works.",
    "Very impressed by {topic}; the quality is top-notch.",
]

EN_NEG = [
    "I regret trying {topic}; it was disappointing.",
    "{topic} is frustrating and poorly designed.",
    "Terrible experience with {topic}. Not worth it.",
    "I expected better, but {topic} failed in basic ways.",
    "This is so bad... {topic} 😤",
    "I hate how {topic} keeps breaking.",
    "{topic} wasted my time and money.",
]

EN_NEU = [
    "{topic} works as described, nothing more and nothing less.",
    "I tried {topic} today; the results were average.",
    "Overall, {topic} is okay. It meets the minimum requirements.",
    "I have mixed feelings about {topic}; it depends on what you need.",
    "Just sharing: I used {topic} this week.",
    "No strong opinion on {topic} yet.",
    "{topic} is neither great nor terrible for me.",
]

EN_SOCIAL = [
    "tbh {topic} is {adj}.",
    "ngl, {topic} is {adj} right now.",
    "IMO {topic} is {adj}...",
    "Just tried {topic}. {adj} experience.",
    "Hot take: {topic} is {adj}.",
]

EN_ADJ = {
    "positive": ["great", "awesome", "amazing", "solid", "perfect"],
    "negative": ["bad", "terrible", "frustrating", "awful", "overhyped"],
    "neutral": ["okay", "average", "fine", "mixed", "decent"],
}

FUSHA_POS = [
    "أعجبني {topic} كثيرًا، وكان الأداء ممتازًا.",
    "تجربتي مع {topic} كانت رائعة ومريحة.",
    "أشعر بالرضا عن {topic}، وأنصح به.",
    "{topic} متميز ويقدم قيمة واضحة.",
    "بصراحة {topic} ممتاز 😊",
    "أحببت {topic}، وقد فاق توقعاتي.",
    "أداء {topic} قوي وثابت بشكل ملحوظ.",
]

FUSHA_NEG = [
    "لم تعجبني تجربة {topic}، وكانت مخيبة للآمال.",
    "{topic} سيئ ويعاني من مشكلات واضحة.",
    "الخدمة المتعلقة بـ {topic} لم تكن بالمستوى المطلوب.",
    "توقعاتي كانت أعلى، لكن {topic} لم يلبِّها.",
    "للأسف {topic} مزعج 😤",
    "لا أحب {topic} بسبب كثرة المشكلات.",
    "{topic} لم يقدم قيمة مقابل ما دُفع فيه.",
]

FUSHA_NEU = [
    "{topic} يعمل بشكل مقبول وفقًا للوصف.",
    "جربت {topic} اليوم وكانت النتائج متوسطة.",
    "بشكل عام {topic} عادي ولا يختلف كثيرًا.",
    "تجربتي مع {topic} كانت متوازنة بلا انطباع قوي.",
    "ملاحظة: استخدمت {topic} هذا الأسبوع.",
    "لا أملك رأيًا حاسمًا حول {topic} حتى الآن.",
]

SHAMI_POS = [
    "عنجد {topic} كتير حلو وريحني.",
    "تجربتي مع {topic} كانت تمام، مبسوط.",
    "{topic} رائع بصراحة وبيستاهل.",
    "كتير انبسطت بـ {topic} 😊",
    "هاد {topic} منيح كتير!",
    "بحس {topic} ممتاز وخلصت من وجعة الراس.",
]

SHAMI_NEG = [
    "مو معقول قديش {topic} سيّئ.",
    "{topic} مو منيح أبدًا وبيضيع الوقت.",
    "عنجد تجربة {topic} بتقهر.",
    "{topic} مزعج ومش عملي 😤",
    "صراحة ندمت على {topic}.",
    "{topic} مو طبيعي قديش بخزي.",
]

SHAMI_NEU = [
    "{topic} عادي، لا هو خارق ولا سيّئ.",
    "جربت {topic} اليوم، الوضع متوسط.",
    "هيك يعني {topic} بيمشي الحال.",
    "عم جرّب {topic} هالأيام، لسا عم قيّم.",
    "بس للتوضيح: استخدمت {topic} هالأسبوع.",
    "لسا ما قررت شو رأيي بـ {topic}.",
]

FUSHA_SOCIAL = [
    "بصراحة، {topic} كان {adj}.",
    "رأيي الشخصي: {topic} {adj} حتى الآن.",
    "تحديث سريع: {topic} {adj}.",
]

SHAMI_SOCIAL = [
    "عنجد {topic} {adj}.",
    "شو هالحكي! {topic} {adj}.",
    "يعني بصراحة {topic} {adj}.",
    "هلق جرّبت {topic}… {adj}.",
]

AR_ADJ_FUSHA = {
    "positive": ["ممتاز", "رائع", "مفيد", "متميز"],
    "negative": ["سيئ", "مزعج", "مخيب", "غير جيد"],
    "neutral": ["عادي", "متوسط", "مقبول"],
}

AR_ADJ_SHAMI = {
    "positive": ["كتير منيح", "تمام", "حلو", "بيرفكت"],
    "negative": ["مو منيح", "سيّئ", "بخزي", "مقرف"],
    "neutral": ["عادي", "نص نص", "بيمشي الحال"],
}


def _pick_template(lang: str, sentiment: str) -> str:
    if lang == "en":
        if random.random() < 0.25:
            return random.choice(EN_SOCIAL)
        return random.choice({"positive": EN_POS, "negative": EN_NEG, "neutral": EN_NEU}[sentiment])
    if lang == "ar_fusha":
        if random.random() < 0.25:
            return random.choice(FUSHA_SOCIAL)
        return random.choice({"positive": FUSHA_POS, "negative": FUSHA_NEG, "neutral": FUSHA_NEU}[sentiment])
    if random.random() < 0.25:
        return random.choice(SHAMI_SOCIAL)
    return random.choice({"positive": SHAMI_POS, "negative": SHAMI_NEG, "neutral": SHAMI_NEU}[sentiment])


def _pick_topic(lang: str) -> str:
    if lang == "en":
        return random.choice(EN_TOPICS)
    if lang == "ar_fusha":
        return random.choice(AR_TOPICS_FUSHA)
    return random.choice(AR_TOPICS_SHAMI)


def _fill_social_placeholders(template: str, lang: str, sentiment: str, topic: str) -> str:
    if "{adj}" not in template:
        return template.format(topic=topic)

    if lang == "en":
        adj = random.choice(EN_ADJ[sentiment])
    elif lang == "ar_fusha":
        adj = random.choice(AR_ADJ_FUSHA[sentiment])
    else:
        adj = random.choice(AR_ADJ_SHAMI[sentiment])

    return template.format(topic=topic, adj=adj)


def _maybe_make_long(text: str, lang: str, sentiment: str) -> str:
    if random.random() > 0.30:
        return text

    extra = []
    for _ in range(random.randint(1, 3)):
        template = _pick_template(lang, sentiment)
        topic = _pick_topic(lang)
        extra.append(_fill_social_placeholders(template, lang, sentiment, topic))

    if lang == "en":
        return " ".join([text] + extra + ["Overall, that was my experience."])
    if lang == "ar_fusha":
        return " ".join([text] + extra + ["بشكل عام، هذا ملخص تجربتي."])
    return " ".join([text] + extra + ["بالنهاية، هيك كانت تجربتي."])


def generate_dataset(
    target_counts: Dict[str, int],
    paraphraser: Paraphraser,
    paraphrase_prob: float,
    synonym_replace_prob: float,
    social_prob: float,
) -> pd.DataFrame:
    rows: List[Dict[str, str]] = []

    for lang, n_lang in target_counts.items():
        per_sent = n_lang // 3
        remainder = n_lang - 3 * per_sent
        counts = {"positive": per_sent, "negative": per_sent, "neutral": per_sent}
        for sentiment in SENTIMENTS[:remainder]:
            counts[sentiment] += 1

        for sentiment, n in counts.items():
            for _ in tqdm(range(n), desc=f"{lang}:{sentiment}"):
                template = _pick_template(lang, sentiment)
                topic = _pick_topic(lang)
                text = _fill_social_placeholders(template, lang, sentiment, topic)
                text = _maybe_make_long(text, lang, sentiment)
                text = normalize_elongation(text)

                if random.random() < social_prob:
                    text = add_social_flavor(text, sentiment=sentiment, language=lang)

                if synonym_replace_prob > 0:
                    text = synonym_replace(text, language=lang, prob=float(synonym_replace_prob))

                p_paraphrase = float(paraphrase_prob)
                if lang != "en":
                    p_paraphrase = min(p_paraphrase, 0.08)

                if random.random() < p_paraphrase:
                    text = paraphraser.paraphrase(text, language=lang)

                rows.append({"text": text, "sentiment": sentiment, "language": lang})

    df = pd.DataFrame(rows)
    return df.sample(frac=1.0, random_state=42).reset_index(drop=True)


def run_generation(
    out_path: str,
    seed: int = 42,
    paraphrase_prob: float = 0.12,
    synonym_replace_prob: float = 0.25,
    social_prob: float = 0.65,
    use_nlpaug: bool = False,
    use_nlpaug_contextual: bool = False,
    use_transformers: bool = False,
    target_counts: Dict[str, int] | None = None,
) -> pd.DataFrame:
    random.seed(seed)
    ensure_dirs(os.path.dirname(out_path))

    cfg = OptionalAugmenters(
        use_nlpaug=use_nlpaug,
        use_nlpaug_contextual=use_nlpaug_contextual,
        use_transformers=use_transformers,
    )
    paraphraser = Paraphraser(cfg)

    effective_paraphrase_prob = float(paraphrase_prob)
    if not (cfg.use_nlpaug or cfg.use_transformers):
        effective_paraphrase_prob = 0.0

    if target_counts is None:
        config = load_config()
        target_counts = dict(config.data.get("synthetic_counts", {
            "en": 1700,
            "ar_fusha": 1700,
            "ar_shami": 1600,
        }))

    df = generate_dataset(
        target_counts,
        paraphraser=paraphraser,
        paraphrase_prob=effective_paraphrase_prob,
        synonym_replace_prob=float(synonym_replace_prob),
        social_prob=float(social_prob),
    )
    df.to_csv(out_path, index=False, encoding="utf-8")
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=str, default="data/sentiment_dataset_multilingual.csv")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--paraphrase_prob", type=float, default=0.12)
    parser.add_argument("--synonym_replace_prob", type=float, default=0.25)
    parser.add_argument("--social_prob", type=float, default=0.65)
    parser.add_argument("--use_nlpaug", action="store_true")
    parser.add_argument("--use_nlpaug_contextual", action="store_true")
    parser.add_argument("--use_transformers", action="store_true")
    args = parser.parse_args()

    out_path = args.out
    if not os.path.isabs(out_path):
        out_path = os.path.join(_ROOT, out_path)

    df = run_generation(
        out_path=out_path,
        seed=args.seed,
        paraphrase_prob=args.paraphrase_prob,
        synonym_replace_prob=args.synonym_replace_prob,
        social_prob=args.social_prob,
        use_nlpaug=bool(args.use_nlpaug),
        use_nlpaug_contextual=bool(args.use_nlpaug_contextual),
        use_transformers=bool(args.use_transformers),
    )
    print(f"Wrote {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()
