import express from 'express';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const router = express.Router();

// In-memory storage (replace with database later)
let conversations = [];
let messages = [];

// GET /api/conversations - Get all conversations
router.get('/', (req, res) => {
  try {
    // Sort by most recent first
    const sortedConversations = [...conversations].sort(
      (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
    );
    res.json(sortedConversations);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST /api/conversations - Create a new conversation
router.post('/', (req, res) => {
  try {
    const newConversation = {
      id: uuidv4(),
      title: 'New Conversation',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    
    conversations.push(newConversation);
    res.status(201).json(newConversation);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});



// DELETE /api/conversations/:conversationId - Delete a conversation
router.delete('/:conversationId', async (req, res) => {
  try {
    const { conversationId } = req.params;
    const index = conversations.findIndex(c => c.id === conversationId);
    
    if (index === -1) {
      return res.status(404).json({ error: 'Conversation not found' });
    }
    
    conversations.splice(index, 1);
    
    // Also delete all messages in this conversation
    messages = messages.filter(m => m.conversationId !== conversationId);
    
    // Clean up associated session data (uploads and OpenSearch data)
    try {
      const cleanupResponse = await axios.delete(`http://localhost:5000/api/upload/session/${conversationId}`);
      console.log(`Session cleanup completed:`, cleanupResponse.data);
    } catch (cleanupError) {
      console.warn('Session cleanup failed:', cleanupError.message);
      // Don't fail the conversation deletion if cleanup fails
    }
    
    res.json({ message: 'Conversation deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET /api/conversations/:conversationId/messages - Get messages for a conversation
router.get('/:conversationId/messages', (req, res) => {
  try {
    const { conversationId } = req.params;
    const conversation = conversations.find(c => c.id === conversationId);
    
    if (!conversation) {
      return res.status(404).json({ error: 'Conversation not found' });
    }
    
    const conversationMessages = messages
      .filter(m => m.conversationId === conversationId)
      .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    res.json(conversationMessages);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST /api/conversations/:conversationId/messages - Send a message
router.post('/:conversationId/messages', async (req, res) => {
  try {
    const { conversationId } = req.params;
    const { content, attachments = [] } = req.body;
    
    const conversation = conversations.find(c => c.id === conversationId);
    
    if (!conversation) {
      return res.status(404).json({ error: 'Conversation not found' });
    }
    
    // Create user message
    const userMessage = {
      id: uuidv4(),
      conversationId,
      role: 'user',
      content,
      attachments,
      timestamp: new Date().toISOString(),
    };
    
    messages.push(userMessage);
    
    // Update conversation title if it's the first message
    if (messages.filter(m => m.conversationId === conversationId).length === 1) {
      conversation.title = content.substring(0, 50) + (content.length > 50 ? '...' : '');
    }
    
    conversation.updatedAt = new Date().toISOString();
    
    // Generate AI response using AI Refinery + AWS OpenSearch
    const aiResponse = await generateAIResponse(content, conversationId, attachments);
    
    const aiMessage = {
      id: uuidv4(),
      conversationId,
      role: 'assistant',
      content: aiResponse,
      timestamp: new Date().toISOString(),
    };
    
    messages.push(aiMessage);
    
    res.status(201).json(aiMessage);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST /api/conversations/:conversationId/system-message - Add system notification
router.post('/:conversationId/system-message', (req, res) => {
  try {
    const { conversationId } = req.params;
    const { content, type = 'info' } = req.body;
    
    const conversation = conversations.find(c => c.id === conversationId);
    
    if (!conversation) {
      return res.status(404).json({ error: 'Conversation not found' });
    }
    
    // Create system message
    const systemMessage = {
      id: uuidv4(),
      conversationId,
      role: 'system',
      content,
      type, // 'info', 'success', 'error'
      timestamp: new Date().toISOString(),
    };
    
    messages.push(systemMessage);
    conversation.updatedAt = new Date().toISOString();
    
    res.status(201).json(systemMessage);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Generate AI response using AI Refinery + AWS OpenSearch pipeline
async function generateAIResponse(userMessage, conversationId, attachments) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(__dirname, '../node-python_scripts/chat_script.py');
    
    // Use conversationId as both user_id and session_id for resume context
    const args = [scriptPath, userMessage, conversationId, conversationId];
    
    const pythonProcess = spawn('python3', args);
    
    let stdoutData = '';
    let stderrData = '';
    
    pythonProcess.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      stderrData += data.toString();
      console.error('Python stderr:', data.toString());
    });
    
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          // Extract JSON from output (it's the last line after all the notices)
          const lines = stdoutData.trim().split('\n');
          const jsonLine = lines[lines.length - 1]; // Get the last line which should be JSON
          
          const result = JSON.parse(jsonLine);
          
          if (result.success) {
            // Return the AI response (without the service badge to keep it clean)
            resolve(result.response);
          } else {
            console.error('AI processing failed:', result.error);
            resolve("I apologize, but I encountered an error processing your request. Please try again.");
          }
        } catch (parseError) {
          console.error('Error parsing Python response:', parseError);
          console.error('Raw output:', stdoutData);
          resolve("I apologize, but I encountered an error processing your request. Please try again.");
        }
      } else {
        console.error(`Python process exited with code ${code}`);
        console.error('stderr:', stderrData);
        resolve("I apologize, but I encountered an error processing your request. Please try again.");
      }
    });
    
    pythonProcess.on('error', (error) => {
      console.error('Failed to start Python process:', error);
      reject(error);
    });
  });
}

export default router;
