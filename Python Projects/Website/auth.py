from operator import index
from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import session
from sqlalchemy.sql.expression import delete, null, update
from sqlalchemy.sql.functions import user
from .models import Note, User
import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random as rand
from .__init__ import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
auth = Blueprint('auth', __name__)
email = ''
data2 = ''
up = False
verified = None
userverified = None
@auth.route('/verify', methods=['GET', 'POST'])
def verify():
    if email:
        if request.method == 'POST':
            code = int(request.form.get('code'))
            if code == pin:
                flash('Email Verified', category='success')
                global verified
                verified = True
                return redirect(url_for('auth.signup'))
            else:
                print(pin)
    else:
        return redirect(url_for('views.home'))
    return render_template("Verify.html", index = "index.js", user=current_user)
@auth.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        global data2
        note = request.form.get('note')
        note_al = Note.query.filter_by(data=note).first()
        if len(note) < 1:
            flash('Note cannot be empty.', category='error')
        elif len(note) > 100000:
            flash('Note cannot exceed 100000 characters.', category='error')
        elif note_al and note_al.user_id == current_user.id:
            pass
        elif up == True:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note updated!', category='success')
            return render_template("notes.html", index = "index.js", user=current_user, data2=data2)
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
            data2 = ''
    return render_template("notes.html", index = "index.js", user=current_user, data2=data2)
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect passsword', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", index = "index.js", user=current_user)
@auth.route('/logout')
@login_required
def logout():
    global verified
    verified = False
    logout_user()
    return redirect(url_for('auth.login'))
@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        global email
        global firstName
        global password1
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email = email).first()
        if user:
            flash('Email already exists, please login.', category='error')
        elif len(email) < 4 or len(email) > 200:
            flash('Please enter a valid email id.', category='error')
        elif len(firstName) < 2 or len(firstName) > 200:
            flash('Name should be more than 1 character and less than 200 characters.', category='error')
        elif password1 != password2:
            flash("Passwords do not match.", category='error')
        elif len(password1) < 7 or len(password1) > 200:
            flash('Password must be at least 7 characters long and less than 200 characters.', category='error')
        else:
            global pin
            pin = rand.randint(1000, 9999)
            global verified
            name = os.environ.get('encrypt_data_name')
            key = os.environ.get('encryption')
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
               smtp.ehlo()
               smtp.starttls()
               smtp.ehlo()
               smtp.login(name, key)
               
               msg = MIMEMultipart("alternative")
               msg["Subject"] = "Email Verification"
               msg["From"] = name
               msg["To"] = email
               text = f"Hi {firstName}, here is your code for email verification - {pin}"
               html = f"""<html><head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <link rel='preconnect' href='https://fonts.googleapis.com'>
<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
<link href='https://fonts.googleapis.com/css2?family=Indie+Flower&display=swap' rel='stylesheet'>
  </head>
  <body style="background-image:linear-gradient(cyan, blue);"><center>
    <div style="border-radius: 10%;width: 50%;background-image:radial-gradient(pink,orange, yellow); border: solid 5px red; border-style:ridge; margin-top:5%;">
    <center><h1 style='font-size: 50px;margin-top: 5%;color: green;'>Email Verification</h1>
    <p style="font-size: 30px; margin-top: 10%; font-family: 'Indie Flower', cursive; color:blue"
  margin-bottom: 230px;'><b>Hi {firstName}, here is your code for email verification - </b><br><br><b style="color: red; font-size: 45px;">{pin}</b></p><br></center>
</div> </center> 
</body>
</html>"""
               part1 = MIMEText(text, "plain")
               part2 = MIMEText(html, "html")
               msg.attach(part1)
               msg.attach(part2)
               smtp.sendmail(name, email, msg.as_string())
            return redirect(url_for('auth.verify'))
    if verified == True:
        new_user = User(email=email, first_name=firstName, password=generate_password_hash(password1, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        name = os.environ.get('encrypt_data_name')
        key = os.environ.get('encryption')
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(name, key)
               
            subject = 'Account Created! Notes App'
            body = f'Hello, {firstName} you have successfully created your account. In this web app you can keep your notes and incase of any problem email to this email address and we would contact you shortly.'
            msg = f'Subject: {subject}\n\n{body}'
            smtp.sendmail(name, email, msg)
            
        flash('Account Created', category='success')
        return redirect(url_for('views.home'))    
    return render_template("sign_up.html", index = "index.js", user=current_user)

emailen = null
pin1 = null
username = null

@auth.route('/forgot', methods=['GET', 'POST'])
def forgot():
    global emailen
    global pin1
    if request.method == "POST":
        emailf = request.form.get('code')
        emailen = User.query.filter_by(email = emailf).first()
        if emailen:
            pin1 = rand.randint(1000, 9999)
            name = os.environ.get('encrypt_data_name')
            key = os.environ.get('encryption')
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
               smtp.ehlo()
               smtp.starttls()
               smtp.ehlo()
               smtp.login(name, key)
               
               msg1 = MIMEMultipart("alternative")
               msg1["Subject"] = "Forgot Password"
               msg1["From"] = name
               msg1["To"] = emailen.email
               global username
               username = emailen.first_name
               text1 = f"Hi {username}, here is your code to reset your password - {pin1}"
               html1 = f"""<html><head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <link rel='preconnect' href='https://fonts.googleapis.com'>
<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
<link href='https://fonts.googleapis.com/css2?family=Indie+Flower&display=swap' rel='stylesheet'>
  </head>
  <body style="background-image:linear-gradient(cyan, blue);"><center>
    <div style="border-radius: 10%;width: 50%;background-image:radial-gradient(pink,orange, yellow); border: solid 5px red; border-style:ridge; margin-top:5%;">
    <center><h1 style='font-size: 50px;margin-top: 5%;color: green;'>Forgot Password</h1>
    <p style="font-size: 30px; margin-top: 10%; font-family: 'Indie Flower', cursive; color:blue"
  margin-bottom: 230px;'><b>Hi {username}, here is your code to reset your password - </b><br><br><b style="color: red; font-size: 45px;">{pin1}</b></p><br></center>
</div> </center> 
</body>
</html>"""
               part1 = MIMEText(text1, "plain")
               part2 = MIMEText(html1, "html")
               msg1.attach(part1)
               msg1.attach(part2)
               smtp.sendmail(name, emailen.email, msg1.as_string())
            return redirect(url_for("auth.forgotnex")) 
        else:
            flash("Account not found, please create a new account!", category="error")
            return redirect(url_for("auth.signup"))
    return render_template("forgot1.html", index = "index.js", user=current_user)
@auth.route('/forgot-next', methods = ["GET", "POST"])
def forgotnex():
    global emailen
    if emailen:
        if request.method == 'POST':
            code = int(request.form.get('code'))
            if code == pin1:
                flash('User Verified!', category='success')
                global userverified
                userverified = True
                return redirect(url_for('auth.reset'))
            else:
                print(pin)
    else:
        return redirect(url_for('views.home'))
    return render_template("forgot.html", index = "index.js", user=current_user)
@auth.route('/reset', methods=["GET", "POST"])
def reset():
    global userverified
    if userverified:
        if request.method =="POST":
            newpass = request.form.get("newpass")
            confirm = request.form.get("confirm")
            if newpass != confirm:
                flash("Passwords do not match.", category='error')
            elif len(newpass) < 7 or len(newpass) > 200:
                flash('Password must be at least 7 characters long and less than 200 characters.', category='error')
            else:
                   hashed = generate_password_hash(newpass, method='sha256')
                   db.session.query(User).update({"password" : hashed})
                   db.session.commit()
                   userverified = False
                   login_user(emailen, remember=True)
                   return redirect(url_for('auth.notes'))
    return render_template("reset.html", index="index.js", user=current_user)
@auth.route('/update-note/<noteId>', methods=['POST', 'GET'])
def update_note(noteId):
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
              global data2
              data2 = note.data
              sessionspec= inspect(note).session
              sessionspec.delete(note)
              sessionspec.commit()
    return redirect('/notes')