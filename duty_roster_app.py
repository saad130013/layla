import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="نظام المناوبات - المستشفى", layout="wide")
st.title("📋 نظام متابعة المناوبات الشهرية")

EXCEL_PATH = "duty_roster_basic_info.xlsx"

@st.cache_data
def load_data():
    try:
        if os.path.exists(EXCEL_PATH):
            # تحديد محرك openpyxl لملفات xlsx
            return pd.read_excel(EXCEL_PATH, engine='openpyxl')
        else:
            # إنشاء ملف جديد بالأعمدة المطلوبة
            return pd.DataFrame(columns=[
                "National ID", "Employee No", "Name", 
                "Present?", "Updated Date"
            ])
    except Exception as e:
        st.error(f"خطأ في تحميل البيانات: {str(e)}")
        return pd.DataFrame()

df = load_data()

# إضافة الأعمدة الناقصة إذا لم تكن موجودة
required_columns = ["National ID", "Employee No", "Name", "Present?", "Updated Date"]
for col in required_columns:
    if col not in df.columns:
        df[col] = ""

# البحث الجانبي
st.sidebar.header("🔍 بحث عن موظف")
search_name = st.sidebar.text_input("اسم الموظف")
search_emp = st.sidebar.text_input("رقم الموظف")

# ... (بقية الأكواد تبقى كما هي)

if st.button("💾 حفظ التحديث"):
    try:
        df.to_excel(EXCEL_PATH, index=False, engine='openpyxl')  # تحديد المحرك
        st.success("✅ تم الحفظ بنجاح")
    except PermissionError:
        st.error("❌ يرجى إغلاق ملف Excel قبل الحفظ")
