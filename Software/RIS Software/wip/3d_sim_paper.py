import numpy as np
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QDoubleSpinBox, QGroupBox, QPushButton
)
import pyqtgraph as pg
import pyqtgraph.opengl as gl

import matplotlib.pyplot as plt

# try:
#     from rissimulator import RISsimulator
# except:
#     from lib.rissimulator import RISsimulator


class RISsimulator_ui(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.sim = RISsimulator()

        # init main widget
        self.setWindowTitle("RIS Beampattern - 3D Mesh mit Ebenenraster")
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # OpenGL Viewer
        self.view = gl.GLViewWidget()
        self.view.opts['distance'] = 2
        self.view.opts['elevation'] = 30
        self.view.opts['azimuth'] = 45
        self.view.orbit(0, 0)
        self.view.setBackgroundColor('white')
        main_layout.addWidget(self.view, stretch=3)

        # Steuerpanel
        config = self.create_config_panel()
        main_layout.addWidget(config, stretch=1)

        self.theta = np.linspace(-np.pi/2, np.pi/2, 181)
        self.phi = np.linspace(-np.pi/2, np.pi/2, 181)
        # self.theta = np.linspace(0, 2*np.pi, 181)
        # self.phi = np.linspace(0, np.pi, 181)
        
        self.resolution = 181
        
        # self.theta = np.linspace(0, np.pi/2, self.resolution)
        # self.phi = np.linspace(0, 2*np.pi, self.resolution)
        
        # self.theta, self.phi = np.meshgrid(np.linspace(0, np.pi/2, self.resolution), np.linspace(0, 2*np.pi, self.resolution))
        
        self.add_grid_planes()

        # self.gen_faces(self.sim.resolution)
        self.gen_faces(181)

        self.plot_beampattern_surface()


#### creating configuration panel with buttons ####################################################
    def create_config_panel(self):
        box = QGroupBox("Konfiguration")
        layout = QVBoxLayout(box)

        self.freq_input = QDoubleSpinBox()
        self.freq_input.setSuffix(" GHz")
        self.freq_input.setRange(5.0, 6.0)
        self.freq_input.setValue(5.15)
        self.freq_input.setSingleStep(0.1)
        self.freq_input.valueChanged.connect(self.set_freq)

        self.theta_i_input = QDoubleSpinBox()
        self.theta_i_input.setSuffix(" °")
        self.theta_i_input.setRange(0, 90)
        self.theta_i_input.setValue(0)
        self.theta_i_input.setSingleStep(1)
        self.theta_i_input.valueChanged.connect(self.set_theta_i)

        self.phi_i_input = QDoubleSpinBox()
        self.phi_i_input.setSuffix(" °")
        self.phi_i_input.setRange(0, 360)
        self.phi_i_input.setValue(0)
        self.phi_i_input.setSingleStep(1)
        self.phi_i_input.valueChanged.connect(self.set_phi_i)

        apply_btn = QPushButton("Anwenden")
        apply_btn.clicked.connect(self.plot_beampattern_surface)

        layout.addWidget(QLabel("Frequenz:"))
        layout.addWidget(self.freq_input)
        layout.addWidget(QLabel("Einfallswinkel Elevation (θi):"))
        layout.addWidget(self.theta_i_input)
        layout.addWidget(QLabel("Einfallswinkel Azimut (φi):"))
        layout.addWidget(self.phi_i_input)
        layout.addStretch()
        layout.addWidget(apply_btn)

        return box


###################################################################################################
#### setter functions for gui #####################################################################

    def set_resolution(self, resolution):
        # if self.sim.set_resolution(resolution): # True if value changed
            # self.faces = self.gen_faces(self.sim.resolution)
        self.faces = self.gen_faces(181)


    def set_freq(self, freq):
        # if self.sim.set_freq(freq*1e9):         # True if value changed
        #     self.plot_beampattern_surface()
        pass

    def set_theta_i(self, theta_i):
        # if self.sim.set_theta_in(np.deg2rad(theta_i)):      # True if value changed
        #     self.plot_beampattern_surface()
        pass

    def set_phi_i(self, phi_i):
        # if self.sim.set_phi_in(np.deg2rad(phi_i)):          # True if value changed
        #     self.plot_beampattern_surface()
        pass

    def set_mask_bool(self, mask_bool):
        # if self.sim.set_mask_bool(mask_bool):     # True if value changed
        #     self.plot_beampattern_surface()
        pass

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
        # self.theta, self.phi = np.meshgrid(np.linspace(0, np.pi/2, 181), np.linspace(0, 2*np.pi, 181))
        # X = AF * self.sim.sinT_cosP
        # Y = AF * self.sim.sinT_sinP
        # Z = AF * self.sim.cosP
        
        X = AF * np.sin(self.theta) * np.cos(self.phi)
        Y = AF * np.sin(self.theta) * np.sin(self.phi)
        Z = AF * np.cos(self.theta)
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
        # self.add_incident_vector(self.sim.theta_i, self.sim.phi_i)
        self.add_incident_vector(0, 0)

        AF = self.paper()
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







    def paper(self):
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
        mask = np.zeros(shape=(Ny, Nx))

        print(mask)

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
        THETA, PHI = np.meshgrid(self.theta, self.phi)

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
        plt.show(False)
        
        return  NPB
















if __name__ == "__main__":
    app = QApplication([])
    win = RISsimulator_ui()
    win.resize(1200, 800)
    win.show()
    app.exec()