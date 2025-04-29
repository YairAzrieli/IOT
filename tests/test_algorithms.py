"""
Unit tests for DCOP algorithm implementations.
"""

import unittest
import random
from core.message import Message
from algorithms.dsa import DSAAgent
from algorithms.mgm import MGMAgent
from algorithms.mgm2 import MGM2Agent


class TestDSAAgent(unittest.TestCase):
    """Test the DSA Agent implementation."""
    
    def setUp(self):
        """Set up a simple test scenario with two agents."""
        random.seed(42)  # For reproducible tests
        
        # Create a simple domain and neighbors setup
        self.domain = [1, 2, 3]
        
        # Create two agents
        self.agent1 = DSAAgent("agent1", self.domain, ["agent2"], 0.7)
        self.agent2 = DSAAgent("agent2", self.domain, ["agent1"], 0.7)
        
        # Set up a simple constraint: prefer different values
        costs = {(1, 1): 10, (1, 2): 5, (1, 3): 5,
                 (2, 1): 5, (2, 2): 10, (2, 3): 5,
                 (3, 1): 5, (3, 2): 5, (3, 3): 10}
                 
        self.agent1.add_constraint("agent2", costs)
        self.agent2.add_constraint("agent1", costs)
        
        # Explicitly set initial values for testing
        self.agent1.state["value"] = 1
        self.agent2.state["value"] = 1
    
    def test_initialization(self):
        """Test that DSA agents are initialized correctly."""
        self.assertEqual(self.agent1.id, "agent1")
        self.assertEqual(self.agent1.state["domain"], self.domain)
        self.assertEqual(self.agent1.state["neighbors"], ["agent2"])
        self.assertEqual(self.agent1.state["probability"], 0.7)
    
    def test_value_exchange(self):
        """Test that agents can exchange value messages."""
        # Agent 1 sends its value to Agent 2
        message = Message(
            sender_id="agent1",
            receiver_id="agent2",
            content={"type": "value_message", "value": 1, "iteration": 0}
        )
        self.agent2.receive(message)
        
        # Check that Agent 2 received the value
        self.assertEqual(self.agent2.state["neighbor_values"].get("agent1"), 1)
    
    def test_utility_calculation(self):
        """Test that utility is calculated correctly."""
        # Set up the known neighbor value
        self.agent1.state["neighbor_values"]["agent2"] = 1
        
        # Calculate utility for different values
        utility_1 = self.agent1.calculate_utility(1)  # Same as neighbor (cost 10)
        utility_2 = self.agent1.calculate_utility(2)  # Different (cost 5)
        
        # Check that different is better than same (higher utility is better)
        self.assertTrue(utility_2 > utility_1)
    
    def test_best_value_finding(self):
        """Test that the agent can find the best value."""
        # Set up the known neighbor value
        self.agent1.state["neighbor_values"]["agent2"] = 1
        
        # Find best value
        best_value, best_utility = self.agent1.find_best_value()
        
        # Best value should be different from neighbor (2 or 3)
        self.assertNotEqual(best_value, 1)
        self.assertIn(best_value, [2, 3])


class TestMGMAgent(unittest.TestCase):
    """Test the MGM Agent implementation."""
    
    def setUp(self):
        """Set up a simple test scenario with two agents."""
        random.seed(42)  # For reproducible tests
        
        # Create a simple domain and neighbors setup
        self.domain = [1, 2, 3]
        
        # Create two agents
        self.agent1 = MGMAgent("agent1", self.domain, ["agent2"])
        self.agent2 = MGMAgent("agent2", self.domain, ["agent1"])
        
        # Set up a simple constraint: prefer different values
        costs = {(1, 1): 10, (1, 2): 5, (1, 3): 5,
                 (2, 1): 5, (2, 2): 10, (2, 3): 5,
                 (3, 1): 5, (3, 2): 5, (3, 3): 10}
                 
        self.agent1.add_constraint("agent2", costs)
        self.agent2.add_constraint("agent1", costs)
        
        # Explicitly set initial values for testing
        self.agent1.state["value"] = 1
        self.agent2.state["value"] = 1
    
    def test_initialization(self):
        """Test that MGM agents are initialized correctly."""
        self.assertEqual(self.agent1.id, "agent1")
        self.assertEqual(self.agent1.state["domain"], self.domain)
        self.assertEqual(self.agent1.state["neighbors"], ["agent2"])
        self.assertEqual(self.agent1.state["phase"], "value")
    
    def test_gain_calculation(self):
        """Test that gain is calculated correctly."""
        # Set up the known neighbor value
        self.agent1.state["neighbor_values"]["agent2"] = 1
        
        # Calculate best value and gain
        best_value, best_utility, gain = self.agent1.find_best_value()
        
        # Gain should be positive (better to be different)
        self.assertTrue(gain > 0)
        self.assertNotEqual(best_value, 1)  # Best is different from current
    
    def test_phase_switching(self):
        """Test that the agent changes phases correctly."""
        # Initial phase is "value"
        self.assertEqual(self.agent1.state["phase"], "value")
        
        # Set up known neighbor value
        self.agent1.state["neighbor_values"]["agent2"] = 1
        
        # Run compute once (should switch to "gain" phase)
        self.agent1.compute()
        self.assertEqual(self.agent1.state["phase"], "gain")
        
        # Run compute again (should switch back to "value" phase)
        self.agent1.compute()
        self.assertEqual(self.agent1.state["phase"], "value")


class TestMGM2Agent(unittest.TestCase):
    """Test the MGM-2 Agent implementation."""
    
    def setUp(self):
        """Set up a simple test scenario with two agents."""
        random.seed(42)  # For reproducible tests
        
        # Create a simple domain and neighbors setup
        self.domain = [1, 2, 3]
        
        # Create two agents
        self.agent1 = MGM2Agent("agent1", self.domain, ["agent2"], 0.5)
        self.agent2 = MGM2Agent("agent2", self.domain, ["agent1"], 0.5)
        
        # Set up a simple constraint: prefer different values
        costs = {(1, 1): 10, (1, 2): 5, (1, 3): 5,
                 (2, 1): 5, (2, 2): 10, (2, 3): 5,
                 (3, 1): 5, (3, 2): 5, (3, 3): 10}
                 
        self.agent1.add_constraint("agent2", costs)
        self.agent2.add_constraint("agent1", costs)
        
        # Explicitly set initial values for testing
        self.agent1.state["value"] = 1
        self.agent2.state["value"] = 1
    
    def test_initialization(self):
        """Test that MGM2 agents are initialized correctly."""
        self.assertEqual(self.agent1.id, "agent1")
        self.assertEqual(self.agent1.state["domain"], self.domain)
        self.assertEqual(self.agent1.state["neighbors"], ["agent2"])
        self.assertEqual(self.agent1.state["p"], 0.5)
        self.assertEqual(self.agent1.state["phase"], "value")
    
    def test_phase_cycle(self):
        """Test that the agent goes through all 4 phases."""
        # Initial phase is "value"
        self.assertEqual(self.agent1.state["phase"], "value")
        
        # Exchange values
        self.agent1.state["neighbor_values"]["agent2"] = 1
        self.agent2.state["neighbor_values"]["agent1"] = 1
        
        # Force agent to be an offerer
        self.agent1.state["role"] = "offerer"
        
        # Run compute (value -> offer)
        self.agent1.compute()
        self.assertEqual(self.agent1.state["phase"], "offer")
        
        # Run compute (offer -> accept)
        self.agent1.compute()
        self.assertEqual(self.agent1.state["phase"], "accept")
        
        # Run compute (accept -> evaluate)
        self.agent1.compute()
        self.assertEqual(self.agent1.state["phase"], "evaluate")
        
        # Run compute (evaluate -> value)
        self.agent1.compute()
        self.assertEqual(self.agent1.state["phase"], "value")
    
    def test_bilateral_change(self):
        """Test that the agent can find good bilateral changes."""
        # Set up the known neighbor value
        self.agent1.state["neighbor_values"]["agent2"] = 1
        
        # Calculate best bilateral change
        our_value, neighbor_value, gain = self.agent1.find_best_bilateral_change("agent2")
        
        # Both values should change from 1
        self.assertNotEqual(our_value, 1)
        self.assertNotEqual(neighbor_value, 1)
        
        # Gain should be positive
        self.assertTrue(gain > 0)


if __name__ == "__main__":
    unittest.main()
