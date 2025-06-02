import argparse
import requests
import json
import dotenv
import os
dotenv.load_dotenv()


USER = os.getenv("TENSORYZE_API_USER")
PASSWORD = os.getenv("TENSORYZE_API_PASSWORD")

def register_pipeline(register_url):
    try:
        with open("./pipeline/manifest.json", "rb") as f:
            manifest = json.load(f)
        
        api_request_content = {"wf_name": manifest["name"], "workflow_manifest": json.dumps(manifest)}

        # Make a request to the specified register_url
        response = requests.put(url=register_url + "/workflow", params=api_request_content, auth=(USER, PASSWORD))
        # Handle response if needed
        print(response.text)
        print(f"Pipeline {manifest['name']} has been successfully registered at {register_url}")

    except Exception as e:
        print(e)
        print("Error while registering the pipeline. Please create a manifest first.")

def execute_pipeline(register_url):
    with open("./pipeline/manifest.json", "rb") as f:
        manifest = json.load(f)
    api_request_content = {"wf_name": manifest["name"]}
    response = requests.post(url=register_url + "/schedule_workflow", params=api_request_content, auth=(USER, PASSWORD))

if __name__ == "__main__":
    import time
    parser = argparse.ArgumentParser(description="Register pipeline")
    parser.add_argument("--register_url", help="URL for pipeline registration")
    args = parser.parse_args()

    if args.register_url:
        register_pipeline(args.register_url)
        
        time.sleep(3)

        execute_pipeline(args.register_url)

    else:
        print("Please provide a register URL using --register_url")
