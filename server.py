from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import logging
from dotenv import load_dotenv
from bson import json_util
import json
from math import ceil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="price competitor")

# MongoDB setup
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, 
                    server_api=ServerApi('1'),
                    tls=True,
                    tlsAllowInvalidCertificates=True)

try:
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB!")
except Exception as e:
    logger.error(f"MongoDB connection error: {e}")
    raise

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class JsonRequest(BaseModel):
    data: Dict[str, Any]

# MongoDB collections
db = client['sample_mflix']
collection = db['circuitbreakers']

@app.post("/api/superbreakers")
async def superbreakers(request: JsonRequest):
    try:
        data = request.data
        logger.info(f"Received data: {data}")
        
        # Use SKU as unique identifier
        filter_query = {"product_code": data.get("specifications")["product_code"]}
        
        # Update or insert the document
        result = collection.update_one(
            filter=filter_query,
            update={"$set": data},
            upsert=True  # Create new document if not exists
        )
        
        return {
            "success": True,
            "message": "Data successfully upserted",
            "modified": result.modified_count,
            "upserted": result.upserted_id is not None
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/products')
async def search_products(request: JsonRequest):
    try:
        data = request.data
        page = data.get('page', 1)
        page_size = data.get('page_size', 10)
        skip = (page - 1) * page_size
        
        logger.info(f"Searching for SKU: {data.get('sku')}")
        
        # Get total count for search results
        total_count = collection.count_documents({"product_code": data["product_code"]})
        
        # Get paginated search results
        products = list(collection.find({"product_code": data["product_code"]})
                       .skip(skip)
                       .limit(page_size))
        
        # Calculate total pages 
        total_pages = ceil(total_count / page_size)
        
        # Convert to JSON-serializable format
        products_json = json.loads(json_util.dumps(products))
        
        return {
            'success': True,
            'products': products_json,
            'pagination': {
                'total': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api')
async def get_all_products(
    page: Optional[int] = Query(default=1, ge=1),
    page_size: Optional[int] = Query(default=10, ge=1, le=100)
):
    try:
        # Calculate skip value for pagination
        skip = (page - 1) * page_size
        
        # Get total count of documents
        total_count = collection.count_documents({})
        
        # Get paginated products
        products = list(collection.find({})
                       .skip(skip)
                       .limit(page_size))
        
        # Calculate total pages
        total_pages = ceil(total_count / page_size)
        
        # Convert to JSON-serializable format
        products_json = json.loads(json_util.dumps(products))
        
        return {
            'success': True,
            'products': products_json,
            'pagination': {
                'total': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
    except Exception as e:
        logger.error(f"Error fetching all products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))