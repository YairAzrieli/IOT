# Distributed Agent Simulation Framework

## Overview
This project implements a modular, event-driven simulation framework for distributed agents. It supports both:

1. A smart wheelchair simulation with environmental sensors, navigation, motors, and user interface agents
2. Implementation of distributed constraint optimization problem (DCOP) algorithms including DSA-C, MGM, and MGM-2

## Project Structure

- **core/** - Core framework components
  - `agent.py` - Base Agent class
  - `message.py` - Message class for inter-agent communication
  - `environment.py` - Environment class and Scheduler
  
- **agents/** - Specialized agent implementations
  - `sensor_agent.py` - Environmental and body sensors
  - `navigation_agent.py` - Path planning and navigation
  - `motor_agent.py` - Motor control
  - `ui_agent.py` - User interface handling
  
- **algorithms/** - DCOP algorithm implementations
  - `dsa.py` - Distributed Stochastic Algorithm (DSA-C)
  - `mgm.py` - Maximum Gain Message (MGM)
  - `mgm2.py` - Maximum Gain Message 2 (MGM-2)
  
- **utils/** - Utilities for graph generation and logging
  - `graph_generator.py` - Random graph generators
  - `logger.py` - Logging and visualization

- **tests/** - Unit tests
  - `test_core.py` - Tests for core components
  - `test_agents.py` - Tests for specialized agents
  - `test_algorithms.py` - Tests for DCOP algorithms

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Required packages: `matplotlib`, `numpy` (see `requirements.txt`)

### Installation
1. Clone the repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

### Running the Simulation
To run the wheelchair simulation:
```python
python main.py
```

To run the DCOP algorithm comparison (uncomment the relevant section in `main.py`):
```python
# Modify parameters as needed
run_dcop_comparison(num_agents=30, num_iterations=50, num_runs=30, seed=42)
```

## Quick Start

For the easiest way to run the complete assignment:
```python
python run_assignment.py
```

This script will:
1. Check the environment and install any missing packages
2. Run the wheelchair demo
3. Let you choose to run a quick demo or the full DCOP experiments

## Assignment Details

This framework is built according to the following requirements:

1. Implement an event-driven, discrete-time simulation of distributed agents
2. Support three DCOP algorithms: DSA-C, MGM, and MGM-2
3. Generate and solve three types of problems:
   - Uniform random graphs with density 0.25
   - Uniform random graphs with density 0.75
   - Graph coloring problems with density 0.1
4. Run each algorithm on 30 different problems and compute average performance
5. Plot cost versus iteration for each algorithm and problem type