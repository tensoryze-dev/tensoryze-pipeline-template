import torch
from PIL import Image
from tensoryze_pipelines.modeling import OpticalInspectionTransformation, TensorPILImageConverter
from tensoryze_service.datamodel import TensoryzeEvent

#to be used in inference service
def inference_preprocessing(event: TensoryzeEvent) -> Image.Image:
    data = event.get_data()
    TR = OpticalInspectionTransformation(img_size = 224) #, crop = [set_y, set_x, w_size, w_size])
    data: torch.Tensor = TR.transform(data).unsqueeze(0)
    return TensorPILImageConverter.convert(data)
