import io
import json
import zipfile
from vampire_lab.config import initial_parameters
from vampire_lab.exports import export_zip
from vampire_lab.simulation import simulate_population


def test_complete_zip():
    p = initial_parameters()
    data = simulate_population(p, 100, .5, 9)
    b = export_zip(data, p, 100, .5, 9, {}, "bonjour", b"%PDF-1.4\n")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        names = z.namelist()
        assert "Data_vampi.csv" in names
        assert "parametres_simulation.json" in names
        assert "carnet.md" in names
        assert "consignes_personnelles.pdf" in names
        assert json.loads(z.read("parametres_simulation.json"))["graine"] == 9
