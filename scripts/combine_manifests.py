# Combining ecu manifest and creating the baseline manifest

import os
import sys
import yaml
import logging
from datetime import datetime

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

ARTIFACTS_DIR = "artifacts"
BASELINE_DIR = "baseline"
BASELINE_FILE = os.path.join(BASELINE_DIR, "baseline-manifest.yaml")

os.makedirs(BASELINE_DIR, exist_ok=True)


def load_ecu_manifests():
    ecus = []

    if not os.path.isdir(ARTIFACTS_DIR):
        raise RuntimeError("Artifacts directory not found")

    for repo in os.listdir(ARTIFACTS_DIR):
        manifest_path = os.path.join(
            ARTIFACTS_DIR, repo, "ecu-manifest.yaml"
        )

        if not os.path.isfile(manifest_path):
            raise RuntimeError(
                f"ecu-manifest.yaml not found for repo '{repo}'"
            )

        with open(manifest_path) as f:
            ecu_manifest = yaml.safe_load(f)

        ecus.append(ecu_manifest)
        logging.info(f"Loaded ECU manifest from {repo}")

    if not ecus:
        raise RuntimeError("No ECU manifests found")

    return ecus


def create_baseline_manifest(ecus):
    return {
        "baseline_id": f"baseline-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        "state": "ASSEMBLED",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "ecus": ecus
    }


def write_baseline_manifest(baseline):
    with open(BASELINE_FILE, "w") as f:
        yaml.dump(baseline, f, sort_keys=False)

    logging.info(f"Baseline manifest written to {BASELINE_FILE}")


def main():
    logging.info("Starting baseline manifest generation")

    try:
        ecus = load_ecu_manifests()
        baseline = create_baseline_manifest(ecus)
        write_baseline_manifest(baseline)
    except Exception as exc:
        logging.error(f"Baseline generation failed: {exc}")
        sys.exit(1)

    logging.info("Baseline manifest generated successfully")


if __name__ == "__main__":
    main()
