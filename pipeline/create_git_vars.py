import os
import json
import yaml
import argparse

# Function to process the manifest file and generate variables
def process_manifest(ct_server):
    with open("./pipeline/manifest.json", "rb") as f:
        manifest = json.load(f)

    vars_dict = {
        "DEVICE_IP": manifest["docker-registry"].split("/")[1],
        "SUBDIR": "components",
        "PROGRAM": "noprogram",
        "ARCHITECTURE": "amd64",
        "BASE_IMAGE": "python:3.9-slim-buster",

        "DOCKER_REGISTRY_URL": manifest["docker-registry"].split("/")[0],
        "DOCKER_REGISTRY_USER": "ML",
        "DOCKER_REGISTRY_PASS": "MLfaps",

        "CT_SERVER_URL": ct_server,
        "CT_WORKFLOW_NAME": manifest["name"],
        "SERVICES": " ".join([manifest["components"][key]["name"] for key in list(manifest["components"].keys())])
    }

    vars_dict = {"variables": vars_dict}
    return vars_dict

# Function to save variables to a YAML file
def save_to_yaml(vars_dict):
    with open('.variables.yml', 'w') as file:
        yaml.dump(vars_dict, file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--ct_url', type=str, help="")

    args = parser.parse_args()

    generated_vars = process_manifest(args.ct_url)
    save_to_yaml(generated_vars)
