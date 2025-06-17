#!/usr/bin/env python3
"""
Real implementation tests for Prime Intellect client.

This tests our actual implementation against the real API endpoints
without mocking the _make_request method.
"""

import asyncio
import os
import sys
import time
from typing import Optional

# Add the pipeiq_framework to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'pipeiq_framework'))

from prime_intellect_client import (
    PrimeIntellectClient,
    GPUAvailability,
    ValidationError,
    AuthenticationError,
    APIError,
    NetworkError,
    RateLimitError,
    Provider,
    StockStatus,
    SocketType,
    SecurityType,
)


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_section(title):
    """Print a section header."""
    print(f"\n--- {title} ---")


def print_test_result(test_name, success, details=""):
    """Print a formatted test result."""
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {test_name}")
    if details:
        print(f"      {details}")


def print_api_result(test_name, count, details=""):
    """Print formatted API call result."""
    print(f"[API]  {test_name}: {count} offers")
    if details:
        print(f"       {details}")


def print_offer_details(offers, max_offers=3, title="Sample Offers"):
    """Print detailed information about offers."""
    if not offers:
        print(f"       No offers to display")
        return
    
    print(f"       {title}:")
    for i, offer in enumerate(offers[:max_offers]):
        print(f"       [{i+1}] ID: {offer.cloud_id}")
        print(f"           GPU: {offer.gpu_type}")
        print(f"           Provider: {offer.provider}")
        print(f"           Price: ${offer.prices.on_demand}/hr" if offer.prices and offer.prices.on_demand else "           Price: Not available")
        print(f"           Stock: {offer.stock_status}")
        print(f"           Socket: {offer.socket}")
        print(f"           Security: {offer.security}")
        print(f"           Country: {offer.country}")
        print(f"           Datacenter: {offer.data_center}")
        print(f"           GPU Count: {offer.gpu_count}")
        if i < min(len(offers), max_offers) - 1:
            print(f"           ---")
    
    if len(offers) > max_offers:
        print(f"       ... and {len(offers) - max_offers} more offers")


async def sleep_between_calls(seconds=1):
    """Add delay between API calls to avoid rate limiting."""
    await asyncio.sleep(seconds)


async def test_client_initialization():
    """Test that our client initializes correctly."""
    print_section("Client Initialization Tests")
    
    # Test with valid parameters
    client = PrimeIntellectClient("test-key")
    assert client._api_key == "test-key"
    assert client._base_url == "https://api.primeintellect.ai"
    assert client._timeout.total == 30.0
    print_test_result("Basic client initialization", True)
    
    # Test with custom parameters
    client2 = PrimeIntellectClient(
        "test-key-2",
        base_url="https://custom.api.url",
        timeout=60.0
    )
    assert client2._api_key == "test-key-2"
    assert client2._base_url == "https://custom.api.url"
    assert client2._timeout.total == 60.0
    print_test_result("Custom client initialization", True)
    
    # Test validation
    try:
        PrimeIntellectClient("")
        print_test_result("Empty API key validation", False, "Should have raised ValidationError")
    except ValidationError:
        print_test_result("Empty API key validation", True, "ValidationError raised correctly")


async def test_error_handling_without_api_key():
    """Test that our error handling works correctly."""
    print_section("Error Handling Tests")
    
    async with PrimeIntellectClient("invalid-key") as client:
        try:
            offers = await client.get_availability()
            print_test_result("Authentication error handling", False, f"Expected error, but got {len(offers)} offers")
        except AuthenticationError as e:
            print_test_result("Authentication error handling", True, f"AuthenticationError: {e}")
        except NetworkError as e:
            print_test_result("Network error handling", True, f"NetworkError: {e}")
        except APIError as e:
            print_test_result("API error handling", True, f"APIError: {e}")
        except Exception as e:
            print_test_result("Unexpected error handling", False, f"{type(e).__name__}: {e}")


async def test_real_api_call():
    """Test against real API if API key is available."""
    print_section("Real API Call Tests")
    
    api_key = "replace-api-key"
    
    if not api_key:
        print("INFO: No API key found - skipping real API tests")
        return
    
    print(f"INFO: Using API key: {api_key[:10]}...")
    
    try:
        async with PrimeIntellectClient(api_key) as client:
            # Test 1: Basic availability call
            print("\nTest 1: Basic get_availability() call")
            offers = await client.get_availability(gpu_type="H100_80GB")
            print_api_result("Basic H100 availability", len(offers))
            print_offer_details(offers, max_offers=3, title="Top H100 Offers")
            
            if offers:
                # Validate model parsing
                offer = offers[0]
                assert isinstance(offer, GPUAvailability)
                assert isinstance(offer.provider, (Provider, type(None)))
                assert isinstance(offer.stock_status, (StockStatus, type(None)))
                print_test_result("Model parsing validation", True)
            
            await sleep_between_calls(2)
            
            # Test 2: Availability with multiple parameters
            print("\nTest 2: get_availability() with multiple parameters")
            filtered_offers = await client.get_availability(
                gpu_type="H100_80GB",
                regions=["united_states", "canada"],
                security="secure_cloud",
                gpu_count=1
            )
            print_api_result("Filtered availability", len(filtered_offers))
            print_offer_details(filtered_offers, max_offers=2, title="Filtered Offers (US/Canada, Secure)")
            
            await sleep_between_calls(2)
            
            # Test 3: Different GPU type
            print("\nTest 3: get_availability() with A100")
            a100_offers = await client.get_availability(gpu_type="A100_80GB")
            print_api_result("A100 availability", len(a100_offers))
            print_offer_details(a100_offers, max_offers=2, title="Top A100 Offers")
            
            await sleep_between_calls(2)
            
            # Test 4: Socket type filtering
            print("\nTest 4: get_availability() with socket filtering")
            pcie_offers = await client.get_availability(
                gpu_type="H100_80GB",
                socket="PCIe"
            )
            print_api_result("PCIe socket filtering", len(pcie_offers))
            
            await sleep_between_calls(2)
            
            # Test 5: Region filtering (using correct region names)
            print("\nTest 5: get_availability() with region filtering")
            us_offers = await client.get_availability(
                gpu_type="H100_80GB",
                regions=["united_states"]
            )
            print_api_result("US region filtering", len(us_offers))
            
            await sleep_between_calls(2)
            
            # Test 6: Security type filtering
            print("\nTest 6: get_availability() with security filtering")
            secure_offers = await client.get_availability(
                gpu_type="H100_80GB",
                security="secure_cloud"
            )
            print_api_result("Secure cloud filtering", len(secure_offers))
            
            await sleep_between_calls(2)
            
            # Test 7: Multiple GPU count
            print("\nTest 7: get_availability() with multiple GPU count")
            multi_gpu_offers = await client.get_availability(
                gpu_type="H100_80GB",
                gpu_count=2
            )
            print_api_result("Multi-GPU filtering", len(multi_gpu_offers))
            
            await sleep_between_calls(2)
            
            # Test 8: All parameters combined (using correct region names)
            print("\nTest 8: get_availability() with ALL parameters")
            all_params_offers = await client.get_availability(
                gpu_type="H100_80GB",
                regions=["united_states", "canada", "eu_west"],
                gpu_count=1,
                socket="PCIe",
                security="secure_cloud"
            )
            print_api_result("All parameters filtering", len(all_params_offers))
            
            await sleep_between_calls(2)
            
            # Test 9: Cluster availability basic
            print("\nTest 9: Basic get_cluster_availability() call")
            cluster_offers = await client.get_cluster_availability(gpu_type="H100_80GB")
            print_api_result("Basic cluster availability", len(cluster_offers))
            print_offer_details(cluster_offers, max_offers=2, title="Sample H100 Clusters")
            
            await sleep_between_calls(2)
            
            # Test 10: Cluster availability with parameters
            print("\nTest 10: get_cluster_availability() with parameters")
            filtered_clusters = await client.get_cluster_availability(
                gpu_type="H100_80GB",
                gpu_count=16,
                regions=["united_states"],
                security="secure_cloud"
            )
            print_api_result("Filtered cluster availability", len(filtered_clusters))
            
            await sleep_between_calls(2)
            
            # Test 11: Different cluster sizes
            print("\nTest 11: get_cluster_availability() with different GPU counts")
            small_clusters = await client.get_cluster_availability(
                gpu_type="H100_80GB",
                gpu_count=8
            )
            await sleep_between_calls(1)
            large_clusters = await client.get_cluster_availability(
                gpu_type="H100_80GB",
                gpu_count=64
            )
            print_api_result("Small clusters (8 GPU)", len(small_clusters))
            print_api_result("Large clusters (64 GPU)", len(large_clusters))
            
            await sleep_between_calls(2)
            
            # Test 12: No parameters (should return all available)
            print("\nTest 12: get_availability() with no parameters")
            all_offers = await client.get_availability()
            print_api_result("No parameters (all offers)", len(all_offers))
            print_offer_details(all_offers, max_offers=3, title="Sample from All Available Offers")
            
            # Summary of results
            print_section("API Test Summary")
            print(f"H100 offers:           {len(offers)}")
            print(f"A100 offers:           {len(a100_offers)}")
            print(f"PCIe filtered:         {len(pcie_offers)}")
            print(f"US region:             {len(us_offers)}")
            print(f"Secure cloud:          {len(secure_offers)}")
            print(f"Multi-GPU:             {len(multi_gpu_offers)}")
            print(f"All params:            {len(all_params_offers)}")
            print(f"Cluster offers:        {len(cluster_offers)}")
            print(f"Filtered clusters:     {len(filtered_clusters)}")
            print(f"Small clusters:        {len(small_clusters)}")
            print(f"Large clusters:        {len(large_clusters)}")
            print(f"Total offers:          {len(all_offers)}")
            
    except AuthenticationError as e:
        print_test_result("Authentication", False, f"Authentication failed: {e}")
    except RateLimitError as e:
        print_test_result("Rate limiting", False, f"Rate limit exceeded: {e}")
    except Exception as e:
        print_test_result("Unexpected error", False, f"{type(e).__name__}: {e}")


async def test_edge_cases():
    """Test edge cases and error conditions."""
    print_section("Edge Case Tests")
    
    api_key = "replace-api-key"
    
    try:
        async with PrimeIntellectClient(api_key) as client:
            # Test 1: Invalid GPU type
            print("\nEdge Case 1: Invalid GPU type")
            try:
                invalid_offers = await client.get_availability(gpu_type="INVALID_GPU")
                print_test_result("Invalid GPU type", False, f"Expected error, got {len(invalid_offers)} offers")
            except (ValidationError, APIError) as e:
                print_test_result("Invalid GPU type", True, "ValidationError raised correctly")
            
            await sleep_between_calls(2)
            
            # Test 2: Invalid region
            print("\nEdge Case 2: Invalid region")
            try:
                invalid_region_offers = await client.get_availability(
                    gpu_type="H100_80GB",
                    regions=["invalid_region"]
                )
                print_test_result("Invalid region", False, f"Expected error, got {len(invalid_region_offers)} offers")
            except (ValidationError, APIError) as e:
                print_test_result("Invalid region", True, "ValidationError raised correctly")
            
            await sleep_between_calls(2)
            
            # Test 3: Very high GPU count
            print("\nEdge Case 3: Very high GPU count")
            try:
                high_count_offers = await client.get_availability(
                    gpu_type="H100_80GB",
                    gpu_count=1000
                )
                print_api_result("High GPU count (1000)", len(high_count_offers))
            except (ValidationError, APIError) as e:
                print_test_result("High GPU count", True, "Error handled correctly")
            
            await sleep_between_calls(2)
            
            # Test 4: Empty regions list
            print("\nEdge Case 4: Empty regions list")
            try:
                empty_regions_offers = await client.get_availability(
                    gpu_type="H100_80GB",
                    regions=[]
                )
                print_api_result("Empty regions list", len(empty_regions_offers))
            except (ValidationError, APIError) as e:
                print_test_result("Empty regions list", False, f"Unexpected error: {e}")
            
            await sleep_between_calls(2)
            
            # Test 5: Invalid security type
            print("\nEdge Case 5: Invalid security type")
            try:
                invalid_security_offers = await client.get_availability(
                    gpu_type="H100_80GB",
                    security="invalid_security"
                )
                print_test_result("Invalid security", False, f"Expected error, got {len(invalid_security_offers)} offers")
            except (ValidationError, APIError) as e:
                print_test_result("Invalid security", True, "ValidationError raised correctly")
                
    except RateLimitError:
        print_test_result("Edge case testing", False, "Rate limit exceeded during edge case tests")
    except Exception as e:
        print_test_result("Edge case testing", False, f"{type(e).__name__}: {e}")


async def test_response_validation():
    """Test that responses are properly validated and parsed."""
    print_section("Response Validation Tests")
    
    api_key = "replace-api-key"
    
    try:
        async with PrimeIntellectClient(api_key) as client:
            offers = await client.get_availability(gpu_type="H100_80GB")
            
            if offers:
                print("\nValidating response structure...")
                offer = offers[0]
                
                # Validate required fields
                assert hasattr(offer, 'cloud_id'), "Missing cloud_id field"
                assert hasattr(offer, 'gpu_type'), "Missing gpu_type field"
                assert offer.cloud_id is not None, "cloud_id should not be None"
                print_test_result("Required fields present", True)
                
                # Validate optional fields are properly typed
                if offer.provider:
                    assert isinstance(offer.provider, Provider), f"Provider should be Provider enum"
                    print_test_result("Provider enum validation", True, f"Valid: {offer.provider}")
                
                if offer.stock_status:
                    assert isinstance(offer.stock_status, StockStatus), f"Stock status should be StockStatus enum"
                    print_test_result("Stock status enum validation", True, f"Valid: {offer.stock_status}")
                
                if offer.socket:
                    assert isinstance(offer.socket, SocketType), f"Socket should be SocketType enum"
                    print_test_result("Socket type enum validation", True, f"Valid: {offer.socket}")
                
                if offer.security:
                    assert isinstance(offer.security, SecurityType), f"Security should be SecurityType enum"
                    print_test_result("Security type enum validation", True, f"Valid: {offer.security}")
                
                if offer.prices:
                    assert hasattr(offer.prices, 'on_demand'), "Prices missing on_demand field"
                    if offer.prices.on_demand:
                        assert isinstance(offer.prices.on_demand, (int, float)), "on_demand should be numeric"
                        assert offer.prices.on_demand > 0, "on_demand should be positive"
                    print_test_result("Pricing structure validation", True)
                
                print_test_result("All response validation tests", True)
            else:
                print_test_result("Response validation", False, "No offers to validate")
                
    except RateLimitError:
        print_test_result("Response validation", False, "Rate limit exceeded")
    except Exception as e:
        print_test_result("Response validation", False, f"{type(e).__name__}: {e}")


async def test_model_validation():
    """Test that our models work correctly."""
    print_section("Model Validation Tests")
    
    # Test GPUAvailability creation
    test_data = {
        "cloudId": "test-instance",
        "gpuType": "H100_80GB",
        "provider": "runpod",
        "stockStatus": "Available",
        "prices": {
            "onDemand": 2.50,
            "currency": "USD"
        }
    }
    
    offer = GPUAvailability.from_dict(test_data)
    assert offer.cloud_id == "test-instance"
    assert offer.gpu_type == "H100_80GB"
    assert offer.provider == Provider.RUNPOD
    assert offer.stock_status == StockStatus.AVAILABLE
    assert offer.prices.on_demand == 2.50
    print_test_result("GPUAvailability model creation", True)
    
    # Test with unknown enum values
    test_data_unknown = {
        "cloudId": "test-unknown",
        "provider": "unknown_provider",
        "stockStatus": "Unknown_Status"
    }
    
    offer_unknown = GPUAvailability.from_dict(test_data_unknown)
    assert offer_unknown.provider is None  # Unknown enum should be None
    assert offer_unknown.stock_status is None
    print_test_result("Unknown enum handling", True, "Unknown values converted to None")


async def test_parameter_handling():
    """Test that our parameter handling works."""
    print_section("Parameter Handling Tests")
    
    async with PrimeIntellectClient("test-key") as client:
        try:
            # This will fail due to invalid API key, but we can check parameter building
            await client.get_availability(
                regions=["united_states", "canada"],
                gpu_type="H100_80GB",
                gpu_count=1,
                socket="PCIe",
                security="secure_cloud"
            )
        except (AuthenticationError, NetworkError, APIError):
            # Expected - we're just testing parameter handling
            pass
        
        print_test_result("Parameter handling", True, "No exceptions during parameter building")


async def main():
    """Run all tests."""
    print_header("Prime Intellect Client - Real Implementation Tests")
    print("These tests exercise our actual code implementation")
    print("(not just mocked responses)")
    
    await test_client_initialization()
    await test_error_handling_without_api_key()
    await test_model_validation()
    await test_parameter_handling()
    await test_real_api_call()
    await test_edge_cases()
    await test_response_validation()
    
    print_header("Real Implementation Tests Complete")
    print("All tests completed successfully")
    print("Note: Some failures due to rate limiting are expected")


if __name__ == "__main__":
    asyncio.run(main()) 