"""
Base Agent class that all specialized agents will inherit from.

Provides the core functionality for message handling and state management.
"""

from typing import List, Dict, Any, Optional
from core.message import Message


class Agent:
    """
    Base class for all agents in the simulation.
    
    Attributes:
        id (str): Unique identifier for the agent.
        mailbox (List[Message]): Queue of incoming messages.
        state (Dict[str, Any]): Internal state of the agent.
    """
    
    def __init__(self, id: str):
        """
        Initialize a new agent.
        
        Args:
            id (str): Unique identifier for the agent.
        """
        self.id = id
        self.mailbox = []
        self.state = {}
    
    def receive(self, msg: Message) -> None:
        """
        Add a message to the agent's mailbox.
        
        Args:
            msg (Message): The message to be received.
        """
        self.mailbox.append(msg)
    
    def compute(self) -> List[Message]:
        """
        Process incoming messages and decide on actions.
        
        This method should be overridden by specific agent implementations
        to provide their logic.
        
        Returns:
            List[Message]: Messages to be sent to other agents.
        """
        # Base implementation returns empty list
        # Subclasses should override this
        return []
    
    def update_state(self) -> None:
        """
        Update internal state based on computation results.
        
        This method should be overridden by specific agent implementations.
        The base implementation does nothing.
        """
        pass
    
    def clear_mailbox(self) -> None:
        """
        Clear the mailbox after processing messages.
        """
        self.mailbox = []