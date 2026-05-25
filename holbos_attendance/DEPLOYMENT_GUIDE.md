# Render Deployment Guide for Holbos Project

## Prerequisites
- GitHub account with this repository pushed
- Render account (free tier available)

## Step-by-Step Deployment

### 1. Generate a New Secret Key
- Visit: https://djecrety.ir/
- Copy the generated key

### 2. Push to GitHub
```bash
git add .
git commit -m "Add deployment configuration for Render"
git push origin main
```

### 3. Create Render Account & Connect GitHub
1. Go to https://render.com
2. Sign up and connect your GitHub account
3. Grant Render access to your repositories

### 4. Deploy Using render.yaml
1. Click "New +" → "Blueprint"
2. Select your GitHub repository
3. Render will automatically detect render.yaml
4. Set environment variables:
   - **SECRET_KEY**: Paste the key from step 1
   - **DATABASE_URL**: Auto-configured by Render
   
5. Click "Deploy"

### Alternative: Manual Deployment

If the YAML approach doesn't work:

1. Click "New +" → "Web Service"
2. Select your GitHub repository
3. **Configure:**
   - Name: `holbos-project`
   - Runtime: `Python 3`
   - Region: `Oregon` (or your preference)
   - Build Command: `bash build.sh`
   - Start Command: `gunicorn holbos_project.wsgi:application`

4. **Add Environment Variables:**
   ```
   SECRET_KEY = <your-generated-key>
   DEBUG = False
   ALLOWED_HOSTS = your-app-name.onrender.com
   ```

5. **Create Database (PostgreSQL):**
   - Click "Create Database"
   - Plan: Free tier
   - Name: `holbos-db`
   - Render auto-sets DATABASE_URL

### 5. After Deployment

1. App will be available at: `https://your-app-name.onrender.com`
2. Create superuser for admin panel:
   ```bash
   python manage.py createsuperuser
   ```
   Run this in Render's Shell tab

3. Access admin panel: `https://your-app-name.onrender.com/admin`

## Troubleshooting

### Static files not loading
- Already handled by WhiteNoise middleware in settings.py
- Make sure STATIC_ROOT is set correctly

### Database migration errors
- Check build.sh is executable
- View logs in Render dashboard

### Import errors
- Verify all packages are in requirements.txt
- Check Python version compatibility

## Environment Variables Summary

| Variable | Required | Example |
|----------|----------|---------|
| SECRET_KEY | Yes | Generated key from djecrety.ir |
| DEBUG | No | False |
| ALLOWED_HOSTS | No | your-app.onrender.com |
| DATABASE_URL | Auto | postgresql://... |

## Files Created for Deployment

- `requirements.txt` - Python dependencies
- `build.sh` - Build script for Render
- `render.yaml` - Infrastructure as Code configuration
- `.env.example` - Environment variables reference
- `settings.py` - Updated for production

## Support

For issues:
1. Check Render dashboard logs
2. Review Django documentation
3. Ensure all SECRET_KEY is properly set
