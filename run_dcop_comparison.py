"""
Run and compare DCOP algorithms on various graph types.

This script implements the specific requirements of the assignment:
1. Generate three types of graphs:
   - Uniform random graph with density 0.25
   - Uniform random graph with density 0.75
   - Graph coloring with density 0.1
2. Run five algorithms on each graph:
   - DSA-C with p=0.2
   - DSA-C with p=0.7
   - DSA-C with p=1.0
   - MGM
   - MGM-2
3. Run each algorithm on 30 different problem instances
4. Average the results over the 30 runs
5. Plot the global cost vs. iteration for each algorithm
"""

import os
import random
import time
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any, Tuple

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
from core.environment import Environment
from core.message import Message  # Make sure Message is imported here


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
    
    # Exchange initial value messages so agents know about their neighbors
    for agent in agents.values():
        for neighbor_id in agent.state["neighbors"]:
            if neighbor_id in agents:
                agents[neighbor_id].receive(
                    Message(
                        sender_id=agent.id,
                        receiver_id=neighbor_id,
                        content={
                            "type": "value_message",
                            "value": agent.state["value"],
                            "iteration": 0
                        }
                    )
                )
    
    # Run algorithm for specified iterations
    costs = []
    
    # Get initial assignment cost
    assignment = {agent_id: agents[agent_id].state["value"] for agent_id in agent_ids}
    cost = calculate_global_cost(graph, assignment)
    costs.append(cost)
    
    # Print initial cost
    print(f"      Initial cost: {cost:.2f}")
    
    for iteration in range(num_iterations):
        # Step environment (will call compute() on all agents)
        env.step()
        
        # Get current assignment
        assignment = {agent_id: agents[agent_id].state["value"] for agent_id in agent_ids}
        
        # Calculate global cost
        cost = calculate_global_cost(graph, assignment)
        costs.append(cost)
        
        # Print every 10 iterations
        if (iteration + 1) % 10 == 0:
            print(f"      Iteration {iteration + 1}, cost: {cost:.2f}")
    
    # Print final cost - בתיקון הבאג של חלוקה באפס
    improvement = (costs[0] - costs[-1]) / costs[0] * 100 if costs[0] != 0 else 0
    print(f"      Final cost: {costs[-1]:.2f}, improvement: {improvement:.2f}%")
    
    return costs


def run_comparison(num_agents: int = 30, num_iterations: int = 50, 
                 num_runs: int = 30, seed: int = 42):
    """
    Run and compare DCOP algorithms on various graph types.
    
    Args:
        num_agents (int): Number of agents in each graph.
        num_iterations (int): Number of iterations to run for each algorithm.
        num_runs (int): Number of different graphs to generate and average over.
        seed (int): Random seed for reproducibility.
    """
    # Make directories for results
    os.makedirs("results", exist_ok=True)
    
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Define graph types
    graph_types = [
        ("uniform_sparse", 5, 0.25),  # Uniform random graph with density 0.25
        ("uniform_dense", 5, 0.75),   # Uniform random graph with density 0.75
        ("graph_coloring", 3, 0.1)    # Graph coloring with 3 colors and density 0.1
    ]
    
    # Define algorithms
    algorithms = [
        ("DSA-C (p=0.2)", lambda id, d, n: DSAAgent(id, d, n, 0.2)),
        ("DSA-C (p=0.7)", lambda id, d, n: DSAAgent(id, d, n, 0.7)),
        ("DSA-C (p=1.0)", lambda id, d, n: DSAAgent(id, d, n, 1.0)),
        ("MGM", lambda id, d, n: MGMAgent(id, d, n)),
        ("MGM-2", lambda id, d, n: MGM2Agent(id, d, n, 0.5))
    ]
    
    # Initialize results dictionary: graph_type -> algorithm -> run -> costs
    results = {}
    for graph_type, _, _ in graph_types:
        results[graph_type] = {}
        for alg_name, _ in algorithms:
            results[graph_type][alg_name] = []
    
    # Run experiments for each graph type
    for graph_type, domain_size, density in graph_types:
        print(f"\nRunning experiments on {graph_type} graph:")
        print(f"  Domain size: {domain_size}, Density: {density}")
        
        # Generate graphs for the runs
        graphs = []
        for run in range(num_runs):
            run_seed = seed + run
            random.seed(run_seed)
            
            if graph_type.startswith("uniform"):
                graph = generate_uniform_random_graph(
                    num_agents, domain_size, density, 100, 200)
            else:  # graph_coloring
                graph = generate_graph_coloring(
                    num_agents, domain_size, density, 100, 200)
            graphs.append(graph)
        
        # Run each algorithm on all graphs
        for alg_name, agent_factory in algorithms:
            print(f"  Running algorithm: {alg_name}")
            
            for run, graph in enumerate(graphs):
                print(f"    Run {run+1}/{num_runs}")
                run_seed = seed + run
                costs = run_dcop_algorithm(graph, agent_factory, num_iterations, run_seed)
                results[graph_type][alg_name].append(costs)
    
    # Calculate average costs per iteration
    avg_results = {}
    for graph_type in results:
        avg_results[graph_type] = {}
        for alg_name in results[graph_type]:
            # Convert list of lists to 2D numpy array
            cost_array = np.array(results[graph_type][alg_name])
            # Calculate mean along runs axis
            avg_costs = np.mean(cost_array, axis=0)
            avg_results[graph_type][alg_name] = avg_costs
    
    # Save results to CSV
    for graph_type in avg_results:
        with open(f"results/{graph_type}_results.csv", "w") as f:
            # Write header
            f.write("Iteration")
            for alg_name in avg_results[graph_type]:
                f.write(f",{alg_name}")
            f.write("\n")
            
            # Write data
            for i in range(len(next(iter(avg_results[graph_type].values())))):
                f.write(f"{i}")
                for alg_name in avg_results[graph_type]:
                    f.write(f",{avg_results[graph_type][alg_name][i]}")
                f.write("\n")
    
    # Plot results
    for graph_type in avg_results:
        plt.figure(figsize=(12, 8))
        
        for alg_name in avg_results[graph_type]:
            iterations = range(len(avg_results[graph_type][alg_name]))
            plt.plot(iterations, avg_results[graph_type][alg_name], label=alg_name)
        
        plt.title(f"Algorithm Comparison on {graph_type} Graph")
        plt.xlabel("Iteration")
        plt.ylabel("Global Cost")
        plt.legend()
        plt.grid(True)
        
        plt.savefig(f"results/{graph_type}_comparison.png")
        plt.close()
    
    print("\nResults have been saved to the 'results' directory.")


if __name__ == "__main__":
    # הרץ את ההשוואה עם ערכים קטנים יותר לטובת בדיקה מהירה
    # שנה למספרים גדולים יותר לתוצאות רשמיות
    run_comparison(num_agents=5, num_iterations=20, num_runs=3, seed=42)
