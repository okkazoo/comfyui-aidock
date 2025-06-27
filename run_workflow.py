import sys
import os
import time
import json
import requests
import websocket
import uuid
from urllib.parse import urlparse
from pathlib import Path
import random
import urllib3
from dotenv import load_dotenv
import signal
import subprocess
import ssl
import re
import datetime
import argparse
from collections import OrderedDict

# Load environment variables and disable warnings
load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration Constants
TEMPLATE_HASH = "87c9953d281b27edaf9692aa5fb85fc6"  # ComfyUI template

# Get the path to vast.py in utils folder relative to this script
SCRIPT_DIR = Path(__file__).parent
VAST_SCRIPT_PATH = str(SCRIPT_DIR / "scripts" / "vast.py")

# Update the workflow path to point to the workflows directory
DEFAULT_WORKFLOW_PATH = SCRIPT_DIR / "workflows" / "default_workflow.json"

# Updated SEARCH_CRITERIA with enforced order
SEARCH_CRITERIA = OrderedDict([
    ('gpu_name', ('=', 'RTX_3090', '🎮 GPU')),
    ('dph', ('<', 3.0, '💵 Price')),
    ('gpu_ram', ('>=', 24, '💾 RAM')),
    ('inet_up', ('>=', 1000, '🌐 Upload')),
    ('inet_down', ('>=', 1000, '🌐 Download')),
    ('reliability', ('>', 0.95, '🛡️  Reliability'))
])

def format_search_criteria():
    """Convert search criteria to human-readable format"""
    symbols = {'>': '>', '<': '<', '>=': '≥', '<=': '≤', '=': ''}
    lines = []
    
    for key, (op, val, display) in SEARCH_CRITERIA.items():
        symbol = symbols.get(op, op)
        if key == 'gpu_name':
            lines.append(f"{display}: {val.replace('_', ' ')}")
        else:
            lines.append(f"{display} {symbol} {val}")
    
    return "\n".join(lines)

def search_instances():
    """Search for available instances matching our criteria"""
    # Build query with proper spacing and format
    query_parts = []
    for key, (op, val, _) in SEARCH_CRITERIA.items():
        if key == 'gpu_name':
            query_parts.append(f"{key} {op} {val}")  # e.g. "gpu_name = RTX_3090"
        else:
            query_parts.append(f"{key} {op} {val}")  # e.g. "dph < 3.0"
    
    # Add required conditions with proper spacing
    query_parts.extend([
        "rentable = true",  # Changed True to true to match CLI format
        "rented = false",   # Changed False to false
        "verified = true"
    ])
    
    # Join with spaces (not AND)
    query = " ".join(query_parts)
    
    cmd = [
        "python", str(VAST_SCRIPT_PATH),
        "search", "offers",
        query,
        "--raw"
    ]
    
    try:
        print(f"\n🔍 Search query: {query}")  # Debug output
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stderr:
            print(f"Warning: {result.stderr}")
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error searching instances: {e}")
        print(f"Error details: {e.stderr}")
        return None

# Import ComfyUIClient class
class ComfyUIClient:
    def __init__(self, server_address, workflow, output_dir="./outputs"):
        # Ensure we're using https:// and wss://
        parsed = urlparse(server_address)
        self.server_address = f"https://{parsed.netloc or parsed.path}"
        self.ws_address = f"wss://{parsed.netloc or parsed.path}/ws"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.running = True
        self.client_id = str(uuid.uuid4())
        self.workflow = workflow  # Store the workflow
        
        # Add timestamp attribute
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        microsecond = str(datetime.datetime.now().microsecond).zfill(6)
        self.timestamp = f"{timestamp}_{microsecond}"

    def queue_prompt(self, prompt):
        """Queue a prompt with retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                p = {"prompt": prompt, "client_id": self.client_id}
                data = json.dumps(p).encode('utf-8')
                
                url = f"{self.server_address}/prompt"
                
                response = requests.post(url, data=data, verify=False)
                response.raise_for_status()
                
                result = response.json()
                prompt_id = result.get('prompt_id')
                
                if prompt_id:
                    print(f"\n✅ Successfully queued prompt (ID: {prompt_id})")
                else:
                    print("\n⚠️ Warning: No prompt ID in response")
                    
                return result
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 502 and attempt < max_retries-1:
                    print(f"🔄 Retrying prompt queue ({attempt+1}/{max_retries})")
                    time.sleep(5)
                    continue
                raise

    def get_image(self, filename, subfolder, folder_type):
        """Download an image from the server"""
        url = f"{self.server_address}/view"
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        }
        response = requests.get(url, params=params, verify=False)
        
        if response.status_code == 200:
            # Get file extension from original filename
            _, ext = os.path.splitext(filename)
            
            # Create new filename with just the timestamp
            new_filename = f"{self.timestamp}{ext}"
            output_path = self.output_dir / new_filename
            
            # Save the image
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Image saved to {output_path}")
            return output_path
        else:
            print(f"Failed to download image: {response.status_code}")
            return None

    def get_history(self, prompt_id):
        """Get the execution history for a prompt"""
        url = f"{self.server_address}/history/{prompt_id}"
        response = requests.get(url, verify=False)
        return response.json()

    def process_history_output(self, history):
        """Process the output history and save images"""
        if 'outputs' not in history:
            return
            
        for node_id, node_output in history['outputs'].items():
            if 'images' in node_output:
                for image in node_output['images']:
                    self.get_image(
                        image['filename'],
                        image['subfolder'],
                        image['type']
                    )

    def wait_for_output(self):
        """Wait for and handle the output from the workflow"""
        ws = websocket.WebSocket()
        try:
            ws.connect(f"{self.ws_address}?clientId={self.client_id}", sslopt={"cert_reqs": ssl.CERT_NONE})
            
            start_time = time.time()
            timeout = 10  
            
            while self.running:
                try:
                    if time.time() - start_time > timeout:
                        print("\n⚠️ Workflow timed out after 5 minutes")
                        break
                        
                    ws.settimeout(10)
                    out = ws.recv()
                    
                    if isinstance(out, str):
                        message = json.loads(out)
                        message_type = message.get("type", "")
                        message_data = message.get("data", {})
                        
                        if message_type == "executing":
                            node_id = str(message_data.get('node', ''))
                            
                            if node_id:  # Only print if we have a node ID
                                node_data = self.workflow.get(node_id, {})
                                node_type = node_data.get('class_type', 'Unknown')
                                print(f"⏳ Processing: {node_type}")
                                
                        elif message_type == "progress":
                            value = message_data.get('value', 0)
                            max_steps = message_data.get('max', 0)
                            print(f"\r⏳ KSampler: {value}/{max_steps} steps", end="", flush=True)
                            if value == max_steps:
                                print()  # New line after completion
                            
                        elif message_type == "executed":
                            # Handle node completion and image saving
                            node_id = str(message_data.get('node', ''))
                            if node_id:
                                node_data = self.workflow.get(node_id, {})
                                if node_data.get('class_type') == 'SaveImage':
                                    output = message_data.get('output', {})
                                    if 'images' in output:
                                        for image in output['images']:
                                            filename = image['filename']
                                            subfolder = image['subfolder']
                                            image_type = image['type']
                                            print(f"\n💾 Saving image: {filename}")
                                            self.get_image(filename, subfolder, image_type)
                                        self.running = False
                                        break
                                    
                        elif message_type == "execution_success":
                            # Workflow is complete
                            print("\n✅ Workflow complete!")
                            self.running = False
                            break
                            
                except websocket.WebSocketTimeoutException:
                    if not self.running:
                        break
                    continue
                    
        finally:
            ws.close()

    def stop(self):
        """Stop the client gracefully"""
        self.running = False

class WorkflowRunner:
    def __init__(self, workflow_path=None, output_dir="./workflow_outputs"):
        # If no workflow path provided, use default
        if workflow_path is None:
            self.workflow_path = DEFAULT_WORKFLOW_PATH
        else:
            self.workflow_path = workflow_path
            
        # Get workflow name from the path and use it directly for the directory name
        workflow_name = Path(self.workflow_path).stem
        
        # Create output directory with just the workflow name
        self.output_dir = Path(output_dir) / workflow_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get current timestamp for the image files
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        microsecond = str(datetime.datetime.now().microsecond).zfill(6)
        self.timestamp = f"{timestamp}_{microsecond}"
        
        self.instance_id = None
        self.comfy_client = None
        
        # Load the workflow using the provided path
        try:
            with open(self.workflow_path, 'r') as f:
                self.workflow = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find workflow file at {self.workflow_path}")
        
        # Keep only the parameter modifications
        self.workflow["3"]["inputs"]["seed"] = random.randint(1, 1000000000000000)
        self.workflow["3"]["inputs"]["steps"] = 30
        self.workflow["3"]["inputs"]["cfg"] = 7
        
        # You can modify prompts here if needed
        # self.workflow["6"]["inputs"]["text"] = "A vast, rocky alien desert..."
        
        self.prompt_text = None  # Add this line

    def find_existing_instance(self):
        """Find and handle existing instances with detailed state logging"""
        try:
            cmd = ["python", VAST_SCRIPT_PATH, "show", "instances", "--raw"]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            instances = json.loads(result.stdout)
            
            for instance in instances:
                if instance.get('template_hash_id') == TEMPLATE_HASH:
                    actual = instance.get('actual_status', '').lower()
                    intended = instance.get('intended_status', '').lower()
                    
                    print(f"\n🔍 Found instance {instance['id']}")
                    
                    # Existing state decision tree
                    if intended == 'running':
                        if actual == 'running':
                            print("   ✅ Already running - using this instance")
                            return instance
                            
                        if actual == 'stopped':
                            print("   🔄 Starting stopped instance...")
                            return self.handle_instance_start(instance['id'], actual, intended)
                            
                    elif intended == 'stopping':
                        print("   🔄 Restarting instance...")
                        return self.handle_instance_restart(instance['id'], actual, intended)

                    # Removed unhandled status warning
                    return self.handle_instance_start(instance['id'], actual, intended)

            print("\n⏳ No existing instances found")
            return None
        except Exception as e:
            print(f"Error checking instances: {e}")
            return None

    def handle_instance_start(self, instance_id, current_actual, current_intended):
        """Handle instance startup with extended port verification"""
        print(f"🚀 Starting instance {instance_id}")
        
        try:
            cmd = ["python", VAST_SCRIPT_PATH, "start", "instance", str(instance_id)]
            subprocess.run(cmd, check=True, capture_output=True)
            
            print("⏳ Waiting for instance to start")
            start_time = time.time()
            
            while time.time() - start_time < 300:  # 5 minute timeout
                time.sleep(1)  # More frequent updates
                elapsed = int(time.time() - start_time)
                
                # Get updated instance info
                cmd = ["python", VAST_SCRIPT_PATH, "show", "instances", "--raw"]
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                instances = json.loads(result.stdout)
                
                for instance in instances:
                    if instance['id'] == instance_id:
                        # Check ports without showing state
                        ports = instance.get('ports', {})
                        
                        # Expanded port candidate list
                        port_candidates = [
                            '8188', '8188/tcp', 'tcp/8188',
                            '8188/http', 'http/8188', '8188-tcp',
                            'tcp-8188', '8188_http', 'http_8188'
                        ]
                        
                        port_found = False
                        for port in port_candidates:
                            if port in ports:
                                host_port = ports[port][0]['HostPort'] if isinstance(ports[port], list) else ports[port]
                                port_found = True
                                break
                        
                        if port_found:
                            print()  # Add newline before returning
                            return instance
                        
                        # Update elapsed time display
                        print(f"\r⏳ Instance startup: {elapsed}s / 300s", end="", flush=True)
                        break
                
            # Final state before error
            print(f"\r⏳ Instance startup: 300s / 300s")  
            print("\n❌ Port 8188 never became available after 5 minutes")
            self.destroy_instance(instance_id)
            return None
            
        except Exception as e:
            print(f"\n❌ Startup failed: {e}")
            self.destroy_instance(instance_id)
            return None

    def destroy_instance(self, instance_id):
        """Destroy an instance reliably"""
        try:
            print(f"🔄 Destroying instance {instance_id}...")
            cmd = ["python", VAST_SCRIPT_PATH, "destroy", "instance", str(instance_id)]
            subprocess.run(cmd, check=True, capture_output=True)
            print("✅ Instance destroyed successfully")
            time.sleep(5)  # Brief wait for cleanup
        except Exception as e:
            print(f"⚠️ Error destroying instance: {e}")

    def start_instance(self, instance_id):
        """Start a stopped instance and verify it's not stuck in scheduling"""
        try:
            # Attempt to start the instance
            cmd = ["python", VAST_SCRIPT_PATH, "start", "instance", str(instance_id)]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Wait and check instance status
            max_retries = 6  # 30 seconds total
            for attempt in range(max_retries):
                time.sleep(5)  # Wait 5 seconds between checks
                
                # Get current instance status
                cmd = ["python", VAST_SCRIPT_PATH, "show", "instances", "--raw"]
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                instances = json.loads(result.stdout)
                
                for instance in instances:
                    if instance['id'] == instance_id:
                        actual_status = instance.get('actual_status', '').lower()
                        intended_status = instance.get('intended_status', '').lower()
                        
                        print(f" Instance {instance_id} status (attempt {attempt + 1}/{max_retries}):")
                        print(f"   Actual: {actual_status}")
                        print(f"   Intended: {intended_status}")
                        
                        # Check for scheduling state
                        if actual_status == 'scheduling' or (intended_status == 'running' and actual_status != 'running'):
                            # Ask for user confirmation before destroying
                            print(f"🔄 Instance {instance_id} stuck in scheduling.")
                            response = input("Do you want to destroy this instance? (y/n): ").strip().lower()
                            if response == 'y':
                                print(f"🔄 Destroying instance {instance_id}...")
                                cmd = ["python", VAST_SCRIPT_PATH, "destroy", "instance", str(instance_id)]
                                subprocess.run(cmd, check=True, capture_output=True)
                                print(f"✅ Successfully destroyed instance {instance_id}")
                                return False
                            else:
                                print("🚫 Skipping instance destruction. Exiting...")
                                sys.exit(0)
                        
                        # Check for success
                        if actual_status == 'running' and intended_status == 'running':
                            print(f"✅ Instance {instance_id} started successfully")
                            return True
                        
                        break  # Found our instance, break inner loop
                
                print(f"⏳ Still waiting for instance to start...")
            
            # If we get here, instance failed to start properly
            print(f"❌ Instance failed to start after {max_retries} attempts")
            return False
            
        except Exception as e:
            print(f"Error starting instance: {e}")
            return False

    def stop_instance(self):
        """Stop the instance (without destroying it)"""
        if self.instance_id:
            print("\n🛑 Stopping instance...")
            try:
                cmd = ["python", VAST_SCRIPT_PATH, "stop", "instance", str(self.instance_id)]
                subprocess.run(cmd, check=True)
                print("✅ Instance stopped successfully")
            except Exception as e:
                print(f"⚠️ Error stopping instance: {e}")
                print("Please manually verify instance status at vast.ai")

    def handle_scheduling_state(self, instance_id):
        """Handle instance stuck in scheduling state"""
        print(f"🔄 Instance {instance_id} stuck in scheduling, destroying it...")
        self.destroy_instance(instance_id)
        return self.create_new_instance()

    def get_server_url(self):
        """Get server URL with proper port handling"""
        instance = self.find_existing_instance()
        
        if instance:
            self.instance_id = instance['id']
            ip = instance.get('public_ipaddr')
            ports = instance.get('ports', {})
            
            # Find ComfyUI port with icon formatting
            for port_name in ports:
                if port_name.startswith('8188'):
                    comfy_port = ports[port_name][0]['HostPort']
                    print(f"\n\n🔗 ComfyUI: {ip}:{comfy_port} → {port_name}")
                    return f"https://{ip}:{comfy_port}"
            
            print(f"❌ No ComfyUI port found in: {list(ports.keys())}")
            raise Exception("Missing ComfyUI port mapping")
        
        # If no instance, create new one
        return self.create_new_instance()

    def get_user_prompt(self):
        """Get custom prompt from user with preview"""
        current_prompt = self.get_current_prompt_from_workflow()
        print(f"\n📄 Current workflow prompt:\n\"{current_prompt}\"")
        new_prompt = input("\nEnter new prompt (or press Enter to keep current):\n> ").strip()
        
        if new_prompt:
            print(f"\n✅ Using custom prompt:\n\"{new_prompt}\"")
            return new_prompt
        print("\n✅ Using existing prompt")
        return current_prompt
        
    def get_current_prompt_from_workflow(self):
        """Extract current prompt from workflow nodes"""
        for node_id, node_data in self.workflow.items():
            if node_data.get('class_type') == 'CLIPTextEncode':
                return node_data['inputs'].get('text', 'No prompt found')
        return "No prompt found in workflow"
        
    def update_workflow_prompt(self, new_prompt):
        """Update workflow with new prompt"""
        for node_id, node_data in self.workflow.items():
            if node_data.get('class_type') == 'CLIPTextEncode':
                node_data['inputs']['text'] = new_prompt
                
    def run(self, skip_prompt=False):
        """Run the complete workflow process"""
        try:
            if not skip_prompt:
                # Get and update prompt
                custom_prompt = self.get_user_prompt()
                self.update_workflow_prompt(custom_prompt)
                
            # Get server URL (from existing or new instance)
            server_url = self.get_server_url()
            
            # Wait for ComfyUI to be fully responsive
            wait_for_comfyui_ready(server_url)
            
            time.sleep(5)  # Small additional wait
            
            # Run the workflow
            self.run_workflow(server_url)
            
            # Show results
            print(f"\n✨ Workflow complete! Images saved in: {self.output_dir}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if self.comfy_client:
                self.comfy_client.stop()
            self.stop_instance()

    def create_new_instance(self):
        """Create a new instance using the latest logic"""
        print("\n🔍 Searching for suitable GPU instance:")
        print(format_search_criteria())
        
        offers = search_instances()
        if not offers:
            raise Exception("❌ No suitable offers found")
        
        best_offer = sorted(offers, key=lambda x: x['dph_total'])[0]
        print(f"\n🚀 Launching instance...")
        instance_data = launch_instance(best_offer['id'])
        
        if not instance_data:
            raise Exception("❌ Failed to launch instance")
            
        # Updated to use new data structure
        self.instance_id = instance_data['instance_id']
        ip = instance_data['ip']
        comfy_port = instance_data['comfy_port']
        
        print(f"\n✅ Instance Created: {self.instance_id}")
        print(f"🌐 Public IP: {ip}")
        
        if comfy_port:
            print(f"🔗 ComfyUI: https://{ip}:{comfy_port}")
            return f"https://{ip}:{comfy_port}"
        
        raise Exception("Could not find ComfyUI port mapping (8188)")

    def run_workflow(self, server_url):
        """Run the workflow on the ComfyUI server"""
        print("\n🎨 Running workflow...")
        
        # Initialize ComfyUI client with workflow
        self.comfy_client = ComfyUIClient(server_url, self.workflow, self.output_dir)
        
        try:
            # Queue workflow
            result = self.comfy_client.queue_prompt(self.workflow)
            
            # Check if the prompt was queued successfully
            if not result.get('prompt_id'):
                raise Exception("Failed to queue workflow - no prompt ID received")
            
            # Wait for results
            self.comfy_client.wait_for_output()
            
            # Verify we got some output
            output_files = list(self.output_dir.glob('*.png'))
            if not output_files:
                raise Exception("No output images were generated")
            
        except Exception as e:
            print(f"\n❌ Error running workflow: {e}")
            raise

    def handle_instance_restart(self, instance_id, current_actual, current_intended):
        """Handle instance restart with state-aware logging"""
        print(f"🔄 Restarting instance {instance_id}")
        print(f"   CURRENT STATE: Actual='{current_actual}', Intended='{current_intended}'")
        
        try:
            # Stop if needed
            if current_actual != 'stopped':
                print("⏳ Stopping instance first...")
                cmd = ["python", VAST_SCRIPT_PATH, "stop", "instance", str(instance_id)]
                subprocess.run(cmd, check=True, capture_output=True)
                time.sleep(10)
                
            # Start fresh
            return self.handle_instance_start(instance_id, 'stopped', 'running')
        except Exception as e:
            print(f"❌ Restart failed: {e}")
            self.destroy_instance(instance_id)
            return None

def wait_for_comfyui_ready(server_url, timeout=600):  # Increased to 10 minutes
    """Wait for ComfyUI server to be fully ready"""
    print("\n⏳ ComfyUI initializing...", end="", flush=True)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        elapsed = int(time.time() - start_time)
        print(f"\r⏳ ComfyUI initializing: {elapsed}s / 600s", end="", flush=True)
        
        try:
            # Original dual-endpoint check from save file
            stats_url = f"{server_url}/system_stats"
            stats_response = requests.get(stats_url, verify=False, timeout=5)
            
            if stats_response.status_code == 200:
                prompt_url = f"{server_url}/prompt"
                prompt_response = requests.options(prompt_url, verify=False, timeout=5)
                
                if prompt_response.status_code != 405:
                    print(f"\r⏳ ComfyUI initializing: {elapsed}s / 600s")  # Final state
                    print("✅ ComfyUI API is fully responsive!")
                    return True
                    
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(5)
    
    # Timeout handling
    print("\r❌ ComfyUI failed to initialize after 600s")
    raise Exception("ComfyUI API failed to respond after 10 minutes")

def main():
    # Setup signal handler for graceful exit
    def signal_handler(signum, frame):
        print("\n\nReceived interrupt signal")
        if hasattr(main, 'runner'):
            main.runner.stop_instance()  # Stop instead of destroy
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    output_dir = "./workflow_outputs"
    
    # Create and run workflow runner
    main.runner = WorkflowRunner(output_dir=output_dir)
    
    # First attempt
    try:
        main.runner.run()
    except Exception as e:
        print(f"\n⚠️ First attempt failed: {e}")
        print("🔄 Retrying with new instance...")
        # Retry with new instance, skipping prompts
        main.runner.run(skip_prompt=True)

if __name__ == "__main__":
    main() 