"""ChromaDB vector store manager for tactical scouting reports."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

from .chunker import TacticalChunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScoutingVectorStore:
    def __init__(
        self,
        persist_dir: Path | str = "data/chromadb",
        collection_name: str = "tactical_scouting_reports",
    ):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Tactical scouting notes and opposition analysis"},
        )

    def add_chunks(self, chunks: list[TacticalChunk]) -> int:
        """Upsert tactical chunks into ChromaDB."""
        if not chunks:
            return 0

        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [c.metadata for c in chunks]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info("Indexed %d chunks into ChromaDB collection '%s'", len(chunks), self.collection_name)
        return len(chunks)

    def search(
        self,
        query: str,
        n_results: int = 3,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Query ChromaDB with optional metadata pre-filtering (e.g. {'team': 'Liverpool'})."""
        query_params: dict[str, Any] = {
            "query_texts": [query],
            "n_results": n_results,
        }
        if metadata_filter:
            query_params["where"] = metadata_filter

        results = self.collection.query(**query_params)

        formatted = []
        if results and results.get("ids") and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                formatted.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    "distance": results["distances"][0][i] if results.get("distances") else None,
                })
        return formatted

    def count(self) -> int:
        """Return total chunks in collection."""
        return self.collection.count()

    def reset(self) -> None:
        """Clear the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(self.collection_name)
