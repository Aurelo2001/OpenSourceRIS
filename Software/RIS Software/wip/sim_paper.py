import numpy as np
import matplotlib.pyplot as plt

# === RIS-SPEZIFIKATION ===
Nx, Ny = 16, 16
M = Nx * Ny
dx = 0.02001  # [m]
dy = 0.013    # [m]

# === FREQUENZ ===
fc = 5.15e9
c = 3e8
wavelength = c / fc
k = 2 * np.pi / wavelength

# === MASK UND PHASEN ===
# Beispielhafte ON/OFF-Matrix (hier zufällig)
np.random.seed(42)
mask = np.random.choice([0, 1], size=(Ny, Nx))

# Phasenwerte in Radiant
phi_on = 0         # z.B. 0°
phi_off = np.pi    # z.B. 180°

# Komplexe Phasenzuordnung: exp(j*phi)
phase_matrix = np.where(mask == 1, np.exp(1j * phi_on), np.exp(1j * phi_off))
x = phase_matrix.flatten()  # (M,) komplexer Vektor für diag(x)

# === POSITIONEN DER RIS-ELEMENTE ===
x_coords = np.arange(Nx) * dx
y_coords = np.arange(Ny) * dy
X, Y = np.meshgrid(x_coords, y_coords)
positions = np.stack([X.ravel(), Y.ravel()], axis=1)

# === GITTER ===
theta = np.linspace(-np.pi/2, np.pi/2, 181)
phi = np.linspace(-np.pi/2, np.pi/2, 181)
THETA, PHI = np.meshgrid(theta, phi)

# === ARRAY MANIFOLD FUNKTION ===
def array_manifold(theta, phi):
    direction = np.array([
        np.cos(theta) * np.cos(phi),
        np.cos(theta) * np.sin(phi),
    ])
    phase_shifts = k * (positions @ direction)
    return np.exp(1j * phase_shifts)

# === SIGNAL UND KANAL ===
J = 4
sigma = np.ones(J, dtype=complex)

np.random.seed(0)
G_static = (np.random.randn(M, J) + 1j * np.random.randn(M, J)) / np.sqrt(2)

# === BEAMPATTERN BERECHNEN ===
B2 = np.zeros_like(THETA)

for i in range(THETA.shape[0]):
    for j in range(THETA.shape[1]):
        v_vec = array_manifold(THETA[i, j], PHI[i, j])
        B = np.abs(np.conj(v_vec).T @ np.diag(x) @ G_static @ sigma)
        B2[i, j] = B ** 2

# === NORMALISIERUNG UND PLOT ===
NPB = B2 / np.max(B2)

plt.figure(figsize=(8, 6))
plt.imshow(10 * np.log10(NPB), extent=[-90, 90, -90, 90], origin='lower', cmap='viridis')
plt.title('Normalized Power Beampattern (16x16 RIS mit ON/OFF-Matrix)')
plt.xlabel('Azimuth φ (deg)')
plt.ylabel('Elevation θ (deg)')
plt.colorbar(label='Power (dB)')
plt.tight_layout()
plt.show()

