from flask import Flask, jsonify, request

from MassyTools.core import Experiment


def create_app():
    app = Flask(__name__)
    experiments = {}

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/experiments")
    def create_experiment():
        payload = request.get_json(force=True) or {}
        name = payload.get("name", f"experiment-{len(experiments) + 1}")
        experiment = Experiment(name=name)
        experiments[name] = experiment
        return jsonify(experiment.to_dict()), 201

    @app.get("/experiments")
    def list_experiments():
        return jsonify([experiment.to_dict() for experiment in experiments.values()])

    @app.get("/experiments/<name>")
    def get_experiment(name):
        experiment = experiments.get(name)
        if experiment is None:
            return jsonify({"error": "Experiment not found"}), 404
        return jsonify(experiment.to_dict())

    @app.post("/experiments/<name>/spectra")
    def add_spectrum(name):
        experiment = experiments.get(name)
        if experiment is None:
            return jsonify({"error": "Experiment not found"}), 404
        payload = request.get_json(force=True) or {}
        spectrum = experiment.add_spectrum(
            name=payload.get("name"),
            filename=payload.get("filename"),
            data=payload.get("data"),
        )
        return jsonify(spectrum.to_dict()), 201

    @app.post("/experiments/<name>/spectra/<int:spectrum_index>/analytes")
    def add_analyte(name, spectrum_index):
        experiment = experiments.get(name)
        if experiment is None:
            return jsonify({"error": "Experiment not found"}), 404
        try:
            spectrum = experiment.spectra[spectrum_index]
        except IndexError:
            return jsonify({"error": "Spectrum not found"}), 404

        payload = request.get_json(force=True) or {}
        analyte = spectrum.add_analyte(
            name=payload["name"],
            charge=payload.get("charge", 1),
            composition=payload.get("composition"),
        )
        analyte.calculate_isotopes()
        return jsonify(analyte.to_dict()), 201

    @app.post("/experiments/<name>/process")
    def process_experiment(name):
        experiment = experiments.get(name)
        if experiment is None:
            return jsonify({"error": "Experiment not found"}), 404
        experiment.process()
        return jsonify(experiment.to_dict())

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
