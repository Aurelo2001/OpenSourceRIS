import sys
import numpy as np

import plotly.graph_objects as go
import plotly.io as pio

import json

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QCheckBox, QHBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView


class RISSimulator:
    def __init__(self, N=16, dx=0.02001, dy=0.013):
        self.N = N
        self.dx = dx
        self.dy = dy
        self.f = 5.5e9
        self.wavelength = 3e8 / self.f
        self.k = 2 * np.pi / self.wavelength
        self.incident_theta = np.radians(25)
        self.incident_phi = 0
        self.patch_enabled = np.ones((N, N), dtype=bool)
        self.patch_onoff = np.ones((N, N), dtype=bool)
        self.phase_shift_table = None
        self.show_incident_vector = True
        self.ris_plane = "xy"
        self.update_patch_grid()
        self._update_patch_phases()

    def update_patch_grid(self):
        n = np.arange(self.N) - (self.N - 1) / 2
        self.XX, self.YY = np.meshgrid(n, n)

    def set_frequency(self, freq_hz):
        self.f = freq_hz
        self.wavelength = 3e8 / self.f
        self.k = 2 * np.pi / self.wavelength
        self._update_patch_phases()

    def set_incident_angle(self, theta_rad, phi_rad):
        self.incident_theta = theta_rad
        self.incident_phi = phi_rad

    def set_patch_enabled(self, enabled_matrix):
        self.patch_enabled = np.array(enabled_matrix, dtype=bool)

    def set_patch_onoff(self, onoff_matrix):
        self.patch_onoff = np.array(onoff_matrix, dtype=bool)
        self._update_patch_phases()

    def load_phase_shift_table(self, fname):
        table = np.loadtxt(fname, delimiter="\t", skiprows=1)
        table[:, 0] *= 1e9
        self.phase_shift_table = table
        self._update_patch_phases()

    def _interpolate_phase(self, freq_hz, on=True):
        if self.phase_shift_table is None:
            return 0.0
        freqs = self.phase_shift_table[:, 0]
        if on:
            phases = self.phase_shift_table[:, 1]
        else:
            phases = self.phase_shift_table[:, 2]
        phase_interp = np.interp(freq_hz, freqs, phases)
        return np.deg2rad(phase_interp)

    def _update_patch_phases(self):
        if self.phase_shift_table is not None:
            on_phase = self._interpolate_phase(self.f, True)
            off_phase = self._interpolate_phase(self.f, False)
            self.patch_phase = np.where(self.patch_onoff, on_phase, off_phase)
        else:
            self.patch_phase = np.zeros((self.N, self.N))

    def get_array_factor(self, theta, phi):
        AF = np.zeros(theta.shape, dtype=np.complex128)
        for ix in range(self.N):
            for iy in range(self.N):
                if not self.patch_enabled[ix, iy]:
                    continue
                phase = self.patch_phase[ix, iy]
                AF += np.exp(1j * self.k * (
                    self.XX[ix, iy] * self.dx * np.sin(theta) * np.cos(phi) +
                    self.YY[ix, iy] * self.dy * np.sin(theta) * np.sin(phi)
                ) + 1j * phase)
        AF_abs = np.abs(AF)
        AF_norm = AF_abs / np.max(AF_abs)
        return AF_norm

    def _get_coords(self, AF_norm, THETA, PHI, ris_plane="xy"):
        # Flexible Achsenzuordnung für verschiedene Ebenen
        if ris_plane == "xy":
            X = AF_norm * np.sin(THETA) * np.cos(PHI)
            Y = AF_norm * np.sin(THETA) * np.sin(PHI)
            Z = AF_norm * np.cos(THETA)
        elif ris_plane == "zx":
            X = AF_norm * np.sin(THETA) * np.cos(PHI)
            Z = AF_norm * np.sin(THETA) * np.sin(PHI)
            Y = AF_norm * np.cos(THETA)
        elif ris_plane == "yz":
            Y = AF_norm * np.sin(THETA) * np.cos(PHI)
            Z = AF_norm * np.sin(THETA) * np.sin(PHI)
            X = AF_norm * np.cos(THETA)
        else:
            raise ValueError("Unknown ris_plane!")
        return X, Y, Z

    def _get_coord_limits(self, X, Y, Z, ris_plane="xy"):
        # Flexible Achsenzuordnung für verschiedene Ebenen
        max_val = np.max(np.abs([X, Y, Z]))
        max_val = max(1.1 * max_val, 0.7)
        if ris_plane == "xy":
            xaxis=dict(range=[-max_val, max_val])
            yaxis=dict(range=[-max_val, max_val])
            zaxis=dict(range=[0, max_val])
        elif ris_plane == "zx":
            xaxis=dict(range=[-max_val, max_val])
            yaxis=dict(range=[0, max_val])
            zaxis=dict(range=[-max_val, max_val])
        elif ris_plane == "yz":
            xaxis=dict(range=[0, max_val])
            yaxis=dict(range=[-max_val, max_val])
            zaxis=dict(range=[-max_val, max_val])
        else:
            raise ValueError("Unknown ris_plane!")
        return xaxis, yaxis, zaxis


    def plot_beampattern(self, show_incident_vector=None, ris_plane=None):
        if show_incident_vector is None:
            show_incident_vector = self.show_incident_vector
        if ris_plane is None:
            ris_plane = self.ris_plane

        theta = np.linspace(0, np.pi / 2, 120)
        phi = np.linspace(0, 2 * np.pi, 240)
        THETA, PHI = np.meshgrid(theta, phi)
        AF_norm = self.get_array_factor(THETA, PHI)
        X, Y, Z = self._get_coords(AF_norm, THETA, PHI, ris_plane)

        data = [
            go.Surface(
                x=X, y=Y, z=Z, surfacecolor=AF_norm,
                colorscale="viridis", cmin=0, cmax=1, opacity=0.85,
                showscale=False,
            )
        ]

        # Incident Angle als Linienvektor einzeichnen (optional)
        if show_incident_vector:
            vec_len = 1.2
            th = self.incident_theta
            ph = self.incident_phi
            # Vektor-Umrechnung je nach RIS-Ebene
            if ris_plane == "xy":
                x_vec = [0, vec_len * np.sin(th) * np.cos(ph)]
                y_vec = [0, vec_len * np.sin(th) * np.sin(ph)]
                z_vec = [0, vec_len * np.cos(th)]
            elif ris_plane == "zx":
                x_vec = [0, vec_len * np.sin(th) * np.cos(ph)]
                z_vec = [0, vec_len * np.sin(th) * np.sin(ph)]
                y_vec = [0, vec_len * np.cos(th)]
            elif ris_plane == "yz":
                y_vec = [0, vec_len * np.sin(th) * np.cos(ph)]
                z_vec = [0, vec_len * np.sin(th) * np.sin(ph)]
                x_vec = [0, vec_len * np.cos(th)]
            else:
                raise ValueError("Unknown ris_plane!")
            data.append(
                go.Scatter3d(
                    x=x_vec, y=y_vec, z=z_vec,
                    mode='lines+markers',
                    line=dict(color='red', width=8),
                    marker=dict(size=4, color='red'),
                    name='Incident Angle',
                )
            )

        # --- Dynamischer quadratischer Achsenbereich ---

        xaxis, yaxis, zaxis = self._get_coord_limits(X, Y, Z, ris_plane)

        fig = go.Figure(data=data)
        fig.update_layout(
            title=f"RIS 3D Beampattern (RIS-Ebene: {ris_plane.upper()})",
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z",
                aspectmode="manual",
                aspectratio=dict(x=1, y=1, z=1),
                xaxis=xaxis,
                yaxis=yaxis,
                zaxis=zaxis,
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )

        # Plotly-Konfiguration für immer sichtbare Bedienelemente
        plotly_config = dict(
            displayModeBar="always",
            displaylogo=False,
            responsive=True,
        )

        return pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config=plotly_config)

# ------- PySide6 GUI-Teil -------

# class RISWindow(QMainWindow):
#     def __init__(self, sim: RISSimulator, phase_file="AngS11.txt"):
#         super().__init__()
#         self.sim = sim
#         self.sim.load_phase_shift_table(phase_file)
#         self.setWindowTitle("RIS Beampattern Visualisierung")
#         self.setGeometry(200, 200, 1200, 800)

#         # Haupt-Widget und Layout
#         main_widget = QWidget()
#         self.setCentralWidget(main_widget)
#         layout = QVBoxLayout(main_widget)

#         # Bedienelemente oben
#         control_layout = QHBoxLayout()
#         layout.addLayout(control_layout)

#         # RIS-Ebene-Auswahl
#         self.combo_plane = QComboBox()
#         self.combo_plane.addItems(["xy", "yz", "zx"])
#         self.combo_plane.currentTextChanged.connect(self.on_plane_changed)
#         control_layout.addWidget(QLabel("RIS-Ebene:"))
#         control_layout.addWidget(self.combo_plane)

#         # Incident Angle Schalter
#         self.chk_incident = QCheckBox("Incident Vector anzeigen")
#         self.chk_incident.setChecked(True)
#         self.chk_incident.stateChanged.connect(self.on_incident_toggle)
#         control_layout.addWidget(self.chk_incident)

#         # Frequenz-Slider
#         self.freq_label = QLabel("Frequenz: 5.500 GHz")
#         control_layout.addWidget(self.freq_label)
#         self.freq_slider = QSlider(Qt.Horizontal)
#         self.freq_slider.setMinimum(5150)
#         self.freq_slider.setMaximum(5875)
#         self.freq_slider.setValue(5500)
#         self.freq_slider.setTickInterval(25)
#         self.freq_slider.valueChanged.connect(self.on_freq_changed)
#         control_layout.addWidget(self.freq_slider)

#         control_layout.addStretch(1)

#         # Plotly-WebView
#         self.webview = QWebEngineView()
#         layout.addWidget(self.webview, stretch=1)

#         # Initialer Plot
#         self.update_plot()

#     def on_plane_changed(self, plane):
#         self.sim.ris_plane = plane
#         self.update_plot()

#     def on_incident_toggle(self, state):
#         self.sim.show_incident_vector = bool(state)
#         self.update_plot()

#     def on_freq_changed(self, value):
#         freq_ghz = value / 1000.0
#         self.freq_label.setText(f"Frequenz: {freq_ghz:.3f} GHz")
#         self.sim.set_frequency(value * 1e6)
#         self.update_plot()

#     def update_plot(self):
#         html = self.sim.plot_beampattern()
#         self.webview.setHtml(html)

###################################################################################################

# ---- RISSimulator wie bisher (siehe oben), nicht nochmal aufgeführt! ----

# ---------------- PySide6 GUI mit JS-Update -----------------

class RISWindow(QMainWindow):
    def __init__(self, sim:RISSimulator, phase_file="AngS11.txt"):
        super().__init__()
        self.sim = sim
        self.sim.load_phase_shift_table(phase_file)
        self.setWindowTitle("RIS Beampattern Visualisierung")
        self.setGeometry(200, 200, 1200, 800)

        # Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)

        self.combo_plane = QComboBox()
        self.combo_plane.addItems(["xy", "yz", "zx"])
        self.combo_plane.currentTextChanged.connect(self.on_plane_changed)
        control_layout.addWidget(QLabel("RIS-Ebene:"))
        control_layout.addWidget(self.combo_plane)

        self.chk_incident = QCheckBox("Incident Vector anzeigen")
        self.chk_incident.setChecked(True)
        self.chk_incident.stateChanged.connect(self.on_incident_toggle)
        control_layout.addWidget(self.chk_incident)

        self.freq_label = QLabel("Frequenz: 5.500 GHz")
        control_layout.addWidget(self.freq_label)
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setMinimum(5150)
        self.freq_slider.setMaximum(5875)
        self.freq_slider.setValue(5500)
        self.freq_slider.setTickInterval(25)
        self.freq_slider.valueChanged.connect(self.on_freq_changed)
        control_layout.addWidget(self.freq_slider)

        control_layout.addStretch(1)

        self.webview = QWebEngineView()
        layout.addWidget(self.webview, stretch=1)

        # ------------- Initiales Plotly-Div als HTML laden --------------
        self.plot_div_id = "risplot"
        html = f"""
        <html>
          <head>
            <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
          </head>
          <body style="margin:0;overflow:hidden;">
            <div id="{self.plot_div_id}" style="width:100vw;height:100vh;"></div>
          </body>
        </html>
        """
        self.webview.setHtml(html)
        # Erstes Plot-Update nach kurzem Delay, damit Plotly geladen ist
        QTimer.singleShot(500, self.update_plot)

    def on_plane_changed(self, plane):
        self.sim.ris_plane = plane
        self.update_plot()

    def on_incident_toggle(self, state):
        self.sim.show_incident_vector = bool(state)
        self.update_plot()

    def on_freq_changed(self, value):
        freq_ghz = value / 1000.0
        self.freq_label.setText(f"Frequenz: {freq_ghz:.3f} GHz")
        self.sim.set_frequency(value * 1e6)
        self.update_plot()

    def update_plot(self):
        # ----------- Plotly Figure wie gewohnt erzeugen ---------------
        fig_html, fig_dict = self._get_plotly_figure()
        # ---------- Sende nur das Update per JavaScript --------------
        js_code = (
            f"Plotly.react('{self.plot_div_id}', {json.dumps(fig_dict['data'])}, {json.dumps(fig_dict['layout'])}, {{displayModeBar:'always', responsive:true}});"
        )
        # Plotly kann noch nicht sicher sofort angesprochen werden – falls nicht, versuche nach kurzem Delay nochmal!
        def try_run_js():
            self.webview.page().runJavaScript(js_code)
        QTimer.singleShot(100, try_run_js)

    def _get_plotly_figure(self):
        # Deine gewohnte Plotly-Logik – Rückgabe: (HTML, fig.to_plotly_json())
        theta = np.linspace(0, np.pi / 2, 80)
        phi = np.linspace(0, 2 * np.pi, 160)
        THETA, PHI = np.meshgrid(theta, phi)
        AF_norm = self.sim.get_array_factor(THETA, PHI)
        AF_db = 20 * np.log10(AF_norm + 1e-12)
        X, Y, Z = self.sim._get_coords(AF_norm, THETA, PHI, self.sim.ris_plane)

        plot_db = True
        AF_plot = AF_norm if plot_db == False else AF_db
        # np.savetxt("af_plot.csv", AF_plot, "%.3f") # TODO

        data = [
            go.Surface(
                x=X.tolist(),
                y=Y.tolist(),
                z=Z.tolist(),
                surfacecolor=AF_plot.tolist(),
                colorscale="viridis", cmin=-40, cmax=0, opacity=1,
                showscale=False,
                # hoverinfo='skip',
                hovertemplate=(
                    "Normierter AF: %{surfacecolor:.2f}<extra></extra>"
                ),
            ),
        ]

        # Incident-Vektor als Linie
        if self.sim.show_incident_vector:
            vec_len = 1.2
            th = self.sim.incident_theta
            ph = self.sim.incident_phi
            plane = self.sim.ris_plane
            if plane == "xy":
                x_vec = [0, vec_len * np.sin(th) * np.cos(ph)]
                y_vec = [0, vec_len * np.sin(th) * np.sin(ph)]
                z_vec = [0, vec_len * np.cos(th)]
            elif plane == "zx":
                x_vec = [0, vec_len * np.sin(th) * np.cos(ph)]
                z_vec = [0, vec_len * np.sin(th) * np.sin(ph)]
                y_vec = [0, vec_len * np.cos(th)]
            elif plane == "yz":
                y_vec = [0, vec_len * np.sin(th) * np.cos(ph)]
                z_vec = [0, vec_len * np.sin(th) * np.sin(ph)]
                x_vec = [0, vec_len * np.cos(th)]
            else:
                raise ValueError("Unknown ris_plane!")
            
            incident_theta_deg = np.degrees(self.sim.incident_theta)
            incident_phi_deg = np.degrees(self.sim.incident_phi)
            angle_str = f"Incident θ: {incident_theta_deg:.1f}°, φ: {incident_phi_deg:.1f}°"
            text=[angle_str, angle_str]
            data.append(
                go.Scatter3d(
                    x=x_vec, y=y_vec, z=z_vec,
                    mode='lines+markers',
                    line=dict(color='red', width=8),
                    marker=dict(size=4, color='red'),
                    name='Incident Angle',
                    text=text,
                    hovertemplate="%{text}<extra></extra>"
                )
            )

        # Quadratische Skalierung
        xaxis, yaxis, zaxis = self.sim._get_coord_limits(X, Y, Z, plane)

        layout = go.Layout(
            title=f"RIS 3D Beampattern (RIS-Ebene: {self.sim.ris_plane.upper()})",
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z",
                aspectmode="manual",
                aspectratio=dict(x=1, y=1, z=1),
                xaxis=xaxis,
                yaxis=yaxis,
                zaxis=zaxis,
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )
        fig = go.Figure(data=data, layout=layout)
        # html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')   # nur für Export
        return None, fig.to_plotly_json()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sim = RISSimulator()
    phase_file = "AngS11.txt"
    win = RISWindow(sim, phase_file)
    win.show()
    sys.exit(app.exec())

