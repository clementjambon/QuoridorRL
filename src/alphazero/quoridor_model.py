import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor


class ResidualBlock(nn.Module):

    def __init__(self, nb_filters: int, kernel_size: int, stride: int) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(nb_filters,
                               nb_filters,
                               kernel_size=kernel_size,
                               stride=stride,
                               padding="same")
        self.bn1 = nn.BatchNorm2d
        self.conv2 = nn.Conv2d(nb_filters,
                               nb_filters,
                               kernel_size=kernel_size,
                               stride=stride,
                               padding="same")
        self.bn2 = nn.BatchNorm2d

    def forward(self, x: Tensor):
        old_x = x

        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x += old_x
        x = F.relu(x)

        return x


class QuoridorModel(nn.Module):

    def __init__(self,
                 grid_size=9,
                 feature_planes=2,
                 time_consistency=8,
                 constant_planes=1,
                 nb_residual_blocks=9,
                 nb_filters=256,
                 kernel_size=3,
                 stride=1) -> None:
        super().__init__()
        self.grid_size = grid_size
        self.nb_residual_blocks = nb_residual_blocks

        self.nb_channels = time_consistency * feature_planes + constant_planes

        # NOTE: padding is applied to keep the same dimensions everywhere

        # Input
        self.conv1 = nn.Conv2d(in_channels=self.nb_channels,
                               out_channels=nb_filters,
                               kernel_size=kernel_size,
                               stride=stride)
        self.bn1 = nn.BatchNorm2d

        # Residual tower
        self.residual_blocks = [
            ResidualBlock(nb_filters, kernel_size, stride)
            for _ in range(self.nb_residual_blocks)
        ]

        # Policy head (the output is now (grid_size-1)x(grid_size-1)x2 for walls and grid_sizexgrid_size for pawn moves)
        self.policy_dist_size = self.grid_size * self.grid_size(
            self.grid_size - 1) * (self.grid_size - 1) * 2
        # TODO: use something else than a flat distribution
        self.policy_conv = nn.Conv2d(nb_filters,
                                     2,
                                     kernel_size=1,
                                     stride=1,
                                     padding="same")
        self.policy_bn = nn.BatchNorm2d
        self.policy_output = nn.Linear(2 * self.grid_size * self.grid_size,
                                       self.policy_dist_size)

        # Value head
        self.value_conv = nn.Conv2d(nb_filters,
                                    1,
                                    kernel_size=1,
                                    stride=1,
                                    padding="same")
        self.value_bn = nn.BatchNorm2d
        self.value_fc1 = nn.Linear(self.grid_size * self.grid_size, 256)
        self.value_fc2 = nn.Linear(256, 1)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)

        for residual_block in self.residual_blocks:
            x = residual_block(x)

        # Policy head
        p = self.policy_conv(x)
        p = self.policy_bn(p)
        p = F.relu(p)
        # Flatten the output
        p = p.view(-1, 2 * self.grid_size * self.grid_size)
        p = self.policy_output(p)
        p = F.softmax(p)

        # Value head
        v = self.value_conv(x)
        v = self.value_bn(v)
        v = F.relu(v)
        # Flatten the ouptput
        v = v.view(-1, self.grid_size * self.grid_size)
        v = self.value_fc1(v)
        v = F.relu(v)
        v = self.value_fc2(v)
        # Make sure values stay in [-1, 1]
        v = F.tanh(v)

        return p, v
