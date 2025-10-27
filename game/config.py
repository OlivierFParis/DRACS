from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    # Core settings
    k: int = 3
    max_health_points: int = 5
    max_mana_points: int = 3
    max_num_turns: int = 20
    starting_mana_points: int = 0

    # View actions
    action_viewer: bool = True

    # Paths
    models_dir: Path = Path("models")
    data_dir: Path = Path("data")


    def model_sig(self):
        """
        Function that defines the specific formatting in which the models are signed as.
        :return: The proper formatting for the different models and the current configurations.
        """
        return f"K{self.k}_HP{self.max_health_points}_MP{self.max_mana_points}"


    def model_query(self, model_name):
        """
        Function that makes the proper model query depending on the model name and the model signature.
        :param model_name: The core name of the model.
        :return: The proper string to query the model's existence.
        """
        return self.models_dir / f"DRACS_{model_name}_MODEL_{self.model_sig()}.pkl"


    def query_existence(self, model_name):
        """
        Function that queries the model's existence in the models' directory.
        :param model_name: The core name of the model.
        :return: Boolean indicating whether the model exists or not. Or in the case of GBC, if the data set for its training exists or not.
        """
        if model_name == "GBC":
            return self.model_query("GBC").exists() or self.data_set_existence()
        else:
            return self.model_query(model_name).exists()


    def data_set_existence(self):
        """
        Function that checks if the data set exists.
        :return: Boolean indicating whether the data set for GBC training exists or not.
        """
        return self.data_query().exists()


    def data_query(self):
        """
        Function that makes the proper data query depending on the data set directory and model signature.
        :return: The proper string to query the data set's existence.
        """
        return self.data_dir / f"GBC_Training_{self.model_sig()}.csv"


    def print_config(self):
        """
        Print the current parameters of the game.
        :return: Nothing.
        """
        print(f"Current Parameters:\n 1. Health Point: {self.max_health_points}\n 2. Max Mana Point: {self.max_mana_points}\n 3. Number of Turns: {self.max_num_turns}\n 4. History Window: {self.k}\n")


    def set_config(self, **kwargs):
        """
        Change the current parameters of the game.
        :param kwargs: Parameters to be changed.
        :return: Nothing.
        """
        for k, v in kwargs.items():
            setattr(self, k, v)





class UserRefusedTraining(Exception):
    """
    Exception raised when the user refuses to proceed with training of the models.
    Propagates back to start_screen() where the user can then decide on what following actions to take.
    """
    def __init__(self, message):
        super().__init__(message)



