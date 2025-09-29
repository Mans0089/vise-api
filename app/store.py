
from typing import Dict, Any

class InMemoryStore:
    def __init__(self):
        self._clients: Dict[int, Dict[str, Any]] = {}
        self._next_id: int = 1

    def add_client(self, data: Dict[str, Any]) -> int:
        cid = self._next_id
        self._next_id += 1
        self._clients[cid] = {**data, "clientId": cid}
        return cid

    def get_client(self, client_id: int):
        return self._clients.get(client_id)

store = InMemoryStore()
