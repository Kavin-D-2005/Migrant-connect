from flask import Flask, render_template, current_app, Response, flash, redirect, send_file, request, session, abort, get_flashed_messages, url_for, jsonify
import mysql
import os
import base64
import io
import math
import mysql.connector
import hashlib
from datetime import datetime
import calendar
import random
import string
from random import randint
from urllib.request import urlopen
import webbrowser
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
from PIL import Image
import urllib.request
import urllib.parse
import pandas as pd
import datetime
from datetime import datetime
from random import randint
from fpdf import FPDF
import qrcode

# Function to create a new MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        charset="utf8",
        database="migrant_connect",
        autocommit=True
    )

app = Flask(__name__)
app.secret_key = 'abcdef'

UPLOAD_FOLDER = 'static/uploads'  # Set the upload directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if not exists
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
upload_path = app.config['UPLOAD_FOLDER']

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        uname = request.form.get('username')
        pwd = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (uname, pwd))
        account = cursor.fetchone()

        cursor.close()
        conn.close()

        if account:
            session['uname'] = uname
            return redirect(url_for('admin_home'))
        else:
            flash('Incorrect username/password!', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/admin_home', methods=['POST','GET'])
def admin_home():
    act = request.args.get("act")
    pid = request.args.get("pid")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM migrant_register")
    migrants = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin_home.html',migrants=migrants)

@app.route('/update_status', methods=['POST'])
def update_status():
    migrant_id = request.form['migrant_id']
    new_status = request.form['status']

    if new_status == 'approved':
        status_value = 1
    elif new_status == 'rejected':
        status_value = 2
    else:
        status_value = 0  

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Update status in the DB
    cursor.execute("UPDATE migrant_register SET status = %s WHERE id = %s", (status_value, migrant_id))
    conn.commit()
    if status_value == 1:
        # Fetch migrant details
        cursor.execute("SELECT name, email, contact FROM migrant_register WHERE id = %s", (migrant_id,))
        migrant = cursor.fetchone()

        if migrant:
            # Prepare QR content
            qr_data = f"Migrant ID: {migrant_id}\nName: {migrant['name']}\nEmail: {migrant['email']}\nContact: {migrant['contact']}"

            # Generate QR code
            qr = qrcode.make(qr_data)

            # Ensure folder exists
            qr_folder = os.path.join(current_app.root_path, 'static', 'qr_codes')
            os.makedirs(qr_folder, exist_ok=True)

            # Save QR image
            qr_filename = f"mid_qr_{migrant_id}.png"
            qr_path = os.path.join(qr_folder, qr_filename)
            qr.save(qr_path)

            # Save filename in DB (make sure `qr_filename` column exists)
            cursor.execute("UPDATE migrant_register SET qr_filename = %s WHERE id = %s", (qr_filename, migrant_id))
            conn.commit()

    cursor.close()
    conn.close()

    flash("Status updated successfully!", "success")
    return redirect(url_for('admin_home'))

@app.route('/add_scheme', methods=['POST'])
def add_scheme():
    scheme_name = request.form['scheme_name']
    scheme_type = request.form['type']
    description = request.form['description']
    eligibility = request.form['eligibility']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO welfare_schemes (scheme_name, type, description, eligibility) VALUES (%s, %s, %s, %s)",
                   (scheme_name, scheme_type, description, eligibility))
    conn.commit()
    cursor.close()
    flash("Scheme added successfully!", "success")
    return redirect(url_for('add_manage_scheme'))

@app.route('/add_manage_scheme')
def add_manage_scheme():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM welfare_schemes")
    schemes = cursor.fetchall()
    cursor.close()
    return render_template('add_manage_scheme.html', schemes=schemes)

@app.route('/view_user', methods=['GET'])
def view_user():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all migrant details with work location (if available)
    cursor.execute("""
        SELECT 
            id, name, occupation, username, job_status, 
            work_latitude, work_longitude, 
            current_address, district, state, country
        FROM migrant_register
    """)
    all_migrants = cursor.fetchall()
    conn.close()

    return render_template('view_user.html', migrants=all_migrants)

def geocode_address(address):
    """Return (lat, lon) for a given address using Nominatim API"""
    try:
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': address, 'format': 'json'},
            headers={'User-Agent': 'YourApp/1.0'}
        )
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None, None

@app.route('/all_migrants', methods=['GET'])
def all_migrants():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id, name, occupation, username, job_status, 
            address, district, state, country, 
            address, 
            work_latitude, work_longitude
        FROM migrant_register
    """)
    raw_data = cursor.fetchall()
    conn.close()

    migrants = []
    for m in raw_data:
        full_address = f"{m['address']}, {m['district']}, {m['state']}, {m['country']}"
        lat, lon = geocode_address(full_address)

        migrants.append({
            'name': m['name'],
            'occupation': m['occupation'],
            'job_status': m['job_status'],
            'username': m['username'],
            'permanent_address': full_address,
            'permanent_lat': lat,
            'permanent_lon': lon,
            'address': m['address'],
            'work_lat': m['work_latitude'],
            'work_lon': m['work_longitude'],
        })
    print(migrants)

    return render_template('all_migrants.html', migrants=migrants)

STATE_COORDINATES = {
    'Andhra Pradesh': (15.9129, 79.7400),
    'Arunachal Pradesh': (28.2180, 94.7278),
    'Assam': (26.2006, 92.9376),
    'Bihar': (25.0961, 85.3131),
    'Chhattisgarh': (21.2787, 81.8661),
    'Goa': (15.2993, 74.1240),
    'Gujarat': (22.2587, 71.1924),
    'Haryana': (29.0588, 76.0856),
    'Himachal Pradesh': (31.1048, 77.1734),
    'Jharkhand': (23.6102, 85.2799),
    'Karnataka': (15.3173, 75.7139),
    'Kerala': (10.8505, 76.2711),
    'Madhya Pradesh': (22.9734, 78.6569),
    'Maharashtra': (19.7515, 75.7139),
    'Manipur': (24.6637, 93.9063),
    'Meghalaya': (25.4670, 91.3662),
    'Mizoram': (23.1645, 92.9376),
    'Nagaland': (26.1584, 94.5624),
    'Odisha': (20.9517, 85.0985),
    'Punjab': (31.1471, 75.3412),
    'Rajasthan': (27.0238, 74.2179),
    'Sikkim': (27.5330, 88.5122),
    'Tamil Nadu': (11.1271, 78.6569),
    'Telangana': (18.1124, 79.0193),
    'Tripura': (23.9408, 91.9882),
    'Uttar Pradesh': (26.8467, 80.9462),
    'Uttarakhand': (30.0668, 79.0193),
    'West Bengal': (22.9868, 87.8550),

    # Union Territories
    'Andaman and Nicobar Islands': (11.7401, 92.6586),
    'Chandigarh': (30.7333, 76.7794),
    'Dadra and Nagar Haveli and Daman and Diu': (20.3974, 72.8328),
    'Delhi': (28.7041, 77.1025),
    'Jammu and Kashmir': (33.7782, 76.5762),
    'Ladakh': (34.1526, 77.5771),
    'Lakshadweep': (10.5667, 72.6417),
    'Puducherry': (11.9416, 79.8083)
}


@app.route("/migrant_map")
def show_migrant_map():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name, state, work_latitude, work_longitude FROM migrant_register WHERE verification_status='verified'")
    migrants = cursor.fetchall()

    data = []
    for m in migrants:
        perm_coords = STATE_COORDINATES.get(m['state'], (22.9734, 78.6569))  # Default to MP center
        # Add small random offset to avoid overlapping markers
        perm_lat = perm_coords[0] + random.uniform(-0.1, 0.1)
        perm_lng = perm_coords[1] + random.uniform(-0.1, 0.1)

        data.append({
            'name': m['name'],
            'state': m['state'],
            'work_latitude': float(m['work_latitude']) if m['work_latitude'] else None,
            'work_longitude': float(m['work_longitude']) if m['work_longitude'] else None,
            'perm_lat': perm_lat,
            'perm_lng': perm_lng
        })

    cursor.close()
    conn.close()

    return render_template("migrant_map.html", migrant_data=data)

def generate_unique_migrant_id():
    while True:
        # Generate ID in PAN format: AAAAA9999A
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        letters_part = ''.join(random.choices(string.ascii_uppercase, k=5))
        digits_part = ''.join(random.choices(string.digits, k=4))
        last_letter = random.choice(string.ascii_uppercase)
        pan_like_id = f"{letters_part}{digits_part}{last_letter}"

        # Check uniqueness in DB
        cursor.execute("SELECT * FROM migrant_register WHERE migrant_id = %s", (pan_like_id,))
        existing = cursor.fetchone()
        if not existing:
            return pan_like_id

@app.route("/register_valitation", methods=['GET', 'POST'])
def register_valitation():
    msg = ''
    aadhar = ''
    contact = ''
    otp = ''
    mess = ''
    if request.method == 'POST':
        aadhar = request.form['aadhar'].strip()
        contact = request.form['phone'].strip()

        # Generate OTP
        otp = str(random.randint(1000, 9999))
        mess = f"Dear user, your OTP is: {otp}"

        # Store in session
        session['aadhar'] = aadhar
        session['contact'] = contact
        session['otp'] = otp

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if already registered
            cursor.execute("SELECT * FROM migrant_register WHERE aadhar=%s AND contact=%s", (aadhar, contact))
            existing = cursor.fetchone()

            if existing:
                # Update OTP if user already exists
                cursor.execute("UPDATE migrant_register SET otp=%s WHERE aadhar=%s AND contact=%s", (otp, aadhar, contact))
                flash("Your Aadhar number is already registered. You can update your profile.", 'warning')
            else:
                # Insert new record with generated migrant_id
                migrant_id = generate_unique_migrant_id()
                cursor.execute("""
                    INSERT INTO migrant_register (migrant_id, aadhar, contact, otp, verified)
                    VALUES (%s, %s, %s, %s, %s)
                """, (migrant_id, aadhar, contact, otp, 0))

            conn.commit()
            flash(f"OTP sent to registered mobile number: {contact}", 'success')
            msg = 'ok'

        except Exception as e:
            flash("Database error: " + str(e), 'danger')
        finally:
            conn.close()

    return render_template('register_valitation.html', name='Migrant User', uid=aadhar, msg=msg, mess=mess, phone=contact)

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "GET":
        uid = request.args.get("uid")
        return render_template("verify_otp.html", uid=uid)

    if request.method == "POST":
        user_otp = request.form['otp'].strip()
        actual_otp = session.get('otp')
        aadhar = session.get('aadhar')
        contact = session.get('contact')

        if user_otp == actual_otp:
            flash("OTP verified successfully!", "success")
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE migrant_register SET verified=1 WHERE aadhar=%s AND contact=%s", (aadhar, contact))
                conn.commit()
            except Exception as e:
                flash("Verification DB update failed: " + str(e), "danger")
            finally:
                conn.close()

            # Clean session
            session.pop('otp', None)
            
            return redirect("/migrant_register")
        else:
            flash("Invalid OTP. Please try again.", "danger")
            return redirect("/register_valitation")


@app.route("/migrant_register", methods=["GET", "POST"])
def migrant_register():
    if 'aadhar' not in session:
        return redirect(url_for('register_valitation'))
    aadhar = session['aadhar']
    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()

        data = request.form
        files = request.files

        # Form data
        name = data['name']
        email = data['email']
        contact = data['contact']
        dob = data['dob']
        gender = data['gender']
        nationality = data['nationality']
        district = data['district']
        state = data['state']
        country = data['country']
        occupation = data['occupation']
        language = data['language']
        username = data['username']
        password = data['password']
        address = data['address']
        current_address = data['current_address']
        pin = data['pin']

        # File saving helper
        def save_file(file_obj, prefix):
            if file_obj and file_obj.filename:
                filename = secure_filename(file_obj.filename)
                final_filename = f"{prefix}_{username}_{filename}"
                file_path = os.path.join(upload_path, final_filename)
                file_obj.save(file_path)
                return final_filename
            return ""

        # Save uploaded files
        photo_filename = save_file(files.get('photo'), 'photo')
        aadhar_filename = save_file(files.get('aadhar_proof'), 'aadhar')
        pan_filename = save_file(files.get('pan_proof'), 'pan')
        ration_filename = save_file(files.get('ration_proof'), 'ration')

        # Update or Insert Query
        update_query = """
            UPDATE migrant_register 
            SET name = %s, email = %s, contact = %s, dob = %s, gender = %s, nationality = %s, 
                district = %s, state = %s, country = %s, occupation = %s, language = %s, 
                username = %s, password = %s, address = %s, current_address = %s, pin = %s,
                photo = %s, aadhar_proof = %s, pan_proof = %s, ration_proof = %s
            WHERE aadhar = %s
        """
        values = (
            name, email, contact, dob, gender, nationality,
            district, state, country, occupation, language,
            username, password, address, current_address, pin,
            photo_filename, aadhar_filename, pan_filename, ration_filename,
            aadhar
        )

        cursor.execute(update_query, values)
        conn.commit()
        cursor.close()
        conn.close()

        flash("Registration successful!, Wait for Admin Approval", "success")
        return redirect("/migrant_login")

    return render_template("migrant_register.html")


@app.route('/migrant_login', methods=['GET', 'POST'])
def migrant_login():
    msg = ""
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(buffered=True) 

        try:
            cursor.execute("SELECT * FROM migrant_register WHERE username = %s AND password = %s AND status=1", (username, pwd))
            account = cursor.fetchone()

            if account:
                session['id'] = account[1]
                session['username'] = account[15]
                return redirect(url_for('migrant_home'))
            else:
                flash('Incorrect username or password! or Not Approved', 'danger')
                return redirect(url_for('migrant_login'))

        except mysql.connector.Error as e:
            flash(f'Database error: {e}', 'danger')
            return redirect(url_for('migrant_login'))

        finally:
            cursor.close()
            conn.close()

    return render_template('migrant_login.html', msg=msg)

@app.route('/migrant_home', methods=['GET', 'POST'])
def migrant_home():
    msg = ""
    if 'username' not in session:
        return redirect(url_for('migrant_login'))

    username = session['username']
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM migrant_register WHERE username=%s",(username,))
    organizer = cur.fetchone()
    return render_template('migrant_home.html', msg=msg,migrant=organizer)

@app.route('/view_schemes',methods=['POST','GET'])
def view_schemes():
    migrant=''
    if 'username' not in session:
        flash("Please login to apply.", "danger")
        return redirect(url_for('migrant_login'))
    migrant_id = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM  welfare_schemes")
    schemes = cursor.fetchall()
    
    cursor.execute("SELECT scheme_id FROM scheme_applications WHERE migrant_id = %s", (migrant_id,))
    applied_scheme_ids = [row["scheme_id"] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('view_schemes.html',schemes=schemes,applied_scheme_ids=applied_scheme_ids)

@app.route('/apply_scheme', methods=['POST'])
def apply_scheme():
    if 'username' not in session:
        flash("Please login to apply.", "danger")
        return redirect(url_for('migrant_login'))

    scheme_id = request.form.get('scheme_id')
    migrant_id = session['username']  # or session['migrant_id'] if available

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if already applied
    cursor.execute("SELECT * FROM scheme_applications WHERE migrant_id=%s AND scheme_id=%s", (migrant_id, scheme_id))
    if cursor.fetchone():
        flash("You have already applied for this scheme.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for('view_schemes'))

    # Insert application
    cursor.execute(
        "INSERT INTO scheme_applications (migrant_id, scheme_id, applied_at, status) VALUES (%s, %s, %s, %s)",
        (migrant_id, scheme_id, datetime.now(), 'Pending')
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Application submitted successfully!", "success")
    return redirect(url_for('view_schemes'))

@app.route('/view_verification', methods=['GET', 'POST'])
def view_verification():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Assuming session contains logged-in migrant's username
    migrant_username = session.get('username')

    if not migrant_username:
        flash("Please log in to view your status.", "warning")
        return redirect('/login')

    # Get verification and scheme status
    cursor.execute("""
        SELECT 
            m.name, 
            m.email,
            m.verification_status,
            m.job_status,
            sa.status AS scheme_status,
            s.scheme_name
        FROM migrant_register m
        LEFT JOIN scheme_applications sa ON m.username = sa.migrant_id
        LEFT JOIN welfare_schemes s ON sa.scheme_id = s.id
        WHERE m.username = %s
    """, (migrant_username,))
    
    migrant_info = cursor.fetchall()
    print(migrant_info)
    conn.close()
    return render_template('view_verification.html', migrants=migrant_info)

@app.route('/work_history', methods=['GET', 'POST'])
def work_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    migrant_username = session.get('username')
    if not migrant_username:
        flash("Please log in to view your work history.", "warning")
        return redirect('/login')

    # Fetch migrant job details
    cursor.execute("""
        SELECT 
            name,
            occupation,
            job_status,
            work_latitude,
            work_longitude,
            current_address,
            district,
            state,
            country
        FROM migrant_register
        WHERE username = %s
    """, (migrant_username,))
    
    job_data = cursor.fetchone()
    conn.close()

    return render_template('work_history.html', job=job_data)

@app.route('/employer_register', methods=['GET', 'POST'])
def employer_register():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        company_name = request.form['company_name']
        employer_name = request.form['employer_name']
        email = request.form['email']
        contact = request.form['contact']
        username = request.form['username']
        password = request.form['password']
        designation = request.form['designation']
        address = request.form['address']
        location = request.form['location']

        # Handle uploaded photo
        photo_file = request.files['photo']
        photo_filename = ""

        if photo_file and photo_file.filename != '':
            if '.' in photo_file.filename and photo_file.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
                photo_filename = secure_filename(username + "_" + photo_file.filename)
                photo_path = os.path.join(upload_path, photo_filename)
                photo_file.save(photo_path)
            else:
                flash("Only image files are allowed for the profile photo.", "danger")
                return redirect('/employer_register')
        else:
            flash("Profile photo is required.", "danger")
            return redirect('/employer_register')

        # Check if username or email exists
        cursor.execute("SELECT * FROM employer_register WHERE username=%s OR email=%s", (username, email))
        if cursor.fetchone():
            flash("Username or Email already exists!", "danger")
            return redirect('/employer_register')

        # Insert into database
        cursor.execute("""
            INSERT INTO employer_register 
            (company_name, employer_name, email, contact, username, password, photo, designation, address, location)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (company_name, employer_name, email, contact, username, password, photo_filename, designation, address, location))
        conn.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect('/employer_login')

    return render_template('employer_register.html')


@app.route('/employer_login', methods=['GET', 'POST'])
def employer_login():
    if request.method == 'POST':
        username = request.form.get('username')
        pwd = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM employer_register WHERE username = %s AND password = %s', (username, pwd))
        account = cursor.fetchone()

        cursor.close()
        conn.close()

        if account:
            session['username'] = username
            return redirect(url_for('employer_home'))
        else:
            flash('Incorrect username/password!', 'danger')
            return redirect(url_for('employer_login'))

    return render_template('employer_login.html')

@app.route('/employer_home',methods=['POST','GET'])
def employer_home():
    attendee=''
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if 'username' not in session:
        return render_template('user_login')

    username = session['username']
    cursor.execute("SELECT * FROM employer_register WHERE username=%s",(username,))
    attendee = cursor.fetchone()
    
    return render_template('employer_home.html',employer=attendee)

@app.route('/employee_migrant_verify', methods=['GET', 'POST'])
def employee_migrant_verify():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        migrant_id = request.form['migrant_id']
        action = request.form['action']  # 'verified' or 'rejected'

        cursor.execute("UPDATE migrant_register SET verification_status=%s WHERE id=%s", (action, migrant_id))

        if action == 'verified':
            cursor.execute("UPDATE scheme_applications SET status='Approved' WHERE migrant_id=%s", (migrant_id,))
        elif action == 'rejected':
            cursor.execute("UPDATE scheme_applications SET status='Rejected' WHERE migrant_id=%s", (migrant_id,))

        conn.commit()
        flash(f"Migrant has been {action.capitalize()} and scheme status updated.", "success")
        return redirect('/employee_migrant_verify')

    # Show only migrants who have applied for a scheme
    cursor.execute("""
        SELECT DISTINCT m.*, sch.scheme_name 
        FROM migrant_register m 
        JOIN scheme_applications s ON m.username = s.migrant_id
        JOIN welfare_schemes sch ON s.scheme_id = sch.id
        WHERE m.status = 1
    """)
    migrants = cursor.fetchall()
    print(migrants)

    conn.close()
    return render_template('employee_migrant_verify.html', migrants=migrants)

@app.route('/update_status1', methods=['GET', 'POST'])
def update_status1():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        migrant_id = request.form['migrant_id']
        action = request.form['action']

        # Optional coordinates for 'hired'
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        if action == 'hired' and latitude and longitude:
            cursor.execute("""
                UPDATE migrant_register 
                SET job_status=%s, work_latitude=%s, work_longitude=%s 
                WHERE id=%s
            """, (action, latitude, longitude, migrant_id))
        else:
            cursor.execute("UPDATE migrant_register SET job_status=%s WHERE id=%s", (action, migrant_id))

        conn.commit()
        flash(f"Migrant job status updated to {action.replace('_', ' ').title()}.", "success")
        return redirect('/update_status1')

    cursor.execute("SELECT * FROM migrant_register WHERE verification_status='verified'")
    migrants = cursor.fetchall()
    conn.close()
    return render_template('update_status1.html', migrants=migrants)


@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('index'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)


