import os
from pathlib import Path
from dotenv import load_dotenv
from run_workflow import WorkflowRunner
from vastai.vast_get_gpu import fetch_vast_offers, filter_compatible_offers, sort_offers
from launch_utils import launch_instance_with_offer_id

SCRIPT_DIR = Path(__file__).parent
WORKFLOW_PATH = SCRIPT_DIR / "workflows" / "default_workflow.json"
OUTPUT_DIR = SCRIPT_DIR / "workflow_outputs"
ENV_PATH = SCRIPT_DIR / ".env"
load_dotenv(ENV_PATH)

def find_best_rtx3090_offer():
    offers = fetch_vast_offers()
    offers = filter_compatible_offers(offers)
    rtx3090_offers = [o for o in offers if o["gpu_name"] == "RTX_3090"]
    if not rtx3090_offers:
        raise RuntimeError("❌ No RTX_3090 offers available.")
    sorted_offers = sort_offers(rtx3090_offers)
    return sorted_offers[0]

def main():
    print("🚀 Auto-selecting best RTX 3090 offer...")
    best_offer = find_best_rtx3090_offer()
    print(f"✅ Selected Offer ID: {best_offer['id']} | GPU: {best_offer['gpu_name']} | DPH: ${best_offer['dph_total']}/hr")

    # 🔥 Launch instance with envs
    launch_instance_with_offer_id(best_offer['id'])

    # 🎨 Run workflow
    runner = WorkflowRunner(workflow_path=WORKFLOW_PATH, output_dir=OUTPUT_DIR)
    runner.instance_id = best_offer['id']
    runner.run(skip_prompt=True)

if __name__ == "__main__":
    main()
