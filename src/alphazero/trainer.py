import pickle
import os
import torch

import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.optim import Adam
from alphazero.quoridor_model import QuoridorModel


class TrainingConfig:
    def __init__(self,
                 batch_size=32,
                 epochs=100,
                 regularization_param=1e-4,
                 learning_rate=1e-3) -> None:
        self.batch_size = batch_size
        self.epochs = epochs
        self.regularization_param = regularization_param
        self.learning_rate = learning_rate

    def description(self) -> str:
        return f"TrainingConfig: batch_size={self.batch_size}; epochs={self.epochs}; regularization_params={self.regularization_param}; learning_rate={self.learning_rate};"


class GameDataset(Dataset):
    def __init__(self, game_files) -> None:
        super().__init__()
        self.load_games(game_files)

    def load_games(self, game_files):
        self.states = []
        for game_file in game_files:
            with open(game_file, "rb") as handle:
                self.states += pickle.load(handle)

    def __len__(self):
        return len(self.states)

    def __getitem__(self, index):
        return self.states[index]


class Trainer:
    def __init__(self, device, model: QuoridorModel, game_files, dirname: str,
                 training_config: TrainingConfig) -> None:
        self.training_config = training_config

        self.device = device
        self.model = model
        self.batch_size = training_config.batch_size
        self.epochs = training_config.epochs

        self.dirname = dirname

        self.nb_game_files = len(game_files)
        self.game_dataset = GameDataset(game_files)
        self.game_dataloader = DataLoader(self.game_dataset,
                                          batch_size=self.batch_size,
                                          shuffle=True)

        self.optimizer = Adam(
            self.model.parameters(),
            lr=training_config.learning_rate,
            weight_decay=training_config.regularization_param)

    def save_model(self):
        model_path = os.path.join(self.dirname, self.model.to_string() + ".pt")
        torch.save(self.model.state_dict(), model_path)
        return model_path

    def cross_entropy(self, p, q):
        return -torch.sum(p * torch.log(q)) / q.size()[0]

    def train(self):
        print("###################################")
        print("Trainer starting training:")
        print(f"GameDataset: loaded {self.nb_game_files} self-play records")
        print(self.model.description())
        print(self.training_config.description())
        print("###################################")
        # Run for every epochs
        for epoch in range(self.epochs):
            # Turn model in training mode
            self.model.train()

            epoch_loss = 0.0
            epoch_data_size = 0

            for batch_idx, data in enumerate(self.game_dataloader):
                #game_idx = data[0].to(self.device)
                states = data[1].to(self.device)
                search_policies = data[2].to(self.device)
                rewards = data[3].to(self.device).unsqueeze(dim=1)

                # Reset gradient and loss
                self.model.zero_grad()
                loss = 0.0

                # Predict the policy and value
                p, v = self.model(states)
                # Compute the loss
                loss = F.mse_loss(v, rewards) + self.cross_entropy(
                    search_policies, p)

                epoch_loss += loss
                epoch_data_size += states.shape[0]

                loss /= states.shape[0]

                # Back-propagate
                loss.backward()
                self.optimizer.step()

                # if (batch_idx + 1) % 100 == 0:
                #     print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.
                #           format(epoch, epoch_data_size,
                #                  len(self.game_dataloader.dataset),
                #                  100. * batch_idx / len(self.game_dataloader),
                #                  loss.item()))

            epoch_loss /= epoch_data_size

            # Print epoch loss
            # print(
            #     f'Epoch {epoch}/{self.epochs} completed. Train loss: {epoch_loss:.6f}'
            # )
        print(
            f"Trainer: completed training with {self.epochs} epochs, final train loss: {epoch_loss:.6f}"
        )
