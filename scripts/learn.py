from components.custom_archs import create_custom_model

from argparse import ArgumentParser
from pathlib import Path
import shutil

import sys
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import torchvision.models as tvmodels
from torchvision.transforms import v2
from torchvision.io import decode_image
import matplotlib.pyplot as plt


class BearCarDataset(Dataset):
    """
    Customized dataset
    """

    def __init__(self, labels_file_path, img_dir):
        self.labels_df = pd.read_csv(labels_file_path, header=None)
        self.img_dir = img_dir
        self.trans_in = v2.Compose([v2.ToDtype(torch.float32, scale=True)])

    def __len__(self):
        return len(self.labels_df)

    def __getitem__(self, idx):
        img_path = self.img_dir / self.labels_df.iloc[idx, 0]
        image = self.trans_in(decode_image(img_path))
        target_steering = torch.as_tensor(
            self.labels_df.iloc[idx, 1], dtype=torch.float32
        )
        target_throttle = torch.as_tensor(
            self.labels_df.iloc[idx, 2], dtype=torch.float32
        )
        return image, target_steering, target_throttle

def train(dataloader, model, loss_fn, optimizer):
    """
    training function for 1 epoch
    """
    model.train()
    num_used_samples = 0
    ep_loss = 0.0
    for i, (img, st, th) in enumerate(dataloader):
        target = torch.stack((st, th), dim=-1)
        feature, target = img.to(DEVICE), target.to(DEVICE)
        pred = model(feature)
        batch_loss = loss_fn(pred, target)
        optimizer.zero_grad()  # zero previous gradient
        batch_loss.backward()  # back propagation
        optimizer.step()  # update params
        num_used_samples += target.shape[0]
        print(
            f"batch loss: {batch_loss.item()} [{num_used_samples}/{len(dataloader.dataset)}]"
        )
        ep_loss = (ep_loss * i + batch_loss.item()) / (i + 1)
    return ep_loss

def validate(dataloader, model, loss_fn):
    model.eval()
    ep_loss = 0.0
    with torch.no_grad():
        for i, (img, st, th) in enumerate(dataloader):
            target = torch.stack((st, th), dim=-1)
            feature, target = img.to(DEVICE), target.to(DEVICE)
            pred = model(feature)
            batch_loss = loss_fn(pred, target)
            ep_loss = (ep_loss * i + batch_loss.item()) / (i + 1)
    return ep_loss


# SETUP
# Params
BATCH_SIZE = 128
LEARNING_RATE = 1e-4
MAX_EPOCHS = 128
PATIENCE = 5
# Parse arguments
parser = ArgumentParser(description="Autopilot Trainer Configs")
parser.add_argument(
    "--data_dir",
    type=str,
    default=None,
    help="Name or path of the data directory (e.g. 2001-02-03-04-05 or year-month-date-hour-minute)",
)
parser.add_argument(
    "--arch",
    type=str,
    default="mobilenet_v3_small",
    help="Name of the model architecture (e.g., mobilenet_v3_small)",
)
args = parser.parse_args()
# Designate processing unit
DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)
print(f"Using {DEVICE} device")
# Instantiate dataset
data_dir = Path(__file__).resolve().parent.parent / "data" / args.data_dir
annotations_path = data_dir / "labels.csv"
# Split train/val (85:15)
anno_df = pd.read_csv(
    annotations_path,
    header=None,
    names=["image_id", "steering_value", "throttle_value"],
)
val_ids = np.arange(
    int(len(anno_df) / 2) - int(len(anno_df) * 0.075),  # lower bound
    int(len(anno_df) / 2) + int(len(anno_df) * 0.075),  # upper bound
)
val_df = anno_df.iloc[val_ids]
train_df = anno_df.drop(val_ids)
val_df = val_df.reset_index(drop=True)
train_df = train_df.reset_index(drop=True)
print(f"train size: {len(train_df)}, validation size: {len(val_df)}")
# Generate train/val annotation files
anno_train_path = data_dir / "labels_train.csv",
if not anno_train_path.exists():
    train_df.to_csv(
        data_dir / "labels_train.csv",
        index=False,
        header=False,
    )
    print(f"Training annotations file saved: {anno_train_path}")
else:
    print(f"Training annotations file already exists: {anno_train_path}")
anno_val_path = data_dir / "labels_val.csv",
if not anno_val_path.exists():
    val_df.to_csv(
        data_dir / "labels_val.csv",
        index=False,
        header=False,
    )
    print(f"Validation annotations file saved: {anno_val_path}")
else:
    print(f"Validation annotations file already exists: {anno_val_path}")
# Create dataset and dataloader
img_dir = data_dir / "images"
train_set = BearCarDataset(data_dir / "labels_train.csv", img_dir)
val_set = BearCarDataset(data_dir / "labels_val.csv", img_dir)
train_dataloader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True)
val_dataloader = DataLoader(val_set, batch_size=BATCH_SIZE)
# Create directory for saving trained models
model_dir = data_dir / "models" / args.arch
if model_dir.exists() and model_dir.is_dir():
    shutil.rmtree(model_dir)  # TODO: ask input to delete.
    print("Old model directory deleted.")
model_dir.mkdir(parents=True, exist_ok=True)
# Instantiate model and config training
try:
    model_class = getattr(tvmodels, args.arch)
    model = model_class(weights=None, num_classes=2).to(DEVICE)
except AttributeError:
    print(f"{args.arch} is not found in torchvision's model collections.")
    try:
        model = create_custom_model(args.arch)
    except ValueError:
        print(f"{args.arch} is not registered as a custom architecture.")
        sys.exit(1)
# Config model optimizer
optimizer = torch.optim.AdamW(
    params=model.parameters(),
    lr=LEARNING_RATE,
    betas=(0.9, 0.999),
    eps=1e-8,
)
loss_fn = nn.MSELoss()
best_loss = float("inf")  # best loss on validation data
since_best_counter = 0
train_losses = []
val_losses = []


# LOOP
# Optimize model
for ep in range(MAX_EPOCHS):
    print(f"Epoch {ep + 1}\n-------------------------------")
    ep_train_loss = train(train_dataloader, model, loss_fn, optimizer)
    ep_val_loss = validate(val_dataloader, model, loss_fn)
    print(
        f"Epoch {ep + 1} training loss: {ep_train_loss}, validation loss: {ep_val_loss}"
    )
    train_losses.append(ep_train_loss)
    val_losses.append(ep_val_loss)
    model_name = f"ep{ep + 1}-mse{ep_val_loss:.4f}"
    torch.save(model.state_dict(), model_dir / f"{model_name}.pth")
    # Early stopping
    if ep_val_loss < best_loss:
        best_loss = ep_val_loss
        since_best_counter = 0  # Reset counter if validation loss improved
        best_model_path = model_dir / "best_model.pth"
        try:
            best_model_path.unlink()
            print("Last best model file has been deleted successfully.")
        except FileNotFoundError:
            print(f"File '{best_model_path}' not found.")
        except Exception as e:
            print(f"Error occurred while deleting the file: {e}")
        torch.save(model.state_dict(), best_model_path)
        print(f"Best model: {model_name} saved at {best_model_path}")
    else:
        since_best_counter += 1
        print(f"{since_best_counter} epochs since best model")
        if since_best_counter >= PATIENCE:
            print("Early stopping triggered!")
            break
print("Optimize Done!")  # debug
# Graph training process
plt.plot(range(len(train_losses)), train_losses, "b--", label="Training")
plt.plot(range(len(val_losses)), val_losses, "orange", label="Validation")
plt.grid(True)
plt.xlabel("Epoch")
plt.ylabel("MSE Loss")
plt.legend()
plt.title(model_name)
plt.savefig(model_dir / "learning_curve.png")
