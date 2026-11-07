import threading
from time import time, sleep
from serial import Serial


class ThreadedMessenger:
    def __init__(self, port="/dev/ttyACM0", baudrate=115200) -> None:
        self.communicator = Serial(port=port, baudrate=baudrate, timeout=0.01)
        print(f"Messenger connected at: {self.communicator.name}\n")
        self.out_msg = "s,1500000,1500000\n"
        # self.in_msg = None
        # self.ang_vel_z = 0.0
        self.pico_thread = threading.Thread(target=self.process_msgs, daemon=True)
        self.pico_thread.start()

    def process_msgs(self):
        last_ts = time()
        while self.communicator is not None and self.communicator.is_open:
            # Transmit velocity commands to Pico
            curr_ts = time()
            dt = curr_ts - last_ts
            if dt >= 0.02:  # TX freq: 50 Hz
                # Encode string to bytes and send
                self.communicator.write(self.out_msg.encode("utf-8"))
                last_ts = curr_ts
            # Receive motion data from Pico
            # if self.communicator.in_waiting > 0:
            #     self.in_msg = (
            #         self.communicator.readline().decode("utf-8", "ignore").strip()
            #     )
            #     if self.in_msg:
            #         try:
            #             self.ang_vel_z = float(self.in_msg)
            #         except ValueError:
            #             pass
            sleep(0.01)  # prevent 100% CPU usage


# Component Test
if __name__ == "__main__":
    # SAFETY CHECK
    is_lifted = input("Is anything contacting any wheels of BearCar? (Y/n)")
    while is_lifted != "n":
        print("Please lift BearCar up and remove everything that is making the contact")
        is_lifted = input("Is anything contacting any wheels of BearCar? (Y/n)")
    print("Hold tight! You are about to unleash the beast!")
    print("Verify light order: cyan -> yellow -> green -> blue -> purple -> red")
    for i in reversed(range(3)):
        print(i + 1)
        sleep(1)

    # SETUP
    msngr = ThreadedMessenger()
    modes = ("s", "p", "n", "r", "a", "e")
    pulsewidths = (1_500_000, 1_600_000, 1_400_000)
    sleep(3)  # wait communication to be stablized

    # LOOP
    msngr.out_msg = f"{modes[0]},{pulsewidths[0]},{pulsewidths[0]}\n"
    print("---\nSTANDBY, CYAN, MID, STALL")
    # print(f"In message (ang_vel_z): {msngr.ang_vel_z}")
    print(f"Out message: {msngr.out_msg}")
    sleep(2)
    msngr.out_msg = f"{modes[1]},{pulsewidths[0]},{pulsewidths[0]}\n"
    print("---\nPAUSE, YELLOW, MID, STALL")
    # print(f"In message (ang_vel_z): {msngr.ang_vel_z}")
    print(f"Out message: {msngr.out_msg}")
    sleep(2)
    msngr.out_msg = f"{modes[2]},{pulsewidths[1]},{pulsewidths[1]}\n"
    print("---\nNORMAL, GREEN, RIGHT, FORWARD")
    # print(f"In message (ang_vel_z): {msngr.ang_vel_z}")
    print(f"Out message: {msngr.out_msg}")
    sleep(2)
    msngr.out_msg = f"{modes[3]},{pulsewidths[2]},{pulsewidths[1]}\n"
    print("---\nRECORDING, BLUE, LEFT, FORWARD")
    # print(f"In message (ang_vel_z): {msngr.ang_vel_z}")
    print(f"Out message: {msngr.out_msg}")
    sleep(2)
    msngr.out_msg = f"{modes[4]},{pulsewidths[2]},{pulsewidths[2]}\n"
    print("---\nAUTOPILOT, PURPLE, LEFT, REVERSE")
    # print(f"In message (ang_vel_z): {msngr.ang_vel_z}")
    print(f"Out message: {msngr.out_msg}")
    sleep(2)
    msngr.out_msg = f"{modes[5]},{pulsewidths[0]},{pulsewidths[0]}\n"
    print("---\nERROR, RED, MID, STALL")
    # print(f"In message (ang_vel_z): {msngr.ang_vel_z}")
    print(f"Out message: {msngr.out_msg}")
    sleep(2)
    msngr.communicator.close()
    print(f"Serial Port: {msngr.communicator.name} closed.")
