"""
Unit tests for core components (Agent, Message, Environment).
"""

import unittest
import random
from core.agent import Agent
from core.message import Message
from core.environment import Environment, Scheduler


class TestAgent(unittest.TestCase):
    """Test the Agent class."""
    
    def test_initialization(self):
        """Test that an agent can be initialized properly."""
        agent = Agent("test_agent")
        self.assertEqual(agent.id, "test_agent")
        self.assertEqual(agent.mailbox, [])
    
    def test_receive_message(self):
        """Test that an agent can receive a message."""
        agent = Agent("test_agent")
        message = Message("sender", "test_agent", {"content": "test"})
        agent.receive(message)
        self.assertEqual(len(agent.mailbox), 1)
        self.assertEqual(agent.mailbox[0].content, {"content": "test"})
    
    def test_clear_mailbox(self):
        """Test that an agent's mailbox can be cleared."""
        agent = Agent("test_agent")
        message = Message("sender", "test_agent", {"content": "test"})
        agent.receive(message)
        agent.clear_mailbox()
        self.assertEqual(agent.mailbox, [])


class TestMessage(unittest.TestCase):
    """Test the Message class."""
    
    def test_initialization(self):
        """Test that a message can be initialized properly."""
        message = Message("sender", "receiver", {"key": "value"})
        self.assertEqual(message.sender_id, "sender")
        self.assertEqual(message.receiver_id, "receiver")
        self.assertEqual(message.content, {"key": "value"})


class TestEnvironment(unittest.TestCase):
    """Test the Environment class."""
    
    def test_register_agent(self):
        """Test that an agent can be registered with the environment."""
        env = Environment()
        agent = Agent("test_agent")
        env.register_agent(agent)
        self.assertIn("test_agent", env.agents)
    
    def test_step(self):
        """Test that the environment can step forward."""
        class TestingAgent(Agent):
            def compute(self):
                self.compute_called = True
                return []
                
            def update_state(self):
                self.update_called = True
        
        env = Environment()
        agent = TestingAgent("test_agent")
        env.register_agent(agent)
        
        # Step the environment
        env.step()
        
        # Check that compute and update_state were called
        self.assertTrue(hasattr(agent, "compute_called"))
        self.assertTrue(hasattr(agent, "update_called"))


if __name__ == "__main__":
    unittest.main()
