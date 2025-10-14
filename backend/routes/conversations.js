import express from 'express';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

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
    
    // Simulate AI response (replace with actual LLM integration)
    const aiResponse = await generateAIResponse(content, attachments);
    
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

// Simulate AI response (replace with actual LLM API call)
async function generateAIResponse(userMessage, attachments) {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  let response = "I'm an AI assistant that can analyze your resume. ";
  
  if (attachments && attachments.length > 0) {
    response += "This is your message: " + userMessage + "\n\nI can see you've uploaded files. ";
  }
  
  response += "Ask me questions about your resume content, skills, or experience.";
  
  return response;
}

export default router;
