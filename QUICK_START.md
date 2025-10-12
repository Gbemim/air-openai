# 🎉 ChatBot AI - Ready to Use!

## ✅ Status: FULLY OPERATIONAL

Both frontend and backend are now running!

### 🌐 Access the Application

**Frontend:** http://localhost:3000
**Backend API:** http://localhost:5000

---

## 🚀 What's Working

### ✅ Backend (Port 5000)
- REST API for conversations
- Message handling
- File uploads (PDF)
- URL attachments support

### ✅ Frontend (Port 3000)
- Clean, simple ChatGPT-like interface
- Conversation sidebar
- Message input with attachments
- PDF file upload
- Website URL attachment
- Real-time messaging

---

## 🎨 Features

1. **Session Management**
   - Click "➕ New Chat" to start a conversation
   - All conversations appear in the sidebar
   - Click to switch between conversations
   - Hover over a conversation and click 🗑️ to delete

2. **Messaging**
   - Type your message in the text area
   - Press Enter to send (Shift+Enter for new line)
   - See your messages on the right (green)
   - AI responses on the left (gray)

3. **File Attachments**
   - Click 📎 to attach a PDF file
   - Only PDF files are supported
   - Files are uploaded to the backend

4. **URL Attachments**
   - Click 🔗 to add a website URL
   - Enter the URL and click "Add"
   - URLs appear with your message

---

## 🔧 How to Use

1. **Open your browser** and go to: http://localhost:3000

2. **Click "➕ New Chat"** to create your first conversation

3. **Type a message** and press Enter or click ➤

4. **Attach files or URLs** using the 📎 and 🔗 buttons

5. **Switch conversations** by clicking on them in the sidebar

---

## 🤖 LLM Integration

The backend currently returns a placeholder response. To integrate your own LLM:

1. Open: `/home/gbemi/AIR/backend/routes/conversations.js`
2. Find the `generateAIResponse` function (around line 103)
3. Replace with your LLM API call:

```javascript
async function generateAIResponse(userMessage, attachments) {
  // Example: Call your LLM API
  const response = await fetch('YOUR_LLM_ENDPOINT', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: userMessage,
      files: attachments.filter(a => a.type === 'file'),
      urls: attachments.filter(a => a.type === 'url')
    })
  });
  
  const data = await response.json();
  return data.response;
}
```

---

## 🛑 Stopping the Servers

**To stop the backend:**
```bash
# In the backend terminal, press Ctrl+C
```

**To stop the frontend:**
```bash
# In the frontend terminal, press Ctrl+C
```

---

## 🔄 Restarting

**Backend:**
```bash
cd /home/gbemi/AIR/backend
npm run dev
```

**Frontend:**
```bash
cd /home/gbemi/AIR/frontend
python3 -m http.server 3000
```

---

## 📂 Project Structure

```
AIR/
├── backend/              # Express API (Port 5000)
│   ├── routes/
│   │   ├── conversations.js  # Chat logic
│   │   └── upload.js         # File uploads
│   ├── utils/
│   │   └── aws.js            # AWS S3 utilities
│   ├── server.js             # Main server
│   └── .env                  # Configuration
│
├── frontend/             # React UI (Port 3000)
│   └── index.html        # Single-file app
│
└── README.md
```

---

## ☁️ AWS S3 Integration (Optional)

Currently, files are stored locally. To use AWS S3:

1. Update `.env` in the backend folder:
```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your_bucket
```

2. Uncomment S3 code in `backend/routes/upload.js`

---

## 💡 Tips

- The app works entirely in your browser
- No build process needed for the frontend
- All data is stored in memory (restart clears data)
- To persist data, integrate a database

---

## 🎯 Next Steps

1. **Test the interface** at http://localhost:3000
2. **Integrate your LLM** in the backend
3. **Add a database** for data persistence
4. **Deploy to production** (AWS, Vercel, etc.)

---

## ❓ Troubleshooting

**Can't access the frontend?**
- Make sure you're going to http://localhost:3000
- Check that the Python server is running

**Backend not responding?**
- Verify backend is running on port 5000
- Check: `curl http://localhost:5000/api/health`

**CORS errors?**
- The backend is configured to allow localhost:3000
- If you change ports, update `backend/.env`

---

## 🎉 Enjoy your ChatBot!

Your clean and simple ChatGPT-like interface is ready to use!
