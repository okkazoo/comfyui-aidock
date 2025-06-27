import os
import subprocess
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
VAST_SCRIPT_PATH = os.path.join(ROOT_DIR, "vastai", "vast.py")
load_dotenv(os.path.join(ROOT_DIR, ".env"))

def build_env_block():
    return (
        "-p 1111:1111 -p 8080:8080 -p 8384:8384 -p 72299:72299 -p 8188:8188 "
        "-e OPEN_BUTTON_PORT=1111 "
        "-e OPEN_BUTTON_TOKEN=1 "
        "-e JUPYTER_DIR=/ "
        "-e DATA_DIRECTORY=/workspace/ "
        "-e PORTAL_CONFIG=\"localhost:1111:11111:/:Instance Portal|localhost:8188:18188:/:ComfyUI|localhost:8080:18080:/:Jupyter|localhost:8080:8080:/terminals/1:Jupyter Terminal|localhost:8384:18384:/:Syncthing\" "
        "-e COMFYUI_ARGS=\"--disable-auto-launch --port 18188 --enable-cors-header\""
    )

def launch_instance_with_offer_id(offer_id):
    print(f"🚀 Launching ComfyUI instance with Offer ID: {offer_id}")
    docker_image = "ghcr.io/okkazoo/comfyui-aidock:pytorch-2.3.0-py3.10-v2-cuda-12.1.1-base-22.04"
    docker_user = os.getenv("DOCKER_USERNAME", "okkazoo")
    docker_token = os.getenv("DOCKER_PASSWORD", "ghp_xxxx")

    cmd = [
        "python", VAST_SCRIPT_PATH,
        "create", "instance", str(offer_id),
        "--image", docker_image,
        "--disk", "100",
        "--login", f"-u {docker_user} -p {docker_token} ghcr.io",
        "--onstart-cmd", "init.sh",
        "--jupyter", "--ssh", "--direct",
        "--env", build_env_block()
    ]

    print("▶ Running:", " ".join(cmd))
    subprocess.run(cmd)
