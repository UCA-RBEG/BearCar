# BearCar

![bearcar_portrait](https://uca-rbeg.github.io/bearcar_docs/images/bearcar_annotate.png)

BearCar is an educational/recreational autonomous driving platform based on an 1:16 RC car.
Visit [documentations](https://uca-rbeg.github.io/bearcar_docs/) for more details.

> [!IMPORTANT]
> This project is strongly inspired by the
[DonkeyCar](https://github.com/autorope/donkeycar) project.

## Quick Start

### Download BearCar software

```bash
cd ~
git clone https://github.com/UCAEngineeringPhysics/BearCar.git
```

### Install [uv](https://docs.astral.sh/uv/getting-started/installation/) Python Package Manager
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
grep -qF 'eval "$(uv generate-shell-completion bash)"' "$HOME/.bashrc" || echo 'eval "$(uv generate-shell-completion bash)"' >>"$HOME/.bashrc"
```

### Setup Environment

```bash
cd ~/BearCar
./setup_env.sh
```

### Hook Up the Gamepad

Plug in USB receiver or connect via bluetooth.
> [!TIP]
> PS4 controller

### Have Fun Driving

```bash
cd ~/BearCar
uv run scripts/drive.py
```

## Demo Videos

- [Initial BearCar](https://youtube.com/shorts/Kcm6qQqev3s)
- [Another Autopilot](https://youtu.be/8GX6HnfgrJQ)
