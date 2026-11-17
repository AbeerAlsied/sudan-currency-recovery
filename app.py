import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. إعدادات الصفحة والهوية البصرية
st.set_page_config(
    page_title="الجنيه أولاً | مركز تحليل وإنقاذ الاقتصاد السوداني",
    page_icon="🇸🇩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحسين الخطوط والاتجاه العربي (RTL) لمنع أي تداخل على الجوال والويب
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', sans-serif !important;
}

.block-container { padding-top: 1.5rem; }

h1, h2, h3, h4, h5, h6, p, span, label, div, li {
    direction: rtl !important;
    text-align: right !important;
}

/* بطاقات المؤشرات */
[data-testid="stMetric"] {
    background: #f8fafc;
    padding: 16px;
    border-radius: 12px;
    border-right: 5px solid #123b5d;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

/* صناديق التشخيص والتحذير */
.diagnosis-box {
    background: #eef6fa;
    border-right: 5px solid #13a6a6;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
}

.warning-box {
    background: #fff8eb;
    border-right: 5px solid #d97706;
    padding: 14px;
    border-radius: 8px;
    margin-top: 10px;
}

.policy-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-right: 6px solid #123b5d;
    padding: 18px;
    border-radius: 10px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# 2. البيانات المرجعية (هيكل جاهز للربط بالمصادر الرسمية)
REQUIRED_COLS = [
    "year", "exports_usd_m", "imports_usd_m", "inflation_pct",
    "fx_reserves_usd_m", "gold_exports_usd_m", "agriculture_exports_usd_m",
    "essential_imports_usd_m"
]

AR_LABELS = {
    "year": "السنة",
    "exports_usd_m": "إجمالي الصادرات (مليون $)",
    "imports_usd_m": "إجمالي الواردات (مليون $)",
    "inflation_pct": "معدل التضخم السنوي (%)",
    "fx_reserves_usd_m": "الاحتياطيات الأجنبية (مليون $)",
    "gold_exports_usd_m": "صادرات الذهب (مليون $)",
    "agriculture_exports_usd_m": "الصادرات الزراعية والحيوانية (مليون $)",
    "essential_imports_usd_m": "الواردات الأساسية - قمح/دواء/وقود (مليون $)"
}

def load_demo_data():
    # بيانات هيكلية تجريبية لمحاكاة الاختلالات الاقتصادية (قابلة للاستبدال بملف CSV موثق)
    data = [
        [2018, 3485, 7350, 63.3, 1400, 1250, 1450, 3100],
        [2019, 3740, 8100, 51.0, 1250, 1300, 1600, 3400],
        [2020, 3800, 7950, 163.3, 1100, 1420, 1580, 3500],
        [2021, 4280, 8400, 359.1, 1000, 1850, 1650, 3800],
        [2022, 4357, 8900, 138.8, 950, 2020, 1590, 4100],
        [2023, 2150, 5200, 171.5, 650, 1150, 720, 2900],
        [2024, 1816, 4517, 210.0, 500, 1050, 540, 2750],
    ]
    return pd.DataFrame(data, columns=REQUIRED_COLS)

# 3. الشريط الجانبي وإدارة البيانات والتنقل
with st.sidebar:
    st.markdown("## 🇸🇩 الجنيه أولاً")
    st.caption("مركز ذكاء اقتصادي تفاعلي مبني على الأدلة")
    st.divider()
    
    page = st.radio(
        "أقسام المركز:",
        [
            "🏠 الرئيسية (ملخص الحالة)",
            "📊 التحليل الاقتصادي الذكي",
            "🪙 تحليل الذهب والتجارة",
            "📉 التضخم والقوة الشرائية",
            "🧪 مختبر إنقاذ الجنيه",
            "🤖 المستشار الاقتصادي",
            "📚 مركز البيانات والمصادر"
        ]
    )
    
    st.divider()
    st.subheader("⚙️ قاعدة البيانات")
    uploaded_file = st.file_uploader("استيراد بيانات موثقة (CSV)", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            data_status = "بيانات مرفوعة من المستخدم"
        except Exception as e:
            st.error(f"خطأ في قراءة الملف: {e}")
            st.stop()
    else:
        df = load_demo_data()
        data_status = "بيانات هيكلية تجريبية (للمعاينة والاختبار)"

# التحقق من سلامة الأعمدة والحسابات الأساسية
if not all(col in df.columns for col in REQUIRED_COLS):
    st.error("الملف المرفوع يفتقد لبعض الأعمدة القياسية المطلوبة. راجع قسم (مركز البيانات).")
    st.stop()

df = df.sort_values("year").reset_index(drop=True)
df["trade_balance"] = df["exports_usd_m"] - df["imports_usd_m"]
df["coverage_ratio"] = (df["exports_usd_m"] / df["imports_usd_m"]) * 100
df["gold_share_pct"] = (df["gold_exports_usd_m"] / df["exports_usd_m"]) * 100
df["agri_share_pct"] = (df["agriculture_exports_usd_m"] / df["exports_usd_m"]) * 100
df["non_essential_imports"] = df["imports_usd_m"] - df["essential_imports_usd_m"]

latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest

# ==========================================
# القسم 1: الرئيسية (ملخص حالة الاقتصاد)
# ==========================================
if page == "🏠 الرئيسية (ملخص الحالة)":
    st.title("🇸🇩 الجنيه أولاً — مركز تحليل وإنقاذ الاقتصاد السوداني")
    st.caption(f"حالة البيانات الحالية: **{data_status}** | سنة الأساس للتحليل: **{int(latest['year'])}**")
    
    # حساب مؤشر الاستقرار الاقتصادي المركب (من 100)
    coverage_score = min(latest["coverage_ratio"], 100) * 0.4
    inflation_score = max(0, (100 - min(latest["inflation_pct"], 100))) * 0.4
    diversification_score = max(0, (100 - latest["gold_share_pct"])) * 0.2
    stability_index = round(coverage_score + inflation_score + diversification_score, 1)

    if stability_index < 35:
        status_color = "🔴 وضع حرج (اختلال هيكلي حاد)"
    elif stability_index < 65:
        status_color = "🟡 وضع هش (يتطلب إصلاحات عاجلة)"
    else:
        status_color = "🟢 وضع مستقر نسبياً"

    # بطاقة التشخيص الفوري
    st.markdown(f"""
    <div class="diagnosis-box">
        <h4>🩺 التشخيص التنفيذي الفوري ({int(latest['year'])})</h4>
        <p><b>حالة المؤشر العام:</b> {status_color} ({stability_index} / 100 نقطة)</p>
        <p>يعاني الميزان التجاري من عجز قدره <b>{abs(latest['trade_balance']):,.1f} مليون دولار</b>، حيث لا تغطي الصادرات سوى <b>{latest['coverage_ratio']:.1f}%</b> من فاتورة الواردات. 
        كما يتركز الاقتصاد بشكل خطير في مورد واحد، إذ يمثل <b>الذهب {latest['gold_share_pct']:.1f}%</b> من إجمالي الصادرات، مما يجعل الجنيه مكشوفاً أمام أي صدمات في الإنتاج أو التهريب.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي الصادرات", f"{latest['exports_usd_m']:,.1f} م$", f"{latest['exports_usd_m'] - prev['exports_usd_m']:,.1f} م$")
    c2.metric("إجمالي الواردات", f"{latest['imports_usd_m']:,.1f} م$", f"{latest['imports_usd_m'] - prev['imports_usd_m']:,.1f} م$", delta_color="inverse")
    c3.metric("العجز التجاري", f"{abs(latest['trade_balance']):,.1f} م$", f"تغطية {latest['coverage_ratio']:.1f}%")
    c4.metric("معدل التضخم", f"{latest['inflation_pct']:.1f}%", f"{latest['inflation_pct'] - prev['inflation_pct']:+.1f}%", delta_color="inverse")

    st.subheader("مسار الفجوة التجارية عبر السنوات")
    fig_main = go.Figure()
    fig_main.add_trace(go.Bar(x=df["year"], y=df["exports_usd_m"], name="الصادرات", marker_color="#13a6a6"))
    fig_main.add_trace(go.Bar(x=df["year"], y=df["imports_usd_m"], name="الواردات", marker_color="#123b5d"))
    fig_main.update_layout(barmode="group", xaxis_title="السنة", yaxis_title="مليون دولار أمريكي", hovermode="x unified")
    st.plotly_chart(fig_main, use_container_width=True)

# ==========================================
# القسم 2: التحليل الاقتصادي الذكي
# ==========================================
elif page == "📊 التحليل الاقتصادي الذكي":
    st.title("📊 التشخيص الاقتصادي الذكي (قراءة ما وراء الأرقام)")
    
    selected_year = st.selectbox("اختاري السنة للتحليل التفصيلي:", df["year"].astype(int).tolist(), index=len(df)-1)
    row = df[df["year"] == selected_year].iloc[0]
    
    st.markdown(f"""
    <div class="policy-card">
        <h4>🔍 ماذا تعني أرقام سنة {int(row['year'])} اقتصادياً؟</h4>
        <ul>
            <li><b>فجوة النقد الأجنبي:</b> مقابل كل <b>100 دولار</b> دفعها السودان للاستيراد، لم يدخل البلاد من التصدير سوى <b>{row['coverage_ratio']:.1f} دولار</b> فقط. الفارق (<b>{100 - row['coverage_ratio']:.1f} دولار</b>) يمثل ضغطاً مباشراً يبحث عن تمويل أو يضغط على سعر الصرف في السوق الموازي.</li>
            <li><b>هشاشة الهيكل التصديري:</b> استحوذ الذهب على <b>{row['gold_share_pct']:.1f}%</b> من الصادرات مقابل <b>{row['agri_share_pct']:.1f}%</b> للقطاع الزراعي والحيواني، رغم أن الزراعة هي القطاع الأكثر تشغيلاً للسكان والأكثر استدامة.</li>
            <li><b>نزيف الواردات القابلة للإحلال:</b> من أصل <b>{row['imports_usd_m']:,.0f} مليون دولار</b> واردات، ذهب مبلغ <b>{row['non_essential_imports']:,.0f} مليون دولار</b> ({(row['non_essential_imports']/row['imports_usd_m'])*100:.1f}%) لسلع غير أساسية أو سلع يمكن تصنيعها محلياً.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(
            names=["صادرات الذهب", "الصادرات الزراعية", "صادرات أخرى"],
            values=[row["gold_exports_usd_m"], row["agriculture_exports_usd_m"], max(0, row["exports_usd_m"] - row["gold_exports_usd_m"] - row["agriculture_exports_usd_m"])],
            title=f"هيكل الصادرات في {selected_year}",
            color_discrete_sequence=["#d97706", "#13a6a6", "#123b5d"]
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col2:
        fig_imp = px.pie(
            names=["واردات أساسية (قمح/دواء/وقود)", "واردات قابلة للإحلال والتصنيع"],
            values=[row["essential_imports_usd_m"], row["non_essential_imports"]],
            title=f"هيكل الواردات في {selected_year}",
            color_discrete_sequence=["#123b5d", "#e11d48"]
        )
        st.plotly_chart(fig_imp, use_container_width=True)

# ==========================================
# القسم 3: تحليل الذهب والتجارة (اكتشاف الأسباب)
# ==========================================
elif page == "🪙 تحليل الذهب والتجارة":
    st.title("🪙 تشريح ملفات الأزمة: الذهب، الصادرات، والاستيراد")
    
    tab1, tab2, tab3 = st.tabs(["🪙 ملف الذهب (أين تذهب العائدات؟)", "🚢 ملف الصادرات (لماذا نبيع خاماً؟)", "📦 ملف الاستيراد (استنزاف الدولار)"])
    
    with tab1:
        st.subheader("تحليل الاعتماد المفرط على الذهب")
        st.write(f"يشكل الذهب حالياً **{latest['gold_share_pct']:.1f}%** من حصيلة الصادرات المعلنة.")
        st.markdown("""
        **الخلل الهيكلي المكتشف:**
        1. **تصدير الخام دون قيمة مضافة:** تصدير الذهب في صورته الأولية يحرم الخزينة من عائدات التصنيع والمشغولات.
        2. **فجوة التهريب والسياسات الشرائية:** عندما يشتري البنك المركزي الذهب بسعر أقل من السعر الموازي أو يتأخر في السداد، يتسرب الإنتاج عبر الحدود، فتظهر الأرقام في تقارير دول الجوار ولا تدخل الاحتياطي الأجنبي السوداني.
        """)
        fig_gold = px.line(df, x="year", y="gold_share_pct", markers=True, title="نسبة مساهمة الذهب في إجمالي الصادرات (%)")
        st.plotly_chart(fig_gold, use_container_width=True)
        
    with tab2:
        st.subheader("مأزق تصدير المواد الخام")
        st.markdown("""
        **لماذا عائداتنا ضعيفة رغم الموارد؟**
        * تصدير **السمسم، الفول السوداني، الصمغ العربي، والماشية** كمواد خام أو حية يترك هامش الربح الأكبر للدول المستوردة التي تعيد تصنيعها وتغليفها.
        * ضعف سلاسل الإمداد والنقل والتخزين يرفع تكلفة المنتج السوداني ويفقده التنافسية السعرية.
        """)
        fig_agri = px.area(df, x="year", y=["gold_exports_usd_m", "agriculture_exports_usd_m"], title="مقارنة تطور عائدات الذهب مقابل الزراعة (مليون $)")
        st.plotly_chart(fig_agri, use_container_width=True)

    with tab3:
        st.subheader("السلع التي تستنزف النقد الأجنبي")
        st.write(f"تبلغ فاتورة الواردات غير الأساسية والقابلة للإحلال المحلي **{latest['non_essential_imports']:,.1f} مليون دولار** سنوياً.")
        st.info("💡 **فرصة الإنقاذ المباشرة:** استهداف 30% فقط من هذه الواردات بالتصنيع المحلي يوفر نحو "
                f"**{latest['non_essential_imports']*0.3:,.1f} مليون دولار** سنوياً دون الحاجة لانتظار قروض خارجية.")

# ==========================================
# القسم 4: التضخم والقوة الشرائية
# ==========================================
elif page == "📉 التضخم والقوة الشرائية":
    st.title("📉 التضخم وتآكل القوة الشرائية للجنيه")
    
    st.markdown("""
    **الآلية الاقتصادية للتضخم في السودان:**
    يرتبط التضخم بمسارين متوازيين: **أولاً:** تمويل العجز الحكومي بالاستدانة من النظام المصرفي (طباعة النقود دون غطاء إنتاجي)، مما يزيد الكتلة النقدية المطاردة لسلع محدودة. **ثانياً:** تراجع سعر الصرف الذي يرفع تكلفة مدخلات الإنتاج المستوردة (التضخم المستورد).
    """)
    
    fig_inf = px.line(df, x="year", y="inflation_pct", markers=True, title="مسار معدل التضخم السنوي (%)")
    fig_inf.update_traces(line_color="#e11d48", line_width=3)
    st.plotly_chart(fig_inf, use_container_width=True)

    st.subheader("🧮 حاسبة تآكل القوة الشرائية (أثر التضخم التراكمي)")
    col_a, col_b = st.columns(2)
    with col_a:
        amount = st.number_input("أدخلي مبلغاً بالجنيه السوداني:", min_value=100, value=100000, step=1000)
    with col_b:
        start_yr = st.selectbox("سنة الأساس للمقارنة:", df["year"].astype(int).tolist()[:-1], index=0)
    
    sub_df = df[df["year"] > start_yr]
    erosion_factor = 1.0
    for inf in sub_df["inflation_pct"]:
        erosion_factor *= (1 + (inf / 100))
    
    real_value = amount / erosion_factor
    st.warning(f"مبلغ **{amount:,.0f} جنيه** في سنة **{start_yr}**، تعادل قوته الشرائية الحقيقية في **{int(latest['year'])}** حوالي **{real_value:,.1f} جنيه** فقط (فقد **{(1 - (1/erosion_factor))*100:.1f}%** من قيمته الحقيقية).")

# ==========================================
# القسم 5: مختبر إنقاذ الجنيه (أهم ميزة في المشروع)
# ==========================================
elif page == "🧪 مختبر إنقاذ الجنيه":
    st.title("🧪 مختبر السياسات وإنقاذ الجنيه")
    st.write("اختبري أثر السياسات الاقتصادية الحقيقية على الميزان التجاري وفجوة النقد الأجنبي مقارنة بسنة الأساس "
             f"**({int(latest['year'])})**.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 1️⃣ سياسة القيمة المضافة للزراعة")
        agri_boost = st.slider("زيادة عائدات الزراعة بالتصنيع (%)", 0, 150, 30, 5,
                               help="تحويل تصدير الخامات إلى زيوت، لحوم مبردة، وصمغ مصنع")
    with col2:
        st.markdown("#### 2️⃣ سياسة إحلال الواردات")
        import_sub = st.slider("تخفيض الواردات غير الأساسية (%)", 0, 60, 20, 5,
                               help="إنتاج السلع الاستهلاكية والغذائية محلياً")
    with col3:
        st.markdown("#### 3️⃣ حوكمة صادرات الذهب")
        gold_formal = st.slider("استعادة عائدات الذهب المهرب (%)", 0, 100, 25, 5,
                                help="توجيه الذهب للقنوات الرسمية عبر سياسات تسعير مرنة")

    # الحسابات الرياضية للسيناريو
    new_agri = latest["agriculture_exports_usd_m"] * (1 + agri_boost / 100)
    new_gold = latest["gold_exports_usd_m"] * (1 + gold_formal / 100)
    other_exports = max(0, latest["exports_usd_m"] - latest["agriculture_exports_usd_m"] - latest["gold_exports_usd_m"])
    
    sim_exports = new_agri + new_gold + other_exports
    sim_imports = latest["essential_imports_usd_m"] + (latest["non_essential_imports"] * (1 - import_sub / 100))
    
    base_balance = latest["trade_balance"]
    sim_balance = sim_exports - sim_imports
    net_gain = sim_balance - base_balance
    sim_coverage = (sim_exports / sim_imports) * 100

    st.divider()
    st.subheader("📊 نتائج محاكاة السياسات المختارة:")
    
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("الصادرات المتوقعة", f"{sim_exports:,.1f} م$", f"+{sim_exports - latest['exports_usd_m']:,.1f} م$")
    r2.metric("الواردات المتوقعة", f"{sim_imports:,.1f} م$", f"{sim_imports - latest['imports_usd_m']:,.1f} م$", delta_color="inverse")
    r3.metric("الميزان التجاري الجديد", f"{sim_balance:,.1f} م$", f"+{net_gain:,.1f} م$ تحسن")
    r4.metric("تغطية الواردات الجديدة", f"{sim_coverage:.1f}%", f"{sim_coverage - latest['coverage_ratio']:+.1f}%")

    # رسم مقارنة السيناريو
    comp_df = pd.DataFrame({
        "الحالة": ["الوضع الحالي", "سيناريو الإصلاح"],
        "الصادرات": [latest["exports_usd_m"], sim_exports],
        "الواردات": [latest["imports_usd_m"], sim_imports]
    })
    fig_sim = px.bar(comp_df, x="الحالة", y=["الصادرات", "الواردات"], barmode="group",
                     title="مقارنة الميزان التجاري: الوضع الحالي مقابل سيناريو السياسات",
                     color_discrete_sequence=["#13a6a6", "#123b5d"])
    st.plotly_chart(fig_sim, use_container_width=True)

    # القيد المنهجي الصارم
    st.markdown("""
    <div class="warning-box">
        <b>⚠️ تنبيه منهجي صارم للخبراء وصناع القرار:</b><br>
        تحسن الميزان التجاري وتقليص العجز في هذا السيناريو يمثل <b>شرطاً ضرورياً</b> لتخفيف الضغط عن العملة، لكنه <b>لا يعني تلقائياً ارتفاع سعر الجنيه</b> ما لم يترافق مع:
        (1) وقف التمويل بالعجز وطباعة النقود، (2) توحيد سعر الصرف واستعادة الثقة في الجهاز المصرفي، (3) الاستقرار الأمني والمؤسسي.
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# القسم 6: المستشار الاقتصادي الذكي (Rule-Based)
# ==========================================
elif page == "🤖 المستشار الاقتصادي":
    st.title("🤖 المستشار الاقتصادي (محرك التوصيات المبني على الأدلة)")
    st.write("يقوم النظام بفحص مؤشرات البيانات تلقائياً وتوليد توصيات محددة مرتبطة بأدلتها الرقمية وتكاليفها وعقباتها.")

    recommendations = []

    # القاعدة 1: هيمنة الذهب
    if latest["gold_share_pct"] > 45:
        recommendations.append({
            "title": "فك الارتباط الأحادي بالذهب عبر التصنيع الزراعي وتصدير القيمة المضافة",
            "evidence": f"يمثل الذهب حالياً {latest['gold_share_pct']:.1f}% من الصادرات مقابل {latest['agri_share_pct']:.1f}% فقط للزراعة، مما يجعل الاقتصاد رهينة لمورد واحد قابل للتهريب.",
            "why": "القطاع الزراعي والحيواني يمتلك ميزة نسبية مستدامة ويوفر دخلاً مباشراً لملايين الأسر، وتصنيعه يضاعف العائد الدولاري 3 إلى 4 أضعاف مقارنة بتصدير الخام.",
            "cost_obstacles": "التكلفة: متوسطة إلى مرتفعة (تمويل مصانع التكرير، المسالخ الحديثة، وسلاسل التبريد). العقبات: ضعف الطاقة الكهربائية، صعوبة التمويل المصرفي، ومشاكل النقل.",
            "kpi": "رفع مساهمة الصادرات الزراعية المصنعة إلى 35% من إجمالي الصادرات خلال 24 شهراً."
        })

    # القاعدة 2: نزيف الواردات
    if (latest["non_essential_imports"] / latest["imports_usd_m"]) > 0.30:
        recommendations.append({
            "title": "برنامج عاجل لإحلال الواردات الاستهلاكية والغذائية المصنعة",
            "evidence": f"يستنزف استيراد السلع غير الأساسية {latest['non_essential_imports']:,.0f} مليون دولار سنوياً ({(latest['non_essential_imports']/latest['imports_usd_m'])*100:.1f}% من إجمالي الواردات).",
            "why": "توفير النقد الأجنبي عن طريق تقليل الطلب على الدولار أسرع وأقل تكلفة من البحث عن قروض خارجية جديدة.",
            "cost_obstacles": "التكلفة: منخفضة (حوافز ضريبية وجمركية للمصانع المحلية القائمة). العقبات: ارتفاع تكاليف التشغيل والضرائب المحلية التي تجعل المنتج المستورد أرخص من المحلي.",
            "kpi": "خفض فاتورة الواردات غير الأساسية بنسبة 20% خلال السنة الأولى."
        })

    # القاعدة 3: التضخم المفرط
    if latest["inflation_pct"] > 50:
        recommendations.append({
            "title": "كبح التضخم عبر ضبط الكتلة النقدية وإصلاح المالية العامة",
            "evidence": f"بلغ معدل التضخم {latest['inflation_pct']:.1f}%، وهو مستوى يدمر القوة الشرائية ويفقد الجنيه وظيفته كمخزن للقيمة.",
            "why": "لا يمكن استقرار سعر الصرف في ظل نمو مستمر في عرض النقود الناتج عن تمويل عجز الموازنة من البنك المركزي.",
            "cost_obstacles": "التكلفة: إدارية وتشريعية بالأساس (رقمنة التحصيل الضريبي وترشيد الإنفاق). العقبات: مقاومة الإصلاح الضريبي وضغوط الإنفاق الطارئ.",
            "kpi": "خفض معدل التضخم السنوي إلى ما دون 40% خلال 18 شهراً."
        })

    for idx, rec in enumerate(recommendations, 1):
        st.markdown(f"""
        <div class="policy-card">
            <h4>📌 التوصية #{idx}: {rec['title']}</h4>
            <p><b>📊 الدليل من البيانات:</b> {rec['evidence']}</p>
            <p><b>🎯 لماذا هذه التوصية؟</b> {rec['why']}</p>
            <p><b>⚠️ التكلفة والعقبات المتوقعة:</b> {rec['cost_obstacles']}</p>
            <p><b>📏 مؤشر قياس النجاح (KPI):</b> {rec['kpi']}</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# القسم 7: مركز البيانات والمصادر
# ==========================================
elif page == "📚 مركز البيانات والمصادر":
    st.title("📚 مركز البيانات والمنهجية المرجعية")
    st.markdown("""
    **القاعدة الذهبية للمشروع:**
    > *"لن نعرض أي رقم باعتباره حقيقة اقتصادية نهائية إلا إذا ارتبط بمصدر رسمي موثوق، وتاريخ نشر محدد، ووحدة قياس واضحة."*
    """)

    st.subheader("1. الجدول الإحصائي المستخدم حالياً في التحليل")
    display_df = df.rename(columns=AR_LABELS)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.download_button(
        label="📥 تنزيل القالب القياسي للبيانات (CSV) لتعبئته بأرقام رسمية",
        data=df[REQUIRED_COLS].to_csv(index=False).encode("utf-8-sig"),
        file_name="sudan_economic_template.csv",
        mime="text/csv"
    )

    st.subheader("2. المصادر المعتمدة لتغذية النظام في النسخة البحثية")
    sources_df = pd.DataFrame([
        {"الجهة المصدرية": "بنك السودان المركزي", "البيانات المطلوبة": "التقارير السنوية، ميزان المدفوعات، حصائل الصادر والوارد، عرض النقود", "دورية النشر": "ربع سنوية / سنوية"},
        {"الجهة المصدرية": "الجهاز المركزي للإحصاء (CBS)", "البيانات المطلوبة": "الرقم القياسي لأسعار المستهلكين (التضخم)، إحصاءات التجارة الخارجية", "دورية النشر": "شهرية / سنوية"},
        {"الجهة المصدرية": "الشركة السودانية للموارد المعدنية", "البيانات المطلوبة": "إنتاج الذهب الرسمي، الكميات المصدرة، وعائدات التعدين", "دورية النشر": "سنوية"},
        {"الجهة المصدرية": "صندوق النقد والبنك الدوليين", "البيانات المطلوبة": "التقديرات المقارنة للنمو، الفجوة التمويلية، وتقارير الاقتصاد الكلي", "دورية النشر": "نصف سنوية"},
    ])
    st.table(sources_df)
