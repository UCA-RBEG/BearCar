from pathlib import Path
import torch
from torchvision import models
from torchinfo import summary


model = models.mobilenet_v3_small(weights=None, num_classes=2)
batch_size = 1
summary(model, input_size=(batch_size, 3, 224, 224))

model_path = Path(__file__).parents[2].joinpath("models", "best_model.pth")
model.load_state_dict(
    torch.load(
        model_path,
        weights_only=True,
        map_location=torch.device("cpu"),
    )
)
model.eval()  # freeze weights
