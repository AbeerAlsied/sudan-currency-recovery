# -*- coding: utf-8 -*-
"""
الجنيه أولاً | مركز تحليل الاقتصاد السوداني
نسخة موثقة: بيانات بنك السودان المركزي حتى سبتمبر 2026.

التثبيت:
    pip install streamlit pandas plotly openpyxl

التشغيل:
    streamlit run app.py

مهم:
- كل مشاهدة رقمية مرتبطة بمصدر ورقم صفحة ووحدة وفترة وحالة البيانات.
- تاريخ الاطلاع المسجل: 17 نوفمبر 2026.
- لا تُعرض بيانات غير موجودة في المصادر المستخدمة.
"""

from io import BytesIO
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="الجنيه أولاً | اقتصاد السودان",
    page_icon="🇸🇩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# 1) سجل المصادر الرسمي
# =========================================================
ACCESS_DATE = "2026-11-17"

SOURCES = {
    "CBOS_09_2026": {
        "institution": "بنك السودان المركزي",
        "title": "The Economic Review — Issue No. 09/2026",
        "publication_year": 2026,
        "publication_date": "2026 (اليوم المحدد للنشر غير مذكور داخل التقرير)",
        "report_period": "01–30 سبتمبر 2026",
        "url": "https://cbos.gov.sd/sites/default/files/Sep%2026_EN.pdf",
        "landing_url": "https://cbos.gov.sd/en/periodicals-publications",
        "access_date": ACCESS_DATE,
        "note": "التقرير الدوري الصادر عن إدارة الإحصاء. النجمة (*) تعني بيانات أولية، والنجمتان (**) تعني بيانات معدلة بحسب مفتاح التقرير."
    },
    "CBOS_H1_2026": {
        "institution": "بنك السودان المركزي",
        "title": "Economic & Financial Statistics Review — January–June 2026",
        "publication_year": 2026,
        "publication_date": "2026 (التاريخ الدقيق غير مثبت في نسخة الجدول المستخدمة)",
        "report_period": "يناير–يونيو 2026",
        "url": "https://cbos.gov.sd/en/periodicals-publications",
        "landing_url": "https://cbos.gov.sd/en/periodicals-publications",
        "access_date": ACCESS_DATE,
        "note": "صفحة منشورات البنك تسجل إصدار مراجعة الإحصاءات الاقتصادية والمالية للنصف الأول 2026. لا تُستخدم أرقام هذا المصدر في الرسوم الحالية إلا عند إضافتها مع جدولها المحدد."
    },
}

def source_url(source_id, page=None):
    base = SOURCES[source_id]["url"]
    return f"{base}#page={page}" if page else base

# =========================================================
# 2) البيانات الخام — كل مجموعة لها مرجع صفحة وحالة
# =========================================================
# التضخم: معدل التضخم في نهاية الفترة، بالمئة.
inflation = pd.DataFrame([
    ("ديسمبر 2023", "2023-12", 92.7),
    ("ديسمبر 2024", "2024-12", 187.8),
    ("ديسمبر 2025", "2025-12", 68.2),
    ("يناير 2026", "2026-01", 60.3),
    ("فبراير 2026", "2026-02", 56.4),
    ("مارس 2026", "2026-03", 40.2),
    ("أبريل 2026", "2026-04", 45.8),
    ("مايو 2026", "2026-05", 44.5),
    ("يونيو 2026", "2026-06", 51.3),
    ("يوليو 2026", "2026-07", 41.6),
    ("أغسطس 2026", "2026-08", 26.1),
    ("سبتمبر 2026", "2026-09", 28.5),
], columns=["الفترة", "period_code", "التضخم السنوي (%)"])
inflation["source_id"] = "CBOS_09_2026"
inflation["source_page"] = 3
inflation["unit"] = "%"
inflation["data_status"] = "منشورة؛ حالة المراجعة غير موضحة لكل نقطة في جدول التضخم"
inflation["publication_year"] = 2026

# السيولة: مليون جنيه سوداني، نقاط منشورة في الرسم البياني في صفحة 1.
money = pd.DataFrame([
    ("ديسمبر 2025", "2025-12", 8828027, 25303107),
    ("يناير 2026", "2026-01", 9108813, 26742536),
    ("مارس 2026", "2026-03", 11641498, 32101028),
    ("يونيو 2026", "2026-06", 13122915, 36833648),
    ("سبتمبر 2026", "2026-09", 15677980, 42352800),
], columns=["الفترة", "period_code", "M1 (مليون جنيه)", "M2 (مليون جنيه)"])
money["M1 (مليار جنيه)"] = money["M1 (مليون جنيه)"] / 1000
money["M2 (مليار جنيه)"] = money["M2 (مليون جنيه)"] / 1000
money["source_id"] = "CBOS_09_2026"
money["source_page"] = 1
money["unit"] = "مليون جنيه سوداني"
money["data_status"] = "أولية (*) وفق ملاحظة الرسم في التقرير"
money["publication_year"] = 2026

# المؤشرات النقدية الأخرى، من جدول الصفحة الأولى.
bank_summary = pd.DataFrame([
    ("إجمالي أصول/خصوم المصارف", 48501317, "مليون جنيه سوداني", "أولية (*)", 1),
    ("إجمالي التمويل المصرفي", 9087061, "مليون جنيه سوداني", "أولية (*)", 1),
    ("إجمالي الودائع المصرفية", 33840977, "مليون جنيه سوداني", "أولية (*)", 1),
    ("نمو عرض النقود M2", 67.4, "%", "أولية (*)", 1),
], columns=["المؤشر", "القيمة", "الوحدة", "حالة البيانات", "صفحة المصدر"])
bank_summary["الفترة"] = "سبتمبر 2026"
bank_summary["source_id"] = "CBOS_09_2026"
bank_summary["publication_year"] = 2026

# سعر الصرف: متوسط أسعار الدولار المعلنة لدى البنوك ومكاتب الصرافة.
exchange = pd.DataFrame([
    ("البنوك التجارية", "شراء", 3748.21, 4582.09),
    ("البنوك التجارية", "بيع", 3789.50, 4624.24),
    ("مكاتب الصرافة", "شراء", 4388.43, 5984.39),
    ("مكاتب الصرافة", "بيع", 5010.23, 6065.32),
], columns=["القناة", "النوع", "أغسطس 2026", "سبتمبر 2026"])
exchange["source_id"] = "CBOS_09_2026"
exchange["source_page"] = 4
exchange["unit"] = "جنيه سوداني لكل دولار أمريكي"
exchange["data_status"] = "قيمة منشورة في التقرير؛ غير موسومة كأولية أو معدلة في هذا الجدول"
exchange["publication_year"] = 2026

# ميزان المدفوعات — مليون دولار أمريكي.
bop = pd.DataFrame([
    ("2024", "سنوي", -2312.1, -2410.4, -1285.6, 3134.5, 4420.1, -1124.8, "معدلة (*)"),
    ("2025", "سنوي", -3828.3, -3867.1, -3367.6, 3223.13, 6590.8, -499.4, "معدلة (*)"),
    ("الربع الأول 2026", "ربع سنوي", -1208.4, -1002.1, -926.8, 817.1, 1744.0, -75.3, "معدلة (*)"),
    ("الربع الثاني 2026", "ربع سنوي", -1388.6, -1278.6, -1000.9, 1320.4, 2321.2, -277.8, "معدلة (*)"),
    ("الربع الثالث 2026", "ربع سنوي", -950.6, -768.6, -517.0, 1668.1, 2185.1, -251.6, "أولية (**)"),
], columns=[
    "الفترة", "نوع الفترة", "الحساب الجاري (مليون دولار)",
    "السلع والخدمات (مليون دولار)", "ميزان تجارة السلع (مليون دولار)",
    "صادرات السلع (مليون دولار)", "واردات السلع (مليون دولار)",
    "ميزان تجارة الخدمات (مليون دولار)", "حالة البيانات"
])
bop["source_id"] = "CBOS_09_2026"
bop["source_page"] = 4
bop["unit"] = "مليون دولار أمريكي"
bop["publication_year"] = 2026

# التمويل حسب القطاع — رصيد التمويل وتدفق التمويل، مليون جنيه.
sector_finance = pd.DataFrame([
    ("الزراعة", 1954749, 28.1, 274112, 26.2),
    ("الصناعة", 1748430, 25.1, 193547, 18.5),
    ("النقل والتخزين", 251263, 3.6, 20236, 1.9),
    ("التجارة المحلية", 91314, 1.3, 17962, 1.7),
    ("الصادرات", 484841, 7.0, 49542, 4.7),
    ("الواردات", 758474, 10.9, 314099, 30.1),
    ("الإنشاءات", 155232, 2.2, 2200, 0.3),
    ("الطاقة والتعدين", 174035, 2.5, 43938, 4.2),
    ("مؤسسات مالية غير مصرفية", 51183, 0.7, 1750, 0.2),
    ("حكومات الولايات والمحليات", 9105, 0.1, 0, 0.0),
    ("أخرى", 1273654, 18.3, 127726, 12.2),
], columns=[
    "القطاع", "رصيد التمويل (مليون جنيه)", "حصة الرصيد (%)",
    "تمويل سبتمبر (مليون جنيه)", "حصة تمويل سبتمبر (%)"
])
sector_finance["الفترة"] = "سبتمبر 2026"
sector_finance["source_id"] = "CBOS_09_2026"
sector_finance["source_page"] = 2
sector_finance["unit"] = "مليون جنيه سوداني"
sector_finance["data_status"] = "أولية (*)"
sector_finance["publication_year"] = 2026

# =========================================================
# 3) بناء سجل تتبع لكل قيمة رقمية
# =========================================================
def provenance_row(indicator, period, value, unit, source_id, page, status):
    src = SOURCES[source_id]
    return {
        "المؤشر": indicator,
        "الفترة": period,
        "القيمة": value,
        "وحدة القياس": unit,
        "الجهة": src["institution"],
        "اسم التقرير": src["title"],
        "سنة النشر": src["publication_year"],
        "تاريخ النشر": src["publication_date"],
        "رقم العدد": "09/2026",
        "رقم الصفحة": page,
        "حالة البيانات": status,
        "تاريخ الاطلاع": src["access_date"],
        "رابط الجدول/التقرير": source_url(source_id, page),
        "ملاحظات المصدر": src["note"],
    }

provenance = []

for _, r in inflation.iterrows():
    provenance.append(provenance_row(
        "معدل التضخم في نهاية الفترة", r["الفترة"], r["التضخم السنوي (%)"],
        "%", "CBOS_09_2026", 3, r["data_status"]
    ))

for _, r in money.iterrows():
    for col, indicator in [
        ("M1 (مليون جنيه)", "عرض النقود الضيق M1"),
        ("M2 (مليون جنيه)", "عرض النقود الواسع M2")
    ]:
        provenance.append(provenance_row(
            indicator, r["الفترة"], r[col], "مليون جنيه سوداني",
            "CBOS_09_2026", 1, r["data_status"]
        ))

for _, r in bank_summary.iterrows():
    provenance.append(provenance_row(
        r["المؤشر"], r["الفترة"], r["القيمة"], r["الوحدة"],
        "CBOS_09_2026", int(r["صفحة المصدر"]), r["حالة البيانات"]
    ))

for _, r in exchange.iterrows():
    for month in ["أغسطس 2026", "سبتمبر 2026"]:
        provenance.append(provenance_row(
            f"سعر {r['النوع']} الدولار — {r['القناة']}",
            month, r[month], "جنيه سوداني لكل دولار أمريكي",
            "CBOS_09_2026", 4, r["data_status"]
        ))

bop_columns = [
    "الحساب الجاري (مليون دولار)", "السلع والخدمات (مليون دولار)",
    "ميزان تجارة السلع (مليون دولار)", "صادرات السلع (مليون دولار)",
    "واردات السلع (مليون دولار)", "ميزان تجارة الخدمات (مليون دولار)"
]
for _, r in bop.iterrows():
    for col in bop_columns:
        provenance.append(provenance_row(
            col.replace(" (مليون دولار)", ""), r["الفترة"], r[col],
            "مليون دولار أمريكي", "CBOS_09_2026", 4, r["حالة البيانات"]
        ))

for _, r in sector_finance.iterrows():
    for col in ["رصيد التمويل (مليون جنيه)", "حصة الرصيد (%)",
                "تمويل سبتمبر (مليون جنيه)", "حصة تمويل سبتمبر (%)"]:
        unit = "%" if "%" in col else "مليون جنيه سوداني"
        provenance.append(provenance_row(
            f"{col} — {r['القطاع']}", r["الفترة"], r[col], unit,
            "CBOS_09_2026", 2, r["data_status"]
        ))

provenance_df = pd.DataFrame(provenance)

# =========================================================
# 4) الواجهة
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
html, body, [class*="css"] {font-family:'Cairo',sans-serif;}
.stApp {background:#f3f6fa;}
section[data-testid="stSidebar"] {background:#102b46;}
section[data-testid="stSidebar"] * {color:white !important;}
.hero {background:linear-gradient(120deg,#102b46,#087f8c);color:white;
padding:26px 30px;border-radius:18px;margin-bottom:16px;direction:rtl;}
.hero h1 {font-size:30px;margin:0 0 8px;}
.hero p {margin:0;opacity:.95;}
.title {color:#102b46;font-size:22px;font-weight:800;border-right:5px solid #0b9b91;
padding-right:12px;margin:12px 0 16px;direction:rtl;}
.box {background:#e8f4f5;border-right:5px solid #0b9b91;padding:13px 16px;
border-radius:10px;direction:rtl;margin:8px 0;}
.warn {background:#fff4df;border-right:5px solid #e5a000;padding:13px 16px;
border-radius:10px;direction:rtl;margin:8px 0;}
.card {background:white;border:1px solid #e5eaf0;border-radius:14px;padding:14px 16px;
box-shadow:0 2px 8px rgba(20,40,60,.04);direction:rtl;min-height:100px;}
.label {color:#667788;font-size:13px;}
.value {color:#102b46;font-size:23px;font-weight:800;}
.note {color:#82909d;font-size:11px;}
div.stButton>button, div.stDownloadButton>button {
border-radius:10px;background:#087f8c;color:white;font-weight:700;}
a {color:#087f8c;}
</style>
""", unsafe_allow_html=True)

def section(title):
    st.markdown(f'<div class="title">{title}</div>', unsafe_allow_html=True)

def metric(label, value, note=""):
    st.markdown(
        f'<div class="card"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="note">{note}</div></div>',
        unsafe_allow_html=True
    )

def chart_line(df, x, y, title):
    fig = px.line(df, x=x, y=y, markers=True, title=title)
    fig.update_layout(template="plotly_white", title_x=.98, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

def chart_bar(df, x, y, title):
    fig = px.bar(df, x=x, y=y, text_auto=".2s", title=title)
    fig.update_layout(template="plotly_white", title_x=.98)
    st.plotly_chart(fig, use_container_width=True)

def source_card(source_id, page, status, unit, period):
    s = SOURCES[source_id]
    st.markdown(
        f"""<div class="box">
        <b>توثيق البيانات المعروضة</b><br>
        الجهة: {s['institution']}<br>
        التقرير: {s['title']} — سنة النشر: {s['publication_year']}<br>
        الفترة المرجعية: {period}<br>
        الصفحة: {page} | وحدة القياس: {unit}<br>
        حالة البيانات: {status}<br>
        تاريخ الاطلاع: {s['access_date']}<br>
        <a href="{source_url(source_id, page)}" target="_blank">فتح التقرير عند صفحة المصدر</a>
        </div>""",
        unsafe_allow_html=True
    )

def show_provenance_for(prefix):
    selected = provenance_df[provenance_df["المؤشر"].str.contains(prefix, case=False, na=False)]
    st.dataframe(selected, use_container_width=True, hide_index=True)

# =========================================================
# 5) القيم المحسوبة من بيانات المصدر
# =========================================================
latest_inflation = float(inflation.iloc[-1]["التضخم السنوي (%)"])
latest_m2_bn = float(money.iloc[-1]["M2 (مليار جنيه)"])
bank_sell = float(exchange[(exchange["القناة"] == "البنوك التجارية") &
                           (exchange["النوع"] == "بيع")]["سبتمبر 2026"].iloc[0])
bureau_sell = float(exchange[(exchange["القناة"] == "مكاتب الصرافة") &
                             (exchange["النوع"] == "بيع")]["سبتمبر 2026"].iloc[0])
quarterly_bop = bop[bop["نوع الفترة"] == "ربع سنوي"]
exports_9m = quarterly_bop["صادرات السلع (مليون دولار)"].sum()
imports_9m = quarterly_bop["واردات السلع (مليون دولار)"].sum()
goods_balance_9m = quarterly_bop["ميزان تجارة السلع (مليون دولار)"].sum()
current_account_9m = quarterly_bop["الحساب الجاري (مليون دولار)"].sum()

# =========================================================
# 6) التنقل
# =========================================================
pages = [
    "مركز القيادة",
    "التضخم والقوة الشرائية",
    "الجنيه وسعر الصرف",
    "السيولة والسياسة النقدية",
    "التجارة وميزان المدفوعات",
    "التمويل والقطاعات الإنتاجية",
    "مختبر السياسات",
    "المستشار الاقتصادي",
    "مركز توثيق البيانات",
]
st.sidebar.markdown("## 🇸🇩 الجنيه أولاً")
st.sidebar.caption("مركز تحليل الاقتصاد السوداني")
page = st.sidebar.radio("اختاري القسم", pages)
st.sidebar.markdown("---")
st.sidebar.caption("آخر بيانات شهرية: سبتمبر 2026")
st.sidebar.caption("التجارة الخارجية: حتى الربع الثالث 2026")
st.sidebar.caption(f"تاريخ الاطلاع المسجل: {ACCESS_DATE}")

st.markdown("""
<div class="hero">
<h1>🇸🇩 الجنيه أولاً</h1>
<p>مركز تحليل الاقتصاد السوداني — أرقام منشورة، توثيق قابل للتتبع، وتجارب سياسات افتراضية.</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="box"><b>منهجية التوثيق:</b> كل رقم في الجداول والمؤشرات مرتبط باسم التقرير، '
    'سنة النشر، صفحة المصدر، وحدة القياس، حالة البيانات، وتاريخ الاطلاع. '
    'لا تعني كلمة «منشورة» أن الرقم نهائي إذا لم يحدد التقرير حالته.</div>',
    unsafe_allow_html=True
)

# =========================================================
# 7) الصفحات
# =========================================================
if page == "مركز القيادة":
    section("لوحة القيادة الاقتصادية — أحدث بيانات منشورة")
    cols = st.columns(4)
    with cols[0]:
        metric("التضخم السنوي", f"{latest_inflation:.1f}%", "سبتمبر 2026 — نهاية الفترة")
    with cols[1]:
        metric("عرض النقود M2", f"{latest_m2_bn:,.1f}", "مليار جنيه — سبتمبر 2026")
    with cols[2]:
        metric("بيع الدولار بالبنوك", f"{bank_sell:,.2f}", "جنيه/دولار — سبتمبر 2026")
    with cols[3]:
        metric("بيع الدولار بالصرافة", f"{bureau_sell:,.2f}", "جنيه/دولار — سبتمبر 2026")

    cols = st.columns(3)
    with cols[0]:
        metric("صادرات السلع", f"{exports_9m:,.1f} مليون $", "يناير–سبتمبر 2026")
    with cols[1]:
        metric("واردات السلع", f"{imports_9m:,.1f} مليون $", "يناير–سبتمبر 2026")
    with cols[2]:
        metric("عجز تجارة السلع", f"{abs(goods_balance_9m):,.1f} مليون $", "يناير–سبتمبر 2026")

    section("قراءة سريعة للاتجاهات")
    c1, c2 = st.columns(2)
    with c1:
        chart_line(inflation, "الفترة", "التضخم السنوي (%)", "التضخم السنوي — نهاية الفترة")
        source_card("CBOS_09_2026", 3, inflation.iloc[-1]["data_status"], "%", "ديسمبر 2023–سبتمبر 2026")
    with c2:
        chart_line(money, "الفترة", "M2 (مليار جنيه)", "عرض النقود M2 — مليار جنيه")
        source_card("CBOS_09_2026", 1, "أولية (*)", "مليون جنيه سوداني", "ديسمبر 2025–سبتمبر 2026")
    st.markdown(
        '<div class="warn">لا تكفي هذه المؤشرات وحدها للحكم على الاقتصاد. '
        'ينبغي قراءتها مع الإنتاج والتشغيل والدخل والأسعار وتوفر السلع والظروف الأمنية.</div>',
        unsafe_allow_html=True
    )

elif page == "التضخم والقوة الشرائية":
    section("التضخم والقوة الشرائية")
    a, b = st.columns(2)
    with a:
        metric("التضخم السنوي في سبتمبر 2026", "28.5%", "نهاية الفترة")
    with b:
        metric("التضخم السنوي في ديسمبر 2024", "187.8%", "نهاية الفترة")
    chart_line(inflation, "الفترة", "التضخم السنوي (%)", "التضخم السنوي في السودان")
    source_card("CBOS_09_2026", 3, "حالة المراجعة غير موضحة لكل نقطة في جدول التضخم", "%", "ديسمبر 2023–سبتمبر 2026")
    st.subheader("سجل نقاط التضخم")
    st.dataframe(inflation.drop(columns=["period_code"]), use_container_width=True, hide_index=True)
    with st.expander("تفاصيل توثيق كل نقطة"):
        show_provenance_for("معدل التضخم")
    st.markdown(
        '<div class="warn">التضخم السنوي لا يساوي الزيادة الشهرية في الأسعار. '
        'ولا نحسب القوة الشرائية التراكمية من نسب سنوية متداخلة؛ نحتاج سلسلة مؤشر أسعار المستهلك أو التضخم الشهري المتتابع.</div>',
        unsafe_allow_html=True
    )

elif page == "الجنيه وسعر الصرف":
    section("سعر الصرف")
    st.write("متوسط أسعار الدولار المعلنة لدى البنوك التجارية ومكاتب الصرافة كما في 30 سبتمبر 2026.")
    long_fx = exchange.melt(
        id_vars=["القناة", "النوع"], value_vars=["أغسطس 2026", "سبتمبر 2026"],
        var_name="الشهر", value_name="جنيه لكل دولار"
    )
    fig = px.bar(long_fx, x="القناة", y="جنيه لكل دولار", color="الشهر",
                 barmode="group", facet_col="النوع", title="مقارنة أسعار الشراء والبيع")
    fig.update_layout(template="plotly_white", title_x=.98)
    st.plotly_chart(fig, use_container_width=True)
    source_card("CBOS_09_2026", 4, exchange.iloc[0]["data_status"],
                "جنيه سوداني لكل دولار أمريكي", "أغسطس وسبتمبر 2026")
    st.dataframe(exchange.drop(columns=["source_id", "source_page", "unit", "data_status", "publication_year"]),
                 use_container_width=True, hide_index=True)
    with st.expander("توثيق كل سعر صرف"):
        show_provenance_for("سعر")
    st.markdown(
        '<div class="warn">سعر مكاتب الصرافة ليس بالضرورة سعر السوق الموازي. '
        'التقرير يعرض قنوات مصرفية وصرافة؛ لذلك لا نعيد تسمية هذه القيم باعتبارها أسعاراً غير رسمية.</div>',
        unsafe_allow_html=True
    )

elif page == "السيولة والسياسة النقدية":
    section("السيولة والسياسة النقدية")
    a, b, c = st.columns(3)
    with a:
        metric("M2 في سبتمبر 2026", f"{latest_m2_bn:,.1f} مليار", "مليون جنيه ÷ 1000")
    with b:
        metric("نمو M2 المنشور", "67.4%", "كما ورد في جدول المؤشرات النقدية")
    with c:
        metric("إجمالي التمويل المصرفي", "9,087,061 مليون", "جنيه سوداني — سبتمبر 2026")
    chart_line(money, "الفترة", "M2 (مليار جنيه)", "تطور عرض النقود M2")
    chart_line(money, "الفترة", "M1 (مليار جنيه)", "تطور عرض النقود M1")
    source_card("CBOS_09_2026", 1, "أولية (*) في الرسم؛ راجعي حاشية الجدول", "مليون جنيه سوداني", "ديسمبر 2025–سبتمبر 2026")
    st.subheader("المؤشرات المصرفية")
    st.dataframe(bank_summary.drop(columns=["source_id", "publication_year"]),
                 use_container_width=True, hide_index=True)
    with st.expander("توثيق المؤشرات النقدية والمصرفية"):
        show_provenance_for("عرض النقود")
        show_provenance_for("إجمالي")

elif page == "التجارة وميزان المدفوعات":
    section("التجارة الخارجية وميزان المدفوعات")
    st.markdown('<div class="warn">بيانات 2026 هنا تغطي الربع الأول والثاني والثالث فقط؛ لا تمثل السنة كاملة.</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        metric("صادرات السلع 2026", f"{exports_9m:,.1f} مليون $", "يناير–سبتمبر")
    with c2:
        metric("واردات السلع 2026", f"{imports_9m:,.1f} مليون $", "يناير–سبتمبر")
    with c3:
        metric("ميزان تجارة السلع", f"{goods_balance_9m:,.1f} مليون $", "يناير–سبتمبر — عجز")
    c1, c2 = st.columns(2)
    with c1:
        chart_line(bop, "الفترة", "الحساب الجاري (مليون دولار)", "رصيد الحساب الجاري")
    with c2:
        chart_line(bop, "الفترة", "ميزان تجارة السلع (مليون دولار)", "ميزان تجارة السلع")
    trade = bop.melt(id_vars=["الفترة"], value_vars=[
        "صادرات السلع (مليون دولار)", "واردات السلع (مليون دولار)"
    ], var_name="البند", value_name="مليون دولار")
    fig = px.bar(trade, x="الفترة", y="مليون دولار", color="البند",
                 barmode="group", title="صادرات وواردات السلع")
    fig.update_layout(template="plotly_white", title_x=.98)
    st.plotly_chart(fig, use_container_width=True)
    source_card("CBOS_09_2026", 4, "2024 و2025 وQ1 وQ2 2026 معدلة (*)؛ Q3 2026 أولية (**)",
                "مليون دولار أمريكي", "2024 و2025 سنوياً؛ 2026 ربع سنوي حتى Q3")
    st.dataframe(bop.drop(columns=["source_id", "source_page", "unit", "publication_year"]),
                 use_container_width=True, hide_index=True)
    with st.expander("توثيق كل رقم في ميزان المدفوعات"):
        show_provenance_for("الحساب")
        show_provenance_for("صادرات")
        show_provenance_for("واردات")
        show_provenance_for("ميزان")

elif page == "التمويل والقطاعات الإنتاجية":
    section("التمويل المصرفي حسب القطاعات")
    st.markdown('<div class="warn">هذه بيانات تمويل مصرفي، وليست قياساً لقيمة الإنتاج أو مساهمة القطاع في الناتج المحلي.</div>',
                unsafe_allow_html=True)
    sf = sector_finance.sort_values("حصة الرصيد (%)", ascending=True)
    chart_bar(sf, "القطاع", "حصة الرصيد (%)", "حصة القطاعات من رصيد التمويل المصرفي")
    sf2 = sector_finance.sort_values("حصة تمويل سبتمبر (%)", ascending=True)
    chart_bar(sf2, "القطاع", "حصة تمويل سبتمبر (%)", "حصة القطاعات من تمويل سبتمبر")
    source_card("CBOS_09_2026", 2, "أولية (*)", "مليون جنيه سوداني ونسبة مئوية", "نهاية سبتمبر 2026")
    st.dataframe(sector_finance.drop(columns=["source_id", "source_page", "unit", "data_status", "publication_year"]),
                 use_container_width=True, hide_index=True)
    with st.expander("توثيق قيم كل قطاع"):
        show_provenance_for("القطاع")
    st.info("لا نستنتج من ارتفاع التمويل أن إنتاج القطاع ارتفع؛ ذلك يحتاج بيانات إنتاج مستقلة.")

elif page == "مختبر السياسات":
    section("مختبر سيناريوهات التجارة")
    st.markdown(
        '<div class="warn">محاكاة حسابية افتراضية باستخدام بيانات الصادرات والواردات المنشورة لأول 9 أشهر من 2026. '
        'ليست توقعاً اقتصادياً، ولا تقيس أثر السيناريو على الأسعار أو سعر الصرف أو الوظائف.</div>',
        unsafe_allow_html=True
    )
    export_growth = st.slider("افتراض زيادة الصادرات (%)", 0, 50, 10, 5)
    import_cut_pct = st.slider("افتراض خفض الواردات (%)", 0, 30, 5, 5)
    protected_imports_pct = st.slider("النسبة التي نفترض حمايتها من الواردات الضرورية (%)", 50, 100, 80, 5)
    max_cut = imports_9m * (1 - protected_imports_pct / 100)
    requested_cut = imports_9m * import_cut_pct / 100
    actual_cut = min(max_cut, requested_cut)
    simulated_exports = exports_9m * (1 + export_growth / 100)
    simulated_imports = imports_9m - actual_cut
    before = exports_9m - imports_9m
    after = simulated_exports - simulated_imports
    a, b, c = st.columns(3)
    with a:
        metric("الرصيد قبل السيناريو", f"{before:,.1f} مليون $", "محسوب من Q1–Q3 2026")
    with b:
        metric("الرصيد بعد السيناريو", f"{after:,.1f} مليون $", "نتيجة افتراضية")
    with c:
        metric("التحسن الحسابي", f"{after-before:,.1f} مليون $", "مليون دولار")
    st.write(f"خفض الواردات في النموذج: **{actual_cut:,.1f} مليون دولار**.")
    if requested_cut > max_cut:
        st.warning("تم تقييد الخفض وفق نسبة الواردات التي اخترت حمايتها.")
    compare = pd.DataFrame({
        "الحالة": ["البيانات المنشورة", "السيناريو الافتراضي"],
        "الصادرات": [exports_9m, simulated_exports],
        "الواردات": [imports_9m, simulated_imports],
    })
    fig = go.Figure()
    fig.add_bar(name="الصادرات", x=compare["الحالة"], y=compare["الصادرات"])
    fig.add_bar(name="الواردات", x=compare["الحالة"], y=compare["الواردات"])
    fig.update_layout(barmode="group", template="plotly_white", title="قبل وبعد السيناريو", title_x=.98)
    st.plotly_chart(fig, use_container_width=True)
    source_card("CBOS_09_2026", 4, "مدخلات السيناريو: Q1 وQ2 معدلة؛ Q3 أولية",
                "مليون دولار أمريكي", "يناير–سبتمبر 2026")
    st.caption("خفض الواردات بصورة عشوائية قد يضر الغذاء والدواء والوقود ومدخلات الإنتاج.")

elif page == "المستشار الاقتصادي":
    section("المستشار الاقتصادي — قراءة أولية مدعومة بالأرقام")
    findings = [
        ("التضخم",
         f"بلغ التضخم السنوي 28.5% في سبتمبر 2026 مقابل 26.1% في أغسطس 2026.",
         "متابعة أسعار الغذاء والنقل والطاقة شهرياً وتحليل أسباب تغير الأسعار.",
         "CBOS_09_2026", 3, "%", "سبتمبر 2026"),
        ("التجارة الخارجية",
         f"بلغ عجز تجارة السلع المحسوب من Q1–Q3 نحو {abs(goods_balance_9m):,.1f} مليون دولار.",
         "دراسة كلفة الإنتاج والنقل والتخزين وإزالة عوائق وصول المنتجين للأسواق.",
         "CBOS_09_2026", 4, "مليون دولار أمريكي", "يناير–سبتمبر 2026"),
        ("الحساب الجاري",
         f"بلغ عجز الحساب الجاري المحسوب من الأرباع الثلاثة الأولى {abs(current_account_9m):,.1f} مليون دولار.",
         "تحليل السلع والخدمات والدخل والتحويلات معاً، لا التركيز على بند منفرد.",
         "CBOS_09_2026", 4, "مليون دولار أمريكي", "يناير–سبتمبر 2026"),
        ("السيولة",
         f"بلغ عرض النقود M2 نحو {latest_m2_bn:,.1f} مليار جنيه في سبتمبر 2026.",
         "متابعة مصادر نمو السيولة وصلتها بالائتمان والإنفاق والأسعار والإنتاج.",
         "CBOS_09_2026", 1, "مليار جنيه سوداني (تحويل من مليون)", "سبتمبر 2026"),
        ("سعر الصرف",
         f"بلغ سعر بيع الدولار 4,624.24 جنيهاً في البنوك و6,065.32 في مكاتب الصرافة.",
         "تحسين شفافية التسعير وتوفر النقد الأجنبي وعدم الخلط بين أسعار الصرافة والسوق الموازي.",
         "CBOS_09_2026", 4, "جنيه سوداني لكل دولار", "30 سبتمبر 2026"),
    ]
    for title, evidence, action, sid, pg, unit, period in findings:
        with st.container(border=True):
            st.markdown(f"### {title}")
            st.write("**ما تقوله البيانات:** " + evidence)
            st.write("**مسار يستحق الدراسة:** " + action)
            s = SOURCES[sid]
            st.markdown(f"[المصدر — {s['title']}، صفحة {pg}]({source_url(sid, pg)})")
            st.caption(f"الوحدة: {unit} | الفترة: {period} | سنة النشر: {s['publication_year']} | الاطلاع: {ACCESS_DATE}")
    st.warning("هذه قراءة وصفية أولية وليست توصية استثمارية أو خطة حكومية. السياسات تحتاج دراسات أثر وتكلفة وبيانات اجتماعية وإنتاجية.")

elif page == "مركز توثيق البيانات":
    section("مركز توثيق البيانات والمراجع")
    st.write("هذا القسم هو سجل الإسناد التفصيلي للقيم المستخدمة في المؤشرات والرسوم. كل صف يمثل رقماً محدداً وفترة محددة.")
    st.subheader("المصدر الأساسي")
    src = SOURCES["CBOS_09_2026"]
    st.markdown(f"**الجهة:** {src['institution']}")
    st.markdown(f"**اسم التقرير:** {src['title']}")
    st.markdown(f"**سنة النشر:** {src['publication_year']}")
    st.markdown(f"**الفترة التي يغطيها:** {src['report_period']}")
    st.markdown(f"**تاريخ الاطلاع:** {src['access_date']}")
    st.markdown(f"[فتح التقرير الأصلي PDF]({src['url']})")
    st.markdown(f"[صفحة منشورات بنك السودان المركزي]({src['landing_url']})")
    st.info("مفتاح التقرير: (*) بيانات معدلة في جدول ميزان المدفوعات؛ (**) بيانات أولية في جدول ميزان المدفوعات. وفي الجداول الأخرى يُتبع تعريف النجمة المكتوب بجانب الجدول نفسه.")
    st.subheader("البحث داخل سجل الأرقام")
    indicator_filter = st.text_input("اكتبي اسم المؤشر للبحث", placeholder="مثال: التضخم، M2، الصادرات، الزراعة")
    status_options = ["الكل"] + sorted(provenance_df["حالة البيانات"].dropna().unique().tolist())
    status_filter = st.selectbox("حالة البيانات", status_options)
    filtered = provenance_df.copy()
    if indicator_filter.strip():
        filtered = filtered[filtered["المؤشر"].str.contains(indicator_filter.strip(), case=False, na=False)]
    if status_filter != "الكل":
        filtered = filtered[filtered["حالة البيانات"] == status_filter]
    st.caption(f"عدد السجلات المعروضة: {len(filtered)} من أصل {len(provenance_df)}")
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=520)
    st.subheader("تنزيل البيانات الموثقة")
    excel = BytesIO()
    with pd.ExcelWriter(excel, engine="openpyxl") as writer:
        inflation.drop(columns=["period_code"]).to_excel(writer, sheet_name="Inflation", index=False)
        money.drop(columns=["period_code"]).to_excel(writer, sheet_name="Money_Supply", index=False)
        bank_summary.to_excel(writer, sheet_name="Bank_Summary", index=False)
        exchange.to_excel(writer, sheet_name="Exchange_Rates", index=False)
        bop.to_excel(writer, sheet_name="Balance_of_Payments", index=False)
        sector_finance.to_excel(writer, sheet_name="Sector_Finance", index=False)
        provenance_df.to_excel(writer, sheet_name="Data_Provenance", index=False)
        pd.DataFrame([{
            "source_id": k, **v
        } for k, v in SOURCES.items()]).to_excel(writer, sheet_name="Sources", index=False)
    st.download_button(
        "تنزيل ملف Excel مع سجل المصادر لكل رقم",
        data=excel.getvalue(),
        file_name="Sudan_Economic_Data_2026_with_sources.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.subheader("حدود التغطية")
    st.markdown("""
    - لا توجد في قاعدة البيانات الحالية أرقام موثقة للذهب أو الإنتاج الزراعي أو الناتج المحلي أو العجز المالي.
    - لا تُعامل بيانات مكاتب الصرافة كسعر السوق الموازي.
    - بيانات ميزان المدفوعات السنوية 2024 و2025 وبيانات Q1 وQ2 2026 موسومة كمعدلة في التقرير، بينما Q3 2026 أولية.
    - بيانات التمويل القطاعي في سبتمبر 2026 أولية، وهي تمويل مصرفي وليست إنتاجاً.
    - تاريخ النشر الدقيق غير ظاهر في متن تقرير سبتمبر؛ لذلك يوثق التطبيق سنة النشر 2026 ولا يخترع يوماً للنشر.
    """)

st.markdown("---")
st.markdown(
    f'<div style="text-align:center;color:#758596;font-size:12px;direction:rtl">'
    f'الجنيه أولاً | بنك السودان المركزي — بيانات حتى سبتمبر 2026 | تاريخ الاطلاع {ACCESS_DATE}'
    f'</div>',
    unsafe_allow_html=True
)
