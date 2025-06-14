from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    """Configuration for a model connection."""
    model_id: str = Field(..., description="Unique identifier for the model")
    model_type: str = Field(..., description="Type of the model (e.g., 'llm', 'image', 'audio')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model-specific parameters")
    endpoint: Optional[str] = Field(None, description="Custom endpoint URL for the model")
    
class MCPConfig(BaseModel):
    """Configuration for an MCP (Model Control Protocol) server."""
    server_url: str = Field(..., description="URL of the MCP server")
    api_key: Optional[str] = Field(None, description="API key for the MCP server")
    timeout: int = Field(30, description="Timeout in seconds for MCP server requests")
    retry_attempts: int = Field(3, description="Number of retry attempts for failed requests")
    additional_headers: Dict[str, str] = Field(default_factory=dict, description="Additional headers for MCP server requests") 