"""
Data models for the Prime Intellect API responses.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any, Union


class GPUType(str, Enum):
    """GPU types supported by Prime Intellect API."""
    CPU_NODE = "CPU_NODE"
    A10_24GB = "A10_24GB"
    A100_80GB = "A100_80GB"
    A100_40GB = "A100_40GB"
    A30_24GB = "A30_24GB"
    A40_48GB = "A40_48GB"
    B200_180GB = "B200_180GB"
    RTX3070_8GB = "RTX3070_8GB"
    RTX3080_10GB = "RTX3080_10GB"
    RTX3080Ti_12GB = "RTX3080Ti_12GB"
    RTX3090_24GB = "RTX3090_24GB"
    RTX3090Ti_24GB = "RTX3090Ti_24GB"
    RTX4070Ti_12GB = "RTX4070Ti_12GB"
    RTX4080_16GB = "RTX4080_16GB"
    RTX4080Ti_16GB = "RTX4080Ti_16GB"
    RTX4090_24GB = "RTX4090_24GB"
    RTX5090_32GB = "RTX5090_32GB"
    H100_80GB = "H100_80GB"
    H200_96GB = "H200_96GB"
    GH200_96GB = "GH200_96GB"
    H200_141GB = "H200_141GB"
    GH200_480GB = "GH200_480GB"
    GH200_624GB = "GH200_624GB"
    L4_24GB = "L4_24GB"
    L40_48GB = "L40_48GB"
    L40S_48GB = "L40S_48GB"
    RTX4000_8GB = "RTX4000_8GB"
    RTX5000_16GB = "RTX5000_16GB"
    RTX6000_24GB = "RTX6000_24GB"
    RTX8000_48GB = "RTX8000_48GB"
    RTX2000Ada_16GB = "RTX2000Ada_16GB"
    RTX4000Ada_20GB = "RTX4000Ada_20GB"
    RTX5000Ada_32GB = "RTX5000Ada_32GB"
    RTX6000Ada_48GB = "RTX6000Ada_48GB"
    A2000_6GB = "A2000_6GB"
    A4000_16GB = "A4000_16GB"
    A4500_20GB = "A4500_20GB"
    A5000_24GB = "A5000_24GB"
    A6000_48GB = "A6000_48GB"
    V100_16GB = "V100_16GB"
    V100_32GB = "V100_32GB"
    P100_16GB = "P100_16GB"
    T4_16GB = "T4_16GB"
    P4_8GB = "P4_8GB"
    P40_24GB = "P40_24GB"


class SocketType(str, Enum):
    """Socket types for GPUs - from API documentation."""
    PCIE = "PCIe"
    SXM2 = "SXM2"
    SXM3 = "SXM3"
    SXM4 = "SXM4"
    SXM5 = "SXM5"
    SXM6 = "SXM6"


class SecurityType(str, Enum):
    """Security types - from API documentation."""
    SECURE_CLOUD = "secure_cloud"
    COMMUNITY_CLOUD = "community_cloud"


class StockStatus(str, Enum):
    """Stock status values - from API documentation."""
    AVAILABLE = "Available"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    UNAVAILABLE = "Unavailable"


class Provider(str, Enum):
    """Provider values - from API documentation."""
    RUNPOD = "runpod"
    FLUIDSTACK = "fluidstack"
    LAMBDALABS = "lambdalabs"
    HYPERSTACK = "hyperstack"
    OBLIVUS = "oblivus"
    CUDOCOMPUTE = "cudocompute"
    SCALEWAY = "scaleway"
    TENSORDOCK = "tensordock"
    DATACRUNCH = "datacrunch"
    LATITUDE = "latitude"
    CRUSOECLOUD = "crusoecloud"
    MASSEDCOMPUTE = "massedcompute"
    AKASH = "akash"
    PRIMEINTELLECT = "primeintellect"
    PRIMECOMPUTE = "primecompute"
    DC_IMPALA = "dc_impala"
    DC_KUDU = "dc_kudu"
    DC_ROAN = "dc_roan"
    NEBIUS = "nebius"
    DC_ELAND = "dc_eland"
    DC_WILDEBEEST = "dc_wildebeest"


@dataclass
class ResourceSpec:
    """Resource specification (disk, vcpu, memory)."""
    min_count: Optional[int] = None
    default_count: Optional[int] = None
    max_count: Optional[int] = None
    price_per_unit: Optional[float] = None
    step: Optional[int] = None
    default_included_in_price: Optional[bool] = None
    additional_info: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceSpec":
        """Create ResourceSpec from dictionary."""
        return cls(
            min_count=data.get("minCount"),
            default_count=data.get("defaultCount"),
            max_count=data.get("maxCount"),
            price_per_unit=data.get("pricePerUnit"),
            step=data.get("step"),
            default_included_in_price=data.get("defaultIncludedInPrice"),
            additional_info=data.get("additionalInfo"),
        )


@dataclass
class Pricing:
    """Pricing information for GPU offers."""
    on_demand: Optional[float] = None
    community_price: Optional[float] = None
    is_variable: Optional[bool] = None
    currency: str = "USD"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pricing":
        """Create Pricing from dictionary."""
        return cls(
            on_demand=data.get("onDemand"),
            community_price=data.get("communityPrice"),
            is_variable=data.get("isVariable"),
            currency=data.get("currency", "USD"),
        )


@dataclass
class GPUAvailability:
    """GPU availability information."""
    cloud_id: str
    gpu_type: str  # Using string for flexibility
    socket: Optional[SocketType] = None
    provider: Optional[Provider] = None
    data_center: Optional[str] = None
    country: Optional[str] = None
    gpu_count: Optional[int] = None
    gpu_memory: Optional[int] = None
    disk: Optional[ResourceSpec] = None
    vcpu: Optional[ResourceSpec] = None
    memory: Optional[ResourceSpec] = None
    internet_speed: Optional[int] = None
    interconnect: Optional[int] = None
    interconnect_type: Optional[str] = None
    provisioning_time: Optional[int] = None
    stock_status: Optional[StockStatus] = None
    security: Optional[SecurityType] = None
    prices: Optional[Pricing] = None
    images: Optional[List[str]] = None
    is_spot: Optional[bool] = None
    prepaid_time: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GPUAvailability":
        """Create GPUAvailability from dictionary."""
        # Helper function to safely convert to enum
        def safe_enum(enum_class, value):
            if value is None:
                return None
            try:
                return enum_class(value)
            except ValueError:
                return None  # Unknown value, return None
        
        prices = None
        if data.get("prices"):
            prices = Pricing.from_dict(data["prices"])

        disk = None
        if data.get("disk"):
            disk = ResourceSpec.from_dict(data["disk"])

        vcpu = None
        if data.get("vcpu"):
            vcpu = ResourceSpec.from_dict(data["vcpu"])

        memory = None
        if data.get("memory"):
            memory = ResourceSpec.from_dict(data["memory"])

        return cls(
            cloud_id=data["cloudId"],
            gpu_type=data.get("gpuType", ""),
            socket=safe_enum(SocketType, data.get("socket")),
            provider=safe_enum(Provider, data.get("provider")),
            data_center=data.get("dataCenter"),
            country=data.get("country"),
            gpu_count=data.get("gpuCount"),
            gpu_memory=data.get("gpuMemory"),
            disk=disk,
            vcpu=vcpu,
            memory=memory,
            internet_speed=data.get("internetSpeed"),
            interconnect=data.get("interconnect"),
            interconnect_type=data.get("interconnectType"),
            provisioning_time=data.get("provisioningTime"),
            stock_status=safe_enum(StockStatus, data.get("stockStatus")),
            security=safe_enum(SecurityType, data.get("security")),
            prices=prices,
            images=data.get("images"),
            is_spot=data.get("isSpot"),
            prepaid_time=data.get("prepaidTime"),
        ) 