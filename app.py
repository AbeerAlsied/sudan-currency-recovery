# -*- coding: utf-8 -*-
"""
الجنيه أولاً | مركز تحليل وإنقاذ الاقتصاد السوداني
تشغيل:
    pip install streamlit pandas numpy plotly
    streamlit run app.py

مهم:
- البيانات الافتراضية أدناه توضيحية وليست أرقاماً رسمية موثقة.
- استبدلها بملف CSV موثق قبل استخدام النتائج في بحث أو قرار فعلي.
- المحاكاة سيناريوهات افتراضية وليست توقعات اقتصادية.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =========================================================
# 1) إعداد الصفحة والتصميم
# =========================================================
st.set_page_config(
    page_title="الجنيه أولاً | مركز الاقتصاد السوداني",
    page_icon="🇸🇩",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
.stApp { background: #f3f6fa; }
section[data-testid="stSidebar"] { background: #102b46; }
section[data-testid="stSidebar"] * { color: #ffffff !important; }
.hero {
    background: linear-gradient(120deg,#102b46,#087f8c);
    color: white; padding: 28px 30px; border-radius: 18px;
    margin-bottom: 18px; direction: rtl;
}
.hero h1 { font-size: 30px; margin: 0 0 8px 0; }
.hero p { font-size: 15px; margin: 0; opacity: .95; }
.section-title {
    color:#102b46; font-size:23px; font-weight:800;
    border-right:5px solid #0b9b91; padding-right:12px;
    margin: 8px 0 18px 0; direction:rtl;
}
.info-box {
    background:#e8f4f5; border-right:5px solid #0b9b91;
    padding:14px 16px; border-radius:10px; direction:rtl;
}
.warning-box {
    background:#fff4df; border-right:5px solid #e5a000;
    padding:14px 16px; border-radius:10px; direction:rtl;
}
.danger-box {
    background:#ffeded; border-right:5px solid #d9534f;
    padding:14px 16px; border-radius:10px; direction:rtl;
}
.metric-card {
    background:white; border:1px solid #e5eaf0; border-radius:14px;
    padding:14px 16px; box-shadow:0 2px 8px rgba(20,40,60,.04);
    direction:rtl; min-height:105px;
}
.metric-label { color:#667788; font-size:13px; }
.metric-value { color:#102b46; font-size:25px; font-weight:800; }
.metric-note { color:#82909d; font-size:11px; }
.small-note {color:#657789;font-size:12px;direction:rtl;}
div.stButton > button {
    border-radius:10px; border:0; background:#087f8c;
    color:white; font-weight:700; min-height:42px;
}
div.stButton > button:hover { background:#075e68; color:white; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) تعريف البيانات والأعمدة
# =========================================================
REQUIRED_COLUMNS = [
    "year", "exports_usd_m", "imports_usd_m",
    "gold_exports_usd_m", "agri_exports_usd_m",
    "essential_imports_usd_m", "inflation_pct",
    "official_fx_sdg", "parallel_fx_sdg",
    "m2_sdg_bn", "fiscal_deficit_sdg_bn",
]

COLUMN_LABELS = {
    "year": "السنة",
    "exports_usd_m": "إجمالي الصادرات (مليون دولار)",
    "imports_usd_m": "إجمالي الواردات (مليون دولار)",
    "gold_exports_usd_m": "صادرات الذهب (مليون دولار)",
    "agri_exports_usd_m": "الصادرات الزراعية والحيوانية (مليون دولار)",
    "essential_imports_usd_m": "الواردات الأساسية (مليون دولار)",
    "inflation_pct": "التضخم السنوي (%)",
    "official_fx_sdg": "سعر الصرف الرسمي (جنيه/دولار)",
    "parallel_fx_sdg": "سعر الصرف الموازي (جنيه/دولار)",
    "m2_sdg_bn": "عرض النقود M2 (مليار جنيه)",
    "fiscal_deficit_sdg_bn": "العجز المالي (مليار جنيه)",
}

# أرقام توضيحية مصطنعة لبناء التطبيق واختبار وظائفه فقط.
# لا يجوز تقديمها على أنها بيانات السودان الرسمية.
def load_illustrative_baseline():
    rows = [
        [2018, 4200, 9000, 1500, 1100, 6500, 63, 47, 55, 9000, 1200],
        [2019, 4100, 8200, 1450, 1050, 6000, 51, 45, 85, 11500, 1500],
        [2020, 3900, 7600, 1300, 1000, 5600, 163, 55, 120, 14500, 2100],
        [2021, 4600, 8800, 1700, 1200, 6400, 359, 440, 520, 19000, 3200],
        [2022, 5200, 9600, 1900, 1450, 6900, 138, 570, 580, 25000, 4100],
        [2023, 4300, 7900, 1550, 1250, 5900, 66, 600, 950, 31000, 5200],
        [2024, 3600, 6900, 1250, 1050, 5200, 150, 1100, 2200, 39000, 6800],
    ]
    df = pd.DataFrame(rows, columns=REQUIRED_COLUMNS)
    df["data_type"] = "بيانات توضيحية"
    df["primary_source"] = "لا يوجد — أرقام افتراضية لاختبار التطبيق"
    df["source_url"] = ""
    df["updated_at"] = "غير متاح"
    df["notes"] = "بيانات توضيحية مصطنعة وليست بيانات رسمية."
    return df

# =========================================================
# 3) فحص البيانات وتنظيفها
# =========================================================
def validate_economic_data(raw_df):
    df = raw_df.copy()
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("الأعمدة الناقصة: " + "، ".join(missing))

    for col in REQUIRED_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[REQUIRED_COLUMNS].isna().any().any():
        bad = df[REQUIRED_COLUMNS].columns[df[REQUIRED_COLUMNS].isna().any()].tolist()
        raise ValueError("توجد خلايا فارغة أو غير رقمية في: " + "، ".join(bad))

    if not np.all(np.equal(np.mod(df["year"], 1), 0)):
        raise ValueError("يجب أن تكون السنة أعداداً صحيحة.")
    df["year"] = df["year"].astype(int)

    if df["year"].duplicated().any():
        dup = df.loc[df["year"].duplicated(), "year"].tolist()
        raise ValueError(f"هناك سنوات مكررة: {dup}")

    nonnegative = [
        "exports_usd_m", "imports_usd_m", "gold_exports_usd_m",
        "agri_exports_usd_m", "essential_imports_usd_m",
        "inflation_pct", "m2_sdg_bn",
    ]
    for col in nonnegative:
        if (df[col] < 0).any():
            raise ValueError(f"لا يُسمح بقيم سالبة في {COLUMN_LABELS[col]}.")

    for col in ["official_fx_sdg", "parallel_fx_sdg"]:
        if (df[col] <= 0).any():
            raise ValueError(f"{COLUMN_LABELS[col]} يجب أن تكون أكبر من صفر.")

    if (df["imports_usd_m"] <= 0).any():
        raise ValueError("إجمالي الواردات يجب أن يكون أكبر من صفر.")
    if (df["essential_imports_usd_m"] > df["imports_usd_m"]).any():
        raise ValueError("الواردات الأساسية لا يمكن أن تتجاوز إجمالي الواردات.")
    if ((df["gold_exports_usd_m"] + df["agri_exports_usd_m"]) > df["exports_usd_m"]).any():
        raise ValueError("مجموع صادرات الذهب والزراعة يتجاوز إجمالي الصادرات.")

    return df.sort_values("year").reset_index(drop=True)

def compute_indicators(df):
    res = df.copy()
    res["trade_balance_usd_m"] = res["exports_usd_m"] - res["imports_usd_m"]
    res["import_coverage_pct"] = (res["exports_usd_m"] / res["imports_usd_m"]) * 100
    res["gold_share_pct"] = (res["gold_exports_usd_m"] / res["exports_usd_m"].replace(0, np.nan)) * 100
    res["agri_share_pct"] = (res["agri_exports_usd_m"] / res["exports_usd_m"].replace(0, np.nan)) * 100
    res["other_exports_usd_m"] = (
        res["exports_usd_m"] - res["gold_exports_usd_m"] - res["agri_exports_usd_m"]
    )
    res["essential_import_share_pct"] = (
        res["essential_imports_usd_m"] / res["imports_usd_m"]
    ) * 100
    res["nonessential_imports_usd_m"] = (
        res["imports_usd_m"] - res["essential_imports_usd_m"]
    )
    res["fx_gap_pct"] = (
        (res["parallel_fx_sdg"] - res["official_fx_sdg"])
        / res["official_fx_sdg"]
    ) * 100
    res["m2_growth_pct"] = res["m2_sdg_bn"].pct_change() * 100
    res["exports_growth_pct"] = res["exports_usd_m"].pct_change() * 100
    res["imports_growth_pct"] = res["imports_usd_m"].pct_change() * 100

    # مؤشر داخلي تجريبي للتوضيح فقط، وليس مؤشراً اقتصادياً معتمداً.
    # تُقيد المكونات بين صفر و100 لتجنب تضخم المؤشر.
    fx_component = 100 - res["fx_gap_pct"].clip(0, 300) / 3
    coverage_component = res["import_coverage_pct"].clip(0, 100)
    diversification_component = (
        100 - res["gold_share_pct"].clip(0, 100)
    )
    inflation_component = 100 - res["inflation_pct"].clip(0, 300) / 3
    res["project_stability_index"] = (
        0.30 * fx_component.clip(0, 100)
        + 0.30 * coverage_component.clip(0, 100)
        + 0.20 * diversification_component.clip(0, 100)
        + 0.20 * inflation_component.clip(0, 100)
    )
    return res

# =========================================================
# 4) تحميل البيانات من الملف أو الافتراضية
# =========================================================
st.sidebar.markdown("## 🇸🇩 الجنيه أولاً")
st.sidebar.caption("مركز تحليل الاقتصاد السوداني")
uploaded = st.sidebar.file_uploader("ارفع ملف البيانات CSV", type=["csv"])

if uploaded is not None:
    try:
        raw = pd.read_csv(uploaded)
        data = compute_indicators(validate_economic_data(raw))
        data_origin = "ملف CSV مرفوع"
        st.sidebar.success("تم تحميل البيانات وفحصها بنجاح.")
    except Exception as exc:
        data = compute_indicators(validate_economic_data(load_illustrative_baseline()))
        data_origin = "البيانات التوضيحية — فشل تحميل الملف"
        st.sidebar.error(f"تعذر استخدام الملف: {exc}")
else:
    data = compute_indicators(validate_economic_data(load_illustrative_baseline()))
    data_origin = "بيانات توضيحية مصطنعة"

st.sidebar.markdown("---")
st.sidebar.markdown("### تنبيه البيانات")
st.sidebar.caption("البيانات الافتراضية للتجربة فقط. ارفع CSV موثقاً لتحليل الأرقام الفعلية.")
pages = [
    "مركز القيادة",
    "الجنيه وسعر الصرف",
    "الذهب والمعادن",
    "الإنتاج والتنويع",
    "التجارة الخارجية",
    "التضخم والقوة الشرائية",
    "السياسة النقدية والمالية",
    "مختبر إنقاذ الجنيه",
    "المستشار الاقتصادي",
    "البيانات والمصادر",
]
page = st.sidebar.radio("انتقل إلى القسم", pages)
st.sidebar.markdown("---")
st.sidebar.caption("نسخة تحليلية تعليمية — ليست بديلاً عن التقارير الرسمية.")

latest = data.iloc[-1]
previous = data.iloc[-2] if len(data) > 1 else latest
year_latest = int(latest["year"])

# =========================================================
# 5) أدوات عرض عامة
# =========================================================
def metric_card(label, value, note=""):
    st.markdown(
        f"""<div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
        </div>""",
        unsafe_allow_html=True,
    )

def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

def fmt_num(value, digits=1):
    if pd.isna(value):
        return "غير متاح"
    return f"{value:,.{digits}f}"

def source_warning():
    if "توضيحية" in data_origin:
        st.markdown(
            '<div class="warning-box"><b>تنبيه مهم:</b> النتائج الحالية مبنية على بيانات توضيحية مصطنعة، '
            'ولا تمثل وصفاً موثقاً للاقتصاد السوداني. ارفع بيانات موثقة قبل الاستنتاج أو الاقتباس.</div>',
            unsafe_allow_html=True,
        )

def chart_line(df, x, y, title, labels=None):
    fig = px.line(df, x=x, y=y, markers=True, title=title, labels=labels)
    fig.update_layout(template="plotly_white", title_x=0.98, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

def chart_bar(df, x, y, title, labels=None):
    fig = px.bar(df, x=x, y=y, title=title, labels=labels, text_auto=".2s")
    fig.update_layout(template="plotly_white", title_x=0.98)
    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# 6) واجهة الأقسام
# =========================================================
st.markdown("""
<div class="hero">
    <h1>🇸🇩 الجنيه أولاً</h1>
    <p>مركز تحليل وإنقاذ الاقتصاد السوداني — من قراءة المؤشرات إلى اختبار الحلول والسياسات.</p>
</div>
""", unsafe_allow_html=True)

source_warning()
st.caption(f"مصدر البيانات الحالي: {data_origin} | آخر سنة في البيانات: {year_latest}")

if page == "مركز القيادة":
    section("لوحة القيادة الاقتصادية")
    st.write("ملخص سريع لأهم المؤشرات المتاحة في مجموعة البيانات الحالية.")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("إجمالي الصادرات", f"{fmt_num(latest['exports_usd_m'])} مليون $", f"سنة {year_latest}")
    with c2:
        metric_card("إجمالي الواردات", f"{fmt_num(latest['imports_usd_m'])} مليون $", f"سنة {year_latest}")
    with c3:
        metric_card("التضخم", f"{fmt_num(latest['inflation_pct'])}%", "المعدل السنوي")
    with c4:
        metric_card("فجوة سعر الصرف", f"{fmt_num(latest['fx_gap_pct'])}%", "الموازي مقارنة بالرسمي")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        metric_card("الميزان التجاري", f"{fmt_num(latest['trade_balance_usd_m'])} مليون $", "الصادرات ناقص الواردات")
    with c6:
        metric_card("تغطية الواردات", f"{fmt_num(latest['import_coverage_pct'])}%", "الصادرات ÷ الواردات")
    with c7:
        metric_card("حصة الذهب", f"{fmt_num(latest['gold_share_pct'])}%", "من إجمالي الصادرات")
    with c8:
        metric_card("مؤشر المشروع", f"{fmt_num(latest['project_stability_index'])}/100", "مؤشر تجريبي غير معتمد")

    section("صورة الاقتصاد عبر الزمن")
    col1, col2 = st.columns(2)
    with col1:
        chart_line(data, "year", ["exports_usd_m", "imports_usd_m"], "الصادرات والواردات (مليون دولار)")
    with col2:
        chart_line(data, "year", "inflation_pct", "التضخم السنوي (%)")
    col3, col4 = st.columns(2)
    with col3:
        chart_line(data, "year", ["official_fx_sdg", "parallel_fx_sdg"], "سعر الصرف الرسمي والموازي")
    with col4:
        chart_line(data, "year", "project_stability_index", "مؤشر الاستقرار التجريبي")

    section("أبرز الإشارات")
    signals = []
    if latest["trade_balance_usd_m"] < 0:
        signals.append("العجز التجاري: قيمة الواردات أعلى من الصادرات.")
    else:
        signals.append("فائض تجاري وفق البيانات المدخلة.")
    if latest["gold_share_pct"] > 50:
        signals.append("تركيز مرتفع للصادرات في الذهب؛ التنويع يستحق الدراسة.")
    if latest["fx_gap_pct"] > 20:
        signals.append("فجوة سعر الصرف كبيرة وفق الأرقام المدخلة.")
    if latest["inflation_pct"] > 20:
        signals.append("التضخم مرتفع ويضغط على القوة الشرائية.")
    if latest["essential_import_share_pct"] > 80:
        signals.append("معظم الواردات مصنفة كأساسية؛ مساحة خفضها محدودة.")
    for s in signals:
        st.markdown(f"- {s}")

elif page == "الجنيه وسعر الصرف":
    section("الجنيه السوداني وسعر الصرف")
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("السعر الرسمي", f"{fmt_num(latest['official_fx_sdg'])} جنيه/$")
    with c2:
        metric_card("السعر الموازي", f"{fmt_num(latest['parallel_fx_sdg'])} جنيه/$")
    with c3:
        metric_card("الفجوة", f"{fmt_num(latest['fx_gap_pct'])}%")
    chart_line(data, "year", ["official_fx_sdg", "parallel_fx_sdg"], "تطور سعر الصرف الرسمي والموازي")
    section("كيف نقرأ فجوة الصرف؟")
    st.markdown("""
    <div class="info-box">
    فجوة الصرف تقيس الفرق النسبي بين السعر الموازي والرسمي. ارتفاعها قد يرتبط بنقص المعروض من النقد الأجنبي،
    أو قيود الوصول إليه، أو توقعات التضخم والمخاطر. لكنها وحدها لا تشرح كل أسباب تراجع العملة.
    </div>""", unsafe_allow_html=True)
    st.write(f"وفق آخر سنة مدخلة ({year_latest})، تبلغ الفجوة المحسوبة **{fmt_num(latest['fx_gap_pct'])}%**.")
    st.write("لتحليل أعمق نحتاج أيضاً إلى بيانات احتياطيات النقد الأجنبي، التحويلات، تدفقات الصادرات، والطلب على الاستيراد.")

elif page == "الذهب والمعادن":
    section("الذهب والمعادن — من مورد طبيعي إلى حصيلة نقد أجنبي")
    gold = data[["year", "gold_exports_usd_m", "exports_usd_m", "gold_share_pct"]].copy()
    col1, col2 = st.columns(2)
    with col1:
        chart_bar(gold, "year", "gold_exports_usd_m", "قيمة صادرات الذهب (مليون دولار)")
    with col2:
        chart_line(gold, "year", "gold_share_pct", "حصة الذهب من إجمالي الصادرات (%)")
    metric_card("حصة الذهب في آخر سنة", f"{fmt_num(latest['gold_share_pct'])}%", "من إجمالي الصادرات")
    st.markdown("""
    <div class="info-box">
    السؤال الاقتصادي ليس فقط كم ينتج السودان من الذهب، بل كم من قيمته يصل إلى القنوات الرسمية؟
    يتطلب ذلك بيانات الإنتاج، الصادرات الرسمية، التهريب التقديري، الأسعار العالمية، وتكاليف التعدين.
    </div>""", unsafe_allow_html=True)
    st.subheader("بيانات إضافية نحتاجها")
    st.write("- إنتاج الذهب بالطن سنوياً.")
    st.write("- الكمية المصدرة رسمياً وقيمتها.")
    st.write("- تقديرات الفاقد والتهريب مع توضيح منهجية التقدير.")
    st.write("- عدد العاملين ومساهمة التعدين في الإيرادات والوظائف.")

elif page == "الإنتاج والتنويع":
    section("الإنتاج والتنويع الاقتصادي")
    prod = data[["year", "agri_exports_usd_m", "other_exports_usd_m", "gold_exports_usd_m"]].melt(
        id_vars="year", var_name="sector", value_name="value"
    )
    names = {
        "agri_exports_usd_m": "الزراعة والثروة الحيوانية",
        "other_exports_usd_m": "صادرات أخرى",
        "gold_exports_usd_m": "الذهب",
    }
    prod["sector"] = prod["sector"].map(names)
    fig = px.bar(prod, x="year", y="value", color="sector", barmode="stack",
                 title="تركيب الصادرات حسب المجموعات (مليون دولار)")
    fig.update_layout(template="plotly_white", title_x=.98)
    st.plotly_chart(fig, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        metric_card("الصادرات الزراعية والحيوانية", f"{fmt_num(latest['agri_exports_usd_m'])} مليون $")
    with c2:
        metric_card("الصادرات الأخرى", f"{fmt_num(latest['other_exports_usd_m'])} مليون $")
    st.markdown("""
    <div class="info-box">
    التنويع لا يعني زيادة الصادرات الزراعية فقط؛ بل رفع الإنتاجية، تحسين التخزين والنقل والكهرباء،
    التصنيع المحلي، الجودة، والوصول للأسواق. لا يمكن تقدير أثر ذلك بدقة دون بيانات إنتاج وتكاليف وأسعار.
    </div>""", unsafe_allow_html=True)
    st.subheader("أسئلة يجب أن يجيب عنها التحليل")
    st.write("- ما السلع التي يملك السودان فيها ميزة إنتاجية؟")
    st.write("- ما العوائق التي تمنع وصول المنتج إلى السوق؟")
    st.write("- ما نسبة الإنتاج التي تستهلك محلياً وما الذي يمكن تصديره دون الإضرار بالأمن الغذائي؟")
    st.write("- ما أثر الكهرباء والطرق والتمويل والتخزين على تكلفة الإنتاج؟")

elif page == "التجارة الخارجية":
    section("التجارة الخارجية والميزان التجاري")
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("الميزان التجاري", f"{fmt_num(latest['trade_balance_usd_m'])} مليون $")
    with c2:
        metric_card("تغطية الواردات", f"{fmt_num(latest['import_coverage_pct'])}%")
    with c3:
        metric_card("الواردات الأساسية", f"{fmt_num(latest['essential_import_share_pct'])}% من الواردات")
    col1, col2 = st.columns(2)
    with col1:
        chart_line(data, "year", "trade_balance_usd_m", "الميزان التجاري (مليون دولار)")
    with col2:
        chart_line(data, "year", "import_coverage_pct", "قدرة الصادرات على تغطية الواردات (%)")
    mix = pd.DataFrame({
        "الفئة": ["واردات أساسية", "واردات أخرى"],
        "القيمة": [latest["essential_imports_usd_m"], latest["nonessential_imports_usd_m"]],
    })
    fig = px.pie(mix, names="الفئة", values="القيمة", hole=.48, title=f"تركيب الواردات — {year_latest}")
    fig.update_layout(title_x=.98)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    <div class="warning-box">
    تقليل الواردات بصورة عشوائية قد يضر الغذاء والدواء ومدخلات الإنتاج. أي سياسة إحلال واردات يجب أن تفرق
    بين السلع الضرورية والسلع التي يمكن إنتاج بديل محلي لها بكفاءة وجودة وسعر مناسب.
    </div>""", unsafe_allow_html=True)

elif page == "التضخم والقوة الشرائية":
    section("التضخم والقوة الشرائية")
    c1, c2 = st.columns(2)
    with c1:
        metric_card("التضخم في آخر سنة", f"{fmt_num(latest['inflation_pct'])}%")
    with c2:
        metric_card("تغير التضخم عن السنة السابقة", f"{fmt_num(latest['inflation_pct'] - previous['inflation_pct'])} نقطة مئوية")
    chart_line(data, "year", "inflation_pct", "معدل التضخم السنوي (%)")

    st.subheader("حاسبة القوة الشرائية")
    years = data["year"].astype(int).tolist()
    left, right = st.columns(2)
    with left:
        base_year = st.selectbox("سنة المبلغ الأصلي", years, index=0)
    with right:
        target_year = st.selectbox("السنة المراد المقارنة بها", years, index=len(years)-1)
    amount = st.number_input("أدخل المبلغ بالجنيه", min_value=0.0, value=10000.0, step=500.0)
    if base_year == target_year:
        factor = 1.0
    else:
        low, high = sorted([base_year, target_year])
        selected = data[(data["year"] > low) & (data["year"] <= high)]
        factor = float(np.prod(1 + selected["inflation_pct"].to_numpy() / 100))
    if target_year >= base_year:
        equivalent = amount * factor
        st.success(
            f"المبلغ المكافئ في أسعار سنة {target_year} ≈ **{equivalent:,.2f} جنيه** "
            f"للحفاظ على قوة شراء {amount:,.2f} جنيه في سنة {base_year}."
        )
    else:
        real_value = amount / factor
        st.success(
            f"قيمة مبلغ {amount:,.2f} جنيه في سنة {target_year} بأسعار سنة {base_year} "
            f"≈ **{real_value:,.2f} جنيه**."
        )
    st.caption("الحساب تقريبي ويستخدم معدلات التضخم السنوية المدخلة، ولا يعكس اختلاف تضخم السلع بين الأسر.")

elif page == "السياسة النقدية والمالية":
    section("السياسة النقدية والمالية")
    c1, c2 = st.columns(2)
    with c1:
        metric_card("عرض النقود M2", f"{fmt_num(latest['m2_sdg_bn'])} مليار جنيه")
    with c2:
        metric_card("العجز المالي", f"{fmt_num(latest['fiscal_deficit_sdg_bn'])} مليار جنيه")
    col1, col2 = st.columns(2)
    with col1:
        chart_line(data, "year", "m2_sdg_bn", "عرض النقود M2 (مليار جنيه)")
    with col2:
        chart_line(data, "year", "fiscal_deficit_sdg_bn", "العجز المالي (مليار جنيه)")
    if pd.notna(latest["m2_growth_pct"]):
        st.write(f"نمو عرض النقود بين آخر سنتين: **{fmt_num(latest['m2_growth_pct'])}%**.")
    st.markdown("""
    <div class="info-box">
    تحليل التضخم يحتاج ربط عرض النقود والإنفاق العام والإيرادات والإنتاج وسعر الصرف وتوقعات الجمهور.
    لا يكفي النظر إلى متغير واحد لإثبات سبب التضخم.
    </div>""", unsafe_allow_html=True)
    st.caption("تأكد من تعريف العجز المالي في ملفك: هل القيمة عجز موجب أم رصيد مالي سالب؟ وثّق ذلك في عمود notes.")

elif page == "مختبر إنقاذ الجنيه":
    section("مختبر السياسات — جرّب سيناريوهات افتراضية")
    st.markdown("""
    <div class="warning-box">
    هذه أداة حساب سيناريو مبسط، وليست نموذجاً اقتصادياً تنبؤياً. تفترض أن الزيادة المحددة تتحول مباشرة
    إلى صادرات إضافية، ولا تحسب تغير الأسعار أو تكاليف الإنتاج أو ردود فعل السوق.
    </div>""", unsafe_allow_html=True)

    st.subheader("1) زيادة الصادرات")
    a, b = st.columns(2)
    with a:
        agri_increase = st.slider("زيادة الصادرات الزراعية والحيوانية (%)", 0, 100, 20, 5)
    with b:
        gold_increase = st.slider("زيادة حصيلة صادرات الذهب الرسمية (%)", 0, 100, 10, 5)
    st.subheader("2) إدارة الواردات")
    import_cut = st.slider("خفض الواردات غير الأساسية (%)", 0, 60, 10, 5)

    extra_agri = latest["agri_exports_usd_m"] * agri_increase / 100
    extra_gold = latest["gold_exports_usd_m"] * gold_increase / 100
    reduced_imports = latest["nonessential_imports_usd_m"] * import_cut / 100
    scenario_exports = latest["exports_usd_m"] + extra_agri + extra_gold
    scenario_imports = latest["imports_usd_m"] - reduced_imports
    scenario_balance = scenario_exports - scenario_imports
    scenario_coverage = (scenario_exports / scenario_imports * 100) if scenario_imports > 0 else np.nan

    st.subheader("نتيجة السيناريو")
    x1, x2, x3 = st.columns(3)
    with x1:
        metric_card("الصادرات بعد السيناريو", f"{scenario_exports:,.1f} مليون $")
    with x2:
        metric_card("الواردات بعد السيناريو", f"{scenario_imports:,.1f} مليون $")
    with x3:
        metric_card("الميزان التجاري الجديد", f"{scenario_balance:,.1f} مليون $")
    st.metric("تغطية الواردات بعد السيناريو", f"{scenario_coverage:,.1f}%")
    st.write("التحسن الحسابي في الميزان التجاري:",
             f"**{scenario_balance - latest['trade_balance_usd_m']:,.1f} مليون دولار**.")
    compare = pd.DataFrame({
        "الحالة": ["قبل السيناريو", "بعد السيناريو"],
        "الصادرات": [latest["exports_usd_m"], scenario_exports],
        "الواردات": [latest["imports_usd_m"], scenario_imports],
    })
    fig = go.Figure()
    fig.add_trace(go.Bar(name="الصادرات", x=compare["الحالة"], y=compare["الصادرات"]))
    fig.add_trace(go.Bar(name="الواردات", x=compare["الحالة"], y=compare["الواردات"]))
    fig.update_layout(barmode="group", title="مقارنة الصادرات والواردات", template="plotly_white", title_x=.98)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("لا تستنتج من تحسن الميزان التجاري وحده أن سعر الصرف سيتحسن تلقائياً؛ توجد عوامل أخرى كثيرة.")

elif page == "المستشار الاقتصادي":
    section("المستشار الاقتصادي — تشخيص أولي وتوصيات")
    st.write(f"التشخيص مبني على آخر سنة متاحة: **{year_latest}**.")
    recommendations = []

    if latest["trade_balance_usd_m"] < 0:
        recommendations.append((
            "العجز التجاري",
            f"العجز التجاري يبلغ {abs(latest['trade_balance_usd_m']):,.1f} مليون دولار.",
            "رفع القدرة التصديرية تدريجياً، وتحسين الخدمات اللوجستية، ومراجعة الواردات غير الأساسية دون المساس بالغذاء والدواء ومدخلات الإنتاج."
        ))
    else:
        recommendations.append((
            "الميزان التجاري",
            f"يوجد فائض تجاري قدره {latest['trade_balance_usd_m']:,.1f} مليون دولار وفق البيانات.",
            "تحليل استدامة الفائض ومصادره، وتوجيه النقد الأجنبي لدعم الإنتاج والاستثمار."
        ))

    if latest["gold_share_pct"] > 40:
        recommendations.append((
            "تركيز الصادرات في الذهب",
            f"حصة الذهب {latest['gold_share_pct']:.1f}% من الصادرات.",
            "تنويع الصادرات ورفع القيمة المضافة محلياً، وتحسين شفافية بيانات الإنتاج والتصدير."
        ))
    else:
        recommendations.append((
            "تنويع الصادرات",
            f"حصة الذهب {latest['gold_share_pct']:.1f}% من الصادرات.",
            "متابعة تنوع السلع المصدرة وعدم الاعتماد على سلعة واحدة، مع دعم القطاعات القابلة للتوسع."
        ))

    if latest["fx_gap_pct"] > 20:
        recommendations.append((
            "فجوة سعر الصرف",
            f"الفجوة المحسوبة {latest['fx_gap_pct']:.1f}%.",
            "تحسين تدفق النقد الأجنبي عبر الصادرات والتحويلات والقنوات الرسمية، وزيادة الثقة والشفافية؛ مع تجنب الوعود بخفض سريع للسعر."
        ))
    if latest["inflation_pct"] > 20:
        recommendations.append((
            "ضغط التضخم",
            f"التضخم السنوي {latest['inflation_pct']:.1f}%.",
            "حماية الإنتاج وسلاسل الإمداد، وتحسين إدارة المالية العامة، ونشر بيانات دورية للأسعار؛ مع تقييم أثر أي إجراء على الأسر محدودة الدخل."
        ))
    if latest["essential_import_share_pct"] > 80:
        recommendations.append((
            "هيكل الواردات",
            f"{latest['essential_import_share_pct']:.1f}% من الواردات مصنفة كأساسية.",
            "تجنب الخفض العشوائي للواردات، والتركيز على إحلال مدروس للسلع التي يمكن إنتاجها محلياً بكفاءة."
        ))
    if pd.notna(latest["m2_growth_pct"]) and latest["m2_growth_pct"] > 30:
        recommendations.append((
            "نمو عرض النقود",
            f"نمو M2 بين آخر سنتين {latest['m2_growth_pct']:.1f}%.",
            "تحليل مصادر نمو السيولة وربطها بالإنتاج والتمويل والعجز، وعدم افتراض أن العلاقة مع التضخم آلية أو فورية."
        ))

    for title, evidence, action in recommendations:
        with st.container(border=True):
            st.markdown(f"### {title}")
            st.write("**الدليل من البيانات:** " + evidence)
            st.write("**مسار عمل مقترح:** " + action)

    st.markdown("""
    <div class="info-box">
    هذه توصيات أولية مولدة من قواعد واضحة، وليست استشارة حكومية أو دراسة أثر مكتملة.
    يجب اختبار كل توصية ببيانات إضافية، وتقدير تكلفتها، والفئات المستفيدة والمتضررة، والمدة اللازمة.
    </div>""", unsafe_allow_html=True)

elif page == "البيانات والمصادر":
    section("مركز البيانات والمصادر")
    st.write("الأعمدة المطلوبة في ملف CSV:")
    schema = pd.DataFrame({
        "اسم العمود": REQUIRED_COLUMNS,
        "المعنى": [COLUMN_LABELS[c] for c in REQUIRED_COLUMNS],
    })
    st.dataframe(schema, use_container_width=True, hide_index=True)
    st.subheader("البيانات المستخدمة حالياً")
    st.dataframe(data, use_container_width=True, hide_index=True)
    csv_out = data.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "تنزيل البيانات الحالية CSV",
        data=csv_out,
        file_name="sudan_economic_data_template.csv",
        mime="text/csv",
    )
    st.subheader("مصادر رسمية ومراجع للبحث عن البيانات")
    st.markdown("""
    - **بنك السودان المركزي:** التقارير السنوية والنشرات الإحصائية والبيانات النقدية.
    - **الجهاز المركزي للإحصاء السوداني:** مؤشرات الأسعار والتضخم والإحصاءات السكانية والإنتاجية.
    - **وزارة المالية والتخطيط الاقتصادي:** الموازنة العامة والإيرادات والإنفاق والعجز.
    - **صندوق النقد الدولي:** قواعد بيانات الاقتصاد الكلي وتقارير السودان.
    - **البنك الدولي:** مؤشرات التنمية والاقتصاد الكلي.
    - **UN Comtrade:** بيانات التجارة السلعية حسب الدولة والسلعة والشريك التجاري.
    - **FAOSTAT:** الإنتاج الزراعي والثروة الحيوانية.
    """)
    st.markdown("""
    <div class="warning-box">
    لا يكفي كتابة اسم جهة كمصدر. لكل رقم في النسخة البحثية أضف رابط الجدول أو التقرير، سنة النشر،
    تاريخ الاطلاع، وحدة القياس، وما إذا كانت القيمة فعلية أو تقديرية أو أولية.
    </div>""", unsafe_allow_html=True)
    st.subheader("قالب توثيق مقترح")
    citation_template = pd.DataFrame([
        ["exports_usd_m", "رابط المصدر الأصلي", "2024", "مليون دولار", "فعلي/تقديري", "تاريخ الاطلاع"],
        ["inflation_pct", "رابط المصدر الأصلي", "2024", "% سنوي", "فعلي/تقديري", "تاريخ الاطلاع"],
    ], columns=["المتغير", "رابط المصدر", "السنة", "الوحدة", "نوع الرقم", "تاريخ الاطلاع"])
    st.dataframe(citation_template, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#758596;font-size:12px;direction:rtl'>"
    "الجنيه أولاً | مشروع تحليل اقتصادي تعليمي — تُحدّث النتائج عند رفع بيانات موثقة"
    "</div>",
    unsafe_allow_html=True,
)
 
