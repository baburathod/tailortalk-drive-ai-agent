# 🚀 STREAMLIT FRONTEND - DEPLOYMENT GUIDE

## 📋 TABLE OF CONTENTS
1. [Local Testing](#local-testing)
2. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
3. [Environment Variables](#environment-variables)
4. [Troubleshooting](#troubleshooting)
5. [Final Checklist](#final-checklist)

---

## 🏠 LOCAL TESTING

### Prerequisites
- Python 3.9+
- Your backend already deployed on Render (https://tailortalk-drive-ai-agent.onrender.com)

### Step 1: Install Frontend Dependencies

```bash
cd frontend
pip install -r requirements.txt
```

### Step 2: Configure `.env`

Ensure `frontend/.env` has:
```env
BACKEND_URL=https://tailortalk-drive-ai-agent.onrender.com
```

**For local testing only**, you can use:
```env
BACKEND_URL=http://localhost:8000
```

### Step 3: Run Locally

```bash
streamlit run app.py
```

**Output:**
```
You can now view your Streamlit app in your browser.

URL: http://localhost:8501
```

### Step 4: Test Queries

Try these in the UI:
- ✅ "Find finance PDFs"
- ✅ "Show me all spreadsheets"
- ✅ "Find documents containing internship"

---

## ☁️ STREAMLIT CLOUD DEPLOYMENT

### Step 1: Prepare GitHub Repository

Ensure your GitHub repo has this structure:
```
TailorTalk-assignment/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .streamlit/
│   │   └── config.toml
│   └── .env
├── credentials.json
└── .env
```

### Step 2: Push to GitHub

```bash
cd c:\Users\ramav\Downloads\TailorTalk-assignment
git add .
git commit -m "Complete Streamlit frontend setup"
git push origin main
```

### Step 3: Deploy on Streamlit Cloud

1. Go to: https://share.streamlit.io
2. Click **"New app"**
3. Fill in details:
   - **GitHub account:** baburathod
   - **Repository:** tailortalk-drive-ai-agent
   - **Branch:** main
   - **Main file path:** `frontend/app.py`
4. Click **"Deploy"**

**Wait 2-3 minutes...**

Your app will be live at:
```
https://[your-username]-tailortalk-drive-ai-agent.streamlit.app
```

### Step 4: Configure Secrets

1. In Streamlit Cloud dashboard, go to your app
2. Click **Settings** (gear icon, top-right)
3. Click **Secrets**
4. Paste this:

```
BACKEND_URL=https://tailortalk-drive-ai-agent.onrender.com
```

5. Click **Save**

**Your app auto-reloads with the new environment variable.**

---

## 🔑 ENVIRONMENT VARIABLES

### Frontend (Streamlit Cloud)
- **Location:** Streamlit Cloud → Settings → Secrets
- **Variables:**
  ```
  BACKEND_URL=https://tailortalk-drive-ai-agent.onrender.com
  ```

### Backend (Render) - Already Configured
- GROQ_API_KEY
- GOOGLE_APPLICATION_CREDENTIALS (as Secret File)
- DRIVE_FOLDER_ID
- BACKEND_URL

---

## 🐛 TROUBLESHOOTING

### Issue: "Backend offline" ❌

**Check:**
1. Is backend running? https://tailortalk-drive-ai-agent.onrender.com/docs
2. Is `BACKEND_URL` correct in Streamlit secrets?
3. Are CORS headers enabled? (Should be in FastAPI)

**Fix:**
```python
# In backend/app/main.py, ensure:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Issue: "Request Timeout"

**Cause:** Backend taking >60 seconds to respond

**Solutions:**
1. Check if Google Drive API has credentials.json
2. Reduce search scope (fewer files)
3. Increase timeout: Edit `app.py` line with `timeout=60`

---

### Issue: "Cannot find credentials"

**On Backend:**
1. Go to Render dashboard
2. Settings → Environment
3. Add Secret File: `credentials.json`
4. Paste your Google Service Account JSON

---

## ✅ FINAL CHECKLIST

Before sharing with recruiter:

- [ ] Backend deployed and working (https://tailortalk-drive-ai-agent.onrender.com/docs)
- [ ] Frontend deployed and working (Streamlit Cloud)
- [ ] Chat history displays correctly
- [ ] Sample queries work
- [ ] Error handling shows appropriate messages
- [ ] Loading spinner works
- [ ] Backend status shows "✅ Backend connected" in sidebar
- [ ] Clear chat history button works
- [ ] No console errors
- [ ] Professional UI displays properly
- [ ] All links clickable and functional

---

## 🎯 FINAL SUBMISSION

### Share These Links with Recruiter:

**Live Application:**
```
https://[your-username]-tailortalk-drive-ai-agent.streamlit.app
```

**GitHub Repository:**
```
https://github.com/baburathod/tailortalk-drive-ai-agent
```

**Backend API Docs:**
```
https://tailortalk-drive-ai-agent.onrender.com/docs
```

---

## 💡 TIPS FOR RECRUITER DEMO

1. **Try these queries:**
   - "Find all PDFs"
   - "Show me spreadsheets from last week"
   - "Find documents about internship"

2. **Point out:**
   - ✅ End-to-end full-stack application
   - ✅ Production-ready deployment
   - ✅ Professional UI with error handling
   - ✅ Real-time Google Drive integration
   - ✅ AI-powered natural language search

3. **Architecture:**
   - Streamlit frontend (deployed on Streamlit Cloud)
   - FastAPI backend (deployed on Render)
   - LangChain agent with Groq LLM
   - Google Drive API integration

---

## 📞 SUPPORT

If something breaks:
1. Check Streamlit Cloud logs
2. Check Render backend logs
3. Ensure credentials.json is set on backend
4. Ensure BACKEND_URL is correct
5. Clear browser cache and reload

---

**Status:** ✅ Ready for Production
