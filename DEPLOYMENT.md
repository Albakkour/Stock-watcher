# Free Deployment Guide for Stock Watcher

This guide will help you deploy the Stock Watcher application for free using **Firebase Hosting** (frontend) and **Render** (backend services).

## Architecture Overview

- **Frontend**: React app hosted on Firebase Hosting (free tier)
- **Backend API**: FastAPI service on Render (free tier)
- **Alert Engine**: Python worker on Render (free tier)
- **Stock Generator**: Python worker on Render (free tier)
- **Redis**: Render's free Redis instance (25MB)
- **RabbitMQ**: CloudAMQP free tier (25K messages/month) or alternative solution

## Prerequisites

1. GitHub account with your code pushed to a repository
2. Firebase account (free tier)
3. Render account (free tier)
4. CloudAMQP account (free tier) - for RabbitMQ

## Step 1: Set Up RabbitMQ (CloudAMQP Free Tier)

1. Go to [CloudAMQP](https://www.cloudamqp.com/) and sign up
2. Create a new instance (select the "Little Lemur" free plan)
3. Copy the connection URL (it looks like: `amqp://user:pass@host/vhost`)
4. Note down:
   - Host (e.g., `lemur.rmq.cloudamqp.com`)
   - Username
   - Password
   - Virtual Host (usually your username)

## Step 2: Deploy to Render

### 2.1 Connect GitHub Repository

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Select the repository containing this project

### 2.2 Create Redis Database

1. In Render dashboard, click "New +" → "Redis"
2. Name it: `stock-watcher-redis`
3. Select "Free" plan
4. Click "Create Redis"
5. Note the connection details (host, port, password)

### 2.3 Deploy Services Using render.yaml

1. In Render dashboard, click "New +" → "Blueprint"
2. Select your repository
3. Render will automatically detect `render.yaml`
4. Review the services and click "Apply"

### 2.4 Configure Environment Variables

After deployment, you need to set RabbitMQ credentials manually:

**For `stock-watcher-alert-engine` service:**
- Go to the service → Environment
- Add **ONE** of the following options:

  **Option 1 (Recommended)**: Use the full connection URL from CloudAMQP:
  - `RABBIT_URL`: Your full CloudAMQP URL (e.g., `amqp://user:pass@lemur.rmq.cloudamqp.com/vhost`)

  **Option 2**: Use individual parameters:
  - `RABBIT_HOST`: Your CloudAMQP host (e.g., `lemur.rmq.cloudamqp.com`)
  - `RABBIT_USER`: Your CloudAMQP username
  - `RABBIT_PASS`: Your CloudAMQP password
  - `RABBIT_VHOST`: Your virtual host (usually your username, e.g., `/username`)

**For `stock-watcher-generator` service:**
- Go to the service → Environment
- Add the same RabbitMQ variables as above (use the same option for both services)

**Note**: Redis credentials are automatically injected from the database connection.

### 2.5 Get Backend API URL

1. Once `stock-watcher-api` is deployed, note its URL (e.g., `https://stock-watcher-api.onrender.com`)
2. This will be used for the frontend configuration

## Step 3: Deploy Frontend to Firebase Hosting

### 3.1 Install Firebase CLI

```bash
npm install -g firebase-tools
```

### 3.2 Login to Firebase

```bash
firebase login
```

### 3.3 Initialize Firebase in Your Project

```bash
cd frontend
firebase init hosting
```

When prompted:
- Select "Use an existing project" or create a new one
- Set public directory: `dist`
- Configure as single-page app: **Yes**
- Set up automatic builds: **No** (we'll build manually)

### 3.4 Build Frontend with API URL

1. Create/update `.env.production` in the `frontend` directory:

```bash
VITE_API_BASE=https://your-api-url.onrender.com
```

Replace `your-api-url.onrender.com` with your actual Render API URL.

2. Build the frontend:

```bash
cd frontend
npm install
npm run build
```

### 3.5 Deploy to Firebase

```bash
firebase deploy --only hosting
```

Your frontend will be available at: `https://your-project-id.web.app`

## Step 4: Verify Deployment

1. **Check Backend API**: Visit `https://your-api-url.onrender.com/docs` to see the API documentation
2. **Check Workers**: In Render dashboard, check that both workers are running (no errors in logs)
3. **Check Frontend**: Visit your Firebase hosting URL and verify it connects to the API

## Step 5: Set Up Auto-Deploy (Optional)

### Render Auto-Deploy

Render automatically deploys when you push to your main branch (if connected via GitHub).

### Firebase Auto-Deploy with GitHub Actions

Create `.github/workflows/deploy-frontend.yml`:

```yaml
name: Deploy Frontend to Firebase

on:
  push:
    branches: [ main ]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Build
        run: |
          cd frontend
          npm run build
        env:
          VITE_API_BASE: ${{ secrets.VITE_API_BASE }}
      - uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: '${{ secrets.GITHUB_TOKEN }}'
          firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT }}'
          projectId: your-project-id
          channelId: live
```

## Troubleshooting

### Workers Not Starting

- Check Render logs for errors
- Verify all environment variables are set correctly
- Ensure RabbitMQ connection is working (test with CloudAMQP dashboard)

### Frontend Can't Connect to API

- Check CORS settings in `backend-api/app.py` (already configured for all origins)
- Verify the API URL in `.env.production` matches your Render URL
- Check browser console for CORS errors

### Redis Connection Issues

- Verify Redis database is running in Render
- Check that Redis password is set correctly
- Render's free Redis has a 25MB limit - monitor usage

### RabbitMQ Connection Issues

- Verify CloudAMQP instance is running
- Check connection URL format
- Free tier has rate limits (25K messages/month)

## Free Tier Limitations

### Render Free Tier
- Services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- 750 hours/month total runtime
- Redis: 25MB storage, no persistence

### Firebase Hosting Free Tier
- 10GB storage
- 360MB/day bandwidth
- Unlimited requests

### CloudAMQP Free Tier
- 25,000 messages/month
- 1 connection
- 1 queue

## Cost Optimization Tips

1. **Reduce Update Frequency**: Set `UPDATE_PERIOD` to 30+ seconds to reduce RabbitMQ usage
2. **Monitor Usage**: Keep an eye on CloudAMQP message count
3. **Use Render's Free Redis**: It's sufficient for small-scale usage
4. **Consider Alternatives**: For production, consider upgrading to paid tiers

## Alternative: Simplified Architecture (No RabbitMQ)

If you want to avoid RabbitMQ entirely, you can modify the architecture to have the stock-generator directly check alerts. This would require code changes but eliminates the need for CloudAMQP.

Would you like me to create a simplified version without RabbitMQ?
