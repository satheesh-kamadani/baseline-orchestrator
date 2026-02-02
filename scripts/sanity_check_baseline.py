# Running sanity checks on baseline manifest

import sys
import yaml
import logging

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

BASELINE_FILE = "baseline/baseline-manifest.yaml"


def load_baseline():
    try:
        with open(BASELINE_FILE) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise RuntimeError("Baseline manifest not found")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Invalid YAML format: {e}")


def sanity_checks(baseline):
    logging.info("Running baseline sanity checks")

    # 1️⃣ Check baseline_id
    if "baseline_id" not in baseline:
        raise RuntimeError("Missing 'baseline_id'")

    # 2️⃣ Check ECUs
    ecus = baseline.get("ecus")
    if not ecus or not isinstance(ecus, list):
        raise RuntimeError("No ECUs found in baseline")

    seen_ecus = set()

    for ecu in ecus:
        ecu_name = ecu.get("ecu_name")
        if not ecu_name:
            raise RuntimeError("ECU missing 'ecu_name'")

        if ecu_name in seen_ecus:
            raise RuntimeError(f"Duplicate ECU found: {ecu_name}")

        seen_ecus.add(ecu_name)

        if "artifact_path" not in ecu:
            raise RuntimeError(f"ECU '{ecu_name}' missing 'artifact_path'")

        if "commit" not in ecu:
            raise RuntimeError(f"ECU '{ecu_name}' missing 'commit'")

        logging.info(f"ECU '{ecu_name}' passed sanity checks")

    logging.info("All sanity checks passed")


def main():
    try:
        baseline = load_baseline()
        sanity_checks(baseline)
    except Exception as exc:
        logging.error(f"Sanity checks failed: {exc}")
        sys.exit(1)

    logging.info("Baseline is sane and qualified")


if __name__ == "__main__":
    main()