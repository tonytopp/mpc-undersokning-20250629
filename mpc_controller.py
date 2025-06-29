import numpy as np
import cvxpy as cp
from typing import List, Tuple, Optional
import matplotlib.pyplot as plt


class MPCController:
    """Model Predictive Control implementation för linjära system"""
    
    def __init__(self, A: np.ndarray, B: np.ndarray, Q: np.ndarray, R: np.ndarray, 
                 N: int, x_min: Optional[np.ndarray] = None, x_max: Optional[np.ndarray] = None,
                 u_min: Optional[np.ndarray] = None, u_max: Optional[np.ndarray] = None):
        """
        Initialiserar MPC-controller
        
        Args:
            A: System matrix (n x n)
            B: Input matrix (n x m)
            Q: State weight matrix (n x n)
            R: Input weight matrix (m x m)
            N: Prediction horizon
            x_min: Minimum state constraints
            x_max: Maximum state constraints
            u_min: Minimum input constraints
            u_max: Maximum input constraints
        """
        self.A = A
        self.B = B
        self.Q = Q
        self.R = R
        self.N = N
        
        self.n = A.shape[0]  # Antal states
        self.m = B.shape[1]  # Antal inputs
        
        self.x_min = x_min if x_min is not None else -np.inf * np.ones(self.n)
        self.x_max = x_max if x_max is not None else np.inf * np.ones(self.n)
        self.u_min = u_min if u_min is not None else -np.inf * np.ones(self.m)
        self.u_max = u_max if u_max is not None else np.inf * np.ones(self.m)
        
    def solve(self, x0: np.ndarray, x_ref: Optional[np.ndarray] = None) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        Löser MPC-problemet för given initial state
        
        Args:
            x0: Initial state
            x_ref: Reference trajectory (om None, används noll-referens)
            
        Returns:
            Optimal control input och predicted states
        """
        if x_ref is None:
            x_ref = np.zeros((self.N + 1, self.n))
        
        # Beslutsvariablar
        x = cp.Variable((self.N + 1, self.n))
        u = cp.Variable((self.N, self.m))
        
        # Kostnadsfunktion
        cost = 0
        for k in range(self.N):
            cost += cp.quad_form(x[k] - x_ref[k], self.Q)
            cost += cp.quad_form(u[k], self.R)
        cost += cp.quad_form(x[self.N] - x_ref[self.N], self.Q)
        
        # Begränsningar
        constraints = [x[0] == x0]
        
        for k in range(self.N):
            constraints.append(x[k + 1] == self.A @ x[k] + self.B @ u[k])
            constraints.append(x[k] >= self.x_min)
            constraints.append(x[k] <= self.x_max)
            constraints.append(u[k] >= self.u_min)
            constraints.append(u[k] <= self.u_max)
        
        constraints.append(x[self.N] >= self.x_min)
        constraints.append(x[self.N] <= self.x_max)
        
        # Lös optimeringsproblemet
        problem = cp.Problem(cp.Minimize(cost), constraints)
        problem.solve()
        
        if problem.status != cp.OPTIMAL:
            raise ValueError(f"MPC problem inte optimalt löst: {problem.status}")
        
        # Returnera första kontrollinputen och predicted states
        return u.value[0], x.value
    
    def simulate(self, x0: np.ndarray, T: int, x_ref: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulerar systemet med MPC-styrning
        
        Args:
            x0: Initial state
            T: Antal tidssteg att simulera
            x_ref: Reference trajectory
            
        Returns:
            States och control inputs över tid
        """
        states = np.zeros((T + 1, self.n))
        inputs = np.zeros((T, self.m))
        
        states[0] = x0
        
        for t in range(T):
            # Lös MPC för nuvarande state
            if x_ref is not None:
                ref_horizon = x_ref[t:min(t + self.N + 1, len(x_ref))]
                if len(ref_horizon) < self.N + 1:
                    # Utöka med sista värdet om referensen är kortare
                    ref_horizon = np.vstack([ref_horizon, 
                                           np.tile(ref_horizon[-1], (self.N + 1 - len(ref_horizon), 1))])
            else:
                ref_horizon = None
                
            u_opt, _ = self.solve(states[t], ref_horizon)
            inputs[t] = u_opt
            
            # Simulera systemet ett steg
            states[t + 1] = self.A @ states[t] + self.B @ u_opt
            
        return states, inputs
    

def example_double_integrator():
    """Exempel: MPC för double integrator (position och hastighet)"""
    # System: double integrator
    dt = 0.1
    A = np.array([[1, dt], 
                  [0, 1]])
    B = np.array([[0.5 * dt**2], 
                  [dt]])
    
    # Viktmatriser
    Q = np.diag([10, 1])  # Vikta position mer än hastighet
    R = np.array([[0.1]])  # Liten vikt på control input
    
    # Begränsningar
    x_min = np.array([-10, -2])  # Min position och hastighet
    x_max = np.array([10, 2])     # Max position och hastighet
    u_min = np.array([-1])        # Min acceleration
    u_max = np.array([1])         # Max acceleration
    
    # Skapa MPC-controller
    N = 20  # Prediction horizon
    mpc = MPCController(A, B, Q, R, N, x_min, x_max, u_min, u_max)
    
    # Initial state och referens
    x0 = np.array([-5, 0])  # Start vid position -5, hastighet 0
    T = 100
    
    # Skapa referenstrajectory (step response)
    x_ref = np.zeros((T + 1, 2))
    x_ref[20:, 0] = 5  # Flytta till position 5 efter 20 tidssteg
    
    # Simulera
    states, inputs = mpc.simulate(x0, T, x_ref)
    
    # Plotta resultat
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
    
    time = np.arange(T + 1) * dt
    
    ax1.plot(time, states[:, 0], label='Position')
    ax1.plot(time, x_ref[:, 0], '--', label='Referens')
    ax1.set_ylabel('Position')
    ax1.legend()
    ax1.grid(True)
    
    ax2.plot(time, states[:, 1], label='Hastighet')
    ax2.axhline(y=x_max[1], color='r', linestyle='--', label='Max hastighet')
    ax2.axhline(y=x_min[1], color='r', linestyle='--', label='Min hastighet')
    ax2.set_ylabel('Hastighet')
    ax2.legend()
    ax2.grid(True)
    
    ax3.step(time[:-1], inputs[:, 0], label='Acceleration')
    ax3.axhline(y=u_max[0], color='r', linestyle='--', label='Max acceleration')
    ax3.axhline(y=u_min[0], color='r', linestyle='--', label='Min acceleration')
    ax3.set_xlabel('Tid (s)')
    ax3.set_ylabel('Acceleration')
    ax3.legend()
    ax3.grid(True)
    
    plt.tight_layout()
    plt.savefig('mpc_double_integrator.png')
    print("MPC-simulering klar! Se 'mpc_double_integrator.png'")
    
    return mpc, states, inputs


if __name__ == "__main__":
    mpc, states, inputs = example_double_integrator()