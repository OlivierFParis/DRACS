import csv
import os
from operator import indexOf
import numpy as np

from computer import ACTIONS
import computer


class Game:
    def __init__(self, cfg, player_1, player_2, training_game = False):
        self.cfg = cfg
        self.turn_max = cfg.max_num_turns
        self.player_1 = player_1
        self.player_2 = player_2
        self.turn_number = 1
        self.history = []
        self.k = cfg.k
        self.winner = None
        self.acc_prediction = 0
        self.innac_prediction = 0
        self.training_game = training_game
        self.loggers = DataLogger(self.cfg)
        self.action_viewer = cfg.action_viewer
        self.start_game()


    # Main game loop
    def start_game(self):
        while True:
            if self.turn_number > self.turn_max:
                if self.action_viewer: print("Out of Time!")
                self.turned_out()
                break
            self.print_round()
            self.round_development()
            if self.call_win(self.check_win()):
                break
            self.turn_number += 1



    # Displays the round number, and the hp and mp of the players
    def print_round(self):
        if self.action_viewer:
            print("Round {}".format(self.turn_number))
            print("There are {} Rounds Left".format(self.turn_max-self.turn_number))
            print("Player 1: {}".format(self.player_1.name))
            print(f"Health Points: {self.player_1.health_points}\nMana Points: {self.player_1.mana_points}\n\n")
            print("Player 2: {}".format(self.player_2.name))
            print(f"Health Points: {self.player_2.health_points}\nMana Points: {self.player_2.mana_points}\n\n")



    def take_action(self):
        """
        Function that calls for each player to make their action, updates the predictive score, updates the models, and calls for recording of the actions if enabled
        :return: The player's action
        """
        # Calls the required functions to construct the input for the AI model
        p1_state = self.player_1.get_state()
        p2_state = self.player_2.get_state()
        current_state = (p1_state[0], p2_state[0], p1_state[1], p2_state[1])
        action_state_window = self.encode_sequence(self.history, current_state).reshape(1, -1)
        reversed_action_state_window = self.loggers.action_state_reversal(action_state_window.copy().flatten().tolist())
        reversed_action_state_window = np.array(reversed_action_state_window, dtype=np.float32).reshape(1, -1)

        # Asks for the player's action
        p1_action = self.player_1.play(reversed_action_state_window, current_state, 0)
        p2_action = self.player_2.play(action_state_window, current_state, 1)

        # If player_2 is an AI model (True unless Players are both human), and if the prediction of the AI model matches or not the action of the player, increase respective count.
        if isinstance(self.player_2, computer.Computer) and self.player_2.predict == p1_action:
            self.acc_prediction += 1 # Accurate prediction
        else:
            self.innac_prediction += 1 # Inaccurate prediction

        # If player_1 or player_2 is an AI model, update the model with new play history
        if isinstance(self.player_1, computer.Computer): self.player_1.model_update(reversed_action_state_window, p2_action-1)
        if isinstance(self.player_2, computer.Computer): self.player_2.model_update(action_state_window, p1_action-1)

        # Stores the player's actions in a list and sends them for recording in a csv file if option to train the GBC model is selected.
        player_actions = [p1_action, p2_action]
        if self.training_game: self.loggers.record(action_state_window.copy(), player_actions.copy())
        self.history_update(player_actions)

        return p1_action, p2_action


    def round_development(self):
        """
        Function that will finalize the outcome of each player's action. Distribute the lost hp and mp for each, such that the actions both occur at the same time, and are independent of one another.
        The function is divided into two types of actions and outcomes. Instant, such as mana, which is subtracted either at call in the player class, or in the match block to subtract from the other player's mana.
        Timed-actions are those whose outcomes are stored in the stats_box. These will all be distributed at the end, and can either store positive (gain) or negative (loss) values.
        :return: Nothing.
        """
        stats_box = [0, 0, 0, 0] # (hp1, hp2, mp1, mp2)
        player_list = (self.player_1, self.player_2)
        action_list = self.take_action()
        player_turn = 0
        for i in action_list:
            match i:
                case 1: # Attack
                    stats_box[(player_turn+1)%2] += -1
                case 2: # Defend
                    if action_list[(player_turn+1)%2] == 1:
                        player_list[(player_turn+1)%2].set_mana_points(-1,2) # Subtracts the opposing player's mana by 1.
                        stats_box[player_turn] += 1 # Adds one hp to current player to negate attack from other player
                case 3: # Rest
                    stats_box[player_turn+2] += 2
                case 4: # Counter
                    if action_list[(player_turn+1)%2] == 1:
                        stats_box[player_turn] += 1
                        stats_box[(player_turn+1)%2] += -1
                case 5: # Steal
                    match action_list[(player_turn+1)%2]:
                        case 1: # Attack
                            stats_box[player_turn] += 1
                            stats_box[(player_turn+1)%2] += -1
                        case 2: # Defend
                            stats_box[((player_turn + 1) % 2) + 2] += -1 # Subtracts one mana point from opponent, in stats_box.
                            if player_list[(player_turn + 1) % 2].get_mana_points() > 0: # If opponent has at least 1 mana point when defending, increase current player's mana by 1.
                                stats_box[player_turn+ 2] += 1
                        case 3: # Rest
                            stats_box[player_turn] += 1
                            stats_box[(player_turn + 1) % 2] += -1
                            stats_box[player_turn + 2] += 1
                            stats_box[((player_turn + 1) % 2) + 2] += -1
                        case 4: # Counter
                            stats_box[player_turn] += 1
                            stats_box[(player_turn + 1) % 2] += -1
                            if player_list[(player_turn + 1) % 2].get_mana_points() > 0: # Since Counter's mana cost is an instant cost, it is subtracted during call in the player class. Thus, the current player cannot steal non-existent mana.
                                stats_box[player_turn + 2] += 1
                                stats_box[((player_turn + 1) % 2) + 2] += -1
                        case 5: # Steal
                            pass # Nothing occurs
            player_turn +=1

        # Distributes the outcome to the players. If the mana value in the stats_box at this moment is in the negative, the player will instead be subtracted a health point.
        self.player_1.set_health_points(stats_box[0])
        self.player_2.set_health_points(stats_box[1])
        self.player_1.set_mana_points(stats_box[2],5)
        self.player_2.set_mana_points(stats_box[3],5)



    def check_win(self):
        """
        Function that checks if the game is over from a player reaching zero hp.
        :return: An integer value corresponding to the winning condition.
        """
        player_life = (self.player_1.health_points, self.player_2.health_points)
        if player_life.__contains__(0):
            if player_life.count(0) == 1:
                dead_player = indexOf(player_life, 0)
                return dead_player
            else:
                return 2
        else:
            return None


    def call_win(self, win_code):
        """
        Function that is called when a player lost or the timer (turn number) reached zero. Results in printing the outcome of the game.
        :param win_code: integer value corresponding to the winning condition.
        :return: Boolean value indicating if there was a win or not.
        """
        if win_code is not None:
            match win_code:
                case 0:
                    if self.action_viewer: print(f"{self.player_2.name} Wins!")
                    if self.action_viewer: print("Game Over\n")
                    self.player_2.save()
                    self.winner = 2
                    if self.training_game: self.loggers.data_GBC_save()
                    return True
                case 1:
                    if self.action_viewer: print(f"{self.player_1.name} Wins!")
                    if self.action_viewer: print("Game Over\n")
                    self.player_2.save()
                    self.winner = 1
                    if self.training_game: self.loggers.data_GBC_save()
                    return True
                case 2:
                    if self.action_viewer: print(f"We have a Tie!")
                    if self.action_viewer: print("Game Over\n")
                    self.player_2.save()
                    self.winner = 0
                    if self.training_game: self.loggers.data_GBC_save()
                    return True
        else:
            return False



    # Function called when the timer for the maximum number of turns reaches zero
    def turned_out(self):
        scores = [0, 0]
        scores[0] = self.player_1.health_points + self.player_1.mana_points*0.75
        scores[1] = self.player_2.health_points + self.player_2.mana_points*0.75
        outcome = 0 if scores[0] < scores[1] else 1 if scores[0] > scores[1] else 2
        self.call_win(outcome)


    
    def encode_sequence(self, history, current_state):
        """
        Function used to encode the current state of the game, and the history window that will be considered for the AI model's prediction.
        :param history: Total action history of the present game, as a list.
        :param current_state: Current state of the player's (i.e., hp and mp).
        :return: New list merging the previous k round's actions, from history, and the current state of the players.
        """
        sequence = history[-self.k:]
        mana_length = self.cfg.max_mana_points+1
        x = np.zeros(10*self.k+2+mana_length*2, dtype=np.float32)
        for i in range(len(sequence)):
            for j in range(len(sequence[i])):
                x[i * 10 + j] = sequence[i][j]
        for z in range(0,2):
            x[10 * self.k + z] = current_state[z]
        for z in range(0,2):
            x[10 * self.k + 2 + z*mana_length + current_state[z+2]] = 1
        return x


    def history_update(self, player_actions): # History is solely for actions
        """
        Function that updates the total history by adding the new actions taken by the player's to the list.
        :param player_actions: The player's actions, denoted as 1 to 5 (Corrected in loop to correspond to cell 0 to 4).
        :return: Nothing.
        """
        data_list = []
        for i in range (0,2): # Actions
            for j in range (0,5):
                data_list.append(1) if player_actions[i]-1 == j else data_list.append(0)
        self.history.append(data_list)


class DataLogger:
    """
    Class DataLogger, which contains the main functions and definitions to generate the csv file used by the GBC model for training.
    """
    def __init__(self, cfg):
        self.k = cfg.k
        self.filename = cfg.data_query()
        self.max_mana_points = cfg.max_mana_points
        ACTIONS
        Actor_Viewer = ["my","opp"]
        self.header = [f"h{i}_{z}_{j}" for i in range(1,self.k+1) for z in Actor_Viewer for j in ACTIONS] + ["my_hp"]+ ["opp_hp"] + [f"{z}_mp{u}" for z in Actor_Viewer for u in range(0,self.max_mana_points+1)] + ["label"]
        self.file_exists = os.path.exists(self.filename)
        self.rows = []


    def record(self, action_state_window, player_moves):
        """
        Function that records the list of the previous k round's actions that have been merged with the current state of the player's (Total information given to the AI models), and adds the label representing the true player's move.
        :param action_state_window: List containing the action history of the previous k rounds and the state of the players.
        :param player_moves: True action taken by the player.
        :return: Nothing.
        """
        list_action_state_window = action_state_window.copy().flatten().tolist()
        action_state_actor_1 = list_action_state_window.copy()
        action_state_actor_2 = self.action_state_reversal(list_action_state_window.copy())
        self.rows.append(action_state_actor_1 + [player_moves[0]])
        self.rows.append(action_state_actor_2 + [player_moves[1]])


    def action_state_reversal(self, action_state_window):
        """
        Function used to reverse the action history and player states to acquire the perspective of the opposing model/player.
        :param action_state_window: List containing the action history of the previous k rounds and the state of the players.
        :return: The reversed action_state_window seen from the opposing perspective.
        """
        rev_action_state_window = []
        move_history = action_state_window[:self.k*10]
        hp_history = action_state_window[self.k*10:self.k*10+2]
        mp_history = action_state_window[self.k*10+2:]

        for i in range(0,len(move_history),10):
            first_half = move_history[i:i+5]
            second_half = move_history[i+5:i+10]
            rev_action_state_window.extend(second_half)
            rev_action_state_window.extend(first_half)
        rev_action_state_window.extend(hp_history[1:])
        rev_action_state_window.extend(hp_history[:1])
        first_mp_half = mp_history[:len(mp_history)//2]
        second_mp_half = mp_history[len(mp_history)//2:]
        rev_action_state_window.extend(second_mp_half)
        rev_action_state_window.extend(first_mp_half)
        return rev_action_state_window


    def data_GBC_save(self):
        """
        Function used to save the data in the csv file.
        :return: Nothing.
        """
        with open(self.filename, "a", newline="") as file:
            writer = csv.writer(file)
            if not self.file_exists:
                writer.writerow(self.header)
            writer.writerows(self.rows)

