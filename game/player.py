class Player:
    def __init__(self, health_points, mana_points, name):
        self.health_points = health_points
        self.mana_points = mana_points
        self.name = name

    def play(self, action_state_window, current_state, player_number):
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
        self.health_points += health_points
        if self.health_points > 5:
            self.health_points = 5

    def set_mana_points(self, mana_points, action):
        self.mana_points += mana_points
        if self.mana_points > 3:
            self.mana_points = 3
        if self.mana_points < 0:
            self.mana_points = 0
            if action == 5:
                self.set_health_points(mana_points)

    def get_mana_points(self):
        return self.mana_points

    def get_state(self):
        return self.health_points, self.mana_points

    def model_update(self):
        pass

    def save(self):
        pass