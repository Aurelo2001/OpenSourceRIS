import plotly.graph_objects as go
import numpy as np

# Beispiel: Richtcharakteristik als Kugel mit Amplitudenmodulation
theta = np.linspace(0, np.pi, 100)
phi = np.linspace(0, 2*np.pi, 100)
theta, phi = np.meshgrid(theta, phi)

# Beispielhafte Funktion für die Richtcharakteristik (ersetzen durch echte Werte)
r = np.abs(np.sin(theta) * np.cos(2*phi))

# Umrechnen in kartesische Koordinaten
x = r * np.sin(theta) * np.cos(phi)
y = r * np.sin(theta) * np.sin(phi)
z = r * np.cos(theta)

# Plotly-3D-Surface erstellen
fig = go.Figure(
    data=[
        go.Surface(
            x=x, y=y, z=z, surfacecolor=r,
            colorbar=dict(title='Amplitude')
        )
    ]
)
fig.update_layout(
    title='3D Richtcharakteristik der Antenne',
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
        aspectmode='data'
    )
)

# Interaktive HTML-Datei exportieren
fig.show()
