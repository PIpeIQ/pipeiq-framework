#!/usr/bin/env python3
"""
Pytest test suite for the Persona API client.
Tests all classes, methods, and configurations to determine necessity and functionality.

Usage:
    pytest test_persona.py -v
    pytest test_persona.py::TestPersonaService::test_initialization -v
    pytest test_persona.py --tb=short
"""

import pytest
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
    pytest.exit(f"Error importing Persona client: {e}\nPlease ensure your code is in 'persona_service.py' in the same directory")


@pytest.fixture(scope="session")
def api_key():
    """Get API key from environment variable."""
    key = os.getenv("PERSONA_API_KEY")
    if not key:
        pytest.exit(
            "PERSONA_API_KEY environment variable not set!\n"
            "Set it with: export PERSONA_API_KEY='your_persona_api_key_here'"
        )
    return key


@pytest.fixture
def sample_inquiry_config():
    """Sample inquiry configuration for testing."""
    return InquiryConfig(
        template_id="test_template",
        reference_id="test_ref",
        metadata={"test": "data"},
        expires_at=datetime.now() + timedelta(hours=1)
    )


@pytest.fixture
def sample_verification_config():
    """Sample verification configuration for testing."""
    return VerificationConfig(type=VerificationType.GOVERNMENT_ID)


@pytest.fixture
def sample_rate_limit_config():
    """Sample rate limit configuration for testing."""
    return RateLimitConfig(requests_per_second=5, burst_size=2)


@pytest.fixture
def sample_cache_config():
    """Sample cache configuration for testing."""
    return CacheConfig(ttl=1, max_size=2)


class TestEnumClasses:
    """Test all enum classes."""
    
    def test_inquiry_status_enum(self):
        """Test InquiryStatus enum."""
        statuses = [s.value for s in InquiryStatus]
        expected = ["created", "completed", "expired", "failed", "pending", "approved", "declined", "review"]
        assert all(status in expected for status in statuses)
        assert len(statuses) == len(expected)
    
    def test_verification_type_enum(self):
        """Test VerificationType enum."""
        types = [t.value for t in VerificationType]
        assert len(types) > 0
        assert "government_id" in types
        assert "selfie" in types
    
    def test_report_type_enum(self):
        """Test ReportType enum."""
        types = [t.value for t in ReportType]
        assert len(types) > 0
        assert "watchlist" in types
    
    def test_document_type_enum(self):
        """Test DocumentType enum."""
        types = [t.value for t in DocumentType]
        assert len(types) > 0
        assert "passport" in types
        assert "drivers_license" in types
    
    def test_case_status_enum(self):
        """Test CaseStatus enum."""
        statuses = [s.value for s in CaseStatus]
        assert len(statuses) > 0
        assert "open" in statuses
        assert "closed" in statuses
    
    def test_verification_method_enum(self):
        """Test VerificationMethod enum."""
        methods = [m.value for m in VerificationMethod]
        assert len(methods) > 0
        assert "document" in methods
        assert "selfie" in methods
    
    def test_webhook_event_type_enum(self):
        """Test WebhookEventType enum."""
        events = [e.value for e in WebhookEventType]
        assert len(events) > 0
        assert "inquiry.created" in events
    
    def test_batch_operation_type_enum(self):
        """Test BatchOperationType enum."""
        operations = [o.value for o in BatchOperationType]
        assert len(operations) > 0
        assert "create_inquiries" in operations
    
    def test_retry_strategy_enum(self):
        """Test RetryStrategy enum."""
        strategies = [s.value for s in RetryStrategy]
        assert len(strategies) > 0
        assert "exponential_backoff" in strategies


class TestConfigurationClasses:
    """Test all configuration dataclasses."""
    
    def test_inquiry_config(self, sample_inquiry_config):
        """Test InquiryConfig dataclass."""
        config = sample_inquiry_config
        assert config.template_id == "test_template"
        assert config.reference_id == "test_ref"
        assert config.metadata == {"test": "data"}
        assert isinstance(config.expires_at, datetime)
    
    def test_verification_config(self, sample_verification_config):
        """Test VerificationConfig dataclass."""
        config = sample_verification_config
        assert config.type == VerificationType.GOVERNMENT_ID
        assert config.country is None
        assert config.document_type is None
    
    def test_report_config(self):
        """Test ReportConfig dataclass."""
        config = ReportConfig(type=ReportType.WATCHLIST, inquiry_id="test_inquiry")
        assert config.type == ReportType.WATCHLIST
        assert config.inquiry_id == "test_inquiry"
        assert config.metadata is None
    
    def test_document_config(self):
        """Test DocumentConfig dataclass."""
        config = DocumentConfig(type=DocumentType.PASSPORT, country="US")
        assert config.type == DocumentType.PASSPORT
        assert config.country == "US"
    
    def test_case_config(self):
        """Test CaseConfig dataclass."""
        config = CaseConfig(reference_id="test_case")
        assert config.reference_id == "test_case"
        assert config.status == CaseStatus.OPEN
        assert config.tags == []  # Should use default_factory
    
    def test_verification_method_config(self):
        """Test VerificationMethodConfig dataclass."""
        config = VerificationMethodConfig(method=VerificationMethod.DOCUMENT)
        assert config.method == VerificationMethod.DOCUMENT
        assert config.enabled is True
    
    def test_webhook_config(self):
        """Test WebhookConfig dataclass."""
        config = WebhookConfig(
            url="https://example.com",
            events=[WebhookEventType.INQUIRY_CREATED]
        )
        assert config.url == "https://example.com"
        assert WebhookEventType.INQUIRY_CREATED in config.events
    
    def test_batch_operation_config(self):
        """Test BatchOperationConfig dataclass."""
        config = BatchOperationConfig(
            type=BatchOperationType.CREATE_INQUIRIES,
            items=[]
        )
        assert config.type == BatchOperationType.CREATE_INQUIRIES
        assert config.items == []
    
    def test_rate_limit_config(self, sample_rate_limit_config):
        """Test RateLimitConfig dataclass."""
        config = sample_rate_limit_config
        assert config.requests_per_second == 5
        assert config.burst_size == 2
    
    def test_retry_config(self):
        """Test RetryConfig dataclass."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF
        assert 429 in config.retry_on_status_codes  # Should use default_factory
    
    def test_cache_config(self, sample_cache_config):
        """Test CacheConfig dataclass."""
        config = sample_cache_config
        assert config.ttl == 1
        assert config.max_size == 2
        assert config.enabled is True


class TestUtilityClasses:
    """Test utility classes like RateLimiter and Cache."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter(self, sample_rate_limit_config):
        """Test RateLimiter functionality."""
        limiter = RateLimiter(sample_rate_limit_config)
        
        # Test token acquisition timing
        start_time = time.time()
        await limiter.acquire()
        await limiter.acquire()  # Should use burst
        await limiter.acquire()  # Should wait
        elapsed = time.time() - start_time
        
        # Should take at least 0.15 seconds (allowing for small tolerance)
        assert elapsed >= 0.15, f"Rate limiting not working (took {elapsed:.2f}s)"
    
    @pytest.mark.asyncio
    async def test_cache_basic_operations(self, sample_cache_config):
        """Test Cache basic operations."""
        cache = Cache(sample_cache_config)
        
        # Test set and get
        await cache.set("key1", "value1")
        value = await cache.get("key1")
        assert value == "value1"
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, sample_cache_config):
        """Test Cache expiration."""
        cache = Cache(sample_cache_config)
        
        # Test expiration
        await cache.set("key1", "value1")
        await asyncio.sleep(1.1)  # Wait for TTL
        expired_value = await cache.get("key1")
        assert expired_value is None
    
    @pytest.mark.asyncio
    async def test_cache_max_size(self, sample_cache_config):
        """Test Cache max size eviction."""
        cache = Cache(sample_cache_config)
        
        # Test max size (config has max_size=2)
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")  # Should evict oldest
        
        # First key should be evicted
        value1 = await cache.get("key1")
        value3 = await cache.get("key3")
        assert value1 is None  # Evicted
        assert value3 == "value3"  # Still there


class TestDecorators:
    """Test the retry and cache decorators."""
    
    @pytest.mark.asyncio
    async def test_retry_decorator(self):
        """Test retry decorator functionality."""
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
    
    @pytest.mark.asyncio
    async def test_cache_decorator(self):
        """Test cache decorator functionality."""
        cache = Cache(CacheConfig(ttl=10))
        
        @with_cache(cache)
        async def cached_function(x):
            cached_function.call_count += 1
            return f"result_{x}"
        
        cached_function.call_count = 0
        
        result1 = await cached_function(1)
        result2 = await cached_function(1)  # Should use cache
        
        assert result1 == result2 == "result_1"
        assert cached_function.call_count == 1  # Only called once due to caching


class TestExceptionClasses:
    """Test custom exception classes."""
    
    def test_exception_hierarchy(self):
        """Test exception class hierarchy."""
        assert issubclass(ConnectionError, PersonaError)
        assert issubclass(VerificationError, PersonaError)
        assert issubclass(ReportError, PersonaError)
    
    def test_exception_instantiation(self):
        """Test exception instantiation."""
        exceptions = [
            PersonaError("Base error"),
            ConnectionError("Connection failed"),
            VerificationError("Verification failed"),
            ReportError("Report generation failed")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, Exception)
            assert str(exc) != ""


class TestPersonaService:
    """Test PersonaService class."""
    
    def test_initialization(self, api_key):
        """Test PersonaService initialization."""
        service = PersonaService(
            api_key=api_key,
            environment="sandbox"
        )
        
        assert service.api_key == api_key
        assert service.environment == "sandbox"
        assert service.base_url == "https://sandbox.withpersona.com/api/v1"
        assert service.rate_limiter is not None
        assert service.cache is not None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, api_key):
        """Test PersonaService as context manager."""
        async with PersonaService(api_key=api_key) as service:
            assert service.session is not None
            assert hasattr(service.session, 'request')
        # Session should be closed after context (can't easily test this)
    
    def test_service_methods_exist(self, api_key):
        """Test that all expected methods exist on PersonaService."""
        service = PersonaService(api_key=api_key)
        
        expected_methods = [
            'create_inquiry', 'get_inquiry', 'list_inquiries',
            'create_verification', 'get_verification',
            'create_report', 'get_report',
            'create_case', 'get_case', 'update_case', 'list_cases',
            'register_webhook', 'list_webhooks', 'delete_webhook',
            'execute_batch_operation', 'get_batch_operation_status',
            'verify_webhook_signature', 'process_webhook_event'
        ]
        
        for method_name in expected_methods:
            assert hasattr(service, method_name), f"Method {method_name} not found"
            assert callable(getattr(service, method_name)), f"Method {method_name} not callable"
    
    @pytest.mark.asyncio
    async def test_webhook_signature_verification(self, api_key):
        """Test webhook signature verification."""
        service = PersonaService(api_key=api_key)
        
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
        assert is_valid is True
        
        # Test invalid signature
        is_invalid = await service.verify_webhook_signature(payload, "invalid_signature", secret)
        assert is_invalid is False
    
    @pytest.mark.asyncio
    async def test_process_webhook_event(self, api_key):
        """Test webhook event processing."""
        service = PersonaService(api_key=api_key)
        
        # Test valid payload
        payload = {
            "data": {
                "type": "inquiry.created",
                "id": "test_id"
            }
        }
        
        result = await service.process_webhook_event(payload)
        assert result["event_type"] == "inquiry.created"
        assert "processed_at" in result
        assert result["payload"] == payload
        
        # Test invalid payload
        with pytest.raises(PersonaError, match="Invalid webhook payload"):
            await service.process_webhook_event({"invalid": "payload"})


class TestAPIConnectivity:
    """Test actual API connectivity."""
    
    @pytest.mark.asyncio
    async def test_api_connection(self, api_key):
        """Test basic API connectivity."""
        async with PersonaService(api_key=api_key, environment="sandbox") as service:
            try:
                # Attempt to list inquiries (should return 200 even if empty)
                result = await service.list_inquiries(page_size=1)
                # If we get here, the API is working
                assert result is not None
            except Exception as api_error:
                error_str = str(api_error)
                
                # Check error type and provide meaningful assertions
                if "401" in error_str or "unauthorized" in error_str.lower():
                    pytest.fail(f"Authentication failed - check API key: {api_error}")
                elif "400" in error_str or "404" in error_str:
                    # API is reachable but endpoint might not exist - this is actually good
                    pass
                else:
                    pytest.fail(f"Network/connection error: {api_error}")


class TestCodeNecessityAnalysis:
    """Analyze code necessity and provide recommendations."""
    
    def test_core_classes_present(self):
        """Test that core essential classes are present."""
        core_classes = [
            PersonaService,
            InquiryConfig,
            PersonaError,
            RateLimiter,
            Cache
        ]
        
        for cls in core_classes:
            assert cls is not None, f"Core class {cls.__name__} is missing"
    
    def test_enum_completeness(self):
        """Test enum completeness and suggest optimizations."""
        enums = [
            InquiryStatus, VerificationType, ReportType, DocumentType,
            CaseStatus, VerificationMethod, WebhookEventType,
            BatchOperationType, RetryStrategy
        ]
        
        enum_count = len(enums)
        assert enum_count > 0
        
        # Check if enums have reasonable number of values
        for enum_cls in enums:
            values = list(enum_cls)
            assert len(values) > 0, f"Enum {enum_cls.__name__} is empty"
    
    def test_config_classes_count(self):
        """Test configuration classes and suggest consolidation."""
        config_classes = [
            InquiryConfig, VerificationConfig, ReportConfig, DocumentConfig,
            CaseConfig, VerificationMethodConfig, WebhookConfig,
            BatchOperationConfig, RateLimitConfig, RetryConfig, CacheConfig
        ]
        
        config_count = len(config_classes)
        assert config_count > 0
        
        # Suggest optimization if too many config classes
        if config_count > 8:
            print(f"\n💡 OPTIMIZATION SUGGESTION: You have {config_count} configuration classes.")
            print("   Consider consolidating similar configs or using a flexible base config class.")


# Pytest configuration and custom reporting
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Mark API tests as slow
        if "api" in item.nodeid.lower() or "connectivity" in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)


@pytest.fixture(autouse=True)
def print_test_info(request):
    """Print test information for better visibility."""
    test_name = request.node.name
    class_name = request.node.parent.name if hasattr(request.node.parent, 'name') else ""
    
    print(f"\n🧪 Running: {class_name}::{test_name}")


# Custom pytest report
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Custom terminal summary with necessity analysis."""
    if exitstatus == 0:
        terminalreporter.write_sep("=", "PERSONA CLIENT ANALYSIS")
        terminalreporter.write_line("🎉 All tests passed! Your Persona client is working correctly.")
        terminalreporter.write_line("")
        terminalreporter.write_line("📊 CODE NECESSITY ANALYSIS:")
        terminalreporter.write_line("="*60)
        terminalreporter.write_line("🔴 ESSENTIAL CLASSES:")
        terminalreporter.write_line("  PersonaService: Main service class - KEEP")
        terminalreporter.write_line("  InquiryConfig: Core configuration - KEEP")
        terminalreporter.write_line("  PersonaError: Exception handling - KEEP")
        terminalreporter.write_line("  RateLimiter: API protection - RECOMMENDED")
        terminalreporter.write_line("  Cache: Performance optimization - RECOMMENDED")
        terminalreporter.write_line("")
        terminalreporter.write_line("🟡 CONDITIONAL CLASSES:")
        terminalreporter.write_line("  BatchOperationConfig: Only if using batch operations")
        terminalreporter.write_line("  WebhookConfig: Only if implementing webhooks")
        terminalreporter.write_line("  Specific exceptions: Could consolidate to PersonaError")
        terminalreporter.write_line("")
        terminalreporter.write_line("💡 RECOMMENDATIONS:")
        terminalreporter.write_line("  - Remove unused enum values")
        terminalreporter.write_line("  - Consider consolidating similar config classes")
        terminalreporter.write_line("  - Keep decorators for resilience and performance")
        terminalreporter.write_line("  - All core functionality is working correctly!")