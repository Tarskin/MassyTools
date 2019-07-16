from sklearn.cluster import DBSCAN
from pathlib import PurePath


def classify_mass_spectra(mass_spectra):
    """
    Classifcation controller function.

    :param mass_spectra:
    :return None
    """
    data = normalize_intensity(mass_spectra)

    clustering = density_based_spatial_clustering(data)

    rename_mass_spectra(mass_spectra, clustering)


def density_based_spatial_clustering(data):
    clustering = DBSCAN(eps=3, min_samples=2).fit(data)
    return clustering


def normalize_intensity(mass_spectra):
    data = []

    for index, mass_spectrum in enumerate(mass_spectra):
        _, _y = zip(*mass_spectrum.data)
        max_y = max(_y)
        norm_y = [x / max_y for x in _y]
        data.append(norm_y)

    return data


def rename_mass_spectra(mass_spectra, clustering):
    for index, mass_spectrum in enumerate(mass_spectra):
        mass_spectrum.filename = (
            PurePath(mass_spectrum.filename).parent / PurePath(
            '[' + str(clustering.labels_[index])+ '] '+
            str(PurePath(mass_spectrum.filename).name))
        )
