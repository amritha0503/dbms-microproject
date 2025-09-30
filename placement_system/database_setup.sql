-- Placement System Database Schema
-- Run this in MySQL to create the complete database structure

CREATE DATABASE IF NOT EXISTS placement_db;
USE placement_db;

-- Drop existing tables if they exist (in correct order to handle foreign keys)
DROP TABLE IF EXISTS Interview;
DROP TABLE IF EXISTS Application;
DROP TABLE IF EXISTS Job;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Company;
DROP TABLE IF EXISTS Admin;

-- 1. Company Table
CREATE TABLE Company (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100),
    contact_phone VARCHAR(15),
    website VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Student Table
CREATE TABLE Student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    department VARCHAR(50) NOT NULL,
    cgpa DECIMAL(3,2) NOT NULL,
    graduation_year INT NOT NULL,
    phone VARCHAR(15),
    address TEXT,
    resume_path VARCHAR(255),
    status ENUM('Active', 'Placed', 'Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Admin Table
CREATE TABLE Admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role ENUM('Super Admin', 'Placement Officer') DEFAULT 'Placement Officer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Job Table
CREATE TABLE Job (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    job_description TEXT NOT NULL,
    salary_package DECIMAL(10,2),
    location VARCHAR(100),
    eligibility_criteria TEXT,
    min_cgpa DECIMAL(3,2) DEFAULT 0.0,
    required_skills TEXT,
    job_type ENUM('Full-time', 'Part-time', 'Internship') DEFAULT 'Full-time',
    application_deadline DATE,
    status ENUM('Open', 'Closed', 'On-hold') DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES Company(company_id) ON DELETE CASCADE
);

-- 5. Application Table
CREATE TABLE Application (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    job_id INT NOT NULL,
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_round ENUM('Applied', 'Round 1', 'Round 2', 'Technical Interview', 'HR Interview', 'Selected', 'Rejected') DEFAULT 'Applied',
    overall_status ENUM('In Progress', 'Selected', 'Rejected') DEFAULT 'In Progress',
    admin_comments TEXT,
    resume_path VARCHAR(255),
    cover_letter TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES Job(job_id) ON DELETE CASCADE,
    UNIQUE KEY unique_application (student_id, job_id)
);

-- 6. Interview Rounds Table (New enhanced structure)
CREATE TABLE Interview_Rounds (
    round_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    round_name ENUM('Round 1', 'Round 2', 'Technical Interview', 'HR Interview') NOT NULL,
    scheduled_date DATETIME,
    scheduled_time TIME,
    location VARCHAR(200),
    interview_mode ENUM('Online', 'Offline', 'Hybrid') DEFAULT 'Offline',
    interviewer_name VARCHAR(100),
    interviewer_email VARCHAR(100),
    round_status ENUM('Scheduled', 'Completed', 'Cancelled', 'Rescheduled') DEFAULT 'Scheduled',
    result ENUM('Pending', 'Passed', 'Failed', 'On Hold') DEFAULT 'Pending',
    feedback TEXT,
    score DECIMAL(5,2),
    max_score DECIMAL(5,2) DEFAULT 100.00,
    admin_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES Application(application_id) ON DELETE CASCADE
);

-- 7. Interview Table (Keeping for backward compatibility, but Interview_Rounds is preferred)
CREATE TABLE Interview (
    interview_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    interview_date DATETIME NOT NULL,
    interview_type ENUM('Technical', 'HR', 'Group Discussion', 'Final') NOT NULL,
    location VARCHAR(100),
    interviewer_name VARCHAR(100),
    feedback TEXT,
    result ENUM('Pending', 'Passed', 'Failed') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES Application(application_id) ON DELETE CASCADE
);

-- Insert sample data
-- Companies
INSERT INTO Company (company_name, location, contact_email, contact_phone, website, description) VALUES
('TechCorp Solutions', 'Bangalore', 'hr@techcorp.com', '9876543210', 'www.techcorp.com', 'Leading software development company'),
('DataSoft Technologies', 'Hyderabad', 'careers@datasoft.com', '9876543211', 'www.datasoft.com', 'Data analytics and AI solutions'),
('WebFlow Systems', 'Chennai', 'jobs@webflow.com', '9876543212', 'www.webflow.com', 'Web development and digital solutions'),
('CloudTech Innovations', 'Pune', 'hiring@cloudtech.com', '9876543213', 'www.cloudtech.com', 'Cloud infrastructure and services');

-- Admins (passwords are hashed in real app, here plain text for demo)
INSERT INTO Admin (username, password, full_name, email, role) VALUES
('admin', 'admin123', 'System Administrator', 'admin@college.edu', 'Super Admin'),
('placement_officer', 'officer123', 'Placement Officer', 'placement@college.edu', 'Placement Officer');

-- Students (passwords would be hashed in real app)
INSERT INTO Student (name, email, password, department, cgpa, graduation_year, phone, status) VALUES
('Alice Johnson', 'alice@student.com', 'alice123', 'Computer Science', 8.5, 2024, '9876543220', 'Active'),
('Bob Smith', 'bob@student.com', 'bob123', 'Information Technology', 7.8, 2024, '9876543221', 'Active'),
('Carol Davis', 'carol@student.com', 'carol123', 'Electronics', 9.2, 2024, '9876543222', 'Active'),
('David Wilson', 'david@student.com', 'david123', 'Computer Science', 8.0, 2024, '9876543223', 'Active'),
('Eva Brown', 'eva@student.com', 'eva123', 'Information Technology', 8.8, 2024, '9876543224', 'Active');

-- Jobs
INSERT INTO Job (company_id, job_title, job_description, salary_package, location, min_cgpa, required_skills, application_deadline) VALUES
(1, 'Software Developer', 'Develop web applications using modern frameworks', 600000.00, 'Bangalore', 7.0, 'Python, JavaScript, React', '2024-12-31'),
(1, 'Backend Developer', 'Build scalable backend systems', 650000.00, 'Bangalore', 7.5, 'Java, Spring Boot, MySQL', '2024-12-31'),
(2, 'Data Analyst', 'Analyze large datasets and create insights', 550000.00, 'Hyderabad', 7.0, 'Python, SQL, Tableau', '2024-12-25'),
(3, 'Frontend Developer', 'Create responsive user interfaces', 520000.00, 'Chennai', 6.5, 'HTML, CSS, JavaScript, Angular', '2024-12-28'),
(4, 'Cloud Engineer', 'Manage cloud infrastructure', 700000.00, 'Pune', 8.0, 'AWS, Docker, Kubernetes', '2024-12-30');

-- Applications
INSERT INTO Application (student_id, job_id, current_round, overall_status) VALUES
(1, 1, 'Applied', 'In Progress'),
(1, 2, 'Round 1', 'In Progress'),
(2, 1, 'Applied', 'In Progress'),
(2, 3, 'Selected', 'Selected'),
(3, 4, 'Applied', 'In Progress'),
(3, 5, 'Technical Interview', 'In Progress'),
(4, 2, 'Rejected', 'Rejected'),
(5, 1, 'Applied', 'In Progress'),
(5, 5, 'Round 2', 'In Progress');

-- Interview Rounds
INSERT INTO Interview_Rounds (application_id, round_name, scheduled_date, scheduled_time, location, interview_mode, interviewer_name, interviewer_email, round_status, result, feedback, score, admin_notes) VALUES
(2, 'Round 1', '2025-10-05', '10:00:00', 'Conference Room A', 'Offline', 'John Doe', 'john.doe@techcorp.com', 'Completed', 'Passed', 'Good technical knowledge', 85.00, 'Proceed to next round'),
(6, 'Technical Interview', '2025-10-08', '14:00:00', 'Online Meeting', 'Online', 'Sarah Wilson', 'sarah.wilson@cloudtech.com', 'Scheduled', 'Pending', NULL, NULL, 'Technical round for cloud engineer position'),
(9, 'Round 2', '2025-10-10', '11:00:00', 'Conference Room B', 'Offline', 'Mike Johnson', 'mike.johnson@cloudtech.com', 'Scheduled', 'Pending', NULL, NULL, 'Second round assessment');

-- Interviews
INSERT INTO Interview (application_id, interview_date, interview_type, location, interviewer_name, result) VALUES
(2, '2024-01-15 10:00:00', 'Technical', 'Bangalore Office', 'John Doe', 'Passed'),
(4, '2024-01-12 14:00:00', 'HR', 'Online', 'Jane Smith', 'Passed'),
(6, '2024-01-20 11:00:00', 'Technical', 'Pune Office', 'Mike Johnson', 'Pending'),
(9, '2024-01-18 15:00:00', 'Technical', 'Pune Office', 'Sarah Wilson', 'Pending');