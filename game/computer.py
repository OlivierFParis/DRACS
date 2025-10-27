import joblib
import numpy as np
import os
import pandas as pd
import random
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning, module=r"sklearn\.linear_model") # Warning suppression for overly confident prediction

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split

from player import Player

ACTIONS = ["Attack","Defend","Rest","Counter","Steal"] # List to display the action taken by the AI model


class Computer(Player):
    def __init__(self, cfg, name):
        super().__init__(cfg,name)
        self.action_viewer = cfg.action_viewer
        self.k = cfg.k
        self.clf = None
        self.path = None
        self.classifier_model(self.k)
        self.predict = 0
        self.features = None

    def print_action(self, action):
        """
        Function that prints the actions taken by the AI model.
        :param action: Integer 1 to 5 corresponding to the action taken by the AI model.
        :return: Nothing.
        """
        if self.action_viewer:
            print(ACTIONS[int(action)-1])


    def classifier_model(self, k = 3):
        """
        Function to load the classifier model of the different AI models, or to generate a new model for training or from trained data.
        :param k: History Window k corresponding to the previous rounds taken into consideration. Default is 3. Overwriten by call.
        :return: Nothing.
        """
        match self.name:
            case "RANDOM":
                pass
            case "SIMPLE":
                pass
            case "RANDOM_2": # Used for training purposes
                self.name = "RANDOM"
                self.path = self.cfg.model_query("ADAPTIVE")
                if os.path.exists(self.path):
                    self.clf = joblib.load(self.path)
                    if self.action_viewer: print("Model loaded")
                else:
                    self.clf = SGDClassifier(loss="log_loss", random_state=42)
                    X0 = np.zeros((5, 10 * k+2+(self.cfg.max_mana_points+1)*2), dtype=np.float32)
                    y0 = np.array([0, 1, 2, 3, 4])
                    self.clf.partial_fit(X0, y0, classes=np.array([0, 1, 2, 3, 4]))
            case "SIMPLE_2": # Used for training purposes
                self.name = "SIMPLE"
                self.path = self.cfg.model_query("ADAPTIVE")
                if os.path.exists(self.path):
                    self.clf = joblib.load(self.path)
                    if self.action_viewer: print("Model loaded")
                else:
                    self.clf = SGDClassifier(loss="log_loss", random_state=42)
                    X0 = np.zeros((5, 10 * k+2+(self.cfg.max_mana_points+1)*2), dtype=np.float32)
                    y0 = np.array([0, 1, 2, 3, 4])
                    self.clf.partial_fit(X0, y0, classes=np.array([0, 1, 2, 3, 4]))
            case "ADAPTIVE": # Adaptive model (Stochastic Gradient Classifier)
                self.path = self.cfg.model_query("ADAPTIVE")
                if self.action_viewer: print(self.path)
                if os.path.exists(self.path):
                    self.clf = joblib.load(self.path)
                    if self.action_viewer: print("Model loaded")
                else:
                    self.clf = SGDClassifier(loss="log_loss", random_state=42)
                    X0 = np.zeros((5, 10 * k+2+(self.cfg.max_mana_points+1)*2), dtype=np.float32)
                    y0 = np.array([0, 1, 2, 3, 4])
                    self.clf.partial_fit(X0, y0, classes=np.array([0, 1, 2, 3, 4]))
                pass
            case "STRATEGIST": #TODO Reinforced Learning Algorithm
                pass
            case "GBC": # Gradient Boosting Classifier model
                self.path = self.cfg.model_query("GBC")
                if os.path.exists(self.path):
                    bundle = joblib.load(self.path)
                    self.clf = bundle["model"]
                    self.feature_cols = bundle["feature_cols"]
                    if self.action_viewer: print("Model loaded")
                else: # Creating the model if the model does not exist, but the data does.
                    print("Creating Model. Please wait...")
                    df = pd.read_csv(self.cfg.data_query())
                    FEATURE_COLS = df.columns.drop("label").tolist()
                    X = df[FEATURE_COLS]
                    y = df["label"]

                    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
                    gbc = GradientBoostingClassifier(random_state=42)
                    gbc.fit(X_tr, y_tr)

                    joblib.dump({"model": gbc, "feature_cols": FEATURE_COLS}, self.path)

                    bundle = joblib.load(self.path)

                    self.clf = bundle["model"]
                    self.feature_cols = bundle["feature_cols"]
                    if self.action_viewer: print("Model loaded")


    def play(self, action_state_window, current_state, player_number):
        """
        Function used to direct the respective AI model to their function to acquire an action from the AI model.
        :param action_state_window: List containing the action history of the previous k rounds and the state of the players.
        :param current_state: Current state of the player's (i.e., hp and mp).
        :param player_number: Integer indicating if the player is player 1 (0) or player 2 (1).
        :return: The integer corresponding to the action that the AI model plays, from 1 to 5.
        """
        match self.name:
            case "RANDOM":
                return self.random_action()
            case "SIMPLE":
                return self.simple_action(current_state, player_number)
            case "ADAPTIVE":
                return self.adaptive_action(action_state_window, current_state, player_number)
            case "STRATEGIST": #TODO Future RL Algorithm
                pass
            case "GBC":
                return self.gbc_action(action_state_window, current_state, player_number)

        # If error occurs
        return self.random_action()



    def action_cost(self, action):
        """
        Function to subtract the mana cost of the action taken by the AI model.
        :param action: The integer corresponding to the action that the AI model plays, from 1 to 5.
        :return: Nothing.
        """
        if action == 4: # Counter
            self.mana_points -= 1
        if action == 5: # Steal
            self.mana_points -= 3


    def random_action(self):
        """
        Function for Random AI model.
        :return: The integer corresponding to the action that the AI model plays, from 1 to 5.
        """
        while True:
            try:
                choice_1 = int(random.randint(1, 5))
                if choice_1 == 4:
                    if self.mana_points < 1:
                        continue # Repeats loop
                    else:
                        self.action_cost(choice_1)
                if choice_1 == 5:
                    if self.mana_points < 3:
                        continue # Repeats loop
                    else:
                        self.action_cost(choice_1)
                self.print_action(choice_1) # Calls to have the action displayed
                return choice_1
            except ValueError:
                print("Invalid value!")
            except Exception as e:
                print(f"An error occurred: {e}")
        return None


    def adaptive_action(self, action_state_window, current_state, player_number):
        """
        Function for Adaptive AI model.
        :param action_state_window: List containing the action history of the previous k rounds and the state of the players.
        :param current_state: Current state of the player's (i.e., hp and mp).
        :param player_number: Integer indicating if the player is player 1 (0) or player 2 (1).
        :return: The integer corresponding to the action that the AI model plays, from 1 to 5.
        """
        if current_state[0] == 0 or current_state[1] == 0: # Ensures that the model does not continue to play when the game is over.
            raise RuntimeError(f"Was going to calculate when {current_state[0]} or {current_state[1]} is zero\n{current_state}")
        probs = self.clf.predict_proba(action_state_window)[0] # Probabilities of actions taken by the opponent. With the highest value corresponding to the most likely action to be taken.

        # Masks impossible actions depending on mana state of opponent, such as counter of steal.
        if current_state[3-player_number] < 1:
            probs[3] = 0
            probs[4] = 0
        if current_state[3-player_number] < 3:
            probs[4] = 0

        # Normalizes the probabilities
        s = probs.sum()
        if s > 0:
            probs /= s
        else:
            return self.random_action() # If all probabilities are zero, chooses a random action

        # Takes the most likely predicted action adds 1 to make it an integer from 1 to 5 and sends it to separate function to calculate best action to take.
        pred_action = int(np.argmax(probs)) + 1
        self.predict = pred_action
        return self.decision(pred_action, current_state, player_number)


    def simple_action(self, current_state, player_number):
        """
        Function for Simple AI model. Hardcoded to generate a simplistic rule-based heuristic model.
        :param current_state: Current state of the player's (i.e., hp and mp).
        :param player_number: Integer indicating if the player is player 1 (0) or player 2 (1).
        :return: The integer corresponding to the action that the AI model plays, from 1 to 5.
        """
        health_state = current_state[0], current_state[1]
        mana_state = current_state[2], current_state[3]
        if health_state[player_number%2] >= 3 and mana_state[player_number%2] == 0:
            action = [1, 3]
            weight = [45,55] # Makes the model more likely to rest than attack in this event 45% of the time it will attack, 55% of the time it will rest.
            selected_action = random.choices(action, weights = weight,k=1)
            self.print_action(selected_action[0])
            return selected_action[0]
        elif (mana_state[player_number%2] == 1 or mana_state[player_number%2] == 2) and health_state[player_number%2] == 1 and mana_state[(player_number+1)%2] >= 3:
            self.print_action(2)
            return 2
        elif (mana_state[player_number%2] == 1 or mana_state[player_number%2] == 2) and health_state[player_number%2] == 1 and mana_state[(player_number+1)%2] == 2:
            self.action_cost(4)
            self.print_action(4)
            return 4
        elif mana_state[player_number % 2] == 0 and health_state[(player_number+1)%2] == 1:
            self.print_action(1)
            return 1
        elif mana_state[player_number%2] == 2:
            self.print_action(1)
            return 1
        elif mana_state[player_number%2] == 1:
            self.print_action(3)
            return 3
        elif mana_state[player_number%2] >= 3:
            self.print_action(5)
            self.action_cost(5)
            return 5
        else:
            action = [1, 3]
            weight = [40,60] # Makes the model more likely to rest than attack in this event.
            selected_action = random.choices(action, weights = weight,k=1)
            self.print_action(selected_action[0])
            return selected_action[0]


    def gbc_action(self, action_state_window, current_state, player_number):
        """
        Function for GBC AI model.
        :param action_state_window: List containing the action history of the previous k rounds and the state of the players.
        :param current_state: Current state of the player's (i.e., hp and mp).
        :param player_number: Integer indicating if the player is player 1 (0) or player 2 (1).
        :return: The integer corresponding to the action that the AI model plays, from 1 to 5.
        """
        vec = np.asarray(action_state_window, dtype=float).reshape(-1)
        df_input = pd.DataFrame([vec], columns=self.feature_cols)
        probs = self.clf.predict_proba(df_input)[0]

        if current_state[3-player_number] < 1:
            probs[3] = 0
            probs[4] = 0
        if current_state[3-player_number] < 3:
            probs[4] = 0
        s = probs.sum()
        if s > 0:
            probs /= s
        else:
            return self.random_action()
        pred_action = int(np.argmax(probs)) + 1
        self.predict = pred_action
        return self.decision(pred_action, current_state, player_number)



    def decision(self, predicted_action, current_state, player_number):
        """
        Function to decide on which action the AI model should play. Which will be determined by the best expected value for each possible actions.
        :param predicted_action: Predicted action the opponent is to play, determined by the AI model.
        :param current_state: Current state of the player's (i.e., hp and mp).
        :param player_number: Integer indicating if the player is player 1 (0) or player 2 (1).
        :return: The integer corresponding to the action that the AI model plays, from 1 to 5.
        """
        expected_value = -100 # Initial expected value
        best_action = None # Integer value corresponding to the action the AI model should play.

        for i in range(1,6):
            if i == 4 or i == 5:
                if current_state[2+player_number] < 1: # Masks impossible actions
                    continue
            if i == 5:
                if current_state[2+player_number] < 3: # Masks impossible actions
                    continue
            action_value = self.resolve_turn(current_state, predicted_action, i, player_number)
            if expected_value < action_value:
                expected_value = action_value
                best_action = i

        if best_action is None:
            return self.random_action()

        self.print_action(best_action)
        self.action_cost(best_action)
        return best_action



    def resolve_turn(self, current_state, predicted_action, tentative_action, player_number):
        """
        Function that computes the statistical outcome of each action, in terms of resulting hp and mp for each player. Mirrors round_development function in game.py
        :param current_state: Current state of the player's (i.e., hp and mp).
        :param predicted_action: Predicted action the opponent is to play, determined by the AI model.
        :param tentative_action: Possible action to be taken by the AI model.
        :param player_number: Integer indicating if the player is player 1 (0) or player 2 (1).
        :return: The expected value of the respective possible action to be taken by the AI model.
        """
        stats_outcome = [current_state[0], current_state[1], current_state[2], current_state[3], 0] # List corresponding to the hp and mp of each player and an integer representing whether death of either player occurs.
        action_list = predicted_action, tentative_action # When we target the one commiting the action we use (player_turn + player_number + 1) % 2, if we are targeting the one receiving the outcome then we use (player_turn + player_number) % 2
        player_turn = 0
        for i in action_list:
            match i:
                case 1:  # Attack
                    stats_outcome[(player_turn + player_number) % 2] += -1
                case 2:  # Defend
                    if action_list[(player_turn + 1) % 2] == 1:
                        if stats_outcome[(player_turn + player_number) % 2 + 2] > 0:
                            stats_outcome[(player_turn + player_number) % 2 + 2] -= 1
                        stats_outcome[(player_turn + player_number + 1) % 2] += 1
                case 3:  # Rest
                    stats_outcome[(player_turn + player_number + 1) % 2 + 2] += 2
                case 4:  # Counter
                    stats_outcome[(player_turn + player_number + 1) % 2 + 2] -= 1
                    if action_list[(player_turn + 1) % 2] == 1:
                        stats_outcome[(player_turn + player_number + 1) % 2] += 1
                        stats_outcome[(player_turn + player_number) % 2] += -1
                case 5:  # Steal
                    stats_outcome[(player_turn + player_number + 1) % 2 + 2] -= 3
                    match action_list[(player_turn + 1) % 2]:
                        case 1:  # Attack
                            stats_outcome[(player_turn + player_number + 1) % 2] += 1
                            stats_outcome[(player_turn + player_number) % 2] += -1
                        case 2:  # Defend
                            stats_outcome[(player_turn + player_number) % 2 + 2] += -1
                            if stats_outcome[(player_turn + player_number) % 2+2] >= 0:
                                stats_outcome[(player_turn + player_number+1) % 2 + 2] += 1
                            else:
                                stats_outcome[(player_turn + player_number) % 2 + 2] = 0
                                stats_outcome[(player_turn + player_number) % 2] -= 1
                        case 3:  # Rest
                            stats_outcome[(player_turn + player_number + 1) % 2] += 1
                            stats_outcome[(player_turn + player_number) % 2] += -1
                            stats_outcome[(player_turn + player_number+1) % 2 + 2] += 1
                            stats_outcome[(player_turn + player_number) % 2 + 2] += -1
                        case 4:  # Counter
                            stats_outcome[(player_turn + player_number + 1) % 2] += 1
                            stats_outcome[(player_turn + player_number) % 2] += -1
                            if stats_outcome[(player_turn + player_number) % 2 + 2] >= 0:
                                stats_outcome[(player_turn + player_number + 1) % 2 + 2] += 1
                                if stats_outcome[(player_turn + player_number) % 2 + 2] > 0:
                                    stats_outcome[((player_turn + player_number) % 2) + 2] += -1
                        case 5:  # Steal
                            pass  # Nothing occurs
            player_turn += 1

        if stats_outcome[0] == 0 and stats_outcome[1] == 0:
            stats_outcome[4] = -1
        elif stats_outcome[1-player_number] == 0:
            stats_outcome[4] = 1
        elif stats_outcome[0+player_number] == 0:
            stats_outcome[4] = -1
        else:
            stats_outcome[4] = 0
        return self.ev_score(stats_outcome, current_state, player_number)



    def ev_score(self, stats_outcome, current_state, player_number):
        """
        Function to calculate the expected value each action would result in, based on a simplistic formula.
        :param stats_outcome: The list of changes incurred by the players based on the selected action from the AI model.
        :param current_state: Current state of the player's (i.e., hp and mp).
        :param player_number: Integer indicating if the player is player 1 (0) or player 2 (1).
        :return: A score dictating the expected value of the possible action.
        """
        w_hp = 1.0
        w_mp = 0.25
        w_term = 5.0
        delta_health = [current_state[0] - stats_outcome[0], current_state[1] - stats_outcome[1]]
        delta_mana =  [current_state[2] - stats_outcome[2], current_state[3] - stats_outcome[3]]
        expected_value = w_hp*(delta_health[1-player_number]-delta_health[0+player_number])+w_mp*(delta_mana[1-player_number]-delta_mana[0+player_number])+w_term*stats_outcome[4]
        return expected_value


    def model_update(self, action_state_window, true_action):
        """
        Function to update the online model (Stochastic Gradient Classifier)
        :param action_state_window: List containing the action history of the previous k rounds and the state of the players.
        :param true_action: The actual action taken by the opposing player.
        :return: Nothing.
        """
        if self.name == "ADAPTIVE":
            self.clf.partial_fit(action_state_window, np.array([true_action]))


    def save(self): # Once the game is over, saves the ML model
        if self.path is not None and self.clf is not None and self.name != "GBC":
            joblib.dump(self.clf, self.path)

