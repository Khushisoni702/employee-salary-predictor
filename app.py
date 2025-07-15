import streamlit as st
import pandas as pd
import pickle
import base64
from fpdf import FPDF
import plotly.express as px

# Load model
with open("model/salary_model.pkl", "rb") as f:
    model = pickle.load(f)

# Streamlit Config
st.set_page_config(page_title="Employee Salary Predictor", layout="centered", page_icon="💼")

# Theme Toggle
theme = st.sidebar.radio("Select Theme", ["Dark", "Light"], index=0)
if theme == "Light":
    st.markdown("""
        <style>
        .stApp {
            background-color: #f5f5f5;
            color: #000000;
        }
        h1, h2, h3, h4, h5, h6, p, div {
            color: #111 !important;
        }
        .title {
            color: #111 !important;
        }
        </style>
    """, unsafe_allow_html=True)


# Sidebar Navigation
st.sidebar.title("📂 Menu")
page = st.sidebar.radio("Navigate to:", ["🏠 Home", "🔮 Predict Salary", "📊 View History", "🧹 Clear History", "ℹ️ About"])

# Custom App Title/Logo
st.sidebar.markdown("""
    <h2 style='color:#60a5fa;'>💼 Salary Predictor</h2>
    <hr style='border:1px solid #333;'>
""", unsafe_allow_html=True)

# Session history
if "history" not in st.session_state:
    st.session_state.history = []

# Home Page
def home_page():
    st.markdown("""
        <h1 style='text-align: center; font-size: 50px; color: #38bdf8; font-weight: bold; 
                   text-shadow: 2px 2px 4px #00000088;'>💼 Welcome to Employee Salary Predictor</h1>
        <p style='text-align: center; font-size: 20px; color: #c4b5fd; padding: 20px 50px;'>
            This application uses a powerful Machine Learning model to estimate employee salaries based on
            factors like <strong>education level, job title, city, experience, and age</strong>.
        </p>
        <p style='text-align: center; font-size: 18px; color: #cbd5e1; padding: 0 50px;'>
            🚀 Start by selecting an option from the sidebar: Predict Salary, View Your Prediction History,
            or Learn More About This Project.
        </p>
    """, unsafe_allow_html=True)

if page == "🏠 Home":
    home_page()

elif page == "🔮 Predict Salary":
    st.markdown("""
        <h2 style='text-align: center; font-size: 40px; color: #60a5fa; font-weight: bold;
                   margin-bottom: 30px; text-shadow: 1px 1px 4px #00000088;'>🔮 Predict Employee Salary</h2>
    """, unsafe_allow_html=True)

    education = st.selectbox("Select Education Level", ["Bachelor", "Master", "PhD"])
    job = st.selectbox("Select Job Title", ["Data Scientist", "Web Developer", "UI/UX Designer", "DevOps Engineer"])
    industry = st.selectbox("Select Industry", ["IT", "Retail", "Manufacturing", "Telecom"])
    city = st.selectbox("Select City", ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune"])
    experience = st.slider("Experience (Years)", 0, 40, 5)
    age = st.slider("Age", 20, 65, 30)
    col = st.columns(3)
    with col[1]:
        predict_clicked = st.button("🔮 Predict Salary", key="predict_btn")

    if predict_clicked:
        with st.spinner("Calculating salary... Please wait"):
            input_df = pd.DataFrame([{ "Experience": experience, "Age": age, "Education": education,
                                       "Job_Title": job, "Industry": industry, "City": city }])
            input_encoded = pd.get_dummies(input_df)
            input_encoded = input_encoded.reindex(columns=model.feature_names_in_, fill_value=0)
            salary = model.predict(input_encoded)[0]

            st.toast(f"💰 Estimated Salary: ₹{int(salary):,}", icon="✅")
            result = input_df.copy()
            result["Predicted_Salary"] = int(salary)
            st.session_state.history.append(result)

elif page == "📊 View History":
    st.markdown("""
        <h2 style='text-align: center; font-size: 40px; color: #38bdf8; font-weight: bold;
                   margin-bottom: 20px; text-shadow: 1px 1px 4px #00000088;'>📊 Prediction History & Insights</h2>
    """, unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown("### 📊 Predicted Salary vs Average by Role")
        history_df = st.session_state.history[-1].copy()

        avg_salaries = {
            "Data Scientist": 850000,
            "Web Developer": 600000,
            "UI/UX Designer": 700000,
            "DevOps Engineer": 900000
        }

        history_df["Avg_Salary"] = history_df["Job_Title"].map(avg_salaries)
        chart_df = history_df[["Job_Title", "Predicted_Salary", "Avg_Salary"]].melt(id_vars="Job_Title", 
                                    value_vars=["Predicted_Salary", "Avg_Salary"],
                                    var_name="Salary_Type", value_name="Salary")
        bar_chart = px.bar(chart_df, x="Job_Title", y="Salary", color="Salary_Type",
                           barmode="group", text_auto=".2s",
                           labels={"Job_Title": "Job", "Salary": "Salary", "Salary_Type": "Type"},
                           title="Predicted vs Average Salary by Job Title",
                           color_discrete_map={"Predicted_Salary": "#38bdf8", "Avg_Salary": "#f97316"},
                           width=700, height=400)
        st.plotly_chart(bar_chart)

        full_history_df = pd.concat(st.session_state.history, ignore_index=True)
        full_history_df["Avg_Salary"] = full_history_df["Job_Title"].map(avg_salaries)

        line_chart = px.line(full_history_df, x="Experience", y=["Predicted_Salary", "Avg_Salary"],
                             markers=True, title="Experience vs Salary Comparison (Full History)",
                             labels={"value": "Salary", "Experience": "Years of Experience", "variable": "Type"},
                             color_discrete_map={"Predicted_Salary": "#38bdf8", "Avg_Salary": "#f97316"},
                             width=700, height=400)
        st.plotly_chart(line_chart)

        st.markdown("### 📤 Export Predictions")

        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode("utf-8")

        def convert_df_to_pdf(df):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "Employee Salary Predictions", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", "", 12)
            for i, row in df.iterrows():
                text = f"{i+1}. {row['Job_Title']} | Exp: {row['Experience']} | Age: {row['Age']} | City: {row['City']} | Predicted Salary: Rs. {row['Predicted_Salary']:,}"
                pdf.multi_cell(0, 8, text)
                pdf.ln(1)
            return pdf.output(dest='S').encode("latin1")

        csv = convert_df_to_csv(full_history_df)
        pdf = convert_df_to_pdf(full_history_df)

        def styled_download_button(content, filename, label):
            b64 = base64.b64encode(content).decode()
            return f"""
                <a href="data:application/octet-stream;base64,{b64}" download="{filename}" 
                   style="display: inline-block; background-color: #60a5fa; color: black; 
                          font-weight: bold; text-decoration: none; padding: 10px 20px; 
                          border-radius: 8px; margin: 5px 10px;">
                    {label}
                </a>
            """

        st.markdown(styled_download_button(csv, "predictions.csv", "⬇️ Download CSV"), unsafe_allow_html=True)
        st.markdown(styled_download_button(pdf, "predictions.pdf", "📄 Download PDF"), unsafe_allow_html=True)
    else:
        st.info("No predictions available yet to show.")

elif page == "🧹 Clear History":
    st.markdown("""
        <h2 style='text-align: center; font-size: 40px; color: #f87171; font-weight: bold;
                   margin-bottom: 20px; text-shadow: 1px 1px 4px #00000088;'>🧹 Clear Prediction History</h2>
    """, unsafe_allow_html=True)
    if st.button("🗑️ Confirm and Clear History"):
        st.session_state.history = []
        st.success("Prediction history cleared!")

elif page == "ℹ️ About":
    st.markdown("""
        <h2 style='text-align: center; font-size: 40px; color: #facc15; font-weight: bold;
                   margin-bottom: 20px; text-shadow: 1px 1px 4px #00000088;'>📘 About This App</h2>
    """, unsafe_allow_html=True)
    st.markdown("""
        This Streamlit app helps you predict employee salaries based on various attributes
        such as experience, education level, job title, industry, and city.

        ### Features:
        - 🔮 Predict salaries with a pre-trained machine learning model
        - 📊 Visualize predictions and compare with average market values
        - 📤 Export predictions as CSV and PDF
        - 🧹 Easily clear your prediction history
        - 🌗 Switch between Light and Dark themes
    """)

# Footer
st.markdown("""
    <hr style="border-top: 1px solid #444; margin-top: 50px;">
    <div style="text-align: center; color: #aaa; font-size: 14px; padding-top: 10px;">
        🚀 Powered by Machine Learning • Built with Streamlit<br>
        👩‍💻 Created by <strong>Khushi Soni</strong> |
        <a href="https://github.com/Khushisoni702" target="_blank" style="color: #4fd1c5; text-decoration: none;">
            GitHub Profile
        </a><br>
        © 2025 All rights reserved.
    </div>
""", unsafe_allow_html=True)

