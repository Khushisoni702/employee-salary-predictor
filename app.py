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

# Styling
st.markdown("""
<style>
.stApp {
    background-color: #0d1117;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    animation: fadein 1.2s ease-in;
}
@keyframes fadein {
  from {opacity: 0;}
  to {opacity: 1;}
}
.title {
    text-align: center;
    font-size: 46px;
    color: #7dd3fc;
    font-weight: bold;
    margin-bottom: 5px;
    text-shadow: 2px 2px 5px #00000088;
}
.subtitle {
    text-align: center;
    font-size: 18px;
    color: #c4b5fd;
    margin-bottom: 30px;
}
.stSelectbox label, .stSlider label {
    color: #e2e8f0;
    font-weight: 600;
}
.stButton > button {
    background-color: #60a5fa;
    color: black;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    margin-top: 10px;
}
.center-button > div {
    display: flex;
    justify-content: center;
}
.download-button {
    background-color: #38bdf8;
    color: black;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-weight: bold;
    text-decoration: none;
}
.download-button:hover {
    background-color: #0ea5e9;
    color: white;
}
footer {
    text-align: center;
    color: #aaa;
    padding: 2rem 0 1rem 0;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# Headings
st.markdown("<div class='title'>💼 Employee Salary Predictor</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Estimate salary based on experience, age, and role</div>", unsafe_allow_html=True)

# Inputs
education = st.selectbox("Select Education Level", ["Bachelor", "Master", "PhD"])
job = st.selectbox("Select Job Title", ["Data Scientist", "Web Developer", "UI/UX Designer", "DevOps Engineer"])
industry = st.selectbox("Select Industry", ["IT", "Retail", "Manufacturing", "Telecom"])
city = st.selectbox("Select City", ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune"])
experience = st.slider("Experience (Years)", 0, 40, 5)
age = st.slider("Age", 20, 65, 30)

# Store predictions
if "history" not in st.session_state:
    st.session_state.history = []

    # ✅ Predict & Clear Buttons – Centered, Styled Separately
with st.container():
    col = st.columns(3)
    with col[1]:  # Center column
        # Blue Predict Button
        predict_clicked = st.button("🔮 Predict Salary", key="predict_btn")
        # Red Clear Button
        clear_clicked = st.button("🗑️ Clear History", key="clear_btn")

        # Inject CSS for custom colors
        st.markdown("""
        <style>
        div[data-testid="stButton"][data-baseweb="button"] > button[kind="primary"][data-testid="baseButton-element"][key="predict_btn"] {
            background-color: #60a5fa;
            color: black;
            font-weight: bold;
            width: 250px;
            height: 45px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        div[data-testid="stButton"][data-baseweb="button"] > button[kind="primary"][data-testid="baseButton-element"][key="clear_btn"] {
            background-color: #ef4444;
            color: white;
            font-weight: bold;
            width: 250px;
            height: 45px;
            border-radius: 8px;
        }
        </style>
        """, unsafe_allow_html=True)

# 🔮 Predict Logic
if predict_clicked:
    with st.spinner("Calculating salary... Please wait"):
        input_df = pd.DataFrame([{
            "Experience": experience,
            "Age": age,
            "Education": education,
            "Job_Title": job,
            "Industry": industry,
            "City": city
        }])
        input_encoded = pd.get_dummies(input_df)
        input_encoded = input_encoded.reindex(columns=model.feature_names_in_, fill_value=0)
        salary = model.predict(input_encoded)[0]

        st.toast(f"💰 Estimated Salary: ₹{int(salary):,}", icon="✅")

        result = input_df.copy()
        result["Predicted_Salary"] = int(salary)
        if "history" not in st.session_state:
            st.session_state.history = []
        st.session_state.history.append(result)

# 🧹 Clear Logic
if clear_clicked:
    st.session_state.history = []
    st.success("Prediction history cleared!")

# Chart
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

    # Prepare data for grouped bar chart
    chart_df = history_df[["Job_Title", "Predicted_Salary", "Avg_Salary"]].copy()
    chart_df = chart_df.melt(
        id_vars="Job_Title",
        value_vars=["Predicted_Salary", "Avg_Salary"],
        var_name="Salary_Type",
        value_name="Salary"
    )

    bar_chart = px.bar(
        chart_df,
        x="Job_Title",
        y="Salary",
        color="Salary_Type",
        barmode="group",
        text_auto=".2s",
        labels={"Job_Title": "Job", "Salary": "Salary", "Salary_Type": "Type"},
        title="Predicted vs Average Salary by Job Title",
        color_discrete_map={"Predicted_Salary": "#38bdf8", "Avg_Salary": "#f97316"},
        width=700,
        height=400
    )

    st.plotly_chart(bar_chart)

    # Build line chart using full history
    full_history_df = pd.concat(st.session_state.history, ignore_index=True)
    full_history_df["Avg_Salary"] = full_history_df["Job_Title"].map(avg_salaries)

    line_chart = px.line(
        full_history_df,
        x="Experience",
        y=["Predicted_Salary", "Avg_Salary"],
        markers=True,
        title="Experience vs Salary Comparison (Full History)",
        labels={"value": "Salary", "Experience": "Years of Experience", "variable": "Type"},
        color_discrete_map={"Predicted_Salary": "#38bdf8", "Avg_Salary": "#f97316"},
        width=700,
        height=400
    )
    st.plotly_chart(line_chart)

    # Export
    st.markdown("### 📤 Export Predictions")

    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    def convert_df_to_pdf(df):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(200, 10, "Employee Salary Predictions", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        for i, row in df.iterrows():
            text = f"{i+1}. {row['Job_Title']} | Exp: {row['Experience']} | Age: {row['Age']} | City: {row['City']} | Predicted Salary: Rs. {row['Predicted_Salary']:,}"
            pdf.multi_cell(0, 8, text)
            pdf.ln(1)
        return pdf.output(dest='S')

    full_history_df = pd.concat(st.session_state.history, ignore_index=True)
    full_history_df["Avg_Salary"] = full_history_df["Job_Title"].map(avg_salaries)

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
    st.info("No predictions available yet to export.")

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
