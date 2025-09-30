# Deployment Checklist ✅

## Pre-Deployment
- [ ] Set up cloud database (PlanetScale/Railway)
- [ ] Import database schema using `setup_cloud_db.py`
- [ ] Test database connection locally
- [ ] Update environment variables in `.env`
- [ ] Test application locally with cloud database
- [ ] Commit all changes to Git
- [ ] Push to GitHub repository

## Vercel Deployment
- [ ] Create Vercel account
- [ ] Import GitHub repository
- [ ] Configure environment variables in Vercel dashboard
- [ ] Deploy application
- [ ] Test `/health` endpoint
- [ ] Test login functionality
- [ ] Test file upload (resume) functionality
- [ ] Test admin and student dashboards

## Post-Deployment
- [ ] Set up custom domain (optional)
- [ ] Configure file storage for resumes (Cloudinary/S3)
- [ ] Set up monitoring and alerts
- [ ] Update documentation with live URLs
- [ ] Share access credentials with stakeholders

## Environment Variables Needed
```
DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password  
DB_NAME=placement_db
DB_PORT=3306
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=production
```

## Test URLs After Deployment
- Health Check: `https://your-app.vercel.app/health`
- Student Login: `https://your-app.vercel.app/student/login`
- Admin Login: `https://your-app.vercel.app/admin/login`

## Rollback Plan
- [ ] Keep local database backup
- [ ] Keep Git commit history
- [ ] Document working local configuration