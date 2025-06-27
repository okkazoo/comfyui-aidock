import os
import sys
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv

# Setup
ROOT_DIR = Path(__file__).resolve().parent
VAST_SCRIPT_PATH = os.path.join(ROOT_DIR, "vastai", "vast.py")
WORKFLOW_PATH = ROOT_DIR / "workflows" / "default_workflow.json"
OUTPUT_DIR = ROOT_DIR / "workflow_outputs"
load_dotenv(ROOT_DIR / ".env")

# Ensure vastai imports work
sys.path.insert(0, str(ROOT_DIR / "vastai"))

from vastai.vast_get_gpu import (
    fetch_vast_offers, filter_compatible_offers, filter_ranked_available_gpus,
    search_offers, build_query, get_price, sort_offers, print_results, find_best_offer
)

from run_workflow import WorkflowRunner

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

def launch_instance(offer_id):
    print(f"\n🚀 Launching ComfyUI instance with Offer ID: {offer_id}")
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

def select_gpu_and_offer():
    raw_offers = fetch_vast_offers()
    offers = filter_compatible_offers(raw_offers)
    ranked = filter_ranked_available_gpus(offers)

    if not ranked:
        print("❌ No ranked GPUs available.")
        sys.exit(1)

    print("🎯 Choose a GPU type:")
    for i, gpu in enumerate(ranked):
        print(f"[{i}] {gpu['name']:<14} {gpu['vram']:<8} {gpu['desc']}")

    try:
        selection = int(input("\nEnter the number of the GPU you'd like to use: "))
        gpu_name = ranked[selection]["name"]
    except (IndexError, ValueError):
        print("❌ Invalid selection.")
        sys.exit(1)

    print(f"\n🔍 Searching for best offers for: {gpu_name}")
    query = build_query(gpu_name)
    gpu_offers = search_offers(query)
    gpu_offers = filter_compatible_offers(gpu_offers)

    if not gpu_offers:
        print("❌ No compatible offers found.")
        sys.exit(1)

    sorted_offers = sort_offers(gpu_offers)
    print_results(sorted_offers)

    best = find_best_offer(sorted_offers)
    if not best:
        print("❌ No suitable offer found.")
        sys.exit(1)

    print(f"\n✅ Best offer selected: ID {best['id']} | GPU: {best['gpu_name']} | DPH: ${get_price(best)}")
    return best["id"]

def run_workflow(instance_id):
    runner = WorkflowRunner(workflow_path=WORKFLOW_PATH, output_dir=OUTPUT_DIR)
    runner.instance_id = instance_id
    runner.run(skip_prompt=True)

def main():
    offer_id = select_gpu_and_offer()
    launch_instance(offer_id)
    run_workflow(offer_id)

if __name__ == "__main__":
    main()
