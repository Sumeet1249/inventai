import numpy as np
from services.physics_service.solvers.elasticity import LinearElasticitySolver

def test_linear_elasticity_solver():
    # Test for aluminum (69 GPa, 0.33 Poisson)
    solver = LinearElasticitySolver(E=69.0, nu=0.33)
    
    # Generate 100 random points in a 1x1x1 cube
    points = np.random.uniform(0, 1, (100, 3))
    
    # Define a downward force
    forces = {"z": -100.0}
    
    results = solver.solve(points, forces)
    
    # Verify the structure of the output
    assert "points" in results
    assert "von_mises_stress" in results
    assert "max_stress_mpa" in results
    assert "avg_stress_mpa" in results
    
    # The length of the output stress array should match the input points
    assert len(results["von_mises_stress"]) == 100
    
    # Stress should be strictly positive (magnitude)
    assert results["max_stress_mpa"] > 0
    assert results["avg_stress_mpa"] > 0
    
    # Since forces scale linearly in our mock equation, 
    # testing a bigger force should yield higher max stress.
    heavy_results = solver.solve(points, {"z": -500.0})
    assert heavy_results["max_stress_mpa"] > results["max_stress_mpa"]
