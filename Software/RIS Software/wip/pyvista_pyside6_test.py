import numpy as np
import pyvista as pv

# --- Phase-Tabelle laden ---
phase_table = np.loadtxt("AngS11.txt", delimiter="\t", skiprows=1)
phase_table[:, 0] *= 1e9  # Frequenzen in Hz umrechnen

def interpolate_phase(freq):
    return np.deg2rad(np.interp(freq, phase_table[:, 0], phase_table[:, 1]))

# --- Konstanten ---
c = 3e8
fc = 5.5e9  # Trägerfrequenz
λ = c / fc

# --- RIS-Konfiguration ---
Nx, Ny = 16, 16
dx, dy = 0.02001, 0.013
positions = np.array([[i * dx, j * dy, 0] for j in range(Ny) for i in range(Nx)])

# --- Eingangswinkel einstellen ---
theta_in_deg = 30   # Elevation
phi_in_deg = 0      # Azimut
θ_in = np.deg2rad(theta_in_deg)
φ_in = np.deg2rad(phi_in_deg)
k_in = np.array([np.cos(θ_in)*np.cos(φ_in), np.cos(θ_in)*np.sin(φ_in), np.sin(θ_in)])

# --- RIS-Phasen berechnen ---
phi_ris = interpolate_phase(fc)
x = np.exp(1j * (phi_ris - 2 * np.pi / λ * positions @ k_in))

# --- Beampattern berechnen ---
θ_vals = np.linspace(-90, 90, 181)
φ_vals = np.linspace(-90, 90, 181)
θ_grid, φ_grid = np.meshgrid(np.deg2rad(θ_vals), np.deg2rad(φ_vals), indexing='ij')

kx = np.cos(θ_grid) * np.cos(φ_grid)
ky = np.cos(θ_grid) * np.sin(φ_grid)
kz = np.sin(θ_grid)
response = np.zeros_like(θ_grid, dtype=np.complex128)

for i in range(θ_grid.shape[0]):
    for j in range(θ_grid.shape[1]):
        k_out = np.array([kx[i, j], ky[i, j], kz[i, j]])
        phase = np.exp(1j * 2 * np.pi / λ * positions @ k_out)
        response[i, j] = np.sum(x * phase)

# --- Normalisieren ---
power = np.abs(response)**2
npb = power / np.max(power)

# --- Koordinaten für 3D-Plot ---
r = npb
X = r * kx
Y = r * ky
Z = r * kz

# --- PyVista: Darstellung ---
grid = pv.StructuredGrid()
grid.points = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
grid.dimensions = θ_grid.shape[0], θ_grid.shape[1], 1
grid["NPB"] = r.ravel(order="C")

plotter = pv.Plotter()
plotter.add_mesh(grid, scalars="NPB", cmap="viridis", show_scalar_bar=True)
plotter.add_axes()
plotter.show()
