from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from datetime import datetime, date
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Database connection configuration
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        # your MySQL username
        password="amritha@2005",  # your MySQL password
        database="placement_db"    # the DB you created
    )

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            flash('Admin access required.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'student':
            flash('Student access required.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ========== AUTHENTICATION ROUTES ==========

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/<user_type>', methods=['GET', 'POST'])
def login(user_type=None):
    if request.method == 'POST':
        user_type = request.form['user_type']
        email_or_username = request.form['email_or_username']
        password = request.form['password']
        
        db = get_db_connection()
        cursor = db.cursor()
        
        try:
            if user_type == 'student':
                cursor.execute("SELECT student_id, name, email FROM Student WHERE email = %s AND password = %s", 
                             (email_or_username, password))
                user = cursor.fetchone()
                if user:
                    session['user_id'] = user[0]
                    session['user_name'] = user[1]
                    session['user_type'] = 'student'
                    flash(f'Welcome, {user[1]}!')
                    return redirect(url_for('student_dashboard'))
            elif user_type == 'admin':
                cursor.execute("SELECT admin_id, full_name, username FROM Admin WHERE username = %s AND password = %s", 
                             (email_or_username, password))
                user = cursor.fetchone()
                if user:
                    session['user_id'] = user[0]
                    session['user_name'] = user[1]
                    session['user_type'] = 'admin'
                    flash(f'Welcome, {user[1]}!')
                    return redirect(url_for('admin_dashboard'))
            
            flash('Invalid credentials. Please try again.')
            
        except Exception as e:
            flash(f'Error during login: {str(e)}')
        finally:
            cursor.close()
            db.close()
    
    return render_template('login.html', selected_user_type=user_type)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        action = request.form['action']
        
        if action == 'login':
            email = request.form['email']
            password = request.form['password']
            
            db = get_db_connection()
            cursor = db.cursor()
            
            try:
                cursor.execute("SELECT student_id, name, email FROM Student WHERE email = %s AND password = %s", 
                             (email, password))
                user = cursor.fetchone()
                if user:
                    session['user_id'] = user[0]
                    session['user_name'] = user[1]
                    session['user_type'] = 'student'
                    flash(f'Welcome, {user[1]}!')
                    return redirect(url_for('student_dashboard'))
                else:
                    flash('Invalid email or password. Please try again.')
                    
            except Exception as e:
                flash(f'Error during login: {str(e)}')
            finally:
                cursor.close()
                db.close()
                
        elif action == 'register':
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            department = request.form['department']
            cgpa = request.form['cgpa']
            graduation_year = request.form['graduation_year']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            if password != confirm_password:
                flash('Passwords do not match!')
                return render_template('student_login.html')
            
            db = get_db_connection()
            cursor = db.cursor()
            
            try:
                # Check if email already exists
                cursor.execute("SELECT email FROM Student WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email already registered. Please use a different email.')
                    return render_template('student_login.html')
                
                # Insert new student
                cursor.execute("""
                    INSERT INTO Student (name, email, phone, department, cgpa, graduation_year, password) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, email, phone, department, cgpa, graduation_year, password))
                db.commit()
                
                flash('Registration successful! You can now login.')
                return render_template('student_login.html')
                
            except Exception as e:
                flash(f'Error during registration: {str(e)}')
                db.rollback()
            finally:
                cursor.close()
                db.close()
    
    return render_template('student_login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        action = request.form['action']
        
        if action == 'login':
            username = request.form['username']
            password = request.form['password']
            
            db = get_db_connection()
            cursor = db.cursor()
            
            try:
                cursor.execute("SELECT admin_id, full_name, username FROM Admin WHERE username = %s AND password = %s", 
                             (username, password))
                user = cursor.fetchone()
                if user:
                    session['user_id'] = user[0]
                    session['user_name'] = user[1]
                    session['user_type'] = 'admin'
                    flash(f'Welcome, {user[1]}!')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid username or password. Please try again.')
                    
            except Exception as e:
                flash(f'Error during login: {str(e)}')
            finally:
                cursor.close()
                db.close()
                
        elif action == 'register':
            full_name = request.form['full_name']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            if password != confirm_password:
                flash('Passwords do not match!')
                return render_template('admin_login.html')
            
            db = get_db_connection()
            cursor = db.cursor()
            
            try:
                # Check if username already exists
                cursor.execute("SELECT username FROM Admin WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash('Username already taken. Please choose a different username.')
                    return render_template('admin_login.html')
                
                # Check if email already exists
                cursor.execute("SELECT email FROM Admin WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email already registered. Please use a different email.')
                    return render_template('admin_login.html')
                
                # Insert new admin
                cursor.execute("""
                    INSERT INTO Admin (full_name, username, email, password) 
                    VALUES (%s, %s, %s, %s)
                """, (full_name, username, email, password))
                db.commit()
                
                flash('Registration successful! You can now login.')
                return render_template('admin_login.html')
                
            except Exception as e:
                flash(f'Error during registration: {str(e)}')
                db.rollback()
            finally:
                cursor.close()
                db.close()
    
    return render_template('admin_login.html')

# ========== STUDENT ROUTES ==========

@app.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Get student's applications with job and company details and current round status
        cursor.execute("""
            SELECT a.application_id, c.company_name, j.job_title, j.salary_package, 
                   a.application_date, a.status,
                   COALESCE(
                       (SELECT CASE 
                           WHEN ir.status = 'Passed' AND ir.round_name = 'Round 1' THEN 'Round 1 - Passed'
                           WHEN ir.status = 'Failed' AND ir.round_name = 'Round 1' THEN 'Round 1 - Failed'
                           WHEN ir.status = 'Passed' AND ir.round_name = 'Round 2' THEN 'Round 2 - Passed'
                           WHEN ir.status = 'Failed' AND ir.round_name = 'Round 2' THEN 'Round 2 - Failed'
                           WHEN ir.status = 'Passed' AND ir.round_name = 'Technical Interview' THEN 'Technical Interview - Passed'
                           WHEN ir.status = 'Failed' AND ir.round_name = 'Technical Interview' THEN 'Technical Interview - Failed'
                           WHEN ir.status = 'Passed' AND ir.round_name = 'HR Interview' THEN 'HR Interview - Passed'
                           WHEN ir.status = 'Failed' AND ir.round_name = 'HR Interview' THEN 'HR Interview - Failed'
                           WHEN ir.status = 'Pending' AND ir.round_name = 'Round 1' THEN 'Round 1 - Pending'
                           WHEN ir.status = 'Pending' AND ir.round_name = 'Round 2' THEN 'Round 2 - Pending'
                           WHEN ir.status = 'Scheduled' AND ir.round_name = 'Technical Interview' THEN 'Technical Interview - Scheduled'
                           WHEN ir.status = 'Scheduled' AND ir.round_name = 'HR Interview' THEN 'HR Interview - Scheduled'
                           ELSE CONCAT(ir.round_name, ' - ', ir.status)
                       END
                       FROM Interview_Rounds ir 
                       WHERE ir.application_id = a.application_id 
                       ORDER BY 
                           CASE ir.round_name 
                               WHEN 'Round 1' THEN 1
                               WHEN 'Round 2' THEN 2
                               WHEN 'Technical Interview' THEN 3
                               WHEN 'HR Interview' THEN 4
                           END DESC
                       LIMIT 1),
                       CASE a.status
                           WHEN 'Applied' THEN 'Application Submitted'
                           WHEN 'Shortlisted' THEN 'Under Review'
                           WHEN 'Rejected' THEN 'Application Rejected'
                           ELSE a.status
                       END
                   ) as current_round_status
            FROM Application a
            JOIN Job j ON a.job_id = j.job_id
            JOIN Company c ON j.company_id = c.company_id
            WHERE a.student_id = %s
            ORDER BY a.application_date DESC
        """, (session['user_id'],))
        applications = cursor.fetchall()
        
        # Get available jobs - convert min_cgpa to float to avoid comparison issues
        cursor.execute("""
            SELECT j.job_id, c.company_name, j.job_title, j.salary_package, 
                   j.location, CAST(j.min_cgpa AS DECIMAL(3,2)), j.application_deadline
            FROM Job j
            JOIN Company c ON j.company_id = c.company_id
            WHERE j.status = 'Open' AND j.application_deadline >= CURDATE()
            ORDER BY j.application_deadline ASC
        """)
        available_jobs = cursor.fetchall()
        
        # Get student's profile - convert CGPA to ensure consistent type
        cursor.execute("""
            SELECT student_id, name, email, password, department, 
                   CAST(cgpa AS DECIMAL(3,2)), graduation_year, phone, address, 
                   resume_path, status, created_at 
            FROM Student 
            WHERE student_id = %s
        """, (session['user_id'],))
        student_profile = cursor.fetchone()
        
        # Add today's date for deadline comparison
        today = date.today()
        
        return render_template('student_dashboard.html', 
                             applications=applications, 
                             available_jobs=available_jobs,
                             student_profile=student_profile,
                             today=today)
    
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}')
        return render_template('student_dashboard.html', applications=[], available_jobs=[], student_profile=None, today=date.today())
    finally:
        cursor.close()
        db.close()

@app.route('/student/profile')
@login_required
@student_required
def student_profile():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("SELECT * FROM Student WHERE student_id = %s", (session['user_id'],))
        student = cursor.fetchone()
        return render_template('student_profile.html', student=student)
    except Exception as e:
        flash(f'Error loading profile: {str(e)}')
        return redirect(url_for('student_dashboard'))
    finally:
        cursor.close()
        db.close()

@app.route('/student/update_profile', methods=['POST'])
@login_required
@student_required
def update_student_profile():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            UPDATE Student SET phone = %s, address = %s 
            WHERE student_id = %s
        """, (request.form['phone'], request.form['address'], session['user_id']))
        db.commit()
        flash('Profile updated successfully!')
    except Exception as e:
        flash(f'Error updating profile: {str(e)}')
        db.rollback()
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for('student_profile'))

@app.route('/student/apply/<int:job_id>')
@login_required
@student_required
def apply_for_job(job_id):
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Check if already applied
        cursor.execute("SELECT * FROM Application WHERE student_id = %s AND job_id = %s", 
                      (session['user_id'], job_id))
        existing_application = cursor.fetchone()
        
        if existing_application:
            flash('You have already applied for this job!')
        else:
            # Check CGPA eligibility
            cursor.execute("""
                SELECT s.cgpa, j.min_cgpa, j.job_title, c.company_name
                FROM Student s, Job j, Company c
                WHERE s.student_id = %s AND j.job_id = %s AND j.company_id = c.company_id
            """, (session['user_id'], job_id))
            result = cursor.fetchone()
            
            if result and float(result[0]) >= float(result[1]):
                cursor.execute("""
                    INSERT INTO Application (student_id, job_id, status) 
                    VALUES (%s, %s, 'Applied')
                """, (session['user_id'], job_id))
                db.commit()
                flash(f'Successfully applied for {result[2]} at {result[3]}!')
            else:
                flash('You do not meet the minimum CGPA requirement for this job.')
                
    except Exception as e:
        flash(f'Error applying for job: {str(e)}')
        db.rollback()
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for('student_dashboard'))

@app.route('/student/job/<int:job_id>')
@login_required
@student_required
def job_details(job_id):
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Get detailed job information
        cursor.execute("""
            SELECT j.job_id, c.company_name, j.job_title, j.job_description, j.location, 
                   j.salary_package, j.eligibility_criteria, j.min_cgpa, j.required_skills, 
                   j.job_type, j.application_deadline, j.status
            FROM Job j
            JOIN Company c ON j.company_id = c.company_id
            WHERE j.job_id = %s
        """, (job_id,))
        job = cursor.fetchone()
        
        if not job:
            flash('Job not found.')
            return redirect(url_for('student_dashboard'))
        
        # Get company details
        cursor.execute("""
            SELECT c.company_id, c.company_name, c.location, c.contact_email, c.website, c.contact_phone, c.description
            FROM Company c
            JOIN Job j ON c.company_id = j.company_id
            WHERE j.job_id = %s
        """, (job_id,))
        company = cursor.fetchone()
        
        # Get student's applications
        cursor.execute("""
            SELECT a.application_id, c.company_name, j.job_title, j.salary_package, 
                   a.application_date, a.status
            FROM Application a
            JOIN Job j ON a.job_id = j.job_id
            JOIN Company c ON j.company_id = c.company_id
            WHERE a.student_id = %s
        """, (session['user_id'],))
        applications = cursor.fetchall()
        
        # Get student's profile
        cursor.execute("""
            SELECT student_id, name, email, password, department, 
                   CAST(cgpa AS DECIMAL(3,2)), graduation_year, phone, address, 
                   resume_path, status, created_at 
            FROM Student 
            WHERE student_id = %s
        """, (session['user_id'],))
        student_profile = cursor.fetchone()
        
        return render_template('job_details.html', 
                             job=job, 
                             company=company,
                             applications=applications, 
                             student_profile=student_profile)
    
    except Exception as e:
        flash(f'Error loading job details: {str(e)}')
        return redirect(url_for('student_dashboard'))
    finally:
        cursor.close()
        db.close()

@app.route('/student/apply_detailed/<int:job_id>', methods=['POST'])
@login_required
@student_required
def apply_for_job_detailed(job_id):
    import os
    from werkzeug.utils import secure_filename
    
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Check if already applied
        cursor.execute("SELECT * FROM Application WHERE student_id = %s AND job_id = %s", 
                      (session['user_id'], job_id))
        existing_application = cursor.fetchone()
        
        if existing_application:
            flash('You have already applied for this job!')
            return redirect(url_for('job_details', job_id=job_id))
        
        # Handle file upload
        resume_path = None
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename:
                try:
                    # Create uploads directory if it doesn't exist
                    upload_folder = os.path.join('static', 'uploads', 'resumes')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    # Clean the filename to avoid special characters
                    original_filename = secure_filename(file.filename)
                    if not original_filename:
                        flash('Invalid filename. Please rename your file and try again.')
                        return redirect(url_for('job_details', job_id=job_id))
                    
                    # Generate secure filename with timestamp to avoid conflicts
                    import time
                    timestamp = int(time.time())
                    file_ext = os.path.splitext(original_filename)[1]
                    filename = f"{session['user_id']}_{job_id}_{timestamp}{file_ext}"
                    filepath = os.path.join(upload_folder, filename)
                    
                    # Check file size (5MB limit)
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > 5 * 1024 * 1024:  # 5MB
                        flash('File size too large. Please upload a file smaller than 5MB.')
                        return redirect(url_for('job_details', job_id=job_id))
                    
                    # Save file
                    file.save(filepath)
                    
                    # Verify file was saved successfully
                    if os.path.exists(filepath):
                        resume_path = filepath
                        print(f"File saved successfully: {filepath}")  # Debug log
                    else:
                        flash('Failed to save resume file. Please try again.')
                        return redirect(url_for('job_details', job_id=job_id))
                        
                except Exception as e:
                    flash(f'Error uploading resume: {str(e)}')
                    print(f"File upload error: {str(e)}")  # Debug log
                    return redirect(url_for('job_details', job_id=job_id))
        
        if not resume_path:
            flash('Resume upload is required to apply for this job.')
            return redirect(url_for('job_details', job_id=job_id))
        
        # Check CGPA eligibility
        cursor.execute("""
            SELECT s.cgpa, j.min_cgpa, j.job_title, c.company_name
            FROM Student s, Job j, Company c
            WHERE s.student_id = %s AND j.job_id = %s AND j.company_id = c.company_id
        """, (session['user_id'], job_id))
        result = cursor.fetchone()
        
        if result and float(result[0]) >= float(result[1]):
            # Get cover letter
            cover_letter = request.form.get('cover_letter', '')
            
            # Insert application with resume path and cover letter
            cursor.execute("""
                INSERT INTO Application (student_id, job_id, status, admin_comments, resume_path, cover_letter) 
                VALUES (%s, %s, 'Applied', %s, %s, %s)
            """, (session['user_id'], job_id, f'Resume: {resume_path}', resume_path, cover_letter))
            
            # Update student's resume path in profile
            cursor.execute("""
                UPDATE Student SET resume_path = %s WHERE student_id = %s
            """, (resume_path, session['user_id']))
            
            db.commit()
            flash(f'Successfully applied for {result[2]} at {result[3]}! Your resume has been uploaded.')
        else:
            flash('You do not meet the minimum CGPA requirement for this job.')
            
    except Exception as e:
        flash(f'Error applying for job: {str(e)}')
        db.rollback()
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for('job_details', job_id=job_id))

@app.route('/student/interviews')
@login_required
@student_required
def student_interviews():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT i.interview_id, c.company_name, j.job_title, i.interview_date, 
                   i.interview_type, i.location, i.result, i.feedback
            FROM Interview i
            JOIN Application a ON i.application_id = a.application_id
            JOIN Job j ON a.job_id = j.job_id
            JOIN Company c ON j.company_id = c.company_id
            WHERE a.student_id = %s
            ORDER BY i.interview_date DESC
        """, (session['user_id'],))
        interviews = cursor.fetchall()
        
        return render_template('student_interviews.html', interviews=interviews)
    except Exception as e:
        flash(f'Error loading interviews: {str(e)}')
        return redirect(url_for('student_dashboard'))
    finally:
        cursor.close()
        db.close()

@app.route('/student/notifications')
@login_required
@student_required
def student_notifications():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Get all notifications for the student
        cursor.execute("""
            SELECT notification_id, message, notification_type, is_read, created_at
            FROM Student_Notifications 
            WHERE student_id = %s 
            ORDER BY created_at DESC
        """, (session['user_id'],))
        notifications = cursor.fetchall()
        
        # Mark all notifications as read
        cursor.execute("""
            UPDATE Student_Notifications 
            SET is_read = TRUE 
            WHERE student_id = %s AND is_read = FALSE
        """, (session['user_id'],))
        db.commit()
        
        return render_template('student_notifications.html', notifications=notifications)
    except Exception as e:
        flash(f'Error loading notifications: {str(e)}')
        return redirect(url_for('student_dashboard'))
    finally:
        cursor.close()
        db.close()

# ========== ADMIN ROUTES ==========

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM Student")
        total_students = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Company")
        total_companies = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Job WHERE status = 'Open'")
        active_jobs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Application")
        total_applications = cursor.fetchone()[0]
        
        # Get recent applications
        cursor.execute("""
            SELECT a.application_id, s.name, c.company_name, j.job_title, 
                   a.application_date, a.status
            FROM Application a
            JOIN Student s ON a.student_id = s.student_id
            JOIN Job j ON a.job_id = j.job_id
            JOIN Company c ON j.company_id = c.company_id
            ORDER BY a.application_date DESC
            LIMIT 10
        """)
        recent_applications = cursor.fetchall()
        
        return render_template('admin_dashboard.html',
                             total_students=total_students,
                             total_companies=total_companies,
                             active_jobs=active_jobs,
                             total_applications=total_applications,
                             recent_applications=recent_applications)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}')
        return render_template('admin_dashboard.html')
    finally:
        cursor.close()
        db.close()

@app.route('/admin/students')
@login_required
@admin_required
def manage_students():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("SELECT * FROM Student ORDER BY name")
        students = cursor.fetchall()
        return render_template('admin_students.html', students=students)
    except Exception as e:
        flash(f'Error loading students: {str(e)}')
        return render_template('admin_students.html', students=[])
    finally:
        cursor.close()
        db.close()

@app.route('/admin/companies')
@login_required
@admin_required
def manage_companies():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("SELECT * FROM Company ORDER BY company_name")
        companies = cursor.fetchall()
        return render_template('admin_companies.html', companies=companies)
    except Exception as e:
        flash(f'Error loading companies: {str(e)}')
        return render_template('admin_companies.html', companies=[])
    finally:
        cursor.close()
        db.close()

@app.route('/admin/add_company', methods=['POST'])
@login_required
@admin_required
def add_company():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO Company (company_name, location, contact_email, contact_phone, website, description) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (request.form['company_name'], request.form['location'], 
              request.form['contact_email'], request.form['contact_phone'], 
              request.form['website'], request.form['description']))
        db.commit()
        flash('Company added successfully!')
    except Exception as e:
        flash(f'Error adding company: {str(e)}')
        db.rollback()
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for('manage_companies'))

@app.route('/admin/company/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_company_form():
    if request.method == 'GET':
        return render_template('admin_add_company.html')
    
    elif request.method == 'POST':
        # Handle form submission (same as existing add_company logic)
        db = get_db_connection()
        cursor = db.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Company (company_name, location, contact_email, contact_phone, website, description)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (request.form['company_name'], request.form['location'], 
                  request.form.get('contact_email', ''), request.form.get('contact_phone', ''),
                  request.form.get('website', ''), request.form.get('description', '')))
            db.commit()
            flash('Company added successfully!')
        except Exception as e:
            flash(f'Error adding company: {str(e)}')
            db.rollback()
        finally:
            cursor.close()
            db.close()
        
        return redirect(url_for('manage_companies'))

@app.route('/admin/student/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student_form():
    if request.method == 'GET':
        return render_template('admin_add_student.html')
    
    elif request.method == 'POST':
        # Handle form submission
        db = get_db_connection()
        cursor = db.cursor()
        
        try:
            # Hash the password
            password_hash = hashlib.sha256(request.form['password'].encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO Student (name, email, password, department, cgpa, graduation_year, phone, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (request.form['name'], request.form['email'], password_hash,
                  request.form['department'], request.form['cgpa'], 
                  request.form['graduation_year'], request.form.get('phone', ''),
                  request.form.get('status', 'Active')))
            db.commit()
            flash('Student added successfully!')
        except Exception as e:
            flash(f'Error adding student: {str(e)}')
            db.rollback()
        finally:
            cursor.close()
            db.close()
        
        return redirect(url_for('manage_students'))

@app.route('/admin/jobs')
@login_required
@admin_required
def manage_jobs():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT j.*, c.company_name 
            FROM Job j 
            JOIN Company c ON j.company_id = c.company_id 
            ORDER BY j.created_at DESC
        """)
        jobs = cursor.fetchall()
        
        cursor.execute("SELECT company_id, company_name FROM Company ORDER BY company_name")
        companies = cursor.fetchall()
        
        # Add today's date for deadline comparison
        today = date.today()
        
        return render_template('admin_jobs.html', jobs=jobs, companies=companies, today=today)
    except Exception as e:
        flash(f'Error loading jobs: {str(e)}')
        return render_template('admin_jobs.html', jobs=[], companies=[], today=date.today())
    finally:
        cursor.close()
        db.close()

@app.route('/admin/add_job', methods=['POST'])
@login_required
@admin_required
def add_job():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO Job (company_id, job_title, job_description, salary_package, 
                           location, min_cgpa, required_skills, job_type, application_deadline) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (request.form['company_id'], request.form['job_title'], 
              request.form['job_description'], request.form['salary_package'],
              request.form['location'], request.form['min_cgpa'], 
              request.form['required_skills'], request.form['job_type'],
              request.form['application_deadline']))
        db.commit()
        flash('Job added successfully!')
    except Exception as e:
        flash(f'Error adding job: {str(e)}')
        db.rollback()
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for('manage_jobs'))

@app.route('/admin/job/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_job_form():
    if request.method == 'GET':
        # Show the add job form
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT company_id, company_name FROM Company ORDER BY company_name")
            companies = cursor.fetchall()
            return render_template('admin_add_job.html', companies=companies)
        except Exception as e:
            flash(f'Error loading companies: {str(e)}')
            return redirect(url_for('manage_jobs'))
        finally:
            cursor.close()
            db.close()
    
    elif request.method == 'POST':
        # Handle form submission (same as existing add_job logic)
        db = get_db_connection()
        cursor = db.cursor()
        
        try:
            salary_package = request.form.get('salary_package')
            if salary_package:
                salary_package = int(salary_package)
            else:
                salary_package = None
            
            cursor.execute("""
                INSERT INTO Job (company_id, job_title, job_description, salary_package, 
                               location, min_cgpa, required_skills, job_type, application_deadline)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (request.form['company_id'], request.form['job_title'], 
                  request.form['job_description'], salary_package,
                  request.form['location'], request.form['min_cgpa'], 
                  request.form.get('required_skills', ''), request.form['job_type'],
                  request.form['application_deadline']))
            db.commit()
            flash('Job added successfully!')
        except Exception as e:
            flash(f'Error adding job: {str(e)}')
            db.rollback()
        finally:
            cursor.close()
            db.close()
        
        return redirect(url_for('manage_jobs'))

@app.route('/admin/applications')
@login_required
@admin_required
def manage_applications():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT a.application_id, s.name, s.email, s.cgpa, c.company_name, 
                   j.job_title, a.application_date, a.status, a.current_round,
                   a.resume_path, a.cover_letter, s.student_id, j.job_id, a.overall_status
            FROM Application a
            JOIN Student s ON a.student_id = s.student_id
            JOIN Job j ON a.job_id = j.job_id
            JOIN Company c ON j.company_id = c.company_id
            ORDER BY a.application_date DESC
        """)
        applications = cursor.fetchall()
        
        return render_template('admin_applications.html', applications=applications)
    except Exception as e:
        flash(f'Error loading applications: {str(e)}')
        return render_template('admin_applications.html', applications=[])
    finally:
        cursor.close()
        db.close()

@app.route('/admin/schedule_interview/<int:app_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def schedule_interview(app_id):
    db = get_db_connection()
    cursor = db.cursor()
    
    # Get the round type from query parameter (only Technical or HR)
    round_name = request.args.get('round', 'Technical')
    if round_name not in ['Technical', 'HR']:
        round_name = 'Technical Interview' if round_name == 'Technical' else 'HR Interview'
    else:
        round_name = 'Technical Interview' if round_name == 'Technical' else 'HR Interview'
    
    if request.method == 'POST':
        round_name = request.form['round_name']
        scheduled_date = request.form['scheduled_date']
        scheduled_time = request.form['scheduled_time']
        location = request.form['location']
        interview_type = request.form['interview_type']
        interviewer_name = request.form['interviewer_name']
        
        try:
            # Insert new interview round
            cursor.execute("""
                INSERT INTO Interview_Rounds 
                (application_id, round_name, scheduled_date, scheduled_time, location, 
                 interview_type, interviewer_name, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Scheduled')
            """, (app_id, round_name, scheduled_date, scheduled_time, location, 
                  interview_type, interviewer_name))
            
            # Update application current round
            cursor.execute("""
                UPDATE Application 
                SET current_round = %s 
                WHERE application_id = %s
            """, (round_name, app_id))
            
            # Send notification to student
            cursor.execute("""
                SELECT student_id FROM Application WHERE application_id = %s
            """, (app_id,))
            student_id = cursor.fetchone()[0]
            
            notification_message = f"Your {round_name} has been scheduled for {scheduled_date} at {scheduled_time}. Location: {location}. Interviewer: {interviewer_name}."
            cursor.execute("""
                INSERT INTO Student_Notifications (student_id, message, notification_type, created_at)
                VALUES (%s, %s, 'Interview Scheduled', NOW())
            """, (student_id, notification_message))
            
            db.commit()
            flash(f'Interview for {round_name} scheduled successfully!')
            return redirect(url_for('manage_applications'))
            
        except Exception as e:
            flash(f'Error scheduling interview: {str(e)}')
            db.rollback()
    
    try:
        # Get application details
        cursor.execute("""
            SELECT a.application_id, s.name, s.email, s.cgpa, c.company_name, 
                   j.job_title, a.application_date, a.status, a.current_round,
                   a.resume_path, a.cover_letter, s.student_id, j.job_id, a.overall_status
            FROM Application a
            JOIN Student s ON a.student_id = s.student_id
            JOIN Job j ON a.job_id = j.job_id
            JOIN Company c ON j.company_id = c.company_id
            WHERE a.application_id = %s
        """, (app_id,))
        application = cursor.fetchone()
        
        # Get existing interview rounds
        cursor.execute("""
            SELECT * FROM Interview_Rounds 
            WHERE application_id = %s 
            ORDER BY scheduled_date DESC, scheduled_time DESC
        """, (app_id,))
        existing_rounds = cursor.fetchall()
        
        return render_template('admin_schedule_interview.html', 
                             application=application, 
                             existing_rounds=existing_rounds,
                             round_name=round_name)
                             
    except Exception as e:
        flash(f'Error loading application: {str(e)}')
        return redirect(url_for('manage_applications'))
    finally:
        cursor.close()
        db.close()

@app.route('/admin/update_screening_round/<int:app_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_screening_round(app_id):
    db = get_db_connection()
    cursor = db.cursor()
    
    # Get the round type from query parameter
    round_name = request.args.get('round', 'Round1')
    
    if request.method == 'POST':
        round_name = request.form['round_name']
        result = request.form['result']  # Pass/Fail
        feedback = request.form['feedback']
        next_round_description = request.form.get('next_round_description', '')
        
        try:
            # Insert screening round result
            cursor.execute("""
                INSERT INTO Interview_Rounds 
                (application_id, round_name, status, feedback, interviewer_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (app_id, round_name, result, feedback, session.get('user_name', 'Admin')))
            
            # Update application status based on result
            if result == 'Pass':
                new_round = None  # Initialize the variable
                
                if round_name in ['Round 1', 'Round1']:
                    new_round = 'Round 2'
                elif round_name in ['Round 2', 'Round2']:
                    new_round = 'Technical Interview'
                
                # Only update if we have a valid next round
                if new_round:
                    cursor.execute("""
                        UPDATE Application 
                        SET current_round = %s 
                        WHERE application_id = %s
                    """, (new_round, app_id))
                
                # Create notification for student
                cursor.execute("""
                    SELECT student_id FROM Application WHERE application_id = %s
                """, (app_id,))
                student_id = cursor.fetchone()[0]
                
                notification_message = f"Congratulations! You have passed {round_name}. {next_round_description}"
                cursor.execute("""
                    INSERT INTO Student_Notifications (student_id, message, notification_type, created_at)
                    VALUES (%s, %s, 'Round Update', NOW())
                """, (student_id, notification_message))
                
            else:  # Fail
                cursor.execute("""
                    UPDATE Application 
                    SET current_round = 'Rejected', overall_status = 'Rejected'
                    WHERE application_id = %s
                """, (app_id,))
                
                # Create notification for student
                cursor.execute("""
                    SELECT student_id FROM Application WHERE application_id = %s
                """, (app_id,))
                student_id = cursor.fetchone()[0]
                
                notification_message = f"Thank you for your interest. Unfortunately, you did not pass {round_name}. {feedback}"
                cursor.execute("""
                    INSERT INTO Student_Notifications (student_id, message, notification_type, created_at)
                    VALUES (%s, %s, 'Round Update', NOW())
                """, (student_id, notification_message))
            
            db.commit()
            flash(f'{round_name} result updated successfully!')
            return redirect(url_for('manage_applications'))
            
        except Exception as e:
            flash(f'Error updating round result: {str(e)}')
            db.rollback()
    
    try:
        # Get application details
        cursor.execute("""
            SELECT a.application_id, s.name, s.email, s.cgpa, c.company_name, 
                   j.job_title, a.application_date, a.status, a.current_round,
                   a.resume_path, a.cover_letter, s.student_id, j.job_id, a.overall_status
            FROM Application a
            JOIN Student s ON a.student_id = s.student_id
            JOIN Job j ON a.job_id = j.job_id
            JOIN Company c ON j.company_id = c.company_id
            WHERE a.application_id = %s
        """, (app_id,))
        application = cursor.fetchone()
        
        return render_template('admin_screening_round.html', 
                             application=application, 
                             round_name=round_name)
                             
    except Exception as e:
        flash(f'Error loading application: {str(e)}')
        return redirect(url_for('manage_applications'))
    finally:
        cursor.close()
        db.close()

@app.route('/admin/update_interview_status/<int:round_id>/<status>')
@login_required
@admin_required
def update_interview_status(round_id, status):
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            UPDATE Interview_Rounds 
            SET status = %s 
            WHERE round_id = %s
        """, (status, round_id))
        
        db.commit()
        flash(f'Interview status updated to {status}!')
    except Exception as e:
        flash(f'Error updating interview status: {str(e)}')
        db.rollback()
    finally:
        cursor.close()
        db.close()
    
    return redirect(request.referrer or url_for('manage_applications'))

@app.route('/admin/application_details/<int:app_id>')
@login_required
@admin_required
def application_details(app_id):
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Get application details
        cursor.execute("""
            SELECT a.application_id, s.name, s.email, s.phone, s.cgpa, s.department,
                   c.company_name, j.job_title, j.job_description, j.salary_package,
                   a.current_round, a.overall_status, a.application_date, a.resume_path,
                   a.cover_letter, a.admin_comments
            FROM Application a
            JOIN Student s ON a.student_id = s.student_id
            JOIN Job j ON a.job_id = j.job_id
            JOIN Company c ON j.company_id = c.company_id
            WHERE a.application_id = %s
        """, (app_id,))
        application = cursor.fetchone()
        
        # Get all interview rounds for this application
        cursor.execute("""
            SELECT round_id, round_name, scheduled_date, scheduled_time, location,
                   interview_mode, interviewer_name, interviewer_email, round_status,
                   result, feedback, score, max_score, admin_notes, created_at
            FROM Interview_Rounds 
            WHERE application_id = %s 
            ORDER BY 
                CASE round_name 
                    WHEN 'Round 1' THEN 1
                    WHEN 'Round 2' THEN 2
                    WHEN 'Technical Interview' THEN 3
                    WHEN 'HR Interview' THEN 4
                END, created_at
        """, (app_id,))
        interview_rounds = cursor.fetchall()
        
        return render_template('application_details.html', 
                             application=application, interview_rounds=interview_rounds)
    except Exception as e:
        flash(f'Error loading application details: {str(e)}', 'error')
        return redirect(url_for('manage_applications'))
    finally:
        cursor.close()
        db.close()

@app.route('/admin/update_application_status/<int:app_id>/<status>')
@login_required
@admin_required
def update_application_status(app_id, status):
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Update both current_round and overall_status based on the status
        if status in ['Selected', 'Rejected']:
            cursor.execute("""
                UPDATE Application 
                SET current_round = %s, overall_status = %s, status = %s 
                WHERE application_id = %s
            """, (status, status, status, app_id))
        else:
            cursor.execute("""
                UPDATE Application 
                SET current_round = %s, status = %s 
                WHERE application_id = %s
            """, (status, status, app_id))
        
        db.commit()
        flash(f'Application status updated to {status}!')
    except Exception as e:
        flash(f'Error updating status: {str(e)}')
        db.rollback()
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for('manage_applications'))

@app.route('/admin/view_resume/<int:app_id>')
@login_required
@admin_required
def view_resume(app_id):
    from flask import send_file
    import os
    
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT a.resume_path, s.name, j.job_title, c.company_name
            FROM Application a
            JOIN Student s ON a.student_id = s.student_id
            JOIN Job j ON a.job_id = j.job_id
            JOIN Company c ON j.company_id = c.company_id
            WHERE a.application_id = %s
        """, (app_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            resume_path = result[0]
            
            # Handle both absolute and relative paths
            if not os.path.isabs(resume_path):
                # If it's a relative path, make it absolute
                resume_path = os.path.join(os.getcwd(), resume_path)
            
            print(f"Looking for resume at: {resume_path}")  # Debug log
            
            if os.path.exists(resume_path):
                # Get file extension from original path
                file_ext = os.path.splitext(resume_path)[1] or '.pdf'
                download_name = f"Resume_{result[1].replace(' ', '_')}_{result[2].replace(' ', '_')}{file_ext}"
                
                return send_file(resume_path, as_attachment=True, download_name=download_name)
            else:
                flash(f'Resume file not found at path: {resume_path}')
        else:
            flash('No resume available for this application.')
            
    except Exception as e:
        flash(f'Error accessing resume: {str(e)}')
        print(f"Resume access error: {str(e)}")  # Debug log
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for('manage_applications'))

# ✅ Student Management Routes
@app.route('/admin/student/update/<int:student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_student(student_id):
    db = get_db_connection()
    cursor = db.cursor()
    
    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM Student WHERE student_id = %s", (student_id,))
            student = cursor.fetchone()
            if not student:
                flash('Student not found.')
                return redirect(url_for('manage_students'))
            return render_template('admin_update_student.html', student=student)
        except Exception as e:
            flash(f'Error loading student: {str(e)}')
            return redirect(url_for('manage_students'))
        finally:
            cursor.close()
            db.close()
    
    elif request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            department = request.form['department']
            cgpa = float(request.form['cgpa'])
            graduation_year = int(request.form['graduation_year'])
            phone = request.form.get('phone', '')
            status = request.form.get('status', 'Active')
            
            cursor.execute("""
                UPDATE Student 
                SET name = %s, email = %s, department = %s, cgpa = %s, 
                    graduation_year = %s, phone = %s, status = %s
                WHERE student_id = %s
            """, (name, email, department, cgpa, graduation_year, phone, status, student_id))
            
            db.commit()
            flash('Student updated successfully!')
        except Exception as e:
            flash(f'Error updating student: {str(e)}')
            db.rollback()
        finally:
            cursor.close()
            db.close()
        
        return redirect(url_for('manage_students'))

@app.route('/admin/student/delete/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Check if student has applications
        cursor.execute("SELECT COUNT(*) FROM Application WHERE student_id = %s", (student_id,))
        application_count = cursor.fetchone()[0]
        
        if application_count > 0:
            flash(f'Cannot delete student. They have {application_count} job applications.')
        else:
            cursor.execute("DELETE FROM Student WHERE student_id = %s", (student_id,))
            db.commit()
            flash('Student deleted successfully!')
    except Exception as e:
        flash(f'Error deleting student: {str(e)}')
        db.rollback()
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for('manage_students'))

# ✅ Company Management Routes
@app.route('/admin/company/update/<int:company_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_company(company_id):
    db = get_db_connection()
    cursor = db.cursor()
    
    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM Company WHERE company_id = %s", (company_id,))
            company = cursor.fetchone()
            if not company:
                flash('Company not found.')
                return redirect(url_for('manage_companies'))
            return render_template('admin_update_company.html', company=company)
        except Exception as e:
            flash(f'Error loading company: {str(e)}')
            return redirect(url_for('manage_companies'))
        finally:
            cursor.close()
            db.close()
    
    elif request.method == 'POST':
        try:
            company_name = request.form['company_name']
            location = request.form['location']
            contact_email = request.form.get('contact_email', '')
            contact_phone = request.form.get('contact_phone', '')
            website = request.form.get('website', '')
            description = request.form.get('description', '')
            
            cursor.execute("""
                UPDATE Company 
                SET company_name = %s, location = %s, contact_email = %s, 
                    contact_phone = %s, website = %s, description = %s
                WHERE company_id = %s
            """, (company_name, location, contact_email, contact_phone, website, description, company_id))
            
            db.commit()
            flash('Company updated successfully!')
        except Exception as e:
            flash(f'Error updating company: {str(e)}')
            db.rollback()
        finally:
            cursor.close()
            db.close()
        
        return redirect(url_for('manage_companies'))

@app.route('/admin/company/delete/<int:company_id>', methods=['POST'])
@login_required
@admin_required
def delete_company(company_id):
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Check if company has jobs
        cursor.execute("SELECT COUNT(*) FROM Job WHERE company_id = %s", (company_id,))
        job_count = cursor.fetchone()[0]
        
        if job_count > 0:
            flash(f'Cannot delete company. They have {job_count} active jobs.')
        else:
            cursor.execute("DELETE FROM Company WHERE company_id = %s", (company_id,))
            db.commit()
            flash('Company deleted successfully!')
    except Exception as e:
        flash(f'Error deleting company: {str(e)}')
        db.rollback()
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for('manage_companies'))

# ✅ Job Management Routes
@app.route('/admin/job/update/<int:job_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_job(job_id):
    db = get_db_connection()
    cursor = db.cursor()
    
    if request.method == 'GET':
        try:
            cursor.execute("""
                SELECT j.*, c.company_name 
                FROM Job j 
                JOIN Company c ON j.company_id = c.company_id 
                WHERE j.job_id = %s
            """, (job_id,))
            job = cursor.fetchone()
            
            cursor.execute("SELECT company_id, company_name FROM Company ORDER BY company_name")
            companies = cursor.fetchall()
            
            if not job:
                flash('Job not found.')
                return redirect(url_for('manage_jobs'))
            return render_template('admin_update_job.html', job=job, companies=companies)
        except Exception as e:
            flash(f'Error loading job: {str(e)}')
            return redirect(url_for('manage_jobs'))
        finally:
            cursor.close()
            db.close()
    
    elif request.method == 'POST':
        try:
            company_id = int(request.form['company_id'])
            job_title = request.form['job_title']
            salary_package = request.form.get('salary_package')
            location = request.form['location']
            min_cgpa = float(request.form['min_cgpa'])
            job_type = request.form['job_type']
            requirements = request.form.get('requirements', '')
            description = request.form.get('description', '')
            
            # Convert empty salary to None
            if salary_package:
                salary_package = int(salary_package)
            else:
                salary_package = None
            
            cursor.execute("""
                UPDATE Job 
                SET company_id = %s, job_title = %s, salary_package = %s, 
                    location = %s, min_cgpa = %s, job_type = %s, 
                    requirements = %s, description = %s
                WHERE job_id = %s
            """, (company_id, job_title, salary_package, location, min_cgpa, 
                  job_type, requirements, description, job_id))
            
            db.commit()
            flash('Job updated successfully!')
        except Exception as e:
            flash(f'Error updating job: {str(e)}')
            db.rollback()
        finally:
            cursor.close()
            db.close()
        
        return redirect(url_for('manage_jobs'))

@app.route('/admin/job/delete/<int:job_id>', methods=['POST'])
@login_required
@admin_required
def delete_job(job_id):
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Check if job has applications
        cursor.execute("SELECT COUNT(*) FROM Application WHERE job_id = %s", (job_id,))
        application_count = cursor.fetchone()[0]
        
        if application_count > 0:
            flash(f'Cannot delete job. It has {application_count} applications.')
        else:
            cursor.execute("DELETE FROM Job WHERE job_id = %s", (job_id,))
            db.commit()
            flash('Job deleted successfully!')
    except Exception as e:
        flash(f'Error deleting job: {str(e)}')
        db.rollback()
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for('manage_jobs'))

@app.route('/download_resume/<filename>')
@login_required
@admin_required
def download_resume(filename):
    from flask import send_from_directory, abort
    import os
    
    # Define the directory where resumes are stored
    resume_dir = os.path.join(app.root_path, 'uploads', 'resumes')
    
    # Create directory if it doesn't exist
    os.makedirs(resume_dir, exist_ok=True)
    
    # Full path to the file
    file_path = os.path.join(resume_dir, filename)
    
    # Check if file exists
    if os.path.exists(file_path):
        try:
            return send_from_directory(resume_dir, filename, as_attachment=True)
        except Exception as e:
            flash(f'Error downloading resume: {str(e)}')
            return redirect(url_for('manage_applications'))
    else:
        # File doesn't exist - show a friendly message
        flash(f'Resume file "{filename}" not found on server.')
        return redirect(url_for('manage_applications'))

# ✅ Run Flask
if __name__ == "__main__":
    app.run(debug=True)
