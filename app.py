from flask import Flask, render_template, request, redirect, session, url_for, flash
from pymongo import MongoClient
import utils
import config

app = Flask(__name__)
app.secret_key = '976650297127'  # Change this in production

# MongoDB setup
client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]
users_col = db['users']

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']
        user = users_col.find_one({'mobile': mobile, 'password': password})
        if user:
            session['user'] = user['mobile']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    sheet_data = utils.fetch_attendance_sheet()
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        valid = utils.validate_user_in_sheet(name, mobile, sheet_data)
        if valid:
            users_col.insert_one({'name': name, 'mobile': mobile, 'password': mobile, 'role': 'user'})
            flash('User added successfully')
        else:
            flash('Invalid employee or mobile number')
    return render_template('admin_dashboard.html', sheet=sheet_data)

@app.route('/user')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    mobile = session['user']
    sheet_data = utils.fetch_attendance_sheet()
    user_data = utils.get_user_attendance(mobile, sheet_data)
    return render_template('user_dashboard.html', user=user_data)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        old = request.form['old_password']
        new = request.form['new_password']
        user = users_col.find_one({'mobile': session['user'], 'password': old})
        if user:
            users_col.update_one({'mobile': session['user']}, {'$set': {'password': new}})
            flash('Password updated')
        else:
            flash('Old password incorrect')
    return render_template('change_password.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
