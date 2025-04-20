import streamlit as st
import pandas as pd
from datetime import datetime
import os

# تهيئة الصفحة
st.set_page_config(
    page_title="نظام المناوبات - المستشفى",
    layout="wide",
    page_icon="🏥"
)
st.title("📋 نظام متابعة المناوبات الشهرية")

EXCEL_PATH = "duty_roster_basic_info.xlsx"

@st.cache_data
def load_data():
    try:
        if os.path.exists(EXCEL_PATH):
            return pd.read_excel(EXCEL_PATH, engine='openpyxl')
        else:
            return pd.DataFrame(columns=[
                "National ID", "Employee No", 
                "Name", "Present?", "Updated Date"
            ])
    except Exception as e:
        st.error(f"خطأ في تحميل الملف: {str(e)}")
        return pd.DataFrame()

# تحميل البيانات
df = load_data()

# معالجة البيانات المفقودة
df["Name"] = df["Name"].fillna("").astype(str)
df["Employee No"] = df["Employee No"].astype(str).str.strip()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                  جزء البحث والتصفية
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.sidebar.header("🔍 بحث متقدم")
search_type = st.sidebar.radio(
    "نوع البحث:",
    ["بالاسم", "برقم الموظف"],
    horizontal=True
)

results = df.copy()
if search_type == "بالاسم":
    name_query = st.sidebar.text_input("اكتب جزءًا من الاسم")
    if name_query:
        results = df[
            df["Name"].str.contains(name_query, case=False, na=False, regex=False)
        ]
else:
    emp_query = st.sidebar.text_input("اكتب جزءًا من الرقم")
    if emp_query:
        results = df[
            df["Employee No"].str.contains(emp_query, case=False, na=False, regex=False)
        ]

# عرض النتائج
st.subheader("🔎 نتائج البحث")
if not results.empty:
    st.dataframe(
        results.style.set_properties(
            **{'background-color': '#f5f5f5', 'color': 'black'}
        ),
        height=400,
        use_container_width=True
    )
else:
    st.warning("⚠️ لا توجد نتائج مطابقة")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                  جزء تحديث البيانات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.divider()
st.subheader("🔄 تحديث حالة الموظف")

if not df.empty:
    selected_emp = st.selectbox(
        "اختر الموظف:",
        df["Employee No"].unique(),
        format_func=lambda x: f"{x} - {df[df['Employee No']==x]['Name'].iloc[0]}"
    )
    
    emp_data = df[df["Employee No"] == selected_emp].iloc[0]
    
    with st.form("update_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("الاسم", value=emp_data["Name"])
            emp_id = st.text_input("رقم الموظف", value=emp_data["Employee No"], disabled=True)
        with col2:
            present = st.selectbox("الحضور", ["نعم", "لا"], index=0 if emp_data["Present?"] == "نعم" else 1)
            update_date = st.date_input("تاريخ التحديث", value=datetime.today())
        
        if st.form_submit_button("💾 حفظ التغييرات"):
            try:
                df.loc[df["Employee No"] == selected_emp, "Name"] = new_name
                df.loc[df["Employee No"] == selected_emp, "Present?"] = present
                df.loc[df["Employee No"] == selected_emp, "Updated Date"] = update_date
                df.to_excel(EXCEL_PATH, index=False, engine='openpyxl')
                st.success("✅ تم التحديث بنجاح")
                st.rerun()
            except PermissionError:
                st.error("❌ يرجى إغلاق ملف Excel قبل الحفظ")
else:
    st.info("ℹ️ لا توجد بيانات متاحة للتحديث")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                  تعليمات التشغيل
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.sidebar.divider()
st.sidebar.markdown("""
**تعليمات التشغيل:**  
1. تأكد من تثبيت المكتبات المطلوبة:  
   `pip install openpyxl`  
2. اختبر البحث بأجزاء من الاسم أو الرقم  
3. أغلق ملف Excel أثناء التشغيل
""")
