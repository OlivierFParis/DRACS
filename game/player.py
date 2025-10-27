
class Player:
    def __init__(self, cfg, name):
        self.cfg = cfg
        self.health_points = cfg.max_health_points
        self.mana_points = cfg.starting_mana_points
        self.name = name

    def play(self, action_state_window, current_state, player_number):
        """
        Function used to ask what the user would like their action to be.
        :param action_state_window: List containing the action history of the previous k rounds and the state of the players. *Not used by player.
        :param current_state: Current state of the player's (i.e., hp and mp). *Not used by player.
        :param player_number: Integer indicating if the player is player 1 (0) or player 2 (1). Not used by player.
        :return: The integer corresponding to the action that the player plays.
        """
        while True:
            try:
                print(f"Your Turn: {self.name}\nWhat would you like to do?\n1. ATTACK\n2. DEFEND\n3. REST\n4. COUNTER\n5. STEAL\n")
                choice_1 = int(input())
                match choice_1:
                    case 1: # Attack
                        return 1
                    case 2: # Defend
                        return 2
                    case 3: # Rest
                        return 3
                    case 4: # Counter
                        if self.mana_points < 1:
                            print("You don't have enough mana points")
                            continue
                        else:
                            self.mana_points -= 1
                            return 4
                    case 5: # Steal
                        if self.mana_points < 3:
                            print("You don't have enough mana points")
                            continue
                        else:
                            self.mana_points -= 3
                            return 5
                    case _:
                        print("Invalid choice")
                        continue
            except ValueError:
                print("Invalid value!")
            except Exception as e:
                print(f"An error occurred: {e}")


    def set_health_points(self, health_points):
        """
        Function to set the player's health points.
        :param health_points: Integer value representing the health points to add, can be positive (gain) or negative (loss).
        :return: Nothing.
        """
        self.health_points += health_points
        if self.health_points > self.cfg.max_health_points:
            self.health_points = self.cfg.max_health_points

    def set_mana_points(self, mana_points, action):
        """
        Function to set the player's mana points.
        :param mana_points: Integer value representing the mana points to add, can be positive (gain) or negative (loss).
        :param action: Whether the action that resulted in the call is due to defense (2) or steal (5).
        :return: Nothing.
        """
        self.mana_points += mana_points
        if self.mana_points > self.cfg.max_mana_points:
            self.mana_points = self.cfg.max_mana_points
        if self.mana_points < 0:
            self.mana_points = 0
            if action == 5: # If the player's mana points are at zero and the action resulting in the change came from a steal, subtract one health point instead.
                self.set_health_points(mana_points)


    def get_mana_points(self):
        return self.mana_points

    def get_state(self):
        return self.health_points, self.mana_points

    def model_update(self):
        pass

    def save(self):
        pass