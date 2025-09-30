# Vercel Deployment Guide for Placement System

## Prerequisites

1. **Database Setup**: You'll need a cloud MySQL database. Recommended options:
   - **PlanetScale** (Free tier available)
   - **Railway** (Free tier available)
   - **AWS RDS** (Paid)
   - **Google Cloud SQL** (Paid)
   - **Aiven** (Free tier available)

2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)

## Step-by-Step Deployment

### 1. Setup Cloud Database

#### Option A: PlanetScale (Recommended - Free)
1. Go to [planetscale.com](https://planetscale.com)
2. Sign up and create a new database
3. Import your database schema from `database_setup.sql`
4. Get connection details (host, username, password)

#### Option B: Railway (Alternative - Free)
1. Go to [railway.app](https://railway.app)
2. Create a MySQL service
3. Import your database schema
4. Get connection details

### 2. Prepare for Deployment

1. **Clone/Download your project**
2. **Set up environment variables** (create `.env` file):
   ```env
   DB_HOST=your_planetscale_host
   DB_USER=your_planetscale_username
   DB_PASSWORD=your_planetscale_password
   DB_NAME=placement_db
   DB_PORT=3306
   FLASK_SECRET_KEY=your_super_secret_random_key
   FLASK_ENV=production
   ```

### 3. Deploy to Vercel

#### Method 1: GitHub Integration (Recommended)
1. Push your code to GitHub repository
2. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
3. Click "New Project"
4. Import your GitHub repository
5. Set Environment Variables:
   - Go to Project Settings → Environment Variables
   - Add all variables from your `.env` file
6. Deploy!

#### Method 2: Vercel CLI
1. Install Vercel CLI: `npm i -g vercel`
2. In your project folder: `vercel`
3. Follow the prompts
4. Set environment variables: `vercel env add`

### 4. Post-Deployment

1. **Test your application**
2. **Set up custom domain** (optional)
3. **Configure database connection pooling** for better performance

## Important Notes

### File Upload Considerations
- Vercel has limitations on file storage
- Consider using cloud storage for resume uploads:
  - **Cloudinary** (Free tier)
  - **AWS S3** (Paid)
  - **Supabase Storage** (Free tier)

### Database Connection
- Use connection pooling for production
- Set appropriate timeout values
- Consider read replicas for better performance

### Security
- Never commit `.env` files
- Use strong secret keys
- Set up proper CORS if needed
- Consider adding rate limiting

## Troubleshooting

### Common Issues:
1. **Database Connection Timeout**
   - Increase connection timeout in config
   - Check database credentials

2. **Cold Start Issues**
   - First request might be slow (normal for serverless)

3. **File Upload Issues**
   - Implement cloud storage solution
   - Check file size limits

### Environment Variables in Vercel:
```
DB_HOST=your_database_host
DB_USER=your_database_user  
DB_PASSWORD=your_database_password
DB_NAME=placement_db
DB_PORT=3306
FLASK_SECRET_KEY=your_secret_key
FLASK_ENV=production
```

## Alternative: Railway Deployment

If you prefer Railway (simpler for beginners):
1. Connect GitHub repo to Railway
2. Add MySQL service
3. Set environment variables
4. Deploy automatically

## Cost Considerations

- **Vercel**: Free tier (limited)
- **PlanetScale**: Free tier (5GB storage)
- **Railway**: Free tier (5GB storage, 500 hours/month)

Total monthly cost: $0 for free tiers!