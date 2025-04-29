"""
Sensor Agent implementation.

Responsible for reading environmental or body sensors and 
sending data to the navigation system.
"""

from typing import List, Dict, Any, Optional
from core.agent import Agent
from core.message import Message


class SensorAgent(Agent):
    """
    An agent that manages a sensor (environmental or body).
    
    Attributes:
        id (str): Unique identifier for the agent.
        sensor_type (str): Type of sensor (e.g., "proximity", "temperature").
        data_recipients (List[str]): List of agent IDs that should receive sensor data.
        sensor_value (float): Current sensor reading.
        threshold (float): Threshold for significant sensor events.
    """
    
    def __init__(self, id: str, sensor_type: str, data_recipients: List[str], 
                 threshold: float = 0.0):
        """
        Initialize a sensor agent.
        
        Args:
            id (str): Unique identifier for the agent.
            sensor_type (str): Type of sensor.
            data_recipients (List[str]): Recipients of sensor data.
            threshold (float): Threshold for significant readings.
        """
        super().__init__(id)
        self.sensor_type = sensor_type
        self.data_recipients = data_recipients
        self.state = {
            "sensor_value": 0.0,
            "threshold": threshold
        }
    
    def read_sensor(self) -> float:
        """
        Read current sensor value.
        
        This is a placeholder that would be replaced by actual sensor API calls
        or simulation logic.
        
        Returns:
            float: Current sensor reading.
        """
        # In a real implementation, this would read from hardware
        # or a simulated environment
        return 0.0  # Default value, should be overridden
    
    def compute(self) -> List[Message]:
        """
        Read sensor and generate messages if thresholds are exceeded.
        
        Returns:
            List[Message]: Messages containing sensor data.
        """
        # Read the current sensor value
        current_value = self.read_sensor()
        self.state["new_sensor_value"] = current_value
        
        # Only send messages if reading is significant
        messages = []
        if abs(current_value - self.state["sensor_value"]) > self.state["threshold"]:
            for recipient_id in self.data_recipients:
                messages.append(Message(
                    sender_id=self.id,
                    receiver_id=recipient_id,
                    content={
                        "type": "sensor_reading",
                        "sensor_type": self.sensor_type,
                        "value": current_value,
                        "timestamp": -1  # Will be set by the environment
                    }
                ))
        
        return messages
    
    def update_state(self) -> None:
        """Update the stored sensor value with the newly read value."""
        if "new_sensor_value" in self.state:
            self.state["sensor_value"] = self.state["new_sensor_value"]
            del self.state["new_sensor_value"]


class ProximitySensorAgent(SensorAgent):
    """A specialized sensor agent that simulates a proximity sensor."""
    
    def __init__(self, id: str, data_recipients: List[str], max_distance: float = 100.0):
        """
        Initialize a proximity sensor.
        
        Args:
            id (str): Unique identifier for the agent.
            data_recipients (List[str]): Recipients of sensor data.
            max_distance (float): Maximum detectable distance.
        """
        super().__init__(id, "proximity", data_recipients)
        self.state["max_distance"] = max_distance
    
    def read_sensor(self) -> float:
        """
        Simulate reading from a proximity sensor.
        
        In a real implementation, this would read from the hardware.
        
        Returns:
            float: Simulated distance reading.
        """
        # This would be replaced with actual sensor readings
        # For now, just return a constant value
        return 50.0  # Half the maximum distance


class BodySensorAgent(SensorAgent):
    """A specialized sensor agent that simulates body monitoring sensors."""
    
    def __init__(self, id: str, data_recipients: List[str], sensor_type: str = "posture"):
        """
        Initialize a body sensor.
        
        Args:
            id (str): Unique identifier for the agent.
            data_recipients (List[str]): Recipients of sensor data.
            sensor_type (str): Type of body sensor (e.g., "posture", "motion").
        """
        super().__init__(id, sensor_type, data_recipients)
    
    def read_sensor(self) -> float:
        """
        Simulate reading from a body sensor.
        
        Returns:
            float: Simulated sensor reading.
        """
        # This would be replaced with actual sensor readings
        return 0.0  # Normal condition