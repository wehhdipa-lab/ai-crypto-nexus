"""Protocol risk scoring."""
from dataclasses import dataclass
@dataclass
class ProtocolScore:
    protocol: str; overall: float; audit: float; tvl: float; exploit: float; team: float; decentralization: float
class ProtocolScorer:
    W = {"audit": 0.25, "tvl": 0.20, "exploit": 0.25, "team": 0.15, "decentralization": 0.15}
    def score(self, name: str, data: dict) -> ProtocolScore:
        s = {
            "audit": min(data.get("audits", 0)/3, 1),
            "tvl": min(data.get("tvl", 0)/1e9, 1),
            "exploit": 1 if data.get("exploits", 0) == 0 else max(0, 1 - data["exploits"]*0.3),
            "team": data.get("team_doxxed", 0.5),
            "decentralization": data.get("decentralization", 0.5),
        }
        overall = sum(s[k]*self.W[k] for k in self.W)
        return ProtocolScore(protocol=name, overall=round(overall,3), **s)
