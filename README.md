# **tensoryze pipeline editor**

This repository serves as a scaffold for the interactive and experimental-friendly development of Data and ML pipelines in the context of tensoryze core.

It ensures a free yet standardized development and a seamless integration of your custom Python code into the tensoryze core; especially towards its GitOps Deployment and Workflow Orchestrator capabilities.  

The development of this environment was guided by the following philosophy:
- Maintain a continuous experimentation mindset to minimize operational disruption, allowing multiple layers of experimentation and deployment to coexist:
    - **First Layer**: Execute pipeline code within the provided Jupyter Notebook (```pipeline-development.ipynb```). 
    - **Second Layer**: Locally build and execute the containerized ML pipeline on your machine.
    - **Third Layer**: Push the pipeline steps to a docker registry and register the ML pipeline with tensoryze core. The pipeline will be executed in the ops environment.
    - **Fourth Layer**: Add the deployment pipeline step to the pipeline allowing the GitOps deployment of the ML model.
- Structure projects for transparency, ensuring that related components are housed together for easy comprehension.
- Keep data science code close to its execution environment, enabling quick understanding of explored domains.
- Execute code consistently across various platforms, from Jupyter notebooks to cloud-triggered jobs.

### **How to develop a containerized ML pipeline:**
- Use ```make python_env``` to setup a local python environment and install tensoryze-piplines libary. [[GitHub - tensoryze-pipeliens](/https://github.com/tensoryze-dev/tensoryze_pipelines.git)]
- Develop and Iterate in the **frist layer**
    - Create the pipeline using the notebook ```pipeline-development.ipynb```.
    - (**Alternatively**, you are free to develop in another environment as long as you defer to the overall expectations.)
    - Test the components within the Notebook (after every pipeline step (== cell) run restart the kernel to avoid memory-related issues).
    - Use the "%%" magic command to save the **app.py** and **dockerfile** to the respective subfolders.
    - After all steps are created, use the "%%" magic command to create the pipeline manifest.
- Proceed to the **second layer** and execute the pipeline locally.
    - ```make local_run```
- After a sucessfull local run, register the pipeline with tensoryze core
    - ```make push_and_register```
    - ```make pipeline_execution```



## Outstanding Features:
- Add scripts like register.py and test_local.py to tensoryze_pipelines
- VS Code Extension
