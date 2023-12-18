import logging
from typing import Iterable, List, Optional, Tuple
import uuid
from langchain.docstore.document import Document
from vocode import getenv
from vocode.streaming.vector_db.base_vector_db import VectorDB

from vocode.streaming.models.vector_db import SupabaseConfig
from langchain.vectorstores.supabase import SupabaseVectorStore

try:
    from supabase.client import create_client
except ImportError:
    raise ImportError(
        "You need to install the supabase client to use the Supabase vector database. "
        "You can install it with `pip install supabase`."
    )


logger = logging.getLogger(__name__)

class SupabaseVectorStoreDB(VectorDB):
    def __init__(self, config: SupabaseConfig, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.config = config
        self.supabase_url = getenv("SUPABASE_URL") or self.config.supbase_url
        self.supabase_key = getenv("SUPABASE_KEY") or self.config.supbase_key
        self.table_name = self.config.table_name
        self.query_name = self.config.query_name
        self.supabase = create_client(self.supabase_url, self.supabase_key)

    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None,
        namespace: Optional[str] = None,
    ) -> List[Tuple[Document, float]]:
        """Return supabase documents most similar to query, along with scores.

        Args:
            query: Text to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.
            filter: Dictionary of argument(s) to filter on metadata
            namespace: Namespace to search in. Default will search in '' namespace.

        Returns:
            List of Documents most similar to the query and score for each
        """
        # Embed the query
        query_embedding = await self.create_openai_embedding(query)

        # Prepare parameters for the match_documents RPC
        match_documents_params = dict(query_embedding=query_embedding, match_count=k)

        # Call the match_documents RPC
        response = self.supabase.rpc(self.query_name, params=match_documents_params).execute()
        if response.error:
            logger.error(f"Error fetching documents: {response.error}")
            return []

        docs = []
        for row in response.data:
            # Create Document object
            metadata = row["metadata"]
            text = metadata.pop(self._text_key)
            doc = Document(page_content=text, metadata=metadata)

            # Get similarity score
            score = row["similarity"]

            docs.append((doc, score))

        # Sort documents by score in descending order
        docs.sort(key=lambda x: x[1], reverse=True)

        # return docs List[Tuple[Document, float]]
        # docs = [
        #     (
        #         Document(
        #             page_content="Hello",
        #             metadata={"source": "test"},
        #             lc_kwargs={"page_content": "Hello"},
        #         ),
        #         0.5,
        #     ),
        #     (
        #         Document(
        #             page_content="Hello",
        #             metadata={"source": "test"},
        #             lc_kwargs={"page_content": "Hello"},
        #         ),
        #         0.5,
        #     ),
        #     (
        #         Document(
        #             page_content="Hello",
        #             metadata={"source": "test"},
        #             lc_kwargs={"page_content": "Hello"},
        #         ),
        #         0.5,
        #     ),
        #     (
        #         Document(
        #             page_content="Hello",
        #             metadata={"source": "test"},
        #             lc_kwargs={"page_content": "Hello"},
        #         ),
        #         0.5,
        #     ),
        # ]
        return docs