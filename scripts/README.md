# Script Usage Instructions

## 1. Data Collection
```console
uv run ~/BearCar/scripts/drive.py
```

> [!TIP]
> Press `L1` to pause or resume driving.
> Press `R1` to start or stop data recording.
> Press `X` to end driving.

Data will be saved at `~/BearCar/data/YYYY-MM-DD-HH-MM/`

**(On RPi)** transfer data to the training server:
```console
rsync -av --partial --progress ~/BearCar/data/YYYY-MM-DD-HH-MM server@192.168.0.14:~/BearCar/data/
```


## 2. Train A Model
**(On Server)** train a model by specify data directory and model architecture
```console
uv run ~/BearCar/scripts/learn.py --data_dir YYYY-MM-DD-HH-MM --arch mobilenet_v3_small
```

**(On Server)** transfer model back to RPi
```console
rsync -av --partial --progress ~/BearCar/data/YYYY-MM-DD-HH-MM/models/mobilenet_v3_small/best_model.pth rpi@192.168.0.101:~/BearCar/models/mobilenet_v3_small/
```

## 3. Deploy Autopilot
**(On RPi)** run the autopilot model by specify its architecture:
```console
uv run ~/BearCar/scripts/drive.py --arch mobilenet_v3_small --model best_model
```
