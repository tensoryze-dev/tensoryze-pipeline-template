COMPONENT_FOLDER := components
include .env

.PHONY: help all setup init_repo python_setup local_run push_to_registry push_step_registry register create_variables deploy github_save _copy_source_files _local_run _get_git_remote _clean_up

help:
	@echo "Usage: make [target]"
	@echo
	@echo "[!] Please make sure that the .env file is setup correctly."
	@echo
	@echo "Available targets:"
	@@awk '/^#/{c=substr($$0,3);next}c&&/^[[:alpha:]][[:alnum:]_-]+:/{print substr($$1,1,index($$1,":")),c}1{c=0}' $(MAKEFILE_LIST) | column -s: -t


#			setup the development environment
python_setup:
# Usage: make python_setup GITHUB_TOKEN=your_token
	@echo "Setting up the development environment"
	python3 -m venv .venv
	./.venv/bin/pip install ipykernel
	./.venv/bin/pip install git+https://$(GITHUB_TOKEN)@github.com/tensoryze-dev/tensoryze_pipelines.git#egg=tensoryze_pipelines[ml]
	@TENSORYZE_PATH=$$(./.venv/bin/python -c "import tensoryze_pipelines, os; print(os.path.dirname(tensoryze_pipelines.__file__))") && \
	echo "" >> .env && \
	echo "TENSORYZE_PIPELINES_PATH=$$TENSORYZE_PATH" >> .env && \
	echo "📍 Path saved to .env as TENSORYZE_PIPELINES_PATH=$$TENSORYZE_PATH"
#			Force the reinstallation of the tensoryze_pipelines package
update_env:
	./.venv/bin/pip install --no-deps --force-reinstall git+https://$(GITHUB_TOKEN)@github.com/tensoryze-dev/tensoryze_pipelines.git#egg=tensoryze_pipelines

#			Local Test Run of the defined pipeline manifest
local_run: _copy_source_files _local_run
# Usage: make local_run GITHUB_TOKEN=your_token

_local_run:
	@echo "Build and execute the pipeline locally"
	@echo ----------------------------------------
	@./.venv/bin/python -m tensoryze_pipelines.pipeline.local.test_run --TOKEN=$(GITHUB_TOKEN) --manifest_path ./pipeline/manifest.json --components_folder ./components


build_local:
	@echo "Build the pipeline locally"
	@echo ----------------------------------------
	@for dir in $(COMPONENT_FOLDER)/*; do \
		if [ -d "$$dir" ]; then \
			docker build ./$$dir --no-cache; \
		fi \
	done

#			Push the built components to the container registry
push_to_registry:
	@for dir in $(COMPONENT_FOLDER)/*; do \
		if [ -d "$$dir" ]; then \
			component_name=$$(basename $$dir); \
			echo "Component name: $$component_name"; \
			docker build \
				--build-arg GITHUB_INSTALL_TOKEN=$(GITHUB_TOKEN) \
				-t $(TENSORYZE_API_HOST):$(DOCKER_REGISTRY_PORT)/${DATAPRODUCT_NAME}/$$component_name:latest \
				$$dir --no-cache; \
			echo "Tagged as $(TENSORYZE_API_HOST):$(DOCKER_REGISTRY_PORT)/${DATAPRODUCT_NAME}/$$component_name:latest"; \
			docker push $(TENSORYZE_API_HOST):$(DOCKER_REGISTRY_PORT)/${DATAPRODUCT_NAME}/$$component_name:latest; \
		fi \
	done


push_step_registry:
	echo "Component name: $(COMPONENT_NAME)"
	docker build -t $(COMPONENT_NAME):latest components/$(COMPONENT_NAME) --no-cache
	docker tag $(COMPONENT_NAME):latest $(CONTAINER_REGISTRY_URL)/$(COMPONENT_NAME):latest
	docker push $(CONTAINER_REGISTRY_URL)/$(COMPONENT_NAME):latest


#			Registers the pipeline with the CT Orchestrator
register:
	@echo "CURL the CT Orchestrator: ${TENSORYZE_API_HOST}:${TENSORYZE_API_PORT}/${TENSORYZE_API_VERSION}/orchestrator"
	./.venv/bin/python ./pipeline/register.py --register_url ${TENSORYZE_API_HOST}:${TENSORYZE_API_PORT}/${TENSORYZE_API_VERSION}/orchestrator



#			Creates the variables for the pipeline
versioning:
	@echo "Checking if GitHub repo exists..."


	@if [ -z "${GITHUB_TOKEN}" ]; then \
		echo "Error: GITHUB_TOKEN is not set"; \
		exit 1; \
	fi

	@if [ -z "${GIT_USER}" ] || [ -z "${GIT_REPO_NAME}" ]; then \
		echo "Error: TENSORYZE_API_HOST and GIT_REPO_NAME must be set"; \
		exit 1; \
	fi


	@if [ ! -d .git ]; then \
		echo "No Git repository found. Initializing..."; \
		git init; \
	fi

	@if git remote | grep -q "^origin$$"; then \
		git remote remove origin; \
		echo "Removed existing origin."; \
	fi

	@if ! curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
		https://api.github.com/repos/${GIT_USER}/${GIT_REPO_NAME} | grep -q '"full_name"'; then \
		echo "Repository does not exist. Creating it..."; \
		curl -s -X POST -H "Authorization: token ${GITHUB_TOKEN}" \
			-H "Accept: application/vnd.github.v3+json" \
			https://api.github.com/user/repos \
			-d "{\"name\":\"${GIT_REPO_NAME}\"}" > /dev/null; \
		echo "Repository created."; \
	else \
		echo "Repository exists."; \
	fi

	@git remote add origin https://github.com/${GIT_USER}/${GIT_REPO_NAME}.git
	@echo "Added new origin: https://github.com/${GIT_USER}/${GIT_REPO_NAME}.git"
	git add .
	git commit -m 'Initial commit'
	@git push -u origin HEAD



#			Copy the required files to the subfolders of each component
_copy_source_files:
	@echo "Copying requirements.txt to all subfolders in $(COMPONENT_FOLDER)"
	@for dir in $(COMPONENT_FOLDER)/*; do \
		if [ -d "$$dir" ]; then \
			cp -rf ./install/requirements.txt "$$dir/";\
			cp -rf ./inference_artifacts "$$dir/";\
			cp -rf ./testing_artifacts "$$dir/";\
			cp -rf ./.env "$$dir/";\
		fi \
	done

#			Get the current remote repository
_get_git_remote:
	git remote show origin

