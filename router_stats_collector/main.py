"""Main entry point for the router stats collector application."""

import asyncio
import logging
import signal
import sys

from router_stats_collector.collector import RouterStatsCollector
from router_stats_collector.config import Config
from router_stats_collector.datastore import (
    DataStore,
    FileDataStore,
    InMemoryDataStore,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def create_datastore(config: Config) -> DataStore:
    """Create a datastore based on configuration.

    Args:
        config: Application configuration.

    Returns:
        DataStore instance.
    """
    if config.datastore_type == "memory":
        logger.info("Using in-memory data store")
        return InMemoryDataStore()
    else:
        logger.info(f"Using file data store: {config.data_file_path or 'default path'}")
        return FileDataStore(config.data_file_path)


async def run_collector(config: Config) -> None:
    """Run the router stats collector.

    Args:
        config: Application configuration.
    """
    # Create datastore
    datastore = create_datastore(config)

    # Create collector
    collector = RouterStatsCollector(
        router_ip=config.router_ip,
        password=config.router_password,
        datastore=datastore,
        collection_interval=config.collection_interval,
    )

    # Setup signal handlers for graceful shutdown
    shutdown_event = asyncio.Event()

    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, initiating shutdown...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start collector
        await collector.start()

        logger.info("Router stats collector is running. Press Ctrl+C to stop.")

        # Wait for shutdown signal
        await shutdown_event.wait()

    except Exception as e:
        logger.error(f"Error running collector: {e}", exc_info=True)
        raise
    finally:
        # Stop collector
        await collector.stop()


def main() -> None:
    """Main entry point."""
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = Config.from_env()

        logger.info(f"Router IP: {config.router_ip}")
        logger.info(f"Collection interval: {config.collection_interval}s")
        logger.info(f"Datastore type: {config.datastore_type}")

        # Run the collector
        asyncio.run(run_collector(config))

    except KeyboardInterrupt:
        logger.info("Shutdown complete")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
