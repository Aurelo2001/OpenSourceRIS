import numpy as np
import plotly.graph_objects as go

# === RIS SPEZIFIKATION ===
Nx, Ny = 16, 16
M = Nx * Ny
dx = 0.02001
dy = 0.013

# === FREQUENZPARAMETER ===
fc = 5.15e9
c = 3e8
wavelength = c / fc
k = 2 * np.pi / wavelength

# === MASK UND PHASEN ===
# np.random.seed(42)
# mask = np.random.choice([0, 1], size=(Ny, Nx))
mask = np.zeros(shape=(Ny, Nx))
phi_on = 0
phi_off = np.pi
phase_matrix = np.where(mask == 1, np.exp(1j * phi_on), np.exp(1j * phi_off))
x = phase_matrix.flatten()

# === POSITIONEN DER RIS-ELEMENTE ===
x_coords = np.arange(Nx) * dx
y_coords = np.arange(Ny) * dy
Xpos, Ypos = np.meshgrid(x_coords, y_coords)
positions = np.stack([Xpos.ravel(), Ypos.ravel()], axis=1)

# === WINKELGITTER ===
theta = np.linspace(0, np.pi / 2, 181)     # Elevation 0–90°
phi = np.linspace(0, 2 * np.pi, 361)       # Azimut 0–360°
THETA, PHI = np.meshgrid(theta, phi)

# === ARRAY MANIFOLD ===
def array_manifold(theta_val, phi_val):
    direction = np.array([
        np.cos(theta_val) * np.cos(phi_val),
        np.cos(theta_val) * np.sin(phi_val)
    ])
    phase_shifts = k * (positions @ direction)
    return np.exp(1j * phase_shifts)

# === SIGNAL UND KANAL ===
J = 4
sigma = np.ones(J, dtype=complex)
np.random.seed(0)
G_static = (np.random.randn(M, J) + 1j * np.random.randn(M, J)) / np.sqrt(2)

# === BEAMPATTERN-BERECHNUNG ===
B2 = np.zeros_like(THETA)
for i in range(THETA.shape[0]):
    for j in range(THETA.shape[1]):
        v_vec = array_manifold(THETA[i, j], PHI[i, j])
        B = np.abs(np.conj(v_vec).T @ np.diag(x) @ G_static @ sigma)
        B2[i, j] = B ** 2

# === NORMALISIERUNG UND CLIPPING ===
NPB = B2 / np.max(B2)
NPB_dB = 10 * np.log10(NPB)
NPB_dB_clipped = np.clip(NPB_dB, -40, 0)

# === SPHÄRISCHE KOORDINATEN IN X/Y/Z ===
R = (NPB_dB_clipped + 40) / 40  # normiert auf [0, 1] für Radius

X = R * np.sin(THETA) * np.cos(PHI)
Y = R * np.sin(THETA) * np.sin(PHI)
Z = R * np.cos(THETA)

# === PLOTLY MESH ===
fig = go.Figure(data=[
    go.Surface(
        x=X,
        y=Y,
        z=Z,
        surfacecolor=NPB_dB_clipped,
        colorscale='Viridis',
        cmin=-40,
        cmax=0,
        showscale=True,
        lighting=dict(ambient=0.5, diffuse=0.5),
    )
])

fig.update_layout(
    title="Sphärische Beampattern-Darstellung (in dB)",
    scene=dict(
        xaxis=dict(title="X"),
        yaxis=dict(title="Y"),
        zaxis=dict(title="Z"),
        aspectmode="data"
    ),
    margin=dict(l=0, r=0, b=0, t=30),
    template="plotly_white"
)

fig.show()
