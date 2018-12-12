from flask import Flask, request, render_template, session, redirect, url_for
from models.user import User
import mlab
mlab.connect()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'teamcolorpictures'

@app.route('/homepage') # Hiển thị trang chủ
def homepage():
    return render_template('homepage.html')

@app.route('/signup', methods=['GET', 'POST']) # Đăng ký tài khoản
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    else:
        form = request.form
        f = form['fullname']
        u = form['username']
        p = form['password']
        e = form['email']
        new_user = User(fulname=f, username=u, password=p, email=e)
        user_check = User.objects(username=u).first()        
        email_check = User.objects(email=e).first()
        if user_check is None:
            return "Username đã tồn tại" # Làm sao để hiện thông báo ngay trên trang Login?
        elif email_check is None:
            return "Email đã tồn tại" # Làm sao để hiện thông báo ngay trên trang Login?
        else:
            new_user.save()
            return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST']) # Đăng nhập
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        form = request.form
        u = form['username']
        p = form['password']
        user_check = User.objects(username=u).first()
        if user_check is None:
            return 'Username khong ton tai'
        elif p != user_check.password:
            return 'Password khong hop le'
        else:
            session['token'] = u
            return redirect(url_for('myprofile'))

@app.route('/logout') # Đăng xuất
def logout():
    if 'token' in session:
        del session['token']
    return redirect(url_for('homepage'))

@app.route('/top100pics') # Hiển thị 100 Pics đc nhiều like nhất
def top100pics():
    return render_template('top100pics.html')

@app.route('/top100artists') # Hiển thị 100 Artists đc nhiều like nhất
def top100artists():
    return render_template('top100artists.html')

@app.route('/<artist_profile>') # Hiển thị trang cá nhân của 1 artist không phải mình
def profile_artist(user):
    return render_template('artist_profile.html')

@app.route('/<artist>/<finished_picname>') # Hiển thị hình phóng to của một bức tranh cụ thể của 1 artist cụ thể,
# khi click vào tranh đó
def onepic_showing(artist, finished_picname):
    return render_template('onepic_showing.html')

@app.route('/myprofile/<project>') # Hiển thị trang profile của mình
def myprofile(project):
    if project == 'working':
        return render_template('working.html')
    elif project == 'finished':
        return render_template('finished.html')

@app.route('<category>') # Hiển thị category sau khi người dùng click vào 1 category cụ thể. 
# VD: click vào mục Animals sẽ hiện luôn ra trang có danh sách các tranh Animal
def category(category):
    return render_template('category.html')

@app.route('/painting/<picname>') # Hiển thị ra trang vẽ tranh khi click vào 1 bức tranh tìm thấy trong category,
# hoặc click vào Get me a random pic
def randompic(picname):
    return print(picname)
    
if __name__ == '__main__':
  app.run(debug=True)