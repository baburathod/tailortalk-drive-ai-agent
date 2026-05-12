# 🔧 GOOGLE DRIVE AUTHENTICATION - COMPLETE SETUP GUIDE

## ✅ WHAT WAS FIXED

Your backend code now has:
1. ✅ **Enhanced logging** - Shows exactly where the authentication is failing
2. ✅ **Multiple credential loading methods** - Handles Render's Secret Files mount point
3. ✅ **Better error messages** - Frontend displays helpful guidance
4. ✅ **Proper API initialization** - Tests credentials on startup
5. ✅ **Detailed debugging** - Logs show full authentication flow

---

## 📋 HOW TO SET UP credentials.json IN RENDER

### STEP 1: Get Your Google Service Account JSON

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Go to **Service Accounts** (Search: "Service Accounts")
4. Click your Service Account email
5. Go to **Keys** tab
6. Click **Add Key** → **Create new key**
7. Select **JSON**
8. Click **Create**
9. A JSON file downloads automatically

**IMPORTANT:** Keep this file secure! Don't share it.

### STEP 2: Add credentials.json to Render as Secret File

1. Go to your Render service dashboard
2. Click on your backend service
3. Go to **Settings** (scroll down to bottom of page)
4. Look for **Secret Files** section (at the bottom, above **Region**)
5. Click **Add Secret File**

**In the dialog that appears:**
- **Filename:** `credentials.json`
- **File contents:** 
  - Open the JSON file you downloaded
  - Copy **ALL** the contents
  - Paste into the "File contents" box

6. Click **Create**
7. **Wait for auto-redeploy** (takes 2-3 minutes)

**It should look like this:**
```
Filename: credentials.json
File contents: {
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "...",
  ...
}
```

### STEP 3: Verify DRIVE_FOLDER_ID Environment Variable

1. In Render dashboard, go to **Environment**
2. Look for `DRIVE_FOLDER_ID` (or `GOOGLE_DRIVE_FOLDER_ID`)
3. Make sure it's set to your shared Google Drive folder ID
4. If not set, **add it now**

**How to get your folder ID:**
- Open your shared folder in Google Drive
- Look at the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
- Copy that ID

### STEP 4: Check the Backend Service Started

1. In Render dashboard, go to **Logs**
2. You should see logs like:

```
[startup] Initializing agent on module load...
[CONFIG] GOOGLE_APPLICATION_CREDENTIALS: credentials.json
[INIT] Checking: /etc/secrets/credentials.json
[INIT] ✅ File exists at /etc/secrets/credentials.json
[INIT] ✅ Successfully loaded credentials from file: /etc/secrets/credentials.json
[INIT] [TEST] Testing Google Drive API connection...
[INIT] ✅ Google Drive API v3 service initialized successfully
[INIT] Authenticated as: [YOUR NAME] ([YOUR EMAIL])
[startup] ✅ Agent ready
```

**If you see errors:**
```
[INIT] ❌ CRITICAL: Google Drive credentials not loaded from any source!
```
→ Go back to STEP 2 and check that credentials.json was added

---

## 🧪 TEST YOUR SETUP

### Test 1: Check Backend Logs

1. Render dashboard → **Logs**
2. Look for: `✅ Google Drive API v3 service initialized successfully`
3. If you see it, credentials are working! ✅

### Test 2: Make a Test Request

Use curl or Postman:

```bash
curl -X POST "https://tailortalk-drive-ai-agent.onrender.com/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find PDFs",
    "history": []
  }'
```

**Expected response:**
- If auth works: Returns files or "No files found"
- If auth fails: Returns clear error message

### Test 3: Use Your Streamlit Frontend

1. Open your Streamlit app
2. Type: `"Find PDFs"`
3. Submit

**Expected results:**
- ✅ If working: Shows list of PDF files from your Drive
- ❌ If not working: Shows error message (check logs)

---

## 🐛 TROUBLESHOOTING

### Problem 1: "credentials not found or service not initialized"

**Cause:** credentials.json wasn't added to Render

**Fix:**
1. Go back to STEP 2
2. Add the Secret File
3. Wait for auto-redeploy (2-3 min)
4. Check logs again

### Problem 2: "Invalid JSON format in file"

**Cause:** You pasted incomplete or corrupted JSON

**Fix:**
1. Download your Service Account JSON again from Google Cloud Console
2. Copy the **entire** JSON file
3. Paste it again in Render Secret File
4. Make sure it starts with `{` and ends with `}`

### Problem 3: "Permission denied"

**Cause:** Service Account doesn't have access to your folder

**Fix:**
1. Go to your Google Drive folder
2. Click **Share**
3. Paste your Service Account email (from the JSON file)
4. Give it **Editor** access
5. Click **Share**

### Problem 4: No files found, but files exist

**Cause:** Folder ID might be wrong or Service Account not shared

**Fix:**
1. Verify DRIVE_FOLDER_ID is correct
2. Verify Service Account has access to that folder
3. Try searching all files (omit folder ID temporarily)

### Problem 5: "Private key is invalid"

**Cause:** JSON wasn't pasted correctly

**Fix:**
1. Make sure the `private_key` field has the **full key**
2. It should start with `-----BEGIN PRIVATE KEY-----`
3. And end with `-----END PRIVATE KEY-----`

---

## ✅ COMPLETE SETUP CHECKLIST

- [ ] Downloaded Service Account JSON from Google Cloud
- [ ] Added credentials.json as Secret File in Render
- [ ] Set DRIVE_FOLDER_ID environment variable
- [ ] Shared Drive folder with Service Account email
- [ ] Redeployed Render service
- [ ] Checked logs for `✅ Google Drive API v3 service initialized`
- [ ] Tested with sample query in Streamlit
- [ ] Files are now appearing in responses

---

## 🔍 WHAT THE CODE NOW DOES

### On Startup (Render boots up):
1. ✅ Reads credentials.json from `/etc/secrets/credentials.json`
2. ✅ Validates it's proper JSON
3. ✅ Authenticates with Google Drive API
4. ✅ Tests connection by calling `about()` API
5. ✅ Logs success message with authenticated user info

### On Each Search Request:
1. ✅ Checks credentials are loaded
2. ✅ Checks service is initialized
3. ✅ Builds proper Google Drive API query
4. ✅ Executes files().list() call
5. ✅ Returns files with names, types, links
6. ✅ Logs all details for debugging

### If Anything Fails:
1. ✅ Logs detailed error messages
2. ✅ Returns helpful error to user
3. ✅ Explains what went wrong
4. ✅ Suggests how to fix it

---

## 📚 REFERENCE: Google Drive API Query Examples

Once auth is working, try these queries:

| What You Want | Query |
|---|---|
| All PDFs | `mimeType='application/pdf'` |
| All Sheets | `mimeType='application/vnd.google-apps.spreadsheet'` |
| Files with "budget" | `name contains 'budget'` |
| Modified today | `modifiedTime > '2024-05-13T00:00:00'` |
| PDF + budget | `(name contains 'budget') and mimeType='application/pdf'` |
| Owned by account | `'me' in owners` |

---

## 🆘 IF IT STILL DOESN'T WORK

1. **Check render logs** - Copy full error message
2. **Verify credentials.json** - Make sure it's valid JSON
3. **Check folder sharing** - Service Account has access
4. **Check DRIVE_FOLDER_ID** - Is it correct?
5. **Try alternative**: Use `GOOGLE_CREDENTIALS_JSON` env var with raw JSON string

### Alternative Method: GOOGLE_CREDENTIALS_JSON

Instead of using a file, you can paste the JSON directly as an environment variable:

1. In Render, go to **Environment**
2. Click **Add Environment Variable**
3. Name: `GOOGLE_CREDENTIALS_JSON`
4. Value: Paste the entire JSON (all on one line or multi-line)
5. Save and redeploy

The code will try this method if the file isn't found.

---

## ✨ WHEN IT WORKS

You'll see in Render logs:
```
[INIT] ✅ Successfully loaded credentials from file: /etc/secrets/credentials.json
[INIT] ✅ Google Drive API v3 service initialized successfully
[INIT] Authenticated as: John Doe (john@myproject.iam.gserviceaccount.com)
```

And in Streamlit when you search:
```
Query: Find PDFs
✅ Found 5 PDF files
1. Financial_Report.pdf
2. Budget_2024.pdf
3. Proposal.pdf
...
```

---

## 🎯 NEXT STEPS

1. ✅ **Do the setup above** (STEPS 1-4)
2. ✅ **Check Render logs** to verify it worked
3. ✅ **Test in Streamlit** with sample query
4. ✅ **Celebrate!** Google Drive search now works

---

**Need help?** Check the logs in Render. The error messages will tell you exactly what's wrong and how to fix it.
