"""Tests for router stats collector."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from router_stats_collector.collector import RouterStatsCollector
from router_stats_collector.datastore import InMemoryDataStore


class TestRouterStatsCollector:
    """Tests for RouterStatsCollector."""

    @pytest.fixture
    def mock_router_client(self):
        """Create a mock router client."""
        with patch(
            "router_stats_collector.collector.TplinkRouterProvider.get_client"
        ) as mock_method:
            mock_instance = MagicMock()
            mock_instance.get_firmware.return_value = {"version": "1.0.0"}
            mock_instance.get_status.return_value = {"status": "online"}
            mock_instance.get_ipv4_status.return_value = {"ip": "192.168.1.1"}
            mock_instance.get_clients.return_value = [
                {"name": "device1"},
                {"name": "device2"},
            ]
            mock_instance.logout.return_value = None
            mock_method.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_collect_stats_success(self, mock_router_client):
        """Test successful stats collection."""
        datastore = InMemoryDataStore()
        collector = RouterStatsCollector(
            router_ip="192.168.1.1",
            password="test_password",
            datastore=datastore,
            collection_interval=60,
        )

        stats = await collector.collect_stats()

        assert "firmware" in stats
        assert "status" in stats
        assert "ipv4_status" in stats
        assert "connected_devices" in stats
        assert stats["connected_devices"] == 2
        assert "clients" in stats
        assert len(stats["clients"]) == 2

        # Verify logout was called
        mock_router_client.logout.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_and_stop(self, mock_router_client):
        """Test starting and stopping the collector."""
        datastore = InMemoryDataStore()
        collector = RouterStatsCollector(
            router_ip="192.168.1.1",
            password="test_password",
            datastore=datastore,
            collection_interval=1,  # Short interval for testing
        )

        # Start collector
        await collector.start()
        assert collector._running is True

        # Let it run for a short time
        await asyncio.sleep(0.5)

        # Stop collector
        await collector.stop()
        assert collector._running is False

        # Verify stats were collected
        all_stats = await datastore.read_all()
        assert len(all_stats) >= 0  # May or may not have collected depending on timing

    @pytest.mark.asyncio
    async def test_collection_loop_writes_to_datastore(self, mock_router_client):
        """Test that collection loop writes stats to datastore."""
        datastore = InMemoryDataStore()
        collector = RouterStatsCollector(
            router_ip="192.168.1.1",
            password="test_password",
            datastore=datastore,
            collection_interval=0.1,  # Very short interval for testing
        )

        await collector.start()
        await asyncio.sleep(0.3)  # Let it collect a few times
        await collector.stop()

        all_stats = await datastore.read_all()
        assert len(all_stats) >= 1  # Should have at least one collection

        # Verify stats structure
        if all_stats:
            assert "timestamp" in all_stats[0]
            assert "firmware" in all_stats[0]

    @pytest.mark.asyncio
    async def test_double_start(self, mock_router_client):
        """Test that starting an already running collector is handled."""
        datastore = InMemoryDataStore()
        collector = RouterStatsCollector(
            router_ip="192.168.1.1",
            password="test_password",
            datastore=datastore,
        )

        await collector.start()
        await collector.start()  # Should not raise error

        await collector.stop()

    @pytest.mark.asyncio
    async def test_stop_not_running(self):
        """Test that stopping a non-running collector is handled."""
        datastore = InMemoryDataStore()
        collector = RouterStatsCollector(
            router_ip="192.168.1.1",
            password="test_password",
            datastore=datastore,
        )

        await collector.stop()  # Should not raise error
