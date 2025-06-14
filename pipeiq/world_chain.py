from typing import Dict, List, Optional, Union, Any
from enum import Enum
import json
import aiohttp
from datetime import datetime, timedelta
from .solana import SolanaWallet
import asyncio

class WorldChainError(Exception):
    """Base exception for World Chain related errors."""
    pass

class WorldChainValidationError(WorldChainError):
    """Raised when validation fails."""
    pass

class WorldChainNetworkError(WorldChainError):
    """Raised when network operations fail."""
    pass

class WorldChainStatus(str, Enum):
    """Status of World Chain operations."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class TokenType(str, Enum):
    """Supported token types for bridging."""
    USDC = "usdc"
    WLD = "wld"
    ETH = "eth"

class NodeStatus(str, Enum):
    """Status of World Chain nodes."""
    ACTIVE = "active"
    SYNCING = "syncing"
    OFFLINE = "offline"

class TransactionType(str, Enum):
    BRIDGE = "bridge"
    DEPLOY = "deploy"
    UPDATE = "update"
    VERIFY = "verify"

class RateLimitExceededError(WorldChainError):
    """Raised when rate limit is exceeded."""
    pass

class BatchOperationError(WorldChainError):
    """Raised when a batch operation fails."""
    pass

class WorldChainService:
    """Service for interacting with World Chain."""
    
    def __init__(
        self,
        wallet: SolanaWallet,
        base_url: str = "https://api.world.org/v1",
        rate_limit: int = 100,
        enable_audit_logging: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the World Chain service.
        
        Args:
            wallet: SolanaWallet instance for signing transactions
            base_url: Base URL for World Chain API
            rate_limit: Maximum requests per minute
            enable_audit_logging: Whether to enable audit logging
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retry attempts
        """
        self.wallet = wallet
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.enable_audit_logging = enable_audit_logging
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._session: Optional[aiohttp.ClientSession] = None
        self._audit_logs: List[Dict] = []
        self._node_health_cache: Dict[str, Dict] = {}
        self._token_balances_cache: Dict[str, Dict] = {}
        self._transaction_history: List[Dict] = []
        self._rate_limit_tokens = rate_limit
        self._last_rate_limit_reset = datetime.now()
        self._rate_limit_lock = asyncio.Lock()

    async def __aenter__(self):
        """Set up async context."""
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up async context."""
        if self._session:
            await self._session.close()
            self._session = None

    def _log_audit(self, operation: str, details: Dict):
        """Log an audit entry."""
        if self.enable_audit_logging:
            self._audit_logs.append({
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "wallet_address": self.wallet.public_key,
                "details": details
            })

    async def _check_rate_limit(self):
        """Check and update rate limit tokens."""
        async with self._rate_limit_lock:
            now = datetime.now()
            if (now - self._last_rate_limit_reset) >= timedelta(seconds=1):
                self._rate_limit_tokens = self.rate_limit
                self._last_rate_limit_reset = now
            
            if self._rate_limit_tokens <= 0:
                raise RateLimitExceededError("Rate limit exceeded")
            
            self._rate_limit_tokens -= 1

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Any:
        """Make an API request with retry logic and rate limiting."""
        if not self._session:
            raise WorldChainError("Service not initialized. Use async with context.")

        for attempt in range(self.max_retries):
            try:
                await self._check_rate_limit()
                async with self._session.request(method, f"{self.base_url}/{endpoint}", **kwargs) as response:
                    if response.status == 429:  # Too Many Requests
                        retry_after = int(response.headers.get("Retry-After", self.retry_delay))
                        await asyncio.sleep(retry_after)
                        continue
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise WorldChainError(f"API request failed: {error_text}")
                    
                    return await response.json()
            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    raise WorldChainNetworkError(f"Network error after {self.max_retries} retries: {str(e)}")
                await asyncio.sleep(self.retry_delay * (attempt + 1))

    def _log_transaction(self, transaction_type: TransactionType, details: Dict):
        """Log a transaction to history."""
        self._transaction_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": transaction_type.value,
            "wallet_address": self.wallet.public_key,
            "details": details
        })

    async def get_transaction_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        transaction_type: Optional[TransactionType] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get transaction history with filtering."""
        filtered_history = self._transaction_history

        if start_time:
            filtered_history = [
                tx for tx in filtered_history
                if datetime.fromisoformat(tx["timestamp"]) >= start_time
            ]

        if end_time:
            filtered_history = [
                tx for tx in filtered_history
                if datetime.fromisoformat(tx["timestamp"]) <= end_time
            ]

        if transaction_type:
            filtered_history = [
                tx for tx in filtered_history
                if tx["type"] == transaction_type.value
            ]

        if limit:
            filtered_history = filtered_history[-limit:]

        return filtered_history

    async def batch_bridge_tokens(
        self,
        operations: List[Dict[str, Any]]
    ) -> List[Dict]:
        """Perform multiple token bridge operations in batch."""
        if not self._session:
            raise WorldChainError("Service not initialized. Use async with context.")

        results = []
        errors = []

        for op in operations:
            try:
                result = await self.bridge_token(
                    token_type=op["token_type"],
                    amount=op["amount"],
                    destination_chain=op["destination_chain"],
                    metadata=op.get("metadata")
                )
                results.append(result)
            except Exception as e:
                errors.append({
                    "operation": op,
                    "error": str(e)
                })

        if errors:
            raise BatchOperationError(f"Batch operation completed with errors: {errors}")

        return results

    async def batch_deploy_mini_apps(
        self,
        apps: List[Dict[str, Any]]
    ) -> List[Dict]:
        """Deploy multiple mini apps in batch."""
        if not self._session:
            raise WorldChainError("Service not initialized. Use async with context.")

        results = []
        errors = []

        for app in apps:
            try:
                result = await self.deploy_mini_app(
                    app_data=app["app_data"],
                    metadata=app.get("metadata")
                )
                results.append(result)
            except Exception as e:
                errors.append({
                    "app": app,
                    "error": str(e)
                })

        if errors:
            raise BatchOperationError(f"Batch deployment completed with errors: {errors}")

        return results

    async def verify_human(self, proof: Dict) -> Dict:
        """
        Verify a human using World ID.
        
        Args:
            proof: World ID proof data
            
        Returns:
            Dict containing verification result
            
        Raises:
            WorldChainValidationError: If proof is invalid
            WorldChainNetworkError: If network request fails
        """
        try:
            signature = await self.wallet.sign_message(str(proof))
            result = await self._make_request(
                "POST",
                "verify",
                json={
                    "proof": proof,
                    "wallet_address": self.wallet.public_key,
                    "signature": signature
                }
            )
            
            self._log_audit("verify_human", {"proof_id": result["id"]})
            self._log_transaction(TransactionType.VERIFY, {"proof_id": result["id"]})
            return result
        except Exception as e:
            self._log_transaction(TransactionType.VERIFY, {
                "error": str(e),
                "proof": proof
            })
            raise

    async def get_gas_status(self) -> Dict:
        """
        Get gas fee status for the wallet.
        
        Returns:
            Dict containing gas fee information
            
        Raises:
            WorldChainNetworkError: If network request fails
        """
        if not self._session:
            raise WorldChainError("Service not initialized. Use async with context.")

        try:
            async with self._session.get(
                f"{self.base_url}/gas/{self.wallet.public_key}"
            ) as response:
                if response.status != 200:
                    raise WorldChainNetworkError(
                        f"Failed to get gas status: {await response.text()}"
                    )
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise WorldChainNetworkError(f"Network error getting gas status: {str(e)}")

    async def deploy_mini_app(
        self,
        app_data: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Deploy a mini app to World Chain.
        
        Args:
            app_data: Mini app data and configuration
            metadata: Optional metadata for the deployment
            
        Returns:
            Dict containing deployment information
            
        Raises:
            WorldChainValidationError: If app data is invalid
            WorldChainNetworkError: If deployment fails
        """
        if not self._session:
            raise WorldChainError("Service not initialized. Use async with context.")

        try:
            signature = await self.wallet.sign_message(str(app_data))
            async with self._session.post(
                f"{self.base_url}/apps",
                json={
                    "app_data": app_data,
                    "metadata": metadata or {},
                    "wallet_address": self.wallet.public_key,
                    "signature": signature
                }
            ) as response:
                if response.status != 200:
                    raise WorldChainNetworkError(
                        f"Deployment failed: {await response.text()}"
                    )
                
                result = await response.json()
                self._log_audit("deploy_mini_app", {"app_id": result["id"]})
                self._log_transaction(TransactionType.DEPLOY, {
                    "app_id": result["id"],
                    "app_data": app_data,
                    "metadata": metadata
                })
                return result
                
        except aiohttp.ClientError as e:
            raise WorldChainNetworkError(f"Network error during deployment: {str(e)}")

    async def get_mini_app_status(self, app_id: str) -> Dict:
        """
        Get status of a deployed mini app.
        
        Args:
            app_id: ID of the mini app
            
        Returns:
            Dict containing app status
            
        Raises:
            WorldChainNetworkError: If request fails
        """
        try:
            async with self._session.get(
                f"{self.base_url}/apps/{app_id}"
            ) as response:
                if response.status != 200:
                    raise WorldChainNetworkError(
                        f"Failed to get app status: {await response.text()}"
                    )
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise WorldChainNetworkError(f"Network error: {str(e)}")

    async def update_mini_app(
        self,
        app_id: str,
        updates: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Update a deployed mini app.
        
        Args:
            app_id: ID of the mini app
            updates: Updates to apply
            metadata: Optional metadata for the update
            
        Returns:
            Dict containing update status
            
        Raises:
            WorldChainValidationError: If updates are invalid
            WorldChainNetworkError: If update fails
        """
        if not self._session:
            raise WorldChainError("Service not initialized. Use async with context.")

        try:
            signature = await self.wallet.sign_message(str(updates))
            async with self._session.put(
                f"{self.base_url}/apps/{app_id}",
                json={
                    "updates": updates,
                    "metadata": metadata or {},
                    "wallet_address": self.wallet.public_key,
                    "signature": signature
                }
            ) as response:
                if response.status != 200:
                    raise WorldChainNetworkError(
                        f"Update failed: {await response.text()}"
                    )
                
                result = await response.json()
                self._log_audit("update_mini_app", {
                    "app_id": app_id,
                    "version": updates.get("version")
                })
                self._log_transaction(TransactionType.UPDATE, {
                    "app_id": app_id,
                    "updates": updates,
                    "metadata": metadata
                })
                return result
                
        except aiohttp.ClientError as e:
            raise WorldChainNetworkError(f"Network error during update: {str(e)}")

    async def bridge_token(
        self,
        token_type: TokenType,
        amount: str,
        destination_chain: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Bridge tokens to another chain.
        
        Args:
            token_type: Type of token to bridge
            amount: Amount to bridge
            destination_chain: Target chain
            metadata: Optional metadata for the bridge operation
            
        Returns:
            Dict containing bridge operation status
            
        Raises:
            WorldChainValidationError: If parameters are invalid
            WorldChainNetworkError: If bridge operation fails
        """
        try:
            bridge_data = {
                "token_type": token_type.value,
                "amount": amount,
                "destination_chain": destination_chain,
                "wallet_address": self.wallet.public_key
            }
            signature = await self.wallet.sign_message(str(bridge_data))
            
            result = await self._make_request(
                "POST",
                "bridge",
                json={
                    **bridge_data,
                    "metadata": metadata or {},
                    "signature": signature
                }
            )
            
            self._log_audit("bridge_token", {
                "bridge_id": result["id"],
                "token_type": token_type.value,
                "amount": amount
            })
            self._log_transaction(TransactionType.BRIDGE, {
                "bridge_id": result["id"],
                "token_type": token_type.value,
                "amount": amount
            })
            return result
        except Exception as e:
            self._log_transaction(TransactionType.BRIDGE, {
                "error": str(e),
                "token_type": token_type.value,
                "amount": amount
            })
            raise

    async def get_bridge_status(self, bridge_id: str) -> Dict:
        """
        Get status of a bridge operation.
        
        Args:
            bridge_id: ID of the bridge operation
            
        Returns:
            Dict containing bridge operation status
            
        Raises:
            WorldChainNetworkError: If request fails
        """
        if not self._session:
            raise WorldChainError("Service not initialized. Use async with context.")

        try:
            async with self._session.get(
                f"{self.base_url}/bridge/{bridge_id}"
            ) as response:
                if response.status != 200:
                    raise WorldChainNetworkError(
                        f"Failed to get bridge status: {await response.text()}"
                    )
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise WorldChainNetworkError(f"Network error getting bridge status: {str(e)}")

    async def get_node_status(self, node_id: str) -> Dict:
        """
        Get status of a World Chain node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            Dict containing node status
            
        Raises:
            WorldChainNetworkError: If request fails
        """
        if not self._session:
            raise WorldChainError("Service not initialized. Use async with context.")

        try:
            async with self._session.get(
                f"{self.base_url}/nodes/{node_id}"
            ) as response:
                if response.status != 200:
                    raise WorldChainNetworkError(
                        f"Failed to get node status: {await response.text()}"
                    )
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise WorldChainNetworkError(f"Network error: {str(e)}")

    async def list_nodes(
        self,
        status: Optional[NodeStatus] = None,
        region: Optional[str] = None
    ) -> List[Dict]:
        """
        List World Chain nodes with optional filtering.
        
        Args:
            status: Filter by node status
            region: Filter by region
            
        Returns:
            List of node information
            
        Raises:
            WorldChainNetworkError: If request fails
        """
        try:
            params = {}
            if status:
                params["status"] = status.value
            if region:
                params["region"] = region
                
            async with self._session.get(
                f"{self.base_url}/nodes",
                params=params
            ) as response:
                if response.status != 200:
                    raise WorldChainNetworkError(
                        f"Failed to list nodes: {await response.text()}"
                    )
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise WorldChainNetworkError(f"Network error: {str(e)}")

    async def get_audit_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        operation: Optional[str] = None
    ) -> List[Dict]:
        """
        Get audit logs with optional filtering.
        
        Args:
            start_time: Filter logs after this time
            end_time: Filter logs before this time
            operation: Filter by operation type
            
        Returns:
            List of audit log entries
        """
        logs = self._audit_logs
        
        if start_time:
            logs = [
                log for log in logs
                if datetime.fromisoformat(log["timestamp"]) >= start_time
            ]
            
        if end_time:
            logs = [
                log for log in logs
                if datetime.fromisoformat(log["timestamp"]) <= end_time
            ]
            
        if operation:
            logs = [log for log in logs if log["operation"] == operation]
            
        return logs

    async def get_network_info(self) -> Dict:
        """
        Get World Chain network information.
        
        Returns:
            Dict containing network status and metrics
            
        Raises:
            WorldChainNetworkError: If request fails
        """
        try:
            async with self._session.get(
                f"{self.base_url}/network-info"
            ) as response:
                if response.status != 200:
                    raise WorldChainNetworkError(
                        f"Failed to get network info: {await response.text()}"
                    )
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise WorldChainNetworkError(f"Network error: {str(e)}")

    async def get_rate_limit_status(self) -> Dict:
        """Get current rate limit status."""
        return {
            "remaining_tokens": self._rate_limit_tokens,
            "rate_limit": self.rate_limit,
            "reset_time": self._last_rate_limit_reset.isoformat()
        }

    async def clear_caches(self):
        """Clear all caches."""
        self._node_health_cache.clear()
        self._token_balances_cache.clear()

    async def clear_transaction_history(self):
        """Clear transaction history."""
        self._transaction_history.clear()

    async def get_service_status(self) -> Dict:
        """Get comprehensive service status."""
        return {
            "rate_limit": await self.get_rate_limit_status(),
            "cache_sizes": {
                "node_health": len(self._node_health_cache),
                "token_balances": len(self._token_balances_cache)
            },
            "transaction_count": len(self._transaction_history),
            "audit_log_count": len(self._audit_logs),
            "session_active": self._session is not None
        } 