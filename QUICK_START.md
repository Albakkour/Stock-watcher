# Quick Start - Free Deployment

This is a condensed guide to get your Stock Watcher app deployed for free in under 30 minutes.

## Prerequisites Checklist

- [ ] GitHub repository with your code
- [ ] Firebase account (free)
- [ ] Render account (free)
- [ ] CloudAMQP account (free)

## Deployment Steps

### 1. CloudAMQP Setup (5 minutes)

1. Sign up at https://www.cloudamqp.com/
2. Create "Little Lemur" instance (free)
3. Copy connection details:
   - Host (e.g., `lemur.rmq.cloudamqp.com`)
   - Username
   - Password

### 2. Render Setup (10 minutes)

1. Go to https://dashboard.render.com/
2. Click "New +" → "Redis"
   - Name: `stock-watcher-redis`
   - Plan: Free
   - Create it

3. Click "New +" → "Blueprint"
   - Connect GitHub repo
   - Select this repository
   - Render will auto-detect `render.yaml`
   - Click "Apply"

4. After services deploy, set RabbitMQ env vars:
   - Go to `stock-watcher-alert-engine` → Environment
   - Add `RABBIT_URL` with your full CloudAMQP URL (e.g., `amqp://user:pass@host/vhost`)
   - Or add individual: `RABBIT_HOST`, `RABBIT_USER`, `RABBIT_PASS`, `RABBIT_VHOST`
   - Repeat for `stock-watcher-generator`

5. Copy your API URL (e.g., `https://stock-watcher-api.onrender.com`)

### 3. Firebase Setup (10 minutes)

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize (in frontend directory)
cd frontend
firebase init hosting
# Select: Use existing project, dist as public dir, yes to SPA

# Set API URL
echo "VITE_API_BASE=https://your-api-url.onrender.com" > .env.production

# Build and deploy
npm install
npm run build
firebase deploy --only hosting
```

### 4. Test It!

1. Visit your Firebase URL
2. Check Render logs to ensure workers are running
3. Wait 15-30 seconds for stock data to appear

## Environment Variables Reference

### Render Services (Auto-configured)
- `REDIS_HOST` - Auto from Redis database
- `REDIS_PORT` - Auto from Redis database  
- `REDIS_PASSWORD` - Auto from Redis database

### Manual Configuration Needed
- `RABBIT_HOST` - Your CloudAMQP host
- `RABBIT_USER` - Your CloudAMQP username
- `RABBIT_PASS` - Your CloudAMQP password

### Frontend (.env.production)
- `VITE_API_BASE` - Your Render API URL

## Troubleshooting

**Workers not starting?**
- Check Render logs
- Verify RabbitMQ credentials are correct

**Frontend can't connect?**
- Check API URL in `.env.production`
- Verify API is accessible at `/docs` endpoint

**No stock data?**
- Check `stock-watcher-generator` logs
- Verify Redis connection
- Check RabbitMQ connection

## Next Steps

- Set up GitHub Actions for auto-deploy (see DEPLOYMENT.md)
- Monitor usage on CloudAMQP (25K messages/month limit)
- Consider upgrading if you need more resources
