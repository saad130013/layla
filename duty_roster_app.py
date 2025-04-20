
import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="نظام المناوبات - المستشفى", layout="wide")
st.title("📋 نظام متابعة المناوبات الشهرية")

EXCEL_PATH = "duty_roster_basic_info.xlsx"

@st.cache_data
def load_data():
    if os.path.exists(EXCEL_PATH):
        return pd.read_excel(EXCEL_PATH)
    else:
        return pd.DataFrame(columns=["National ID", "Employee No", "Name", "Present?", "Updated Date"])

df = load_data()

# التأكد من وجود العمود "Name" إذا أضفته لاحقاً
if "Name" not in df.columns:
    df["Name"] = ""
if "Present?" not in df.columns:
    df["Present?"] = ""
if "Updated Date" not in df.columns:
    df["Updated Date"] = ""

# البحث الجانبي
st.sidebar.header("🔍 بحث عن موظف")
search_name = st.sidebar.text_input("اسم الموظف")
search_emp = st.sidebar.text_input("رقم الموظف")

results = df
if search_name:
    results = results[df["Name"].astype(str).str.contains(search_name, case=False, na=False)]
if search_emp:
    results = results[df["Employee No"].astype(str).str.contains(search_emp)]

st.subheader("📄 نتائج البحث")
st.dataframe(results)

# نموذج التحديث
st.subheader("✅ تحديث حالة الحضور")
if not df.empty:
    selected_emp = st.selectbox("اختر رقم الموظف", df["Employee No"].astype(str).unique())
    emp_row = df[df["Employee No"].astype(str) == selected_emp].iloc[0]
    new_name = st.text_input("اسم الموظف", value=emp_row.get("Name", ""))
    present = st.selectbox("هل حضر؟", ["", "نعم", "لا"])
    update_date = st.date_input("تاريخ التحديث", value=datetime.today())

    if st.button("💾 حفظ التحديث"):
        df.loc[df["Employee No"].astype(str) == selected_emp, "Name"] = new_name
        df.loc[df["Employee No"].astype(str) == selected_emp, "Present?"] = present
        df.loc[df["Employee No"].astype(str) == selected_emp, "Updated Date"] = update_date
        df.to_excel(EXCEL_PATH, index=False)
        st.success("✅ تم حفظ التحديث بنجاح")
