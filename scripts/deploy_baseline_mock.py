# Deploying baseline software to system test rig(Mock).

import sys
import yaml
import logging
from datetime import datetime

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

BASELINE_FILE = "baseline/baseline-manifest.yaml"
DEPLOYMENT_REPORT = "deployment/deployment-report.yaml"


def load_baseline():
    try:
        with open(BASELINE_FILE) as f:
            return yaml.safe_load(f)
    except Exception as exc:
        raise RuntimeError(f"Failed to load baseline manifest: {exc}")


def simulate_deployment(baseline):
    logging.info("Starting mock deployment to system test rig")

    rig_id = "SYSTEM-RIG-01"
    deployed_ecus = []

    for ecu in baseline.get("ecus", []):
        ecu_name = ecu["ecu_name"]
        logging.info(f"Deploying ECU '{ecu_name}' to {rig_id}")
        deployed_ecus.append(ecu_name)

    report = {
        "baseline_id": baseline["baseline_id"],
        "rig_id": rig_id,
        "status": "DEPLOYED",
        "deployed_at": datetime.utcnow().isoformat() + "Z",
        "ecus": deployed_ecus
    }

    return report


def write_deployment_report(report):
    with open(DEPLOYMENT_REPORT, "w") as f:
        yaml.dump(report, f, sort_keys=False)

    logging.info(f"Deployment report written to {DEPLOYMENT_REPORT}")


def main():
    try:
        baseline = load_baseline()
        report = simulate_deployment(baseline)
        write_deployment_report(report)
    except Exception as exc:
        logging.error(f"Deployment failed: {exc}")
        sys.exit(1)

    logging.info("Mock deployment completed successfully")


if __name__ == "__main__":
    main()
