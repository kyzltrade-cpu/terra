# Terra: AI-Native Pre-Construction Estimator & WhatsApp SLA Compliance Engine

**Terra** is a lightweight, high-performance, and extremely robust commercial facility and janitorial operating platform. It is engineered specifically to protect gross margins at the two most critical points of the commercial cleaning contract lifecycle: **winning the contract** and **proving the work**.

---

## Key Features

1.  **AI Bid Copilot (Pre-Bid):** Parses unstructured corporate and municipal PDF RFPs and CAD blueprints. Automatically extracts cleanable square footage and floor materials (carpet, tile, terrazzo) and maps them to standard **ISSA Cleaning Production Rates** using the robust **Llama 3.1 70B model on NVIDIA NIM** to generate margin-protected, contract-winning bids in under 3 minutes.
2.  **WhatsApp Zero-Friction Ingress (Post-Shift):** Replaces high-friction native mobile apps with WhatsApp. Workers scan physical QR codes placed inside high-traffic zones (e.g., restroom doors, main lobbies), which pre-populates a secure WhatsApp check-in message.
3.  **GPS Geofence Validation:** A secure Twilio webhook validates the user's real-time GPS location against the property's CAD bounds using the Haversine formula, completely eliminating compliance fraud ("ghost cleaning").
4.  **Whisper Voice Logbook:** Workers record natural-language Spanish or dialect voice memos. The backend transcribes the audio, maps terms against our custom **Slang Context Dictionary** (translating field slang like *"pulidora"* or *"mopa"*), and automatically dispatches canonical English maintenance tickets.

---

## Codebase Directory Structure

```
terra/
├── .env                            # Pre-warmed NVIDIA NIM API keys
├── .gitignore
├── requirements.txt                # Python package dependencies
├── README.md                       # Product documentation
├── implementation_plan.md          # Technical database & route specifications
├── backend/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application layer
│   ├── database.py                 # SQLAlchemy database setup & get_db()
│   ├── models.py                   # ORM models (Properties, Zones, Events)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── bid_copilot.py          # PDF RFP parsing routes
│   │   └── whatsapp_webhook.py     # Twilio Webhook (QR scans + geofencing)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bid_estimator.py        # ISSA production math & Llama 3.1 70B NIM service
│   │   └── voice_processor.py      # Whisper translation & slang dictionary mapping
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py             # FastAPI TestClient & Mock DB fixtures
│       ├── test_bid_estimator.py   # Test suite for ISSA calculations
│       ├── test_voice_processor.py # Test suite for slang translation
│       └── test_whatsapp_webhook.py# Test suite for QR scans & voice webhooks
```

---

## Setup & Local Installation

### 1. Create a Virtual Environment and Install Dependencies
```bash
# Initialize venv
python3 -m venv venv
source venv/bin/activate

# Install all packages
pip install -r requirements.txt
```

### 2. Configure Environment Variables (`.env`)
Create a `.env` file in the root directory:
```ini
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/terraclean
NVIDIA_API_KEY=your_nvidia_nim_api_key_here
NVIDIA_MODEL=meta/llama-3.1-70b-instruct
```

### 3. Run the Automated Test Suite
Verify that all core services, geofencing coordinates, and Whisper translation schemas are passing:
```bash
./venv/bin/pytest backend/tests/ -v
```

### 4. Start the Local Server
```bash
./venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## Configuring the Twilio Webhook URL

Twilio requires a publicly routable HTTPS endpoint to forward incoming WhatsApp messages to your local WSL server.

### Step 1: Start a Secure Tunnel using Cloudflare
```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

### Step 2: Grab the Generated Endpoint
Cloudflare will output a public hostname like:
`https://your-unique-subdomain.trycloudflare.com`

### Step 3: Configure Twilio WhatsApp Sandbox
1. Go to your **Twilio Console** -> **Messaging** -> **Try it Out** -> **Send a WhatsApp Message**.
2. Go to **Sandbox Settings**.
3. Under **"When a message comes in"**, paste your secure endpoint followed by the WhatsApp route:
   `https://your-unique-subdomain.trycloudflare.com/api/whatsapp/webhook`
4. Click **Save**.
