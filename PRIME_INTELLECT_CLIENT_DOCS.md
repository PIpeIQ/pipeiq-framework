# Prime Intellect Client

An async Python client library for the Prime Intellect REST API. This library provides idiomatic async/await support for checking GPU availability and pricing across multiple cloud providers, including both single-node instances and multi-node clusters.

## Features

- 🚀 **Async/await support** using aiohttp
- 🔍 **GPU availability search** across providers
- 🏗️ **Cluster availability** for multi-node deployments
- 🏷️ **Type-safe** with dataclasses and enums  
- 🛡️ **Comprehensive error handling**
- 📊 **Resource filtering** by region, GPU type, count, etc.
- 🔧 **Easy to use** context manager API

## Installation

```bash
pip install prime-intellect-client
```

## Quick Start

```python
import asyncio
from prime_intellect_client import PrimeIntellectClient

async def main():
    async with PrimeIntellectClient("your-api-key") as client:
        # Get single-node GPU availability
        gpu_offers = await client.get_availability(
            gpu_type="H100_80GB",
            regions=["united_states", "canada"]
        )
        
        for offer in gpu_offers:
            print(f"Provider: {offer.provider}")
            print(f"Price: ${offer.prices.on_demand}/hr")
            print(f"Stock: {offer.stock_status}")
            print("---")

asyncio.run(main())
```

## API Methods

### GPU Availability

Get availability for single-node GPU instances:

```python
async with PrimeIntellectClient("your-api-key") as client:
    offers = await client.get_availability(
        gpu_type="H100_80GB",
        regions=["united_states"],
        gpu_count=1,
        security="secure_cloud"
    )
```

### Cluster Availability

Get availability for multi-node cluster deployments:

```python
async with PrimeIntellectClient("your-api-key") as client:
    cluster_offers = await client.get_cluster_availability(
        gpu_type="H100_80GB",
        gpu_count=16,
        regions=["united_states"]
    )
    
    for cluster in cluster_offers:
        print(f"GPU Count: {cluster.gpu_count}")
        print(f"Provider: {cluster.provider}")
        print(f"Price: ${cluster.prices.on_demand}/hr")
        if cluster.interconnect:
            print(f"Interconnect: {cluster.interconnect} Gbps")
```

## Filtering Options

Both `get_availability()` and `get_cluster_availability()` support these parameters:

- **regions**: List of regions (e.g., `["united_states", "canada", "eu_west"]`)
- **gpu_type**: GPU model (e.g., `"H100_80GB"`, `"A100_80GB"`)
- **gpu_count**: Number of GPUs needed
- **socket**: Socket type (e.g., `"PCIe"`, `"SXM5"`)
- **security**: `"secure_cloud"` or `"community_cloud"`

## Response Objects

All methods return lists of `GPUAvailability` objects with these fields:

```python
@dataclass
class GPUAvailability:
    cloud_id: str                           # Provider's instance ID
    gpu_type: str                          # GPU model
    provider: Optional[Provider]           # Cloud provider enum
    gpu_count: Optional[int]               # Number of GPUs
    data_center: Optional[str]             # Location/datacenter
    country: Optional[str]                 # Country code
    stock_status: Optional[StockStatus]    # Availability status
    prices: Optional[Pricing]              # Cost information
    interconnect: Optional[int]            # Network speed (Gbps)
    interconnect_type: Optional[str]       # Network type
    socket: Optional[SocketType]           # Socket type enum
    security: Optional[SecurityType]       # Security type enum
    gpu_memory: Optional[int]              # GPU memory in GB
    # ... additional fields for disk, vcpu, memory specs
```

## Error Handling

```python
from prime_intellect_client import (
    ValidationError,
    AuthenticationError, 
    APIError,
    NetworkError,
    RateLimitError
)

try:
    offers = await client.get_availability(gpu_type="H100_80GB")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except APIError as e:
    print(f"API error: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
```

## Use Cases

### Find Cheapest GPU
```python
offers = await client.get_availability(gpu_type="H100_80GB")
cheapest = min(offers, key=lambda x: x.prices.on_demand or float('inf'))
print(f"Cheapest: {cheapest.provider} at ${cheapest.prices.on_demand}/hr")
```

### Multi-Node Clusters
```python
clusters = await client.get_cluster_availability(
    gpu_type="H100_80GB", 
    gpu_count=16
)
for cluster in clusters:
    print(f"{cluster.gpu_count}x H100_80GB - ${cluster.prices.on_demand}/hr")
```

### Compare Regions
```python
us_offers = await client.get_availability(regions=["united_states"])
eu_offers = await client.get_availability(regions=["eu_west", "eu_east"])
```

## Requirements

- Python 3.9+
- aiohttp (automatically installed)
- Valid Prime Intellect API key

## Getting Your API Key

1. Sign up at [Prime Intellect](https://primeintellect.ai)
2. Navigate to your dashboard
3. Generate an API key in the API section
4. Use the key in your client initialization

## API Documentation

For complete API documentation:
- [Prime Intellect Docs](https://docs.primeintellect.ai)
- [API Reference](https://docs.primeintellect.ai/api-reference)
- [Availability API](https://docs.primeintellect.ai/api-reference/availability/get-gpu-availability)
- [Cluster API](https://docs.primeintellect.ai/api-reference/availability/get-cluster-availability)

## Example Integration

**requirements.txt:**
```
prime-intellect-client>=0.1.0
```

**main.py:**
```python
import asyncio
from prime_intellect_client import PrimeIntellectClient

async def find_best_gpu():
    async with PrimeIntellectClient("your-api-key") as client:
        offers = await client.get_availability(gpu_type="H100_80GB")
        if offers:
            best = min(offers, key=lambda x: x.prices.on_demand or float('inf'))
            print(f"Best deal: {best.provider} - ${best.prices.on_demand}/hr")
        else:
            print("No offers found")

if __name__ == "__main__":
    asyncio.run(find_best_gpu())
```

## Support

For questions and support:
- [Prime Intellect Docs](https://docs.primeintellect.ai)
- [API Reference](https://docs.primeintellect.ai/api-reference)

## License

MIT License 