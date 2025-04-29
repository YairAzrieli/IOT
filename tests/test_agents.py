"""
Unit tests for specialized agent implementations for the wheelchair simulation.
"""

import unittest
import random
from agents.sensor_agent import SensorAgent, ProximitySensorAgent, BodySensorAgent
from agents.navigation_agent import NavigationAgent
from agents.motor_agent import MotorAgent
from agents.ui_agent import UIAgent
from core.message import Message


class TestSensorAgents(unittest.TestCase):
    """Test the sensor agent implementations."""
    
    def test_proximity_sensor_agent(self):
        """Test that proximity sensor agent works correctly."""
        # Create a proximity sensor agent with a fixed position
        agent = ProximitySensorAgent("proximity1", (0, 0), 5.0)
        
        # Check initialization
        self.assertEqual(agent.id, "proximity1")
        self.assertEqual(agent.position, (0, 0))
        self.assertEqual(agent.range, 5.0)
        
        # Test detecting an obstacle
        obstacles = [{"position": (3, 0), "radius": 1.0}]
        agent.update_environment(obstacles=obstacles)
        
        # Agent should detect the obstacle
        messages = agent.compute()
        
        # There should be at least one message reporting the obstacle
        self.assertTrue(len(messages) > 0)
        
        # The message should be addressed to the navigation agent
        self.assertEqual(messages[0].receiver_id, "navigation")
        
        # The message should contain obstacle information
        self.assertIn("detected_obstacles", messages[0].content)
    
    def test_body_sensor_agent(self):
        """Test that body sensor agent works correctly."""
        # Create a body sensor agent
        agent = BodySensorAgent("body1")
        
        # Test with battery level
        agent.update_environment(battery_level=75)
        
        # Agent should report the battery level
        messages = agent.compute()
        
        # There should be a message
        self.assertTrue(len(messages) > 0)
        
        # The message should be addressed to the UI agent
        self.assertEqual(messages[0].receiver_id, "ui")
        
        # The message should contain battery information
        self.assertIn("battery_level", messages[0].content)
        self.assertEqual(messages[0].content["battery_level"], 75)


class TestNavigationAgent(unittest.TestCase):
    """Test the navigation agent implementation."""
    
    def setUp(self):
        """Set up a navigation agent for testing."""
        self.agent = NavigationAgent("navigation")
        
        # Set up some initial state
        self.agent.state["position"] = (0, 0)
        self.agent.state["target"] = (10, 10)
        self.agent.state["detected_obstacles"] = []
    
    def test_initialization(self):
        """Test that navigation agent is initialized correctly."""
        self.assertEqual(self.agent.id, "navigation")
        self.assertIn("position", self.agent.state)
        self.assertIn("target", self.agent.state)
        self.assertIn("detected_obstacles", self.agent.state)
    
    def test_obstacle_processing(self):
        """Test that navigation agent processes obstacle messages."""
        # Create an obstacle message
        obstacle_msg = Message(
            sender_id="proximity1",
            receiver_id="navigation",
            content={
                "type": "obstacle_update",
                "detected_obstacles": [{"position": (5, 5), "distance": 3.0}]
            }
        )
        
        # Agent receives the message
        self.agent.receive(obstacle_msg)
        
        # Agent computes
        messages = self.agent.compute()
        
        # Check that the agent updated its internal obstacle list
        self.assertTrue(len(self.agent.state["detected_obstacles"]) > 0)
        
        # There should be a message to the motor agent with movement instructions
        motor_msgs = [m for m in messages if m.receiver_id == "motor"]
        self.assertTrue(len(motor_msgs) > 0)
        self.assertIn("movement", motor_msgs[0].content)


class TestMotorAgent(unittest.TestCase):
    """Test the motor agent implementation."""
    
    def setUp(self):
        """Set up a motor agent for testing."""
        self.agent = MotorAgent("motor")
    
    def test_initialization(self):
        """Test that motor agent is initialized correctly."""
        self.assertEqual(self.agent.id, "motor")
        self.assertIn("speed", self.agent.state)
        self.assertIn("direction", self.agent.state)
    
    def test_movement_command(self):
        """Test that motor agent processes movement commands."""
        # Create a movement command message
        move_msg = Message(
            sender_id="navigation",
            receiver_id="motor",
            content={
                "type": "movement_command",
                "movement": {"speed": 2.0, "direction": 45}
            }
        )
        
        # Agent receives the message
        self.agent.receive(move_msg)
        
        # Agent computes
        messages = self.agent.compute()
        
        # Check that the agent updated its internal state
        self.assertEqual(self.agent.state["speed"], 2.0)
        self.assertEqual(self.agent.state["direction"], 45)
        
        # There should be a status message to the UI agent
        ui_msgs = [m for m in messages if m.receiver_id == "ui"]
        self.assertTrue(len(ui_msgs) > 0)
        self.assertIn("speed", ui_msgs[0].content)
        self.assertIn("direction", ui_msgs[0].content)


class TestUIAgent(unittest.TestCase):
    """Test the UI agent implementation."""
    
    def setUp(self):
        """Set up a UI agent for testing."""
        self.agent = UIAgent("ui")
    
    def test_initialization(self):
        """Test that UI agent is initialized correctly."""
        self.assertEqual(self.agent.id, "ui")
        self.assertIn("battery_level", self.agent.state)
        self.assertIn("speed", self.agent.state)
        self.assertIn("direction", self.agent.state)
        self.assertIn("obstacles", self.agent.state)
    
    def test_status_updates(self):
        """Test that UI agent processes status updates."""
        # Create a battery update message
        battery_msg = Message(
            sender_id="body1",
            receiver_id="ui",
            content={
                "type": "status_update",
                "battery_level": 65
            }
        )
        
        # Create a motor status message
        motor_msg = Message(
            sender_id="motor",
            receiver_id="ui",
            content={
                "type": "status_update",
                "speed": 1.5,
                "direction": 90
            }
        )
        
        # Agent receives the messages
        self.agent.receive(battery_msg)
        self.agent.receive(motor_msg)
        
        # Agent computes
        self.agent.compute()
        
        # Check that the agent updated its internal state
        self.assertEqual(self.agent.state["battery_level"], 65)
        self.assertEqual(self.agent.state["speed"], 1.5)
        self.assertEqual(self.agent.state["direction"], 90)


if __name__ == "__main__":
    unittest.main()
