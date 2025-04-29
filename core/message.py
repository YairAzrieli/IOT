"""
Message class for inter-agent communication.

Defines the structure for messages exchanged between agents.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Message:
    """
    A message passed between agents.
    
    Attributes:
        sender_id (str): ID of the agent sending the message.
        receiver_id (str): ID of the agent receiving the message.
        content (Dict[str, Any]): Data payload of the message.
    """
    sender_id: str
    receiver_id: str
    content: Dict[str, Any]