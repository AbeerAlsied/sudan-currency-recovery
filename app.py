import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="الجنيه أولاً | Sudan Economic Monitor", page_icon="🇸🇩", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', sans-serif !important;
}

.block-container {padding-top: 1.6rem;}
[data-testid="stMetric"] {background:#f3f7fa;padding:14px;border-radius:12px;border:1px solid #dce6ee;}
.note {background:#fff7df;border-right:5px solid #d99b22;padding:12px;border-radius:8px;}

/* إصلاح تداخل العناوين والنصوص العربية على الجوال */
h1, h2, h3, h4, h5, h6, p, span, label, div {
    direction: rtl !important;
    text-align: right !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🇸🇩 الجنيه أولاً")
st.subheader("لوحة أولية لتحليل المؤشرات الاقتصادية السودانية")
st.markdown(
    '<div class="note"><b>تنبيه مهم:</b> البيانات الافتراضية داخل المشروع تجريبية ومصطنعة لتجربة البرنامج فقط، '
    'وليست أرقاماً حقيقية عن السودان. لا تستخدم لاتخاذ قرار اقتصادي أو إصدار توقعات عن سعر الصرف.</div>',
    unsafe_allow_html=True
)

REQUIRED = [
    "year", "exports_usd_m", "imports_usd_m", "inflation_pct",
    "fx_reserves_usd_m", "gold_exports_usd_m", "agriculture_exports_usd_m"
]
AR = {
    "year": "السنة",
    "exports_usd_m": "الصادرات (مليون دولار)",
    "imports_usd_m": "الواردات (مليون دولار)",
    "inflation_pct": "التضخم (%)",
    "fx_reserves_usd_m": "الاحتياطيات الأجنبية (مليون دولار)",
    "gold_exports_usd_m": "صادرات الذهب (مليون دولار)",
    "agriculture_exports_usd_m": "الصادرات الزراعية (مليون دولار)"
}

def demo_data():
    return pd.DataFrame([
        [2018, 4200, 7800, 63, 1400, 1500, 900],
        [2019, 3900, 7600, 51, 1250, 1400, 850],
        [2020, 3600, 7200, 163, 1100, 1250, 820],
        [2021, 4100, 7900, 359, 1000, 1600, 900],
        [2022, 4500, 8300, 138, 950, 1800, 1050],
        [2023, 3000, 6900, 120, 700, 1100, 750],
        [2024, 2600, 6100, 170, 550, 900, 650],
        [2025, 2800, 6200, 145, 600, 1000, 700],
    ], columns=REQUIRED)

with st.sidebar:
    st.header("مصدر البيانات")
    uploaded = st.file_uploader("ارفع ملف CSV موثوق", type=["csv"])
    st.caption("يمكنك البدء بالبيانات التجريبية، ثم استبدالها ببيانات موثقة.")
    use_demo = st.toggle("استخدام بيانات العرض التجريبية", value=uploaded is None)

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        source_label = "ملف CSV مرفوع"
    except Exception as e:
        st.error(f"تعذر قراءة الملف: {e}")
        st.stop()
elif use_demo:
    df = demo_data()
    source_label = "بيانات تجريبية مصطنعة"
else:
    st.info("ارفع ملف CSV أو فعّل بيانات العرض التجريبية من الشريط الجانبي.")
    st.stop()

missing = [c for c in REQUIRED if c not in df.columns]
if missing:
    st.error("الأعمدة التالية ناقصة في ملفك: " + ", ".join(missing))
    st.code(",".join(REQUIRED))
    st.stop()

for c in REQUIRED:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df = df.dropna(subset=REQUIRED).sort_values("year")
if df.empty:
    st.error("لا توجد صفوف رقمية صالحة بعد قراءة الملف.")
    st.stop()

df["net_exports_usd_m"] = df["exports_usd_m"] - df["imports_usd_m"]
df["export_import_coverage_pct"] = (df["exports_usd_m"] / df["imports_usd_m"].replace(0, pd.NA)) * 100

st.caption(f"مصدر البيانات الحالي: **{source_label}** | عدد السنوات: **{len(df)}**")
latest = df.iloc[-1]
previous = df.iloc[-2] if len(df) > 1 else None

st.header("1) لقطة المؤشرات")
c1, c2, c3, c4 = st.columns(4)
c1.metric("الصادرات", f'{latest["exports_usd_m"]:,.0f} مليون $')
c2.metric("الواردات", f'{latest["imports_usd_m"]:,.0f} مليون $')
c3.metric("فجوة التجارة", f'{latest["net_exports_usd_m"]:,.0f} مليون $')
c4.metric("التضخم", f'{latest["inflation_pct"]:,.1f}%')

st.caption(f"آخر سنة في البيانات: {int(latest['year'])}. الفجوة = الصادرات ناقص الواردات، ولا تمثل وحدها ميزان المدفوعات الكامل.")

st.header("2) اتجاه المؤشرات عبر الزمن")
metric = st.selectbox("اختاري المؤشر", [
    "exports_usd_m", "imports_usd_m", "net_exports_usd_m",
    "inflation_pct", "fx_reserves_usd_m", "gold_exports_usd_m",
    "agriculture_exports_usd_m"
], format_func=lambda x: AR.get(x, "صافي الصادرات"))
fig = px.line(df, x="year", y=metric, markers=True, title=AR.get(metric, metric))
fig.update_layout(xaxis_title="السنة", yaxis_title=AR.get(metric, metric), hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    fig2 = px.bar(df, x="year", y=["exports_usd_m", "imports_usd_m"],
                  barmode="group", title="مقارنة الصادرات والواردات")
    fig2.update_layout(xaxis_title="السنة", yaxis_title="مليون دولار",
                       legend_title="المؤشر")
    st.plotly_chart(fig2, use_container_width=True)
with right:
    fig3 = px.line(df, x="year", y=["gold_exports_usd_m", "agriculture_exports_usd_m"],
                   markers=True, title="مصادر مختارة للصادرات")
    fig3.update_layout(xaxis_title="السنة", yaxis_title="مليون دولار",
                       legend_title="المصدر")
    st.plotly_chart(fig3, use_container_width=True)

st.header("3) مختبر السيناريوهات")
st.write("جرّبي افتراضات حسابية لمعرفة أثرها المباشر على فجوة الصادرات والواردات. هذه ليست توقعات لسعر الجنيه.")
col1, col2, col3 = st.columns(3)
with col1:
    export_growth = st.slider("زيادة الصادرات المفترضة (%)", 0, 100, 10, 5)
with col2:
    import_reduction = st.slider("انخفاض الواردات المفترض (%)", 0, 50, 5, 5)
with col3:
    inflation_change = st.slider("تغير التضخم المفترض (نقطة مئوية)", -30, 30, -5, 1)

scenario_exports = latest["exports_usd_m"] * (1 + export_growth / 100)
scenario_imports = latest["imports_usd_m"] * (1 - import_reduction / 100)
scenario_gap = scenario_exports - scenario_imports
base_gap = latest["exports_usd_m"] - latest["imports_usd_m"]
scenario_inflation = max(0, latest["inflation_pct"] + inflation_change)

s1, s2, s3 = st.columns(3)
s1.metric("الصادرات في السيناريو", f"{scenario_exports:,.0f} مليون $")
s2.metric("الواردات في السيناريو", f"{scenario_imports:,.0f} مليون $")
s3.metric("فجوة التجارة في السيناريو", f"{scenario_gap:,.0f} مليون $",
          delta=f"{scenario_gap-base_gap:,.0f} مليون $ مقارنة بالأساس")
st.info(f"التضخم الافتراضي بعد التغيير: **{scenario_inflation:.1f}%**. هذا الحساب لا يثبت أن سعر الصرف سيتحسن؛ فالسعر يتأثر بعوامل أخرى كثيرة.")

st.header("4) فحص جودة البيانات")
quality = pd.DataFrame({
    "الفحص": ["عدد الصفوف", "سنوات مكررة", "قيم مفقودة", "قيم سالبة في المؤشرات"],
    "النتيجة": [
        len(df),
        int(df["year"].duplicated().sum()),
        int(df[REQUIRED].isna().sum().sum()),
        int((df[REQUIRED[1:]] < 0).sum().sum())
    ]
})
st.dataframe(quality, use_container_width=True, hide_index=True)

with st.expander("عرض البيانات المستخدمة"):
    display_df = df.copy()
    display_df = display_df.rename(columns=AR)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.download_button("تنزيل البيانات الحالية CSV",
                       data=df.to_csv(index=False).encode("utf-8-sig"),
                       file_name="sudan_economic_data.csv",
                       mime="text/csv")

st.header("5) ما الذي نحتاجه في النسخة البحثية؟")
st.markdown("""
- بيانات سنوية أو شهرية موثقة عن الصادرات والواردات.
- بيانات التضخم ومؤشرات الأسعار.
- بيانات الاحتياطيات وتدفقات النقد الأجنبي عند توفرها.
- بيانات إنتاج وصادرات الذهب والقطاعات الزراعية.
- مصدر واضح، وتاريخ نشر، ووحدة قياس لكل رقم.

**قاعدة المشروع:** لن نعرض أي رقم باعتباره حقيقة إلا إذا ربطناه بمصدر موثوق وتاريخ ووحدة قياس.
""")

st.caption("نسخة تعليمية أولية — لا تقدم توصيات استثمارية أو توقعاً لسعر الصرف.")
