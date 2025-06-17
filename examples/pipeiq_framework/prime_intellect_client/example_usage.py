import asyncio
import os
import sys

# Add the pipeiq_framework to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'pipeiq_framework'))

from prime_intellect_client import PrimeIntellectClient


async def main():
    # Initialize the client with your API key
    api_key = "your-api-key-here"  # Replace with your actual API key
    client = PrimeIntellectClient(api_key)
    
    async with client:
        # Get single GPU availability
        print("Getting H100 GPU availability...")
        offers = await client.get_availability(gpu_type="H100_80GB")
        print(f"Found {len(offers)} H100 offers")
        
        # Show first offer details
        if offers:
            offer = offers[0]
            print(f"First offer: {offer.cloud_id}")
            print(f"Provider: {offer.provider}")
            print(f"Price: ${offer.prices.on_demand}/hr" if offer.prices else "No pricing")
        
        print()
        
        # Get cluster availability
        print("Getting H100 cluster availability...")
        clusters = await client.get_cluster_availability(gpu_type="H100_80GB")
        print(f"Found {len(clusters)} cluster configurations")
        
        # Show first cluster details
        if clusters:
            cluster = clusters[0]
            print(f"First cluster: {cluster.cloud_id}")
            print(f"Provider: {cluster.provider}")
            print(f"GPU Count: {cluster.gpu_count}")
            print(f"Price: ${cluster.prices.on_demand}/hr" if cluster.prices else "No pricing")


if __name__ == "__main__":
    asyncio.run(main())
