import joblib
import numpy as np
import os
import pandas as pd
import random

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split

from player import Player

ACTIONS = ["Attack","Defend","Rest","Counter","Steal"]


class Computer(Player):
    def __init__(self, health_points, mana_points, name, k = 3, action_viewer = True):
        super().__init__(health_points, mana_points,name)
        self.action_viewer = action_viewer
        self.k = k
        self.clf = None
        self.path = None
        self.classifier_model(self.k)
        self.predict = 1
        self.features = None

    def print_action(self, action):
        if self.action_viewer:
            print(ACTIONS[int(action)-1])

    def classifier_model(self, k = 3):
        match self.name:
            case "AI_RANDOM":
                pass
            case "AI_SIMPLE":
                pass
            case "AI_RANDOM2":
                self.name = "AI_RANDOM"
                self.path = "models\\DRACS_ADPT_model_AIvsAI_TRAINED.pkl"
                if os.path.exists(self.path):
                    self.clf = joblib.load(self.path)
                    if self.action_viewer: print("Model loaded")
                else:
                    self.clf = SGDClassifier(loss="log_loss", random_state=42)
                    X0 = np.zeros((5, 10 * k+10), dtype=np.float32)
                    y0 = np.array([0, 1, 2, 3, 4])
                    self.clf.partial_fit(X0, y0, classes=np.array([0, 1, 2, 3, 4]))
            case "AI_SIMPLE2":
                self.name = "AI_SIMPLE"
                self.path = "models\\DRACS_ADPT_model_AIvsAI_TRAINED.pkl"
                if os.path.exists(self.path):
                    self.clf = joblib.load(self.path)
                    if self.action_viewer: print("Model loaded")
                else:
                    self.clf = SGDClassifier(loss="log_loss", random_state=42)
                    X0 = np.zeros((5, 10 * k+10), dtype=np.float32)
                    y0 = np.array([0, 1, 2, 3, 4])
                    self.clf.partial_fit(X0, y0, classes=np.array([0, 1, 2, 3, 4]))
            case "AI_ADAPTIVE":
                self.path = "models\\DRACS_ADPT_model_AIvsAI_TRAINED.pkl"
                if self.action_viewer: print(self.path)
                if os.path.exists(self.path):
                    self.clf = joblib.load(self.path)
                    if self.action_viewer: print("Model loaded")
                else:
                    self.clf = SGDClassifier(loss="log_loss", random_state=42)
                    X0 = np.zeros((5, 10 * k+10), dtype=np.float32)
                    y0 = np.array([0, 1, 2, 3, 4])
                    self.clf.partial_fit(X0, y0, classes=np.array([0, 1, 2, 3, 4]))
                pass
            case "AI_STRATEGIST":
                pass
            case "AI_GBC":
                self.path = "models\\DRACS_GBC_model_AIvsAI_TRAINED.pkl"
                if os.path.exists(self.path):
                    bundle = joblib.load(self.path)
                    self.clf = bundle["model"]
                    self.feature_cols = bundle["feature_cols"]
                    if self.action_viewer: print("Model loaded")
                else:
                    print("Creating Model. Please wait...")
                    df = pd.read_csv("data\\GBC_Training.csv")
                    FEATURE_COLS = df.columns.drop("label").tolist()
                    X = df[FEATURE_COLS]
                    y = df["label"]

                    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
                    gbc = GradientBoostingClassifier(random_state=42)
                    gbc.fit(X_tr, y_tr)

                    joblib.dump({"model": gbc, "feature_cols": FEATURE_COLS},
                                "models\\DRACS_GBC_model_AIvsAI_TRAINED.pkl")

                    bundle = joblib.load("models\\DRACS_GBC_model_AIvsAI_TRAINED.pkl")
                    self.clf = bundle["model"]
                    self.feature_cols = bundle["feature_cols"]
                    if self.action_viewer: print("Model loaded")


    def play(self, action_state_window, current_state, player_number):
        match self.name:
            case "AI_RANDOM":
                return self.random_action()
            case "AI_SIMPLE":
                return self.simple_action(current_state, player_number)
            case "AI_ADAPTIVE":
                return self.adaptive_action(action_state_window, current_state)
            case "AI_STRATEGIST": #TODO Future RL Algorithm
                pass
            case "AI_GBC":
                return self.gbc_action(action_state_window, current_state, player_number)

        # If error occurs
        return self.random_action()



    def action_cost(self, action):
        if action == 4:
            self.mana_points -= 1
        if action == 5:
            self.mana_points -= 3


    def random_action(self):
        while True:
            try:
                choice_1 = int(random.randint(1, 5))
                if choice_1 == 4:
                    if self.mana_points < 1:
                        continue
                    else:
                        self.action_cost(choice_1)
                if choice_1 == 5:
                    if self.mana_points < 3:
                        continue
                    else:
                        self.action_cost(choice_1)
                self.print_action(choice_1)
                return choice_1
            except ValueError:
                print("Invalid value!")
            except Exception as e:
                print(f"An error occurred: {e}")
        return None


    def adaptive_action(self, action_state_window, current_state):
        if current_state[0] == 0 or current_state[1] == 0:
            raise RuntimeError(f"Was going to calculate when {current_state[0]} or {current_state[1]} is zero\n{current_state}")
        probs = self.clf.predict_proba(action_state_window)[0]

        if current_state[2] < 1:
            probs[3] = 0
            probs[4] = 0
        if current_state[2] != 3:
            probs[4] = 0
        s = probs.sum()
        if s > 0:
            probs /= s
        else:
            return self.random_action()
        pred_action = int(np.argmax(probs)) + 1
        self.predict = pred_action
        return self.decision(pred_action, current_state)


    def simple_action(self, current_state, player_number): # Add a number in parameter that states whether we are calling for player1 or player2
        health_state = current_state[0], current_state[1]
        mana_state = current_state[2], current_state[3]
        if (health_state[player_number%2] == 5 or health_state[player_number%2] == 4 or health_state[player_number%2] == 3) and mana_state[player_number%2] == 0:
            action = [1, 3]
            weight = [45,55]
            selected_action = random.choices(action, weights = weight,k=1)
            self.print_action(selected_action[0])
            return selected_action[0]
        elif (mana_state[player_number%2] == 1 or mana_state[player_number%2] == 2) and health_state[player_number%2] == 1 and mana_state[(player_number+1)%2] == 3:
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
        elif mana_state[player_number%2] == 3:
            self.print_action(5)
            self.action_cost(5)
            return 5
        else:
            action = [1, 3]
            weight = [40,60]
            selected_action = random.choices(action, weights = weight,k=1)
            self.print_action(selected_action[0])
            return selected_action[0]

    def gbc_action(self, action_state_window, current_state, player_number):
        vec = np.asarray(action_state_window, dtype=float).reshape(-1)
        df_input = pd.DataFrame([vec], columns=self.feature_cols)
        probs = self.clf.predict_proba(df_input)[0]

        if current_state[2+player_number] < 1:
            probs[3] = 0
            probs[4] = 0
        if current_state[2+player_number] != 3:
            probs[4] = 0
        s = probs.sum()
        if s > 0:
            probs /= s
        else:
            return self.random_action()
        pred_action = int(np.argmax(probs)) + 1
        self.predict = pred_action
        return self.decision(pred_action, current_state)



    def decision(self, predicted_action, current_state):
        expected_value = -100
        best_action = None
        for i in range(1,6):
            if i == 4 or i == 5:
                if current_state[3] < 1:
                    continue
            if i == 5:
                if current_state[3] != 3:
                    continue
            action_value = self.resolve_turn(current_state, predicted_action, i)
            if expected_value < action_value:
                expected_value = action_value
                best_action = i
        if best_action is None:
            return self.random_action()
        self.print_action(best_action)
        self.action_cost(best_action)
        return best_action


    def resolve_turn(self, current_state, predicted_action, tentative_action):
        stats_outcome = [current_state[0], current_state[1], current_state[2], current_state[3], 0]
        action_list = predicted_action, tentative_action
        player_turn = 0
        for i in action_list:
            match i:
                case 1:  # Attack
                    stats_outcome[(player_turn + 1) % 2] += -1
                case 2:  # Defend
                    if action_list[(player_turn + 1) % 2] == 1:
                        if stats_outcome[(player_turn + 1) % 2] != 0:
                            stats_outcome[(player_turn + 1) % 2] -= 1
                        stats_outcome[player_turn] += 1
                case 3:  # Rest
                    stats_outcome[player_turn + 2] += 2
                case 4:  # Counter
                    stats_outcome[player_turn + 2] -= 1
                    if action_list[(player_turn + 1) % 2] == 1:
                        stats_outcome[player_turn] += 1
                        stats_outcome[(player_turn + 1) % 2] += -1
                case 5:  # Steal
                    stats_outcome[player_turn + 2] -= 3
                    match action_list[(player_turn + 1) % 2]:
                        case 1:  # Attack
                            stats_outcome[player_turn] += 1
                            stats_outcome[(player_turn + 1) % 2] += -1
                        case 2:  # Defend
                            stats_outcome[((player_turn + 1) % 2) + 2] += -1
                            if stats_outcome[(player_turn + 1) % 2+2] >= 0:
                                stats_outcome[player_turn + 2] += 1
                            else:
                                stats_outcome[(player_turn + 1) % 2 + 2] = 0
                                stats_outcome[(player_turn + 1) % 2] -= 1
                        case 3:  # Rest
                            stats_outcome[player_turn] += 1
                            stats_outcome[(player_turn + 1) % 2] += -1
                            stats_outcome[player_turn + 2] += 1
                            stats_outcome[((player_turn + 1) % 2) + 2] += -1
                        case 4:  # Counter
                            stats_outcome[player_turn] += 1
                            stats_outcome[(player_turn + 1) % 2] += -1
                            if stats_outcome[(player_turn + 1) % 2+2] >= 0:
                                stats_outcome[player_turn + 2] += 1
                                stats_outcome[((player_turn + 1) % 2) + 2] += -1
                        case 5:  # Steal
                            pass  # Nothing occurs
            player_turn += 1
        if stats_outcome[0] == 0 and stats_outcome[1] == 0:
            stats_outcome[4] = -1
        elif stats_outcome[0] == 0:
            stats_outcome[4] = 1
        elif stats_outcome[1] == 0:
            stats_outcome[4] = -1
        else:
            stats_outcome[4] = 0
        return self.ev_score(stats_outcome, current_state)



    def ev_score(self, stats_outcome, current_state):
        w_hp = 1.0
        w_mp = 0.25
        w_term = 5.0
        delta_health = [current_state[0] - stats_outcome[0], current_state[1] - stats_outcome[1]]
        delta_mana =  [current_state[2] - stats_outcome[2], current_state[3] - stats_outcome[3]]
        expected_value = w_hp*(delta_health[0]-delta_health[1])+w_mp*(delta_mana[0]-delta_mana[1])+w_term*stats_outcome[4]
        return expected_value

    def model_update(self, action_state_window, p1_action):
        if self.name == "AI_ADAPTIVE":
            self.clf.partial_fit(action_state_window, np.array([p1_action]))


    def save(self): # Once the game is over, saves the ML model
        if self.path is not None and self.clf is not None and self.name != "AI_GBC":
          joblib.dump(self.clf, self.path)


