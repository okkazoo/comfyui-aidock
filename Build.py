import subprocess
import os
import sys
from pathlib import Path

def load_env(env_path=".env"):
    env_vars = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip()
    return env_vars

def run(cmd, cwd=None, input=None, show=True):
    if show:
        print(f"▶ Running: {cmd}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=True,
        input=input,
        text=True
    )
    if result.returncode != 0:
        print("❌ Command failed.")
        sys.exit(result.returncode)

def main():
    BASE_DIR = Path(__file__).resolve().parent
    env_path = BASE_DIR / ".env"

    if not env_path.exists():
        print("❌ .env file not found.")
        sys.exit(1)

    env = load_env(env_path)

    target_tag = "okkazoo/mcp-tools:comfyui-aidock"

    print(f"🔐 Logging into Docker Hub as {env['DOCKER_USERNAME']}")
    run(f"docker login --username {env['DOCKER_USERNAME']} --password-stdin", input=env["DOCKER_TOKEN"])

    print("📦 Building image via docker-compose")
    run("docker compose build --no-cache", cwd=str(BASE_DIR))

    print("🔍 Locating the most recent comfyui image")
    result = subprocess.run(
        'docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | findstr comfyui',
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0 or not result.stdout.strip():
        print("❌ Could not find built image matching 'comfyui'")
        sys.exit(1)

    image_info = result.stdout.strip().split()
    source_tag, image_id = image_info[0], image_info[1]

    print(f"🏷️ Tagging image ID {image_id} as {target_tag}")
    run(f"docker tag {image_id} {target_tag}")

    print(f"☁️  Pushing image to Docker Hub: {target_tag}")
    run(f"docker push {target_tag}")

    print(f"✅ Done. Image pushed as {target_tag}")

if __name__ == "__main__":
    main()
