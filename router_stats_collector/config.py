"""Configuration management for the router stats collector."""

import os
from dataclasses import dataclass
from getpass import getpass
from typing import Literal

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Application configuration."""

    router_ip: str
    router_password: str
    collection_interval: int
    datastore_type: Literal["memory", "file"]
    data_file_path: str | None

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.

        Environment variables:
            ROUTER_IP: IP address of the router (required)
            ROUTER_PASSWORD: Admin password (optional, will prompt if not set)
            COLLECTION_INTERVAL: Collection interval in seconds (default: 60)
            DATASTORE_TYPE: Type of datastore - 'memory' or 'file' (default: 'file')
            DATA_FILE_PATH: Path to data file (only for file datastore)

        Returns:
            Config instance loaded from environment.

        Raises:
            ValueError: If required configuration is missing.
        """
        # Get router IP (required)
        router_ip = os.getenv("ROUTER_IP")
        if not router_ip:
            raise ValueError(
                "ROUTER_IP environment variable is required. "
                "Set it in .env file or export it in your shell."
            )

        # Get password (prompt if not in environment)
        router_password = os.getenv("ROUTER_PASSWORD")
        if not router_password:
            router_password = getpass("Enter router admin password: ")
            if not router_password:
                raise ValueError("Router password is required")

        # Get collection interval (default: 60 seconds)
        collection_interval = int(os.getenv("COLLECTION_INTERVAL", "60"))
        if collection_interval <= 0:
            raise ValueError("COLLECTION_INTERVAL must be a positive integer")

        # Get datastore type (default: file)
        datastore_type = os.getenv("DATASTORE_TYPE", "file").lower()
        if datastore_type not in ("memory", "file"):
            raise ValueError("DATASTORE_TYPE must be 'memory' or 'file'")

        # Get data file path (only relevant for file datastore)
        data_file_path = os.getenv("DATA_FILE_PATH")

        return cls(
            router_ip=router_ip,
            router_password=router_password,
            collection_interval=collection_interval,
            datastore_type=datastore_type,  # type: ignore
            data_file_path=data_file_path,
        )
