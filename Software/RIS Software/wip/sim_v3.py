import numpy as np
import matplotlib.pyplot as plt

# --- Parameter ---
M, N = 16, 16
dx = 0.02001  # m
dy = 0.013    # m
fc = 5.15e9   # Hz
c = 3e8       # Lichtgeschwindigkeit
wavelength = c / fc

# --- Phasen-Tabelle vorbereiten ---
phase_table = np.loadtxt("AngS11.txt", delimiter="\t", skiprows=1)
phase_table[:,0] *= 1e9

def interpolate_phase(freq):
    return np.deg2rad(np.interp(float(freq), phase_table[0], phase_table[1]))

# --- RIS Positionen berechnen ---
x_coords = (np.arange(N) - (N - 1) / 2) * dx
y_coords = (np.arange(M) - (M - 1) / 2) * dy
xx, yy = np.meshgrid(x_coords, y_coords)
positions = np.stack([xx.ravel(), yy.ravel(), np.zeros(M * N)], axis=1)

def compute_tau(positions, theta, phi):
    u = np.array([
        np.cos(theta) * np.cos(phi),
        np.cos(theta) * np.sin(phi),
        np.sin(theta)
    ])
    return -1 / c * (positions @ u)

def compute_B(theta, phi, freq):
    tau = compute_tau(positions, theta, phi)
    phase_shift = interpolate_phase(freq)
    x = np.exp(1j * phase_shift) * np.ones(M * N)
    v = np.exp(2j * np.pi * freq * tau)
    B_complex = np.vdot(v, x)
    return np.abs(B_complex) / np.sqrt(M * N)

# --- Gitter für Azimut und Elevation ---
theta_vals = np.linspace(-np.pi/6, np.pi/6, 181)  # Elevation [-30°, +30°]
phi_vals = np.linspace(-np.pi/6, np.pi/6, 181)    # Azimut [-30°, +30°]

B_grid = np.zeros((len(theta_vals), len(phi_vals)))

for i, theta in enumerate(theta_vals):
    for j, phi in enumerate(phi_vals):
        B_grid[i, j] = compute_B(theta, phi, fc)

NPB = B_grid**2 / np.max(B_grid**2)

# --- Plot ---
plt.figure(figsize=(8, 6))
extent = [-30, 30, -30, 30]
plt.imshow(NPB, extent=extent, origin='lower', cmap='viridis', aspect='auto')
plt.colorbar(label="Normalized Power")
plt.xlabel("Azimuth (°)")
plt.ylabel("Elevation (°)")
plt.title("Normalized Power Beampattern (NPB)")
plt.tight_layout()
plt.show()
