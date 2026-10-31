import torch.nn as nn


class DonkeyNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv24 = nn.Conv2d(3, 24, kernel_size=(5, 5), stride=(2, 2))
        self.conv32 = nn.Conv2d(24, 32, kernel_size=(5, 5), stride=(2, 2))
        self.conv64_5 = nn.Conv2d(32, 64, kernel_size=(5, 5), stride=(2, 2))
        self.conv64_3 = nn.Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1))

        self.fc1 = nn.Linear(64 * 21 * 21, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 2)
        self.relu = nn.ReLU()
        self.flatten = nn.Flatten()

    def forward(self, x):  # 120x160
        x = self.relu(self.conv24(x))  # (224 - 5) / 2 + 1 = 110
        x = self.relu(self.conv32(x))  # (110 - 5) / 2 + 1 = 53
        x = self.relu(self.conv64_5(x))  # (53 - 5) / 2 + 1 = 25
        x = self.relu(self.conv64_3(x))  # 25 - 3 + 1  = 23
        x = self.relu(self.conv64_3(x))  # 23 - 3 + 1  = 21

        x = self.flatten(x)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x


if __name__ == "__main__":
    from torchinfo import summary

    model = DonkeyNet()  # Adjust num_classes as needed
    batch_size = 1
    summary(model, input_size=(batch_size, 3, 224, 224))
