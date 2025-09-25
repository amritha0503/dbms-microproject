from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from datetime import datetime
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
def login():
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
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

# ========== STUDENT ROUTES ==========

@app.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Get student's applications with job and company details
        cursor.execute("""
            SELECT a.application_id, c.company_name, j.job_title, j.salary_package, 
                   a.application_date, a.status
            FROM Application a
            JOIN Job j ON a.job_id = j.job_id
            JOIN Company c ON j.company_id = c.company_id
            WHERE a.student_id = %s
            ORDER BY a.application_date DESC
        """, (session['user_id'],))
        applications = cursor.fetchall()
        
        # Get available jobs
        cursor.execute("""
            SELECT j.job_id, c.company_name, j.job_title, j.salary_package, 
                   j.location, j.min_cgpa, j.application_deadline
            FROM Job j
            JOIN Company c ON j.company_id = c.company_id
            WHERE j.status = 'Open' AND j.application_deadline >= CURDATE()
            ORDER BY j.application_deadline ASC
        """)
        available_jobs = cursor.fetchall()
        
        # Get student's profile
        cursor.execute("SELECT * FROM Student WHERE student_id = %s", (session['user_id'],))
        student_profile = cursor.fetchone()
        
        return render_template('student_dashboard.html', 
                             applications=applications, 
                             available_jobs=available_jobs,
                             student_profile=student_profile)
    
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}')
        return render_template('student_dashboard.html', applications=[], available_jobs=[], student_profile=None)
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
            
            if result and result[0] >= result[1]:
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
        
        return render_template('admin_jobs.html', jobs=jobs, companies=companies)
    except Exception as e:
        flash(f'Error loading jobs: {str(e)}')
        return render_template('admin_jobs.html', jobs=[], companies=[])
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

@app.route('/admin/applications')
@login_required
@admin_required
def manage_applications():
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT a.application_id, s.name, s.email, s.cgpa, c.company_name, 
                   j.job_title, a.application_date, a.status
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

@app.route('/admin/update_application_status/<int:app_id>/<status>')
@login_required
@admin_required
def update_application_status(app_id, status):
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("UPDATE Application SET status = %s WHERE application_id = %s", 
                      (status, app_id))
        db.commit()
        flash(f'Application status updated to {status}!')
    except Exception as e:
        flash(f'Error updating status: {str(e)}')
        db.rollback()
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for('manage_applications'))

# ✅ Run Flask
if __name__ == "__main__":
    app.run(debug=True)
