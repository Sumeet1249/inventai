import matplotlib.pyplot as plt
import numpy as np
import os

class PhysicsPlotter:
    """Generates heatmaps from physics solver outputs."""
    
    @staticmethod
    def plot_stress_heatmap(points: np.ndarray, stress: np.ndarray, output_path: str):
        """Plots a 3D scatter heatmap of the stress field."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Convert to MPa for plot scale
        stress_mpa = stress / 1e6
        
        sc = ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                        c=stress_mpa, cmap='jet', alpha=0.6, s=10)
        
        cbar = plt.colorbar(sc, ax=ax, label='Von Mises Stress (MPa)')
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('PINN Linear Elasticity Analysis')
        
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return output_path
