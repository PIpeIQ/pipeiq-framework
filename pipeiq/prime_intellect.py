"""
Prime Intellect API integration for PipeIQ.

This module provides a service class for interacting with the Prime Intellect API,
enabling GPU instance management and monitoring.
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from .exceptions import APIError, ValidationError, NetworkError
from dataclasses import dataclass
import json

class GPUProvider(str, Enum):
    """Supported GPU providers."""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"

class PodStatus(str, Enum):
    """Pod status states."""
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"

class ResourceType(str, Enum):
    """Resource types for monitoring."""
    GPU = "gpu"
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"

class CostPeriod(str, Enum):
    """Cost tracking periods."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class QuotaType(str, Enum):
    """Resource quota types."""
    GPU_HOURS = "gpu_hours"
    STORAGE = "storage"
    NETWORK = "network"
    API_CALLS = "api_calls"

class BatchOperationStatus(str, Enum):
    """Batch operation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class MonitoringInterval(str, Enum):
    """Monitoring data collection intervals."""
    MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    HOUR = "1h"
    DAY = "1d"

class ScheduleType(str, Enum):
    """Schedule types for resource management."""
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    ON_DEMAND = "on_demand"

class OptimizationStrategy(str, Enum):
    """Cost optimization strategies."""
    PERFORMANCE = "performance"
    COST = "cost"
    BALANCED = "balanced"

class PodPriority(str, Enum):
    """Pod priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ResourceSchedule:
    """Class for managing resource schedules."""
    
    def __init__(
        self,
        schedule_type: ScheduleType,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        recurrence: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a resource schedule.

        Args:
            schedule_type: Type of schedule
            start_time: When the schedule should start
            end_time: Optional end time for the schedule
            recurrence: Optional recurrence pattern
        """
        self.schedule_type = schedule_type
        self.start_time = start_time
        self.end_time = end_time
        self.recurrence = recurrence or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schedule to dictionary format."""
        return {
            "type": self.schedule_type.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "recurrence": self.recurrence
        }

class CostOptimizer:
    """Class for optimizing resource costs."""
    
    def __init__(
        self,
        strategy: OptimizationStrategy,
        constraints: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize cost optimizer.

        Args:
            strategy: Optimization strategy
            constraints: Optional optimization constraints
        """
        self.strategy = strategy
        self.constraints = constraints or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert optimizer to dictionary format."""
        return {
            "strategy": self.strategy.value,
            "constraints": self.constraints
        }

class PrimeIntellectError(Exception):
    """Base exception for Prime Intellect related errors."""
    pass

class PrimeIntellectAPIError(PrimeIntellectError):
    """Exception raised for API-related errors."""
    pass

class PrimeIntellectValidationError(PrimeIntellectError):
    """Exception raised for validation errors."""
    pass

class PrimeIntellectNetworkError(PrimeIntellectError):
    """Exception raised for network-related errors."""
    pass

class ResourceMetrics:
    """Class for tracking resource metrics."""
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize metrics tracking.

        Args:
            max_history: Maximum number of historical values to keep
        """
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.last_update: Dict[str, datetime] = {}
        self.max_history = max_history
    
    def add_metric(self, resource_type: str, value: float, timestamp: Optional[datetime] = None):
        """Add a metric value."""
        if resource_type not in self.metrics:
            self.metrics[resource_type] = []
        
        self.metrics[resource_type].append({
            "value": value,
            "timestamp": timestamp or datetime.utcnow()
        })
        
        # Trim history if needed
        if len(self.metrics[resource_type]) > self.max_history:
            self.metrics[resource_type] = self.metrics[resource_type][-self.max_history:]
        
        self.last_update[resource_type] = datetime.utcnow()
    
    def get_latest(self, resource_type: str) -> Optional[float]:
        """Get the latest metric value."""
        if resource_type not in self.metrics or not self.metrics[resource_type]:
            return None
        return self.metrics[resource_type][-1]["value"]
    
    def get_average(self, resource_type: str, period: timedelta) -> Optional[float]:
        """Get the average metric value over a period."""
        if resource_type not in self.metrics:
            return None
        
        now = datetime.utcnow()
        values = [
            m["value"] for m in self.metrics[resource_type]
            if now - m["timestamp"] <= period
        ]
        
        return sum(values) / len(values) if values else None
    
    def get_statistics(
        self,
        resource_type: str,
        period: timedelta
    ) -> Optional[Dict[str, float]]:
        """
        Get statistical metrics over a period.

        Args:
            resource_type: Type of resource
            period: Time period

        Returns:
            Dictionary containing min, max, avg, and std dev
        """
        if resource_type not in self.metrics:
            return None
        
        now = datetime.utcnow()
        values = [
            m["value"] for m in self.metrics[resource_type]
            if now - m["timestamp"] <= period
        ]
        
        if not values:
            return None
        
        import statistics
        return {
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0
        }

class ScalingPolicy(Enum):
    """Scaling policy types for pods."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"

class BackupType(Enum):
    """Types of backup operations."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

class NetworkType(Enum):
    """Types of network configurations."""
    STANDARD = "standard"
    DEDICATED = "dedicated"
    ISOLATED = "isolated"

@dataclass
class ScalingConfig:
    """Configuration for pod scaling."""
    min_instances: int
    max_instances: int
    target_cpu_utilization: float
    target_memory_utilization: float
    cooldown_period: int  # in seconds
    policy: ScalingPolicy

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "target_cpu_utilization": self.target_cpu_utilization,
            "target_memory_utilization": self.target_memory_utilization,
            "cooldown_period": self.cooldown_period,
            "policy": self.policy.value
        }

@dataclass
class BackupConfig:
    """Configuration for backup operations."""
    backup_type: BackupType
    retention_days: int
    schedule: Optional[Dict[str, Any]] = None
    include_volumes: bool = True
    include_config: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "backup_type": self.backup_type.value,
            "retention_days": self.retention_days,
            "schedule": self.schedule,
            "include_volumes": self.include_volumes,
            "include_config": self.include_config
        }

@dataclass
class NetworkConfig:
    """Configuration for network settings."""
    network_type: NetworkType
    bandwidth_limit: Optional[int] = None  # in Mbps
    security_groups: Optional[List[str]] = None
    vpc_id: Optional[str] = None
    subnet_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "network_type": self.network_type.value,
            "bandwidth_limit": self.bandwidth_limit,
            "security_groups": self.security_groups,
            "vpc_id": self.vpc_id,
            "subnet_id": self.subnet_id
        }

class PrimeIntellectService:
    """Service class for interacting with the Prime Intellect API."""

    BASE_URL = "https://api.primeintellect.ai/v1"
    
    def __init__(
        self,
        api_key: str,
        session: Optional[aiohttp.ClientSession] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        enable_metrics_tracking: bool = True,
        max_history: int = 1000
    ):
        """
        Initialize the Prime Intellect service.

        Args:
            api_key: Prime Intellect API key
            session: Optional aiohttp ClientSession
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            enable_metrics_tracking: Whether to enable local metrics tracking
            max_history: Maximum number of historical values to keep
        """
        self.api_key = api_key
        self._session = session
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self._metrics = ResourceMetrics(max_history) if enable_metrics_tracking else None

    async def __aenter__(self):
        """Create aiohttp session if not provided."""
        if not self._session:
            self._session = aiohttp.ClientSession(headers=self._headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session if we created it."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Make an API request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request payload
            params: Query parameters

        Returns:
            API response data

        Raises:
            PrimeIntellectAPIError: For API-related errors
            PrimeIntellectNetworkError: For network-related errors
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with self._session.request(
                    method,
                    url,
                    json=data,
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 400:
                        error_data = await response.json()
                        raise PrimeIntellectValidationError(
                            f"Validation error: {error_data.get('message', 'Unknown error')}"
                        )
                    elif response.status == 401:
                        raise PrimeIntellectAPIError("Invalid API key")
                    elif response.status == 403:
                        raise PrimeIntellectAPIError("Insufficient permissions")
                    elif response.status == 404:
                        raise PrimeIntellectAPIError("Resource not found")
                    elif response.status == 429:
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                            continue
                        raise PrimeIntellectAPIError("Rate limit exceeded")
                    else:
                        raise PrimeIntellectAPIError(
                            f"API error: {response.status} - {await response.text()}"
                        )
            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise PrimeIntellectNetworkError(f"Network error: {str(e)}")

    async def get_gpu_availability(
        self,
        provider: Optional[GPUProvider] = None,
        region: Optional[str] = None
    ) -> List[Dict]:
        """
        Get GPU availability information.

        Args:
            provider: Optional GPU provider to filter by
            region: Optional region to filter by

        Returns:
            List of available GPU configurations
        """
        params = {}
        if provider:
            params["provider"] = provider.value
        if region:
            params["region"] = region

        return await self._make_request("GET", "availability/gpu", params=params)

    async def get_cluster_availability(
        self,
        provider: Optional[GPUProvider] = None,
        region: Optional[str] = None
    ) -> List[Dict]:
        """
        Get cluster availability information.

        Args:
            provider: Optional GPU provider to filter by
            region: Optional region to filter by

        Returns:
            List of available cluster configurations
        """
        params = {}
        if provider:
            params["provider"] = provider.value
        if region:
            params["region"] = region

        return await self._make_request("GET", "availability/cluster", params=params)

    async def create_pod(
        self,
        name: str,
        gpu_type: str,
        provider: GPUProvider,
        region: str,
        image: str,
        command: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Create a new pod.

        Args:
            name: Pod name
            gpu_type: GPU type
            provider: GPU provider
            region: Region
            image: Container image
            command: Optional command to run
            env: Optional environment variables

        Returns:
            Created pod information
        """
        data = {
            "name": name,
            "gpu_type": gpu_type,
            "provider": provider.value,
            "region": region,
            "image": image
        }
        if command:
            data["command"] = command
        if env:
            data["env"] = env

        return await self._make_request("POST", "pods", data=data)

    async def get_pods(
        self,
        status: Optional[PodStatus] = None,
        provider: Optional[GPUProvider] = None
    ) -> List[Dict]:
        """
        Get list of pods.

        Args:
            status: Optional status to filter by
            provider: Optional provider to filter by

        Returns:
            List of pods
        """
        params = {}
        if status:
            params["status"] = status.value
        if provider:
            params["provider"] = provider.value

        return await self._make_request("GET", "pods", params=params)

    async def get_pod(self, pod_id: str) -> Dict:
        """
        Get pod details.

        Args:
            pod_id: Pod ID

        Returns:
            Pod details
        """
        return await self._make_request("GET", f"pods/{pod_id}")

    async def delete_pod(self, pod_id: str) -> Dict:
        """
        Delete a pod.

        Args:
            pod_id: Pod ID

        Returns:
            Deletion confirmation
        """
        return await self._make_request("DELETE", f"pods/{pod_id}")

    async def get_pod_status(self, pod_id: str) -> Dict:
        """
        Get pod status.

        Args:
            pod_id: Pod ID

        Returns:
            Pod status information
        """
        return await self._make_request("GET", f"pods/{pod_id}/status")

    async def get_pod_history(self, pod_id: str) -> List[Dict]:
        """
        Get pod history.

        Args:
            pod_id: Pod ID

        Returns:
            List of pod history events
        """
        return await self._make_request("GET", f"pods/{pod_id}/history")

    async def add_metrics(
        self,
        pod_id: str,
        metrics: Dict[str, Union[int, float, str]]
    ) -> Dict:
        """
        Add metrics for a pod.

        Args:
            pod_id: Pod ID
            metrics: Metrics data

        Returns:
            Confirmation of metrics addition
        """
        return await self._make_request(
            "POST",
            f"pools/{pod_id}/metrics",
            data={"metrics": metrics}
        )

    async def get_resource_usage(
        self,
        pod_id: str,
        resource_type: ResourceType,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get resource usage metrics for a pod.

        Args:
            pod_id: Pod ID
            resource_type: Type of resource to monitor
            start_time: Optional start time for metrics
            end_time: Optional end time for metrics

        Returns:
            List of resource usage metrics
        """
        params = {"resource_type": resource_type.value}
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()

        return await self._make_request(
            "GET",
            f"pods/{pod_id}/resources",
            params=params
        )

    async def get_cost_estimate(
        self,
        gpu_type: str,
        provider: GPUProvider,
        region: str,
        duration_hours: float
    ) -> Dict[str, float]:
        """
        Get cost estimate for GPU usage.

        Args:
            gpu_type: GPU type
            provider: GPU provider
            region: Region
            duration_hours: Expected duration in hours

        Returns:
            Cost estimate in different currencies
        """
        return await self._make_request(
            "GET",
            "costs/estimate",
            params={
                "gpu_type": gpu_type,
                "provider": provider.value,
                "region": region,
                "duration_hours": duration_hours
            }
        )

    async def get_cost_history(
        self,
        pod_id: Optional[str] = None,
        period: CostPeriod = CostPeriod.DAILY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cost history for pods.

        Args:
            pod_id: Optional pod ID to filter by
            period: Cost period
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            List of cost records
        """
        params = {"period": period.value}
        if pod_id:
            params["pod_id"] = pod_id
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        return await self._make_request(
            "GET",
            "costs/history",
            params=params
        )

    async def scale_pod(
        self,
        pod_id: str,
        gpu_count: int,
        wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """
        Scale a pod's GPU resources.

        Args:
            pod_id: Pod ID
            gpu_count: New GPU count
            wait_for_completion: Whether to wait for scaling to complete

        Returns:
            Updated pod information
        """
        result = await self._make_request(
            "POST",
            f"pods/{pod_id}/scale",
            data={"gpu_count": gpu_count}
        )

        if wait_for_completion:
            while True:
                status = await self.get_pod_status(pod_id)
                if status["status"] == PodStatus.RUNNING.value:
                    break
                await asyncio.sleep(5)

        return result

    async def get_pod_logs(
        self,
        pod_id: str,
        lines: int = 100,
        follow: bool = False
    ) -> Union[str, List[str]]:
        """
        Get pod logs.

        Args:
            pod_id: Pod ID
            lines: Number of lines to retrieve
            follow: Whether to follow the logs

        Returns:
            Pod logs as string or list of strings
        """
        params = {"lines": lines}
        if follow:
            params["follow"] = "true"

        return await self._make_request(
            "GET",
            f"pods/{pod_id}/logs",
            params=params
        )

    async def get_health_check(self) -> Dict[str, Any]:
        """
        Get API health check information.

        Returns:
            Health check information
        """
        return await self._make_request("GET", "health")

    async def get_api_status(self) -> Dict[str, Any]:
        """
        Get API status information.

        Returns:
            API status information
        """
        return await self._make_request("GET", "status")

    def track_metric(self, resource_type: str, value: float):
        """
        Track a metric locally.

        Args:
            resource_type: Type of resource
            value: Metric value
        """
        if self._metrics:
            self._metrics.add_metric(resource_type, value)

    def get_latest_metric(self, resource_type: str) -> Optional[float]:
        """
        Get the latest tracked metric value.

        Args:
            resource_type: Type of resource

        Returns:
            Latest metric value or None if not available
        """
        if self._metrics:
            return self._metrics.get_latest(resource_type)
        return None

    def get_average_metric(
        self,
        resource_type: str,
        period: timedelta
    ) -> Optional[float]:
        """
        Get the average tracked metric value over a period.

        Args:
            resource_type: Type of resource
            period: Time period

        Returns:
            Average metric value or None if not available
        """
        if self._metrics:
            return self._metrics.get_average(resource_type, period)
        return None

    async def batch_create_pods(
        self,
        pod_configs: List[Dict[str, Any]],
        wait_for_completion: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Create multiple pods in a batch operation.

        Args:
            pod_configs: List of pod configurations
            wait_for_completion: Whether to wait for all pods to be ready

        Returns:
            List of created pods
        """
        result = await self._make_request(
            "POST",
            "pods/batch",
            data={"pods": pod_configs}
        )

        if wait_for_completion:
            pod_ids = [pod["id"] for pod in result["pods"]]
            while True:
                statuses = await asyncio.gather(*[
                    self.get_pod_status(pod_id)
                    for pod_id in pod_ids
                ])
                if all(s["status"] == PodStatus.RUNNING.value for s in statuses):
                    break
                await asyncio.sleep(5)

        return result["pods"]

    async def batch_delete_pods(
        self,
        pod_ids: List[str],
        wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """
        Delete multiple pods in a batch operation.

        Args:
            pod_ids: List of pod IDs to delete
            wait_for_completion: Whether to wait for all pods to be deleted

        Returns:
            Batch operation result
        """
        result = await self._make_request(
            "DELETE",
            "pods/batch",
            data={"pod_ids": pod_ids}
        )

        if wait_for_completion:
            while True:
                try:
                    statuses = await asyncio.gather(*[
                        self.get_pod_status(pod_id)
                        for pod_id in pod_ids
                    ])
                    if all(s["status"] == PodStatus.TERMINATED.value for s in statuses):
                        break
                except PrimeIntellectAPIError:
                    # Pods not found means they're deleted
                    break
                await asyncio.sleep(5)

        return result

    async def get_quotas(self) -> Dict[str, Dict[str, Any]]:
        """
        Get current resource quotas.

        Returns:
            Dictionary of quota information by type
        """
        return await self._make_request("GET", "quotas")

    async def get_quota_usage(
        self,
        quota_type: QuotaType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get quota usage information.

        Args:
            quota_type: Type of quota to check
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Quota usage information
        """
        params = {"type": quota_type.value}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        return await self._make_request(
            "GET",
            "quotas/usage",
            params=params
        )

    async def get_monitoring_data(
        self,
        pod_id: str,
        resource_type: ResourceType,
        interval: MonitoringInterval,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get detailed monitoring data.

        Args:
            pod_id: Pod ID
            resource_type: Type of resource to monitor
            interval: Data collection interval
            start_time: Optional start time
            end_time: Optional end time

        Returns:
            List of monitoring data points
        """
        params = {
            "resource_type": resource_type.value,
            "interval": interval.value
        }
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()

        return await self._make_request(
            "GET",
            f"pods/{pod_id}/monitoring",
            params=params
        )

    async def get_alerts(
        self,
        pod_id: Optional[str] = None,
        severity: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get monitoring alerts.

        Args:
            pod_id: Optional pod ID to filter by
            severity: Optional severity level to filter by
            start_time: Optional start time
            end_time: Optional end time

        Returns:
            List of alerts
        """
        params = {}
        if pod_id:
            params["pod_id"] = pod_id
        if severity:
            params["severity"] = severity
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()

        return await self._make_request(
            "GET",
            "alerts",
            params=params
        )

    def get_metric_statistics(
        self,
        resource_type: str,
        period: timedelta
    ) -> Optional[Dict[str, float]]:
        """
        Get statistical metrics over a period.

        Args:
            resource_type: Type of resource
            period: Time period

        Returns:
            Dictionary containing min, max, avg, and std dev
        """
        if self._metrics:
            return self._metrics.get_statistics(resource_type, period)
        return None

    async def get_batch_operation_status(
        self,
        operation_id: str
    ) -> Dict[str, Any]:
        """
        Get status of a batch operation.

        Args:
            operation_id: Batch operation ID

        Returns:
            Operation status information
        """
        return await self._make_request(
            "GET",
            f"batch/{operation_id}"
        )

    async def cancel_batch_operation(
        self,
        operation_id: str
    ) -> Dict[str, Any]:
        """
        Cancel a batch operation.

        Args:
            operation_id: Batch operation ID

        Returns:
            Cancellation confirmation
        """
        return await self._make_request(
            "POST",
            f"batch/{operation_id}/cancel"
        )

    async def schedule_pod(
        self,
        pod_config: Dict[str, Any],
        schedule: ResourceSchedule,
        priority: PodPriority = PodPriority.MEDIUM
    ) -> Dict[str, Any]:
        """
        Schedule a pod for future creation.

        Args:
            pod_config: Pod configuration
            schedule: Resource schedule
            priority: Pod priority level

        Returns:
            Scheduled pod information
        """
        data = {
            "pod_config": pod_config,
            "schedule": schedule.to_dict(),
            "priority": priority.value
        }
        
        return await self._make_request(
            "POST",
            "pods/schedule",
            data=data
        )

    async def get_scheduled_pods(
        self,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of scheduled pods.

        Args:
            status: Optional status filter
            start_time: Optional start time filter
            end_time: Optional end time filter

        Returns:
            List of scheduled pods
        """
        params = {}
        if status:
            params["status"] = status
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()

        return await self._make_request(
            "GET",
            "pods/scheduled",
            params=params
        )

    async def cancel_scheduled_pod(
        self,
        schedule_id: str
    ) -> Dict[str, Any]:
        """
        Cancel a scheduled pod.

        Args:
            schedule_id: Schedule ID

        Returns:
            Cancellation confirmation
        """
        return await self._make_request(
            "POST",
            f"pods/scheduled/{schedule_id}/cancel"
        )

    async def optimize_costs(
        self,
        optimizer: CostOptimizer,
        pod_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Optimize costs for pods.

        Args:
            optimizer: Cost optimizer configuration
            pod_ids: Optional list of pod IDs to optimize

        Returns:
            Optimization results
        """
        data = {
            "optimizer": optimizer.to_dict()
        }
        if pod_ids:
            data["pod_ids"] = pod_ids

        return await self._make_request(
            "POST",
            "pods/optimize",
            data=data
        )

    async def get_cost_recommendations(
        self,
        pod_ids: Optional[List[str]] = None,
        strategy: Optional[OptimizationStrategy] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cost optimization recommendations.

        Args:
            pod_ids: Optional list of pod IDs
            strategy: Optional optimization strategy

        Returns:
            List of recommendations
        """
        params = {}
        if pod_ids:
            params["pod_ids"] = pod_ids
        if strategy:
            params["strategy"] = strategy.value

        return await self._make_request(
            "GET",
            "pods/cost-recommendations",
            params=params
        )

    async def update_pod_priority(
        self,
        pod_id: str,
        priority: PodPriority
    ) -> Dict[str, Any]:
        """
        Update pod priority.

        Args:
            pod_id: Pod ID
            priority: New priority level

        Returns:
            Updated pod information
        """
        return await self._make_request(
            "PATCH",
            f"pods/{pod_id}/priority",
            data={"priority": priority.value}
        )

    async def get_resource_availability(
        self,
        start_time: datetime,
        end_time: datetime,
        resource_type: Optional[ResourceType] = None
    ) -> Dict[str, Any]:
        """
        Get resource availability for a time period.

        Args:
            start_time: Start time
            end_time: End time
            resource_type: Optional resource type filter

        Returns:
            Resource availability information
        """
        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        if resource_type:
            params["resource_type"] = resource_type.value

        return await self._make_request(
            "GET",
            "resources/availability",
            params=params
        )

    async def get_cost_forecast(
        self,
        start_time: datetime,
        end_time: datetime,
        pod_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get cost forecast for a time period.

        Args:
            start_time: Start time
            end_time: End time
            pod_ids: Optional list of pod IDs

        Returns:
            Cost forecast information
        """
        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        if pod_ids:
            params["pod_ids"] = pod_ids

        return await self._make_request(
            "GET",
            "costs/forecast",
            params=params
        )

    async def get_resource_utilization(
        self,
        start_time: datetime,
        end_time: datetime,
        resource_type: Optional[ResourceType] = None
    ) -> Dict[str, Any]:
        """
        Get resource utilization for a time period.

        Args:
            start_time: Start time
            end_time: End time
            resource_type: Optional resource type filter

        Returns:
            Resource utilization information
        """
        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        if resource_type:
            params["resource_type"] = resource_type.value

        return await self._make_request(
            "GET",
            "resources/utilization",
            params=params
        )

    async def configure_scaling(
        self,
        pod_id: str,
        scaling_config: ScalingConfig
    ) -> Dict[str, Any]:
        """Configure scaling for a pod."""
        url = f"{self.BASE_URL}/pods/{pod_id}/scaling"
        async with self._session.post(url, json=scaling_config.to_dict()) as response:
            if response.status != 200:
                raise PrimeIntellectError(f"Failed to configure scaling: {await response.text()}")
            return await response.json()

    async def get_scaling_status(self, pod_id: str) -> Dict[str, Any]:
        """Get current scaling status of a pod."""
        url = f"{self.BASE_URL}/pods/{pod_id}/scaling/status"
        async with self._session.get(url) as response:
            if response.status != 200:
                raise PrimeIntellectError(f"Failed to get scaling status: {await response.text()}")
            return await response.json()

    async def create_backup(
        self,
        pod_id: str,
        backup_config: BackupConfig
    ) -> Dict[str, Any]:
        """Create a backup of a pod."""
        url = f"{self.BASE_URL}/pods/{pod_id}/backup"
        async with self._session.post(url, json=backup_config.to_dict()) as response:
            if response.status != 200:
                raise PrimeIntellectError(f"Failed to create backup: {await response.text()}")
            return await response.json()

    async def restore_from_backup(
        self,
        pod_id: str,
        backup_id: str,
        restore_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Restore a pod from a backup."""
        url = f"{self.BASE_URL}/pods/{pod_id}/restore"
        data = {"backup_id": backup_id}
        if restore_config:
            data.update(restore_config)
        async with self._session.post(url, json=data) as response:
            if response.status != 200:
                raise PrimeIntellectError(f"Failed to restore from backup: {await response.text()}")
            return await response.json()

    async def list_backups(
        self,
        pod_id: str,
        backup_type: Optional[BackupType] = None
    ) -> List[Dict[str, Any]]:
        """List available backups for a pod."""
        url = f"{self.BASE_URL}/pods/{pod_id}/backups"
        params = {}
        if backup_type:
            params["type"] = backup_type.value
        async with self._session.get(url, params=params) as response:
            if response.status != 200:
                raise PrimeIntellectError(f"Failed to list backups: {await response.text()}")
            return await response.json()

    async def configure_network(
        self,
        pod_id: str,
        network_config: NetworkConfig
    ) -> Dict[str, Any]:
        """Configure network settings for a pod."""
        url = f"{self.BASE_URL}/pods/{pod_id}/network"
        async with self._session.post(url, json=network_config.to_dict()) as response:
            if response.status != 200:
                raise PrimeIntellectError(f"Failed to configure network: {await response.text()}")
            return await response.json()

    async def get_network_stats(
        self,
        pod_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get network statistics for a pod."""
        url = f"{self.BASE_URL}/pods/{pod_id}/network/stats"
        params = {}
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
        async with self._session.get(url, params=params) as response:
            if response.status != 200:
                raise PrimeIntellectError(f"Failed to get network stats: {await response.text()}")
            return await response.json()

    async def update_network_security(
        self,
        pod_id: str,
        security_groups: List[str]
    ) -> Dict[str, Any]:
        """Update security groups for a pod's network."""
        url = f"{self.BASE_URL}/pods/{pod_id}/network/security"
        async with self._session.post(url, json={"security_groups": security_groups}) as response:
            if response.status != 200:
                raise PrimeIntellectError(f"Failed to update network security: {await response.text()}")
            return await response.json()

    async def get_network_availability(
        self,
        network_type: NetworkType,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get network availability for a specific type and region."""
        url = f"{self.BASE_URL}/network/availability"
        params = {"type": network_type.value}
        if region:
            params["region"] = region
        async with self._session.get(url, params=params) as response:
            if response.status != 200:
                raise PrimeIntellectError(f"Failed to get network availability: {await response.text()}")
            return await response.json() 