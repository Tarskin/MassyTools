from bin.mass_spectrum import MassSpectrum

A = MassSpectrum()


def test_spectrum_init():
    assert isinstance(A, MassSpectrum)
