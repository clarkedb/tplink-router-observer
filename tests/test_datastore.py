"""Tests for datastore implementations."""

import json
import tempfile
from pathlib import Path

import pytest

from router_stats_collector.datastore import FileDataStore, InMemoryDataStore


class TestInMemoryDataStore:
    """Tests for InMemoryDataStore."""

    @pytest.mark.asyncio
    async def test_write_and_read(self):
        """Test writing and reading stats."""
        store = InMemoryDataStore()

        # Write some stats
        stats1 = {"metric1": 100, "metric2": "value1"}
        stats2 = {"metric1": 200, "metric2": "value2"}

        await store.write(stats1)
        await store.write(stats2)

        # Read all stats
        all_stats = await store.read_all()

        assert len(all_stats) == 2
        assert "timestamp" in all_stats[0]
        assert all_stats[0]["metric1"] == 100
        assert all_stats[1]["metric1"] == 200

    @pytest.mark.asyncio
    async def test_empty_store(self):
        """Test reading from empty store."""
        store = InMemoryDataStore()
        all_stats = await store.read_all()
        assert all_stats == []

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing the store."""
        store = InMemoryDataStore()
        await store.write({"test": "data"})
        await store.close()
        # Should still be able to read after close for in-memory store
        all_stats = await store.read_all()
        assert len(all_stats) == 1


class TestFileDataStore:
    """Tests for FileDataStore."""

    @pytest.mark.asyncio
    async def test_write_and_read(self):
        """Test writing and reading stats to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_stats.jsonl"
            store = FileDataStore(file_path)

            # Write some stats
            stats1 = {"metric1": 100, "metric2": "value1"}
            stats2 = {"metric1": 200, "metric2": "value2"}

            await store.write(stats1)
            await store.write(stats2)

            # Read all stats
            all_stats = await store.read_all()

            assert len(all_stats) == 2
            assert "timestamp" in all_stats[0]
            assert all_stats[0]["metric1"] == 100
            assert all_stats[1]["metric1"] == 200

    @pytest.mark.asyncio
    async def test_file_persistence(self):
        """Test that data persists across store instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_stats.jsonl"

            # Write with first store instance
            store1 = FileDataStore(file_path)
            await store1.write({"metric": 100})
            await store1.close()

            # Read with second store instance
            store2 = FileDataStore(file_path)
            all_stats = await store2.read_all()

            assert len(all_stats) == 1
            assert all_stats[0]["metric"] == 100
            await store2.close()

    @pytest.mark.asyncio
    async def test_empty_file(self):
        """Test reading from empty file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "empty.jsonl"
            store = FileDataStore(file_path)
            all_stats = await store.read_all()
            assert all_stats == []

    @pytest.mark.asyncio
    async def test_creates_parent_directories(self):
        """Test that parent directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "subdir" / "nested" / "test.jsonl"
            store = FileDataStore(file_path)

            await store.write({"test": "data"})

            assert file_path.exists()
            assert file_path.parent.exists()

    @pytest.mark.asyncio
    async def test_json_lines_format(self):
        """Test that data is stored in JSON Lines format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.jsonl"
            store = FileDataStore(file_path)

            await store.write({"metric": 1})
            await store.write({"metric": 2})

            # Read raw file and verify format
            with open(file_path, "r") as f:
                lines = f.readlines()

            assert len(lines) == 2
            # Each line should be valid JSON
            for line in lines:
                data = json.loads(line)
                assert "timestamp" in data
                assert "metric" in data
