# Resume Processing Pipeline

This directory contains the resume PDF processing pipeline that extracts text, chunks it, generates embeddings, and stores them in AWS OpenSearch for semantic search.

## Files Overview

- `aws_opensearch.py` - AWS OpenSearch client for vector storage and retrieval
- `chunk.py` - PDF text extraction, chunking, and embedding generation
- `process_resume.py` - CLI script called by Node.js to process uploaded resumes
- `search_resume.py` - CLI script for semantic search of resume content
- `get_session_data.py` - CLI script to retrieve all data for a session

## Pipeline Flow

1. **Upload**: User uploads PDF via `/api/upload` endpoint
2. **Extract**: PDF text is extracted using pdfminer
3. **Section**: Text is split into logical resume sections (Education, Experience, etc.)
4. **Chunk**: Sections are chunked into smaller pieces for embedding
5. **Embed**: Each chunk is converted to a vector using OpenAI's text-embedding-3-large
6. **Store**: Chunks and embeddings are stored in AWS OpenSearch with session metadata
7. **Search**: Users can search resume content using semantic similarity

## Session Support

The pipeline supports session-based isolation:
- Each uploaded resume can be associated with a session ID
- Session IDs allow filtering search results to specific conversations
- Session data can be retrieved or deleted independently

## API Endpoints

### Upload Resume
```
POST /api/upload
Content-Type: multipart/form-data

Body:
- file: PDF file
- sessionId: (optional) session identifier

Response:
{
  "filename": "unique-filename.pdf",
  "originalName": "resume.pdf",
  "sessionId": "session-uuid",
  "status": "processed" | "processing_failed",
  "processedAt": "2024-01-01T00:00:00Z"
}
```

### Search Resume Content
```
POST /api/upload/search

Body:
{
  "query": "software engineer experience",
  "sessionId": "optional-session-id",
  "k": 5
}

Response:
{
  "results": [
    {
      "content": "relevant text chunk",
      "metadata": {...},
      "score": 0.85
    }
  ],
  "query": "software engineer experience",
  "sessionId": "session-id"
}
```

### Get Session Data
```
GET /api/upload/session/:sessionId

Response:
{
  "sessionId": "session-id",
  "data": {
    "chunks": [...],
    "total_chunks": 15
  }
}
```

## Environment Variables Required

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
OPENSEARCH_ENDPOINT=your-domain.region.es.amazonaws.com
OPENAI_API_KEY=your_openai_key
```

## Dependencies

Python packages (install via `pip install -r requirements.txt`):
- openai
- pdfminer.six
- langchain-text-splitters
- boto3
- opensearch-py
- requests-aws4auth
- python-dotenv

## OpenSearch Index Structure

The pipeline creates an index called `resume-vectors` with the following mapping:

```json
{
  "mappings": {
    "properties": {
      "content": {"type": "text"},
      "embedding": {
        "type": "knn_vector",
        "dimension": 3072,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil"
        }
      },
      "metadata": {
        "properties": {
          "session_id": {"type": "keyword"},
          "type": {"type": "keyword"},
          "filename": {"type": "keyword"},
          "created_at": {"type": "date"}
        }
      }
    }
  }
}
```

## Error Handling

- PDF extraction errors are caught and logged
- OpenSearch connection issues are handled gracefully
- Failed uploads return appropriate HTTP status codes
- Processing errors are reported in the upload response