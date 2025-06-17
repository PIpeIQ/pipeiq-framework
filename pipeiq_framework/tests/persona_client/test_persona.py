#!/usr/bin/env python3
"""
Comprehensive test suite for the Persona API client.
"""

import asyncio
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import traceback

# Import all classes from the Persona module
# Importing from persona_service.py in the same directory
try:
    from persona_service import (
        # Enums
        InquiryStatus, VerificationType, ReportType, DocumentType,
        CaseStatus, VerificationMethod, WebhookEventType,
        BatchOperationType, RetryStrategy,
        
        # Configuration classes
        InquiryConfig, VerificationConfig, ReportConfig, DocumentConfig,
        CaseConfig, VerificationMethodConfig, WebhookConfig,
        BatchOperationConfig, RateLimitConfig, RetryConfig, CacheConfig,
        
        # Utility classes
        RateLimiter, Cache, PersonaService,
        
        # Exceptions
        PersonaError, ConnectionError, VerificationError, ReportError,
        
        # Decorators
        with_retry, with_cache
    )
except ImportError as e:
    print(f"Error importing Persona client: {e}")
    print("Please ensure your code is in 'persona_service.py' in the same directory")
    sys.exit(1)

class TestResult:
    """Container for test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.results = {}
    
    def add_success(self, test_name: str, message: str = ""):
        self.passed += 1
        self.results[test_name] = {"status": "PASS", "message": message}
        print(f"✅ {test_name}: {message}")
    
    def add_failure(self, test_name: str, error: str):
        self.failed += 1
        self.results[test_name] = {"status": "FAIL", "error": error}
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ {test_name}: {error}")
    
    def print_summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success rate: {(self.passed/total*100):.1f}%" if total > 0 else "No tests run")
        
        if self.errors:
            print(f"\n{'='*60}")
            print("FAILURES:")
            print(f"{'='*60}")
            for error in self.errors:
                print(f"- {error}")

class PersonaTestSuite:
    """Comprehensive test suite for Persona API client."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.results = TestResult()
    
    def test_enum_classes(self):
        """Test all enum classes."""
        print("\n🧪 Testing Enum Classes...")
        
        # Test InquiryStatus
        try:
            statuses = [s.value for s in InquiryStatus]
            expected = ["created", "completed", "expired", "failed", "pending", "approved", "declined", "review"]
            assert all(status in expected for status in statuses)
            self.results.add_success("InquiryStatus", f"All {len(statuses)} statuses valid")
        except Exception as e:
            self.results.add_failure("InquiryStatus", str(e))
        
        # Test VerificationType
        try:
            types = [t.value for t in VerificationType]
            assert len(types) > 0
            assert "government_id" in types
            self.results.add_success("VerificationType", f"Contains {len(types)} verification types")
        except Exception as e:
            self.results.add_failure("VerificationType", str(e))
        
        # Test other enums
        enum_tests = [
            (ReportType, "ReportType"),
            (DocumentType, "DocumentType"),
            (CaseStatus, "CaseStatus"),
            (VerificationMethod, "VerificationMethod"),
            (WebhookEventType, "WebhookEventType"),
            (BatchOperationType, "BatchOperationType"),
            (RetryStrategy, "RetryStrategy")
        ]
        
        for enum_class, name in enum_tests:
            try:
                values = [e.value for e in enum_class]
                assert len(values) > 0
                self.results.add_success(name, f"Contains {len(values)} values")
            except Exception as e:
                self.results.add_failure(name, str(e))
    
    def test_config_classes(self):
        """Test all configuration dataclasses."""
        print("\n🧪 Testing Configuration Classes...")
        
        # Test InquiryConfig
        try:
            config = InquiryConfig(
                template_id="test_template",
                reference_id="test_ref",
                metadata={"test": "data"},
                expires_at=datetime.now() + timedelta(hours=1)
            )
            assert config.template_id == "test_template"
            assert config.reference_id == "test_ref"
            self.results.add_success("InquiryConfig", "Successfully created with all fields")
        except Exception as e:
            self.results.add_failure("InquiryConfig", str(e))
        
        # Test other config classes
        config_tests = [
            (VerificationConfig, {"type": VerificationType.GOVERNMENT_ID}, "VerificationConfig"),
            (ReportConfig, {"type": ReportType.WATCHLIST}, "ReportConfig"),
            (DocumentConfig, {"type": DocumentType.PASSPORT, "country": "US"}, "DocumentConfig"),
            (CaseConfig, {"reference_id": "test_case"}, "CaseConfig"),
            (VerificationMethodConfig, {"method": VerificationMethod.DOCUMENT}, "VerificationMethodConfig"),
            (WebhookConfig, {"url": "https://example.com", "events": [WebhookEventType.INQUIRY_CREATED]}, "WebhookConfig"),
            (BatchOperationConfig, {"type": BatchOperationType.CREATE_INQUIRIES, "items": []}, "BatchOperationConfig"),
            (RateLimitConfig, {"requests_per_second": 10}, "RateLimitConfig"),
            (RetryConfig, {}, "RetryConfig"),
            (CacheConfig, {}, "CacheConfig")
        ]
        
        for config_class, kwargs, name in config_tests:
            try:
                config = config_class(**kwargs)
                assert config is not None
                self.results.add_success(name, "Successfully instantiated")
            except Exception as e:
                self.results.add_failure(name, str(e))
    
    async def test_rate_limiter(self):
        """Test the RateLimiter class."""
        print("\n🧪 Testing RateLimiter...")
        
        try:
            config = RateLimitConfig(requests_per_second=5, burst_size=2)
            limiter = RateLimiter(config)
            
            # Test token acquisition
            start_time = time.time()
            await limiter.acquire()
            await limiter.acquire()  # Should use burst
            await limiter.acquire()  # Should wait
            elapsed = time.time() - start_time
            
            # Should take at least 0.2 seconds (1/5 requests per second)
            if elapsed >= 0.15:  # Small tolerance
                self.results.add_success("RateLimiter", f"Correctly limited requests (took {elapsed:.2f}s)")
            else:
                self.results.add_failure("RateLimiter", f"Rate limiting not working (took {elapsed:.2f}s)")
        except Exception as e:
            self.results.add_failure("RateLimiter", str(e))
    
    async def test_cache(self):
        """Test the Cache class."""
        print("\n🧪 Testing Cache...")
        
        try:
            config = CacheConfig(ttl=1, max_size=2)
            cache = Cache(config)
            
            # Test basic operations
            await cache.set("key1", "value1")
            value = await cache.get("key1")
            assert value == "value1"
            
            # Test expiration
            await asyncio.sleep(1.1)
            expired_value = await cache.get("key1")
            assert expired_value is None
            
            # Test max size
            await cache.set("key2", "value2")
            await cache.set("key3", "value3")
            await cache.set("key4", "value4")  # Should evict oldest
            
            self.results.add_success("Cache", "All operations working correctly")
        except Exception as e:
            self.results.add_failure("Cache", str(e))
    
    async def test_decorators(self):
        """Test the retry and cache decorators."""
        print("\n🧪 Testing Decorators...")
        
        # Test retry decorator
        try:
            retry_config = RetryConfig(max_retries=2, initial_delay=0.1)
            
            @with_retry(retry_config)
            async def failing_function():
                failing_function.call_count += 1
                if failing_function.call_count < 3:
                    raise Exception("Temporary failure")
                return "success"
            
            failing_function.call_count = 0
            result = await failing_function()
            assert result == "success"
            assert failing_function.call_count == 3
            self.results.add_success("with_retry", "Retry mechanism working correctly")
        except Exception as e:
            self.results.add_failure("with_retry", str(e))
        
        # Test cache decorator
        try:
            cache = Cache(CacheConfig(ttl=10))
            
            @with_cache(cache)
            async def cached_function(x):
                cached_function.call_count += 1
                return f"result_{x}"
            
            cached_function.call_count = 0
            
            result1 = await cached_function(1)
            result2 = await cached_function(1)  # Should use cache
            
            assert result1 == result2 == "result_1"
            assert cached_function.call_count == 1  # Only called once
            self.results.add_success("with_cache", "Cache decorator working correctly")
        except Exception as e:
            self.results.add_failure("with_cache", str(e))
    
    async def test_persona_service_initialization(self):
        """Test PersonaService initialization and basic setup."""
        print("\n🧪 Testing PersonaService Initialization...")
        
        try:
            service = PersonaService(
                api_key=self.api_key,
                environment="sandbox"
            )
            
            assert service.api_key == self.api_key
            assert service.environment == "sandbox"
            assert service.base_url == "https://sandbox.withpersona.com/api/v1"
            assert service.rate_limiter is not None
            assert service.cache is not None
            
            self.results.add_success("PersonaService Init", "Service initialized correctly")
        except Exception as e:
            self.results.add_failure("PersonaService Init", str(e))
    
    async def test_persona_service_context_manager(self):
        """Test PersonaService as context manager."""
        print("\n🧪 Testing PersonaService Context Manager...")
        
        try:
            async with PersonaService(api_key=self.api_key) as service:
                assert service.session is not None
                assert hasattr(service.session, 'request')
            
            # Session should be closed after context
            self.results.add_success("PersonaService Context", "Context manager working correctly")
        except Exception as e:
            self.results.add_failure("PersonaService Context", str(e))
    
    async def test_persona_service_methods(self):
        """Test PersonaService methods (without actual API calls)."""
        print("\n🧪 Testing PersonaService Methods...")
        
        try:
            async with PersonaService(api_key=self.api_key) as service:
                # Test method existence and basic structure
                methods_to_test = [
                    'create_inquiry', 'get_inquiry', 'list_inquiries',
                    'create_verification', 'get_verification',
                    'create_report', 'get_report',
                    'create_case', 'get_case', 'update_case', 'list_cases',
                    'register_webhook', 'list_webhooks', 'delete_webhook',
                    'execute_batch_operation', 'get_batch_operation_status'
                ]
                
                missing_methods = []
                for method_name in methods_to_test:
                    if not hasattr(service, method_name):
                        missing_methods.append(method_name)
                    elif not callable(getattr(service, method_name)):
                        missing_methods.append(f"{method_name} (not callable)")
                
                if missing_methods:
                    self.results.add_failure("PersonaService Methods", f"Missing: {missing_methods}")
                else:
                    self.results.add_success("PersonaService Methods", f"All {len(methods_to_test)} methods present")
        except Exception as e:
            self.results.add_failure("PersonaService Methods", str(e))
    
    async def test_webhook_verification(self):
        """Test webhook signature verification."""
        print("\n🧪 Testing Webhook Verification...")
        
        try:
            service = PersonaService(api_key=self.api_key)
            
            # Test webhook signature verification
            payload = '{"test": "data"}'
            secret = "test_secret"
            
            # Create a valid signature
            import hmac
            import hashlib
            valid_signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Test valid signature
            is_valid = await service.verify_webhook_signature(payload, valid_signature, secret)
            assert is_valid == True
            
            # Test invalid signature
            is_invalid = await service.verify_webhook_signature(payload, "invalid_signature", secret)
            assert is_invalid == False
            
            self.results.add_success("Webhook Verification", "Signature verification working correctly")
        except Exception as e:
            self.results.add_failure("Webhook Verification", str(e))
    
    async def test_exception_classes(self):
        """Test custom exception classes."""
        print("\n🧪 Testing Exception Classes...")
        
        try:
            # Test exception hierarchy
            assert issubclass(ConnectionError, PersonaError)
            assert issubclass(VerificationError, PersonaError)
            assert issubclass(ReportError, PersonaError)
            
            # Test exception instantiation
            exceptions = [
                PersonaError("Base error"),
                ConnectionError("Connection failed"),
                VerificationError("Verification failed"),
                ReportError("Report generation failed")
            ]
            
            for exc in exceptions:
                assert isinstance(exc, Exception)
                assert str(exc) != ""
            
            self.results.add_success("Exception Classes", "All exception classes working correctly")
        except Exception as e:
            self.results.add_failure("Exception Classes", str(e))
    
    async def test_api_connectivity(self):
        """Test basic API connectivity (if possible)."""
        print("\n🧪 Testing API Connectivity...")
        
        try:
            async with PersonaService(api_key=self.api_key, environment="sandbox") as service:
                # Try to make a simple request that should work
                # This will test the actual API connection
                try:
                    # Attempt to list inquiries (should return 200 even if empty)
                    result = await service.list_inquiries(page_size=1)
                    self.results.add_success("API Connectivity", "Successfully connected to Persona API")
                except Exception as api_error:
                    # Check if it's an authentication error vs network error
                    error_str = str(api_error)
                    if "401" in error_str or "unauthorized" in error_str.lower():
                        self.results.add_failure("API Connectivity", f"Authentication failed: {api_error}")
                    elif "400" in error_str or "404" in error_str:
                        self.results.add_success("API Connectivity", "API reachable (got HTTP error response)")
                    else:
                        self.results.add_failure("API Connectivity", f"Network/connection error: {api_error}")
        except Exception as e:
            self.results.add_failure("API Connectivity", str(e))
    
    def analyze_necessity(self):
        """Analyze which classes/methods are necessary based on test results."""
        print("\n🔍 Analyzing Code Necessity...")
        
        # Core necessary classes (based on typical API client patterns)
        core_classes = {
            "PersonaService": "Main service class - ESSENTIAL",
            "InquiryConfig": "Core configuration for main API feature - ESSENTIAL",
            "PersonaError": "Base exception handling - ESSENTIAL",
            "RateLimiter": "Prevents API abuse - RECOMMENDED",
            "Cache": "Performance optimization - RECOMMENDED"
        }
        
        # Potentially unnecessary classes
        potentially_unnecessary = {
            "BatchOperationConfig": "Only needed if batch operations are used",
            "WebhookConfig": "Only needed if webhooks are implemented",
            "ReportError": "Specific exception - could use generic PersonaError",
            "VerificationError": "Specific exception - could use generic PersonaError",
            "ConnectionError": "Specific exception - could use generic PersonaError"
        }
        
        # Utility classes
        utility_classes = {
            "with_retry": "Decorator for resilience - RECOMMENDED",
            "with_cache": "Decorator for performance - OPTIONAL"
        }
        
        print("\n📊 NECESSITY ANALYSIS:")
        print("="*60)
        
        print("\n🔴 ESSENTIAL CLASSES:")
        for cls, reason in core_classes.items():
            status = "✅ WORKING" if cls in [r for r in self.results.results if "PASS" in str(self.results.results[r])] else "❓ CHECK"
            print(f"  {cls}: {reason} [{status}]")
        
        print("\n🟡 CONDITIONAL CLASSES:")
        for cls, reason in potentially_unnecessary.items():
            print(f"  {cls}: {reason}")
        
        print("\n🟢 UTILITY CLASSES:")
        for cls, reason in utility_classes.items():
            print(f"  {cls}: {reason}")
        
        # Count enum usage
        enum_count = sum(1 for result in self.results.results if "Status" in result or "Type" in result or "Method" in result)
        print(f"\n📝 ENUMS: {enum_count} enum classes defined")
        print("  - Consider consolidating similar enums")
        print("  - Remove unused enum values")
        
        # Configuration classes analysis
        config_count = sum(1 for result in self.results.results if "Config" in result)
        print(f"\n⚙️  CONFIGURATION CLASSES: {config_count} config classes")
        print("  - Consider using a single flexible config class")
        print("  - Keep only configs for features you'll actually use")
    
    async def run_all_tests(self):
        """Run the complete test suite."""
        print("🚀 Starting Persona API Client Test Suite")
        print("="*60)
        
        # Run all tests
        self.test_enum_classes()
        self.test_config_classes()
        await self.test_rate_limiter()
        await self.test_cache()
        await self.test_decorators()
        await self.test_persona_service_initialization()
        await self.test_persona_service_context_manager()
        await self.test_persona_service_methods()
        await self.test_webhook_verification()
        await self.test_exception_classes()
        await self.test_api_connectivity()
        
        # Print results
        self.results.print_summary()
        
        # Analyze necessity
        self.analyze_necessity()

async def main():
    """Main test runner."""
    # Get API key from environment variable
    API_KEY = os.getenv("PERSONA_API_KEY")
    
    if not API_KEY:
        print("❌ Error: PERSONA_API_KEY environment variable not set!")
        print("\nTo set the environment variable:")
        print("\nOr run with: PERSONA_API_KEY='your_key_here' python test_persona.py")
        sys.exit(1)
    
    print(f"🔑 Using API key: {API_KEY[:20]}...")
    
    test_suite = PersonaTestSuite(API_KEY)
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())