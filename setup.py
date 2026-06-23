from setuptools import setup, find_packages

setup(
    name="ai-crypto-nexus",
    version="0.1.0",
    description="AI × Crypto Intelligence Platform",
    author="wehhdipa-lab",
    python_requires=">=3.11",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "web3>=6.0.0",
        "eth-abi>=5.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "torch>=2.0.0",
        "transformers>=4.35.0",
        "openai>=1.0.0",
        "anthropic>=0.18.0",
        "aiohttp>=3.9.0",
        "redis>=5.0.0",
        "pydantic>=2.5.0",
        "structlog>=23.2.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "ruff>=0.1.0",
            "mypy>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nexus=nexus.cli:main",
        ],
    },
)
