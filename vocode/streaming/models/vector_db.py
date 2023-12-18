from enum import Enum
from typing import Optional
from .model import TypedModel

DEFAULT_EMBEDDINGS_MODEL = "text-embedding-ada-002"


class VectorDBType(str, Enum):
    BASE = "vector_db_base"
    PINECONE = "vector_db_pinecone"
    SUPABASE = "vector_db_supabase"


class VectorDBConfig(TypedModel, type=VectorDBType.BASE.value):
    embeddings_model: str = DEFAULT_EMBEDDINGS_MODEL


class PineconeConfig(VectorDBConfig, type=VectorDBType.PINECONE.value):
    index: str
    api_key: Optional[str] = None
    api_environment: Optional[str] = None
    top_k: int = 3

class SupabaseConfig(VectorDBConfig, type=VectorDBType.SUPABASE.value):
    """
    This class is a configuration for the Supabase Vector Database.
    It inherits from the VectorDBConfig class and is of type SUPABASE.
    """
    supbase_url: str  # The URL of the Supabase instance
    supbase_key: str  # The key to authenticate with the Supabase instance
    table_name: str  # The name of the table in the Supabase database
    query_name: str  # The name of the query to be executed on the Supabase database