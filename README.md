# WhatsApp AI Bot

A complete AI-powered WhatsApp automation bot built with Flask, Groq AI (LLaMA 3), and Meta's WhatsApp Cloud API.

## Features

- AI-powered responses in Urdu
- Business assistant behavior
- Automatic greeting detection
- Price list responses
- Order collection (name, address, phone)
- Multi-user conversation memory
- Webhook integration with Meta
- Production-ready deployment

## Folder Structure

```
whatsapp-ai-bot/
├── app.py              # Flask webhook server
├── groq_ai.py          # Groq AI integration
├── whatsapp.py         # WhatsApp Cloud API client
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── render.yaml         # Render.com deployment config
└── README.md           # This file
```

## Prerequisites

1. **Groq API Key**: Get from [https://console.groq.com/keys](https://console.groq.com/keys)
2. **Meta Developer Account**: Create at [https://developers.facebook.com](https://developers.facebook.com)
3. **WhatsApp Business Account**: Set up in Meta Business Manager
4. **Render.com Account**: Create free account at [https://render.com](https://render.com)
5. **GitHub Account**: For code deployment

## Setup Guide

### 1. Clone and Setup Project

```bash
# Clone your repository
git clone https://github.com/yourusername/whatsapp-ai-bot.git
cd whatsapp-ai-bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
GROQ_API_KEY=your_groq_api_key_here
WHATSAPP_API_TOKEN=your_whatsapp_api_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
VERIFY_TOKEN=your_custom_verify_token_here
```

**Where to get these values:**

| Variable | How to Get |
|----------|-----------|
| `GROQ_API_KEY` | Go to [https://console.groq.com/keys](https://console.groq.com/keys) → Create API Key |
| `WHATSAPP_API_TOKEN` | Meta Developer Console → WhatsApp → API Setup → Access Token |
| `WHATSAPP_PHONE_NUMBER_ID` | Meta Developer Console → WhatsApp → API Setup → Phone Number ID |
| `VERIFY_TOKEN` | Create any random secure string (e.g., `my_bot_123_secret`) |

### 3. Meta WhatsApp Cloud API Setup

1. **Create Meta App**:
   - Go to [https://developers.facebook.com/apps](https://developers.facebook.com/apps)
   - Click "Create App"
   - Select "Business" as app type
   - Enter app name

2. **Add WhatsApp Product**:
   - In your app dashboard, click "Add Product"
   - Find "WhatsApp" and click "Set Up"

3. **Get API Credentials**:
   - Go to WhatsApp → API Setup
   - Note down:
     - **Temporary Access Token**
     - **Phone Number ID**
   - Add a test phone number (your own number for testing)

4. **Configure Webhook** (do this after deployment):
   - Go to WhatsApp → Configuration
   - Click "Edit" next to Webhook
   - Callback URL: `https://your-service.onrender.com/webhook`
   - Verify Token: Same as your `VERIFY_TOKEN` env variable
   - Click "Verify and Save"
   - Subscribe to: `messages`, `message_status` events

### 4. Deployment on Render.com

#### Option A: Using render.yaml (Blueprints)

1. **Push code to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/whatsapp-ai-bot.git
git push -u origin main
```

2. **On Render.com**:
   - Log in to [https://dashboard.render.com](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml` and create the service

3. **Add Environment Variables**:
   - Go to your new Web Service
   - Click "Environment" tab
   - Add these variables:
     - `GROQ_API_KEY` = your_groq_api_key
     - `WHATSAPP_API_TOKEN` = your_whatsapp_token
     - `WHATSAPP_PHONE_NUMBER_ID` = your_phone_id
     - `VERIFY_TOKEN` = your_verify_token

#### Option B: Manual Web Service

1. Click "New" → "Web Service"
2. Connect your GitHub repo
3. Configure:
   - **Name**: whatsapp-ai-bot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
4. Add environment variables (same as above)
5. Click "Create Web Service"

### 5. Webhook Configuration in Meta

After deployment:

1. Get your Render service URL: `https://whatsapp-ai-bot-xxx.onrender.com`
2. Go to Meta Developer Console → Your App → WhatsApp → Configuration
3. Click "Edit" next to Webhook
4. Enter:
   - **Callback URL**: `https://your-service.onrender.com/webhook`
   - **Verify Token**: (same as `VERIFY_TOKEN` in your env)
5. Click "Verify and Save"
6. In "Webhook Fields", subscribe to:
   - `messages`
   - `message_statuses`

### 6. Testing the Bot

1. **Health Check**:
   - Visit: `https://your-service.onrender.com/health`
   - Should return: `{"status": "healthy"}`

2. **Test Messages**:
   - Send "hello" or "hi" → Bot replies in Urdu greeting
   - Send "price" or "kitna" → Bot sends price list
   - Send "order" or "buy" → Bot asks for details

## Bot Behavior

| User Input | Bot Response |
|------------|--------------|
| hello, hi, salam | Greeting in Urdu |
| price, kitna, rate | Price list with 4 products |
| order, buy, mangwana | Asks for name, address, phone |
| Other messages | AI-generated Urdu reply |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service status |
| `/health` | GET | Health check |
| `/webhook` | GET | Webhook verification (Meta) |
| `/webhook` | POST | Receive messages |
| `/send-message` | POST | Manual message sending |

### Manual Message API

```bash
curl -X POST https://your-service.onrender.com/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "923001234567",
    "message": "Hello from bot!"
  }'
```

## Local Development

```bash
# Setup environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Copy env file
cp .env.example .env
# Edit .env with your keys

# Run locally
python app.py

# Test webhook locally (use ngrok for external access)
ngrok http 5000
```

## Troubleshooting

### Webhook Verification Failed
- Check that `VERIFY_TOKEN` matches in both `.env` and Meta Console
- Ensure your service is deployed and `/webhook` endpoint is accessible

### Messages Not Received
- Verify webhook is subscribed to `messages` event
- Check Render logs for errors
- Ensure test phone number is added in Meta Console

### API Token Expired
- Temporary tokens expire after 24 hours
- Generate a permanent token in Meta Business Manager

### Bot Not Responding
- Check `GROQ_API_KEY` is valid
- Review Render service logs
- Test Groq API directly

## Security Notes

- Never commit `.env` file
- Use strong, random `VERIFY_TOKEN`
- Rotate API keys regularly
- For production, use Redis/database for conversation storage
- Add rate limiting for production use

## Free Tier Limits

| Service | Free Tier Limit |
|---------|----------------|
| Render | 750 hours/month, sleeps after 15 min inactivity |
| Groq | Check [Groq pricing](https://groq.com/pricing) |
| WhatsApp Cloud API | 1,000 free conversations/month |

## Next Steps for Production

1. Replace in-memory storage with Redis/Database
2. Add proper error handling and retry logic
3. Implement rate limiting
4. Add logging and monitoring
5. Create a dashboard for order management
6. Add more languages support

## Support

- **Groq Docs**: [https://console.groq.com/docs](https://console.groq.com/docs)
- **WhatsApp Cloud API**: [https://developers.facebook.com/docs/whatsapp/cloud-api](https://developers.facebook.com/docs/whatsapp/cloud-api)
- **Render Docs**: [https://render.com/docs](https://render.com/docs)

## License

MIT License - Free for personal and commercial use.
