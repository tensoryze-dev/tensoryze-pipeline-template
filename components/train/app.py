
import pytorch_lightning as pl
import  os, glob
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks import ModelCheckpoint

from tensoryze_pipelines.modeling import (
    OpticalInspectionDataloader, OpticalInspectionDataset,  OpticalInspectionTransformation, TemperatureScaledActiveLearner,
    ResNet18
)
from tensoryze_pipelines.utils.logging import logger
from tensoryze_pipelines.io import (
    DataLakeInterface, LakeFSClient, MachineLearningDataLakeClient,
    write_dict_to_yaml, read_pickle, write_json, image_folder_to_dataset,
    ExperimentTrackingInterface, MLFlowExperimentTracking, 

)

OUT_FILES = os.environ.get('OUT_FILES', ["/tmp/run_id.yaml"])
N_EPOCHS = os.environ.get('N_EPOCHS', 10)

log = logger
experiment_tracker = MLFlowExperimentTracking(ExperimentTrackingInterface())
client = MachineLearningDataLakeClient(
    LakeFSClient(interface=DataLakeInterface()) 
)
local_path = client.download_dataset(folder = "/tmp")

X_test, y_test = image_folder_to_dataset(local_path, subfolder="test-data")  
X_train, y_train = image_folder_to_dataset(local_path, subfolder="train-data")  

log.info("🛠️   preparing training data")
TR = OpticalInspectionTransformation(img_size = 224) #, crop = [set_y, set_x, w_size, w_size])
DS_TRAIN = OpticalInspectionDataset(X_train, y_train, sensor = "vision_line", transform = TR.transform)
DL_TRAIN = OpticalInspectionDataloader(DS_TRAIN, log=log, test_split=False)

DS_TEST = OpticalInspectionDataset(X_test, y_test, sensor = "vision_line", transform = TR.transform)
DL_TEST = OpticalInspectionDataloader(DS_TEST, log=log, test_split=False, val_split=False)

DL_TEST.prepare_dataloaders()
DL_TRAIN.prepare_dataloaders()

log.info("✔️   prepared training data")

# TODO: Log sample images to MLFlow
img = DL_TRAIN.show_images(DL_TEST.testloader, n=10)

with experiment_tracker as experiment_tracker:
    experiment_tracker.log_figure(img, file_name="verify_data.png")

    early_stop_callback = EarlyStopping(monitor="val_loss", min_delta=0.00, patience=50, verbose=False, mode="min")
    checkpoint_callback = ModelCheckpoint(dirpath='/tmp/best_after_fit', save_top_k=1, verbose=True, monitor='val_loss', mode='min') # Define a ModelCheckpoint callback to save the best model


    trainer = pl.Trainer(
        max_epochs=N_EPOCHS, 
        accelerator="gpu", 
        devices=1,
        callbacks=[
            early_stop_callback,
            checkpoint_callback
        ],
    )

    log.info("[ ] Starting training")

    trainer.fit(
        model=ResNet18(), 
        train_dataloaders=DL_TRAIN.trainloader, 
        val_dataloaders=DL_TRAIN.valloader, 
    )

    log.info("[x]  Training completed")

    best_model_checkpoint = checkpoint_callback.best_model_path # Load the best mode checkpoint into a variable
    print(best_model_checkpoint)
    loaded_model = ResNet18.load_from_checkpoint(best_model_checkpoint) # Load the best checkpointed model into a variable == uncalibrated model
    loaded_model.eval()    
    
    active_learner = TemperatureScaledActiveLearner(loaded_model, DL_TRAIN)
    al_infer_config = active_learner.get_config(manual_treshold=0.25)
    write_json(al_infer_config, './inference_artifacts/al_infer_config.json')

    log.info("[ ] logging inference artifacts...")
    for file in glob.glob(os.path.join("./inference_artifacts", "*.*")):
        experiment_tracker.log_artifact(file_name = file)
        log.info(f"[x] Logged to mlflow: {file}")

    log_names = ["/tmp/model.pkl","/tmp/transform.pkl"]
    objects = [trainer.model, TR]   
    
    for f_name, obj in zip(log_names, objects):
        experiment_tracker.log_artifact(file_name = f_name, artifact=obj)


    write_dict_to_yaml({"id": f"{experiment_tracker.experiment_id}/{experiment_tracker.run_id}"}, OUT_FILES[0])
