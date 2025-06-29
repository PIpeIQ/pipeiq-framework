"""Tests for the Prime Intellect service."""

import pytest
import aiohttp
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from pipeiq.prime_intellect import (
    PrimeIntellectService,
    GPUProvider,
    PodStatus,
    ResourceType,
    CostPeriod,
    PrimeIntellectAPIError,
    PrimeIntellectValidationError,
    PrimeIntellectNetworkError,
    QuotaType,
    BatchOperationStatus,
    MonitoringInterval,
    ScheduleType,
    OptimizationStrategy,
    PodPriority,
    ResourceSchedule,
    CostOptimizer,
    ScalingPolicy,
    BackupType,
    NetworkType,
    ScalingConfig,
    BackupConfig,
    NetworkConfig,
    PrimeIntellectError
)

@pytest.fixture
def api_key():
    return "test_api_key"

@pytest.fixture
def service(api_key):
    return PrimeIntellectService(api_key)

@pytest.fixture
def mock_response():
    return {
        "id": "test_pod_id",
        "name": "test_pod",
        "status": "running",
        "gpu_type": "nvidia-tesla-t4",
        "provider": "aws",
        "region": "us-west-2"
    }

@pytest.mark.asyncio
async def test_get_gpu_availability(service, mock_response):
    """Test getting GPU availability."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = [mock_response]
        
        result = await service.get_gpu_availability(
            provider=GPUProvider.AWS,
            region="us-west-2"
        )
        
        assert result == [mock_response]
        mock_request.assert_called_once_with(
            "GET",
            "availability/gpu",
            params={"provider": "aws", "region": "us-west-2"}
        )

@pytest.mark.asyncio
async def test_get_cluster_availability(service, mock_response):
    """Test getting cluster availability."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = [mock_response]
        
        result = await service.get_cluster_availability(
            provider=GPUProvider.AWS,
            region="us-west-2"
        )
        
        assert result == [mock_response]
        mock_request.assert_called_once_with(
            "GET",
            "availability/cluster",
            params={"provider": "aws", "region": "us-west-2"}
        )

@pytest.mark.asyncio
async def test_create_pod(service, mock_response):
    """Test creating a pod."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = mock_response
        
        result = await service.create_pod(
            name="test_pod",
            gpu_type="nvidia-tesla-t4",
            provider=GPUProvider.AWS,
            region="us-west-2",
            image="nvidia/cuda:11.0",
            command="python train.py",
            env={"MODEL_PATH": "/data/model"}
        )
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            "POST",
            "pods",
            data={
                "name": "test_pod",
                "gpu_type": "nvidia-tesla-t4",
                "provider": "aws",
                "region": "us-west-2",
                "image": "nvidia/cuda:11.0",
                "command": "python train.py",
                "env": {"MODEL_PATH": "/data/model"}
            }
        )

@pytest.mark.asyncio
async def test_get_pods(service, mock_response):
    """Test getting list of pods."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = [mock_response]
        
        result = await service.get_pods(
            status=PodStatus.RUNNING,
            provider=GPUProvider.AWS
        )
        
        assert result == [mock_response]
        mock_request.assert_called_once_with(
            "GET",
            "pods",
            params={"status": "running", "provider": "aws"}
        )

@pytest.mark.asyncio
async def test_get_pod(service, mock_response):
    """Test getting pod details."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = mock_response
        
        result = await service.get_pod("test_pod_id")
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            "GET",
            "pods/test_pod_id"
        )

@pytest.mark.asyncio
async def test_delete_pod(service, mock_response):
    """Test deleting a pod."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = {"status": "deleted"}
        
        result = await service.delete_pod("test_pod_id")
        
        assert result == {"status": "deleted"}
        mock_request.assert_called_once_with(
            "DELETE",
            "pods/test_pod_id"
        )

@pytest.mark.asyncio
async def test_get_pod_status(service, mock_response):
    """Test getting pod status."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = {"status": "running"}
        
        result = await service.get_pod_status("test_pod_id")
        
        assert result == {"status": "running"}
        mock_request.assert_called_once_with(
            "GET",
            "pods/test_pod_id/status"
        )

@pytest.mark.asyncio
async def test_get_pod_history(service, mock_response):
    """Test getting pod history."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = [mock_response]
        
        result = await service.get_pod_history("test_pod_id")
        
        assert result == [mock_response]
        mock_request.assert_called_once_with(
            "GET",
            "pods/test_pod_id/history"
        )

@pytest.mark.asyncio
async def test_add_metrics(service, mock_response):
    """Test adding metrics."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = {"status": "success"}
        
        metrics = {
            "gpu_utilization": 85.5,
            "memory_used": "8.2GB",
            "temperature": 65
        }
        
        result = await service.add_metrics("test_pod_id", metrics)
        
        assert result == {"status": "success"}
        mock_request.assert_called_once_with(
            "POST",
            "pools/test_pod_id/metrics",
            data={"metrics": metrics}
        )

@pytest.mark.asyncio
async def test_api_error_handling(service):
    """Test API error handling."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.side_effect = PrimeIntellectAPIError("API error")
        
        with pytest.raises(PrimeIntellectAPIError) as exc_info:
            await service.get_pod("test_pod_id")
        
        assert str(exc_info.value) == "API error"

@pytest.mark.asyncio
async def test_validation_error_handling(service):
    """Test validation error handling."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.side_effect = PrimeIntellectValidationError("Validation error")
        
        with pytest.raises(PrimeIntellectValidationError) as exc_info:
            await service.create_pod(
                name="test_pod",
                gpu_type="invalid",
                provider=GPUProvider.AWS,
                region="us-west-2",
                image="nvidia/cuda:11.0"
            )
        
        assert str(exc_info.value) == "Validation error"

@pytest.mark.asyncio
async def test_network_error_handling(service):
    """Test network error handling."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.side_effect = PrimeIntellectNetworkError("Network error")
        
        with pytest.raises(PrimeIntellectNetworkError) as exc_info:
            await service.get_pods()
        
        assert str(exc_info.value) == "Network error"

@pytest.mark.asyncio
async def test_retry_logic(service):
    """Test retry logic for failed requests."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.side_effect = [
            PrimeIntellectAPIError("Rate limit exceeded"),
            {"status": "success"}
        ]
        
        result = await service.get_pods()
        
        assert result == {"status": "success"}
        assert mock_request.call_count == 2

@pytest.mark.asyncio
async def test_context_manager(api_key):
    """Test context manager functionality."""
    async with PrimeIntellectService(api_key) as service:
        assert isinstance(service, PrimeIntellectService)
        assert service._session is not None
        assert not service._session.closed
    
    assert service._session.closed

@pytest.mark.asyncio
async def test_get_resource_usage(service, mock_response):
    """Test getting resource usage metrics."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = [
            {
                "timestamp": "2024-03-20T10:00:00Z",
                "value": 85.5,
                "unit": "percent"
            }
        ]
        
        start_time = datetime(2024, 3, 20, 10, 0, 0)
        end_time = datetime(2024, 3, 20, 11, 0, 0)
        
        result = await service.get_resource_usage(
            "test_pod_id",
            ResourceType.GPU,
            start_time,
            end_time
        )
        
        assert len(result) == 1
        assert result[0]["value"] == 85.5
        mock_request.assert_called_once_with(
            "GET",
            "pods/test_pod_id/resources",
            params={
                "resource_type": "gpu",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
        )

@pytest.mark.asyncio
async def test_get_cost_estimate(service, mock_response):
    """Test getting cost estimate."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = {
            "usd": 2.50,
            "eur": 2.30,
            "gbp": 1.95
        }
        
        result = await service.get_cost_estimate(
            "nvidia-tesla-t4",
            GPUProvider.AWS,
            "us-west-2",
            1.0
        )
        
        assert result["usd"] == 2.50
        mock_request.assert_called_once_with(
            "GET",
            "costs/estimate",
            params={
                "gpu_type": "nvidia-tesla-t4",
                "provider": "aws",
                "region": "us-west-2",
                "duration_hours": 1.0
            }
        )

@pytest.mark.asyncio
async def test_get_cost_history(service, mock_response):
    """Test getting cost history."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = [
            {
                "date": "2024-03-20",
                "cost": 60.00,
                "currency": "usd"
            }
        ]
        
        start_date = datetime(2024, 3, 20)
        end_date = datetime(2024, 3, 21)
        
        result = await service.get_cost_history(
            pod_id="test_pod_id",
            period=CostPeriod.DAILY,
            start_date=start_date,
            end_date=end_date
        )
        
        assert len(result) == 1
        assert result[0]["cost"] == 60.00
        mock_request.assert_called_once_with(
            "GET",
            "costs/history",
            params={
                "pod_id": "test_pod_id",
                "period": "daily",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )

@pytest.mark.asyncio
async def test_scale_pod(service, mock_response):
    """Test scaling a pod."""
    with patch.object(service, '_make_request') as mock_request, \
         patch.object(service, 'get_pod_status') as mock_status:
        mock_request.return_value = mock_response
        mock_status.return_value = {"status": "running"}
        
        result = await service.scale_pod(
            "test_pod_id",
            gpu_count=2,
            wait_for_completion=True
        )
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            "POST",
            "pods/test_pod_id/scale",
            data={"gpu_count": 2}
        )
        mock_status.assert_called_once_with("test_pod_id")

@pytest.mark.asyncio
async def test_get_pod_logs(service, mock_response):
    """Test getting pod logs."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = [
            "2024-03-20 10:00:00 INFO: Starting pod",
            "2024-03-20 10:00:01 INFO: Pod running"
        ]
        
        result = await service.get_pod_logs(
            "test_pod_id",
            lines=2,
            follow=False
        )
        
        assert len(result) == 2
        mock_request.assert_called_once_with(
            "GET",
            "pods/test_pod_id/logs",
            params={"lines": 2}
        )

@pytest.mark.asyncio
async def test_get_health_check(service, mock_response):
    """Test getting health check information."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = {
            "status": "healthy",
            "version": "1.0.0",
            "uptime": 3600
        }
        
        result = await service.get_health_check()
        
        assert result["status"] == "healthy"
        mock_request.assert_called_once_with("GET", "health")

@pytest.mark.asyncio
async def test_get_api_status(service, mock_response):
    """Test getting API status information."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = {
            "status": "operational",
            "load": 0.5,
            "active_pods": 100
        }
        
        result = await service.get_api_status()
        
        assert result["status"] == "operational"
        mock_request.assert_called_once_with("GET", "status")

def test_metrics_tracking(service):
    """Test local metrics tracking."""
    # Track some metrics
    service.track_metric("gpu_utilization", 85.5)
    service.track_metric("gpu_utilization", 90.0)
    service.track_metric("memory_usage", 8.2)
    
    # Get latest metrics
    assert service.get_latest_metric("gpu_utilization") == 90.0
    assert service.get_latest_metric("memory_usage") == 8.2
    assert service.get_latest_metric("cpu_usage") is None
    
    # Get average metrics
    period = timedelta(minutes=5)
    assert service.get_average_metric("gpu_utilization", period) == 87.75
    assert service.get_average_metric("memory_usage", period) == 8.2
    assert service.get_average_metric("cpu_usage", period) is None

def test_metrics_tracking_disabled():
    """Test metrics tracking when disabled."""
    service = PrimeIntellectService("test_api_key", enable_metrics_tracking=False)
    
    # Try to track metrics
    service.track_metric("gpu_utilization", 85.5)
    
    # Metrics should not be available
    assert service.get_latest_metric("gpu_utilization") is None
    assert service.get_average_metric("gpu_utilization", timedelta(minutes=5)) is None

@pytest.mark.asyncio
async def test_scale_pod_timeout(service, mock_response):
    """Test scaling a pod with timeout."""
    with patch.object(service, '_make_request') as mock_request, \
         patch.object(service, 'get_pod_status') as mock_status:
        mock_request.return_value = mock_response
        mock_status.return_value = {"status": "pending"}
        
        with pytest.raises(PrimeIntellectAPIError) as exc_info:
            await service.scale_pod(
                "test_pod_id",
                gpu_count=2,
                wait_for_completion=True
            )
        
        assert "Scaling operation timed out" in str(exc_info.value)
        assert mock_request.call_count == 1
        assert mock_status.call_count > 1

@pytest.mark.asyncio
async def test_get_pod_logs_follow(service, mock_response):
    """Test getting pod logs with follow mode."""
    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = "2024-03-20 10:00:00 INFO: Starting pod"
        
        result = await service.get_pod_logs(
            "test_pod_id",
            lines=100,
            follow=True
        )
        
        assert isinstance(result, str)
        mock_request.assert_called_once_with(
            "GET",
            "pods/test_pod_id/logs",
            params={"lines": 100, "follow": "true"}
        )

@pytest.mark.asyncio
async def test_batch_create_pods():
    """Test batch pod creation."""
    mock_response = {
        "pods": [
            {"id": "pod1", "status": "pending"},
            {"id": "pod2", "status": "pending"}
        ]
    }
    
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_post.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.batch_create_pods([
            {"name": "pod1", "gpu_type": "a100"},
            {"name": "pod2", "gpu_type": "a100"}
        ])
        
        assert len(result) == 2
        assert result[0]["id"] == "pod1"
        assert result[1]["id"] == "pod2"

@pytest.mark.asyncio
async def test_batch_delete_pods():
    """Test batch pod deletion."""
    mock_response = {"status": "success"}
    
    with patch("aiohttp.ClientSession.delete", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_delete.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.batch_delete_pods(["pod1", "pod2"])
        
        assert result["status"] == "success"

@pytest.mark.asyncio
async def test_get_quotas():
    """Test getting resource quotas."""
    mock_response = {
        "gpu_hours": {"limit": 1000, "used": 500},
        "storage": {"limit": 1000, "used": 200}
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.get_quotas()
        
        assert "gpu_hours" in result
        assert "storage" in result
        assert result["gpu_hours"]["limit"] == 1000

@pytest.mark.asyncio
async def test_get_quota_usage():
    """Test getting quota usage."""
    mock_response = {
        "usage": 500,
        "limit": 1000,
        "remaining": 500
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.get_quota_usage(
            QuotaType.GPU_HOURS,
            start_date=datetime.utcnow() - timedelta(days=7)
        )
        
        assert result["usage"] == 500
        assert result["limit"] == 1000

@pytest.mark.asyncio
async def test_get_monitoring_data():
    """Test getting monitoring data."""
    mock_response = {
        "data": [
            {"timestamp": "2024-01-01T00:00:00Z", "value": 80},
            {"timestamp": "2024-01-01T00:05:00Z", "value": 85}
        ]
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.get_monitoring_data(
            "pod1",
            ResourceType.GPU_UTILIZATION,
            MonitoringInterval.FIVE_MINUTES
        )
        
        assert len(result) == 2
        assert result[0]["value"] == 80

@pytest.mark.asyncio
async def test_get_alerts():
    """Test getting monitoring alerts."""
    mock_response = {
        "alerts": [
            {
                "id": "alert1",
                "severity": "warning",
                "message": "High GPU utilization"
            }
        ]
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.get_alerts(severity="warning")
        
        assert len(result) == 1
        assert result[0]["id"] == "alert1"

def test_metric_statistics():
    """Test metric statistics calculation."""
    service = PrimeIntellectService("test_key", enable_metrics_tracking=True)
    
    # Add some test metrics
    now = datetime.utcnow()
    for i in range(5):
        service._metrics.add_metric(
            "gpu_utilization",
            80 + i,
            now - timedelta(minutes=i)
        )
    
    stats = service.get_metric_statistics(
        "gpu_utilization",
        timedelta(minutes=10)
    )
    
    assert stats is not None
    assert stats["min"] == 80
    assert stats["max"] == 84
    assert stats["avg"] == 82
    assert "std_dev" in stats

@pytest.mark.asyncio
async def test_batch_operation_status():
    """Test getting batch operation status."""
    mock_response = {
        "status": "in_progress",
        "progress": 50,
        "total": 100
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.get_batch_operation_status("op1")
        
        assert result["status"] == "in_progress"
        assert result["progress"] == 50

@pytest.mark.asyncio
async def test_cancel_batch_operation():
    """Test canceling a batch operation."""
    mock_response = {"status": "cancelled"}
    
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_post.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.cancel_batch_operation("op1")
        
        assert result["status"] == "cancelled"

@pytest.mark.asyncio
async def test_batch_operation_error_handling():
    """Test error handling in batch operations."""
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 400
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"error": "Invalid pod configuration"}
        )
        
        service = PrimeIntellectService("test_key")
        with pytest.raises(PrimeIntellectAPIError):
            await service.batch_create_pods([{"invalid": "config"}])

@pytest.mark.asyncio
async def test_quota_validation():
    """Test quota validation."""
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 403
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"error": "Quota exceeded"}
        )
        
        service = PrimeIntellectService("test_key")
        with pytest.raises(PrimeIntellectAPIError) as exc_info:
            await service.get_quota_usage(QuotaType.GPU_HOURS)
        
        assert "Quota exceeded" in str(exc_info.value)

@pytest.mark.asyncio
async def test_monitoring_data_validation():
    """Test monitoring data validation."""
    service = PrimeIntellectService("test_key")
    
    with pytest.raises(PrimeIntellectValidationError):
        await service.get_monitoring_data(
            "pod1",
            ResourceType.GPU_UTILIZATION,
            "invalid_interval"
        )

def test_metrics_history_limiting():
    """Test metrics history limiting."""
    service = PrimeIntellectService("test_key", max_history=3)
    
    # Add more metrics than the limit
    for i in range(5):
        service._metrics.add_metric("gpu_utilization", i)
    
    # Should only keep the last 3 values
    assert len(service._metrics.metrics["gpu_utilization"]) == 3
    assert service._metrics.metrics["gpu_utilization"][-1]["value"] == 4

@pytest.mark.asyncio
async def test_schedule_pod():
    """Test scheduling a pod."""
    mock_response = {
        "schedule_id": "schedule1",
        "status": "scheduled",
        "start_time": "2024-01-01T00:00:00Z"
    }
    
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_post.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        schedule = ResourceSchedule(
            schedule_type=ScheduleType.ONE_TIME,
            start_time=datetime.utcnow() + timedelta(hours=1)
        )
        
        result = await service.schedule_pod(
            pod_config={"name": "pod1", "gpu_type": "a100"},
            schedule=schedule,
            priority=PodPriority.HIGH
        )
        
        assert result["schedule_id"] == "schedule1"
        assert result["status"] == "scheduled"

@pytest.mark.asyncio
async def test_get_scheduled_pods():
    """Test getting scheduled pods."""
    mock_response = {
        "pods": [
            {
                "schedule_id": "schedule1",
                "status": "scheduled",
                "start_time": "2024-01-01T00:00:00Z"
            }
        ]
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.get_scheduled_pods(
            status="scheduled",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(days=1)
        )
        
        assert len(result) == 1
        assert result[0]["schedule_id"] == "schedule1"

@pytest.mark.asyncio
async def test_cancel_scheduled_pod():
    """Test canceling a scheduled pod."""
    mock_response = {"status": "cancelled"}
    
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_post.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.cancel_scheduled_pod("schedule1")
        
        assert result["status"] == "cancelled"

@pytest.mark.asyncio
async def test_optimize_costs():
    """Test cost optimization."""
    mock_response = {
        "savings": 100.0,
        "recommendations": [
            {"pod_id": "pod1", "action": "scale_down"}
        ]
    }
    
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_post.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        optimizer = CostOptimizer(
            strategy=OptimizationStrategy.COST,
            constraints={"max_cost": 1000.0}
        )
        
        result = await service.optimize_costs(
            optimizer=optimizer,
            pod_ids=["pod1", "pod2"]
        )
        
        assert result["savings"] == 100.0
        assert len(result["recommendations"]) == 1

@pytest.mark.asyncio
async def test_get_cost_recommendations():
    """Test getting cost recommendations."""
    mock_response = {
        "recommendations": [
            {
                "pod_id": "pod1",
                "action": "scale_down",
                "estimated_savings": 50.0
            }
        ]
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.get_cost_recommendations(
            pod_ids=["pod1"],
            strategy=OptimizationStrategy.COST
        )
        
        assert len(result) == 1
        assert result[0]["pod_id"] == "pod1"
        assert result[0]["estimated_savings"] == 50.0

@pytest.mark.asyncio
async def test_update_pod_priority():
    """Test updating pod priority."""
    mock_response = {
        "pod_id": "pod1",
        "priority": "high"
    }
    
    with patch("aiohttp.ClientSession.patch", new_callable=AsyncMock) as mock_patch:
        mock_patch.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_patch.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.update_pod_priority(
            pod_id="pod1",
            priority=PodPriority.HIGH
        )
        
        assert result["pod_id"] == "pod1"
        assert result["priority"] == "high"

@pytest.mark.asyncio
async def test_get_resource_availability():
    """Test getting resource availability."""
    mock_response = {
        "available": True,
        "resources": {
            "gpu": {"count": 5, "type": "a100"},
            "memory": {"total": "100GB", "available": "50GB"}
        }
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.get_resource_availability(
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=1),
            resource_type=ResourceType.GPU
        )
        
        assert result["available"] is True
        assert "resources" in result

@pytest.mark.asyncio
async def test_get_cost_forecast():
    """Test getting cost forecast."""
    mock_response = {
        "forecast": {
            "total_cost": 1000.0,
            "breakdown": {
                "gpu": 800.0,
                "storage": 200.0
            }
        }
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.get_cost_forecast(
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(days=7),
            pod_ids=["pod1", "pod2"]
        )
        
        assert result["forecast"]["total_cost"] == 1000.0
        assert "breakdown" in result["forecast"]

@pytest.mark.asyncio
async def test_get_resource_utilization():
    """Test getting resource utilization."""
    mock_response = {
        "utilization": {
            "gpu": 75.5,
            "memory": 60.0,
            "storage": 45.0
        }
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        service = PrimeIntellectService("test_key")
        result = await service.get_resource_utilization(
            start_time=datetime.utcnow() - timedelta(hours=1),
            end_time=datetime.utcnow(),
            resource_type=ResourceType.GPU
        )
        
        assert "utilization" in result
        assert result["utilization"]["gpu"] == 75.5

def test_resource_schedule():
    """Test ResourceSchedule class."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=1)
    recurrence = {"frequency": "daily", "interval": 1}
    
    schedule = ResourceSchedule(
        schedule_type=ScheduleType.RECURRING,
        start_time=start_time,
        end_time=end_time,
        recurrence=recurrence
    )
    
    schedule_dict = schedule.to_dict()
    assert schedule_dict["type"] == ScheduleType.RECURRING.value
    assert schedule_dict["recurrence"] == recurrence

def test_cost_optimizer():
    """Test CostOptimizer class."""
    constraints = {
        "max_cost": 1000.0,
        "min_performance": 0.8
    }
    
    optimizer = CostOptimizer(
        strategy=OptimizationStrategy.BALANCED,
        constraints=constraints
    )
    
    optimizer_dict = optimizer.to_dict()
    assert optimizer_dict["strategy"] == OptimizationStrategy.BALANCED.value
    assert optimizer_dict["constraints"] == constraints

@pytest.mark.asyncio
async def test_schedule_validation():
    """Test schedule validation."""
    service = PrimeIntellectService("test_key")
    
    with pytest.raises(PrimeIntellectValidationError):
        await service.schedule_pod(
            pod_config={"name": "pod1"},
            schedule=ResourceSchedule(
                schedule_type=ScheduleType.ONE_TIME,
                start_time=datetime.utcnow() - timedelta(hours=1)  # Past time
            )
        )

@pytest.mark.asyncio
async def test_optimizer_validation():
    """Test optimizer validation."""
    service = PrimeIntellectService("test_key")
    
    with pytest.raises(PrimeIntellectValidationError):
        await service.optimize_costs(
            optimizer=CostOptimizer(
                strategy=OptimizationStrategy.COST,
                constraints={"invalid": "constraint"}
            )
        )

@pytest.mark.asyncio
async def test_configure_scaling():
    """Test configuring scaling for a pod."""
    mock_response = {
        "status": "success",
        "scaling_config": {
            "min_instances": 1,
            "max_instances": 5,
            "target_cpu_utilization": 0.7,
            "target_memory_utilization": 0.8,
            "cooldown_period": 300,
            "policy": "automatic"
        }
    }
    
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        service = PrimeIntellectService("test_api_key")
        scaling_config = ScalingConfig(
            min_instances=1,
            max_instances=5,
            target_cpu_utilization=0.7,
            target_memory_utilization=0.8,
            cooldown_period=300,
            policy=ScalingPolicy.AUTOMATIC
        )
        
        result = await service.configure_scaling("pod1", scaling_config)
        assert result == mock_response
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_get_scaling_status():
    """Test getting scaling status of a pod."""
    mock_response = {
        "current_instances": 3,
        "target_instances": 4,
        "last_scaling_time": "2024-03-20T10:00:00Z",
        "next_scaling_time": "2024-03-20T11:00:00Z"
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        service = PrimeIntellectService("test_api_key")
        result = await service.get_scaling_status("pod1")
        assert result == mock_response
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_create_backup():
    """Test creating a backup of a pod."""
    mock_response = {
        "backup_id": "backup1",
        "status": "in_progress",
        "created_at": "2024-03-20T10:00:00Z"
    }
    
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        service = PrimeIntellectService("test_api_key")
        backup_config = BackupConfig(
            backup_type=BackupType.FULL,
            retention_days=30,
            schedule={"frequency": "daily", "time": "02:00"}
        )
        
        result = await service.create_backup("pod1", backup_config)
        assert result == mock_response
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_restore_from_backup():
    """Test restoring a pod from a backup."""
    mock_response = {
        "restore_id": "restore1",
        "status": "in_progress",
        "started_at": "2024-03-20T10:00:00Z"
    }
    
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        service = PrimeIntellectService("test_api_key")
        result = await service.restore_from_backup("pod1", "backup1")
        assert result == mock_response
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_list_backups():
    """Test listing available backups for a pod."""
    mock_response = [
        {
            "backup_id": "backup1",
            "type": "full",
            "created_at": "2024-03-20T10:00:00Z",
            "status": "completed"
        },
        {
            "backup_id": "backup2",
            "type": "incremental",
            "created_at": "2024-03-21T10:00:00Z",
            "status": "completed"
        }
    ]
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        service = PrimeIntellectService("test_api_key")
        result = await service.list_backups("pod1", BackupType.FULL)
        assert result == mock_response
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_configure_network():
    """Test configuring network settings for a pod."""
    mock_response = {
        "status": "success",
        "network_config": {
            "type": "dedicated",
            "bandwidth_limit": 1000,
            "security_groups": ["sg1", "sg2"]
        }
    }
    
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        service = PrimeIntellectService("test_api_key")
        network_config = NetworkConfig(
            network_type=NetworkType.DEDICATED,
            bandwidth_limit=1000,
            security_groups=["sg1", "sg2"]
        )
        
        result = await service.configure_network("pod1", network_config)
        assert result == mock_response
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_get_network_stats():
    """Test getting network statistics for a pod."""
    mock_response = {
        "bandwidth_usage": {
            "in": 100,
            "out": 200
        },
        "latency": 50,
        "packet_loss": 0.1,
        "connections": 1000
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        service = PrimeIntellectService("test_api_key")
        start_time = datetime.utcnow() - timedelta(hours=1)
        end_time = datetime.utcnow()
        result = await service.get_network_stats("pod1", start_time, end_time)
        assert result == mock_response
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_update_network_security():
    """Test updating security groups for a pod's network."""
    mock_response = {
        "status": "success",
        "security_groups": ["sg1", "sg2", "sg3"]
    }
    
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        service = PrimeIntellectService("test_api_key")
        result = await service.update_network_security("pod1", ["sg1", "sg2", "sg3"])
        assert result == mock_response
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_get_network_availability():
    """Test getting network availability for a specific type and region."""
    mock_response = {
        "available": True,
        "capacity": 0.8,
        "latency": 50,
        "bandwidth": 1000
    }
    
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        service = PrimeIntellectService("test_api_key")
        result = await service.get_network_availability(NetworkType.DEDICATED, "us-west-1")
        assert result == mock_response
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_scaling_config_validation():
    """Test validation of scaling configuration."""
    with pytest.raises(ValueError):
        ScalingConfig(
            min_instances=5,
            max_instances=1,  # Invalid: min > max
            target_cpu_utilization=0.7,
            target_memory_utilization=0.8,
            cooldown_period=300,
            policy=ScalingPolicy.AUTOMATIC
        )

@pytest.mark.asyncio
async def test_backup_config_validation():
    """Test validation of backup configuration."""
    with pytest.raises(ValueError):
        BackupConfig(
            backup_type=BackupType.FULL,
            retention_days=-1,  # Invalid: negative retention
            schedule={"frequency": "invalid"}  # Invalid schedule
        )

@pytest.mark.asyncio
async def test_network_config_validation():
    """Test validation of network configuration."""
    with pytest.raises(ValueError):
        NetworkConfig(
            network_type=NetworkType.DEDICATED,
            bandwidth_limit=-1  # Invalid: negative bandwidth
        ) 