import numpy as np
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QDoubleSpinBox, QGroupBox, QPushButton, QComboBox, QCheckBox, QSizePolicy
)
# new
import plotly.graph_objects as go
import plotly.io as pio
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView
import json

# old:
import pyqtgraph as pg
import pyqtgraph.opengl as gl

try:
    from rissimulator import RISsimulator
except:
    from lib.rissimulator import RISsimulator


class RISsimulator_ui(QMainWindow):
    def __init__(self):
        super().__init__()

        self.sim = RISsimulator()
        self.show_hover = False

        # init main widget
        self.setWindowTitle("RIS Beampattern - 3D Mesh mit Ebenenraster")
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

######### controlpanel layout
        layout_config = QHBoxLayout()

        # frequency input
        layout_freq = QHBoxLayout()
        self.freq_input = QDoubleSpinBox()
        self.freq_input.setSuffix(" GHz")
        self.freq_input.setRange(5.0, 6.0)
        self.freq_input.setValue(5.15)
        self.freq_input.setSingleStep(0.1)
        self.freq_input.valueChanged.connect(self.set_freq)
        layout_freq.addWidget(QLabel("Frequenz:"))
        layout_freq.addStretch()
        layout_freq.addWidget(self.freq_input)
        layout_config.addLayout(layout_freq)

        # thetha input
        layout_theta = QHBoxLayout()
        self.theta_i_input = QDoubleSpinBox()
        self.theta_i_input.setSuffix(" °")
        self.theta_i_input.setRange(0, 90)
        self.theta_i_input.setValue(0)
        self.theta_i_input.setSingleStep(1)
        self.theta_i_input.valueChanged.connect(self.set_theta_i)
        self.theta_i_input.valueChanged.connect(self.on_theta_change)
        layout_theta.addWidget(QLabel("Einfallswinkel Elevation (θi):"))
        layout_theta.addStretch()
        layout_theta.addWidget(self.theta_i_input)
        layout_config.addLayout(layout_theta)

        # phi input
        layout_phi = QHBoxLayout()
        self.phi_i_input = QDoubleSpinBox()
        self.phi_i_input.setSuffix(" °")
        self.phi_i_input.setRange(0, 360)
        self.phi_i_input.setValue(0)
        self.phi_i_input.setSingleStep(1)
        self.phi_i_input.valueChanged.connect(self.set_phi_i)
        self.phi_i_input.valueChanged.connect(self.on_phi_change)
        layout_phi.addWidget(QLabel("Einfallswinkel Azimut (φi):"))
        layout_phi.addStretch()
        layout_phi.addWidget(self.phi_i_input)
        layout_config.addLayout(layout_phi)

        # incident vector render checkbox 
        self.chk_incident = QCheckBox("Incident Vector anzeigen")
        self.chk_incident.setChecked(True)
        self.chk_incident.stateChanged.connect(self.on_incident_toggle)
        layout_config.addWidget(self.chk_incident)

        self.chk_hover = QCheckBox("Hover Info anzeigen")
        self.chk_hover.stateChanged.connect(self.on_hover_toggle)
        layout_config.addWidget(self.chk_hover)

        # plane select combobox
        layout_plane = QHBoxLayout()
        self.combo_plane = QComboBox()
        self.combo_plane.addItems(["xy", "yz", "zx"])
        self.combo_plane.currentTextChanged.connect(self.on_plane_changed)
        layout_plane.addWidget(QLabel("RIS-Ebene:"))
        layout_plane.addStretch()
        layout_plane.addWidget(self.combo_plane)
        layout_config.addLayout(layout_plane)

        layout_config.addStretch(1)

        # update plot button
        apply_btn = QPushButton("Anwenden")
        apply_btn.clicked.connect(self.plot_beampattern_surface)
        layout_config.addWidget(apply_btn)
        main_layout.addLayout(layout_config, stretch=1)


######### OpenGL Viewer
        self.view = gl.GLViewWidget()
        self.view.opts['distance'] = 2
        self.view.opts['elevation'] = 30
        self.view.opts['azimuth'] = 45
        self.view.orbit(0, 0)
        self.view.setBackgroundColor('white')
        main_layout.addWidget(self.view, stretch=3)

        self.add_grid_planes()
        self.gen_faces(self.sim.resolution)
        self.plot_beampattern_surface()


######### plotly Viewer
        self.webview = QWebEngineView()
        # main_layout.addWidget(self.webview, stretch=1)

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

###################################################################################################
#### setter functions for gui #####################################################################
# old %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def set_resolution(self, resolution):
        if self.sim.set_resolution(resolution): # True if value changed
            self.faces = self.gen_faces(self.sim.resolution)


    def set_freq(self, freq):
        if self.sim.set_freq(freq*1e9):         # True if value changed
            self.plot_beampattern_surface()


    def set_theta_i(self, theta_i):
        if self.sim.set_theta_in(np.deg2rad(theta_i)):      # True if value changed
            self.plot_beampattern_surface()


    def set_phi_i(self, phi_i):
        if self.sim.set_phi_in(np.deg2rad(phi_i)):          # True if value changed
            self.plot_beampattern_surface()


    def set_mask_bool(self, mask_bool):
        if self.sim.set_mask_bool(mask_bool):     # True if value changed
            self.plot_beampattern_surface()






###################################################################################################
#### setter functions for gui #####################################################################
# new %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    def on_plane_changed(self, plane):
        self.sim.ris_plane = plane
        self.update_plot()


    def on_incident_toggle(self, state):
        self.sim.show_incident_vector = bool(state)
        self.update_plot()


    def on_hover_toggle(self, state):
        self.show_hover = bool(state)
        self.update_plot()


    def on_freq_changed(self, value):
        if self.sim.freq != value*1e9:
            self.sim.set_freq(value*1e9)
            self.update_plot()


    def on_phi_change(self, value):
        if self.sim.phi != value:
            self.sim.set_phi_in(value)
            self.update_plot()


    def on_theta_change(self, value):
        if self.sim.theta != value:
            self.sim.set_theta_in(value)
            self.update_plot()


    def update_plot(self):
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
        AF_norm = self.sim.get_af()
        THETA = self.sim.theta
        PHI = self.sim.phi
        AF_db = 20 * np.log10(AF_norm + 1e-12)
        X, Y, Z = self.sim._get_coords(AF_norm, THETA, PHI, self.sim.ris_plane)

        # TODO: toggle für dB und normiert einfügen?
        # plot_db = True
        # AF_plot = AF_norm if plot_db == False else AF_db

        hovertemplate_surface = (
            "Arrayfaktor: %{surfacecolor:.1f} dB<extra></extra>"
            if self.show_hover else None
        )

        surface = go.Surface(
            x=X.tolist(),
            y=Y.tolist(),
            z=Z.tolist(),
            surfacecolor=AF_db.tolist(),
            colorscale="viridis",
            cmin=np.max([-40, np.nanmin(AF_db)]),
            cmax=np.min([0, np.nanmax(AF_db)]),
            opacity=0.85,
            showscale=True,
            hovertemplate=hovertemplate_surface,
            hoverinfo="all" if self.show_hover else "skip"
        )

        data = [surface]
        plane = self.sim.ris_plane

        # Incident-Vektor als Linie
        if self.sim.show_incident_vector:
            vec_len = 1.2
            th = self.sim.theta_i
            ph = self.sim.phi_i
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
            
            incident_theta_deg = np.degrees(self.sim.theta_i)
            incident_phi_deg = np.degrees(self.sim.phi_i)
            angle_str = f"Incident θ: {incident_theta_deg:.1f}°, φ: {incident_phi_deg:.1f}°"
            
            hovertemplate_vector = (
                "%{text}<extra></extra>" if self.show_hover else None
            )
            data.append(
                go.Scatter3d(
                    x=x_vec, y=y_vec, z=z_vec,
                    mode='lines+markers',
                    line=dict(color='red', width=8),
                    marker=dict(size=4, color='red'),
                    name='Incident Angle',
                    text=[angle_str, angle_str],
                    hovertemplate=hovertemplate_vector,
                    hoverinfo="all" if self.show_hover else "skip",
                    showlegend=False
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










#### adds incident vector to the graphic ##########################################################
    def add_incident_vector(self, theta_i, phi_i):
        try:
            self.view.removeItem(self.arrow)
        except:
            pass
        r = 1.1  # normierte Länge
        x = r * np.sin(-theta_i) * np.cos(phi_i)
        y = r * np.sin(-theta_i) * np.sin(phi_i)
        z = r * np.cos(-theta_i)

        vector = np.array([[0, 0, 0], [x, y, z]])
        self.arrow = gl.GLLinePlotItem(pos=vector, color=("blue"), width=3, antialias=True)
        self.view.addItem(self.arrow)


###################################################################################################
    def gen_faces(self, resolution):
        grid = np.arange(resolution * resolution).reshape((resolution, resolution))
        a = grid[:-1, :-1]
        b = grid[:-1, 1:]
        c = grid[1:, :-1]
        d = grid[1:, 1:]
        tri1 = np.stack([a.ravel(), b.ravel(), c.ravel()], axis=1)
        tri2 = np.stack([b.ravel(), d.ravel(), c.ravel()], axis=1)
        self.faces = np.vstack([tri1, tri2])
        return self.faces


    def gen_vertices(self, AF):
        AF /= np.max(AF)    # norm to 1
        X = AF * self.sim.sinT_cosP
        Y = AF * self.sim.sinT_sinP
        Z = AF * self.sim.cosP
        vertices = np.column_stack((X.ravel(), Y.ravel(), Z.ravel()))
        return vertices


    def gen_colors_face(self, AF):
        af_r = AF.ravel()
        af_for_faces = (af_r[self.faces[:, 0]] + af_r[self.faces[:, 1]] + af_r[self.faces[:, 2]]) / 3

        lut = pg.colormap.get('viridis').getLookupTable(0.0, 1.0, 256).astype(np.uint8)
        color_idx = np.clip((af_for_faces * 255).astype(int), 0, 255)
        color_rgba = lut[color_idx] / 255.0     # shape (n_faces, 3) or (n_faces, 4)

        # Alpha ergänzen um error zu vermeiden
        if color_rgba.shape[1] == 3:
            alpha = np.ones((color_rgba.shape[0], 1))
            faces_colors = np.hstack((color_rgba, alpha))
        return faces_colors


###################################################################################################
    def plot_beampattern_surface(self):
        # TODO: nur beamplot und eventuell vector löschen
        try:
            self.view.removeItem(self.mesh)
        except:
            pass
        # self.add_grid_planes()
        self.add_incident_vector(self.sim.theta_i, self.sim.phi_i)

        AF = self.sim.get_af()
        vertices = self.gen_vertices(AF)
        faces_colors = self.gen_colors_face(AF)

        self.mesh = gl.GLMeshItem(
            vertexes=vertices,
            faces=self.faces,
            faceColors=faces_colors.astype(np.float32),
            smooth=False,
            drawEdges=False
        )
        self.view.addItem(self.mesh)


#### adds mesh like planes to the plot ############################################################
    def add_grid_planes(self):
        size = 1.1
        def create_grid(rotation_axis, angle_deg, translate_vec):
            grid = gl.GLGridItem()
            grid.setSize(size,size)
            grid.setSpacing(0.1, 0.1)
            grid.setColor("grey")  # dunkelgrau
            grid.rotate(angle_deg, *rotation_axis)
            grid.translate(*translate_vec)
            self.view.addItem(grid)

        create_grid((1, 0, 0), 0, (0, 0, 0))
        create_grid((1, 0, 0), 90, (0, -size/2, size/2))
        create_grid((0, 1, 0), 90, (-size/2, 0, size/2))

        # set camera center
        self.view.opts['center'] = pg.Vector(0, 0, size/2)
        self.view.update()



if __name__ == "__main__":
    app = QApplication([])
    win = RISsimulator_ui()
    win.resize(1200, 800)
    win.show()
    app.exec()