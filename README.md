# 🎓 Placement Management System (Flask)

A **Placement Management System** developed using **Flask** to help the **Placement Department** manage, filter, and analyze student eligibility data efficiently.

This project is an extension of the **Student Management System** case study and is designed to meet **college management–level requirements**.

---

## 🚀 Features

### 🔐 Admin Login
- Secure admin login
- Session-based authentication

### 📝 Placement Registration
- Register student placement details
- Fields included:
  - Name
  - Roll Number (Unique)
  - Branch
  - Email (Unique)
  - Mobile (Unique)
  - Gender
  - 10th Percentage
  - Inter/Diploma Percentage
  - B.Tech Percentage / CGPA (Auto converted)
  - Number of Backlogs

### 📊 Student Management
- View all registered students
- Branch-wise student count
- Highlight students with **0 backlogs**
- Edit & delete student records

### 🔍 Advanced Filters
- Filter students by **B.Tech Percentage**
  - Above 60%, 65%, 70%, 80%, 85%, 90%
- Filter by **Branch**
- Filter students with **0 backlogs**
- Sort students by **B.Tech Percentage (Descending)**

### ⬇ Smart Excel Download
- Download student data in **Excel format**
- Downloaded file always matches the **applied filters**
- If no filter is selected, all student data is downloaded

### 🌙 Dark Mode
- Toggle dark/light mode
- Preference saved using browser storage

### 🎨 Premium UI
- Glassmorphism design
- Responsive layout
- Emojis for better user experience

---

## 🛠️ Tech Stack

- **Backend:** Flask, SQLAlchemy
- **Database:** SQLite
- **Frontend:** HTML, CSS, Bootstrap 5
- **Data Export:** Pandas, OpenPyXL

---

## 📂 Project Structure

placement-management-system/
│
├── app.py
├── placement.db
├── requirements.txt
├── README.md
│
├── templates/
│ ├── base.html
│ ├── login.html
│ ├── register.html
│ ├── students.html
│ └── edit.html
│
└── static/
└── css/
└── style.css



---

## ▶️ How to Run the Project

1. Clone or download the project
2. Create a virtual environment (optional but recommended)
3. Install dependencies:

```bash
pip install -r requirements.txt



🔑 Admin Credentials
Username: admin
Password: admin123