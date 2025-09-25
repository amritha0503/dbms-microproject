# Placement Management System

A comprehensive web-based placement management system built with **Flask**, **MySQL**, and **Bootstrap**. This system facilitates the placement process for educational institutions by providing separate interfaces for students and administrators.

## 🚀 Features

### For Students:
- **Dashboard**: View application status, available jobs, and personal statistics
- **Job Applications**: Browse and apply for jobs based on eligibility criteria
- **Profile Management**: Update personal information and view academic details
- **Interview Tracking**: Monitor scheduled interviews and results
- **Status Updates**: Real-time updates on application progress

### For Admins:
- **Dashboard**: Comprehensive overview with statistics and recent activities
- **Student Management**: View and manage student records
- **Company Management**: Add and maintain company profiles
- **Job Posting**: Create and manage job listings
- **Application Processing**: Review applications and update statuses
- **Interview Scheduling**: Schedule and manage interview rounds

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | HTML, CSS, Bootstrap | User interface and responsive design |
| **Backend** | Python Flask | Server-side logic and routing |
| **Database** | MySQL | Data storage and management |
| **Authentication** | Flask Sessions | User login and session management |

## 📋 Prerequisites

Before running this application, make sure you have:

- **Python 3.7+** installed
- **MySQL Server** installed and running
- **Git** (optional, for cloning)

## ⚡ Quick Setup

### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd placement_system
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup MySQL Database
1. **Start MySQL Server**
2. **Create Database**: Run the SQL script in `database_setup.sql`
   ```bash
   mysql -u root -p < database_setup.sql
   ```
   OR manually execute the SQL commands in your MySQL client

### 4. Configure Database Connection
Edit `app.py` and update the database connection details:
```python
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your_mysql_username",      # Update this
        password="your_mysql_password",  # Update this
        database="placement_db"
    )
```

### 5. Run the Application
```bash
python app.py
```

The application will start at: **http://127.0.0.1:5000**

## 🔐 Default Login Credentials

### Student Access:
- **Email**: alice@student.com
- **Password**: alice123

### Admin Access:
- **Username**: admin
- **Password**: admin123

## 📁 Project Structure

```
placement_system/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database_setup.sql     # Database schema and sample data
├── README.md             # Project documentation
│
├── static/
│   └── style.css         # Custom CSS styling
│
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Home page
    ├── login.html        # Login page
    │
    ├── student_dashboard.html      # Student dashboard
    ├── student_profile.html        # Student profile
    ├── student_interviews.html     # Student interviews
    │
    ├── admin_dashboard.html        # Admin dashboard
    ├── admin_students.html         # Student management
    ├── admin_companies.html        # Company management
    ├── admin_jobs.html            # Job management
    ├── admin_applications.html     # Application management
    │
    └── students.html      # Students listing (legacy)
```

## 🗄️ Database Schema

The system uses 6 main tables:

1. **Company** - Company information and contact details
2. **Student** - Student profiles and academic information
3. **Admin** - Administrator accounts and permissions
4. **Job** - Job postings with requirements and details
5. **Application** - Student applications to jobs
6. **Interview** - Interview scheduling and results

## 🎯 Key Functionalities

### Student Features:
- ✅ View personal dashboard with statistics
- ✅ Browse available job openings
- ✅ Apply for jobs (with CGPA eligibility check)
- ✅ Track application status
- ✅ View scheduled interviews
- ✅ Update profile information

### Admin Features:
- ✅ Comprehensive admin dashboard
- ✅ Manage student records
- ✅ Add and manage companies
- ✅ Post job openings
- ✅ Review and process applications
- ✅ Update application statuses
- ✅ Generate placement statistics

## 🚦 Usage Guide

### For Students:
1. Login with student credentials
2. Complete your profile information
3. Browse available jobs on the dashboard
4. Apply for jobs that match your CGPA requirements
5. Track your application status
6. Check for interview schedules

### For Admins:
1. Login with admin credentials
2. Add companies to the system
3. Post job openings for companies
4. Review incoming student applications
5. Update application statuses (Shortlist, Select, Reject)
6. Schedule interviews for shortlisted candidates

## 🔧 Customization

### Adding New Features:
1. **Routes**: Add new Flask routes in `app.py`
2. **Templates**: Create new HTML templates in `templates/`
3. **Styling**: Modify `static/style.css` for custom styling
4. **Database**: Add new tables/columns in `database_setup.sql`

### Configuration Options:
- **Secret Key**: Change Flask secret key for production
- **Database**: Modify connection parameters
- **Email**: Add email functionality for notifications
- **File Upload**: Implement resume upload feature

## 🐛 Troubleshooting

### Common Issues:

**1. Database Connection Error**
```bash
mysql.connector.errors.ProgrammingError: 1045 (28000): Access denied
```
**Solution**: Check MySQL credentials in `app.py`

**2. Module Not Found Error**
```bash
ModuleNotFoundError: No module named 'flask'
```
**Solution**: Install requirements: `pip install -r requirements.txt`

**3. Database Not Found**
```bash
mysql.connector.errors.ProgrammingError: 1049 (42000): Unknown database
```
**Solution**: Run the database setup script: `database_setup.sql`

**4. Port Already in Use**
```bash
OSError: [Errno 48] Address already in use
```
**Solution**: Change the port in `app.py`: `app.run(port=5001)`

## 🚀 Deployment

### For Production:
1. **Use a production database** (not the demo data)
2. **Enable HTTPS** for secure login
3. **Hash passwords** properly (currently plain text for demo)
4. **Set DEBUG=False** in Flask
5. **Use environment variables** for sensitive config

### Deployment Options:
- **Heroku** (with ClearDB MySQL)
- **AWS EC2** (with RDS MySQL)
- **DigitalOcean** (with managed MySQL)
- **Local Server** (Apache/Nginx + MySQL)

## 📊 Demo Data

The system comes with sample data including:
- **4 Companies** (TechCorp, DataSoft, WebFlow, CloudTech)
- **5 Students** with different CGPAs and departments
- **2 Admin accounts** (Super Admin and Placement Officer)
- **5 Job postings** with various requirements
- **Sample applications and interviews**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is created for educational purposes. Feel free to use and modify as needed for your institution.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the database setup
3. Verify all dependencies are installed
4. Ensure MySQL is running

---

**Built with ❤️ for educational institutions to streamline their placement process!**