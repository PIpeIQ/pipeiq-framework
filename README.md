# PIPEIQ Framework

> A decentralized agent protocol to connect AI tools across Web2 and Web3—models, MCP servers, decentralized compute, and more.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Solana](https://img.shields.io/badge/built%20on-Solana-orange)](https://solana.com/)

---

## Overview
PIPEIQ is an open-source framework that enables developers to seamlessly connect and orchestrate AI tools across the Web2 and Web3 ecosystems. It abstracts away the complexities of identity, messaging, and orchestration by providing standardized primitives for agent coordination, tool invocation, and cross-network integration.

With native support for models, MCP servers, decentralized compute providers, and on-chain identity frameworks, PIPEIQ aims to serve as a universal protocol layer for the AI economy—supporting autonomous, composable, and verifiable AI agents.

---

## Key Features

### 🔗 Web2 + Web3 Interop
- Unified routing for AI tools—OpenAI, HuggingFace, MCP servers, Filecoin compute, etc.
- Tool registration and capability exposure via agent profiles

### 🔑 Identity & Wallets
- On-chain agent identities (machine & human-aligned)
- Verifiable credentials & optional proof-of-personhood

### 📊 Staking & Reputation
- Reputation-linked staking mechanisms
- Trust scores based on usage history & task completion

### ⚖️ Agent Task Market
- Publish & bid on decentralized agent tasks
- Support for escrow, arbitration, and bounty resolution

### 🌐 Context Anchoring
- Persistent agent memory using IPFS / Arweave
- Modular context schemas for task recall & chaining

### 🤷 Intent Signaling & Routing
- Message schema for goal-driven task delegation
- Modular routing system between agents & services

### Persona Integration

The Persona integration provides a comprehensive interface for identity verification, including government ID verification, selfie checks, database lookups, and more.

#### Setup

```python
from pipeiq import PersonaService, InquiryConfig, VerificationType, ReportType

# Initialize the Persona service
persona = PersonaService(
    api_key="your_api_key",
    environment="sandbox"  # or "production"
)

# Use async context manager for automatic session management
async with persona as service:
    # Create an inquiry
    config = InquiryConfig(
        template_id="your_template_id",
        reference_id="user_123",
        metadata={"user_id": "123"},
        expires_at=datetime.now() + timedelta(hours=1),
        redirect_url="https://your-app.com/redirect",
        webhook_url="https://your-app.com/webhook"
    )
    inquiry = await service.create_inquiry(config)
```

#### Identity Verification

```python
# Create a government ID verification
verification_config = VerificationConfig(
    type=VerificationType.GOVERNMENT_ID,
    country="US",
    document_type="drivers_license",
    metadata={"document_number": "123456"}
)
verification = await service.create_verification(inquiry_id, verification_config)

# Create a selfie verification
selfie_config = VerificationConfig(
    type=VerificationType.SELFIE,
    metadata={"liveness_check": True}
)
selfie = await service.create_verification(inquiry_id, selfie_config)
```

#### Reports and Checks

```python
# Create a watchlist report
report_config = ReportConfig(
    type=ReportType.WATCHLIST,
    metadata={"search_type": "global"}
)
report = await service.create_report(inquiry_id, report_config)

# Get report results
report_details = await service.get_report(inquiry_id, report_id)
```

#### Inquiry Management

```python
# List all inquiries
inquiries = await service.list_inquiries(
    page_size=10,
    page_number=1,
    status=InquiryStatus.COMPLETED
)

# Approve an inquiry
await service.approve_inquiry(inquiry_id)

# Decline an inquiry
await service.decline_inquiry(inquiry_id)

# Mark for manual review
await service.mark_for_review(inquiry_id)
```

#### Error Handling

```python
from pipeiq import PersonaError, ConnectionError, VerificationError, ReportError

try:
    inquiry = await service.create_inquiry(config)
except ConnectionError as e:
    print(f"Connection error: {e}")
except VerificationError as e:
    print(f"Verification error: {e}")
except ReportError as e:
    print(f"Report error: {e}")
except PersonaError as e:
    print(f"General error: {e}")
```

### Document Verification

The Persona integration supports comprehensive document verification with various document types:

```python
from pipeiq import PersonaService, DocumentConfig, DocumentType

async with PersonaService(api_key="your_api_key") as persona:
    # Create document verification
    config = DocumentConfig(
        type=DocumentType.PASSPORT,
        country="US",
        metadata={"key": "value"},
        front_image="base64_front_image",
        back_image="base64_back_image"
    )
    
    result = await persona.create_document_verification("inq_123", config)
    print(f"Document verification created: {result['data']['id']}")
```

### Case Management

Manage verification cases with comprehensive case management features:

```python
from pipeiq import PersonaService, CaseConfig, CaseStatus

async with PersonaService(api_key="your_api_key") as persona:
    # Create a new case
    config = CaseConfig(
        reference_id="ref_123",
        status=CaseStatus.OPEN,
        metadata={"key": "value"},
        assignee="user_123",
        tags=["tag1", "tag2"]
    )
    
    case = await persona.create_case(config)
    print(f"Case created: {case['data']['id']}")
    
    # Update case status
    updated_case = await persona.update_case(
        case["data"]["id"],
        status=CaseStatus.REVIEW,
        assignee="user_456"
    )
    
    # List cases with filters
    cases = await persona.list_cases(
        page_size=10,
        page_number=1,
        status=CaseStatus.OPEN,
        assignee="user_123",
        tags=["tag1"]
    )
    
    # Manage case tags
    await persona.add_case_tag(case["data"]["id"], "new_tag")
    await persona.remove_case_tag(case["data"]["id"], "new_tag")
```

### Verification Methods

Configure and manage verification methods for inquiries:

```python
from pipeiq import (
    PersonaService,
    VerificationMethodConfig,
    VerificationMethod
)

async with PersonaService(api_key="your_api_key") as persona:
    # Configure verification methods
    methods = [
        VerificationMethodConfig(
            method=VerificationMethod.DOCUMENT,
            enabled=True,
            options={"require_back": True}
        ),
        VerificationMethodConfig(
            method=VerificationMethod.SELFIE,
            enabled=True,
            options={"require_liveness": True}
        )
    ]
    
    result = await persona.configure_verification_methods("inq_123", methods)
    
    # Get configured methods
    methods = await persona.get_verification_methods("inq_123")
```

### Error Handling

The Persona integration includes comprehensive error handling:

```python
from pipeiq import (
    PersonaService,
    PersonaError,
    ConnectionError,
    VerificationError,
    DocumentConfig,
    DocumentType
)

async with PersonaService(api_key="your_api_key") as persona:
    try:
        # Create document verification
        config = DocumentConfig(
            type=DocumentType.PASSPORT,
            country="US"
        )
        result = await persona.create_document_verification("inq_123", config)
    except ConnectionError as e:
        print(f"Connection error: {e}")
    except VerificationError as e:
        print(f"Verification error: {e}")
    except PersonaError as e:
        print(f"Persona error: {e}")
```

### Webhook Integration

The Persona integration supports webhook handling for real-time event notifications:

```python
from pipeiq import (
    PersonaService,
    WebhookConfig,
    WebhookEventType
)

async with PersonaService(api_key="your_api_key") as persona:
    # Register a webhook endpoint
    config = WebhookConfig(
        url="https://your-domain.com/webhook",
        events=[
            WebhookEventType.INQUIRY_CREATED,
            WebhookEventType.INQUIRY_COMPLETED,
            WebhookEventType.DOCUMENT_VERIFIED
        ],
        secret="your_webhook_secret",
        metadata={"environment": "production"}
    )
    
    webhook = await persona.register_webhook(config)
    print(f"Webhook registered: {webhook['data']['id']}")
    
    # List registered webhooks
    webhooks = await persona.list_webhooks()
    
    # Process incoming webhook events
    async def handle_webhook(request):
        payload = await request.json()
        signature = request.headers.get("X-Persona-Signature")
        
        try:
            result = await persona.process_webhook_event(
                payload,
                signature,
                "your_webhook_secret"
            )
            print(f"Processed {result['event_type']} event")
        except PersonaError as e:
            print(f"Error processing webhook: {e}")
```

### Batch Operations

Perform multiple operations in a single request using batch operations:

```python
from pipeiq import (
    PersonaService,
    InquiryConfig,
    DocumentConfig,
    DocumentType,
    ReportConfig,
    ReportType
)

async with PersonaService(api_key="your_api_key") as persona:
    # Create multiple inquiries in batch
    inquiries = [
        InquiryConfig(reference_id="ref_1", template_id="template_1"),
        InquiryConfig(reference_id="ref_2", template_id="template_2")
    ]
    
    batch_result = await persona.create_batch_inquiries(inquiries)
    print(f"Batch operation started: {batch_result['data']['id']}")
    
    # Check batch operation status
    status = await persona.get_batch_operation_status(batch_result["data"]["id"])
    print(f"Batch status: {status['data']['attributes']['status']}")
    
    # Verify multiple documents in batch
    documents = [
        DocumentConfig(
            type=DocumentType.PASSPORT,
            country="US",
            front_image="base64_front_1"
        ),
        DocumentConfig(
            type=DocumentType.DRIVERS_LICENSE,
            country="US",
            front_image="base64_front_2",
            back_image="base64_back_2"
        )
    ]
    
    batch_result = await persona.verify_batch_documents(documents)
    
    # Generate multiple reports in batch
    reports = [
        ReportConfig(type=ReportType.WATCHLIST, inquiry_id="inq_1"),
        ReportConfig(type=ReportType.POLITICALLY_EXPOSED, inquiry_id="inq_2")
    ]
    
    batch_result = await persona.generate_batch_reports(reports)
```

### Advanced Verification Features

Configure and manage verification methods for enhanced security:

```python
from pipeiq import (
    PersonaService,
    VerificationMethodConfig,
    VerificationMethod
)

async with PersonaService(api_key="your_api_key") as persona:
    # Configure verification methods
    methods = [
        VerificationMethodConfig(
            method=VerificationMethod.DOCUMENT,
            enabled=True,
            options={"require_back": True}
        ),
        VerificationMethodConfig(
            method=VerificationMethod.SELFIE,
            enabled=True,
            options={"require_liveness": True}
        ),
        VerificationMethodConfig(
            method=VerificationMethod.FACE_MATCH,
            enabled=True,
            options={"threshold": 0.8}
        )
    ]
    
    result = await persona.configure_verification_methods("inq_123", methods)
    
    # Get configured methods
    methods = await persona.get_verification_methods("inq_123")
    print(f"Enabled methods: {[m['method'] for m in methods['data']['attributes']['methods']]}")
```

### Error Handling

The Persona integration includes comprehensive error handling for all operations:

```python
from pipeiq import (
    PersonaService,
    PersonaError,
    ConnectionError,
    VerificationError,
    WebhookConfig,
    WebhookEventType
)

async with PersonaService(api_key="your_api_key") as persona:
    try:
        # Register webhook
        config = WebhookConfig(
            url="https://example.com/webhook",
            events=[WebhookEventType.INQUIRY_CREATED]
        )
        await persona.register_webhook(config)
        
        # Process webhook event
        await persona.process_webhook_event(
            payload,
            signature,
            "your_webhook_secret"
        )
    except ConnectionError as e:
        print(f"Connection error: {e}")
    except VerificationError as e:
        print(f"Verification error: {e}")
    except PersonaError as e:
        print(f"Persona error: {e}")
```

---

## Architecture

The framework is built on two foundational layers:

### 1. Blockchain-Native Primitives
- ✅ Solana Smart Contracts (Rust)
- ✨ Token Programs for $PIPEIQ
- ⚖️ DAO governance (via Realms)

### 2. Agent-Centric Primitives
- 🤖 Agent Profiles & Permissions
- 🚧 Task Markets & Context Anchors
- 📢 Intent Signaling System

---

## Contributing
We welcome contributions from framework developers, cryptographers, and AI researchers. To get started:

1. Fork this repository
2. Read the [CONTRIBUTING.md](CONTRIBUTING.md) guide
3. Open a Pull Request (PR) with clear description

---

## License
MIT License. See [LICENSE](LICENSE) for details.

---

## Links
- 🔗 [Whitepaper](https://pipeiq.ai/whitepaper)
- 🌐 [Website](https://pipeiq.ai)
- ✉️ Join our community: `discord.gg/pipeiq`  
- 📰 Blog: [Coming Soon]  

---

*PIPEIQ is building the decentralized substrate for AI. Join us.*

# PipeIQ SDK

A Solana-compatible SDK for building decentralized applications.

## Features

- Solana wallet integration
- Attestation service with versioning and audit logging
- World Chain integration for human verification and mini apps
- Rate limiting and retry logic
- Comprehensive error handling
- Webhook support
- Template-based attestations

## Installation

```bash
pip install pipeiq
```

## Usage

### Basic Usage

```python
from pipeiq import PipeIQClient
from pipeiq.solana import SolanaWallet

# Initialize wallet
wallet = SolanaWallet(private_key="your_private_key")

# Create client
client = PipeIQClient(wallet)

# Use the client
result = await client.some_method()
```

### World Chain Integration

The World Chain integration provides functionality for human verification, mini app deployment, and gas fee management.

```python
from pipeiq import WorldChainService
from pipeiq.solana import SolanaWallet

# Initialize wallet
wallet = SolanaWallet(private_key="your_private_key")

# Create World Chain service
service = WorldChainService(
    wallet,
    base_url="https://api.world.org/v1",
    rate_limit=100,
    enable_audit_logging=True
)

# Verify a human using World ID
verification = await service.verify_human(
    proof={
        "type": "world_id",
        "data": "your_proof_data"
    }
)

# Check gas fee status
gas_status = await service.get_gas_status()
if gas_status["free_gas_available"]:
    print("Free gas available!")

# Deploy a mini app
app = await service.deploy_mini_app(
    app_data={
        "name": "My Mini App",
        "version": "1.0.0",
        "config": {
            "key": "value"
        }
    },
    metadata={
        "description": "A test mini app",
        "category": "social"
    }
)

# Get app status
status = await service.get_mini_app_status(app["id"])

# Get network information
network_info = await service.get_network_info()
```

### World Chain Features

#### Human Verification
- Verify users using World ID
- Check verification status
- Handle verification errors

#### Mini App Deployment
- Deploy apps to World Chain
- Track deployment status
- Manage app metadata
- Get deployment URLs

#### Gas Fee Management
- Check free gas availability
- Monitor gas balance
- Track gas usage

#### Network Information
- Get network status
- Monitor block height
- Check gas prices
- View network load

#### Audit Logging
- Track all operations
- Filter logs by operation type
- Filter logs by time range
- Export logs for compliance

### Error Handling

```python
from pipeiq.world_chain import (
    WorldChainError,
    WorldChainValidationError,
    WorldChainNetworkError
)

try:
    # Verify a human
    await service.verify_human(proof={"type": "world_id", "data": "invalid"})
except WorldChainValidationError as e:
    print(f"Validation error: {e}")
except WorldChainNetworkError as e:
    print(f"Network error: {e}")
except WorldChainError as e:
    print(f"General error: {e}")
```

### Using Context Manager

```python
async with WorldChainService(wallet) as service:
    # Service is automatically initialized
    result = await service.verify_human(proof={"type": "world_id", "data": "test"})
    # Session is automatically closed when done
```

### Audit Logging

```python
# Get all audit logs
logs = await service.get_audit_logs()

# Filter logs by operation
verify_logs = await service.get_audit_logs(operation="verify_human")

# Filter logs by time range
recent_logs = await service.get_audit_logs(
    start_time=datetime.now() - timedelta(days=1)
)

# Export logs
for log in logs:
    print(f"Operation: {log['operation']}")
    print(f"Timestamp: {log['timestamp']}")
    print(f"Details: {log['details']}")
```

## Features

### World Chain Integration
- Human verification via World ID
- Mini app deployment and management
- Gas fee tracking and management
- Network status monitoring
- Comprehensive audit logging

### Attestation Versioning
- Track changes to attestations over time
- Maintain version history with metadata
- Compare different versions
- Roll back to previous versions if needed

### Audit Logging
- Comprehensive audit trail of all operations
- Track who made changes and when
- Filter logs by operation type, time range, and more
- Export logs for compliance and auditing

### Enhanced Error Handling
- Specific error types for different scenarios
- Detailed error messages and context
- Validation errors for data integrity
- Version conflict handling

### Rate Limiting and Retries
- Automatic rate limiting to prevent API abuse
- Configurable retry logic for failed requests
- Exponential backoff for retries
- Customizable retry conditions

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Features

- Solana wallet integration for secure authentication
- Support for multiple model types (LLM, Image, Audio, etc.)
- MCP (Model Control Protocol) server integration
- Async/await support for better performance
- Type hints and validation using Pydantic
- Easy-to-use API for model connections

## Configuration

### Model Configuration

The `ModelConfig` class allows you to specify:
- Model ID and type
- Custom parameters
- Optional custom endpoint

### MCP Configuration

The `MCPConfig` class supports:
- Server URL
- API key
- Timeout settings
- Retry attempts
- Custom headers

### Solana Wallet

The `SolanaWallet` class provides:
- Keypair management
- Message signing
- Balance checking
- Network selection (mainnet-beta, testnet, devnet)

## Error Handling

The SDK raises custom exceptions for different error scenarios:
- `PipeIQError`: Base exception for all SDK errors
- `ConnectionError`: Raised for network/API connection issues
- `AuthenticationError`: Raised for authentication/authorization failures

## Prime Intellect Integration

The Prime Intellect integration provides comprehensive GPU resource management and monitoring capabilities.

### Resource Scheduling

The service supports advanced resource scheduling capabilities:

```python
from pipeiq import (
    PrimeIntellectService,
    ScheduleType,
    PodPriority,
    ResourceSchedule
)

# Create a one-time schedule
schedule = ResourceSchedule(
    schedule_type=ScheduleType.ONE_TIME,
    start_time=datetime.utcnow() + timedelta(hours=1)
)

# Schedule a pod
scheduled_pod = await service.schedule_pod(
    pod_config={
        "name": "training-pod",
        "gpu_type": "a100",
        "image": "nvidia/cuda:11.8.0"
    },
    schedule=schedule,
    priority=PodPriority.HIGH
)

# Create a recurring schedule
recurring_schedule = ResourceSchedule(
    schedule_type=ScheduleType.RECURRING,
    start_time=datetime.utcnow(),
    end_time=datetime.utcnow() + timedelta(days=7),
    recurrence={
        "frequency": "daily",
        "interval": 1
    }
)

# Get scheduled pods
scheduled_pods = await service.get_scheduled_pods(
    status="scheduled",
    start_time=datetime.utcnow(),
    end_time=datetime.utcnow() + timedelta(days=1)
)

# Cancel a scheduled pod
await service.cancel_scheduled_pod("schedule_id")
```

### Cost Optimization

The service provides advanced cost optimization features:

```python
from pipeiq import (
    PrimeIntellectService,
    OptimizationStrategy,
    CostOptimizer
)

# Create a cost optimizer
optimizer = CostOptimizer(
    strategy=OptimizationStrategy.COST,
    constraints={
        "max_cost": 1000.0,
        "min_performance": 0.8
    }
)

# Optimize costs
result = await service.optimize_costs(
    optimizer=optimizer,
    pod_ids=["pod1", "pod2"]
)

# Get cost recommendations
recommendations = await service.get_cost_recommendations(
    pod_ids=["pod1"],
    strategy=OptimizationStrategy.COST
)

# Get cost forecast
forecast = await service.get_cost_forecast(
    start_time=datetime.utcnow(),
    end_time=datetime.utcnow() + timedelta(days=7),
    pod_ids=["pod1", "pod2"]
)
```

### Advanced Pod Management

The service provides enhanced pod management capabilities:

```python
from pipeiq import (
    PrimeIntellectService,
    PodPriority,
    ResourceType
)

# Update pod priority
await service.update_pod_priority(
    pod_id="pod1",
    priority=PodPriority.HIGH
)

# Get resource availability
availability = await service.get_resource_availability(
    start_time=datetime.utcnow(),
    end_time=datetime.utcnow() + timedelta(hours=1),
    resource_type=ResourceType.GPU
)

# Get resource utilization
utilization = await service.get_resource_utilization(
    start_time=datetime.utcnow() - timedelta(hours=1),
    end_time=datetime.utcnow(),
    resource_type=ResourceType.GPU
)
```

### Basic Usage

```python
from pipeiq import PrimeIntellectService, PodStatus, ResourceType

# Initialize the service
service = PrimeIntellectService(api_key="your_api_key")

# Create a pod
pod = await service.create_pod(
    name="training-pod",
    gpu_type="a100",
    image="nvidia/cuda:11.8.0"
)

# Get pod status
status = await service.get_pod_status(pod["id"])

# Monitor resources
metrics = await service.get_resource_metrics(
    pod["id"],
    resource_type=ResourceType.GPU_UTILIZATION
)

# Delete the pod
await service.delete_pod(pod["id"])
```

### Batch Operations

The service supports batch operations for managing multiple pods efficiently:

```python
# Create multiple pods in a batch
pods = await service.batch_create_pods([
    {
        "name": "pod1",
        "gpu_type": "a100",
        "image": "nvidia/cuda:11.8.0"
    },
    {
        "name": "pod2",
        "gpu_type": "a100",
        "image": "nvidia/cuda:11.8.0"
    }
])

# Delete multiple pods in a batch
result = await service.batch_delete_pods([pod["id"] for pod in pods])

# Monitor batch operation status
status = await service.get_batch_operation_status("operation_id")

# Cancel a batch operation if needed
await service.cancel_batch_operation("operation_id")
```

### Resource Quotas

Manage and monitor resource quotas:

```python
from pipeiq import QuotaType

# Get current quotas
quotas = await service.get_quotas()

# Get quota usage
usage = await service.get_quota_usage(
    quota_type=QuotaType.GPU_HOURS,
    start_date=datetime.utcnow() - timedelta(days=7)
)
```

### Advanced Monitoring

The service provides detailed monitoring capabilities:

```python
from pipeiq import MonitoringInterval

# Get detailed monitoring data
data = await service.get_monitoring_data(
    pod_id="pod1",
    resource_type=ResourceType.GPU_UTILIZATION,
    interval=MonitoringInterval.FIVE_MINUTES,
    start_time=datetime.utcnow() - timedelta(hours=1)
)

# Get monitoring alerts
alerts = await service.get_alerts(
    pod_id="pod1",
    severity="warning"
)

# Get statistical metrics
stats = service.get_metric_statistics(
    "gpu_utilization",
    timedelta(minutes=30)
)
```

### Metrics Tracking

The service includes built-in metrics tracking with configurable history:

```python
# Initialize with custom history size
service = PrimeIntellectService(
    api_key="your_api_key",
    enable_metrics_tracking=True,
    max_history=1000
)

# Get metric statistics
stats = service.get_metric_statistics(
    "gpu_utilization",
    timedelta(minutes=30)
)
```

### Error Handling

The service provides comprehensive error handling:

```python
from pipeiq import (
    PrimeIntellectError,
    PrimeIntellectAPIError,
    PrimeIntellectValidationError,
    PrimeIntellectNetworkError
)

try:
    pod = await service.create_pod(...)
except PrimeIntellectValidationError as e:
    print(f"Validation error: {e}")
except PrimeIntellectAPIError as e:
    print(f"API error: {e}")
except PrimeIntellectNetworkError as e:
    print(f"Network error: {e}")
```

### Resource Scaling

The service supports advanced resource scaling capabilities:

```python
from pipeiq import (
    PrimeIntellectService,
    ScalingPolicy,
    ScalingConfig
)

# Configure automatic scaling
scaling_config = ScalingConfig(
    min_instances=1,
    max_instances=5,
    target_cpu_utilization=0.7,
    target_memory_utilization=0.8,
    cooldown_period=300,  # 5 minutes
    policy=ScalingPolicy.AUTOMATIC
)

# Apply scaling configuration
await service.configure_scaling("pod1", scaling_config)

# Get current scaling status
scaling_status = await service.get_scaling_status("pod1")
```

### Backup and Restore

The service provides comprehensive backup and restore capabilities:

```python
from pipeiq import (
    PrimeIntellectService,
    BackupType,
    BackupConfig
)

# Create a backup configuration
backup_config = BackupConfig(
    backup_type=BackupType.FULL,
    retention_days=30,
    schedule={
        "frequency": "daily",
        "time": "02:00"
    },
    include_volumes=True,
    include_config=True
)

# Create a backup
backup = await service.create_backup("pod1", backup_config)

# List available backups
backups = await service.list_backups("pod1", BackupType.FULL)

# Restore from backup
restore = await service.restore_from_backup(
    "pod1",
    "backup1",
    restore_config={
        "restore_volumes": True,
        "restore_config": True
    }
)
```

### Advanced Networking

The service offers advanced networking features:

```python
from pipeiq import (
    PrimeIntellectService,
    NetworkType,
    NetworkConfig
)

# Configure network settings
network_config = NetworkConfig(
    network_type=NetworkType.DEDICATED,
    bandwidth_limit=1000,  # Mbps
    security_groups=["sg1", "sg2"],
    vpc_id="vpc-123",
    subnet_id="subnet-456"
)

# Apply network configuration
await service.configure_network("pod1", network_config)

# Get network statistics
network_stats = await service.get_network_stats(
    "pod1",
    start_time=datetime.utcnow() - timedelta(hours=1),
    end_time=datetime.utcnow()
)

# Update security groups
await service.update_network_security("pod1", ["sg1", "sg2", "sg3"])

# Check network availability
availability = await service.get_network_availability(
    NetworkType.DEDICATED,
    region="us-west-1"
)
```

## Phantom Wallet Integration

PipeIQ provides seamless integration with the Phantom wallet for Solana blockchain interactions. The integration supports various operations including connecting to the wallet, managing transactions, and handling token accounts.

### Basic Usage

```python
from pipeiq import PhantomWallet, NetworkType, WalletConfig

# Initialize wallet with default config
wallet = PhantomWallet()

# Or with custom config
config = WalletConfig(
    network=NetworkType.TESTNET,
    auto_approve=True,
    timeout=60000
)
wallet = PhantomWallet(config=config)

# Connect to wallet
connection = await wallet.connect()
print(f"Connected to wallet: {connection['publicKey']}")

# Get balance
balance = await wallet.get_balance(connection['publicKey'])
print(f"Balance: {balance} SOL")

# Disconnect
await wallet.disconnect()
```

### Transaction Management

```python
from pipeiq import TransactionConfig, TransactionStatus

# Send a transaction
transaction = {
    "from": "sender_public_key",
    "to": "recipient_public_key",
    "amount": 1.0
}

config = TransactionConfig(
    fee_payer="sender_public_key",
    recent_blockhash="test_blockhash"
)

result = await wallet.send_transaction(transaction, config)
print(f"Transaction sent: {result['signature']}")

# Check transaction status
status = await wallet.get_transaction_status(result['signature'])
print(f"Transaction status: {status['status']}")
```

### Token Management

```python
# Get token accounts
accounts = await wallet.get_token_accounts("public_key")
for account in accounts:
    print(f"Token: {account['mint']}")
    print(f"Amount: {account['amount']}")
    print(f"Decimals: {account['decimals']}")
```

### Message Signing

```python
# Sign a message
signature = await wallet.sign_message("Hello, World!")
print(f"Message signed: {signature['signature']}")

# Verify signature
is_valid = await wallet.verify_signature(
    "Hello, World!",
    signature['signature'],
    signature['publicKey']
)
print(f"Signature valid: {is_valid}")
```

### Network Management

```python
# Get current network
network = await wallet.get_network()
print(f"Current network: {network}")

# Switch network
await wallet.switch_network(NetworkType.TESTNET)
print(f"Switched to: {await wallet.get_network()}")
```

### Error Handling

```python
from pipeiq import ConnectionError, TransactionError

try:
    # Attempt to get balance without connecting
    balance = await wallet.get_balance("public_key")
except ConnectionError as e:
    print(f"Connection error: {e}")

try:
    # Attempt invalid transaction
    await wallet.send_transaction({})
except TransactionError as e:
    print(f"Transaction error: {e}")
```

### Token Swaps

```python
from pipeiq import SwapType, SwapConfig

# Get a swap quote
quote = await wallet.get_swap_quote(
    input_token="SOL",
    output_token="USDC",
    amount=1.0,
    swap_type=SwapType.EXACT_IN
)
print(f"Expected output: {quote['outputAmount']} USDC")
print(f"Price impact: {quote['priceImpact']}%")

# Execute a swap
config = SwapConfig(
    slippage=0.01,  # 1% slippage tolerance
    deadline=int(datetime.now().timestamp()) + 3600  # 1 hour deadline
)

result = await wallet.execute_swap(
    input_token="SOL",
    output_token="USDC",
    amount=1.0,
    config=config,
    swap_type=SwapType.EXACT_IN
)
print(f"Swap executed: {result['signature']}")
```

### NFT Operations

```python
from pipeiq import NFTStandard, NFTConfig

# Get NFT metadata
config = NFTConfig(
    standard=NFTStandard.METAPLEX,
    verify_ownership=True,
    include_metadata=True
)

metadata = await wallet.get_nft_metadata("nft_mint_address", config)
print(f"NFT Name: {metadata['name']}")
print(f"Collection: {metadata['collection']['key']}")

# Get NFT accounts
accounts = await wallet.get_nft_accounts("owner_address", config)
for account in accounts:
    print(f"NFT: {account['mint']}")
    print(f"Amount: {account['amount']}")

# Transfer NFT
result = await wallet.transfer_nft(
    mint_address="nft_mint_address",
    to_address="recipient_address",
    config=TransactionConfig(fee_payer="sender_address")
)
print(f"NFT transfer initiated: {result['signature']}")
```

### Advanced Transaction Features

```python
# Get priority fee estimate
transaction = {
    "from": "sender_address",
    "to": "recipient_address",
    "amount": 1.0
}

fee_estimate = await wallet.get_priority_fee_estimate(transaction)
print(f"Recommended priority fee: {fee_estimate['recommendedPriorityFee']}")

# Get compute unit estimate
compute_estimate = await wallet.get_compute_unit_estimate(transaction)
print(f"Recommended compute units: {compute_estimate['recommendedComputeUnits']}")

# Get transaction history
history = await wallet.get_transaction_history(
    address="wallet_address",
    limit=10,
    before="last_signature"
)

for tx in history:
    print(f"Transaction: {tx['signature']}")
    print(f"Type: {tx['type']}")
    print(f"Fee: {tx['fee']}")
    print(f"Status: {tx['status']}")
```

### Error Handling

```python
from pipeiq import SwapError, NFTError

try:
    # Attempt invalid swap
    await wallet.execute_swap("SOL", "USDC", -1.0, SwapConfig())
except SwapError as e:
    print(f"Swap error: {e}")

try:
    # Attempt invalid NFT transfer
    await wallet.transfer_nft("", "recipient_address")
except NFTError as e:
    print(f"NFT error: {e}")
```

### Token Staking

```python
from pipeiq import StakeConfig

# Get stake accounts
accounts = await wallet.get_stake_accounts(owner="wallet_address")
for acc in accounts:
    print(f"Stake Account: {acc['address']}, Amount: {acc['amount']}")

# Get stake rewards
rewards = await wallet.get_stake_rewards(stake_account="stake_account_address")
for reward in rewards:
    print(f"Epoch: {reward['epoch']}, Amount: {reward['amount']}")

# Stake tokens
stake_config = StakeConfig(
    validator_address="validator_address",
    amount=10.0,
    lockup_period=3600,
    auto_compound=True
)
result = await wallet.stake_tokens(stake_config)
print(f"Stake initiated: {result['signature']}")

# Unstake tokens
result = await wallet.unstake_tokens(stake_account="stake_account_address", amount=5.0)
print(f"Unstake initiated: {result['signature']}")
```

### Program Interactions

```python
from pipeiq import ProgramConfig, ProgramType

# Get program accounts
accounts = await wallet.get_program_accounts(program_id="program_id")
for acc in accounts:
    print(f"Program Account: {acc['pubkey']}")

# Get program data
program_data = await wallet.get_program_data("program_id")
print(f"Program: {program_data['metadata']['name']}")

# Execute a program instruction
program_config = ProgramConfig(
    program_id="program_id",
    program_type=ProgramType.TOKEN,
    instruction_data={"action": "transfer"},
    accounts=[{"pubkey": "account1", "isSigner": True}],
    signers=["account1"]
)
result = await wallet.execute_program(program_config)
print(f"Program execution signature: {result['signature']}")
```

### Advanced Wallet Management

```python
from pipeiq import WalletFeatureConfig, WalletFeature

# Get wallet features
features = await wallet.get_wallet_features()
for feature in features:
    print(f"Feature: {feature['feature']}, Enabled: {feature['enabled']}")

# Configure a wallet feature
feature_config = WalletFeatureConfig(
    feature=WalletFeature.MULTI_SIG,
    enabled=True,
    options={"threshold": 2, "owners": ["owner1", "owner2"]}
)
result = await wallet.configure_wallet_feature(feature_config)
print(f"Feature configured: {result['feature']}")

# Get wallet permissions
permissions = await wallet.get_wallet_permissions()
print(f"Allowed Programs: {permissions['allowedPrograms']}")

# Update wallet permissions
new_permissions = {
    "allowedPrograms": ["new_program"],
    "allowedDomains": ["new_domain.com"],
    "allowedOperations": ["new_operation"]
}
result = await wallet.update_wallet_permissions(new_permissions)
print(f"Permissions updated: {result}")
```

## Advanced Features

### Rate Limiting

The Persona service includes built-in rate limiting to prevent API throttling. You can configure the rate limits when initializing the service:

```python
from pipeiq import PersonaService, RateLimitConfig

# Configure rate limits
rate_limit_config = RateLimitConfig(
    requests_per_second=10,  # Maximum requests per second
    burst_size=20,          # Maximum burst size
    window_size=1           # Time window in seconds
)

# Initialize service with rate limits
async with PersonaService(
    api_key="your_api_key",
    rate_limit_config=rate_limit_config
) as persona_service:
    # Make API calls - rate limiting is handled automatically
    inquiry = await persona_service.get_inquiry("inquiry_id")
```

You can also update rate limits at runtime:

```python
# Update rate limits
new_config = RateLimitConfig(requests_per_second=20, burst_size=40)
await persona_service.update_rate_limit(new_config)
```

### Retry Mechanism

The service includes automatic retry logic for failed requests. Configure retry behavior when initializing the service:

```python
from pipeiq import PersonaService, RetryConfig, RetryStrategy

# Configure retry behavior
retry_config = RetryConfig(
    max_retries=3,                    # Maximum number of retry attempts
    initial_delay=1.0,                # Initial delay between retries (seconds)
    max_delay=30.0,                   # Maximum delay between retries (seconds)
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF,  # Retry strategy
    retry_on_status_codes=[429, 500, 502, 503, 504]  # Status codes to retry on
)

# Initialize service with retry config
async with PersonaService(
    api_key="your_api_key",
    retry_config=retry_config
) as persona_service:
    # Make API calls - retries are handled automatically
    inquiry = await persona_service.get_inquiry("inquiry_id")
```

Available retry strategies:
- `EXPONENTIAL_BACKOFF`: Delay increases exponentially between retries
- `LINEAR_BACKOFF`: Delay increases linearly between retries
- `CONSTANT`: Fixed delay between retries

Update retry configuration at runtime:

```python
# Update retry config
new_config = RetryConfig(
    max_retries=5,
    initial_delay=0.5,
    strategy=RetryStrategy.LINEAR_BACKOFF
)
await persona_service.update_retry_config(new_config)
```

### Caching

The service includes an in-memory cache to improve performance and reduce API calls. Configure caching when initializing the service:

```python
from pipeiq import PersonaService, CacheConfig

# Configure caching
cache_config = CacheConfig(
    ttl=300,           # Time-to-live for cached items (seconds)
    max_size=1000,     # Maximum number of cached items
    enabled=True       # Enable/disable caching
)

# Initialize service with cache config
async with PersonaService(
    api_key="your_api_key",
    cache_config=cache_config
) as persona_service:
    # First call - hits the API
    inquiry1 = await persona_service.get_inquiry("inquiry_id")
    
    # Second call - uses cache
    inquiry2 = await persona_service.get_inquiry("inquiry_id")
```

Cache management:

```python
# Clear the cache
await persona_service.clear_cache()

# Update cache configuration
new_config = CacheConfig(ttl=600, max_size=100, enabled=False)
await persona_service.update_cache_config(new_config)
```

Note: Caching is only applied to GET requests by default. POST, PUT, and DELETE requests are not cached.

### Error Handling

The service includes comprehensive error handling for rate limits, retries, and caching:

```python
from pipeiq import PersonaService, PersonaError

async with PersonaService("your_api_key") as persona_service:
    try:
        # Make API calls
        inquiry = await persona_service.get_inquiry("test_id")
    except PersonaError as e:
        if "Rate limit exceeded" in str(e):
            # Handle rate limit errors
            print("Rate limit exceeded, please try again later")
        else:
            # Handle other API errors
            print(f"API error: {e}")
    except Exception as e:
        # Handle other errors
        print(f"Unexpected error: {e}")
```

### Best Practices

1. **Rate Limiting**:
   - Set appropriate rate limits based on your API tier
   - Use burst size to handle traffic spikes
   - Monitor rate limit errors and adjust accordingly

2. **Retry Strategy**:
   - Use exponential backoff for most cases
   - Adjust retry counts and delays based on API reliability
   - Consider API costs when setting retry limits

3. **Caching**:
   - Set appropriate TTL based on data freshness requirements
   - Monitor cache size and adjust based on memory constraints
   - Clear cache when data is updated

4. **Error Handling**:
   - Always implement proper error handling
   - Log errors for monitoring and debugging
   - Implement fallback strategies for critical operations

### Advanced Usage Examples

#### Rate Limiting Examples

1. **Handling High Traffic**:
```python
from pipeiq import PersonaService, RateLimitConfig

# Configure for high traffic
rate_limit_config = RateLimitConfig(
    requests_per_second=50,  # High throughput
    burst_size=100,         # Allow bursts
    window_size=1           # 1-second window
)

async with PersonaService("your_api_key", rate_limit_config=rate_limit_config) as persona_service:
    # Process multiple inquiries concurrently
    inquiries = await asyncio.gather(*[
        persona_service.get_inquiry(f"inquiry_{i}")
        for i in range(100)
    ])
```

2. **Adaptive Rate Limiting**:
```python
async with PersonaService("your_api_key") as persona_service:
    # Start with conservative limits
    await persona_service.update_rate_limit(RateLimitConfig(
        requests_per_second=10,
        burst_size=20
    ))
    
    try:
        # Process requests
        await persona_service.get_inquiry("test_id")
    except PersonaError as e:
        if "Rate limit exceeded" in str(e):
            # Reduce rate limit on error
            await persona_service.update_rate_limit(RateLimitConfig(
                requests_per_second=5,
                burst_size=10
            ))
```

#### Retry Strategy Examples

1. **Custom Retry Configuration**:
```python
from pipeiq import PersonaService, RetryConfig, RetryStrategy

# Configure for sensitive operations
retry_config = RetryConfig(
    max_retries=5,                    # More retries
    initial_delay=0.5,                # Start with 500ms
    max_delay=60.0,                   # Max 60s delay
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    retry_on_status_codes=[429, 500, 502, 503, 504, 408]  # Additional status codes
)

async with PersonaService("your_api_key", retry_config=retry_config) as persona_service:
    # Critical operation with enhanced retry
    result = await persona_service.create_inquiry(InquiryConfig(
        reference_id="critical_operation",
        template_id="sensitive_template"
    ))
```

2. **Different Strategies for Different Operations**:
```python
async with PersonaService("your_api_key") as persona_service:
    # Use exponential backoff for critical operations
    await persona_service.update_retry_config(RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF
    ))
    await persona_service.create_inquiry(...)
    
    # Use linear backoff for background operations
    await persona_service.update_retry_config(RetryConfig(
        strategy=RetryStrategy.LINEAR_BACKOFF
    ))
    await persona_service.list_inquiries()
```

#### Caching Examples

1. **Optimizing Frequently Accessed Data**:
```python
from pipeiq import PersonaService, CacheConfig

# Configure cache for frequently accessed data
cache_config = CacheConfig(
    ttl=3600,           # 1 hour cache
    max_size=1000,      # Store up to 1000 items
    enabled=True
)

async with PersonaService("your_api_key", cache_config=cache_config) as persona_service:
    # First call - hits the API
    inquiry = await persona_service.get_inquiry("frequent_id")
    
    # Subsequent calls - use cache
    for _ in range(100):
        cached_inquiry = await persona_service.get_inquiry("frequent_id")
```

2. **Selective Caching**:
```python
async with PersonaService("your_api_key") as persona_service:
    # Enable caching for GET operations
    await persona_service.update_cache_config(CacheConfig(
        ttl=300,
        enabled=True
    ))
    
    # Cache GET requests
    inquiry = await persona_service.get_inquiry("test_id")
    
    # Disable caching for POST operations
    await persona_service.update_cache_config(CacheConfig(
        enabled=False
    ))
    
    # No caching for POST requests
    result = await persona_service.create_inquiry(...)
```

3. **Cache Management**:
```python
async with PersonaService("your_api_key") as persona_service:
    # Populate cache
    await persona_service.get_inquiry("id1")
    await persona_service.get_inquiry("id2")
    
    # Clear cache before critical operation
    await persona_service.clear_cache()
    
    # Update cache configuration
    await persona_service.update_cache_config(CacheConfig(
        ttl=600,      # 10 minutes
        max_size=100  # Smaller cache
    ))
```

#### Error Handling Examples

1. **Comprehensive Error Handling**:
```python
from pipeiq import PersonaService, PersonaError

async with PersonaService("your_api_key") as persona_service:
    try:
        # Make API calls
        inquiry = await persona_service.get_inquiry("test_id")
    except PersonaError as e:
        if "Rate limit exceeded" in str(e):
            # Handle rate limit errors
            print("Rate limit exceeded, implementing backoff...")
            await asyncio.sleep(5)
        elif "API error" in str(e):
            # Handle API errors
            print(f"API error: {e}")
        else:
            # Handle other Persona errors
            print(f"Persona error: {e}")
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error: {e}")
```

2. **Retry with Error Handling**:
```python
async def process_with_retry(persona_service, inquiry_id, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return await persona_service.get_inquiry(inquiry_id)
        except PersonaError as e:
            if attempt == max_attempts - 1:
                raise
            print(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

3. **Cache Error Recovery**:
```python
async def get_inquiry_with_cache_fallback(persona_service, inquiry_id):
    try:
        # Try with cache
        return await persona_service.get_inquiry(inquiry_id)
    except PersonaError:
        # Clear cache on error
        await persona_service.clear_cache()
        # Retry without cache
        return await persona_service.get_inquiry(inquiry_id)
```

### Best Practices

1. **Rate Limiting**:
   - Monitor API usage patterns
   - Adjust rate limits based on traffic
   - Implement graceful degradation
   - Use burst sizes for traffic spikes

2. **Retry Strategy**:
   - Use exponential backoff for most cases
   - Implement circuit breakers for failing endpoints
   - Log retry attempts for monitoring
   - Consider API costs in retry configuration

3. **Caching**:
   - Set appropriate TTL based on data freshness
   - Monitor cache hit rates
   - Implement cache invalidation strategies
   - Use cache size limits to prevent memory issues

4. **Error Handling**:
   - Implement comprehensive error handling
   - Log errors for monitoring
   - Use appropriate retry strategies
   - Implement fallback mechanisms

5. **Performance Optimization**:
   - Use concurrent requests when appropriate
   - Implement proper caching strategies
   - Monitor and adjust rate limits
   - Use appropriate retry configurations
```

## Best Practices and Guidelines

### General Guidelines

1. **API Key Management**:
   ```python
   # Store API keys securely
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   API_KEY = os.getenv("PERSONA_API_KEY")
   
   # Use environment-specific keys
   async with PersonaService(
       api_key=API_KEY,
       environment="sandbox" if os.getenv("ENV") == "development" else "production"
   ) as persona_service:
       # Your code here
   ```

2. **Resource Management**:
   ```python
   # Always use async context manager
   async with PersonaService("your_api_key") as persona_service:
       # Your code here
   # Resources are automatically cleaned up
   ```

3. **Error Handling**:
   ```python
   # Implement comprehensive error handling
   try:
       result = await persona_service.get_inquiry("test_id")
   except PersonaError as e:
       # Log error with context
       logger.error(f"Persona API error: {e}", extra={
           "inquiry_id": "test_id",
           "error_type": type(e).__name__
       })
       # Implement appropriate fallback
   ```

### Rate Limiting Guidelines

1. **Traffic Management**:
   ```python
   # Implement adaptive rate limiting
   class AdaptiveRateLimiter:
       def __init__(self, persona_service):
           self.persona_service = persona_service
           self.base_config = RateLimitConfig(
               requests_per_second=10,
               burst_size=20
           )
           
       async def adjust_limits(self, success_rate):
           if success_rate < 0.9:  # 90% success threshold
               # Reduce limits on high error rate
               await self.persona_service.update_rate_limit(RateLimitConfig(
                   requests_per_second=self.base_config.requests_per_second * 0.5,
                   burst_size=self.base_config.burst_size * 0.5
               ))
           else:
               # Gradually increase limits on good performance
               await self.persona_service.update_rate_limit(self.base_config)
   ```

2. **Burst Handling**:
   ```python
   # Implement burst protection
   async def process_with_burst_protection(persona_service, items):
       # Calculate optimal batch size
       batch_size = min(50, len(items))
       
       # Process in batches
       for i in range(0, len(items), batch_size):
           batch = items[i:i + batch_size]
           await asyncio.gather(*[
               persona_service.get_inquiry(item_id)
               for item_id in batch
           ])
           # Add delay between batches
           await asyncio.sleep(0.1)
   ```

### Retry Strategy Guidelines

1. **Operation-Specific Retry**:
   ```python
   # Implement operation-specific retry strategies
   class RetryStrategyManager:
       def __init__(self, persona_service):
           self.persona_service = persona_service
           
       async def configure_for_operation(self, operation_type):
           if operation_type == "critical":
               await self.persona_service.update_retry_config(RetryConfig(
                   max_retries=5,
                   initial_delay=1.0,
                   strategy=RetryStrategy.EXPONENTIAL_BACKOFF
               ))
           elif operation_type == "background":
               await self.persona_service.update_retry_config(RetryConfig(
                   max_retries=2,
                   initial_delay=0.5,
                   strategy=RetryStrategy.LINEAR_BACKOFF
               ))
   ```

2. **Circuit Breaker Pattern**:
   ```python
   class CircuitBreaker:
       def __init__(self, threshold=5, reset_timeout=60):
           self.threshold = threshold
           self.reset_timeout = reset_timeout
           self.failures = 0
           self.last_failure_time = None
           
       async def execute(self, persona_service, operation):
           if self.is_open():
               raise Exception("Circuit breaker is open")
               
           try:
               result = await operation()
               self.reset()
               return result
           except PersonaError as e:
               self.record_failure()
               raise
               
       def is_open(self):
           if self.failures >= self.threshold:
               if time.time() - self.last_failure_time > self.reset_timeout:
                   self.reset()
                   return False
               return True
           return False
   ```

### Caching Guidelines

1. **Cache Invalidation**:
   ```python
   class CacheManager:
       def __init__(self, persona_service):
           self.persona_service = persona_service
           
       async def get_with_cache(self, inquiry_id):
           try:
               return await self.persona_service.get_inquiry(inquiry_id)
           except PersonaError:
               # Clear cache on error
               await self.persona_service.clear_cache()
               raise
               
       async def invalidate_on_update(self, inquiry_id):
           # Clear cache before update
           await self.persona_service.clear_cache()
           # Perform update
           result = await self.persona_service.update_inquiry(inquiry_id)
           return result
   ```

2. **Cache Warming**:
   ```python
   class CacheWarmer:
       def __init__(self, persona_service):
           self.persona_service = persona_service
           
       async def warm_cache(self, inquiry_ids):
           # Warm cache with frequently accessed data
           await asyncio.gather(*[
               self.persona_service.get_inquiry(inquiry_id)
               for inquiry_id in inquiry_ids
           ])
   ```

### Performance Optimization Guidelines

1. **Concurrent Operations**:
   ```python
   class BatchProcessor:
       def __init__(self, persona_service):
           self.persona_service = persona_service
           
       async def process_batch(self, items, batch_size=50):
           results = []
           for i in range(0, len(items), batch_size):
               batch = items[i:i + batch_size]
               batch_results = await asyncio.gather(*[
                   self.persona_service.get_inquiry(item_id)
                   for item_id in batch
               ])
               results.extend(batch_results)
           return results
   ```

2. **Resource Pooling**:
   ```python
   class PersonaServicePool:
       def __init__(self, api_key, pool_size=5):
           self.pool = asyncio.Queue(maxsize=pool_size)
           for _ in range(pool_size):
               self.pool.put_nowait(PersonaService(api_key))
               
       async def get_service(self):
           return await self.pool.get()
           
       async def release_service(self, service):
           await self.pool.put(service)
   ```

### Monitoring and Logging Guidelines

1. **Performance Monitoring**:
   ```python
   class PerformanceMonitor:
       def __init__(self):
           self.metrics = {
               "request_count": 0,
               "error_count": 0,
               "cache_hits": 0,
               "cache_misses": 0
           }
           
       async def track_operation(self, operation):
           start_time = time.time()
           try:
               result = await operation()
               self.metrics["request_count"] += 1
               return result
           except Exception as e:
               self.metrics["error_count"] += 1
               raise
           finally:
               duration = time.time() - start_time
               # Log metrics
               logger.info("Operation metrics", extra={
                   "duration": duration,
                   "metrics": self.metrics
               })
   ```

2. **Error Tracking**:
   ```python
   class ErrorTracker:
       def __init__(self):
           self.errors = defaultdict(int)
           
       def track_error(self, error):
           error_type = type(error).__name__
           self.errors[error_type] += 1
           
           # Alert on high error rates
           if self.errors[error_type] > 10:
               logger.error(f"High error rate for {error_type}")
   ```

### Security Guidelines

1. **API Key Rotation**:
   ```python
   class APIKeyManager:
       def __init__(self):
           self.keys = []
           self.current_key_index = 0
           
       def add_key(self, key):
           self.keys.append(key)
           
       def get_current_key(self):
           return self.keys[self.current_key_index]
           
       def rotate_key(self):
           self.current_key_index = (self.current_key_index + 1) % len(self.keys)
   ```

2. **Request Validation**:
   ```python
   class RequestValidator:
       @staticmethod
       def validate_inquiry_config(config):
           if not config.reference_id:
               raise ValueError("Reference ID is required")
           if not config.template_id:
               raise ValueError("Template ID is required")
           return config
   ```

### Deployment Guidelines

1. **Environment Configuration**:
   ```python
   class EnvironmentConfig:
       def __init__(self):
           self.config = {
               "development": {
                   "rate_limit": RateLimitConfig(requests_per_second=5),
                   "cache": CacheConfig(ttl=60)
               },
               "production": {
                   "rate_limit": RateLimitConfig(requests_per_second=50),
                   "cache": CacheConfig(ttl=300)
               }
           }
           
       def get_config(self, environment):
           return self.config.get(environment, self.config["development"])
   ```

2. **Health Checks**:
   ```python
   class HealthChecker:
       def __init__(self, persona_service):
           self.persona_service = persona_service
           
       async def check_health(self):
           try:
               # Perform lightweight API call
               await self.persona_service.get_inquiry("health_check")
               return True
           except Exception:
               return False
   ```

These guidelines and best practices help ensure:
- Reliable and efficient API usage
- Proper resource management
- Effective error handling
- Optimal performance
- Secure operations
- Easy maintenance and monitoring

# OpenRouter MCP Connector

The OpenRouter MCP connector provides a unified interface for accessing various AI models through OpenRouter's API, following the Model Context Protocol (MCP) pattern.

## Features

- **Unified Model Access**: Access multiple AI models through a single interface
- **Chat & Text Completions**: Support for both chat and text completion endpoints
- **Rate Limiting**: Built-in rate limiting with token bucket algorithm
- **Caching**: Configurable caching with TTL and size limits
- **Error Handling**: Comprehensive error handling with retry mechanism
- **Type Safety**: Full type hints and Protocol-based interface
- **Resource Management**: Proper resource cleanup with context managers

## Installation

```bash
pip install pipeiq[openrouter]
```

## Configuration

```python
from pipeiq.openrouter_mcp import OpenRouterConfig

config = OpenRouterConfig(
    api_key="your_api_key",
    site_url="https://your-site.com",  # Optional
    site_name="Your Site Name",        # Optional
    timeout=30,                        # Optional
    max_retries=3,                     # Optional
    rate_limit=100,                    # Optional
    cache_ttl=300,                     # Optional
    cache_size=1000                    # Optional
)
```

## Usage

### Basic Usage

```python
from pipeiq.openrouter_mcp import OpenRouterProvider, OpenRouterConfig

# Create configuration
config = OpenRouterConfig(api_key="your_api_key")

# Use the provider
async with OpenRouterProvider(config) as provider:
    # Get the model interface
    model = provider.get_model()
    
    # Get chat completion
    response = await model.chat_completion(
        messages=[{"role": "user", "content": "Hello"}],
        model="gpt-4",
        temperature=0.7
    )
    
    # Get text completion
    response = await model.text_completion(
        prompt="Hello",
        model="gpt-4",
        temperature=0.7
    )
```

### Available Operations

The OpenRouter model interface provides the following operations:

#### Chat Completion
```python
response = await model.chat_completion(
    messages=[
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"}
    ],
    model="gpt-4",
    temperature=0.7,
    max_tokens=100
)
```

#### Text Completion
```python
response = await model.text_completion(
    prompt="Write a poem about AI",
    model="gpt-4",
    temperature=0.8,
    max_tokens=200
)
```

#### List Available Models
```python
models = await model.list_models()
```

#### Get Credit Information
```python
credits = await model.get_credits()
```

## Error Handling

The connector provides specific exception classes for different error scenarios:

```python
from pipeiq.openrouter_mcp import (
    OpenRouterError,
    ConnectionError,
    AuthenticationError,
    RateLimitError,
    ValidationError
)

try:
    async with OpenRouterProvider(config) as provider:
        model = provider.get_model()
        response = await model.chat_completion(
            messages=[{"role": "user", "content": "Hello"}]
        )
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except ConnectionError:
    print("Connection error")
except ValidationError:
    print("Invalid input")
except OpenRouterError:
    print("Other OpenRouter error")
```

## Best Practices

1. **Resource Management**
   - Always use the provider as a context manager
   - Resources are automatically cleaned up when exiting the context

2. **Rate Limiting**
   - The connector automatically handles rate limiting
   - Configure appropriate rate limits based on your API tier

3. **Caching**
   - Use caching for frequently accessed data
   - Configure cache TTL and size based on your needs

4. **Error Handling**
   - Implement proper error handling for all operations
   - Use specific exception classes for different error types

5. **Async/Await**
   - All operations are asynchronous
   - Use `async/await` syntax when calling methods

## API Reference

### OpenRouterProvider

The main entry point for the connector.

```python
provider = OpenRouterProvider(config)
model = provider.get_model()
```

### OpenRouterModel

Protocol defining the interface for OpenRouter operations.

```python
class OpenRouterModel(Protocol):
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]: ...
    
    async def text_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]: ...
    
    async def list_models(self) -> List[Dict[str, Any]]: ...
    
    async def get_credits(self) -> Dict[str, Any]: ...
```

### Configuration Classes

#### OpenRouterConfig
```python
@dataclass
class OpenRouterConfig:
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    site_url: Optional[str] = None
    site_name: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    rate_limit: int = 100
    cache_ttl: int = 300
    cache_size: int = 1000
```

#### RateLimitConfig
```python
@dataclass
class RateLimitConfig:
    requests_per_minute: int
    burst_size: int = 1
    window_size: int = 60
```

#### RetryConfig
```python
@dataclass
class RetryConfig:
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 30.0
    retry_on_status_codes: List[int] = [429, 500, 502, 503, 504]
```

#### CacheConfig
```python
@dataclass
class CacheConfig:
    ttl: int = 300
    max_size: int = 1000
    enabled: bool = True
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.