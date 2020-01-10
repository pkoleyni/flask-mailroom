import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import  pbkdf2_sha256
from model import Donation, Donor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY').encode()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/donations/')
def all():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('donations.jinja2', donations=Donation.select())

@app.route('/create', methods = ['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('create.jinja2')
    elif request.method == 'POST':

        try:
            donor = Donation.select().join(Donor).where(Donor.name == request.form['name']).get()
        except:
            return render_template('create.jinja2', error = 'Donor dose not exists')
        old_donation = donor.value
        added_donation = int(request.form['donation'])
        new_donation = old_donation + added_donation
        Donation.update(value=new_donation).where(donor).execute()
        return redirect(url_for('all'))

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        donor = Donor.select().where(Donor.name == request.form['name']).get()
        if donor and pbkdf2_sha256.verify(request.form['password'], donor.password):
            session['username'] = request.form['name']
            return redirect(url_for('all'))
        return render_template('login.jinja2', error='Incorrect username or password')
    else:
        return render_template('login.jinja2')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port, debug='True')

