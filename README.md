# MassyTools
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/91d94d971ca14c2b9bc831b83d3e0a96)](https://www.codacy.com/gh/Tarskin/MassyTools/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Tarskin/MassyTools&amp;utm_campaign=Badge_Grade)

A data processing tool for targeted high-throughput MALDI-MS data extraction.

The tool has been described in https://pubs.acs.org/doi/abs/10.1021/acs.jproteome.5b00658

## Internal API prototype

The refactored library layer starts at `MassyTools.Experiment` and follows:

`Experiment -> Spectrum -> Analyte -> Isotope`

Analytes can be created from existing MassyTools block notation, or from direct
CHNOS elemental composition:

```python
from MassyTools import Experiment

experiment = Experiment("demo")
spectrum = experiment.add_spectrum(name="sample")
analyte = spectrum.add_analyte(
    "glucose",
    charge=1,
    composition={"C": 6, "H": 12, "N": 0, "O": 6, "S": 0},
)
analyte.calculate_isotopes()
```

A minimal Flask app factory is available in `MassyTools.api:create_app`.
