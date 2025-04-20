import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#               إعدادات أولية وتهيئة البيانات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.set_page_config(
    page_title="نظام المناوبات - المستشفى",
    layout="wide",
    page_icon="🏥"
)
st.title("📋 نظام متابعة المناوبات الشهرية")

EXCEL_PATH = "duty_roster_basic_info.xlsx"
REQUIRED_COLUMNS = ["National ID", "Employee No", "Name", "Present?", "Updated Date"]

@st.cache_data
def load_data():
    try:
        if os.path.exists(EXCEL_PATH):
            df = pd.read_excel(EXCEL_PATH, engine='openpyxl')
            
            # إضافة الأعمدة الناقصة إذا لم تكن موجودة
            for col in REQUIRED_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            
            return df
        else:
            # إنشاء ملف جديد مع جميع الأعمدة المطلوبة
            return pd.DataFrame(columns=REQUIRED_COLUMNS)
            
    except Exception as e:
        st.error(f"خطأ في تحميل الملف: {str(e)}")
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

# تحميل البيانات مع التحقق من الهيكل
df = load_data()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#               معالجة البيانات المفقودة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ملء القيم الفارغة وتحويل الأنواع
for col in REQUIRED_COLUMNS:
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str)
    else:
        df[col] = ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     جزء البحث
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
        results = df[df["Name"].str.contains(name_query, case=False, regex=False)]
else:
    emp_query = st.sidebar.text_input("اكتب جزءًا من الرقم")
    if emp_query:
        results = df[df["Employee No"].str.contains(emp_query, case=False, regex=False)]

# عرض النتائج مع تحسينات
st.subheader("🔎 نتائج البحث")
if not results.empty:
    st.dataframe(
        results[REQUIRED_COLUMNS].style.set_properties(**{'background-color': '#f8f9fa'}),
        height=400,
        use_container_width=True
    )
else:
    st.warning("⚠️ لا توجد نتائج مطابقة")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     جزء التحديث
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.divider()
st.subheader("🔄 تحديث حالة الموظف")

if not df.empty:
    try:
        selected_emp = st.selectbox(
            "اختر الموظف:",
            df["Employee No"].unique(),
            format_func=lambda x: f"{x} - {df[df['Employee No'] == x]['Name'].values[0]}"
        )
        
        emp_data = df[df["Employee No"] == selected_emp].iloc[0]
        
        with st.form("update_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("الاسم", value=emp_data["Name"])
            with col2:
                present = st.selectbox("الحضور", ["نعم", "لا"], index=0 if emp_data["Present?"] == "نعم" else 1)
                update_date = st.date_input("تاريخ التحديث", value=datetime.today())
            
            if st.form_submit_button("💾 حفظ التغييرات"):
                df.loc[df["Employee No"] == selected_emp, "Name"] = new_name
                df.loc[df["Employee No"] == selected_emp, "Present?"] = present
                df.loc[df["Employee No"] == selected_emp, "Updated Date"] = str(update_date)
                df.to_excel(EXCEL_PATH, index=False, engine='openpyxl')
                st.success("✅ تم التحديث بنجاح")
                st.rerun()
                
    except Exception as e:
        st.error(f"حدث خطأ: {str(e)}")
else:
    st.info("ℹ️ لا توجد بيانات متاحة للتحديث")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     تعليمات التشغيل
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.sidebar.divider()
st.sidebar.markdown("""
**التعليمات:**  
1. تأكد من تثبيت:  
   `pip install openpyxl`  
2. ابحث باستخدام جزء من الاسم/الرقم  
3. أغلق ملف Excel قبل التحديث  
""")
