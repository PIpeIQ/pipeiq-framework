from setuptools import setup, find_packages

setup(
    name="pipeiq",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "solana>=0.30.2",
        "anchorpy>=0.18.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "base58>=2.1.1",
        "construct>=2.10.68",
        "pydantic>=2.0.0",
        "websockets>=11.0.3",  # For WebSocket connections
        "aiohttp>=3.8.0",      # For async HTTP requests
        "backoff>=2.2.1",
        "cachetools>=5.3.0",
        "asyncio>=3.4.3",      # For async/await support
        "typing-extensions>=4.0.0",  # For enhanced type hints
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
        "hellomoon": [
            "aiohttp>=3.8.0",
            "websockets>=11.0.3",
            "cachetools>=5.3.0",
            "backoff>=2.2.1",
        ]
    },
    author="PipeIQ",
    author_email="info@pipeiq.io",
    description="A Solana-compatible SDK for connecting to different models and MCP servers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pipeiq",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 