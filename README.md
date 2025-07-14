# 💼 Employee Salary Predictor

This is a Machine Learning-based web application built with **Streamlit** that predicts the salary of an employee based on their experience, education, job title, industry, age, and city. The app provides an intuitive UI and visual insights using animated charts, with options to export predictions in PDF or CSV format.

---

## 🚀 Features

- 🔮 Predict employee salary based on multiple inputs
- 📊 Animated charts for salary comparison with industry averages
- 📤 Export predictions as PDF or CSV
- 💡 Real-time toast notifications
- 🎨 Clean and dark-themed UI
- ⚡ Built using a trained machine learning model

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Machine Learning:** scikit-learn
- **Visualization:** Plotly
- **PDF Generation:** FPDF
- **Others:** Pandas, Pickle

---

## 📁 Project Structure

employee_salary_streamlit/
│
├── app.py # Main Streamlit app
├── model/
│ └── salary_model.pkl # Trained ML model file
├── model_training.ipynb # Jupyter notebook for training
├── requirements.txt # Project dependencies
├── README.md # Project documentation
└── .gitignore # Files/folders to ignore in Git

---

## 🧑‍💻 Getting Started

### 1. Clone the Repository

git clone https://github.com/Khushisoni702/employee-salary-predictor.git
cd employee-salary-predictor 

### 2. Create a Virtual Environment

python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Run the App

streamlit run app.py

## 📦 Deployment
You can deploy this app using Streamlit Cloud:

-Push your code to GitHub.
-Sign in to Streamlit Cloud.
-Link your repo and set app.py as the main file.
-Deploy and share your app!

## 👩‍💻 Author
Khushi Soni