import boto3
import json
import os
from typing import List, Dict, Any
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AWSOpenSearchClient:
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.host = os.getenv('OPENSEARCH_ENDPOINT')
        self.service = 'es'
        
        # Use IAM authentication (since IAM ARN is now set as master user)
        credentials = boto3.Session().get_credentials()
        self.awsauth = AWS4Auth(
            credentials.access_key, 
            credentials.secret_key, 
            self.region, 
            self.service, 
            session_token=credentials.token
        )
        
        # OpenSearch client
        self.client = OpenSearch(
            hosts=[{'host': self.host, 'port': 443}],
            http_auth=self.awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
        
        self.index_name = 'resume-vectors'
        self._create_index_if_not_exists()
    
    def _create_index_if_not_exists(self):
        """Create index with proper mapping for vector search"""
        if not self.client.indices.exists(index=self.index_name):
            mapping = {
                "settings": {
                    "index": {
                        "knn": True,
                        "knn.algo_param.ef_search": 100
                    }
                },
                "mappings": {
                    "properties": {
                        "content": {"type": "text"},
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": 3072,  # text-embedding-3-large dimension
                            "method": {
                                "name": "hnsw",
                                "space_type": "cosinesimil",
                                "engine": "lucene"
                            }
                        },
                        "metadata": {
                            "properties": {
                                "session_id": {"type": "keyword"},
                                "type": {"type": "keyword"},
                                "section": {"type": "keyword"},
                                "source": {"type": "keyword"},
                                "filename": {"type": "keyword"},
                                "created_at": {"type": "date"}
                            }
                        }
                    }
                }
            }
            
            self.client.indices.create(index=self.index_name, body=mapping)
            print(f"Created index: {self.index_name}")
    
    def store_resume_chunks(self, chunks_with_embeddings: List[Dict[str, Any]], session_id: str = None):
        """Store resume chunks with embeddings in OpenSearch"""
        actions = []
        
        for chunk_data in chunks_with_embeddings:
            doc = {
                "content": chunk_data["content"],
                "embedding": chunk_data["embedding"],
                "metadata": {
                    **chunk_data["metadata"],
                    "session_id": session_id,
                    "created_at": chunk_data.get("created_at", "2024-01-01T00:00:00Z")
                }
            }
            
            action = {
                "index": {
                    "_index": self.index_name,
                    "_id": chunk_data["id"]
                }
            }
            actions.append(action)
            actions.append(doc)
        
        # Bulk insert
        response = self.client.bulk(body=actions)
        
        if response.get('errors'):
            print(f"Errors during bulk insert: {response}")
            return False
        
        return True
    
    def search_resume_chunks(self, query_embedding: List[float], session_id: str = None, k: int = 5):
        """Search for similar resume chunks using vector similarity"""
        query_body = {
            "size": k,
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_embedding,
                                    "k": k
                                }
                            }
                        }
                    ]
                }
            },
            "_source": ["content", "metadata"]
        }
        
        # Add session filter if provided
        if session_id:
            query_body["query"]["bool"]["filter"] = [
                {"term": {"metadata.session_id.keyword": session_id}}
            ]
            print(f"[DEBUG OpenSearch] Searching with session filter: {session_id}")
        else:
            print(f"[DEBUG OpenSearch] Searching WITHOUT session filter")
        
        print(f"[DEBUG OpenSearch] Query body: {query_body}")
        response = self.client.search(index=self.index_name, body=query_body)
        print(f"[DEBUG OpenSearch] Search response hits: {response['hits']['total']['value']}")
        
        results = []
        for hit in response['hits']['hits']:
            results.append({
                "content": hit["_source"]["content"],
                "metadata": hit["_source"]["metadata"],
                "score": hit["_score"]
            })
        
        return results
    
    def delete_session_data(self, session_id: str):
        """Delete all resume data for a specific session"""
        query = {
            "query": {
                "term": {"metadata.session_id.keyword": session_id}
            }
        }
        
        response = self.client.delete_by_query(index=self.index_name, body=query)
        return response.get('deleted', 0)
    
    def get_session_chunks(self, session_id: str):
        """Get all chunks for a specific session"""
        query = {
            "query": {
                "term": {"metadata.session_id.keyword": session_id}
            },
            "size": 10000,  # Adjust based on expected chunk count
            "_source": ["content", "metadata"]
        }
        
        response = self.client.search(index=self.index_name, body=query)
        
        chunks = []
        for hit in response['hits']['hits']:
            chunks.append({
                "content": hit["_source"]["content"],
                "metadata": hit["_source"]["metadata"]
            })
        
        return chunks