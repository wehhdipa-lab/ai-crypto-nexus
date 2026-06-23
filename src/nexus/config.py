"""AI-Crypto Nexus — Configuration management."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class ChainID(int, Enum):
    ETHEREUM = 1
    ARBITRUM = 42161
    OPTIMISM = 10
    BASE = 8453
    POLYGON = 137
    BSC = 56
    AVALANCHE = 43114
    SOLANA = 0  # placeholder


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    model_config = {"env_prefix": "NEXUS_", "env_file": ".env", "extra": "ignore"}

    # Environment
    env: Environment = Environment.DEVELOPMENT
    log_level: str = "INFO"
    data_dir: Path = Path("~/.nexus/data").expanduser()

    # Blockchain RPCs
    ethereum_rpc: str = "https://eth.llamarpc.com"
    arbitrum_rpc: str = "https://arb1.arbitrum.io/rpc"
    optimism_rpc: str = "https://mainnet.optimism.io"
    base_rpc: str = "https://mainnet.base.org"
    polygon_rpc: str = "https://polygon-rpc.com"
    bsc_rpc: str = "https://bsc-dataseed.binance.org"
    avalanche_rpc: str = "https://api.avax.network/ext/bc/C/rpc"
    solana_rpc: str = "https://api.mainnet-beta.solana.com"

    # AI/LLM
    openai_api_key: Optional[SecretStr] = None
    anthropic_api_key: Optional[SecretStr] = None
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096

    # Trading
    default_slippage_bps: int = 50  # 0.5%
    max_position_size_usd: float = 10_000.0
    max_drawdown_pct: float = 15.0
    max_leverage: float = 3.0
    gas_priority_multiplier: float = 1.2

    # Wallet (encrypted)
    keystore_path: Path = Path("~/.nexus/keystore.enc").expanduser()
    keystore_password: Optional[SecretStr] = None

    # Data sources
    etherscan_api_key: Optional[SecretStr] = None
    coingecko_api_key: Optional[SecretStr] = None
    twitter_bearer_token: Optional[SecretStr] = None

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    def get_rpc_url(self, chain: ChainID) -> str:
        """Get RPC URL for a given chain."""
        rpc_map = {
            ChainID.ETHEREUM: self.ethereum_rpc,
            ChainID.ARBITRUM: self.arbitrum_rpc,
            ChainID.OPTIMISM: self.optimism_rpc,
            ChainID.BASE: self.base_rpc,
            ChainID.POLYGON: self.polygon_rpc,
            ChainID.BSC: self.bsc_rpc,
            ChainID.AVALANCHE: self.avalanche_rpc,
            ChainID.SOLANA: self.solana_rpc,
        }
        return rpc_map.get(chain, self.ethereum_rpc)


# Singleton
settings = Settings()
