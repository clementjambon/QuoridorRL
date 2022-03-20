from alphazero import QuoridorRepresentation, QuoridorModel, SelfPlayConfig, TrainingConfig, Trainer, SelfPlayer
from alphazero.quoridor_model import ModelConfig
from environment import QuoridorConfig, QuoridorEnv


class Manager:
    def __init__(
        self,
        device,
        game_config: QuoridorConfig,
        environment: QuoridorEnv,
        representation: QuoridorRepresentation,
        save_dir: str,
        selfplay_config: SelfPlayConfig,
        training_config: TrainingConfig,
        model_config: ModelConfig,
        nb_iterations: int = 20,
        selfplay_history: int = 4,
    ) -> None:

        self.device = device

        self.nb_iterations = nb_iterations
        self.selfplay_history = selfplay_history

        self.game_config = game_config
        self.selfplay_config = selfplay_config
        self.training_config = training_config
        self.model_config = model_config

        self.environment = environment
        self.representation = representation
        self.save_dir = save_dir

        self.models = []
        self.models_path = []
        self.selfplays_path = []

    def iterate(self):

        for i in range(self.nb_iterations):
            print(f"Manager: starting iteration {i}")
            # If it is the first iteration, we need to initialize a model
            # TODO: add upstream model params
            current_model = QuoridorModel(self.device, self.game_config,
                                          self.representation,
                                          self.model_config)
            if i > 0:
                # For now, we are just loading the state_dict of the past model
                current_model.load_state_dict(self.models[i - 1].state_dict())
            current_model = current_model.to(self.device)

            # Perform selfplay
            selfplayer = SelfPlayer(current_model, self.game_config,
                                    self.environment, self.representation,
                                    self.save_dir, self.selfplay_config)
            self.selfplays_path.append(selfplayer.play_games())

            # Train the current network
            nb_available_selfplays = min(len(self.selfplays_path),
                                         self.selfplay_history)
            trainer = Trainer(self.device, current_model,
                              self.selfplays_path[-nb_available_selfplays:],
                              self.save_dir, self.training_config)
            trainer.train()
            self.models_path.append(trainer.save_model())
            self.models.append(current_model)