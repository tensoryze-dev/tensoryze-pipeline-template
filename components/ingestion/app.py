import glob, os, dotenv
from tensoryze_pipelines.io.interfaces import DataLakeInterface
from tensoryze_pipelines.io.datalake.clients import LakeFSClient
from tensoryze_pipelines.io.datalake.ml import MachineLearningDataLakeClient
client = LakeFSClient(interface=DataLakeInterface())
client = MachineLearningDataLakeClient(client)
branches = client.create_train_test_branch(test_ratio=0.25)
