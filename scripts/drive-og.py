import argparse
from pathlib import Path
from time import sleep, time
from datetime import datetime
import csv
import json
import cv2 as cv
import torch

from components.autopilot_architectures.bearnet import BearNet
from components.camera import ThreadedCamera
from components.messenger import ThreadedMessenger
from components.driver import Driver

# SAFETY CHECK

# SETUP
# Parse arguments
parser = argparse.ArgumentParser(description="BearCar Driver Selection")
parser.add_argument(
    "--model",
    type=str,
    default=None,
    help="Name or path of the autopilot model to load",
)
args = parser.parse_args()
# Define paths
bc_dir = Path(__file__).parents[1]
data_dir = bc_dir.joinpath("data")
image_dir = str(data_dir.joinpath(datetime.now().strftime("%Y-%m-%d-%H-%M"), "images"))
Path(image_dir).mkdir(parents=True, exist_ok=True)
label_path = str(Path(image_dir).parent.joinpath("labels.csv"))
# Load configs
params_file_path = bc_dir.joinpath("scripts", "components", "configs.json")
with open(params_file_path, "r") as file:
    params = json.load(file)
# Load autopilot model if provided
autopilot = None
if args.model:
    model_path = bc_dir.joinpath("models", args.model + ".pth")
    autopilot = BearNet()
    autopilot.load_state_dict(
        torch.load(
            model_path,
            weights_only=True,
            map_location=torch.device("cpu"),
        )
    )
    autopilot.eval()  # freeze weights
    print("!!!\nAUTOPILOT ON DUTY\n!!!")
else:
    print("~~~\nGet ready, Human!\n~~~")
print("Place BearCar on the ground and enjoy your ride...\n")
sleep(1)  # Let the driver be ready
# Init components
picam = ThreadedCamera(params=params)
messenger = ThreadedMessenger(port="/dev/ttyACM0", baudrate=115200)
driver = Driver(joy_id=0, autopilot_model=autopilot)
# Adjust control rate
if args.model:
    drive_rate = params["frame_rate"]
else:
    drive_rate = int(params["frame_rate"] / 2)


# LOOP
try:
    frame_counts = 0
    record_counts = 0
    start_time = time()
    while not driver.is_terminated:
        frame = picam.read()
        frame_counts += 1
        mode, st_val, th_val, st_pw, th_pw = driver.process_event(params, frame=frame)
        messenger.out_msg = f"{mode},{st_pw},{th_pw}\n"
        action = [st_val, th_val]
        if mode == "r":
            cv.imwrite(image_dir + "/" + str(frame_counts) + ".jpg", frame)
            label = [str(frame_counts) + ".jpg"] + action
            with open(label_path, "a+", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(label)
            record_counts += 1
            # print(f"recorded frame counts: {record_counts}")  # debug
            if record_counts == params["record_cap"]:  # pause recording if max reached
                driver.mode = "p"
                driver.is_paused = True
                driver.is_recording = False
        # For debugging, uncomment following lines
        if not frame_counts % drive_rate:
            elapsed = time() - start_time
            fps = drive_rate / elapsed
            print("---")
            print(f"steering value: {st_val}, throttle value: {th_val}")
            print(f"Out message: {messenger.out_msg}")
            print(f"In message (ang_vel_z): {messenger.ang_vel_z}")
            print(f"Processing at {fps:.2f} FPS | Frame shape: {frame.shape}")
            start_time = time()
        # cv.imshow("Camera", cv.flip(frame, -1))  # picam mounted upside down
        # if cv.waitKey(1) == ord("q"):  # [q]uit
        #     print("Quit signal received.")
        #     break
        sleep(1 / drive_rate)  # see configs.json for FPS
except KeyboardInterrupt:
    print("\nShutdown signal received.")
finally:
    picam.stop()
