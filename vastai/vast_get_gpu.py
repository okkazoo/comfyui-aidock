# select_gpu_offer.py
import subprocess
import json
import os

# --- Configuration Constants ---
VAST_SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "vast.py"))
MIN_COMFYUI_CUDA = 12
REQUIRE_SINGLE_GPU = True

RANKED_GPUS = [
    {"name": "H200_NVL", "vram": "94GB", "desc": "Top-tier Blackwell GPU"},
    {"name": "H100_NVL", "vram": "80GB", "desc": "Enterprise-grade FP8 GPU"},
    {"name": "A100_SXM4", "vram": "40–80GB", "desc": "Strong tensor core, ideal for SDXL"},
    {"name": "L40S", "vram": "48GB", "desc": "Workstation-grade, great VRAM"},
    {"name": "RTX_6000Ada", "vram": "48GB", "desc": "Pro Ada GPU"},
    {"name": "RTX_4090", "vram": "24GB", "desc": "Top consumer GPU"},
    {"name": "RTX_4080S", "vram": "16–20GB", "desc": "Efficient newer gen"},
    {"name": "RTX_3090", "vram": "24GB", "desc": "Best 30-series GPU"},
]

def fetch_vast_offers():
    query = "rentable=true rented=false verified=true"
    cmd = ["python", VAST_SCRIPT_PATH, "search", "offers", query, "--raw"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    
def filter_cuda_compatibility(offers, min_version=12.1):
    compatible = []
    for offer in offers:
        max_cuda_raw = offer.get("cuda_max_good", "")
        try:
            max_cuda = float(max_cuda_raw)
            if max_cuda >= min_version:
                compatible.append(offer)
        except (ValueError, TypeError):
            continue
    return compatible

def filter_compatible_offers(offers):
    filtered = []
    for offer in offers:
        cuda = offer.get("cuda_max_good")
        num_gpus = offer.get("num_gpus", 1)
        gpu_name = offer.get("gpu_name", "Unknown")
        # if not isinstance(cuda, (float, int)):
        #     print(f"⛔ Skipping {gpu_name}: Missing or invalid cuda_max_good value.")
        #     continue
        # if REQUIRE_SINGLE_GPU and num_gpus > 1:
        #     print(f"⛔ Skipping {gpu_name}: More than one GPU ({num_gpus}).")
        #     continue
        # if float(cuda) < MIN_COMFYUI_CUDA:
        #     print(f"⛔ Skipping {gpu_name}: Max CUDA {cuda} < required {MIN_COMFYUI_CUDA}.")
        #     continue
        filtered.append(offer)
    return filtered


def filter_ranked_available_gpus(offers):
    available = {o['gpu_name'].replace(" ", "_") for o in offers if "gpu_name" in o}
    return [gpu for gpu in RANKED_GPUS if gpu["name"] in available]

def choose_gpu(available_gpus):
    print("🎯 Choose a GPU type:")
    for i, gpu in enumerate(available_gpus):
        print(f"[{i}] {gpu['name']:<14} {gpu['vram']:<8} {gpu['desc']}")
    try:
        selection = int(input("\nEnter the number of the GPU you'd like to search for: "))
        return available_gpus[selection]["name"]
    except (IndexError, ValueError):
        print("❌ Invalid selection.")
        return None

def build_query(gpu_name):
    return f"gpu_name == {gpu_name} rentable=true rented=false verified=true"

def search_offers(query):
    cmd = ["python", VAST_SCRIPT_PATH, "search", "offers", query, "--raw"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

def get_price(o):
    for key in ['dph', 'dph_total', 'cost_per_hour', 'dlperf_usd']:
        v = o.get(key)
        if isinstance(v, (int, float)):
            return round(v, 3)
    return "N/A"

def get_value_score(o):
    price = get_price(o)
    perf = o.get('dlperf', 0)
    if isinstance(price, (int, float)) and price > 0:
        return perf / price
    return None

def compute_value_scores(offers):
    values = [(o, get_value_score(o)) for o in offers if isinstance(get_value_score(o), (int, float))]
    if not values:
        return {}
    best_value = max(v for _, v in values)
    return {o['id']: round((v / best_value) * 100, 1) for o, v in values}

def compute_ranked_scores(offers):
    def safe_get(o, key): return o.get(key, 0) or 0
    scores = {}
    values = [get_value_score(o) or 0 for o in offers]
    speeds = [safe_get(o, 'inet_up') + safe_get(o, 'inet_down') for o in offers]
    perfs  = [safe_get(o, 'dlperf') for o in offers]
    max_val = max(values or [1])
    max_speed = max(speeds or [1])
    max_perf = max(perfs or [1])
    for o in offers:
        value = get_value_score(o) or 0
        speed = safe_get(o, 'inet_up') + safe_get(o, 'inet_down')
        perf = safe_get(o, 'dlperf')
        score = (
            (value / max_val) * 0.4 +
            (speed / max_speed) * 0.3 +
            (perf / max_perf) * 0.3
        ) * 100
        scores[o['id']] = round(score, 1)
    return scores

def sort_offers(offers):
    ranked_scores = compute_ranked_scores(offers)
    def sort_key(o):
        for k in ['dph', 'dph_total', 'cost_per_hour', 'dlperf_usd']:
            v = o.get(k)
            if isinstance(v, (int, float)):
                price = v
                break
        else:
            price = float('inf')
        inet_down = o.get('inet_down', 0) or 0
        score = ranked_scores.get(o['id'], 0)
        return (price, -inet_down, -score)
    return sorted(offers, key=sort_key)

def print_results(offers):
    ranked_scores = compute_ranked_scores(offers)
    best_offer = find_best_offer(offers)
    best_offer_id = best_offer['id'] if best_offer else None
    print(f"{'Num':<5} {'ID':<10} {'GPU':<14} {'VRAM':<6} {'#GPUs':<6} {'CUDA':<6} "
          f"{'Price/hr':<10} {'Inet Up':<10} {'Inet Down':<12} {'Score':<8}")
    print("-" * 110)
    for idx, o in enumerate(offers):
        price = get_price(o)
        score = ranked_scores.get(o['id'], "N/A")
        tag = "🏆" if o['id'] == best_offer_id else ""
        cuda = o.get('cuda_max_good', "N/A")
        num_gpus = o.get('num_gpus', 1)
        print(f"{idx:<5} {o['id']:<10} {o.get('gpu_name', 'N/A'):<14} {o.get('gpu_ram', 'N/A'):<6} "
              f"{num_gpus:<6} {cuda:<6} {price:<10} {o.get('inet_up', 0):<10} {o.get('inet_down', 0):<12} {str(score) + tag:<8}")

def find_best_offer(offers):
    def safe_price(o):
        for key in ['dph', 'dph_total', 'cost_per_hour', 'dlperf_usd']:
            v = o.get(key)
            if isinstance(v, (int, float)):
                return v
        return float('inf')
    def score(o):
        price = safe_price(o)
        if not price or price == float('inf'):
            return 0
        return (o.get('inet_up', 0) + o.get('inet_down', 0)) / price
    return max(offers, key=score, default=None)

# --- External Hook ---
def get_best_offer():
    raw_offers = fetch_vast_offers()
    offers = filter_compatible_offers(raw_offers)
    available_ranked = filter_ranked_available_gpus(offers)
    if not available_ranked:
        print("❌ No ranked GPUs available.")
        return None
    gpu_choice = choose_gpu(available_ranked)
    if not gpu_choice:
        return None
    query = build_query(gpu_choice)
    gpu_offers = search_offers(query)
    gpu_offers = filter_compatible_offers(gpu_offers)
    if not gpu_offers:
        print("❌ No compatible offers found for selected GPU.")
        return None
    sorted_offers = sort_offers(gpu_offers)
    print_results(sorted_offers)
    best = find_best_offer(sorted_offers)
    return best

# Optional: test standalone
if __name__ == "__main__":
    best = get_best_offer()
    if best:
        print("\n🔥 Best Offer (balanced internet + price):")
        print(f"ID: {best['id']}")
        print(f"GPU: {best['gpu_name']} | VRAM: {best['gpu_ram']}MB | CUDA: {best.get('cuda_max_good', 'N/A')}")
        print(f"Price/hr: ${get_price(best)}")
        print(f"Inet Up: {best['inet_up']} Mbps | Inet Down: {best['inet_down']} Mbps")
        print(f"Perf Score: {round(best.get('dlperf', 0), 2)}")
