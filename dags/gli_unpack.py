import os
from zipfile import ZipFile
import shutil
import gli_config as cfg
import logging


def unpack_archive():
    branch = "finish"
    if os.path.exists(cfg.transfer_folder):
        logging.info("Found transfer folder")
        if not os.path.exists(cfg.scratch_folder):
            os.mkdir(cfg.scratch_folder)
        if not os.path.exists(cfg.coldp_file):
            for f in sorted(os.listdir(cfg.transfer_folder)):
                if f.endswith(".zip"):
                    logging.info(f"Processing {f}")
                    zip_path = os.path.join(cfg.transfer_folder, f)
                    os.rename(zip_path, cfg.coldp_file)
                    break
        if os.path.exists(cfg.coldp_file):
            with ZipFile(cfg.coldp_file, "r") as zip:
                zip.extractall(cfg.coldp_path)
                for f2 in os.listdir(cfg.coldp_path):
                    if f2.lower().startswith("references."):
                        shutil.move(
                            os.path.join(cfg.coldp_path, f2),
                            os.path.join(cfg.coldp_path, f2[0:9] + f2[10:]),
                        )
            # os.remove(cfg.coldp_file)
            branch = "summarise"

    return branch
