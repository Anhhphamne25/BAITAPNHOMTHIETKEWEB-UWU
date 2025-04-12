from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client
import uuid
import psycopg2

app = Flask(__name__)
app.secret_key = "super-secret-key"

# Supabase config
SUPABASE_URL = "https://lxmdgtxnbwmpbwsglice.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx4bWRndHhuYndtcGJ3c2dsaWNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQyMjI0OTcsImV4cCI6MjA1OTc5ODQ5N30.BhxdSoSRicYcdu5T7il3hI4vG7jhZaOZGHFIzSVwdAw"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def first():
    return redirect(url_for('login'))

#ĐĂNG KÝ
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        existing = supabase.table("user").select("*").eq("username", username).execute()
        if existing.data:
            message1 = "Username đã tồn tại."
            return render_template('register.html', message=message1)
        if password != confirm_password:
            message2 = "Mật khẩu không khớp."
            return render_template('register.html', message=message2)

        supabase.table("user").insert({
            "username": username,
            "email": email,
            "password": password
        }).execute()
        return redirect(url_for('login'))
    return render_template('register.html')




# ĐĂNG NHẬP
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        result = supabase.table("user").select("*").eq("username", username).execute()
        user = result.data[0] if result.data else None

        if user and user["password"] == password:
            session['usermail'] = user['email']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            message = "Đăng nhập không thành công. Vui lòng kiểm tra lại thông tin."
            return render_template('login.html', message=message)
    return render_template('login.html')



# QUÊN MẬT KHẨU
@app.route('/forgotpass', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        result = supabase.table("user").select("*").eq("email", email).execute()
        user = result.data[0] if result.data else None
        if user and user["password"] != old_password:
            message1 = "Mật khẩu cũ không đúng."
            return render_template('forgotpass.html', mess=message1)
        if user and user["password"] == old_password:
            message2 = "Nhớ thì đổi làm gì"
            return render_template('forgotpass.html', mess=message2)
        if user and new_password != confirm_password:
            message3 = "Mật khẩu mới không khớp."
            return render_template('forgotpass.html', message=message3)
    return render_template('forgotpass.html')



#TRANG CHỦ
@app.route('/home', methods=['GET','POST'])
def home():
    username = session.get('username')
    if not username:
        return render_template('home.html', notaccount = 1)
    try:
        result = supabase.table("in4user").select("img").eq("username", username).execute()
        img = result.data[0]['img'] if result.data else None
    except Exception as e:
        img = None
    return render_template('home.html', username=username, img=img)

#TRANG TÀI KHOẢN
@app.route('/account/<username>', methods=['GET', 'POST'])
def account(username):
    if request.method == 'POST':
        if 'img' in request.files:
            img = request.files['img']
            img.save(f'static/images/{img.filename}')
            supabase.table("in4user").update({"img": img.filename}).eq("username", username).execute()
        return redirect(url_for('account', username=username))
    result = supabase.table("in4user").select("*").eq("username", username).execute()
    user_info = result.data[0] if result.data else None
    return render_template('account.html', user_info=user_info)

#TRANG THÊM BÀI NGHIÊN CỨU
@app.route('/addresearch', methods=['GET', 'POST'])
def add_research():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        abstract = request.form['abstract']
        file = request.files['file']
        filename = f"{uuid.uuid4()}_{file.filename}"
        file.save(f'static/uploads/{filename}')
        supabase.table("research").insert({
            "title": title,
            "author": author,
            "abstract": abstract,
            "file": filename
        }).execute()
        return redirect(url_for('home'))
    return render_template('addresearch.html')




#TRANG XEM BÀI NGHIÊN CỨU
@app.route('/viewresearch/<research_id>', methods=['GET'])
def view_research():
    result = supabase.table("research").select("*").execute()
    research_list = result.data if result.data else []
    return render_template('viewresearch.html', research_list=research_list)





#TRANG CATETORY
@app.route('/category', methods=['GET'])
def category(category_name):
    result = supabase.table("research").select("*").eq("category", category_name).execute()
    research_list = result.data if result.data else []
    return render_template('category.html', research_list=research_list, category_name=category_name)









#TRANG TÌM KIẾM BÀI NGHIÊN CỨU
@app.route('/search/<keyword>', methods=['GET'])
def search():
    keyword = request.args.get('keyword')
    if keyword:
        result = supabase.table("research").select("*").ilike("title", f"%{keyword}%").execute()
        research_list = result.data if result.data else []
    else:
        research_list = []
    return render_template('search.html', research_list=research_list)











if __name__ == '__main__':
    app.run(debug=True)
