"""
Environment class that coordinates all agents and their interactions.

Responsible for coordinating agent execution order and message passing.
"""

from typing import Dict, List, Optional, Type
from core.agent import Agent
from core.message import Message


class Environment:
    """
    Manages all agents and coordinates their interactions.
    
    Attributes:
        agents (Dict[str, Agent]): All agents in the simulation indexed by ID.
        time_step (int): Current simulation step.
    """
    
    def __init__(self):
        """Initialize a new environment with no agents and at time step 0."""
        self.agents = {}
        self.time_step = 0
    
    def register_agent(self, agent: Agent) -> None:
        """
        Add an agent to the environment.
        
        Args:
            agent (Agent): The agent to register.
        """
        if agent.id in self.agents:
            raise ValueError(f"Agent with ID {agent.id} already exists")
        self.agents[agent.id] = agent
    
    def step(self) -> None:
        """
        Execute one simulation step.
        
        This involves:
        1. Having each agent compute its actions
        2. Delivering resulting messages to recipient agents
        3. Updating each agent's state
        4. Clearing mailboxes
        5. Incrementing the time step
        """
        # Collect all messages from agents
        all_messages = []
        for agent in self.agents.values():
            outgoing_messages = agent.compute()
            all_messages.extend(outgoing_messages)
        
        # Deliver messages to recipients
        for msg in all_messages:
            if msg.receiver_id in self.agents:
                self.agents[msg.receiver_id].receive(msg)
            else:
                print(f"Warning: Message for unknown agent {msg.receiver_id}")
        
        # Update states and clear mailboxes
        for agent in self.agents.values():
            agent.update_state()
            agent.clear_mailbox()
        
        # Increment time step
        self.time_step += 1


class Scheduler:
    """
    Optional class to control the order of agent execution.
    
    Attributes:
        order (List[str]): The IDs of agents in execution order.
        environment (Environment): Reference to the environment.
    """
    
    def __init__(self, environment: Environment):
        """
        Initialize a scheduler with default order.
        
        Args:
            environment (Environment): The environment to schedule.
        """
        self.environment = environment
        self.order = list(environment.agents.keys())
    
    def set_order(self, order: List[str]) -> None:
        """
        Set the execution order of agents.
        
        Args:
            order (List[str]): Agent IDs in desired execution order.
        
        Raises:
            ValueError: If any agent ID in the order doesn't exist.
        """
        for agent_id in order:
            if agent_id not in self.environment.agents:
                raise ValueError(f"Agent {agent_id} does not exist")
        self.order = order
    
    def get_next_agent(self, current_idx: Optional[int] = None) -> Agent:
        """
        Get the next agent to execute.
        
        Args:
            current_idx (Optional[int]): Current index in the order.
            
        Returns:
            Agent: The next agent to execute.
        """
        if current_idx is None:
            return self.environment.agents[self.order[0]]
        
        next_idx = (current_idx + 1) % len(self.order)
        return self.environment.agents[self.order[next_idx]]