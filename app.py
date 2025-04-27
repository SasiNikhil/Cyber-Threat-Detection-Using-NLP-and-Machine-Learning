import numpy as np
from flask import Flask, request, jsonify, render_template
import sqlite3
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import pickle
import random
import smtplib 
from email.message import EmailMessage

app = Flask(__name__)

global username1
model = pickle.load(open('model.pkl', 'rb'))
cv = pickle.load(open('tf.pkl', 'rb'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/home')
def home():
	return render_template('home.html')


@app.route('/Logon')
def logon():
	return render_template('signup.html')

@app.route('/Login')
def login():
	return render_template('signin.html')



@app.route("/signup")
def signup():
    global otp, username, name, email, number, password
    username = request.args.get('t1','')
    name = request.args.get('t2','')
    email = request.args.get('t3','')
    number = request.args.get('t4','')
    password = request.args.get('t5','')
    otp = random.randint(1000,5000)
    print(otp)
    msg = EmailMessage()
    msg.set_content("Your OTP is : "+str(otp))
    msg['Subject'] = 'OTP'
    msg['From'] = "evotingotp4@gmail.com"
    msg['To'] = email
    
    
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("evotingotp4@gmail.com", "xowpojqyiygprhgr")
    s.send_message(msg)
    s.quit()
    return render_template("val.html")

@app.route('/predict_lo', methods=['POST'])
def predict_lo():
    global otp, username, name, email, number, password
    if request.method == 'POST':
        message = request.form['t1']
        print(message)
        if int(message) == otp:
            print("TRUE")
            con = sqlite3.connect('signup.db')
            cur = con.cursor()
            cur.execute("insert into `info` (`user`,`email`, `password`,`mobile`,`name`) VALUES (?, ?, ?, ?, ?)",(username,email,password,number,name))
            con.commit()
            con.close()
            return render_template("signin.html")
    return render_template("signup.html")

@app.route("/signin")
def signin():
    global username1
    mail1 = request.args.get('t1','')
    password1 = request.args.get('t2','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("select `user`, `password` from info where `user` = ? AND `password` = ?",(mail1,password1,))
    data = cur.fetchone()
    username1 = mail1
    if data == None:
        return render_template("signin.html")
    elif mail1 == 'admin' and password1 == 'admin':
        return render_template("home.html")    
    elif mail1 == str(data[0]) and password1 == str(data[1]):
        return render_template("home.html")
    else:
        return render_template("signin.html")

@app.route("/notebook")
def notebook():
    return render_template("Notebook.html")



def sendmail(message, user):
    email_address = 'truprojects02@gmail.com'
    email_password = 'lncqoxdnuifrauve'
    sender_email = 'truprojects02@gmail.com'
    receiver_email = 'truprojects024@gmail.com'

    msg = EmailMessage()
    msg.set_content(f"CyberThreat Message sent by {user}: {message}")
    msg['Subject'] = 'CyberThreat Alert'
    msg['From'] = email_address
    msg['To'] = receiver_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        connection.login(email_address, email_password)
        connection.send_message(msg)



@app.route('/predict', methods=['POST'])
def predict():
    global username1
    if request.method == 'POST':
        message = request.form['t1']
        data = [message]
        vectorizer = cv.transform(data).toarray()
        prediction = model.predict(vectorizer)
        print(prediction)
        
        if prediction == 0:
            sendmail(message,username1)
            output = 'Cyber Threat Detected.'

        else:
            output = 'Safe Message'

        return render_template('result.html', data=output)



if __name__ == "__main__":
    app.run(debug=True)
