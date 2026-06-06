import streamlit as st

from evaluation.explain import explain_text, render_explanation_html, supports_lime


def render_lime_explanation(predictor, text: str, language: str | None = None) -> None:
    st.markdown("#### 🔬 تفسير LIME")
    st.caption("الكلمات التي أثرت على التصنيف (TF-IDF فقط)")

    if not supports_lime(predictor):
        st.info(
            "⚠️ **LIME متاح فقط مع نموذج TF-IDF.** "
            "BERT نموذج Transformer — استخدم «مقارنة النماذج» لرؤية الفرق بين TF-IDF و BERT."
        )
        return

    try:
        explanation = explain_text(predictor, text, language=language, num_features=8)
        features = explanation.get("features", [])
        if not features:
            st.info("لم يُرجع LIME أي كلمات مؤثرة.")
            return

        html = render_explanation_html(features)
        st.markdown(html, unsafe_allow_html=True)

        table = [{"الكلمة": f["word"], "الوزن": f"{f['weight']:+.3f}"} for f in features]
        st.dataframe(table, use_container_width=True, hide_index=True)
    except ImportError:
        st.warning("ثبّت lime: pip install lime")
    except Exception as exc:
        st.info(f"التفسير غير متاح: {exc}")
