import express from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const router = express.Router();

// Create uploads directory if it doesn't exist
const uploadsDir = path.join(__dirname, '../uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + '-' + file.originalname);
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    // Only accept PDFs
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'));
    }
  }
});

// Notify chat of resume processing status
const notifyChatOfProcessing = async (conversationId, filename, success, error = null) => {
  try {
    const content = success 
      ? `✅ **Resume processed successfully!**\n\nI've analyzed "${filename}" and extracted the content. You can now ask me questions about the resume.`
      : `❌ **Resume processing failed**\n\nError processing "${filename}": ${error}. Please try uploading again.`;
    
    await axios.post(`http://localhost:5000/api/conversations/${conversationId}/system-message`, {
      content,
      type: success ? 'success' : 'error'
    });
    
    console.log(`Chat notified: ${success ? 'success' : 'error'} for ${filename}`);
  } catch (err) {
    console.error('Error notifying chat:', err.message);
  }
};

// Execute Python scripts for resume processing
const runPythonScript = (scriptName, args) => {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, '../node-python_scripts', scriptName);
    const pythonProcess = spawn('python3', [pythonScript, ...args]);
    
    let output = '';
    let errorOutput = '';
    
    pythonProcess.stdout.on('data', (data) => output += data.toString());
    pythonProcess.stderr.on('data', (data) => errorOutput += data.toString());
    
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true, output });
      } else {
        reject(new Error(`Python process failed with code ${code}: ${errorOutput}`));
      }
    });
  });
};

// POST /api/upload - Upload and process PDF resume
router.post('/', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Use conversationId as sessionId for consistency with chat
    // This ensures resume data can be retrieved during chat
    const sessionId = req.body.conversationId || req.body.sessionId || uuidv4();
    
    const fileInfo = {
      filename: req.file.filename,
      originalName: req.file.originalname,
      size: req.file.size,
      mimetype: req.file.mimetype,
      sessionId: sessionId,
      url: `/uploads/${req.file.filename}`,
      status: 'uploaded'
    };

    // Process the resume through the pipeline
    try {
      console.log(`Processing resume: ${req.file.originalname} for session: ${sessionId}`);
      
      const args = [req.file.path, req.file.originalname, sessionId];
      const result = await runPythonScript('process_resume.py', args);
      
      fileInfo.status = 'processed';
      fileInfo.processedAt = new Date().toISOString();
      
      console.log('Resume processing completed successfully');
      
      // Notify chat if conversationId is provided
      if (req.body.conversationId) {
        await notifyChatOfProcessing(req.body.conversationId, req.file.originalname, true);
      }
      
    } catch (processingError) {
      console.error('Resume processing failed:', processingError.message);
      
      fileInfo.status = 'processing_failed';
      fileInfo.error = processingError.message;
      
      // Notify chat of error if conversationId is provided
      if (req.body.conversationId) {
        await notifyChatOfProcessing(req.body.conversationId, req.file.originalname, false, processingError.message);
      }
    }

    res.status(200).json(fileInfo);
  } catch (error) {
    console.error('Upload error:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// POST /api/upload/search - Search resume content using KNN
router.post('/search', async (req, res) => {
  try {
    const { query, sessionId, k = 5 } = req.body;
    
    if (!query) {
      return res.status(400).json({ error: 'Search query is required' });
    }
    
    const args = [query, k.toString()];
    if (sessionId) args.push(sessionId);
    
    const result = await runPythonScript('search_resume.py', args);
    const results = JSON.parse(result.output);
    
    res.json({ results, query, sessionId });
    
  } catch (error) {
    console.error('Search endpoint error:', error.message);
    res.status(500).json({ 
      error: error.message.includes('JSON') ? 'Failed to parse search results' : 'Search failed' 
    });
  }
});



// DELETE /api/upload/session/:sessionId - Clean up session data
router.delete('/session/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;
    
    const result = await runPythonScript('cleanup_session.py', [sessionId, uploadsDir]);
    const cleanupData = JSON.parse(result.output);
    
    console.log(`Session cleanup completed for: ${sessionId}`);
    console.log(`OpenSearch deleted: ${cleanupData.opensearch_deleted} documents`);
    console.log(`Files deleted: ${cleanupData.files_deleted.length}`);
    
    res.json(cleanupData);
    
  } catch (error) {
    console.error('Session cleanup error:', error.message);
    res.status(500).json({ 
      error: 'Session cleanup failed',
      details: error.message 
    });
  }
});


// GET /api/upload/sessions - List all sessions and their files
router.get('/sessions', async (req, res) => {
  try {
    const result = await runPythonScript('list_sessions.py', []);
    const sessionData = JSON.parse(result.output);
    
    res.json(sessionData);
    
  } catch (error) {
    console.error('Sessions list error:', error.message);
    res.status(500).json({ 
      error: 'Failed to list sessions',
      details: error.message 
    });
  }
});

// GET /api/upload/session/:sessionId - View session data
router.get('/session/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;
    
    // Use the existing get_session_chunks method
    const result = await runPythonScript('get_session_data.py', [sessionId]);
    const sessionData = JSON.parse(result.output);
    
    res.json({ 
      sessionId, 
      data: sessionData,
      message: 'To delete this session, use DELETE method instead of GET'
    });
    
  } catch (error) {
    console.error('Session view error:', error.message);
    res.status(500).json({ 
      error: 'Failed to retrieve session data',
      details: error.message 
    });
  }
});

// GET /api/upload/:filename - Serve uploaded files (development only)
router.get('/:filename', (req, res) => {
  const { filename } = req.params;
  const filePath = path.join(uploadsDir, filename);
  
  if (fs.existsSync(filePath)) {
    res.sendFile(filePath);
  } else {
    res.status(404).json({ error: 'File not found' });
  }
});

export default router;
