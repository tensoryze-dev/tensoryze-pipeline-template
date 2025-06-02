import pickle, os
from tensoryze_pipelines.deployment import read_local_model_id, DeploymentSolver
from tensoryze_pipelines.ml_testing import (
    TestFactory, MetricFactory, RunManager, TransformationFactory
)
from tensoryze_pipelines.modeling import OpticalInspectionDataloader, OpticalInspectionDataset, OpticalInspectionTransformation
from tensoryze_pipelines.io import (
    image_folder_to_dataset, ExperimentTrackingInterface, LakeFSClient, DataLakeInterface, MachineLearningDataLakeClient,
)
from tensoryze_pipelines.utils.logging import get_logger

log = get_logger("testing")
IN_FILES = os.environ.get('IN_FILES', ["/tmp/run_id.yaml"])
NEW_MODEL_ID = read_local_model_id(IN_FILES[0], log)
TEST_SPECIFICATION = r"testing_artifacts/test_specification.yaml"


client = LakeFSClient(interface=DataLakeInterface()) 
client = MachineLearningDataLakeClient(client)

_ = ExperimentTrackingInterface()

parsed_model_id = NEW_MODEL_ID.split("/")[1]

with open("/tmp/model.pkl", 'rb') as f:
    model = pickle.load(f)

local_path = client.download_dataset(folder = "/tmp", branch_name=client.test_branch_name)
X_test, y_test = image_folder_to_dataset(local_path, subfolder=client.test_branch_name)
  
log.info("[ ] preparing training data")
TR = OpticalInspectionTransformation(img_size = 224)
DS_TEST = OpticalInspectionDataset(X_test, y_test, sensor = "vision_line", transform = TR.transform)
DL_TEST = OpticalInspectionDataloader(DS_TEST, log=log, test_split=False, val_split=False)

log.info("[x] prepared training data")

transformation_factory = TransformationFactory(224, None, DS_TEST, OpticalInspectionDataloader)
metric_factory = MetricFactory()
test_factory = TestFactory(model, transformation_factory, metric_factory)

run_manager = RunManager(specification_path=TEST_SPECIFICATION, model=model, test_factory=test_factory)
run_manager.execute_tests(run_id = parsed_model_id)

solver = DeploymentSolver(
    test_results=run_manager.test_results,
    hierarchy=run_manager.hierarchy_list,
)
solver.solve()
