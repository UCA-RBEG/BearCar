from pathlib import Path
import json
from time import sleep, time
import cv2 as cv
import torch

from components.camera import ThreadedCamera
from components.messenger import ThreadedMessenger
from components.driver import Driver
from components.autopilot_architectures.bearnet import BearNet


# SAFETY CHECK
is_tangled = input("Observe BearCar closely! Any wheels get entangled? (Y/n)")
while is_tangled != "n":
    print("Please decouple the wires from BearCar's wheels!")
    is_tangled = input("Observe BearCar closely! Any wheels get entangled? (Y/n)")
print("!!!\nAUTOPILOT ON DUTY\n!!!")


# SETUP
# Load configs
params_file_path = Path(__file__).parents[1].joinpath("components", "configs.json")
with open(params_file_path, "r") as file:
    params = json.load(file)
# Load autopilot model
model = BearNet()
model_path = Path(__file__).parents[2].joinpath("models", "dummy_pilot")
model.load_state_dict(
    torch.load(
        model_path,
        weights_only=True,
        map_location=torch.device("cpu"),
    )
)
model.eval()  # freeze weights
# Init components
picam = ThreadedCamera(params=params)
messenger = ThreadedMessenger(port="/dev/ttyACM0", baudrate=115200)
driver = Driver(joy_id=0, autopilot_model=model)

# LOOP
try:
    frame_counts = 0
    start_time = time()
    while not driver.is_terminated:
        frame = picam.read()
        frame_counts += 1
        mode, st_val, th_val, st_pw, th_pw = driver.process_event(params, frame=frame)
        messenger.out_msg = f"{mode},{st_pw},{th_pw}\n"
        if not frame_counts % params["frame_rate"]:
            elapsed = time() - start_time
            fps = params["frame_rate"] / elapsed
            print("---")
            print(f"Processing at {fps:.2f} FPS | Frame shape: {frame.shape}")
            print(f"steering value: {st_val}, throttle_value: {th_val}")
            # print(f"In message (ang_vel_z): {messenger.ang_vel_z}")
            print("Out message: " + messenger.out_msg)
            start_time = time()
        cv.imshow("Camera", cv.flip(frame, -1))  # picam mounted upside down
        if cv.waitKey(1) == ord("q"):  # [q]uit
            print("Quit signal received.")
            break
        sleep(1 / params["frame_rate"])
except KeyboardInterrupt:
    print("\nShutdown signal received.")
finally:
    picam.stop()
