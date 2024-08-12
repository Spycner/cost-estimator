"""
OSF client for downloading data.
"""

import os
import shutil
import zipfile

import tqdm
from osfclient import OSF

from cost_estimator import _DATA_DIR, _DOWNLOAD_DIR, _RUNS_DIR, main_logger

DATASETS = ["airline", "imdb", "ssb", "tpc_h"]
RUNS = ["deepdb_augmented", "parsed_plans", "raw"]

os.makedirs(_DOWNLOAD_DIR, exist_ok=True)
os.makedirs(_DATA_DIR, exist_ok=True)
os.makedirs(_RUNS_DIR, exist_ok=True)


def check_downloaded_files() -> bool:
    """
    Check if all required files have already been downloaded.

    This function checks for the presence of all datasets in the _DATA_DIR
    and all runs in the _RUNS_DIR. It returns True if all required files
    are present, and False otherwise.

    Returns:
        bool: True if all required files are present, False otherwise.
    """
    all_files_present = True

    for dataset in DATASETS:
        if not os.path.exists(os.path.join(_DATA_DIR, dataset)):
            main_logger.info(f"Missing dataset: {dataset}")
            all_files_present = False

    for run in RUNS:
        if not os.path.exists(os.path.join(_RUNS_DIR, run)):
            main_logger.info(f"Missing run: {run}")
            all_files_present = False

    return all_files_present


def download_project(osf_id: str = "ga2xj"):
    """
    Download a project from OSF and move the files to the correct directories.

    This function checks if all required files are already downloaded. If they are,
    it logs a message and returns. Otherwise, it downloads the project from OSF,
    saves the files to a temporary directory, and then moves them to the correct
    locations.

    Args:
        osf_id (str): OSF ID of the project to download. Defaults to "ga2xj".

    Raises:
        OSError: If there are issues with file operations or network connectivity.
    """
    if check_downloaded_files():
        main_logger.info("All required files have already been downloaded.")
        return

    main_logger.info(f"Downloading project with OSF ID: {osf_id}")
    osf_client = OSF()
    project = osf_client.project(osf_id)

    for storage in tqdm.tqdm(project.storages, desc="Processing storages"):
        for file in tqdm.tqdm(storage.files, desc="Downloading files", leave=False):
            file_path = os.path.join(_DOWNLOAD_DIR, file.name)
            with open(file_path, "wb") as f:
                file.write_to(f)
            main_logger.debug(f"Downloaded: {file.name}")

    move_downloads()
    main_logger.info("Project download and file movement completed.")


def move_downloads():
    """
    Unzip and move the downloaded files to the correct directories.

    This function iterates through the DATASETS and RUNS lists, unzipping the
    corresponding files from the temporary download directory and moving them
    to their final locations in _DATA_DIR and _RUNS_DIR respectively.
    """
    main_logger.info("Unzipping and moving downloaded files to their final locations")

    for dataset in DATASETS:
        src_zip = os.path.join(_DOWNLOAD_DIR, f"{dataset}.zip")
        if os.path.exists(src_zip):
            with zipfile.ZipFile(src_zip, "r") as zip_ref:
                zip_ref.extractall(_DATA_DIR)
            os.remove(src_zip)
            main_logger.debug(f"Unzipped and moved dataset: {dataset}")

    for run in RUNS:
        src_zip = os.path.join(_DOWNLOAD_DIR, f"{run}.zip")
        if os.path.exists(src_zip):
            with zipfile.ZipFile(src_zip, "r") as zip_ref:
                zip_ref.extractall(_RUNS_DIR)
            os.remove(src_zip)
            main_logger.debug(f"Unzipped and moved run: {run}")

    main_logger.info("File unzipping and movement completed")


def clean_up():
    """
    Clean up the temporary download directory.
    """
    main_logger.info("Cleaning up temporary download directory")
    shutil.rmtree(_DOWNLOAD_DIR)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--osf_id", type=str, default="ga2xj")
    parser.add_argument(
        "--clean_up", action="store_true", help="Run clean up operation"
    )
    args = parser.parse_args()

    if args.clean_up:
        clean_up()
    else:
        download_project(args.osf_id)
