from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import datetime
import os
import webbrowser
HOST = "127.0.0.1"
PORT = 8000
DATA_FILE = "school_data.json"

DEFAULT_DATA = {
    "students": [],
    "teachers": [],
    "attendance": [],
    "grades": []
}

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for key in DEFAULT_DATA:
                data.setdefault(key, [])
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_DATA.copy()

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>نظام إدارة المدرسة - الإصدار الكامل</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:Tahoma,Arial,sans-serif;background:#0b1120;color:#f8fafc}
button,input,select{font:inherit}
.layout{min-height:100vh;display:flex}
.sidebar{position:fixed;right:0;top:0;bottom:0;width:245px;background:#111827;border-left:1px solid #263244;padding:22px 15px}
.logo{font-size:23px;font-weight:800;padding:10px;margin-bottom:22px}
.logo span{color:#60a5fa}
.nav button{width:100%;border:0;background:transparent;color:#cbd5e1;padding:13px 14px;border-radius:10px;text-align:right;margin:3px 0;cursor:pointer}
.nav button:hover,.nav button.active{background:#2563eb;color:#fff}
.main{margin-right:245px;width:calc(100% - 245px);padding:30px}
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:22px}
h1{margin:0;font-size:29px}h2{margin-top:0}.sub{color:#94a3b8;margin-top:7px}
.date{background:#111827;border:1px solid #263244;border-radius:10px;padding:10px 14px;color:#cbd5e1}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:18px}
.card,.panel{background:#111827;border:1px solid #263244;border-radius:16px}
.card{padding:18px}.card small{color:#94a3b8}.num{font-size:28px;font-weight:bold;margin-top:9px}
.panel{padding:20px;margin-bottom:18px}
.grid{display:grid;grid-template-columns:330px 1fr;gap:18px}
label{display:block;color:#94a3b8;font-size:13px;margin:11px 0 5px}
input,select{width:100%;background:#1e293b;color:#fff;border:1px solid #334155;border-radius:9px;padding:11px;outline:none}
input:focus,select:focus{border-color:#60a5fa}
.btn{border:0;border-radius:9px;padding:10px 14px;cursor:pointer}
.primary{background:#2563eb;color:white}.danger{background:#dc2626;color:white}.secondary{background:#334155;color:white}
.full{width:100%;margin-top:15px}
.toolbar{display:flex;gap:8px;margin-bottom:13px}
.toolbar input{flex:1}
.table-wrap{overflow:auto}
table{width:100%;border-collapse:collapse;min-width:650px}
th,td{padding:12px 9px;border-bottom:1px solid #263244;text-align:right}
th{color:#94a3b8;font-size:13px}
.badge{display:inline-block;padding:4px 8px;border-radius:999px;background:#064e3b;color:#86efac;font-size:12px}
.section{display:none}.section.active{display:block}
.notice{padding:14px;border-radius:10px;background:#172033;color:#cbd5e1;margin-top:12px}
.empty{text-align:center;color:#94a3b8;padding:35px}
.settings-row{display:flex;justify-content:space-between;align-items:center;padding:15px 0;border-bottom:1px solid #263244}
@media(max-width:950px){.sidebar{width:190px}.main{margin-right:190px;width:calc(100% - 190px)}.cards{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}}
@media(max-width:650px){.layout{display:block}.sidebar{position:static;width:100%}.main{margin:0;width:100%;padding:17px}.cards{grid-template-columns:1fr 1fr}.top{display:block}.date{display:inline-block;margin-top:10px}}
</style>
</head>
<body>
<div class="layout">
<aside class="sidebar">
  <div class="logo">🏫 <span>مدرستي</span></div>
  <div class="nav">
    <button class="active" onclick="show('dashboard',this)">🏠 لوحة التحكم</button>
    <button onclick="show('attendance',this)">📝 الحضور والغياب</button>
    <button onclick="show('grades',this)">📚 الدرجات</button>
    <button onclick="show('teachers',this)">👨‍🏫 المدرسين</button>
    <button onclick="show('students',this)">👨‍🎓 الطلاب</button>
    <button onclick="show('settings',this)">⚙️ الإعدادات</button>
  </div>
</aside>

<main class="main">

<section id="dashboard" class="section active">
  <div class="top">
    <div><h1>لوحة التحكم</h1><div class="sub">نظرة سريعة على نظام إدارة المدرسة</div></div>
    <div class="date" id="today"></div>
  </div>
  <div class="cards">
    <div class="card"><small>إجمالي الطلاب</small><div class="num" id="studentCount">0</div></div>
    <div class="card"><small>المدرسون</small><div class="num" id="teacherCount">0</div></div>
    <div class="card"><small>متوسط الدرجات</small><div class="num" id="avgScore">0</div></div>
    <div class="card"><small>حضور اليوم</small><div class="num" id="presentCount">0</div></div>
  </div>
  <div class="panel">
    <h2>آخر الطلاب</h2>
    <div class="table-wrap"><table><thead><tr><th>الاسم</th><th>الصف</th><th>الدرجة</th><th>تاريخ التسجيل</th></tr></thead>
    <tbody id="latest"></tbody></table></div>
  </div>
</section>

<section id="attendance" class="section">
  <div class="top">
    <div><h1>📝 الحضور والغياب</h1><div class="sub">تسجيل ومتابعة حضور وغياب الطلاب يوميًا</div></div>
    <div class="date" id="attendanceDate"></div>
  </div>

  <div class="cards">
    <div class="card"><small>إجمالي السجلات</small><div class="num" id="attTotal">0</div></div>
    <div class="card"><small>حاضر اليوم</small><div class="num" id="attPresent">0</div></div>
    <div class="card"><small>غائب اليوم</small><div class="num" id="attAbsent">0</div></div>
    <div class="card"><small>نسبة الحضور اليوم</small><div class="num" id="attRate">0%</div></div>
  </div>

  <div class="grid">
    <div class="panel">
      <h2>➕ تسجيل الحضور</h2>
      <label>الطالب</label>
      <select id="attStudent"></select>
      <label>الحالة</label>
      <div style="display:flex;gap:8px;margin-top:5px">
        <button class="btn primary" style="flex:1" onclick="saveAttendance('حاضر')">✅ حاضر</button>
        <button class="btn danger" style="flex:1" onclick="saveAttendance('غائب')">❌ غائب</button>
      </div>
      <div class="notice">التاريخ يتم تسجيله تلقائيًا بتاريخ اليوم.</div>
    </div>

    <div class="panel">
      <div class="toolbar">
        <input id="attendanceSearch" placeholder="🔎 بحث باسم الطالب..." oninput="renderAttendance()">
        <button class="btn secondary" onclick="load()">تحديث</button>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>الطالب</th><th>التاريخ</th><th>الحالة</th><th></th></tr></thead>
          <tbody id="attendanceTable"></tbody>
        </table>
      </div>
    </div>
  </div>
</section>

<section id="grades" class="section">
  <div class="top"><div><h1>📚 الدرجات</h1><div class="sub">إضافة درجات للطلاب ومتابعة النتائج</div></div></div>
  <div class="grid">
    <div class="panel">
      <h2>إضافة درجة</h2>
      <label>الطالب</label><select id="gradeStudent"></select>
      <label>المادة</label><input id="subject" placeholder="الرياضيات">
      <label>الدرجة</label><input id="gradeValue" type="number" min="0" max="100" placeholder="90">
      <button class="btn primary full" onclick="addGrade()">حفظ الدرجة</button>
    </div>
    <div class="panel">
      <h2>سجل الدرجات</h2>
      <div class="table-wrap"><table><thead><tr><th>الطالب</th><th>المادة</th><th>الدرجة</th><th>التاريخ</th></tr></thead>
      <tbody id="gradesTable"></tbody></table></div>
    </div>
  </div>
</section>

<section id="teachers" class="section">
  <div class="top"><div><h1>👨‍🏫 المدرسين</h1><div class="sub">إدارة بيانات المدرسين</div></div></div>
  <div class="grid">
    <div class="panel">
      <h2>إضافة مدرس</h2>
      <label>اسم المدرس</label><input id="teacherName" placeholder="محمد أحمد">
      <label>المادة</label><input id="teacherSubject" placeholder="اللغة العربية">
      <label>الهاتف</label><input id="teacherPhone" placeholder="01xxxxxxxxx">
      <button class="btn primary full" onclick="addTeacher()">➕ إضافة المدرس</button>
    </div>
    <div class="panel">
      <h2>قائمة المدرسين</h2>
      <div class="table-wrap"><table><thead><tr><th>#</th><th>الاسم</th><th>المادة</th><th>الهاتف</th><th></th></tr></thead>
      <tbody id="teachersTable"></tbody></table></div>
    </div>
  </div>
</section>

<section id="students" class="section">
  <div class="top"><div><h1>👨‍🎓 الطلاب</h1><div class="sub">إضافة والبحث عن الطلاب</div></div></div>
  <div class="grid">
    <div class="panel">
      <h2>إضافة طالب</h2>
      <label>اسم الطالب</label><input id="studentName" placeholder="أحمد محمد">
      <label>العمر</label><input id="studentAge" type="number" placeholder="13">
      <label>الصف</label><input id="studentClass" placeholder="الأول الإعدادي">
      <label>الدرجة</label><input id="studentScore" type="number" min="0" max="100" placeholder="90">
      <label>العنوان</label><input id="studentAddress" placeholder="العنوان">
      <button class="btn primary full" onclick="addStudent()">➕ إضافة الطالب</button>
    </div>
    <div class="panel">
      <div class="toolbar"><input id="studentSearch" placeholder="🔎 بحث باسم الطالب..." oninput="renderStudents()"><button class="btn secondary" onclick="load()">تحديث</button></div>
      <div class="table-wrap"><table><thead><tr><th>#</th><th>الاسم</th><th>الصف</th><th>العمر</th><th>الدرجة</th><th></th></tr></thead>
      <tbody id="studentsTable"></tbody></table></div>
    </div>
  </div>
</section>

<section id="settings" class="section">
  <div class="top"><div><h1>⚙️ الإعدادات</h1><div class="sub">إعدادات النظام</div></div></div>
  <div class="panel">
    <div class="settings-row"><span>اسم النظام</span><strong>نظام إدارة المدرسة</strong></div>
    <div class="settings-row"><span>حفظ البيانات</span><strong>تلقائي 💾</strong></div>
    <div class="settings-row"><span>قاعدة البيانات</span><strong>school_data.json</strong></div>
    <div class="notice">كل البيانات محفوظة محليًا على جهازك داخل ملف واحد للبيانات.</div>
  </div>
</section>

</main>
</div>

<script>
let data={students:[],teachers:[],attendance:[],grades:[]};

function show(id,btn){
 document.querySelectorAll('.section').forEach(x=>x.classList.remove('active'));
 document.getElementById(id).classList.add('active');
 document.querySelectorAll('.nav button').forEach(x=>x.classList.remove('active'));
 btn.classList.add('active');
}

async function load(){
 const r=await fetch('/api/data'); data=await r.json();
 renderAll();
}
function esc(v){return String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));}
function opts(id){
 const s=document.getElementById(id);
 s.innerHTML=data.students.length?data.students.map(x=>`<option value="${x.id}">${esc(x.name)}</option>`).join(''):'<option value="">لا يوجد طلاب</option>';
}
function renderAll(){
 document.getElementById('studentCount').textContent=data.students.length;
 document.getElementById('teacherCount').textContent=data.teachers.length;
 const avg=data.students.length?data.students.reduce((a,x)=>a+Number(x.score||0),0)/data.students.length:0;
 document.getElementById('avgScore').textContent=avg.toFixed(1);
 const today=new Date().toISOString().slice(0,10);
 document.getElementById('presentCount').textContent=data.attendance.filter(x=>x.date===today&&x.status==='حاضر').length;
 document.getElementById('today').textContent=new Date().toLocaleDateString('ar-EG');

 const latest=[...data.students].reverse().slice(0,5);
 document.getElementById('latest').innerHTML=latest.length?latest.map(x=>`<tr><td>${esc(x.name)}</td><td>${esc(x.class_name)}</td><td>${x.score}</td><td>${x.date}</td></tr>`).join(''):'<tr><td colspan="4" class="empty">لا يوجد طلاب</td></tr>';

 renderStudents();renderTeachers();renderAttendance();renderGrades();opts('attStudent');opts('gradeStudent');
}
function renderStudents(){
 const q=(document.getElementById('studentSearch')?.value||'').toLowerCase();
 const a=data.students.filter(x=>(x.name||'').toLowerCase().includes(q));
 document.getElementById('studentsTable').innerHTML=a.length?a.map((x,i)=>`<tr><td>${i+1}</td><td>${esc(x.name)}</td><td>${esc(x.class_name)}</td><td>${x.age}</td><td>${x.score}</td><td><button class="btn danger" onclick="remove('students',${x.id})">حذف</button></td></tr>`).join(''):'<tr><td colspan="6" class="empty">لا يوجد طلاب</td></tr>';
}
function renderTeachers(){
 document.getElementById('teachersTable').innerHTML=data.teachers.length?data.teachers.map((x,i)=>`<tr><td>${i+1}</td><td>${esc(x.name)}</td><td>${esc(x.subject)}</td><td>${esc(x.phone)}</td><td><button class="btn danger" onclick="remove('teachers',${x.id})">حذف</button></td></tr>`).join(''):'<tr><td colspan="5" class="empty">لا يوجد مدرسون</td></tr>';
}
function renderAttendance(){
 const today=new Date().toISOString().slice(0,10);
 const q=(document.getElementById('attendanceSearch')?.value||'').toLowerCase();
 const rows=[...data.attendance].filter(x=>(x.student_name||'').toLowerCase().includes(q)).reverse();
 const present=data.attendance.filter(x=>x.date===today&&x.status==='حاضر').length;
 const absent=data.attendance.filter(x=>x.date===today&&x.status==='غائب').length;
 const totalToday=present+absent;
 document.getElementById('attTotal').textContent=data.attendance.length;
 document.getElementById('attPresent').textContent=present;
 document.getElementById('attAbsent').textContent=absent;
 document.getElementById('attRate').textContent=(totalToday?Math.round(present/totalToday*100):0)+'%';
 document.getElementById('attendanceDate').textContent=new Date().toLocaleDateString('ar-EG');
 document.getElementById('attendanceTable').innerHTML=rows.length?rows.map(x=>`<tr><td>${esc(x.student_name)}</td><td>${x.date}</td><td><span class="badge" style="${x.status==='غائب'?'background:#4c0519;color:#fda4af':''}">${esc(x.status)}</span></td><td><button class="btn danger" onclick="remove('attendance',${x.id})">حذف</button></td></tr>`).join(''):'<tr><td colspan="4" class="empty">لا يوجد سجل حضور</td></tr>';
}
async function saveAttendance(status){
 if(!attStudent.value){alert('أضف طالبًا أولًا');return}
 const s=data.students.find(x=>x.id==attStudent.value);
 await post('/api/attendance',{student_id:s.id,student_name:s.name,status:status});
}
function renderGrades(){
 document.getElementById('gradesTable').innerHTML=data.grades.length?[...data.grades].reverse().map(x=>`<tr><td>${esc(x.student_name)}</td><td>${esc(x.subject)}</td><td>${x.score}</td><td>${x.date}</td></tr>`).join(''):'<tr><td colspan="4" class="empty">لا يوجد درجات</td></tr>';
}
async function post(url,obj){
 const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)});
 const x=await r.json(); if(!x.success) alert(x.message||'حدث خطأ'); else await load(); return x;
}
async function addStudent(){
 const x={name:studentName.value.trim(),age:studentAge.value,class_name:studentClass.value.trim(),score:studentScore.value,address:studentAddress.value.trim()};
 if(!x.name||!x.age||x.score===''){alert('اكتب الاسم والعمر والدرجة');return}
 await post('/api/students',x);['studentName','studentAge','studentClass','studentScore','studentAddress'].forEach(id=>document.getElementById(id).value='');
}
async function addTeacher(){
 const x={name:teacherName.value.trim(),subject:teacherSubject.value.trim(),phone:teacherPhone.value.trim()};
 if(!x.name||!x.subject){alert('اكتب اسم المدرس والمادة');return}
 await post('/api/teachers',x);['teacherName','teacherSubject','teacherPhone'].forEach(id=>document.getElementById(id).value='');
}

async function addGrade(){
 if(!gradeStudent.value||!subject.value||gradeValue.value===''){alert('أكمل البيانات');return}
 const s=data.students.find(x=>x.id==gradeStudent.value);
 await post('/api/grades',{student_id:s.id,student_name:s.name,subject:subject.value.trim(),score:gradeValue.value});
 subject.value='';gradeValue.value='';
}
async function remove(type,id){
 if(!confirm('هل تريد الحذف؟'))return;
 await fetch('/api/'+type+'/'+id,{method:'DELETE'});await load();
}
load();
</script>
</body>
</html>"""

def send_json(handler, obj, status=200):
    raw=json.dumps(obj,ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type","application/json; charset=utf-8")
    handler.send_header("Content-Length",str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=self.path.split("?")[0]
        if path=="/":
            raw=HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        elif path=="/api/data":
            send_json(self,data)
        else:
            send_json(self,{"success":False,"message":"غير موجود"},404)

    def do_POST(self):
        global data
        path=self.path.split("?")[0]
        length=int(self.headers.get("Content-Length",0))
        try: body=json.loads(self.rfile.read(length).decode("utf-8"))
        except: send_json(self,{"success":False,"message":"بيانات غير صحيحة"},400);return
        today=str(datetime.date.today())

        if path=="/api/students":
            try: age=int(body.get("age",0)); score=float(body.get("score",0))
            except: send_json(self,{"success":False,"message":"العمر والدرجة يجب أن يكونا أرقامًا"},400);return
            if not body.get("name"): send_json(self,{"success":False,"message":"اكتب اسم الطالب"},400);return
            obj={"id":max([x.get("id",0) for x in data["students"]],default=0)+1,"name":body["name"],"age":age,"class_name":body.get("class_name",""),"score":score,"address":body.get("address",""),"date":today}
            data["students"].append(obj)
        elif path=="/api/teachers":
            if not body.get("name"): send_json(self,{"success":False,"message":"اكتب اسم المدرس"},400);return
            obj={"id":max([x.get("id",0) for x in data["teachers"]],default=0)+1,"name":body["name"],"subject":body.get("subject",""),"phone":body.get("phone","")}
            data["teachers"].append(obj)
        elif path=="/api/attendance":
            sid=body.get("student_id")
            existing=next((x for x in data["attendance"] if x.get("student_id")==sid and x.get("date")==today),None)
            if existing:
                existing["student_name"]=body.get("student_name")
                existing["status"]=body.get("status")
            else:
                obj={"id":max([x.get("id",0) for x in data["attendance"]],default=0)+1,"student_id":sid,"student_name":body.get("student_name"),"status":body.get("status"),"date":today}
                data["attendance"].append(obj)
        elif path=="/api/grades":
            try: score=float(body.get("score",0))
            except: send_json(self,{"success":False,"message":"الدرجة غير صحيحة"},400);return
            obj={"id":max([x.get("id",0) for x in data["grades"]],default=0)+1,"student_id":body.get("student_id"),"student_name":body.get("student_name"),"subject":body.get("subject"),"score":score,"date":today}
            data["grades"].append(obj)
        else:
            send_json(self,{"success":False,"message":"غير موجود"},404);return
        save_data();send_json(self,{"success":True})

    def do_DELETE(self):
        global data
        parts=self.path.strip("/").split("/")
        if len(parts)!=3 or parts[0]!="api": send_json(self,{"success":False},404);return
        typ=parts[1]
        try: ident=int(parts[2])
        except: send_json(self,{"success":False},400);return
        if typ not in data: send_json(self,{"success":False},404);return
        old=len(data[typ]);data[typ]=[x for x in data[typ] if x.get("id")!=ident]
        if len(data[typ])==old: send_json(self,{"success":False,"message":"العنصر غير موجود"},404);return
        save_data();send_json(self,{"success":True})

    def log_message(self,*args): pass

def main():
    server=ThreadingHTTPServer((HOST,PORT),Handler)
    url=f"http://{HOST}:{PORT}"
    print("="*55)
    print("🏫 نظام إدارة المدرسة")
    print("🌐 افتح:",url)
    print("⛔ لإيقاف النظام: Ctrl+C")
    print("="*55)
    try:
        webbrowser.open(url)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nتم إيقاف النظام.")
    finally:
        server.server_close()

if __name__=="__main__":
    main()#