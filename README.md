# Router Stats Collector

A modern Python application for collecting and storing statistics from TP-Link routers using the `tplinkrouterc6u` library.

## Features

- **Flexible Data Storage**: Abstract datastore interface with multiple implementations

  - In-memory storage for testing and temporary data
  - File-based storage (JSON Lines format) for persistent local data
  - Extensible design for future backends (e.g., InfluxDB)

- **Secure Configuration**: Environment-based configuration with secure password handling

  - Passwords can be set via environment variables
  - Interactive secure password prompt if not provided
  - `.env` file support for local development

- **Configurable Collection**: Adjustable data collection interval with sensible defaults

- **Production Ready**:
  - Docker support with optimized, small image size
  - Docker Compose for easy deployment
  - Non-root container user for security
  - Comprehensive test suite with pytest
  - CI/CD pipeline with GitHub Actions

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- TP-Link router with compatible firmware

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd deco
```

2. Install dependencies using uv:

```bash
uv sync
```

3. Create a `.env` file from the template:

```bash
cp .env.template .env
```

4. Edit `.env` with your router credentials:

```bash
ROUTER_IP=192.168.1.1
ROUTER_PASSWORD=your_password
COLLECTION_INTERVAL=60
DATASTORE_TYPE=file
```

### Running the Application

#### Local Execution

```bash
# With .env file
router-collector

# Or with environment variables
ROUTER_IP=192.168.1.1 ROUTER_PASSWORD=mypassword router-collector

# Or let it prompt for password
ROUTER_IP=192.168.1.1 router-collector
```

#### Docker

Build and run with Docker:

```bash
# Build the image
docker build -t router-stats-collector .

# Run the container
docker run -d \
  -e ROUTER_IP=192.168.1.1 \
  -e ROUTER_PASSWORD=your_password \
  -e COLLECTION_INTERVAL=60 \
  -v $(pwd)/data:/app/data \
  router-stats-collector
```

#### Docker Compose

The easiest way to run in production:

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Configuration

All configuration is done through environment variables:

| Variable              | Required | Default                   | Description                        |
| --------------------- | -------- | ------------------------- | ---------------------------------- |
| `ROUTER_IP`           | Yes      | -                         | IP address of your TP-Link router  |
| `ROUTER_PASSWORD`     | Yes\*    | -                         | Admin password for the router      |
| `COLLECTION_INTERVAL` | No       | 60                        | Collection interval in seconds     |
| `DATASTORE_TYPE`      | No       | file                      | Datastore type: `memory` or `file` |
| `DATA_FILE_PATH`      | No       | ./data/router_stats.jsonl | Path for file-based storage        |

\*If `ROUTER_PASSWORD` is not provided via environment variable, the application will prompt for it securely.

## Data Storage

### File-Based Storage

Data is stored in JSON Lines format (`.jsonl`), with one JSON object per line. Each entry includes:

```json
{
  "timestamp": "2025-11-07T12:00:00.000000",
  "firmware": {"version": "1.0.0", ...},
  "status": {"status": "online", ...},
  "ipv4_status": {"ip": "192.168.1.1", ...},
  "connected_devices": 5,
  "clients": [...]
}
```

### In-Memory Storage

Useful for testing or when you don't need data persistence:

```bash
DATASTORE_TYPE=memory router-collector
```

## Development

### Setting Up Development Environment

```bash
# Install with dev dependencies
uv sync --dev
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=router_stats_collector --cov-report=html

# Run specific test file
pytest tests/test_datastore.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Install ruff for linting
uv sync --dev

# Run linter
ruff check router_stats_collector tests

# Run formatter
ruff format router_stats_collector tests
```

## Architecture

### Project Structure

```
deco/
├── router_stats_collector/
│   ├── __init__.py
│   ├── collector.py      # Stats collection logic
│   ├── config.py         # Configuration management
│   ├── datastore.py      # Abstract datastore interface
│   └── main.py           # Application entry point
├── tests/
│   ├── test_collector.py
│   ├── test_config.py
│   └── test_datastore.py
├── .github/
│   └── workflows/
│       └── ci.yml        # CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml        # Project dependencies
├── .env.example          # Example configuration
└── README.md
```

### Datastore Interface

The abstract `DataStore` class allows for easy extension:

```python
class DataStore(ABC):
    @abstractmethod
    async def write(self, stats: Dict[str, Any]) -> None:
        """Write router stats to the data store."""
        pass

    @abstractmethod
    async def read_all(self) -> List[Dict[str, Any]]:
        """Read all stored statistics."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the data store and cleanup resources."""
        pass
```

To add a new backend (e.g., InfluxDB):

1. Create a new class inheriting from `DataStore`
2. Implement the required methods
3. Update the factory in `main.py`

## CI/CD

The project includes a GitHub Actions workflow that:

- Runs tests on Python 3.11 and 3.12
- Generates coverage reports
- Builds and validates the Docker image
- Runs linting checks

## Security Considerations

- Passwords are never logged or exposed
- Container runs as non-root user
- Sensitive files are excluded via `.gitignore`
- Environment variables are the recommended way to pass credentials

## Troubleshooting

### Connection Issues

If you can't connect to your router:

1. Verify the router IP is correct
2. Ensure you can ping the router
3. Check that the password is correct
4. Verify the router firmware is compatible with `tplinkrouterc6u`

### Permission Errors

When using Docker with mounted volumes:

```bash
# Create data directory with correct permissions
mkdir -p data
chmod 777 data  # Or use specific user permissions
```

## Future Enhancements

- [ ] InfluxDB datastore implementation
- [ ] Prometheus metrics exporter
- [ ] Web dashboard for visualization
- [ ] Email/Slack alerts for router issues
- [ ] Support for multiple routers
- [ ] Historical data analysis

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and questions:

- GitHub Issues: [Create an issue](<repository-url>/issues)
- Documentation: See this README
- TP-Link Router Library: [tplinkrouterc6u](https://github.com/AlexandrErohin/TP-Link-Archer-C6U)
