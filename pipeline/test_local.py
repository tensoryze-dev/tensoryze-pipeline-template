import json, docker, os, argparse, urllib
mount_dir = os.path.join(os.getcwd(), "pipeline", "tmp")
os.makedirs(mount_dir, exist_ok=True)


def delete_image(name):
    client = docker.from_env()
    try:
        client.images.remove(name, force=True)
        print(f"[x] {name} was removed")
    except:
        print(f"[ ] {name} was not found")

def build_and_run_container(file, name, token):
    logs = []
    client = docker.from_env()
    print("---------------------------------")
    print(f"📌   Execution of {file}: ")
    # Build the Docker image from the Dockerfile
    try:
        
        image_name = name.split("/")[-1]
        print(f"🔄   Building {file}. This might take a while...")
        safe_token = urllib.parse.quote(token, safe='')  # encode all special chars

        image, _ = client.images.build(path=file, tag=name, rm=True, buildargs={"GITHUB_INSTALL_TOKEN": safe_token}, nocache=False)
        print(f"ℹ️   {file} was built!")
        # Run a container from the built image
        print(f"⚙️   Execute {name}")
    except:
        print("Make sure to deinstall docker-py and install docker instead")
        print("pip uninstall docker-py && pip install docker")
        print("Another issue might be due to the utilization of base images.")
        print("Please build the image manually and run the container.")
        print("docker build component/test-component")
        raise

    print(f"ℹ️   {name} was built! Now running the container...")




    container = client.containers.run(name, detach=True, volumes={
            mount_dir: {'bind': '/tmp/', 'mode': 'rw'},
            "/dev/shm": {"bind": "/dev/shm", "mode": "rw"},
        },
        device_requests=[
            docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])
        ]
    )
    print(f"    Logs:")
    for log in container.logs(stream=True, follow=True):
        #print(log.decode("utf-8").strip())

        # continously stream the most important logs to the API
        logs.append("     " + log.decode("utf-8").strip())
        print(logs[-1])

    print(f"✅   Executed {name} successfully.")

with open("./pipeline/manifest.json", "rb") as f:
    manifest = json.load(f)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline runner")
    parser.add_argument("--TOKEN", required=True, help="Authentication token")
    args = parser.parse_args()

    print("ℹ️   We currently only support simple pipelines. Please test the pipeline manually if you have complex pipelines")

    components = manifest["components"]
    steps = manifest["pipeline"]

    for current_step, next_steps in steps.items():
        for next_step in next_steps:
            if next_step != "end":
                component = components[next_step]["name"]
                file = os.path.join("./components", component)
                build_and_run_container(file, component, args.TOKEN)