from json import load
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from datetime import datetime
import uuid

from alphazero import QuoridorRepresentation
from environment import QuoridorConfig


class ModelConfig:
    def __init__(
        self,
        nb_residual_blocks=9,
        nb_filters=64,
        kernel_size=3,
        stride=1,
    ) -> None:
        self.nb_residual_blocks = nb_residual_blocks
        self.nb_filters = nb_filters
        self.kernel_size = kernel_size
        self.stride = stride

    def description(self) -> str:
        return f"ModelConfig: nb_residual_blocks={self.nb_residual_blocks}; nb_filters={self.nb_filters}; kernel_size={self.kernel_size}; stride={self.stride};"


class ResidualBlock(nn.Module):
    def __init__(self, nb_filters: int, kernel_size: int, stride: int) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(nb_filters,
                               nb_filters,
                               kernel_size=kernel_size,
                               stride=stride,
                               padding="same")
        self.bn1 = nn.BatchNorm2d(nb_filters)
        self.conv2 = nn.Conv2d(nb_filters,
                               nb_filters,
                               kernel_size=kernel_size,
                               stride=stride,
                               padding="same")
        self.bn2 = nn.BatchNorm2d(nb_filters)

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


class FlatPolicyHead(nn.Module):
    def __init__(self, nb_filters: int, grid_size: int,
                 nb_actions: int) -> None:
        super().__init__()
        self.grid_size = grid_size

        # TODO: use something else than a flat distribution
        self.policy_conv = nn.Conv2d(nb_filters,
                                     2,
                                     kernel_size=1,
                                     stride=1,
                                     padding="same")
        self.policy_bn = nn.BatchNorm2d(2)
        self.policy_output = nn.Linear(2 * self.grid_size * self.grid_size,
                                       nb_actions)
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x: Tensor) -> Tensor:
        # Policy head
        p = self.policy_conv(x)
        p = self.policy_bn(p)
        p = F.relu(p)
        # Flatten the output
        p = p.view(-1, 2 * self.grid_size * self.grid_size)
        p = self.policy_output(p)
        p = self.softmax(p)

        return p


class SquarePolicyHead(nn.Module):
    def __init__(self) -> None:
        super().__init__()


class ValueHead(nn.Module):
    def __init__(self, nb_filters: int, grid_size: int) -> None:
        super().__init__()
        self.grid_size = grid_size

        self.value_conv = nn.Conv2d(nb_filters,
                                    1,
                                    kernel_size=1,
                                    stride=1,
                                    padding="same")
        self.value_bn = nn.BatchNorm2d(1)
        self.value_fc1 = nn.Linear(grid_size * grid_size, 256)
        self.value_fc2 = nn.Linear(256, 1)

    def forward(self, x: Tensor) -> Tensor:
        v = self.value_conv(x)
        v = self.value_bn(v)
        v = F.relu(v)
        # Flatten the ouptput
        v = v.view(-1, self.grid_size * self.grid_size)
        v = self.value_fc1(v)
        v = F.relu(v)
        v = self.value_fc2(v)
        # Make sure values stay in [-1, 1]
        v = torch.tanh(v)
        return v


class QuoridorModel(nn.Module):
    def __init__(self,
                 device,
                 game_config: QuoridorConfig,
                 representation: QuoridorRepresentation,
                 model_config: ModelConfig,
                 load_dir: str = None) -> None:
        super().__init__()

        self.device = device

        self.grid_size = game_config.grid_size
        self.nb_residual_blocks = model_config.nb_residual_blocks
        self.nb_filters = model_config.nb_filters
        self.kernel_size = model_config.kernel_size
        self.stride = model_config.stride

        self.nb_channels = representation.time_consistency * representation.nb_features + representation.nb_constants

        # NOTE: padding is applied to keep the same dimensions everywhere

        # Input
        self.conv1 = nn.Conv2d(in_channels=self.nb_channels,
                               out_channels=self.nb_filters,
                               kernel_size=self.kernel_size,
                               stride=self.stride,
                               padding="same")
        self.bn1 = nn.BatchNorm2d(self.nb_filters)

        # Residual tower
        self.residual_blocks = nn.ModuleList([
            ResidualBlock(self.nb_filters, self.kernel_size, self.stride)
            for _ in range(self.nb_residual_blocks)
        ])

        # Policy head (the output is now (grid_size-1)x(grid_size-1)x2 for walls and grid_sizexgrid_size for pawn moves)
        self.policy_head = FlatPolicyHead(self.nb_filters, self.grid_size,
                                          game_config.nb_actions)

        # Value head
        self.value_head = ValueHead(self.nb_filters, self.grid_size)

        # Meta data
        self.id = uuid.uuid1()
        self.creation_time = datetime.now()

        # If provided load the model data
        if load_dir is not None:
            self.load_model(load_dir)

    def forward(self, x: Tensor):

        x.to(self.device)
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)

        for residual_block in self.residual_blocks:
            x = residual_block(x)

        # Policy head
        p = self.policy_head(x)

        # Value head
        v = self.value_head(x)

        return p, v

    def description(self) -> str:
        return f"Model: residual blocks={self.nb_residual_blocks}; filters={self.nb_filters}"

    def to_string(self, uuid_based=False):
        model_str = ""
        if uuid_based:
            model_str += self.id
        else:
            model_str += self.creation_time.strftime("%d-%m-%Y-%H-%M-%S")
        model_str += f"-r{self.nb_residual_blocks}-f{self.nb_filters}"
        return model_str

    def load_model(self, load_dir: str):
        self.load_state_dict(torch.load(load_dir))
        self.eval()
