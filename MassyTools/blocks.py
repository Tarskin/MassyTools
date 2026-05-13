from pathlib import Path


def _coerce_value(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def load_building_blocks(block_folder=None):
    """Load MassyTools .block files into a name-indexed dictionary."""
    if block_folder is None:
        block_folder = Path(__file__).resolve().parent.parent / "blocks"
    block_folder = Path(block_folder)

    building_blocks = {}
    for file in block_folder.glob("*.block"):
        keys = []
        values = []
        with file.open() as fr:
            for line in fr:
                parts = line.rstrip().split()
                if not parts:
                    continue
                keys.append(parts[0])
                values.append(_coerce_value(" ".join(parts[1:])))
        building_blocks[file.stem] = dict(zip(keys, values))
    return building_blocks
