import numpy as np
from datetime import datetime

import matplotlib.pyplot as plt

import numexpr as ne

c = 3e8

###################################################################################################
class RISsimulator():
    def __init__(self):
        # RIS-pysical Parameter
        self.M, self.N = 16, 16     # amount of elements
        self.dy = 0.013             # vertical distance between centers of elements in mm 
        self.dx = 0.02001           # horizontal distance between centers of elements in mm 

        self.read_phase_file("AngS11.txt")

        m = np.arange(self.M).reshape((-1, 1, 1, 1))  # M x 1 x 1 x 1
        n = np.arange(self.N).reshape((1, -1, 1, 1))  # 1 x N x 1 x 1
        self.delta_y = m * self.dy
        self.delta_x = n * self.dx

        self.element_mask = np.ones((self.M, self.N), dtype=bool)  # oder dtype=np.float32

        self.resolution = -1
        self.set_resolution(200)    # set resolution of calculation (default: 200)

        self.freq = 5e9
        self.theta_i = 0.1
        self.phi_i = 0.1


        self.k = 2 * np.pi * self.freq / c
        self.sin_theta_i = np.sin(self.theta_i)
        self.cos_phi_i = np.cos(self.phi_i)
        self.sin_phi_i = np.sin(self.phi_i)
        self.psi = self.k * (
            self.delta_x * (self._sin_theta * self._cos_phi - self.sin_theta_i * self.cos_phi_i) +
            self.delta_y * (self._sin_theta * self._sin_phi - self.sin_theta_i * self.sin_phi_i)
        )

        self.get_phase_shift(self.freq)
        self.set_mask_off()
        self.set_freq(5.15e9)       # set frequency (default 5.15GHz)
        self.set_theta_in(0)
        self.set_phi_in(0)


###################################################################################################
    def set_resolution(self, resolution):
        if self.resolution == resolution:
            return
        self.resolution = resolution

        # calculate new spherecal coordinates for AF calculation
        self.theta, self.phi = np.meshgrid(np.linspace(0, np.pi/2, self.resolution), np.linspace(0, 2*np.pi, self.resolution))
        self._sin_theta = np.sin(self.theta)[np.newaxis, np.newaxis, :, :]
        self._cos_theta = np.cos(self.theta)[np.newaxis, np.newaxis, :, :]
        self._cos_phi   = np.cos(self.phi)[np.newaxis, np.newaxis, :, :]
        self._sin_phi   = np.sin(self.phi)[np.newaxis, np.newaxis, :, :]

        self.sinT_cosP  = np.sin(self.theta) * np.cos(self.phi)
        self.sinT_sinP  = np.sin(self.theta) * np.sin(self.phi)
        self.cosP       = np.cos(self.theta)


#### set frequency and update depending ###########################################################
    def set_freq(self, freq):
        if self.freq == freq:
            return False
        self.freq = freq
        self.k = 2 * np.pi * self.freq / c
        self.get_phase_shift(self.freq)
        self.calc_psi()
        self.mask_calc_phase()
        self.array_factor_matrix()
        return True


#### calculates the incident angles and needed values for later calculation #######################
    def set_theta_in(self, theta_i):
        if self.theta_i == theta_i:
            return False
        self.theta_i = theta_i
        self.sin_theta_i = np.sin(theta_i)
        self.calc_psi()
        self.array_factor_matrix()
        return True


    def set_phi_in(self, phi_i):
        if self.phi_i == phi_i:
            return False
        self.phi_i = phi_i
        self.cos_phi_i = np.cos(phi_i)
        self.sin_phi_i = np.sin(phi_i)
        self.calc_psi()
        self.array_factor_matrix()
        return True


#### mask functions ###############################################################################
    def set_mask_bool(self, mask_bool):
        if (self.mask_bool == np.array(mask_bool)).all():
            return False
        self.mask_bool = mask_bool
        self.mask_print_bool(self.mask_bool)
        self.mask_calc_phase()
        self.array_factor_matrix()
        return True

    def set_mask_rand(self):
        self.mask_bool = np.random.randint(0, 2, size=(self.M, self.N))
        self.mask_print_bool(self.mask_bool)
        self.mask_calc_phase()
        self.array_factor_matrix()
        return True

    def set_mask_on(self):
        self.mask_bool = np.ones(shape=(self.M, self.N))
        self.mask_print_bool(self.mask_bool)
        self.mask_calc_phase()
        self.array_factor_matrix()
        return True

    def set_mask_off(self):
        self.mask_bool = np.zeros(shape=(self.M, self.N))
        self.mask_print_bool(self.mask_bool)
        self.mask_calc_phase()
        self.array_factor_matrix()
        return True

    def read_phase_file(self, fname):
        content = np.loadtxt(fname, delimiter="\t", skiprows=1)
        content[:,0] *= 1e9
        self.phase_shift = content


    def get_phase_shift(self, freq):
        self.phase_off = np.interp(freq, self.phase_shift[:,0], self.phase_shift[:,1])
        self.phase_on = np.interp(freq, self.phase_shift[:,0], self.phase_shift[:,2])
        return self.phase_off, self.phase_on


###################################################################################################
    def mask_print_bool(self, pattern):
        """
        Gibt das aktuelle Aktivitätsmuster des RIS (self.element_mask) als Textgrafik aus.
        ░░░░ = inaktiv, ████ = aktiv
        """
        if not hasattr(self, "element_mask"):
            print("Elementmaske ist nicht gesetzt.")
            return

        # for row in self.element_mask:
        for row in pattern:
            line = ""
            for active in row:
                line += "████ " if active else "░░░░ "
            print(line)


###################################################################################################
    def calc_psi(self):
        self.psi = self.k * (
            self.delta_x * (self._sin_theta * self._cos_phi - self.sin_theta_i * self.cos_phi_i) +
            self.delta_y * (self._sin_theta * self._sin_phi - self.sin_theta_i * self.sin_phi_i)
        )


    def mask_calc_phase(self):
        temp = np.copy(self.mask_bool)
        temp[temp==0] = self.phase_off
        temp[temp==1] = self.phase_on
        self.mask_phase = np.deg2rad(temp).astype(np.float32)[:, :, np.newaxis, np.newaxis]


###################################################################################################
    def array_factor_matrix(self):

        start = datetime.now()

        phase = self.psi + self.mask_phase
        re = ne.evaluate("cos(phase)")
        im = ne.evaluate("sin(phase)")
        af = np.ascontiguousarray(re + 1j * im).astype(np.complex64)
        self.AF = np.abs(np.einsum('ijkl->kl', af))
        print("AF calculation time: {:.3f}ms".format((datetime.now()-start).total_seconds()*1000))

        return self.AF


###################################################################################################
    def get_af(self):
        plt.figure(figsize=(8, 6))
        plt.imshow(10 * np.log10(self.AF), extent=[-90, 90, -90, 90], origin='lower', cmap='viridis')
        plt.title('Normalized Power Beampattern (16x16 RIS mit ON/OFF-Matrix)')
        plt.xlabel('Azimuth φ (deg)')
        plt.ylabel('Elevation θ (deg)')
        plt.colorbar(label='Power (dB)')
        plt.tight_layout()
        plt.show()
        return self.AF


if __name__ == "__main__":
    test = RISsimulator()
    test.set_mask_rand()
    test.mask_calc_phase()
    print(f"freq={test.freq:.3f}, phase_on={test.phase_on:.3f}, phase_off={test.phase_off:.3f}")
