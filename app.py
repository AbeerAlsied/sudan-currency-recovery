import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="الجنيه أولاً | بيانات السودان", page_icon="🇸🇩", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:1.5rem;max-width:1200px}
[data-testid="stMetric"]{background:#f2f6fa;padding:14px;border-radius:12px;border:1px solid #dce5ed}
h1,h2,h3{letter-spacing:0}
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).parent
def load_csv(name):
    return pd.read_csv(ROOT / name)

st.title("🇸🇩 الجنيه أولاً")
st.subheader("لوحة تحليل المؤشرات الاقتصادية السودانية")
st.success("هذه النسخة تستخدم بيانات منشورة في مراجعة بنك السودان المركزي: العرض الاقتصادي والمالي، يناير–يونيو 2026. بعض بيانات 2026 أولية أو تغطي نصف السنة فقط.")

trade = load_csv("trade_monthly_2026.csv")
infl = load_csv("inflation_monthly_2024_2026.csv")
commod = load_csv("commodity_exports_quarterly_2026.csv")
fx = load_csv("exchange_rate_snapshots.csv")

trade["month"] = pd.to_datetime(trade["month"])
infl["month"] = pd.to_datetime(infl["month"])
fx["period"] = pd.to_datetime(fx["period"])

st.caption("وحدة التجارة والصادرات: مليون دولار أمريكي. التضخم: %. سعر الصرف: جنيه سوداني لكل دولار أمريكي.")
st.header("1 | التجارة الخارجية — يناير إلى يونيو 2026")
total_exp = trade.exports_usd_m.sum()
total_imp = trade.imports_usd_m.sum()
gap = total_exp-total_imp
a,b,c = st.columns(3)
a.metric("إجمالي الصادرات", f"{total_exp:,.1f} مليون $")
b.metric("إجمالي الواردات", f"{total_imp:,.1f} مليون $")
c.metric("الرصيد التجاري", f"{gap:,.1f} مليون $")
fig = px.bar(trade, x="month", y=["exports_usd_m","imports_usd_m"], barmode="group",
             labels={"month":"الشهر","value":"مليون دولار","variable":"المؤشر"},
             title="الصادرات والواردات شهرياً — 2026")
fig.update_xaxes(tickformat="%b %Y")
st.plotly_chart(fig, use_container_width=True)

st.header("2 | التضخم")
latest_inf = infl.iloc[-1]
x,y = st.columns(2)
x.metric("التضخم في يونيو 2026", f'{latest_inf.inflation_pct:.1f}%')
y.metric("التغير من مارس إلى يونيو 2026",
         f'{infl.loc[infl.month == pd.Timestamp("2026-06-01"),"inflation_pct"].iloc[0] - infl.loc[infl.month == pd.Timestamp("2026-03-01"),"inflation_pct"].iloc[0]:+.1f} نقطة مئوية')
fig2 = px.line(infl, x="month", y="inflation_pct", markers=True,
               labels={"month":"الشهر","inflation_pct":"معدل التضخم %"},
               title="معدل التضخم الشهري المنشور — 2024 إلى يونيو 2026")
fig2.update_xaxes(tickformat="%b %Y")
st.plotly_chart(fig2, use_container_width=True)

st.header("3 | صادرات الذهب والزراعة — 2026")
fig3 = px.bar(commod, x="quarter", y=["gold_exports_usd_m","agriculture_exports_usd_m"],
              barmode="group", labels={"quarter":"الربع","value":"مليون دولار","variable":"نوع الصادرات"},
              title="صادرات الذهب والمنتجات الزراعية حسب الربع")
st.plotly_chart(fig3, use_container_width=True)
st.caption("القيم الزراعية محسوبة بجمع بنود السلع الزراعية الظاهرة في جدول الصادرات السلعية؛ راجع README لمعرفة البنود الداخلة.")

st.header("4 | سعر صرف الدولار مقابل الجنيه")
fig4 = px.line(fx, x="period", y="sdg_per_usd", markers=True,
               labels={"period":"الفترة","sdg_per_usd":"جنيه سوداني لكل دولار"},
               title="نقاط منشورة لمتوسط سعر شراء الدولار المرجح")
fig4.update_xaxes(tickformat="%b %Y")
st.plotly_chart(fig4, use_container_width=True)
st.dataframe(fx, use_container_width=True, hide_index=True)

with st.expander("عرض الجداول الخام"):
    st.subheader("التجارة الشهرية")
    st.dataframe(trade, use_container_width=True, hide_index=True)
    st.subheader("التضخم")
    st.dataframe(infl, use_container_width=True, hide_index=True)
    st.subheader("الصادرات حسب الربع")
    st.dataframe(commod, use_container_width=True, hide_index=True)

st.warning("تنبيه منهجي: تحسن أو تدهور الميزان التجاري لا يحدد سعر الصرف وحده. لا توجد في هذه اللوحة تنبؤات آلية بسعر الدولار، ولا يجوز اعتبار الأرقام وصفاً للسوق الموازي.")
st.markdown("**المصدر الأساسي:** بنك السودان المركزي، Economic & Financial Statistics Review, January–June 2026, Issue 2/2026. مصدر التضخم داخل التقرير: الجهاز المركزي للإحصاء. مصدر التجارة: قوات الجمارك السودانية ووزارة الطاقة والنفط.")
