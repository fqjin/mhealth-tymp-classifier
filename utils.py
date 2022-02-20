import torch
import numpy as np
from scipy.signal import butter, sosfiltfilt


def build_model():
    """Gets the trained PyTorch TorchScript model"""
    model = torch.jit.load('model.pt')
    return model


def preprocess(pressure, compliance):
    """Pre-processes tympanogram data"""
    if np.any(np.diff(pressure) <= 0):
        raise ValueError('Pressure sweep is not monotonic')

    default_p = np.arange(-399, 201, dtype=float)
    lpf = butter(4, 0.04, 'lowpass', output='sos')
    
    trace = np.interp(default_p, pressure, compliance)
    trace = np.stack([trace, sosfiltfilt(lpf, trace)])
    trace = torch.from_numpy(trace).float()[None]
    return trace


def sim_tracing(tpp=0, ecv=1.0, sa=1.0, zeta=2e-3, slope=5e-4):
    """An analytic formula for generating simulated tympanograms"""
    p = np.linspace(-399, 200, 600)
    atm = 1e5 / 10  # 1 atm in decaPascals
    a = 1 / (1 + (tpp - p)**2 / (zeta**2 * (2*atm + tpp + p)**2))
    a200 = a[-1]
    amax = sa / (1 - a200)
    a *= amax
    a += ecv - amax * a200
    a += slope * (p - tpp) * (p < tpp)
    return p, a

