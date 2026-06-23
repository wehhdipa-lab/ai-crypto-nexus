"""Multi-chain Web3 provider."""
from web3 import Web3
from nexus.config import settings, ChainID
import structlog
logger = structlog.get_logger()

class Web3Manager:
    _instances: dict[int, Web3] = {}
    @classmethod
    def get_provider(cls, chain: ChainID) -> Web3:
        if chain.value not in cls._instances:
            cls._instances[chain.value] = Web3(Web3.HTTPProvider(settings.get_rpc_url(chain)))
        return cls._instances[chain.value]
    @classmethod
    def get_balance(cls, chain: ChainID, address: str) -> float:
        w3 = cls.get_provider(chain)
        return float(Web3.from_wei(w3.eth.get_balance(Web3.to_checksum_address(address)), "ether"))
