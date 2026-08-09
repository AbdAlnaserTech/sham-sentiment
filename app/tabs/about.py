"""
تبويب «حول المشروع» — عرض تقديمي لمشروع التخرج.

يُعرض في تبويب Streamlit ويحتوي:
  - بطاقة Hero مع SVG توضيحي
  - أهداف المشروع وتصنيف المشاعر
  - سير العمل والتقنيات المستخدمة
  - معلومات الجامعة والروابط
  - زر CTA للانتقال إلى «تعليق واحد»
"""

from __future__ import annotations

from typing import Any

import streamlit as st
import streamlit.components.v1 as components

# ── بلوك 1: ثوابت العرض ───────────────────────────────────────────────────
# اسم النموذج الظاهر في قسم «التقنيات المستخدمة»
MODEL_DISPLAY_NAME = "BERT · XLM-RoBERTa"

# ── بلوك 2: CSS الوضع الفاتح ──────────────────────────────────────────────
ABOUT_CSS = """
<style>
.about-wrap {
    direction: rtl;
    text-align: right;
    font-family: "Segoe UI", "Noto Sans Arabic", Tahoma, Arial, sans-serif;
    color: #0f172a;
    margin: -0.5rem 0 2rem;
}

/* ── Hero ── */
.about-hero {
    display: grid;
    grid-template-columns: 1fr minmax(220px, 340px);
    gap: 2rem;
    align-items: center;
    background: linear-gradient(135deg, #ffffff 0%, #f0f4fa 55%, #e8eef8 100%);
    border: 1px solid #d7dee8;
    border-radius: 20px;
    padding: 2.5rem 2.25rem;
    margin-bottom: 2.5rem;
    box-shadow: 0 8px 32px rgba(30, 58, 95, 0.07);
    position: relative;
    overflow: hidden;
}
.about-hero::before {
    content: "";
    position: absolute;
    top: -40%;
    left: -10%;
    width: 280px;
    height: 280px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, transparent 70%);
    pointer-events: none;
}
.about-hero-tag {
    display: inline-block;
    background: linear-gradient(90deg, #1e3a5f, #2563eb);
    color: #fff;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    padding: 5px 14px;
    border-radius: 999px;
    margin-bottom: 1rem;
}
.about-hero h2 {
    color: #1e3a5f !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    margin: 0 0 0.6rem !important;
    line-height: 1.35 !important;
}
.about-hero-sub {
    color: #2563eb;
    font-size: 1.05rem;
    font-weight: 600;
    margin: 0 0 1rem;
    line-height: 1.6;
}
.about-hero-desc {
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.85;
    margin: 0;
    max-width: 540px;
}

/* AI visual */
.about-ai-visual {
    background: #fff;
    border: 1px solid #dbeafe;
    border-radius: 16px;
    padding: 1.25rem;
    box-shadow: 0 4px 24px rgba(37, 99, 235, 0.1);
}
.about-ai-visual svg { width: 100%; height: auto; display: block; }

/* ── Section titles ── */
.about-section {
    margin-bottom: 2.75rem;
    direction: rtl;
    text-align: right;
}
.about-section-title {
    color: #1e3a5f;
    font-size: 1.35rem;
    font-weight: 800;
    margin: 0 0 0.35rem;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #2563eb;
    display: inline-block;
}
.about-section-lead {
    color: #64748b;
    font-size: 0.92rem;
    line-height: 1.85;
    margin: 1rem 0 0;
    max-width: 820px;
    direction: rtl;
    text-align: right;
    unicode-bidi: plaintext;
}
.about-section-lead strong {
    direction: rtl;
    unicode-bidi: isolate;
}

/* ── Cards grid ── */
.about-grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-top: 1.25rem;
}
.about-grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 1.25rem;
}
.about-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.35rem 1.25rem;
    box-shadow: 0 2px 14px rgba(15, 23, 42, 0.05);
    transition: box-shadow 0.2s, transform 0.2s;
}
.about-card:hover {
    box-shadow: 0 6px 24px rgba(30, 58, 95, 0.1);
    transform: translateY(-2px);
}
.about-card-icon {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    margin-bottom: 0.85rem;
}
.about-card h4 {
    color: #1e3a5f !important;
    font-size: 0.98rem !important;
    font-weight: 700 !important;
    margin: 0 0 0.45rem !important;
}
.about-card p {
    color: #64748b;
    font-size: 0.84rem;
    line-height: 1.7;
    margin: 0;
}
.about-icon-blue   { background: #eff6ff; color: #2563eb; }
.about-icon-navy   { background: #eef2f7; color: #1e3a5f; }
.about-icon-violet { background: #f5f3ff; color: #7c3aed; }
.about-icon-teal   { background: #f0fdfa; color: #0d9488; }

/* Sentiment cards */
.about-sent-pos { border-top: 3px solid #059669; }
.about-sent-neu { border-top: 3px solid #d97706; }
.about-sent-neg { border-top: 3px solid #dc2626; }
.about-sent-pos h4 { color: #059669 !important; }
.about-sent-neu h4 { color: #d97706 !important; }
.about-sent-neg h4 { color: #dc2626 !important; }
.about-sent-pos .about-card-icon { background: #ecfdf5; color: #059669; }
.about-sent-neu .about-card-icon { background: #fffbeb; color: #d97706; }
.about-sent-neg .about-card-icon { background: #fef2f2; color: #dc2626; }

/* ── Workflow ── */
.about-workflow {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: flex-start;
    direction: rtl;
    gap: 0.35rem;
    margin-top: 1.5rem;
    padding: 1.5rem 1rem;
    background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
    border: 1px solid #e2e8f0;
    border-radius: 16px;
}
.about-wf-step {
    background: #fff;
    border: 1px solid #dbeafe;
    border-radius: 10px;
    padding: 0.65rem 0.9rem;
    font-size: 0.8rem;
    font-weight: 600;
    color: #1e3a5f;
    white-space: nowrap;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.06);
    direction: rtl;
}
.about-wf-step.highlight {
    background: linear-gradient(135deg, #1e3a5f, #2563eb);
    color: #fff;
    border-color: transparent;
}
.about-wf-arrow {
    color: #94a3b8;
    font-size: 1.1rem;
    font-weight: 700;
    padding: 0 0.15rem;
    direction: rtl;
    unicode-bidi: isolate;
}

/* ── Tech badges ── */
.about-tech-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    direction: rtl;
    gap: 0.65rem;
    margin-top: 1.25rem;
}
.about-tech-badge {
    background: #fff;
    border: 1px solid #dbeafe;
    color: #1e3a5f;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 0.55rem 1.1rem;
    border-radius: 999px;
    box-shadow: 0 2px 8px rgba(30, 58, 95, 0.05);
    direction: rtl;
    unicode-bidi: isolate;
}
.about-tech-badge.latin {
    direction: ltr;
}
.about-tech-badge.model {
    background: linear-gradient(90deg, #eff6ff, #f5f3ff);
    border-color: #93c5fd;
    color: #1d4ed8;
}

/* ── Info card ── */
.about-info-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-right: 4px solid #1e3a5f;
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
    margin-top: 1rem;
}
.about-info-row {
    display: flex;
    gap: 0.75rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.88rem;
}
.about-info-row:last-child { border-bottom: none; }
.about-info-label {
    color: #64748b;
    font-weight: 600;
    min-width: 72px;
    flex-shrink: 0;
}
.about-info-value {
    color: #1e293b;
    font-weight: 700;
}

/* ── CTA ── */
.about-cta {
    text-align: center;
    background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 50%, #2563eb 100%);
    border-radius: 18px;
    padding: 2.5rem 2rem;
    margin-top: 2.5rem;
    box-shadow: 0 12px 40px rgba(30, 58, 95, 0.22);
}
.about-cta h3 {
    color: #fff !important;
    font-size: 1.45rem !important;
    font-weight: 800 !important;
    margin: 0 0 0.5rem !important;
}
.about-cta p {
    color: rgba(255,255,255,0.88);
    font-size: 0.92rem;
    margin: 0 0 1.25rem;
    line-height: 1.7;
}

@media (max-width: 960px) {
    .about-hero { grid-template-columns: 1fr; }
    .about-grid-4 { grid-template-columns: repeat(2, 1fr); }
    .about-grid-3 { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
    .about-grid-4 { grid-template-columns: 1fr; }
    .about-hero h2 { font-size: 1.55rem !important; }
    .about-wf-step { font-size: 0.72rem; padding: 0.5rem 0.65rem; }
}
</style>
"""

# ── بلوك 3: CSS الوضع الداكن (يُحقَن عند dark_mode=True) ─────────────────
ABOUT_DARK_CSS = """
<style>
.about-wrap { color: #e2e8f0; }
.about-hero {
    background: linear-gradient(135deg, #1e293b 0%, #1e3a5f 100%);
    border-color: #334155;
}
.about-hero h2 { color: #f1f5f9 !important; }
.about-hero-sub { color: #93c5fd; }
.about-hero-desc { color: #94a3b8; }
.about-ai-visual { background: #0f172a; border-color: #334155; }
.about-section-title { color: #f1f5f9; border-bottom-color: #3b82f6; }
.about-section-lead { color: #94a3b8; }
.about-card {
    background: #1e293b;
    border-color: #334155;
}
.about-card h4 { color: #f1f5f9 !important; }
.about-card p { color: #94a3b8; }
.about-workflow {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    border-color: #334155;
}
.about-wf-step {
    background: #1e293b;
    border-color: #475569;
    color: #e2e8f0;
}
.about-tech-badge {
    background: #1e293b;
    border-color: #475569;
    color: #e2e8f0;
}
.about-info-card {
    background: #1e293b;
    border-color: #334155;
}
.about-info-row { border-bottom-color: #334155; }
.about-info-label { color: #94a3b8; }
.about-info-value { color: #f1f5f9; }
</style>
"""

# ── بلوك 4: رسم SVG توضيحي (NLP → تصنيف المشاعر) ─────────────────────────
AI_VISUAL_SVG = """
<svg viewBox="0 0 320 240" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2563eb;stop-opacity:0.15"/>
      <stop offset="100%" style="stop-color:#7c3aed;stop-opacity:0.25"/>
    </linearGradient>
    <linearGradient id="g2" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1e3a5f"/>
      <stop offset="100%" style="stop-color:#2563eb"/>
    </linearGradient>
  </defs>
  <rect x="10" y="10" width="300" height="220" rx="14" fill="url(#g1)" stroke="#dbeafe" stroke-width="1"/>
  <!-- input text lines -->
  <rect x="28" y="36" width="120" height="8" rx="4" fill="#94a3b8" opacity="0.5"/>
  <rect x="28" y="54" width="90" height="8" rx="4" fill="#94a3b8" opacity="0.35"/>
  <rect x="28" y="72" width="105" height="8" rx="4" fill="#94a3b8" opacity="0.45"/>
  <rect x="28" y="90" width="75" height="8" rx="4" fill="#94a3b8" opacity="0.3"/>
  <!-- flow arrows -->
  <path d="M160 65 L195 65" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow)"/>
  <path d="M160 85 L195 85" stroke="#2563eb" stroke-width="1.5" opacity="0.6"/>
  <path d="M160 105 L195 105" stroke="#2563eb" stroke-width="1.5" opacity="0.4"/>
  <!-- AI core -->
  <circle cx="240" cy="120" r="48" fill="url(#g2)" opacity="0.9"/>
  <circle cx="240" cy="120" r="36" fill="none" stroke="#fff" stroke-width="1.5" opacity="0.4"/>
  <text x="240" y="108" text-anchor="middle" fill="#fff" font-size="11" font-weight="700" font-family="Segoe UI,sans-serif">NLP</text>
  <text x="240" y="128" text-anchor="middle" fill="#bfdbfe" font-size="9" font-family="Segoe UI,sans-serif">AI Model</text>
  <!-- output labels -->
  <rect x="28" y="155" width="52" height="22" rx="6" fill="#ecfdf5" stroke="#059669" stroke-width="1"/>
  <text x="54" y="170" text-anchor="middle" fill="#059669" font-size="9" font-weight="700">إيجابي</text>
  <rect x="88" y="155" width="52" height="22" rx="6" fill="#fffbeb" stroke="#d97706" stroke-width="1"/>
  <text x="114" y="170" text-anchor="middle" fill="#d97706" font-size="9" font-weight="700">محايد</text>
  <rect x="148" y="155" width="52" height="22" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="1"/>
  <text x="174" y="170" text-anchor="middle" fill="#dc2626" font-size="9" font-weight="700">سلبي</text>
  <path d="M240 168 L174 166" stroke="#dc2626" stroke-width="1" opacity="0.4"/>
  <path d="M240 168 L114 166" stroke="#d97706" stroke-width="1" opacity="0.4"/>
  <path d="M240 168 L54 166" stroke="#059669" stroke-width="1" opacity="0.4"/>
</svg>
"""


def _inject_about_styles() -> None:
    """يحقن CSS صفحة «حول» — فاتح + داكن إن لزم."""
    st.markdown(ABOUT_CSS, unsafe_allow_html=True)
    if st.session_state.get("dark_mode"):
        st.markdown(ABOUT_DARK_CSS, unsafe_allow_html=True)


def _switch_to_single_tab() -> None:
    """
    ينقر برمجياً على تبويب «تعليق واحد» عبر JavaScript في iframe Streamlit.

    يُستدعى بعد ضغط زر «ابدأ التحليل» في CTA.
    """
    components.html(
        """
        <script>
        (function () {
            const doc = window.parent.document;
            const tabs = doc.querySelectorAll('[data-baseweb="tab"]');
            for (const tab of tabs) {
                const label = (tab.innerText || tab.textContent || "").trim();
                if (label.includes("تعليق واحد")) {
                    tab.click();
                    window.parent.scrollTo({ top: 0, behavior: "smooth" });
                    break;
                }
            }
        })();
        </script>
        """,
        height=0,
    )


def render_about_panel(config: Any) -> None:
    """
    يبني صفحة «حول المشروع» كاملة من HTML + Streamlit.

    يقرأ من config:
      - ui → اسم الجامعة، القسم
      - platform → روابط GitHub والتطبيق
    """
    ui = config.ui
    platform = config.platform
    uni = ui.get("university_name_ar", "جامعة الشام")
    dept = ui.get("department_ar", "قسم الهندسة المعلوماتية")
    github = platform.get("github_url", "")
    app_url = platform.get("app_url", "")

    _inject_about_styles()

    # ── انتقال تلقائي لتبويب «تعليق واحد» بعد CTA ──
    if st.session_state.pop("about_nav_single", False):
        _switch_to_single_tab()

    st.markdown('<div class="about-wrap">', unsafe_allow_html=True)

    # ── قسم 1: بطاقة Hero ──
    st.markdown(
        f"""
        <section class="about-hero">
            <div>
                <span class="about-hero-tag">AI · NLP · Sentiment Analysis</span>
                <h2>تحليل مشاعر التعليقات</h2>
                <p class="about-hero-sub">
                    منصة ذكية لتحليل آراء المستخدمين باستخدام الذكاء الاصطناعي
                    ومعالجة اللغة الطبيعية
                </p>
                <p class="about-hero-desc">
                    يهدف المشروع إلى تطوير نظام ذكي قادر على تحليل التعليقات النصية
                    وفهم اتجاهاتها العاطفية، ثم تصنيفها تلقائياً إلى إيجابية أو محايدة أو سلبية.
                </p>
            </div>
            <div class="about-ai-visual">{AI_VISUAL_SVG}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # ── قسم 2: نبذة عن المشروع ──
    st.markdown(
        """
        <section class="about-section">
            <h3 class="about-section-title">نبذة عن المشروع</h3>
            <p class="about-section-lead" dir="rtl">
                يستخدم النظام تقنيات <strong>معالجة اللغة الطبيعية</strong>
                و<strong>الذكاء الاصطناعي</strong> لمعالجة التعليقات النصية،
                واستخراج المعلومات الدلالية منها، وتحديد المشاعر التي تعبّر عنها
                بدقة — لدعم فهم آراء المستخدمين في بيئات رقمية متعددة اللغات:
                العربية، الإنجليزية، واللهجة الشامية.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # ── قسم 3: أهداف المشروع ──
    st.markdown(
        """
        <section class="about-section">
            <h3 class="about-section-title">أهداف المشروع</h3>
            <div class="about-grid-4">
                <div class="about-card">
                    <div class="about-card-icon about-icon-blue">📄</div>
                    <h4>تحليل التعليقات</h4>
                    <p>تحليل النصوص واستخراج دلالاتها العاطفية.</p>
                </div>
                <div class="about-card">
                    <div class="about-card-icon about-icon-navy">🏷️</div>
                    <h4>تصنيف المشاعر</h4>
                    <p>تصنيف التعليقات إلى إيجابي ومحايد وسلبي.</p>
                </div>
                <div class="about-card">
                    <div class="about-card-icon about-icon-violet">🤖</div>
                    <h4>استخدام الذكاء الاصطناعي</h4>
                    <p>توظيف تقنيات الذكاء الاصطناعي ومعالجة اللغة الطبيعية في تحليل النصوص.</p>
                </div>
                <div class="about-card">
                    <div class="about-card-icon about-icon-teal">📊</div>
                    <h4>دعم اتخاذ القرار</h4>
                    <p>تقديم نتائج واضحة تساعد على فهم آراء المستخدمين.</p>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # ── قسم 4: تصنيف المشاعر ──
    st.markdown(
        """
        <section class="about-section">
            <h3 class="about-section-title">تصنيف المشاعر</h3>
            <div class="about-grid-3">
                <div class="about-card about-sent-pos">
                    <div class="about-card-icon">😊</div>
                    <h4>إيجابي</h4>
                    <p>يعبر عن الرضا والانطباع الإيجابي.</p>
                </div>
                <div class="about-card about-sent-neu">
                    <div class="about-card-icon">😐</div>
                    <h4>محايد</h4>
                    <p>لا يحمل توجهاً عاطفياً إيجابياً أو سلبياً بشكل واضح.</p>
                </div>
                <div class="about-card about-sent-neg">
                    <div class="about-card-icon">😞</div>
                    <h4>سلبي</h4>
                    <p>يعبر عن عدم الرضا أو الانطباع السلبي.</p>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # ── قسم 5: سير عمل النظام ──
    st.markdown(
        """
        <section class="about-section" dir="rtl">
            <h3 class="about-section-title">كيف يعمل النظام</h3>
            <div class="about-workflow" dir="rtl">
                <span class="about-wf-step">التعليق</span>
                <span class="about-wf-arrow" aria-hidden="true">←</span>
                <span class="about-wf-step">معالجة النص</span>
                <span class="about-wf-arrow" aria-hidden="true">←</span>
                <span class="about-wf-step">استخراج المعلومات</span>
                <span class="about-wf-arrow" aria-hidden="true">←</span>
                <span class="about-wf-step highlight">نموذج الذكاء الاصطناعي</span>
                <span class="about-wf-arrow" aria-hidden="true">←</span>
                <span class="about-wf-step">تصنيف المشاعر</span>
                <span class="about-wf-arrow" aria-hidden="true">←</span>
                <span class="about-wf-step">النتيجة</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # ── قسم 6: التقنيات المستخدمة ──
    st.markdown(
        f"""
        <section class="about-section" dir="rtl">
            <h3 class="about-section-title">التقنيات المستخدمة</h3>
            <div class="about-tech-grid" dir="rtl">
                <span class="about-tech-badge latin">Python</span>
                <span class="about-tech-badge">معالجة اللغة الطبيعية</span>
                <span class="about-tech-badge">معالجة النص</span>
                <span class="about-tech-badge">الذكاء الاصطناعي</span>
                <span class="about-tech-badge">تصنيف المشاعر</span>
                <span class="about-tech-badge model latin">{MODEL_DISPLAY_NAME}</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # ── قسم 7: معلومات المشروع ──
    st.markdown(
        f"""
        <section class="about-section">
            <h3 class="about-section-title">معلومات المشروع</h3>
            <div class="about-info-card">
                <div class="about-info-row">
                    <span class="about-info-label">الجامعة:</span>
                    <span class="about-info-value">{uni}</span>
                </div>
                <div class="about-info-row">
                    <span class="about-info-label">القسم:</span>
                    <span class="about-info-value">{dept}</span>
                </div>
                <div class="about-info-row">
                    <span class="about-info-label">المشروع:</span>
                    <span class="about-info-value">تحليل مشاعر التعليقات</span>
                </div>
                <div class="about-info-row">
                    <span class="about-info-label">المجال:</span>
                    <span class="about-info-value">الذكاء الاصطناعي ومعالجة اللغة الطبيعية</span>
                </div>
                <div class="about-info-row">
                    <span class="about-info-label">GitHub:</span>
                    <span class="about-info-value"><a href="{github}" target="_blank" rel="noopener">{github.replace("https://", "")}</a></span>
                </div>
                <div class="about-info-row">
                    <span class="about-info-label">استضافة التطبيق:</span>
                    <span class="about-info-value"><a href="{app_url}" target="_blank" rel="noopener">{app_url.replace("https://", "")}</a></span>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── قسم 8: دعوة للعمل (CTA) ──
    st.markdown(
        """
        <div class="about-cta">
            <h3>اكتشف النظام</h3>
            <p>انتقل إلى تحليل تعليق وتجربة تصنيف المشاعر باستخدام النظام.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("ابدأ التحليل", type="primary", use_container_width=True, key="about_start_cta"):
            st.session_state["about_nav_single"] = True
            st.rerun()


def render_about_tab(config: Any) -> None:
    """اسم موحّد — يستدعي render_about_panel."""
    render_about_panel(config)
