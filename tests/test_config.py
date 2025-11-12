"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest

from router_stats_collector.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_from_env_with_all_values(self):
        """Test loading config from environment with all values set."""
        env_vars = {
            "ROUTER_IP": "192.168.1.1",
            "ROUTER_PASSWORD": "test_password",
            "COLLECTION_INTERVAL": "30",
            "DATASTORE_TYPE": "memory",
            "DATA_FILE_PATH": "/tmp/test.jsonl",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config.from_env()

            assert config.router_ip == "192.168.1.1"
            assert config.router_password == "test_password"
            assert config.collection_interval == 30
            assert config.datastore_type == "memory"
            assert config.data_file_path == "/tmp/test.jsonl"

    def test_from_env_with_defaults(self):
        """Test loading config with default values."""
        env_vars = {
            "ROUTER_IP": "192.168.1.1",
            "ROUTER_PASSWORD": "test_password",
        }

        # Clear conflicting env vars
        with patch.dict(
            os.environ,
            env_vars,
            clear=False,
        ):
            # Remove optional vars if they exist
            os.environ.pop("COLLECTION_INTERVAL", None)
            os.environ.pop("DATASTORE_TYPE", None)
            os.environ.pop("DATA_FILE_PATH", None)

            config = Config.from_env()

            assert config.router_ip == "192.168.1.1"
            assert config.router_password == "test_password"
            assert config.collection_interval == 60  # default
            assert config.datastore_type == "file"  # default
            assert config.data_file_path is None

    def test_from_env_missing_router_ip(self):
        """Test that missing ROUTER_IP raises ValueError."""
        env_vars = {
            "ROUTER_PASSWORD": "test_password",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            os.environ.pop("ROUTER_IP", None)
            with pytest.raises(ValueError, match="ROUTER_IP"):
                Config.from_env()

    def test_from_env_invalid_collection_interval(self):
        """Test that invalid COLLECTION_INTERVAL raises ValueError."""
        env_vars = {
            "ROUTER_IP": "192.168.1.1",
            "ROUTER_PASSWORD": "test_password",
            "COLLECTION_INTERVAL": "-10",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with pytest.raises(ValueError, match="COLLECTION_INTERVAL"):
                Config.from_env()

    def test_from_env_invalid_datastore_type(self):
        """Test that invalid DATASTORE_TYPE raises ValueError."""
        env_vars = {
            "ROUTER_IP": "192.168.1.1",
            "ROUTER_PASSWORD": "test_password",
            "DATASTORE_TYPE": "invalid",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with pytest.raises(ValueError, match="DATASTORE_TYPE"):
                Config.from_env()

    def test_from_env_prompts_for_password(self):
        """Test that password is prompted if not in environment."""
        env_vars = {
            "ROUTER_IP": "192.168.1.1",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            os.environ.pop("ROUTER_PASSWORD", None)
            with patch(
                "router_stats_collector.config.getpass",
                return_value="prompted_password",
            ):
                config = Config.from_env()
                assert config.router_password == "prompted_password"

    def test_from_env_empty_password_prompt(self):
        """Test that empty password prompt raises ValueError."""
        env_vars = {
            "ROUTER_IP": "192.168.1.1",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            os.environ.pop("ROUTER_PASSWORD", None)
            with patch("router_stats_collector.config.getpass", return_value=""):
                with pytest.raises(ValueError, match="password is required"):
                    Config.from_env()
