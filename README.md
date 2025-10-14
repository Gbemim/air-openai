# Career AI Agents - Full Stack AI System

**AI Refinery + AWS OpenSearch + OpenAI**

A complete career guidance system that:
- Accepts PDF resume uploads
- Stores resumes in AWS OpenSearch vector database  
- Uses AI Refinery orchestrator with custom agents
- Provides intelligent career guidance

---


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
5. Send your message and receive responses



