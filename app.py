from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from io import BytesIO
from collections import Counter
import pandas as pd
import re
import os
from sqlalchemy import or_
from helpers import apply_student_filters

app = Flask(__name__)
app.secret_key = "placement_secret_key"
BASE_DIR=os.path.abspath(os.path.dirname(__file__))
DB_PATH=os.path.join(BASE_DIR,"placement.db")
# ================= CONFIG =================

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"



db = SQLAlchemy(app)

# ================= DATABASE MODEL =================
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    roll = db.Column(db.String(50), unique=True, nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=False)
    gender = db.Column(db.String(20), nullable=False)

    tenth_percentage = db.Column(db.Float, nullable=False)
    inter_percentage = db.Column(db.Float, nullable=False)
    btech_percentage = db.Column(db.Float, nullable=False)

    backlogs = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now)

with app.app_context():
    db.create_all()
# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USERNAME and request.form["password"] == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("register"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= REGISTER =================
@app.route("/", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def register():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            roll = request.form["roll"].strip()
            branch = request.form["branch"]
            email = request.form["email"].strip()
            mobile = request.form["mobile"].strip()
            gender = request.form["gender"]

            tenth = float(request.form["tenth"])
            inter = float(request.form["inter"])
            btech_input = float(request.form["btech"])
            backlogs = int(request.form["backlogs"])
        except ValueError:
            flash("Invalid numeric input", "danger")
            return redirect(url_for("register"))

        # ===== NAME VALIDATION =====
        if not re.match(r"^[A-Za-z.\s]+$", name):
            flash("Name should contain only alphabets, dot and space", "danger")
            return redirect(url_for("register"))

        # ===== UNIQUE CHECKS =====
        if Student.query.filter_by(roll=roll).first():
            flash("Roll number already exists", "danger")
            return redirect(url_for("register"))

        if Student.query.filter_by(email=email).first():
            flash("Email already exists", "danger")
            return redirect(url_for("register"))

        if Student.query.filter_by(mobile=mobile).first():
            flash("Mobile number already exists", "danger")
            return redirect(url_for("register"))

        # ===== STRICT PERCENT VALIDATION =====
        if not (0 <= tenth <= 100):
            flash("10th percentage must be between 0 and 100", "danger")
            return redirect(url_for("register"))

        if not (0 <= inter <= 100):
            flash("Inter/Diploma percentage must be between 0 and 100", "danger")
            return redirect(url_for("register"))

        # ===== CGPA / B.TECH VALIDATION =====
        if btech_input <= 10:
            # CGPA case
            btech_percentage = round(btech_input * 9.5, 2)
            if btech_percentage > 100:
                flash("Converted B.Tech percentage exceeds 100", "danger")
                return redirect(url_for("register"))
        else:
            # Percentage case
            if not (0 <= btech_input <= 100):
                flash("B.Tech percentage must be between 0 and 100", "danger")
                return redirect(url_for("register"))
            btech_percentage = round(btech_input, 2)

        if backlogs < 0:
            flash("Backlogs cannot be negative", "danger")
            return redirect(url_for("register"))

        student = Student(
            name=name,
            roll=roll,
            branch=branch,
            email=email,
            mobile=mobile,
            gender=gender,
            tenth_percentage=tenth,
            inter_percentage=inter,
            btech_percentage=btech_percentage,
            backlogs=backlogs
        )

        db.session.add(student)
        db.session.commit()

        flash("🎉✅✨Student registered successfully!", "success")

        return redirect(url_for("register"))

    total_students = Student.query.count()
    return render_template("register.html", total_students=total_students)

# ================= STUDENTS LIST (MULTI FILTER) =================
@app.route("/students")
def students():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    query = Student.query
    query = apply_student_filters(query, request.args, Student)

    students = query.order_by(Student.btech_percentage.desc(),Student.name.asc()).all()


    percent_filters = request.args.getlist("percent")
    branch_filters = request.args.getlist("branch")
    gender_filters = request.args.getlist("gender")
    zero_backlogs = request.args.get("zero")

    if percent_filters:
        query = query.filter(
            or_(*[Student.btech_percentage >= float(p) for p in percent_filters])
        )

    if branch_filters:
        query = query.filter(Student.branch.in_(branch_filters))

    if gender_filters:
        query = query.filter(Student.gender.in_(gender_filters))

    max_backlogs = request.args.get("max_backlogs", type=int)

    if max_backlogs is not None:
        query = query.filter(Student.backlogs <= max_backlogs)


    students = query.order_by(Student.btech_percentage.desc()).all()

    branch_counts = {}
    for s in Student.query.all():
        branch_counts[s.branch] = branch_counts.get(s.branch, 0) + 1

    return render_template(
        "students.html",
        students=students,
        branch_counts=branch_counts
    )

# ================= DOWNLOAD (SYNCED WITH FILTERS) =================
@app.route("/download")
def download():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    query = Student.query
    query=apply_student_filters(query,request.args,Student)

    # ✅ SAME FILTERS AS /students
    percent_filters = request.args.getlist("percent")
    branch_filters = request.args.getlist("branch")
    gender_filters = request.args.getlist("gender")
    zero_backlogs = request.args.get("zero")

    if percent_filters:
        query = query.filter(
            or_(*[Student.btech_percentage >= float(p) for p in percent_filters])
        )

    if branch_filters:
        query = query.filter(Student.branch.in_(branch_filters))

    if gender_filters:
        query = query.filter(Student.gender.in_(gender_filters))

    max_backlogs = request.args.get("max_backlogs", type=int)

    if max_backlogs is not None:
        query = query.filter(Student.backlogs <= max_backlogs)


    students = query.all()

    # 🛑 SAFETY CHECK
    if not students:
        flash("⚠️ No students available for selected filter", "warning")
        return redirect(url_for("students"))

    # 📥 CREATE EXCEL
    data = []
    for s in students:
        data.append({
            "Name": s.name,
            "Roll": s.roll,
            "Branch": s.branch,
            "Gender": s.gender,
            "Email": s.email,
            "Mobile": s.mobile,
            "10th %": s.tenth_percentage,
            "Inter %": s.inter_percentage,
            "B.Tech %": s.btech_percentage,
            "Backlogs": s.backlogs
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        download_name="filtered_students.xlsx",
        as_attachment=True
    )


# ================= EDIT =================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    student = Student.query.get_or_404(id)

    if request.method == "POST":
        student.branch = request.form["branch"]
        student.backlogs = int(request.form["backlogs"])
        db.session.commit()
        flash("Student updated successfully", "success")
        return redirect(url_for("students"))

    return render_template("edit.html", student=student)

# ================= DELETE =================
@app.route("/delete/<int:id>")
def delete(id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted successfully", "danger")
    return redirect(url_for("students"))

# ================= RUN =================
@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    if __name__ == "__main__":
        app.run()


@app.route("/")
def home():
    return redirect(url_for("login"))
