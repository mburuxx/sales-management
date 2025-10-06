# 🚂 Railway Deployment Guide

Railway is an excellent choice for deploying Django applications because it offers:
- **Free tier** with generous limits (500 hours/month)
- **Automatic PostgreSQL** database provisioning
- **Zero-config deployments** from Git
- **Environment variables** management
- **Automatic HTTPS** certificates
- **No server management** required

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI**: Install the Railway command-line tool
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## 🛠 Installation Options

### Option 1: Using NPM
```bash
npm install -g @railway/cli
```

### Option 2: Using Install Script
```bash
curl -fsSL https://railway.app/install.sh | sh
```

### Option 3: Using Homebrew (macOS)
```bash
brew install railway
```

## 🚀 Quick Deployment

### Method 1: Automated Script (Recommended)
```bash
# Run our automated deployment script
./scripts/deploy-railway.sh
```

### Method 2: Manual Steps

1. **Login to Railway**
   ```bash
   railway login
   ```

2. **Initialize Project**
   ```bash
   railway init
   ```

3. **Add PostgreSQL Database**
   ```bash
   # In Railway dashboard, click: + New → Database → Add PostgreSQL
   # Railway automatically provides DATABASE_URL
   ```

4. **Set Environment Variables**
   ```bash
   # Generate and set secret key
   railway variables set SECRET_KEY="your-generated-secret-key"
   railway variables set DEBUG=False
   railway variables set ALLOWED_HOSTS="localhost,127.0.0.1,.railway.app"
   ```

5. **Deploy Application**
   ```bash
   railway up
   ```

6. **Run Migrations & Create Superuser**
   ```bash
   railway run python manage.py migrate
   railway run python manage.py createsuperuser
   railway run python manage.py loaddata sales/fixtures/initial_data.json
   ```

## 🌐 GitHub Integration

For automatic deployments from GitHub:

1. Go to [railway.app/new](https://railway.app/new)
2. Click **"Deploy from GitHub repo"**
3. Select your `sales-management` repository
4. Railway automatically detects Django and configures deployment
5. Add PostgreSQL database from the dashboard
6. Set environment variables in Railway dashboard

## ⚙️ Environment Variables

Railway automatically provides:
- `DATABASE_URL` (when PostgreSQL is added)
- `PORT` (for the web server)
- `RAILWAY_ENVIRONMENT` (detected automatically)

You need to set:
- `SECRET_KEY` (Django secret key)
- `DEBUG` (set to `False`)
- `ALLOWED_HOSTS` (your domain + `.railway.app`)

### Setting Variables via CLI
```bash
railway variables set SECRET_KEY="your-secret-key"
railway variables set DEBUG=False
railway variables set ALLOWED_HOSTS=".railway.app"
```

### Setting Variables via Dashboard
1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add environment variables

## 📁 Deployment Files

Your project includes these Railway configuration files:

### `railway.toml`
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn salesmgt.wsgi --log-file -"
healthcheckPath = "/health/"
healthcheckTimeout = 300
restartPolicyType = "always"

[environment]
NIXPACKS_PYTHON_VERSION = "3.11"
```

### `Procfile`
```
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn salesmgt.wsgi --log-file -
```

### `nixpacks.toml`
```toml
providers = ["python"]

[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["python manage.py collectstatic --noinput"]

[start]
cmd = "python manage.py migrate && gunicorn salesmgt.wsgi --bind 0.0.0.0:$PORT"
```

## 🔧 Database Configuration

Railway automatically configures PostgreSQL:

1. **Add PostgreSQL**:
   - Dashboard → + New → Database → Add PostgreSQL
   - Railway creates `DATABASE_URL` environment variable

2. **Database Settings**: Your Django settings automatically detect Railway:
   ```python
   DATABASE_URL = config('DATABASE_URL', default=None)
   if DATABASE_URL:
       import dj_database_url
       DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
   ```

## 🚀 Post-Deployment

After successful deployment:

1. **Create Superuser**
   ```bash
   railway run python manage.py createsuperuser
   ```

2. **Load Initial Data**
   ```bash
   railway run python manage.py loaddata sales/fixtures/initial_data.json
   ```

3. **Access Your App**
   ```bash
   railway open
   ```

## 📊 Monitoring & Management

### View Logs
```bash
railway logs
```

### View Environment Variables
```bash
railway variables
```

### Open Railway Shell
```bash
railway shell
```

### Connect to Database
```bash
railway connect postgresql
```

## 🔒 Security Configuration

Railway automatically handles:
- **HTTPS certificates** (automatic)
- **Environment isolation**
- **Secure environment variables**

Your Django settings include:
- Security headers
- CSRF protection
- XSS protection
- Content type sniffing protection

## 💰 Cost Estimation

**Railway Free Tier**:
- 500 execution hours/month
- $5 credit/month
- Shared CPU and memory
- 1GB RAM per service
- PostgreSQL included

**Paid Plans** (if you exceed free tier):
- $5/month for hobby plan
- Pay-per-use pricing
- More resources and features

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check logs
   railway logs
   
   # Verify requirements.txt
   railway run pip list
   ```

2. **Database Connection Issues**
   ```bash
   # Check database status
   railway variables | grep DATABASE_URL
   
   # Test database connection
   railway run python manage.py dbshell
   ```

3. **Static Files Not Loading**
   ```bash
   # Manually collect static files
   railway run python manage.py collectstatic --noinput
   ```

4. **Environment Variables**
   ```bash
   # List all variables
   railway variables
   
   # Check specific variable
   railway run echo $SECRET_KEY
   ```

### Debug Commands
```bash
# Check deployment status
railway status

# View recent deployments
railway list

# Restart service
railway restart

# View service metrics
railway open --dashboard
```

## 🔄 Continuous Deployment

When connected to GitHub:
- **Automatic deployments** on git push
- **Branch deployments** (main branch → production)
- **Preview deployments** for pull requests
- **Rollback capabilities**

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Django on Railway Guide](https://docs.railway.app/guides/django)
- [Railway CLI Reference](https://docs.railway.app/develop/cli)
- [Environment Variables Guide](https://docs.railway.app/develop/variables)

## 🎯 Next Steps

After deployment:
1. Set up custom domain (optional)
2. Configure email backend
3. Set up monitoring and alerting
4. Implement backup strategy
5. Configure CI/CD pipeline

Your Sales Management System is now ready for production on Railway! 🎉