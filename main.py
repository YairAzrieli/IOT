"""
Main entry point for the distributed agent simulation.

Demonstrates the use of the framework with different agent types
and algorithms.
"""

import time
import os
import random
from typing import List, Dict, Any, Tuple

# Import core components
from core.agent import Agent
from core.message import Message
from core.environment import Environment, Scheduler

# Import specialized agents
from agents.sensor_agent import SensorAgent, ProximitySensorAgent, BodySensorAgent
from agents.navigation_agent import NavigationAgent
from agents.motor_agent import MotorAgent
from agents.ui_agent import UIAgent

# Import DCOP algorithms
from algorithms.dsa import DSAAgent
from algorithms.mgm import MGMAgent
from algorithms.mgm2 import MGM2Agent

# Import utilities
from utils.graph_generator import (
    generate_uniform_random_graph,
    generate_graph_coloring,
    calculate_global_cost
)
from utils.logger import Logger, compare_algorithms


def run_wheelchair_simulation(num_steps: int = 10) -> None:
    """
    Run a simple wheelchair agent simulation.
    
    Args:
        num_steps (int): Number of simulation steps to run.
    """
    print("Starting wheelchair simulation...")
    
    # Create environment
    env = Environment()
    
    # Create agents
    proximity_sensor = ProximitySensorAgent(
        id="proximity_sensor",
        data_recipients=["navigation"]
    )
    
    posture_sensor = BodySensorAgent(
        id="posture_sensor",
        data_recipients=["navigation"],
        sensor_type="posture"
    )
    
    navigation = NavigationAgent(
        id="navigation",
        motor_agent_id="motor"
    )
    
    motor = MotorAgent(
        id="motor",
        navigation_agent_id="navigation"
    )
    
    ui = UIAgent(
        id="ui",
        navigation_agent_id="navigation",
        input_devices=["joystick", "voice"]
    )
    
    # Register agents with environment
    env.register_agent(proximity_sensor)
    env.register_agent(posture_sensor)
    env.register_agent(navigation)
    env.register_agent(motor)
    env.register_agent(ui)
    
    # Set up a scheduled order
    scheduler = Scheduler(env)
    scheduler.set_order(["proximity_sensor", "posture_sensor", "ui", "navigation", "motor"])
    
    # Set up initial conditions
    # Add a known destination
    ui.add_destination("kitchen", (10.0, 5.0))
    
    # Set proximity sensor to detect something at 30 units away
    proximity_sensor.state["sensor_value"] = 30.0
    
    # Override the sensor read functions for simulation
    def proximity_read():
        # Simulate object getting closer then farther
        step = env.time_step
        if step < 5:
            return 30.0 - step * 5.0  # Gets closer
        else:
            return 5.0 + (step - 5) * 5.0  # Gets farther
    
    proximity_sensor.read_sensor = proximity_read
    
    # Override UI to simulate user input
    def ui_read_input():
        step = env.time_step
        if step == 0:
            # At step 0, simulate a voice command
            return {"voice": "go to kitchen"}
        elif step == 5:
            # At step 5, simulate joystick override
            return {"joystick": {"x": 0.5, "y": 0.0}}
        else:
            return {}  # No input
    
    ui.read_user_input = ui_read_input
    
    # Run simulation for specified number of steps
    print("Starting simulation...")
    print(f"{'Step':^5} | {'Position':^15} | {'Speed':^8} | {'Direction':^10} | {'Proximity':^10}")
    print("-" * 55)
    
    for step in range(num_steps):
        # Execute one environment step
        env.step()
        
        # Print current state
        pos = motor.state["position"]
        speed = motor.state["speed"]
        direction = motor.state["direction"]
        proximity = proximity_sensor.state["sensor_value"]
        
        print(f"{step:^5} | ({pos[0]:6.2f}, {pos[1]:6.2f}) | {speed:8.2f} | {direction:10.2f} | {proximity:10.2f}")
    
    print("\nSimulation complete!")


def run_dcop_comparison(num_agents: int = 30, num_iterations: int = 50, 
                      num_runs: int = 30, seed: int = 42) -> None:
    """
    Run and compare DCOP algorithms on random graphs.
    
    Args:
        num_agents (int): Number of agents in each graph.
        num_iterations (int): Number of iterations to run for each algorithm.
        num_runs (int): Number of different graphs to generate and average over.
        seed (int): Random seed for reproducibility.
    """
    print("Running DCOP algorithm comparison...")
    
    # Make directories for results
    os.makedirs("results", exist_ok=True)
    
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Compare algorithms for three different graphs as required in the assignment
    graph_types = [
        ("uniform_sparse", 5, 0.25),  # Uniform random graph with density 0.25
        ("uniform_dense", 5, 0.75),   # Uniform random graph with density 0.75
        ("graph_coloring", 3, 0.1)    # Graph coloring with 3 colors and density 0.1
    ]
    
    # Initialize loggers for different algorithms
    loggers = {
        "DSA-C (p=0.2)": {graph_type: Logger(f"results/dsa_p02_{graph_type}.log") 
                          for graph_type, _, _ in graph_types},
        "DSA-C (p=0.7)": {graph_type: Logger(f"results/dsa_p07_{graph_type}.log") 
                          for graph_type, _, _ in graph_types},
        "DSA-C (p=1.0)": {graph_type: Logger(f"results/dsa_p10_{graph_type}.log") 
                          for graph_type, _, _ in graph_types},
        "MGM": {graph_type: Logger(f"results/mgm_{graph_type}.log") 
                for graph_type, _, _ in graph_types},
        "MGM-2": {graph_type: Logger(f"results/mgm2_{graph_type}.log") 
                 for graph_type, _, _ in graph_types}
    }
    
    # Run algorithms on each graph type
    for graph_type, domain_size, density in graph_types:
        print(f"\nRunning experiments on {graph_type} graph:")
        print(f"  Domain size: {domain_size}, Density: {density}")
        
        # For each run, generate a new graph
        for run in range(num_runs):
            print(f"  Run {run+1}/{num_runs}")
            
            # Set a different seed for each run but ensure reproducibility
            run_seed = seed + run
            random.seed(run_seed)
            
            # Generate graph based on type
            if graph_type.startswith("uniform"):
                graph = generate_uniform_random_graph(
                    num_agents, domain_size, density, 100, 200)
            else:  # graph_coloring
                graph = generate_graph_coloring(
                    num_agents, domain_size, density, 100, 200)
            
            # Run each algorithm on this graph
            algorithms = [
                ("DSA-C (p=0.2)", lambda id, d, n: DSAAgent(id, d, n, 0.2)),
                ("DSA-C (p=0.7)", lambda id, d, n: DSAAgent(id, d, n, 0.7)),
                ("DSA-C (p=1.0)", lambda id, d, n: DSAAgent(id, d, n, 1.0)),
                ("MGM", lambda id, d, n: MGMAgent(id, d, n)),
                ("MGM-2", lambda id, d, n: MGM2Agent(id, d, n, 0.5))
            ]
            
            for alg_name, agent_factory in algorithms:
                # Run algorithm with this graph
                costs = run_dcop_algorithm(
                    graph, agent_factory, num_iterations, run_seed)
                
                # Update logger with costs from this run
                for i, cost in enumerate(costs):
                    loggers[alg_name][graph_type].log_iteration(i, cost, 0)
                
                # Reset logger for next run (keep only average)
                if run < num_runs - 1:
                    loggers[alg_name][graph_type].metrics["global_cost"] = []
                    loggers[alg_name][graph_type].metrics["iterations"] = []
        
        # Plot results for this graph type
        plt_loggers = {alg: loggers[alg][graph_type] for alg in loggers}
        compare_algorithms(plt_loggers, f"results/{graph_type}_comparison.png")
    
    print("\nDCOP comparison complete! Results are in the 'results' directory.")


def run_dcop_algorithm(graph: Dict, agent_factory, num_iterations: int, 
                      seed: int) -> List[float]:
    """
    Run a DCOP algorithm on a graph.
    
    Args:
        graph (Dict): Graph description.
        agent_factory: Function that creates an agent.
        num_iterations (int): Number of iterations to run.
        seed (int): Random seed.
        
    Returns:
        List[float]: Global costs at each iteration.
    """
    # Set random seed
    random.seed(seed)
    
    # Create environment
    env = Environment()
    
    # Create agents
    agent_ids = graph["agents"]
    agents = {}
    
    for agent_id in agent_ids:
        domain = graph["domains"][agent_id]
        neighbors = []
        
        # Find neighbors based on constraints
        for (agent_i, agent_j) in graph["constraints"]:
            if agent_id == agent_i:
                neighbors.append(agent_j)
            elif agent_id == agent_j:
                neighbors.append(agent_i)
        
        # Create agent using factory
        agent = agent_factory(agent_id, domain, neighbors)
        agents[agent_id] = agent
        
        # Register agent with environment
        env.register_agent(agent)
    
    # Add constraints to agents
    for (agent_i, agent_j), costs in graph["constraints"].items():
        # Add constraint in both directions
        agents[agent_i].add_constraint(agent_j, costs)
        
        # Flip costs for the other direction
        reverse_costs = {(val_j, val_i): cost for (val_i, val_j), cost in costs.items()}
        agents[agent_j].add_constraint(agent_i, reverse_costs)
    
    # Run algorithm for specified iterations
    costs = []
    
    for _ in range(num_iterations):
        # Get current assignment
        assignment = {agent_id: agents[agent_id].state["value"] 
                     for agent_id in agent_ids}
        
        # Calculate global cost
        cost = calculate_global_cost(graph, assignment)
        costs.append(cost)
        
        # Step environment
        env.step()
    
    # Get final cost
    assignment = {agent_id: agents[agent_id].state["value"] 
                 for agent_id in agent_ids}
    cost = calculate_global_cost(graph, assignment)
    costs.append(cost)
    
    return costs


if __name__ == "__main__":
    # Run both simulations
    run_wheelchair_simulation(num_steps=10)
    print("\n" + "="*50 + "\n")
    
    # Comment this out if you don't want to run the longer DCOP comparison
    # run_dcop_comparison(num_agents=30, num_iterations=50, num_runs=2, seed=42)
