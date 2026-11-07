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
rsync -av --partial --progress ~/BearCar/data/<YYYY-MM-DD-HH-MM> <server>@192.168.0.100:~/BearCar/data/
```

> [!TIP]
> - replace `<YYYY-MM-DD-HH-MM>` with actual data directory name, e.g. `2026-12-01-10-09`
> - replace `<server>` with your user name on the server.


## 2. Train A Model
**(On Server)** train a model by specify data directory and model architecture
```console
uv run ~/BearCar/scripts/learn.py --data_dir 2026-12-01-10-09 --arch mobilenet_v3_small
```

**(On Server)** transfer model back to RPi
```console
rsync -av --partial --progress ~/BearCar/data/2026-12-01-10-09/models/mobilenet_v3_small/best_model.pth rpi@192.168.0.<ip>:~/BearCar/models/mobilenet_v3_small/
```

> [!TIP]
> - replace `<ip>` with ip address of your Raspberry Pi, e.g. `102`

## 3. Deploy Autopilot
**(On RPi)** run the autopilot model by specify its architecture:
```console
uv run ~/BearCar/scripts/drive.py --arch mobilenet_v3_small --model best_model
```
