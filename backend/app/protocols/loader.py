import os
import json
import logging
from typing import Dict, List, Optional
from backend.app.schemas.protocol import ProtocolSchema
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class ProtocolLoader:
    def __init__(self, protocols_dir: Optional[str] = None):
        self.protocols_dir = protocols_dir or settings.PROTOCOLS_DIR
        self._protocols: Dict[str, ProtocolSchema] = {}
        self.load_all()

    def load_all(self) -> Dict[str, ProtocolSchema]:
        """Loads and parses all protocol JSON files from disk."""
        resolved_dir = self.protocols_dir
        if not os.path.isabs(resolved_dir):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
            resolved_dir = os.path.join(base_dir, self.protocols_dir)

        if not os.path.exists(resolved_dir):
            alt_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../protocols/examples"))
            if os.path.exists(alt_dir):
                resolved_dir = alt_dir

        self._protocols.clear()
        if not os.path.exists(resolved_dir):
            logger.warning(f"Protocols directory not found at: {resolved_dir}")
            return self._protocols

        for file_name in os.listdir(resolved_dir):
            if file_name.endswith(".json"):
                full_path = os.path.join(resolved_dir, file_name)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        protocol = ProtocolSchema(**data)
                        self._protocols[protocol.protocol_id] = protocol
                        logger.info(f"Loaded protocol: {protocol.protocol_id} - {protocol.name}")
                except Exception as e:
                    logger.error(f"Failed to load protocol from {file_name}: {e}")

        logger.info(f"Total protocols loaded: {len(self._protocols)}")
        return self._protocols

    def get(self, protocol_id: str) -> Optional[ProtocolSchema]:
        return self._protocols.get(protocol_id)

    def list_all(self) -> List[ProtocolSchema]:
        return list(self._protocols.values())

protocol_loader = ProtocolLoader()
