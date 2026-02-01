import os
import sys
import logging
import requests
import zipfile
import io

# ---------------- Logging setup ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# ---------------- Configuration ----------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    logging.error("GITHUB_TOKEN is not set")
    sys.exit(1)

OWNER = "satheesh-kamadani"

# Repo -> artifact name mapping
ECU_REPOS = {
    "cpp-ci-demo": "ecu-calculator-artifact",
    "ecu-brake": "ecu-brake-artifact"
}

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

BASE_DIR = "artifacts"
os.makedirs(BASE_DIR, exist_ok=True)

# ---------------- Helper functions ----------------
def get_latest_successful_run(repo):
    url = f"https://api.github.com/repos/{OWNER}/{repo}/actions/runs"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    runs = response.json().get("workflow_runs", [])
    for run in runs:
        if run["conclusion"] == "success":
            return run["id"]

    raise RuntimeError(f"No successful workflow runs found for repo '{repo}'")


def fetch_artifact(repo, artifact_name):
    logging.info(f"Fetching artifact '{artifact_name}' from repo '{repo}'")

    run_id = get_latest_successful_run(repo)

    artifacts_url = (
        f"https://api.github.com/repos/{OWNER}/{repo}/actions/runs/{run_id}/artifacts"
    )
    response = requests.get(artifacts_url, headers=HEADERS)
    response.raise_for_status()

    artifacts = response.json().get("artifacts", [])
    artifact = next(
        (a for a in artifacts if a["name"] == artifact_name),
        None
    )

    if not artifact:
        raise RuntimeError(
            f"Artifact '{artifact_name}' not found in repo '{repo}'"
        )

    zip_response = requests.get(
        artifact["archive_download_url"], headers=HEADERS
    )
    zip_response.raise_for_status()

    repo_dir = os.path.join(BASE_DIR, repo)
    os.makedirs(repo_dir, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(zip_response.content)) as zip_file:
        zip_file.extractall(repo_dir)

    logging.info(f"Artifact extracted to '{repo_dir}'")


# ---------------- Main workflow ----------------
def main():
    logging.info("Starting ECU manifest fetch")

    try:
        for repo, artifact_name in ECU_REPOS.items():
            fetch_artifact(repo, artifact_name)

    except Exception as exc:
        logging.error(f"Failed to fetch ECU manifests: {exc}")
        sys.exit(1)

    logging.info("All ECU manifests fetched successfully")


if __name__ == "__main__":
    main()
