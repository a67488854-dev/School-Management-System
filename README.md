from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import date

app = Flask(__name__)

DATA_FILE = "school_data.json"


# =========================================================
# تحميل وحفظ البيانات
# =========================================================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "students": [],
            "teachers": [],
            "attendance": [],
            "grades": []
        }

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        data.setdefault("students", [])
        data.setdefault("teachers", [])
        data.setdefault("attendance", [])
        data.setdefault("grades", [])

        return data

    except Exception:
        return {
            "students": [],
            "teachers": [],
            "attendance": [],
            "grades": []
        }


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


data = load_data()


def next_id(items):
    if not items:
        return 1
    return max(item.get("id", 0) for item in items) + 1


# =========================================================
# الصفحة الرئيسية
# =========================================================

HTML = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>مدرستي - نظام إدارة المدرسة</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Tahoma, Arial, sans-serif;
    background: #070d1d;
    color: #f8fafc;
}

button,
input,
select {
    font-family: inherit;
}

.app {
    display: flex;
    min-height: 100vh;
}

/* =========================
   القائمة
========================= */

.sidebar {
    width: 270px;
    background: #101827;
    border-left: 1px solid #263247;
    padding: 25px 18px;
    position: fixed;
    right: 0;
    top: 0;
    bottom: 0;
}

.logo {
    font-size: 30px;
    font-weight: bold;
    color: #60a5fa;
    text-align: center;
    margin-bottom: 35px;
}

.menu {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.menu button {
    border: none;
    background: transparent;
    color: #dbe4f0;
    padding: 16px;
    border-radius: 14px;
    text-align: right;
    cursor: pointer;
    font-size: 17px;
    transition: 0.2s;
}

.menu button:hover {
    background: #1c2940;
}

.menu button.active {
    background: #2456df;
    color: white;
}

/* =========================
   المحتوى
========================= */

.main {
    margin-right: 270px;
    width: calc(100% - 270px);
    padding: 35px;
}

.section {
    display: none;
}

.section.active {
    display: block;
}

.header {
    background: #111a2b;
    border: 1px solid #27364f;
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 25px;
}

.header h1 {
    margin: 0 0 10px;
    font-size: 30px;
}

.header p {
    margin: 0;
    color: #94a3b8;
    font-size: 16px;
}

/* =========================
   البطاقات
========================= */

.cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 25px;
}

.card {
    background: #111a2b;
    border: 1px solid #27364f;
    border-radius: 18px;
    padding: 25px;
}

.card-title {
    color: #94a3b8;
    margin-bottom: 10px;
}

.card-number {
    font-size: 35px;
    font-weight: bold;
    color: #60a5fa;
}

/* =========================
   Panels
========================= */

.grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.panel {
    background: #111a2b;
    border: 1px solid #27364f;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 20px;
}

.panel h2 {
    margin-top: 0;
}

/* =========================
   Forms
========================= */

.form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
}

label {
    display: block;
    color: #cbd5e1;
    margin-bottom: 7px;
}

input,
select {
    width: 100%;
    padding: 13px;
    background: #0b1323;
    color: white;
    border: 1px solid #334155;
    border-radius: 10px;
    outline: none;
}

input:focus,
select:focus {
    border-color: #3b82f6;
}

.full {
    grid-column: 1 / -1;
}

/* =========================
   Buttons
========================= */

.btn {
    border: none;
    padding: 12px 18px;
    border-radius: 10px;
    cursor: pointer;
    font-weight: bold;
    margin-top: 15px;
}

.primary {
    background: #2563eb;
    color: white;
}

.primary:hover {
    background: #1d4ed8;
}

.danger {
    background: #dc2626;
    color: white;
}

.secondary {
    background: #334155;
    color: white;
}

/* =========================
   Table
========================= */

.toolbar {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.table-wrap {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 13px;
    border-bottom: 1px solid #27364f;
    text-align: right;
}

th {
    background: #172237;
    color: #93c5fd;
}

td {
    color: #e2e8f0;
}

.empty {
    text-align: center;
    color: #94a3b8;
    padding: 30px;
}

/* =========================
   responsive
========================= */

@media (max-width: 900px) {

    .sidebar {
        width: 210px;
    }

    .main {
        margin-right: 210px;
        width: calc(100% - 210px);
    }

    .cards {
        grid-template-columns: repeat(2, 1fr);
    }

    .grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 650px) {

    .sidebar {
        position: relative;
        width: 100%;
        height: auto;
    }

    .app {
        display: block;
    }

    .main {
        margin-right: 0;
        width: 100%;
        padding: 15px;
    }

    .cards {
        grid-template-columns: 1fr;
    }

    .form-grid {
        grid-template-columns: 1fr;
    }

    .full {
        grid-column: auto;
    }
}

</style>
</head>

<body>

<div class="app">

<!-- =========================
     القائمة
========================= -->

<aside class="sidebar">

    <div class="logo">
        🏫 مدرستي
    </div>

    <div class="menu">

        <button onclick="showSection('dashboard', this)" class="active">
            📊 لوحة التحكم
        </button>

        <button onclick="showSection('students', this)">
            👨‍🎓 الطلاب
        </button>

        <button onclick="showSection('attendance', this)">
            📝 الحضور والغياب
        </button>

        <button onclick="showSection('grades', this)">
            📚 الدرجات
        </button>

        <button onclick="showSection('teachers', this)">
            👨‍🏫 المدرسون
        </button>

    </div>

</aside>


<!-- =========================
     المحتوى
========================= -->

<main class="main">


<!-- لوحة التحكم -->

<section id="dashboard" class="section active">

    <div class="header">
        <h1>📊 لوحة التحكم</h1>
        <p>
            إدارة بيانات المدرسة والطلاب والحضور والدرجات والمدرسين.
        </p>
    </div>

    <div class="cards">

        <div class="card">
            <div class="card-title">👨‍🎓 الطلاب</div>
            <div class="card-number" id="studentCount">0</div>
        </div>

        <div class="card">
            <div class="card-title">👨‍🏫 المدرسون</div>
            <div class="card-number" id="teacherCount">0</div>
        </div>

        <div class="card">
            <div class="card-title">📝 سجلات الحضور</div>
            <div class="card-number" id="attendanceCount">0</div>
        </div>

        <div class="card">
            <div class="card-title">📚 الدرجات</div>
            <div class="card-number" id="gradeCount">0</div>
        </div>

    </div>

    <div class="panel">

        <h2>📌 ملخص النظام</h2>

        <p id="dashboardMessage">
            جاري تحميل البيانات...
        </p>

    </div>

</section>


<!-- =========================
     الطلاب
========================= -->

<section id="students" class="section">

    <div class="header">

        <h1>👨‍🎓 إدارة الطلاب</h1>

        <p>
            إضافة وبحث وحذف وتعديل بيانات الطلاب.
        </p>

    </div>


    <div class="grid">

        <div class="panel">

            <h2>➕ إضافة طالب جديد</h2>

            <div class="form-grid">

                <div>
                    <label>اسم الطالب</label>
                    <input id="studentName" placeholder="مثال: أحمد محمد">
                </div>

                <div>
                    <label>العمر</label>
                    <input id="studentAge" type="number" placeholder="13">
                </div>

                <div>
                    <label>الصف</label>
                    <input id="studentClass" placeholder="الأول الإعدادي">
                </div>

                <div>
                    <label>الدرجة</label>
                    <input id="studentScore" type="number" min="0" max="100" placeholder="90">
                </div>

                <div class="full">
                    <label>العنوان</label>
                    <input id="studentAddress" placeholder="العنوان">
                </div>

            </div>

            <button class="btn primary" onclick="addStudent()">
                ➕ إضافة الطالب
            </button>

        </div>


        <div class="panel">

            <h2>🔎 البحث عن طالب</h2>

            <input
                id="studentSearch"
                placeholder="ابحث باسم الطالب..."
                oninput="renderStudents()"
            >

            <button class="btn secondary" onclick="loadAll()">
                🔄 تحديث البيانات
            </button>

        </div>

    </div>


    <div class="panel">

        <h2>📋 الطلاب المسجلون</h2>

        <div class="table-wrap">

            <table>

                <thead>

                    <tr>
                        <th>#</th>
                        <th>الاسم</th>
                        <th>العمر</th>
                        <th>الصف</th>
                        <th>الدرجة</th>
                        <th>العنوان</th>
                        <th>الإجراء</th>
                    </tr>

                </thead>

                <tbody id="studentsTable"></tbody>

            </table>

        </div>

    </div>

</section>


<!-- =========================
     الحضور
========================= -->

<section id="attendance" class="section">

    <div class="header">

        <h1>📝 الحضور والغياب</h1>

        <p>
            تسجيل حضور أو غياب الطلاب وحفظ السجل بالتاريخ.
        </p>

    </div>


    <div class="panel">

        <h2>➕ تسجيل الحضور</h2>

        <div class="form-grid">

            <div>
                <label>الطالب</label>

                <select id="attendanceStudent">
                    <option value="">اختر الطالب</option>
                </select>

            </div>

            <div>

                <label>الحالة</label>

                <select id="attendanceStatus">

                    <option value="حاضر">
                        حاضر
                    </option>

                    <option value="غائب">
                        غائب
                    </option>

                </select>

            </div>

        </div>

        <button class="btn primary" onclick="addAttendance()">
            📝 تسجيل
        </button>

    </div>


    <div class="panel">

        <h2>📋 سجل الحضور</h2>

        <div class="table-wrap">

            <table>

                <thead>

                    <tr>
                        <th>#</th>
                        <th>الطالب</th>
                        <th>الحالة</th>
                        <th>التاريخ</th>
                        <th>الإجراء</th>
                    </tr>

                </thead>

                <tbody id="attendanceTable"></tbody>

            </table>

        </div>

    </div>

</section>


<!-- =========================
     الدرجات
========================= -->

<section id="grades" class="section">

    <div class="header">

        <h1>📚 الدرجات</h1>

        <p>
            إضافة درجات الطلاب وعرضها في جدول.
        </p>

    </div>


    <div class="panel">

        <h2>➕ إضافة درجة</h2>

        <div class="form-grid">

            <div>

                <label>الطالب</label>

                <select id="gradeStudent">
                    <option value="">اختر الطالب</option>
                </select>

            </div>

            <div>

                <label>المادة</label>

                <input id="gradeSubject" placeholder="الرياضيات">

            </div>

            <div>

                <label>الدرجة</label>

                <input
                    id="gradeScore"
                    type="number"
                    min="0"
                    max="100"
                    placeholder="95"
                >

            </div>

        </div>

        <button class="btn primary" onclick="addGrade()">
            ➕ إضافة الدرجة
        </button>

    </div>


    <div class="panel">

        <h2>📋 درجات الطلاب</h2>

        <div class="table-wrap">

            <table>

                <thead>

                    <tr>
                        <th>#</th>
                        <th>الطالب</th>
                        <th>المادة</th>
                        <th>الدرجة</th>
                        <th>التاريخ</th>
                        <th>الإجراء</th>
                    </tr>

                </thead>

                <tbody id="gradesTable"></tbody>

            </table>

        </div>

    </div>

</section>


<!-- =========================
     المدرسون
========================= -->

<section id="teachers" class="section">

    <div class="header">

        <h1>👨‍🏫 المدرسون</h1>

        <p>
            إضافة وإدارة بيانات المدرسين.
        </p>

    </div>


    <div class="panel">

        <h2>➕ إضافة مدرس</h2>

        <div class="form-grid">

            <div>

                <label>اسم المدرس</label>

                <input
                    id="teacherName"
                    placeholder="اسم المدرس"
                >

            </div>

            <div>

                <label>المادة</label>

                <input
                    id="teacherSubject"
                    placeholder="اللغة العربية"
                >

            </div>

            <div>

                <label>رقم الهاتف</label>

                <input
                    id="teacherPhone"
                    placeholder="01000000000"
                >

            </div>

        </div>

        <button class="btn primary" onclick="addTeacher()">
            ➕ إضافة المدرس
        </button>

    </div>


    <div class="panel">

        <h2>📋 المدرسون</h2>

        <div class="table-wrap">

            <table>

                <thead>

                    <tr>
                        <th>#</th>
                        <th>الاسم</th>
                        <th>المادة</th>
                        <th>الهاتف</th>
                        <th>الإجراء</th>
                    </tr>

                </thead>

                <tbody id="teachersTable"></tbody>

            </table>

        </div>

    </div>

</section>


</main>

</div>


<script>

let students = [];
let teachers = [];
let attendance = [];
let grades = [];


// =========================================================
// التنقل بين الصفحات
// =========================================================

function showSection(id, button) {

    document.querySelectorAll(".section").forEach(section => {
        section.classList.remove("active");
    });

    document.getElementById(id).classList.add("active");

    document.querySelectorAll(".menu button").forEach(btn => {
        btn.classList.remove("active");
    });

    button.classList.add("active");

    loadAll();
}


// =========================================================
// تحميل البيانات
// =========================================================

async function loadAll() {

    const response = await fetch("/api/data");

    const result = await response.json();

    students = result.students || [];
    teachers = result.teachers || [];
    attendance = result.attendance || [];
    grades = result.grades || [];

    updateDashboard();
    renderStudents();
    renderTeachers();
    renderAttendance();
    renderGrades();
    updateStudentSelects();
}


// =========================================================
// لوحة التحكم
// =========================================================

function updateDashboard() {

    document.getElementById("studentCount").textContent =
        students.length;

    document.getElementById("teacherCount").textContent =
        teachers.length;

    document.getElementById("attendanceCount").textContent =
        attendance.length;

    document.getElementById("gradeCount").textContent =
        grades.length;

    document.getElementById("dashboardMessage").textContent =
        `النظام يحتوي حاليًا على ${students.length} طالب و ${teachers.length} مدرس و ${attendance.length} سجل حضور و ${grades.length} درجة.`;
}


// =========================================================
// الطلاب
// =========================================================

async function addStudent() {

    const name = document.getElementById("studentName").value.trim();
    const age = document.getElementById("studentAge").value;
    const className = document.getElementById("studentClass").value.trim();
    const score = document.getElementById("studentScore").value;
    const address = document.getElementById("studentAddress").value.trim();

    if (!name || !age || !className) {
        alert("من فضلك اكتب اسم الطالب والعمر والصف.");
        return;
    }

    const response = await fetch("/api/students", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            name,
            age,
            class_name: className,
            score: score || 0,
            address
        })

    });

    const result = await response.json();

    if (!response.ok) {
        alert(result.message);
        return;
    }

    alert("تمت إضافة الطالب بنجاح ✅");

    document.getElementById("studentName").value = "";
    document.getElementById("studentAge").value = "";
    document.getElementById("studentClass").value = "";
    document.getElementById("studentScore").value = "";
    document.getElementById("studentAddress").value = "";

    loadAll();
}


function renderStudents() {

    const search =
        document.getElementById("studentSearch").value
        .toLowerCase()
        .trim();

    const table =
        document.getElementById("studentsTable");

    table.innerHTML = "";

    const filtered = students.filter(student =>
        student.name.toLowerCase().includes(search)
    );

    if (filtered.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="7" class="empty">
                    لا يوجد طلاب
                </td>
            </tr>
        `;

        return;
    }

    filtered.forEach(student => {

        table.innerHTML += `

            <tr>

                <td>${student.id}</td>

                <td>${escapeHtml(student.name)}</td>

                <td>${student.age}</td>

                <td>${escapeHtml(student.class_name)}</td>

                <td>${student.score}</td>

                <td>${escapeHtml(student.address || "-")}</td>

                <td>

                    <button
                        class="btn danger"
                        onclick="deleteStudent(${student.id})"
                    >
                        حذف
                    </button>

                </td>

            </tr>

        `;

    });
}


async function deleteStudent(id) {

    if (!confirm("هل تريد حذف هذا الطالب؟")) {
        return;
    }

    const response = await fetch(
        "/api/students/" + id,
        {
            method: "DELETE"
        }
    );

    const result = await response.json();

    alert(result.message);

    loadAll();
}


// =========================================================
// تحديث قوائم الطلاب
// =========================================================

function updateStudentSelects() {

    const attendanceSelect =
        document.getElementById("attendanceStudent");

    const gradeSelect =
        document.getElementById("gradeStudent");

    attendanceSelect.innerHTML =
        '<option value="">اختر الطالب</option>';

    gradeSelect.innerHTML =
        '<option value="">اختر الطالب</option>';

    students.forEach(student => {

        attendanceSelect.innerHTML += `
            <option value="${student.id}">
                ${escapeHtml(student.name)}
            </option>
        `;

        gradeSelect.innerHTML += `
            <option value="${student.id}">
                ${escapeHtml(student.name)}
            </option>
        `;

    });
}


// =========================================================
// الحضور
// =========================================================

async function addAttendance() {

    const studentId =
        document.getElementById("attendanceStudent").value;

    const status =
        document.getElementById("attendanceStatus").value;

    if (!studentId) {
        alert("اختر الطالب أولاً.");
        return;
    }

    const response = await fetch("/api/attendance", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            student_id: Number(studentId),
            status
        })

    });

    const result = await response.json();

    alert(result.message);

    loadAll();
}


function renderAttendance() {

    const table =
        document.getElementById("attendanceTable");

    table.innerHTML = "";

    if (attendance.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="5" class="empty">
                    لا توجد سجلات حضور
                </td>
            </tr>
        `;

        return;
    }

    [...attendance].reverse().forEach(record => {

        table.innerHTML += `

            <tr>

                <td>${record.id}</td>

                <td>
                    ${escapeHtml(record.student_name)}
                </td>

                <td>
                    ${record.status}
                </td>

                <td>
                    ${record.date}
                </td>

                <td>

                    <button
                        class="btn danger"
                        onclick="deleteAttendance(${record.id})"
                    >
                        حذف
                    </button>

                </td>

            </tr>

        `;

    });
}


async function deleteAttendance(id) {

    if (!confirm("حذف سجل الحضور؟")) {
        return;
    }

    const response = await fetch(
        "/api/attendance/" + id,
        {
            method: "DELETE"
        }
    );

    const result = await response.json();

    alert(result.message);

    loadAll();
}


// =========================================================
// الدرجات
// =========================================================

async function addGrade() {

    const studentId =
        document.getElementById("gradeStudent").value;

    const subject =
        document.getElementById("gradeSubject").value.trim();

    const score =
        document.getElementById("gradeScore").value;

    if (!studentId || !subject || score === "") {

        alert("من فضلك أكمل بيانات الدرجة.");

        return;
    }

    if (Number(score) < 0 || Number(score) > 100) {

        alert("الدرجة يجب أن تكون من 0 إلى 100.");

        return;
    }

    const response = await fetch("/api/grades", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            student_id: Number(studentId),
            subject,
            score: Number(score)
        })

    });

    const result = await response.json();

    alert(result.message);

    document.getElementById("gradeSubject").value = "";
    document.getElementById("gradeScore").value = "";

    loadAll();
}


function renderGrades() {

    const table =
        document.getElementById("gradesTable");

    table.innerHTML = "";

    if (grades.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="6" class="empty">
                    لا توجد درجات
                </td>
            </tr>
        `;

        return;
    }

    [...grades].reverse().forEach(record => {

        table.innerHTML += `

            <tr>

                <td>${record.id}</td>

                <td>
                    ${escapeHtml(record.student_name)}
                </td>

                <td>
                    ${escapeHtml(record.subject)}
                </td>

                <td>
                    ${record.score}
                </td>

                <td>
                    ${record.date}
                </td>

                <td>

                    <button
                        class="btn danger"
                        onclick="deleteGrade(${record.id})"
                    >
                        حذف
                    </button>

                </td>

            </tr>

        `;

    });
}


async function deleteGrade(id) {

    if (!confirm("حذف هذه الدرجة؟")) {
        return;
    }

    const response = await fetch(
        "/api/grades/" + id,
        {
            method: "DELETE"
        }
    );

    const result = await response.json();

    alert(result.message);

    loadAll();
}


// =========================================================
// المدرسون
// =========================================================

async function addTeacher() {

    const name =
        document.getElementById("teacherName").value.trim();

    const subject =
        document.getElementById("teacherSubject").value.trim();

    const phone =
        document.getElementById("teacherPhone").value.trim();

    if (!name || !subject) {

        alert("اكتب اسم المدرس والمادة.");

        return;
    }

    const response = await fetch("/api/teachers", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            name,
            subject,
            phone
        })

    });

    const result = await response.json();

    alert(result.message);

    document.getElementById("teacherName").value = "";
    document.getElementById("teacherSubject").value = "";
    document.getElementById("teacherPhone").value = "";

    loadAll();
}


function renderTeachers() {

    const table =
        document.getElementById("teachersTable");

    table.innerHTML = "";

    if (teachers.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="5" class="empty">
                    لا يوجد مدرسون
                </td>
            </tr>
        `;

        return;
    }

    teachers.forEach(teacher => {

        table.innerHTML += `

            <tr>

                <td>${teacher.id}</td>

                <td>
                    ${escapeHtml(teacher.name)}
                </td>

                <td>
                    ${escapeHtml(teacher.subject)}
                </td>

                <td>
                    ${escapeHtml(teacher.phone || "-")}
                </td>

                <td>

                    <button
                        class="btn danger"
                        onclick="deleteTeacher(${teacher.id})"
                    >
                        حذف
                    </button>

                </td>

            </tr>

        `;

    });
}


async function deleteTeacher(id) {

    if (!confirm("هل تريد حذف المدرس؟")) {
        return;
    }

    const response = await fetch(
        "/api/teachers/" + id,
        {
            method: "DELETE"
        }
    );

    const result = await response.json();

    alert(result.message);

    loadAll();
}


// =========================================================
// حماية عرض النصوص
// =========================================================

function escapeHtml(text) {

    if (text === null || text === undefined) {
        return "";
    }

    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// تشغيل النظام
loadAll();

</script>

</body>
</html>
"""


# =========================================================
# الصفحة
# =========================================================

@app.route("/")
def home():
    return render_template_string(HTML)


# =========================================================
# API - كل البيانات
# =========================================================

@app.route("/api/data")
def get_data():
    return jsonify(data)


# =========================================================
# الطلاب
# =========================================================

@app.route("/api/students", methods=["POST"])
def add_student():

    body = request.get_json() or {}

    name = str(body.get("name", "")).strip()
    age = body.get("age", "")
    class_name = str(body.get("class_name", "")).strip()
    score = body.get("score", 0)
    address = str(body.get("address", "")).strip()

    if not name or not class_name:
        return jsonify({
            "message": "اسم الطالب والصف مطلوبان."
        }), 400

    try:
        age = int(age)
    except:
        age = 0

    try:
        score = float(score)
    except:
        score = 0

    student = {
        "id": next_id(data["students"]),
        "name": name,
        "age": age,
        "class_name": class_name,
        "score": score,
        "address": address,
        "date": str(date.today())
    }

    data["students"].append(student)

    save_data()

    return jsonify({
        "message": "تمت إضافة الطالب بنجاح.",
        "student": student
    })


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):

    student = next(
        (s for s in data["students"] if s["id"] == student_id),
        None
    )

    if not student:
        return jsonify({
            "message": "الطالب غير موجود."
        }), 404

    data["students"] = [
        s for s in data["students"]
        if s["id"] != student_id
    ]

    # حذف سجلات مرتبطة بالطالب
    data["attendance"] = [
        a for a in data["attendance"]
        if a.get("student_id") != student_id
    ]

    data["grades"] = [
        g for g in data["grades"]
        if g.get("student_id") != student_id
    ]

    save_data()

    return jsonify({
        "message": "تم حذف الطالب وجميع سجلاته المرتبطة."
    })


# =========================================================
# المدرسون
# =========================================================

@app.route("/api/teachers", methods=["POST"])
def add_teacher():

    body = request.get_json() or {}

    name = str(body.get("name", "")).strip()
    subject = str(body.get("subject", "")).strip()
    phone = str(body.get("phone", "")).strip()

    if not name or not subject:
        return jsonify({
            "message": "اسم المدرس والمادة مطلوبان."
        }), 400

    teacher = {
        "id": next_id(data["teachers"]),
        "name": name,
        "subject": subject,
        "phone": phone
    }

    data["teachers"].append(teacher)

    save_data()

    return jsonify({
        "message": "تمت إضافة المدرس بنجاح."
    })


@app.route("/api/teachers/<int:teacher_id>", methods=["DELETE"])
def delete_teacher(teacher_id):

    before = len(data["teachers"])

    data["teachers"] = [
        t for t in data["teachers"]
        if t["id"] != teacher_id
    ]

    if len(data["teachers"]) == before:
        return jsonify({
            "message": "المدرس غير موجود."
        }), 404

    save_data()

    return jsonify({
        "message": "تم حذف المدرس."
    })


# =========================================================
# الحضور
# =========================================================

@app.route("/api/attendance", methods=["POST"])
def add_attendance():

    body = request.get_json() or {}

    student_id = body.get("student_id")
    status = body.get("status", "حاضر")

    try:
        student_id = int(student_id)
    except:
        return jsonify({
            "message": "رقم الطالب غير صحيح."
        }), 400

    student = next(
        (
            s for s in data["students"]
            if s["id"] == student_id
        ),
        None
    )

    if not student:
        return jsonify({
            "message": "الطالب غير موجود."
        }), 404

    today = str(date.today())

    # لو الطالب سجل اليوم قبل كده يتم تحديث سجله
    existing = next(
        (
            a for a in data["attendance"]
            if a.get("student_id") == student_id
            and a.get("date") == today
        ),
        None
    )

    if existing:

        existing["status"] = status

        save_data()

        return jsonify({
            "message": "تم تحديث حالة حضور الطالب اليوم."
        })

    record = {
        "id": next_id(data["attendance"]),
        "student_id": student_id,
        "student_name": student["name"],
        "status": status,
        "date": today
    }

    data["attendance"].append(record)

    save_data()

    return jsonify({
        "message": "تم تسجيل الحضور بنجاح."
    })


@app.route("/api/attendance/<int:record_id>", methods=["DELETE"])
def delete_attendance(record_id):

    before = len(data["attendance"])

    data["attendance"] = [
        a for a in data["attendance"]
        if a["id"] != record_id
    ]

    if len(data["attendance"]) == before:
        return jsonify({
            "message": "السجل غير موجود."
        }), 404

    save_data()

    return jsonify({
        "message": "تم حذف سجل الحضور."
    })


# =========================================================
# الدرجات
# =========================================================

@app.route("/api/grades", methods=["POST"])
def add_grade():

    body = request.get_json() or {}

    student_id = body.get("student_id")
    subject = str(body.get("subject", "")).strip()
    score = body.get("score")

    try:
        student_id = int(student_id)
        score = float(score)
    except:
        return jsonify({
            "message": "بيانات الدرجة غير صحيحة."
        }), 400

    if not subject:
        return jsonify({
            "message": "اسم المادة مطلوب."
        }), 400

    if score < 0 or score > 100:
        return jsonify({
            "message": "الدرجة يجب أن تكون من 0 إلى 100."
        }), 400

    student = next(
        (
            s for s in data["students"]
            if s["id"] == student_id
        ),
        None
    )

    if not student:
        return jsonify({
            "message": "الطالب غير موجود."
        }), 404

    record = {
        "id": next_id(data["grades"]),
        "student_id": student_id,
        "student_name": student["name"],
        "subject": subject,
        "score": score,
        "date": str(date.today())
    }

    data["grades"].append(record)

    save_data()

    return jsonify({
        "message": "تمت إضافة الدرجة بنجاح."
    })


@app.route("/api/grades/<int:grade_id>", methods=["DELETE"])
def delete_grade(grade_id):

    before = len(data["grades"])

    data["grades"] = [
        g for g in data["grades"]
        if g["id"] != grade_id
    ]

    if len(data["grades"]) == before:
        return jsonify({
            "message": "الدرجة غير موجودة."
        }), 404

    save_data()

    return jsonify({
        "message": "تم حذف الدرجة."
    })


# =========================================================
# تشغيل البرنامج
# =========================================================

if __name__ == "__main__":

    print("=" * 50)
    print("🏫 نظام إدارة المدرسة")
    print("🌐 http://127.0.0.1:8000")
    print("=" * 50)

    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )
