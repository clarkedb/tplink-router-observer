"""Abstract data store interface and implementations."""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class DataStore(ABC):
    """Abstract base class for data stores."""

    @abstractmethod
    async def write(self, stats: Dict[str, Any]) -> None:
        """Write router stats to the data store.

        Args:
            stats: Dictionary containing router statistics with timestamp.
        """
        pass

    @abstractmethod
    async def read_all(self) -> List[Dict[str, Any]]:
        """Read all stored statistics.

        Returns:
            List of all stored statistics dictionaries.
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the data store and cleanup resources."""
        pass


class InMemoryDataStore(DataStore):
    """In-memory data store implementation."""

    def __init__(self):
        """Initialize the in-memory data store."""
        self._data: List[Dict[str, Any]] = []

    async def write(self, stats: Dict[str, Any]) -> None:
        """Write router stats to memory.

        Args:
            stats: Dictionary containing router statistics with timestamp.
        """
        stats_with_timestamp = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **stats,
        }
        self._data.append(stats_with_timestamp)

    async def read_all(self) -> List[Dict[str, Any]]:
        """Read all stored statistics from memory.

        Returns:
            List of all stored statistics dictionaries.
        """
        return self._data.copy()

    async def close(self) -> None:
        """Close the data store and cleanup resources."""
        # No cleanup needed for in-memory store
        pass


class FileDataStore(DataStore):
    """File-based data store implementation using JSON Lines format."""

    def __init__(self, file_path: str | Path | None = None):
        """Initialize the file data store.

        Args:
            file_path: Path to the data file. If None, uses DATA_FILE_PATH env var
                      or defaults to './data/router_stats.jsonl'
        """
        if file_path is None:
            file_path = os.getenv("DATA_FILE_PATH", "./data/router_stats.jsonl")

        self.file_path = Path(file_path)
        # Create parent directories if they don't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not self.file_path.exists():
            self.file_path.touch()

    async def write(self, stats: Dict[str, Any]) -> None:
        """Write router stats to file in JSON Lines format.

        Args:
            stats: Dictionary containing router statistics with timestamp.
        """
        stats_with_timestamp = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **stats,
        }

        with self.file_path.open("a") as f:
            f.write(json.dumps(stats_with_timestamp) + "\n")

    async def read_all(self) -> List[Dict[str, Any]]:
        """Read all stored statistics from file.

        Returns:
            List of all stored statistics dictionaries.
        """
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            return []

        data = []
        with self.file_path.open("r") as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))

        return data

    async def close(self) -> None:
        """Close the data store and cleanup resources."""
        # No explicit cleanup needed for file-based store
        pass
