import math

from computer import Computer
from game import Game
from player import Player

health_point = 5
mana_point = 0
num_turns_max = 20
k = 3
default = True

def start_screen():
    print("Welcome to DRACS!")
    while True:
        choice_1 = input("Enter your choice: \n1. Start Game\n2. Rules\n3. Parameters\n4. AI vs AI\n5. Training\n6. Exit\n").strip().upper()
        match choice_1:
            case "1" | "START" | "START GAME" | "S":
                start_game()
            case "2" | "RULE" | "RULES" | "R":
                read_rules()
                continue
            case "3" | "PARAMETER" | "PARAMETERS" | "P":
                parameter_selection()
                continue
            case "6" | "EXIT" | "E":
                print("Thank you for playing!")
                break
            case "4":
                ai_vs_ai()
                continue
            case "5":
                training_set()
                continue
            case _:
                print("Invalid choice!")
                continue


def start_game():
    choice_2 = input("Game Mode:\n1. Player vs AI (Default)\n2. Player vs Player\n3. Exit\n").strip().upper()
    match choice_2:
        case "1" | "AI":
            player_1 = Player(health_point, mana_point, "Player 1")
            computer = Computer(health_point, mana_point, diff_selection())
            Game(num_turns_max, player_1, computer)
        case "2" | "PLAYER":
            player_1 = Player(health_point, mana_point, "Player 1")
            player_2 = Player(health_point, mana_point, "Player 2")
            Game(num_turns_max, player_1, player_2)
        case "3" | "EXIT" | "E":
            return
        case _:
            print("Invalid choice!")


def read_rules():
    try:
        rules_file = open("game\\Rules.txt", "r")
        rules = rules_file.read()
        print(rules+"\n")
        rules_file.close()
    except FileNotFoundError:
        print("Rules file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def parameter_selection(): #TODO make it function properly with custom values greater than maximal health and mp
    global default
    print("Please be aware that changing any of the parameters will require the AI algorithms to be retrained.\n")
    global health_point, mana_point, num_turns_max
    while True:
        print(f"Current Parameters:\n 1. Health Point: {health_point}\n 2. Mana Point: {mana_point}\n 3. Number of Turns: {num_turns_max}\n")
        choice_3 = input("What would you like to do?\n1. Change Health Points\n2. Change Mana Points\n3. Change Number of Turns\n4. Set all to Default\n5. Exit\n").strip().upper()
        match choice_3:
            case "1" | "CHANGE HEALTH POINTS" | "HEALTH" | "HEALTH POINTS" | "HP":
                choice_hp = input("Enter Value for Health Points:\n").strip()
                try:
                    health_point = int(choice_hp)
                    if health_point != 5:
                        default = False
                except ValueError:
                    print("Invalid value!")
                except Exception as e:
                    print(f"An error occurred: {e}")
            case "2" | "CHANGE MANA POINTS" | "MANA" | "MANA POINTS" | "MP":
                choice_mp = input("Enter Value for Mana Points:\n").strip()
                try:
                    mana_point = int(choice_mp)
                    if mana_point != 0:
                        default = False
                except ValueError:
                    print("Invalid value!")
                except Exception as e:
                    print(f"An error occurred: {e}")
            case "3" | "CHANGE NUMBER OF TURNS" | "TURN" | "T" | "TURNS":
                choice_tn = input("Enter Value for Number of Turns:\n").strip()
                try:
                    num_turns_max = int(choice_tn)
                    if num_turns_max != 20:
                        default = False
                except ValueError:
                    print("Invalid value!")
                except Exception as e:
                    print(f"An error occurred: {e}")
            case "4" | "DEFAULT" | "D":
                health_point = 5
                mana_point = 0
                num_turns_max = 20
                default = True
            case "5" | "EXIT" | "E":
                break
            case _:
                print("Invalid choice!")
                continue
    if not default:
        choice_param = input("Are you sure you would like to proceed?\nThe program will require retraining, unless the models already exist.\n1. Yes\n2. No\n").strip().upper()
        if choice_param == "1" | "YES": #TODO ensure that the models exist either at runtime or here
            pass
        else:
            print("Restoring Default Parameters...")
            health_point = 5
            mana_point = 0
            num_turns_max = 20
            default = True


def diff_selection():
    choice_diff = input("Select a Difficulty\n1. Random\n2. Simple\n3. Adaptive\n4. Strategist\n5. GBC\n").strip().upper()
    match choice_diff:
        case "1" | "RANDOM" | "R" | "RAND":
            return "AI_RANDOM"
        case "2" | "SIMPLE" | "S" | "SIMP":
            return "AI_SIMPLE"
        case "3" | "ADAPTIVE" | "A" | "ADAPT":
            return "AI_ADAPTIVE"
        case "4" | "STRATEGIST" | "S" | "STRAT":
            return "AI_STRATEGIST"
        case "5" | "GBC":
            return "AI_GBC"
        case _:
            print("Invalid choice!")
            print("Defaulting to Random.")
            return "AI_RANDOM"


def ai_vs_ai():
    action_viewer = False
    game_number = int(input("Enter Game Number: "))
    choice_action_viewer = input("Would you like to see the actions?\n**Default is False. They are too rapid to see.**\n1. Yes\n2. No\n").strip().upper()
    if choice_action_viewer == "1" or choice_action_viewer == "YES":
        action_viewer = True
    else:
        action_viewer = False
    inc_cell_num = 1 + math.ceil((-10+math.sqrt(100-4*(-20*game_number)))/20)
    inc_win_count = [[0,0,0,0] for _ in range(inc_cell_num)]
    successful_prediction = [0,0]
    game_count = 10
    multi_number_game = 0
    for i in range(game_number):
        if i % 100 == 0:
            print(f"Game Number Progress: {i} out of {game_number}")
        if i == game_count+multi_number_game:
            inc_win_count[int(game_count / 10 - 1)][3] = inc_win_count[int(game_count / 10 - 1)][1]/game_count
            multi_number_game += game_count
            game_count += 10
        computer_1 = Computer(health_point, mana_point, "AI_SIMPLE", action_viewer = action_viewer)
        # computer_1 = Computer(health_point, mana_point, "AI_RANDOM", action_viewer = action_viewer)
        # computer_1 = Computer(health_point, mana_point, "AI_GBC", action_viewer = action_viewer)
        # computer_2 = Computer(health_point, mana_point, "AI_ADAPTIVE", action_viewer = action_viewer)
        computer_2 = Computer(health_point, mana_point, "AI_GBC", action_viewer = action_viewer)
        game = Game(num_turns_max, computer_1, computer_2, action_viewer = action_viewer)
        if game.winner == 1:
            successful_prediction[0] += game.acc_prediction
            successful_prediction[1] += game.innac_prediction
            inc_win_count[int(game_count/10-1)][0] += 1
        elif game.winner == 2:
            successful_prediction[0] += game.acc_prediction
            successful_prediction[1] += game.innac_prediction
            inc_win_count[int(game_count / 10 - 1)][1] += 1
        elif game.winner == 0:
            successful_prediction[0] += game.acc_prediction
            successful_prediction[1] += game.innac_prediction
            inc_win_count[int(game_count / 10 - 1)][2] += 1
    Win_count = [0,0,0]
    for i in range(len(inc_win_count)):
        Win_count[0] += inc_win_count[i][0]
        Win_count[1] += inc_win_count[i][1]
        Win_count[2] += inc_win_count[i][2]
    print(f"Winning Board: {inc_win_count}\nSuccessful Prediction: {successful_prediction}\nWin Count for Computer 1: {Win_count[0]}\nWin Count for Computer 2: {Win_count[1]}\nNumber of Ties: {Win_count[2]}\n")


def training_set():
    choice_GBC = input("With or Without Training for GBC?\n**WILL TAKE MUCH LONGER**\n1. With\n2. Without\n")
    if choice_GBC == "1":
        training_game = True
    else:
        training_game = False
    computer_names_1 = ["AI_RANDOM","AI_SIMPLE"]
    computer_names_2 = ["AI_SIMPLE2","AI_RANDOM2"]
    game_number = 2000
    for i in range(game_number):
        computer_1 = Computer(health_point, mana_point, computer_names_1[i%2], action_viewer= False)
        computer_2 = Computer(health_point, mana_point, computer_names_2[i%2], action_viewer= False)
        Game(num_turns_max, computer_1, computer_2, k, training_game, False)
        if i % 100 == 0:
            print(f"Game Number Progress: {i} out of {game_number}")





if __name__ == '__main__':
    start_screen()
    exit()