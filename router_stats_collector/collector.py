"""Router statistics collector."""

import asyncio
import logging
from typing import Any, Dict, Optional

from tplinkrouterc6u import TplinkRouterProvider

from router_stats_collector.datastore import DataStore

logger = logging.getLogger(__name__)


class RouterStatsCollector:
    """Collects statistics from a TP-Link router."""

    def __init__(
        self,
        router_ip: str,
        password: str,
        datastore: DataStore,
        collection_interval: int = 60,
    ):
        """Initialize the router stats collector.

        Args:
            router_ip: IP address of the TP-Link router.
            password: Admin password for the router.
            datastore: Data store instance to write stats to.
            collection_interval: Collection interval in seconds (default: 60).
        """
        self.router_ip = router_ip
        self.password = password
        self.datastore = datastore
        self.collection_interval = collection_interval
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def collect_stats(self) -> Dict[str, Any]:
        """Collect current statistics from the router.

        Returns:
            Dictionary containing router statistics.

        Raises:
            Exception: If unable to collect stats from the router.
        """
        try:
            # Create router client
            client = TplinkRouterProvider.get_client(self.router_ip, self.password)

            # Collect various statistics
            stats = {}

            # Get firmware info
            try:
                firmware = client.get_firmware()
                if firmware:
                    stats["firmware"] = firmware
            except Exception as e:
                logger.warning(f"Failed to get firmware info: {e}")

            # Get status info
            try:
                status = client.get_status()
                if status:
                    stats["status"] = status
            except Exception as e:
                logger.warning(f"Failed to get status info: {e}")

            # Get IPv4 status
            try:
                ipv4_status = client.get_ipv4_status()
                if ipv4_status:
                    stats["ipv4_status"] = ipv4_status
            except Exception as e:
                logger.warning(f"Failed to get IPv4 status: {e}")

            # Get connected devices count
            try:
                clients_list = client.get_clients()
                if clients_list:
                    stats["connected_devices"] = len(clients_list)
                    stats["clients"] = clients_list
            except Exception as e:
                logger.warning(f"Failed to get clients info: {e}")

            # Logout
            try:
                client.logout()
            except Exception as e:
                logger.warning(f"Failed to logout: {e}")

            logger.info(f"Collected stats: {len(stats)} metrics")
            return stats

        except Exception as e:
            logger.error(f"Error collecting router stats: {e}")
            raise

    async def _collection_loop(self) -> None:
        """Internal loop for periodic stats collection."""
        logger.info(
            f"Starting collection loop with interval: {self.collection_interval}s"
        )

        while self._running:
            try:
                # Collect and store stats
                stats = await self.collect_stats()
                await self.datastore.write(stats)
                logger.debug("Stats written to datastore")

            except Exception as e:
                logger.error(f"Error in collection loop: {e}")

            # Wait for next collection interval
            await asyncio.sleep(self.collection_interval)

    async def start(self) -> None:
        """Start the stats collection loop."""
        if self._running:
            logger.warning("Collector is already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._collection_loop())
        logger.info("Router stats collector started")

    async def stop(self) -> None:
        """Stop the stats collection loop."""
        if not self._running:
            logger.warning("Collector is not running")
            return

        logger.info("Stopping router stats collector...")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        await self.datastore.close()
        logger.info("Router stats collector stopped")
