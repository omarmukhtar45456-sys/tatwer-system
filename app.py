import os
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- إعدادات المجلدات ---
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- قاعدة بيانات مؤقتة (للعرض أونلاين) ---
users = {"admin": {"password": "123", "role": "قائد"}, "worker": {"password": "456", "role": "عامل"}}
properties = []
stats = {"worker_logins": 0}

# --- التصميم الكامل (CSS) ---
STYLE = '''
<style>
    body { direction: rtl; font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; }
    .container { max-width: 1250px; margin: auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
    .login-box { max-width: 350px; margin: 80px auto; text-align: center; background: white; padding: 40px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
    .login-box img { max-width: 150px; margin-bottom: 20px; border-radius: 10px; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #fff; overflow: hidden; border-radius: 10px; }
    th { background: #1a202c; color: white; padding: 15px; text-align: center; font-size: 14px; }
    td { padding: 12px; border-bottom: 1px solid #edf2f7; text-align: center; font-size: 14px; }
    
    .status-badge { padding: 5px 12px; border-radius: 15px; color: white; font-weight: bold; font-size: 11px; }
    .status-متاح { background: #48bb78; } .status-محجوز { background: #ecc94b; color: #000; } .status-متباع { background: #f56565; }
    
    .btn { padding: 8px 15px; border-radius: 6px; text-decoration: none; font-size: 13px; cursor: pointer; border: none; transition: 0.3s; }
    .btn-file { background: #3182ce; color: white; }
    .btn-edit { background: #ecc94b; color: black; margin: 0 2px; }
    .btn-delete { background: #e53e3e; color: white; margin: 0 2px; }
    .btn-add { background: #2f855a; color: white; padding: 10px 20px; font-weight: bold; width: 100%; margin-top: 10px; }
    
    .stats-card { background: #ebf8ff; padding: 12px 20px; border-radius: 8px; border-right: 5px solid #3182ce; margin-bottom: 20px; display: inline-block; font-weight: bold; color: #2c5282; }
    .admin-form { background: #f7fafc; padding: 25px; border-radius: 12px; margin-bottom: 30px; border: 1px solid #e2e8f0; }
    .form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; }
    input, select, textarea { padding: 10px; border: 1px solid #cbd5e0; border-radius: 8px; font-family: inherit; font-size: 14px; }
    textarea { grid-column: span 1; height: 42px; resize: none; }
</style>
'''

# --- السماح بقراءة اللوجو من فولدر far الخاص بك ---
@app.route('/far/<path:filename>')
def get_far_logo(filename):
    return send_from_directory('far', filename)

@app.route('/')
def login_page():
    return f'''{STYLE}
    <div class="login-box">
        <img src="/far/logo.png" onerror="this.src='https://via.placeholder.com/150?text=Far+Logo+Missing'">
        <h2 style="color:#2d3748;">نظام إدارة العقارات</h2>
        <form action="/login" method="post">
            <input type="text" name="u" placeholder="اسم المستخدم" style="width:100%; margin-bottom:15px;" required><br>
            <input type="password" name="p" placeholder="كلمة السر" style="width:100%; margin-bottom:15px;" required><br>
            <button type="submit" class="btn btn-add">تسجيل الدخول</button>
        </form>
    </div>'''

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form['u'], request.form['p']
    if u in users and users[u]['password'] == p:
        if users[u]['role'] == "عامل": stats['worker_logins'] += 1
        return redirect(url_for('dashboard', user=u))
    return "خطأ في تسجيل الدخول! <a href='/'>حاول مرة أخرى</a>"

@app.route('/dashboard/<user>')
def dashboard(user):
    role = users[user]['role']
    rows = ""
    for p in reversed(properties):
        admin_actions = ""
        if role == "قائد":
            admin_actions = f'''
                <a href="/edit_page/{p['id']}" class="btn btn-edit">تعديل</a>
                <a href="/delete/{p['id']}" class="btn btn-delete" onclick="return confirm('هل أنت متأكد من الحذف؟')">حذف</a>
            '''
        
        rows += f'''<tr>
            <td><img src="/static/uploads/{p['img']}" width="55" style="border-radius:5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);"></td>
            <td><b>{p['id_num']}</b></td>
            <td>{p['area']}</td>
            <td>{p['region']}</td>
            <td>{p['price']} ج.م</td>
            <td><span class="status-badge status-{p['status']}">{p['status']}</span></td>
            <td>
                <a href="/property/{p['id']}" class="btn btn-file">📂 فتح الملف</a>
                {admin_actions}
            </td>
        </tr>'''

    admin_header = ""
    if role == "قائد":
        admin_header = f'''
        <div class="stats-card">📊 مراقبة النظام: دخل العمال {stats['worker_logins']} مرة</div>
        <div class="admin-form">
            <h4 style="margin-top:0;">➕ إضافة بيان جديد</h4>
            <form action="/add" method="post" enctype="multipart/form-data">
                <div class="form-row">
                    <input type="text" name="id_num" placeholder="رقم القطعة" required>
                    <input type="text" name="area" placeholder="المساحة" required>
                    <input type="text" name="region" placeholder="المنطقة" required>
                    <input type="text" name="price" placeholder="السعر" required>
                    <select name="status"><option>متاح</option><option>محجوز</option><option>متباع</option></select>
                    <textarea name="note" placeholder="أضف ملحوظاتك هنا..."></textarea>
                    <input type="file" name="img" accept="image/*" required style="font-size:11px;">
                </div>
                <button type="submit" class="btn btn-add">حفظ البيانات ونشرها للموظفين</button>
            </form>
        </div>'''

    return f'''{STYLE}<div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #edf2f7; margin-bottom:20px; padding-bottom:10px;">
            <h3>🏠 لوحة التحكم | مرحباً {user}</h3>
            <a href="/" style="color:#e53e3e; font-weight:bold; text-decoration:none; font-size:14px;">🚪 تسجيل الخروج</a>
        </div>
        {admin_header}
        <table>
            <tr><th>معاينة</th><th>رقم القطعة</th><th>المساحة</th><th>المنطقة</th><th>السعر</th><th>الحالة</th><th>الإجراءات</th></tr>
            {rows if rows else '<tr><td colspan="7" style="padding:40px; color:#a0aec0;">لا توجد عقارات مضافة حتى الآن</td></tr>'}
        </table>
    </div>'''

@app.route('/edit_page/<int:pid>')
def edit_page(pid):
    p = next(x for x in properties if x['id'] == pid)
    return f'''{STYLE}
    <div class="container" style="max-width:550px; margin-top:40px;">
        <h3 style="border-bottom:1px solid #eee; padding-bottom:10px;">✏️ تعديل بيانات القطعة: {p['id_num']}</h3>
        <form action="/update/{pid}" method="post">
            <div style="display:flex; flex-direction:column; gap:12px; margin-top:20px;">
                <label>رقم القطعة:</label><input type="text" name="id_num" value="{p['id_num']}">
                <label>المساحة:</label><input type="text" name="area" value="{p['area']}">
                <label>المنطقة:</label><input type="text" name="region" value="{p['region']}">
                <label>السعر:</label><input type="text" name="price" value="{p['price']}">
                <label>الحالة:</label>
                <select name="status">
                    <option {"selected" if p['status']=="متاح" else ""}>متاح</option>
                    <option {"selected" if p['status']=="محجوز" else ""}>محجوز</option>
                    <option {"selected" if p['status']=="متباع" else ""}>متباع</option>
                </select>
                <label>ملحوظات المدير:</label>
                <textarea name="note" style="height:100px;">{p['note']}</textarea>
                <button type="submit" class="btn btn-add">تحديث البيانات</button>
                <a href="javascript:history.back()" style="text-align:center; color:#718096; margin-top:10px;">إلغاء التعديل</a>
            </div>
        </form>
    </div>'''

@app.route('/update/<int:pid>', methods=['POST'])
def update(pid):
    for p in properties:
        if p['id'] == pid:
            p['id_num'], p['area'], p['price'] = request.form['id_num'], request.form['area'], request.form['price']
            p['region'], p['status'], p['note'] = request.form['region'], request.form['status'], request.form['note']
    return redirect(url_for('dashboard', user='admin'))

@app.route('/delete/<int:pid>')
def delete(pid):
    global properties
    properties = [p for p in properties if p['id'] != pid]
    return redirect(url_for('dashboard', user='admin'))

@app.route('/property/<int:pid>')
def view_property(pid):
    p = next(x for x in properties if x['id'] == pid)
    return f'''{STYLE}
    <div class="container" style="max-width:750px; text-align:center;">
        <h2 style="color:#2d3748; margin-bottom:20px;">📄 ملف العقار: {p['id_num']}</h2>
        <img src="/static/uploads/{p['img']}" style="width:100%; border-radius:15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);">
        <div style="text-align:right; background:#f7fafc; padding:30px; border-radius:15px; margin-top:20px; font-size:18px; line-height:2;">
            <p>🔢 <b>رقم القطعة:</b> {p['id_num']}</p>
            <p>📐 <b>المساحة الكلية:</b> {p['area']}</p>
            <p>📍 <b>المنطقة / الموقع:</b> {p['region']}</p>
            <p>💰 <b>السعر المطلوب:</b> <span style="color:#2f855a; font-weight:bold;">{p['price']} ج.م</span></p>
            <p>🔔 <b>حالة العقار:</b> <span class="status-badge status-{p['status']}">{p['status']}</span></p>
            <hr style="border:0; border-top:1px solid #e2e8f0; margin:20px 0;">
            <p>📝 <b>ملحوظات وتفاصيل إضافية:</b><br> 
            <span style="color:#4a5568; font-size:16px; background:white; padding:10px; display:block; border-radius:8px; border:1px solid #edf2f7;">{p['note'] if p['note'] else 'لا توجد ملحوظات إضافية مكتوبة.'}</span></p>
        </div>
        <br><a href="javascript:history.back()" class="btn btn-file" style="padding:12px 50px; font-size:16px;">إغلاق والعودة للجدول</a>
    </div>'''

@app.route('/add', methods=['POST'])
def add():
    file = request.files['img']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    properties.append({
        "id": len(properties) + 1,
        "id_num": request.form['id_num'], "area": request.form['area'],
        "region": request.form['region'], "price": request.form['price'],
        "status": request.form['status'], "note": request.form['note'], "img": filename
    })
    return redirect(url_for('dashboard', user='admin'))

if __name__ == '__main__':
    app.run(debug=True)