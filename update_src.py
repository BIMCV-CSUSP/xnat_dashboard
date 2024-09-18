import argparse
import io
import sys
from pathlib import Path

import pandas as pd
import requests

root_dir = Path(__file__).parent


def send_request(url: str, auth: tuple[str]) -> requests.Response:
    try:
        response = requests.get(url, auth=auth)
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        sys.exit(1)
    return response


def main():
    parser = argparse.ArgumentParser(
        description="Send HTTP POST request with username and password."
    )
    parser.add_argument("username", help="The username for authentication")
    parser.add_argument("password", help="The password for authentication")

    args = parser.parse_args()

    base_url = "https://ceib.cipf.es/xnat2/data/projects?format=csv"
    project_url = lambda project_id: base_url.replace(
        "?format=csv",
        f"/{project_id}/experiments?columns=date,modality,subject_ID&format=csv",
    )
    auth = (args.username, args.password)

    response = send_request(base_url, auth)
    response.encoding = "utf-8"
    if response.status_code == 200:
        projects_df = pd.read_csv(io.StringIO(response.text))
    else:
        raise Exception("Failed to retrieve projects information")

    session_counts, subject_counts = [], []
    for project_id in projects_df["ID"]:
        response = send_request(project_url(project_id), auth)
        response.encoding = "utf-8"
        if response.status_code == 200:
            project_df = pd.read_csv(io.StringIO(response.text))
            project_df.to_csv(root_dir / "src" / "projects" / f"{project_id}.csv")
        else:
            raise Exception(f"Failed to retrieve project {project_id} information")
        session_counts.append(len(project_df))
        subject_count = project_df["subject_ID"].unique().size
        subject_counts.append(subject_count)

    projects_df["session_count"] = session_counts
    projects_df["subject_count"] = subject_counts
    projects_df.to_csv(root_dir / "src" / "projects.csv")


if __name__ == "__main__":
    main()
