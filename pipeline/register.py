import argparse
import requests
import json
import dotenv
import os
import traceback
dotenv.load_dotenv()


USER = os.getenv("TENSORYZE_API_USER")
PASSWORD = os.getenv("TENSORYZE_API_PASSWORD")

def register_pipeline(register_url):
    try:
        with open("./pipeline/manifest.json", "rb") as f:
            manifest = json.load(f)

        if not "http" in register_url:
            register_url = "http://" + register_url
        
        # api_request_content = {"wf_name": manifest["name"], "workflow_manifest": json.dumps(manifest)}

        register_url = register_url.rstrip("/") + "/pipeline_manifest"

        # Make a request to the specified register_url
        response = requests.post(url=register_url, data=json.dumps(manifest), auth=(USER, PASSWORD))

        if response.status_code != 200:
            raise Exception(f"Failed to register pipeline {register_url}: {response.status_code} - {response.text}")
        else:
            print(f"Pipeline {manifest['name']} has been successfully registered at {register_url}")

    except Exception as e:
        print("Error while registering the pipeline. Please create a manifest first.")
        raise 

def execute_pipeline(register_url):
    with open("./pipeline/manifest.json", "rb") as f:
        manifest = json.load(f)

    if not "http" in register_url:
        register_url = "http://" + register_url


    response = requests.post(url=register_url + "/schedule_execution", params={"wf_name": manifest["name"]}, auth=(USER, PASSWORD))

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
