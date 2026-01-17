"""
Postgres Checkpointer for LangGraph using psycopg2 (Sync).

This implementation bypasses the need for psycopg 3 (async) which causes
segmentation faults in some WSL2 environments. It implements the minimal
interface required by LangGraph's BaseCheckpointSaver.
"""
from typing import Any, AsyncIterator, Dict, Optional, Sequence, Tuple
from contextlib import contextmanager
import pickle
import psycopg2
from psycopg2.extras import Json
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    SerializerProtocol,
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

class PostgresSaver(BaseCheckpointSaver):
    def __init__(
        self,
        conn_string: str,
        serde: Optional[SerializerProtocol] = None,
    ):
        super().__init__(serde=serde or JsonPlusSerializer())
        self.conn_string = conn_string
        self._ensure_table()

    def _get_connection(self):
        return psycopg2.connect(self.conn_string)

    def _ensure_table(self):
        """Creates the checkpoints table if it doesn't exist."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    thread_id TEXT NOT NULL,
                    checkpoint_id TEXT NOT NULL,
                    parent_id TEXT,
                    checkpoint BYTEA NOT NULL,
                    metadata BYTEA NOT NULL,
                    PRIMARY KEY (thread_id, checkpoint_id)
                );
                """)
                conn.commit()

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Get the latest checkpoint for the given config."""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"].get("checkpoint_id")
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                if checkpoint_id:
                    cur.execute(
                        "SELECT checkpoint, parent_id, metadata FROM checkpoints WHERE thread_id = %s AND checkpoint_id = %s",
                        (thread_id, checkpoint_id)
                    )
                else:
                    cur.execute(
                        "SELECT checkpoint, parent_id, metadata FROM checkpoints WHERE thread_id = %s ORDER BY checkpoint_id DESC LIMIT 1",
                        (thread_id,)
                    )
                
                row = cur.fetchone()
                if not row:
                    return None
                    
                checkpoint_data, parent_id, metadata_data = row
                
                # Deserialize
                checkpoint = self.serde.loads(checkpoint_data)
                metadata = self.serde.loads(metadata_data)
                
                return CheckpointTuple(
                    config=config,
                    checkpoint=checkpoint,
                    metadata=metadata,
                    parent_config={
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_id": parent_id,
                        }
                    } if parent_id else None,
                )

    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """List checkpoints for the given config."""
        # Minimal implementation for now
        pass

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: Dict[str, Any],
    ) -> RunnableConfig:
        """Save a checkpoint."""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = checkpoint["id"]
        parent_id = config["configurable"].get("checkpoint_id")
        
        # Serialize
        checkpoint_data = self.serde.dumps(checkpoint)
        metadata_data = self.serde.dumps(metadata)
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO checkpoints (thread_id, checkpoint_id, parent_id, checkpoint, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (thread_id, checkpoint_id) 
                    DO UPDATE SET checkpoint = EXCLUDED.checkpoint, metadata = EXCLUDED.metadata;
                    """,
                    (thread_id, checkpoint_id, parent_id, checkpoint_data, metadata_data)
                )
                conn.commit()
                
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
            }
        }
