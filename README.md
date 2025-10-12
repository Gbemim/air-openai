# ChatBot AI

A full-stack ChatGPT-like chatbot application with session management and file attachment support.

## ⚠️ Current Status

The **backend is fully functional and running on port 5000**. The frontend encountered some file corruption issues during setup due to file creation conflicts. I've removed the frontend folder to allow for a clean rebuild.

## ✅ What's Working

- ✅ Backend API (fully functional)
  - Express server running on port 5000
  - Conversation management endpoints
  - Message handling
  - File upload infrastructure
  - AWS S3 integration utilities ready
- ✅ All backend files created and configured
- ✅ Complete project structure designed

## 🔧 Next Steps

You need to rebuild the frontend. Here's how:

## Project Structure

```
AIR/
├── frontend/          # React frontend with Tailwind CSS
├── backend/           # Node.js/Express backend
└── README.md
```

## Features

- 💬 ChatGPT-like chat interface
- 📁 Session/Conversation management
- 📎 PDF file attachments
- 🔗 Website URL attachments
- 🎨 Modern UI with Tailwind CSS
- 🔄 Real-time messaging
- ☁️ AWS-ready architecture

## Tech Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- Axios
- Lucide React (icons)

### Backend
- Node.js
- Express
- Multer (file uploads)
- AWS SDK (for S3 integration)

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Installation

1. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

2. **Install Backend Dependencies**
```bash
cd backend
npm install
```

### Configuration

1. **Backend Configuration**
   - Copy `.env.example` to `.env` in the backend folder
   - Update the environment variables:
   ```env
   PORT=5000
   NODE_ENV=development
   FRONTEND_URL=http://localhost:3000
   
   # AWS Configuration (optional for now)
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_S3_BUCKET=your_bucket_name
   ```

2. **Frontend Configuration**
   - Create `.env` in the frontend folder (optional):
   ```env
   VITE_API_URL=http://localhost:5000/api
   ```

### Running the Application

1. **Start the Backend**
```bash
cd backend
npm run dev
```
The backend will run on http://localhost:5000

2. **Start the Frontend**
```bash
cd frontend
npm run dev
```
The frontend will run on http://localhost:3000

## Usage

1. Open http://localhost:3000 in your browser
2. Click "New Chat" to start a conversation
3. Type your message in the input box
4. Attach PDFs using the file icon
5. Add website URLs using the link icon
6. Send your message and receive responses

## AWS Integration

### Setting up S3 for File Storage

1. Create an S3 bucket in AWS Console
2. Configure bucket permissions for public/private access
3. Update `.env` with your AWS credentials
4. Uncomment S3 upload code in `backend/routes/upload.js`

### Example S3 Integration

In `backend/routes/upload.js`, replace the local storage with:

```javascript
import { uploadToS3 } from '../utils/aws.js';

router.post('/', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Upload to S3
    const s3Url = await uploadToS3(req.file.path, req.file.filename);

    const fileInfo = {
      filename: req.file.filename,
      originalName: req.file.originalname,
      size: req.file.size,
      mimetype: req.file.mimetype,
      url: s3Url, // S3 URL
    };

    res.status(200).json(fileInfo);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

## LLM Integration

To integrate your own LLM (Language Learning Model):

1. Open `backend/routes/conversations.js`
2. Find the `generateAIResponse` function
3. Replace the placeholder with your LLM API call:

```javascript
async function generateAIResponse(userMessage, attachments) {
  // Example: OpenAI integration
  // const response = await openai.chat.completions.create({
  //   model: "gpt-4",
  //   messages: [{ role: "user", content: userMessage }],
  // });
  // return response.choices[0].message.content;
  
  // Or use your custom LLM API
  // const response = await fetch('YOUR_LLM_API_ENDPOINT', {
  //   method: 'POST',
  //   body: JSON.stringify({ message: userMessage, attachments }),
  // });
  // return await response.json();
}
```

## Database Integration

Currently using in-memory storage. To add a database:

1. Install database driver (e.g., `npm install pg` for PostgreSQL)
2. Create database schema for conversations and messages
3. Replace in-memory arrays in `backend/routes/conversations.js` with database queries

Example schema:
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY,
  title VARCHAR(255),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE messages (
  id UUID PRIMARY KEY,
  conversation_id UUID REFERENCES conversations(id),
  role VARCHAR(50),
  content TEXT,
  attachments JSONB,
  timestamp TIMESTAMP
);
```

## Production Deployment

### Frontend (Vercel/Netlify)
```bash
cd frontend
npm run build
# Deploy the 'dist' folder
```

### Backend (AWS EC2/ECS, Heroku, etc.)
```bash
cd backend
# Set environment variables
npm start
```

## Future Enhancements

- [ ] User authentication
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Real-time WebSocket communication
- [ ] Message search functionality
- [ ] Export conversations
- [ ] Multiple file type support
- [ ] Voice input
- [ ] Dark/Light theme toggle

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT
