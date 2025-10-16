import csv
import os
from operator import indexOf
import numpy as np

from computer import ACTIONS
import computer


class Game:
    def __init__(self, turn_max, player_1, player_2, k = 3, training_game = False, action_viewer = True):
        self.turn_max = turn_max
        self.player_1 = player_1
        self.player_2 = player_2
        self.turn_number = 1
        self.history = []
        self.k = k
        self.winner = None
        self.acc_prediction = 0
        self.innac_prediction = 0
        self.training_game = training_game
        self.loggers = DataLogger() if self.training_game else None
        self.action_viewer = action_viewer
        self.start_game()


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


    def print_round(self):
        if self.action_viewer:
            print("Round {}".format(self.turn_number))
            print("There are {} Rounds Left".format(self.turn_max-self.turn_number))
            print("Player 1: {}".format(self.player_1.name))
            print(f"Health Points: {self.player_1.health_points}\nMana Points: {self.player_1.mana_points}\n\n")
            print("Player 2: {}".format(self.player_2.name))
            print(f"Health Points: {self.player_2.health_points}\nMana Points: {self.player_2.mana_points}\n\n")


    def take_action(self):
        p1_state = self.player_1.get_state()
        p2_state = self.player_2.get_state()
        current_state = (p1_state[0], p2_state[0], p1_state[1], p2_state[1])
        action_state_window = self.encode_sequence(self.history, current_state).reshape(1, -1)
        p1_action = self.player_1.play(action_state_window, current_state, 0)
        p2_action = self.player_2.play(action_state_window, current_state, 1)
        if isinstance(self.player_2, computer.Computer) and self.player_2.predict == p1_action:
            self.acc_prediction += 1
        else:
            self.innac_prediction += 1
        if isinstance(self.player_2, computer.Computer): self.player_2.model_update(action_state_window, p1_action-1)

        player_actions = [p1_action, p2_action]
        if self.training_game: self.loggers.record(action_state_window.copy(), player_actions.copy())
        self.history_update(player_actions)
        return p1_action, p2_action


    def round_development(self):
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
                        player_list[(player_turn+1)%2].set_mana_points(-1,2)
                        stats_box[player_turn] += 1
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
                            stats_box[((player_turn + 1) % 2) + 2] += -1
                            if player_list[(player_turn + 1) % 2].get_mana_points() > 0:
                                stats_box[player_turn+ 2] += 1
                        case 3: # Rest
                            stats_box[player_turn] += 1
                            stats_box[(player_turn + 1) % 2] += -1
                            stats_box[player_turn + 2] += 1
                            stats_box[((player_turn + 1) % 2) + 2] += -1
                        case 4: # Counter
                            stats_box[player_turn] += 1
                            stats_box[(player_turn + 1) % 2] += -1
                            if player_list[(player_turn + 1) % 2].get_mana_points() > 0:
                                stats_box[player_turn + 2] += 1
                                stats_box[((player_turn + 1) % 2) + 2] += -1
                        case 5: # Steal
                            pass # Nothing occurs
            player_turn +=1
        self.player_1.set_health_points(stats_box[0])
        self.player_2.set_health_points(stats_box[1])
        self.player_1.set_mana_points(stats_box[2],5)
        self.player_2.set_mana_points(stats_box[3],5)


    def check_win(self):
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


    def turned_out(self):
        scores = [0, 0]
        scores[0] = self.player_1.health_points + self.player_1.mana_points*0.75
        scores[1] = self.player_2.health_points + self.player_2.mana_points*0.75
        outcome = 0 if scores[0] < scores[1] else 1 if scores[0] > scores[1] else 2
        self.call_win(outcome)


    def encode_sequence(self, history, current_state, k = 3):
        sequence = history[-k:]
        x = np.zeros(10*k+10, dtype=np.float32)
        for i in range(len(sequence)):
            for j in range(len(sequence[i])):
                x[i * 10 + j] = sequence[i][j]
        for z in range(0,2):
            x[10 * k + z] = current_state[z]
        for z in range(0,2):
            x[10 * k + 2 + z*4 + current_state[z+2]] = 1
        return x


    def history_update(self, player_actions): # History is solely for actions
        data_list = []
        for i in range (0,2): # Actions
            for j in range (0,5):
                data_list.append(1) if player_actions[i]-1 == j else data_list.append(0)
        self.history.append(data_list)


class DataLogger:
    def __init__(self, filename = "data\\GBC_Training.csv", k=3):
        self.filename = filename
        self.k = k
        ACTIONS
        Actor_Viewer = ["my","opp"]
        self.header = [f"h{i}_{z}_{j}" for i in range(1,self.k+1) for z in Actor_Viewer for j in ACTIONS] + ["my_hp"]+ ["opp_hp"] + [f"{z}_mp{u}" for z in Actor_Viewer for u in range(0,4)] + ["label"]
        self.file_exists = os.path.exists(self.filename)
        self.rows = []

    def record(self, action_state_window, player_moves):
        list_action_state_window = action_state_window.copy().flatten().tolist()
        action_state_actor_1 = list_action_state_window.copy()
        action_state_actor_2 = self.action_state_reversal(list_action_state_window.copy())
        self.rows.append(action_state_actor_1 + [player_moves[0]])
        self.rows.append(action_state_actor_2 + [player_moves[1]])

    def action_state_reversal(self, action_state_window):
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
        with open(self.filename, "a", newline="") as file:
            writer = csv.writer(file)
            if not self.file_exists:
                writer.writerow(self.header)
            writer.writerows(self.rows)

