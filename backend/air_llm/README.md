# Career AI Agents - Full Stack AI System

**AI Refinery + AWS OpenSearch + OpenAI**

A complete career guidance system that:
- ✅ Accepts PDF resume uploads
- 🔍 Stores resumes in AWS OpenSearch vector database  
- 🤖 Uses AI Refinery orchestrator with custom agents
- 💬 Provides intelligent career guidance

---

## 🏗️ Complete Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│              (React - Upload PDF Resume)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP POST
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Node.js)                         │
│              routes/upload.js → multer                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ spawn Python script
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              PYTHON PROCESSING PIPELINE                      │
│   node-python_scripts/process_resume.py → db/chunk.py       │
│                                                               │
│   1. Extract PDF text (pdfminer)                             │
│   2. Chunk sections (RecursiveCharacterTextSplitter)         │
│   3. Generate embeddings (OpenAI text-embedding-3-large)     │
│   4. Store in AWS OpenSearch (3072-dim vectors)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│           AWS OPENSEARCH (Vector Database)                   │
│              Index: resume-vectors                           │
│              - knn_vector field (3072 dimensions)            │
│              - Stores resume chunks with metadata            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              AI REFINERY ORCHESTRATOR                        │
│              (Distiller + Custom Agents)                     │
│                                                               │
│   Agents:                                                    │
│   1. Resume Search Agent                                     │
│      - Uses: OpenAI embeddings + AWS OpenSearch             │
│      - Semantic vector search                                │
│                                                               │
│   2. Resume Assessment Agent                                 │
│      - Uses: AI Refinery (Llama-3.1-70B)                    │
│      - Analyzes resume, provides feedback                    │
│                                                               │
│   3. Job Search Agent                                        │
│      - Uses: AI Refinery (Llama-3.1-70B)                    │
│      - Finds jobs, suggests platforms                        │
│                                                               │
│   4. Interview Prep Agent                                    │
│      - Uses: AI Refinery (Llama-3.1-70B)                    │
│      - Interview questions & strategies                      │
│                                                               │
│   5. General Career Agent                                    │
│      - Uses: OpenAI (GPT-4)                                  │
│      - General career guidance & advice                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
backend/
├── air_llm/                    # AI Agents (THIS FOLDER)
│   ├── config.yaml             # AI Refinery orchestrator config
│   ├── agents.py               # Custom agents + DistillerClient
│   ├── web_enhanced.py         # Web interface with OpenSearch
│   └── README.md               # This file
│
├── db/                         # Database & Processing
│   ├── aws_opensearch.py       # OpenSearch client
│   └── chunk.py                # PDF → Chunks → Embeddings
│
├── node-python_scripts/        # Node ↔ Python bridge
│   ├── process_resume.py       # Called by Node.js
│   └── search_resume.py        # Search resumes
│
├── routes/                     # Node.js API routes
│   ├── upload.js               # Handle PDF uploads
│   └── conversations.js        # Chat endpoints
│
└── server.js                   # Express server

frontend/
└── src/                        # React app for uploads
```

---

## 🔄 Complete User Flow

### 1. **Resume Upload**
```
User uploads PDF → Node.js (upload.js) → Python (process_resume.py)
→ Extract text → Chunk → OpenAI embeddings → AWS OpenSearch
```

### 2. **Chat with Bot**
```
User asks question → AI Refinery Orchestrator analyzes intent
→ Routes to appropriate agent:
   - Resume Search Agent (if needs resume context)
   - Assessment/Jobs/Interview Agent (for analysis)
→ Agent processes using Llama-3.1-70B
→ Response returned to user
```

---

## 🔧 Services Used

### 1. **AI Refinery** (Primary - Orchestration & LLM)
- **DistillerClient**: Project & agent management
- **AsyncAIRefinery**: Chat completions API
- **Model**: meta-llama/Llama-3.1-70B-Instruct
- **Purpose**: Smart routing, resume analysis, job search, interview prep

### 2. **OpenAI** (Embeddings & Search)
- **Model**: text-embedding-3-large (3072 dimensions)
- **Purpose**: Generate embeddings for vector search

### 3. **AWS OpenSearch** (Vector Database)
- **Index**: resume-vectors
- **Type**: knn_vector
- **Purpose**: Store and search resume chunks semantically

---

## 🚀 Setup

### Prerequisites
```bash
# Python packages
pip install airefinery-sdk
pip install opensearchpy requests-aws4auth boto3
pip install pdfminer.six langchain-text-splitters openai

# Node.js packages (already in package.json)
npm install
```

### Environment Variables (.env)
```bash
# AI Refinery
AIR_API_KEY=your_ai_refinery_key

# OpenAI
OPENAI_API_KEY=your_openai_key

# AWS OpenSearch
OPENSEARCH_ENDPOINT=your-opensearch-domain.us-east-1.es.amazonaws.com
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### Run Tests
```bash
# Test AI Refinery agents
cd backend/air_llm
python web_enhanced.py

# Test full backend
cd backend
npm start

# Test frontend
cd frontend
npm start
```

---

## 💡 How It Works

### Resume Upload Process

1. **Frontend**: User uploads PDF
2. **Node.js**: Receives file, saves to `/uploads`
3. **Python Script**: Spawned by Node.js
   ```python
   process_resume_pipeline(file_path, filename, session_id)
   ```
4. **Processing**:
   - Extract text from PDF
   - Split into chunks (1000 chars each)
   - Generate OpenAI embeddings (3072-dim)
   - Store in AWS OpenSearch with metadata
5. **Result**: Resume searchable via vector similarity

### Chat Process

1. **User**: Sends message with optional `session_id`
2. **AI Refinery Orchestrator**: Analyzes message intent
3. **Routing**:
   - If needs resume context → **Resume Search Agent**
     - Searches OpenSearch using OpenAI embeddings
     - Returns relevant resume sections
   - Then routes to → **Assessment/Jobs/Interview Agent**
     - Uses Llama-3.1-70B for analysis
4. **Response**: Returned to user

---

## 📝 API Examples

### Python (Direct)
```python
from web_enhanced import handle_chat, search_resume

# Chat with bot
result = await handle_chat(
    "Assess my resume",
    user_id="user123",
    session_id="session_abc"
)

# Direct vector search
results = await search_resume(
    "Python experience",
    session_id="session_abc"
)
```

### Node.js (via routes)
```javascript
// Upload resume
POST /api/upload
Content-Type: multipart/form-data
Body: { file: resume.pdf, sessionId: "session123" }

// Chat
POST /api/conversations/:conversationId/messages
Body: { message: "Assess my resume", sessionId: "session123" }
```

---

## 🎯 Key Features

✅ **PDF Resume Upload** - Automatic processing pipeline  
✅ **Vector Search** - Semantic search using OpenAI + OpenSearch  
✅ **Smart Routing** - AI Refinery orchestrator handles intent  
✅ **Multiple Agents** - Search, Assessment, Jobs, Interview, General Career  
✅ **Session Management** - Per-user resume storage  
✅ **Full Stack** - Frontend → Backend → AI → Database

---

## 🔍 Custom Agents

All agents are defined in `agents.py`:

### 1. Resume Search Agent
```python
async def resume_search_agent(query: str):
    # Uses: OpenAI embeddings + AWS OpenSearch
    results = search_resume_content(query, session_id, k=5)
    return formatted_results
```

### 2. Resume Assessment Agent
```python
async def resume_assessment_agent(query: str):
    # Uses: AI Refinery (Llama-3.1-70B)
    response = await client.chat.completions.create(...)
    return analysis
```

### 3. Job Search Agent
```python
async def job_search_agent(query: str):
    # Uses: AI Refinery (Llama-3.1-70B)
    return job_search_guidance
```

### 4. Interview Prep Agent
```python
async def interview_prep_agent(query: str):
    # Uses: AI Refinery (Llama-3.1-70B)
    return interview_preparation
```

### 5. General Career Agent
```python
async def general_career_agent(query: str):
    # Uses: OpenAI (GPT-4)
    return general_guidance
```

---

## 📊 Data Flow

```
PDF Resume (User Upload)
    ↓
Text Extraction (pdfminer.six)
    ↓
Chunking (RecursiveCharacterTextSplitter)
    ↓
Embeddings (OpenAI text-embedding-3-large)
    ↓
AWS OpenSearch (knn_vector index)
    ↓
Vector Search (Semantic Similarity)
    ↓
AI Refinery Orchestrator (Intent Detection)
    ↓
Custom Agent (Llama-3.1-70B Processing)
    ↓
Response to User
```

---

## 🎓 Learn More

- [AI Refinery SDK](https://sdk.airefinery.accenture.com/)
- [AWS OpenSearch](https://docs.aws.amazon.com/opensearch-service/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)

---

**Built with:** AI Refinery SDK + AWS OpenSearch + OpenAI + Node.js + React 🚀
