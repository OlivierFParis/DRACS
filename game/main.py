import math

from computer import Computer
from game import Game
from config import UserRefusedTraining
from player import Player
from config import Config

cfg = Config() # Object of the class Config, which holds core configuration for the game

def start_screen():
    """
    Start menu with the different options the user can select.
    :return: Nothing.
    """
    print("Welcome to DRACS!")
    while True:
        try:
            choice_1 = input("Enter your choice: \n1. Start Game\n2. Rules\n3. Parameters\n4. AI vs AI\n5. Training\n6. Predictive Algorithm Assessment\n7. Exit\n").strip().upper()
            match choice_1:
                case "1" | "START" | "START GAME" | "S":
                    start_game()
                case "2" | "RULE" | "RULES" | "R":
                    read_rules()
                    continue
                case "3" | "PARAMETER" | "PARAMETERS" | "P":
                    parameter_selection()
                    continue
                case "4":
                    ai_vs_ai()
                    continue
                case "5":
                    training_set()
                    continue
                case "6":
                    predictive_assess()
                    continue
                case "7" | "EXIT" | "E":
                    print("Thank you for playing!")
                    break
                case _:
                    print("Invalid choice!")
                    continue
        except UserRefusedTraining as e: # Catches raised exception (exception propagation), that occurs when the user refuses to train a certain model
            print(f"\n{e}\n")



def start_game():
    """
    Menu to start the game. Where the player can select between playing against one of the AI models, or another player.
    :return: Nothing.
    """
    choice_2 = input("Game Mode:\n1. Player vs AI (Default)\n2. Player vs Player\n3. Exit\n").strip().upper()
    match choice_2:
        case "1" | "AI":
            player_1 = Player(cfg, "Player 1")
            computer = Computer(cfg, diff_selection())
            game = Game(cfg, player_1, computer)
            print(f"Correct Prediction: {game.acc_prediction}\nIncorrect Prediction: {game.innac_prediction}")
            print(f"Successful Prediction (Ratio): {(game.acc_prediction/(game.acc_prediction+game.innac_prediction))*100}%\n")
        case "2" | "PLAYER":
            player_1 = Player(cfg, "Player 1")
            player_2 = Player(cfg, "Player 2")
            Game(cfg, player_1, player_2)
        case "3" | "EXIT" | "E":
            return
        case _:
            print("Invalid choice!")



def read_rules():
    """
    Displays the rules and extra information for the game.
    :return: Nothing.
    """
    try:
        rules_file = open("game\\Rules.txt", "r")
        rules = rules_file.read()
        print(rules+"\n")
        rules_file.close()
    except FileNotFoundError:
        print("Rules file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")



def parameter_selection():
    """
    The user can change the core parameter that makes up DRACS in this function.
    :return: Nothing.
    """
    print("Please be aware that changing any of the parameters will require the AI algorithms to be retrained.\n")
    while True:
        cfg.print_config() # Displays current parameters for the game
        choice_3 = input("What would you like to do?\n1. Change Health Points\n2. Change Mana Points\n3. Change Number of Turns\n4. History Window\n5. Set all to Default\n6. Exit\n").strip().upper()
        match choice_3:
            case "1" | "CHANGE HEALTH POINTS" | "HEALTH" | "HEALTH POINTS" | "HP":
                choice_hp = input("Enter Value for Health Points:\n").strip()
                try:
                    cfg.set_config(max_health_points=int(choice_hp))
                except ValueError:
                    print("Invalid value!")
                except Exception as e:
                    print(f"An error occurred: {e}")
            case "2" | "CHANGE MANA POINTS" | "MANA" | "MANA POINTS" | "MP":
                choice_mp = input("Enter Value for Mana Points:\n").strip()
                try:
                    cfg.set_config(max_mana_points=int(choice_mp))
                except ValueError:
                    print("Invalid value!")
                except Exception as e:
                    print(f"An error occurred: {e}")
            case "3" | "CHANGE NUMBER OF TURNS" | "TURN" | "T" | "TURNS":
                choice_tn = input("Enter Value for Number of Turns:\n").strip()
                try:
                    cfg.set_config(max_num_turns=int(choice_tn))
                except ValueError:
                    print("Invalid value!")
                except Exception as e:
                    print(f"An error occurred: {e}")
            case "4" | "HIST" | "HISTORY" | "H":
                choice_hist = input("Enter Value for History Window:\n").strip()
                try:
                    cfg.set_config(k=int(choice_hist))
                except ValueError:
                    print("Invalid value!")
                except Exception as e:
                    print(f"An error occurred: {e}")
            case "5" | "DEFAULT" | "D":
                cfg.set_config(max_health_points=5, max_mana_points=3, max_num_turns=20, k = 3)
            case "6" | "EXIT" | "E":
                break
            case _:
                print("Invalid choice!")
                continue



def diff_selection(auto_choice = False, choice_diff = None):
    """
    The user selects for the AI model they want to play against, or that they want to see fight when selecting for AI vs AI combat.
    :param auto_choice: False if the user is making a choice, or True if the function is automatically called for by a different function.
    :param choice_diff: If the call is automatic, defined by auto_choice, the choice_diff is the value representing the automatic choice, from 1 to 5 (currently only 2 or 3).
    :return: Core name of the AI model.
    """
    if not auto_choice: choice_diff = input("Select a Difficulty\n1. Random\n2. Simple\n3. Adaptive\n4. Strategist\n5. GBC\n").strip().upper()
    match choice_diff:
        case "1" | "RANDOM" | "R" | "RAND":
            return "RANDOM"
        case "2" | "SIMPLE" | "S" | "SIMP":
            return "SIMPLE"
        case "3" | "ADAPTIVE" | "A" | "ADAPT":
            model_existence("ADAPTIVE")
            return "ADAPTIVE"
        case "4" | "STRATEGIST" | "S" | "STRAT": #TODO
            print("Strategist is not currently implemented.\nDefaulting to Random.")
            return "STRATEGIST"
        case "5" | "GBC":
            model_existence("GBC")
            return "GBC"
        case _:
            print("Invalid choice!")
            print("Defaulting to Random.")
            return "RANDOM"



def ai_vs_ai():
    """
    Menu for AI vs AI, where the user can make two of the AI models fight against one another.
    :return: Nothing.
    """
    # Inputs and options
    try:
        game_number = int(input("Enter Game Number: ").strip())
        if game_number < 1:
            print("Minimal amount of games required is 1.\nDefaulting to 1.")
            game_number = 1

        choice_action_viewer = input("Would you like to see the actions?\n**Default is False. They are too rapid to see.**\n1. Yes\n2. No\n").strip().upper()
        if choice_action_viewer in {"1", "YES", "Y"}:
            pass
        else:
            cfg.set_config(action_viewer = False)

        custom_ai_fight = input("Would you like to choose the Computer's model?\n1. Yes\n2. No\n").strip().upper()
        if custom_ai_fight == "1" or custom_ai_fight == "YES":
            print("For Computer 1.\n")
            cpu_name_p1 = diff_selection()
            print("For Computer 2.\n")
            cpu_name_p2 = diff_selection()
        else:
            print("Defaulting to Simple vs. Adaptive.\n")
            cpu_name_p1 = diff_selection(True, "2")
            cpu_name_p2 = diff_selection(True, "3")

        # Precomputes game tracking structure.
        inc_cell_num = math.ceil((-10+math.sqrt(100-4*(-20*game_number)))/20) # Number of total "cells" to generate, where every cell contains 10 more games than the last (e.g., 100 games = 4 cells each containing 10, 20, 30, and 40 games respectively.
        inc_win_count = [[0,0,0,0] for _ in range(inc_cell_num)] # Creates the respective amount of cells necessary
        prediction = [0,0]
        game_count = 10 # Tracker for how many games there should be in each cell.
        multi_number_game = 0 # Tracker for the sum of games played in total.

        # Simulation loop
        for i in range(game_number):
            if i % 100 == 0:
                print(f"Game Number Progress: {i} out of {game_number}")
            if i == game_count+multi_number_game:
                inc_win_count[int(game_count / 10 - 1)][3] = inc_win_count[int(game_count / 10 - 1)][1]/game_count
                multi_number_game += game_count
                game_count += 10

            computer_1 = Computer(cfg, cpu_name_p1)
            computer_2 = Computer(cfg, cpu_name_p2)
            game = Game(cfg, computer_1, computer_2)
            prediction[0] += game.acc_prediction
            prediction[1] += game.innac_prediction

            # Increase the count for the AI model that won or if they tied, at its respective location within a cell.
            if game.winner == 1:
                inc_win_count[int(game_count / 10 - 1)][0] += 1
            elif game.winner == 2:
                inc_win_count[int(game_count / 10 - 1)][1] += 1
            elif game.winner == 0:
                inc_win_count[int(game_count / 10 - 1)][2] += 1

        # Sums the total number of wins for each AI model and the number of ties.
        win_count = [0,0,0]
        for i in range(len(inc_win_count)):
            win_count[0] += inc_win_count[i][0]
            win_count[1] += inc_win_count[i][1]
            win_count[2] += inc_win_count[i][2]

        print(f"Winning Board: {inc_win_count}\nWin Count for {cpu_name_p1}: {win_count[0]}\nWin Count for {cpu_name_p2}: {win_count[1]}\nNumber of Ties: {win_count[2]}\n")
        print(f"Predictive Statistics for {cpu_name_p2}")
        print(f"Correct Prediction: {prediction[0]}\nIncorrect Prediction: {prediction[1]}")
        print(f"Successful Prediction (Ratio): {(prediction[0] / (prediction[0] + prediction[1])) * 100}%\n")
        cfg.set_config(action_viewer=True)

    except ValueError:
        print("Invalid value!\n")



def training_set(auto_GBC = False):
    """
    Function to create the core basic model, i.e., the Adaptive model, and the training set for the GBC model.
    :param auto_GBC: If true, the option to train for the GBC model is automatically set to true and will occur, without the user's choice.
    :return: Nothing.
    """
    cfg.set_config(action_viewer = False)
    if not auto_GBC:
        choice_GBC = input("With or Without Training for GBC?\n**WILL TAKE MUCH LONGER**\n1. With\n2. Without\n").strip().upper()
        if choice_GBC in {"1", "WITH"}:
            training_game = True
        else:
            training_game = False
    else:
        print("About to automatically train for GBC.")
        input("Press Enter to continue...")
        training_game = True

    # Switches the AI model's perspective during game recording and saving.
    computer_names_1 = ["RANDOM","SIMPLE"]
    computer_names_2 = ["SIMPLE_2","RANDOM_2"]
    game_number = 2000

    # Main training loop
    for i in range(game_number):
        computer_1 = Computer(cfg, computer_names_1[i%2])
        computer_2 = Computer(cfg, computer_names_2[i%2])
        Game(cfg, computer_1, computer_2, training_game)
        if i % 100 == 0:
            print(f"Game Number Progress: {i} out of {game_number}")
    cfg.set_config(action_viewer = True)



def predictive_assess():
    """
    Function used to assess the predictive power of all the current AI models.
    :return: Nothing.
    """
    # Assess whether the models required exist, or can be generated.
    print("Assessing model existence")
    model_existence("GBC")
    model_existence("ADAPTIVE")

    overall_result = []
    ai_types = [["RANDOM","SIMPLE"], ["RANDOM", "ADAPTIVE"], ["RANDOM","GBC"], ["SIMPLE", "ADAPTIVE"],["SIMPLE", "GBC"], ["GBC", "ADAPTIVE"]]

    # Input and options
    try:
        game_number = int(input("Enter Game Number: ").strip())
        if game_number < 1:
            print("Minimal amount of games required is 1.\nDefaulting to 1.")
            game_number = 1

        choice_action_viewer = input("Would you like to see the actions?\n**Default is False. They are too rapid to see.**\n1. Yes\n2. No\n").strip().upper()
        if choice_action_viewer in {"1", "YES", "Y"}:
            pass
        else:
            cfg.set_config(action_viewer = False)

        # Precomputes game tracking structure.
        inc_cell_num = math.ceil((-10 + math.sqrt(100 - 4 * (-20 * game_number))) / 20) # Calculates the number of cells required for each game, increasing by 10
        for u in range(len(ai_types)):
            print(f"\nStarting Fight Between {ai_types[u][0]} and {ai_types[u][1]}")
            overall_result.append(f"Fight Between {ai_types[u][0]} and {ai_types[u][1]}\n")
            inc_win_count = [[0, 0, 0, 0] for _ in range(inc_cell_num)]
            prediction = [0, 0]
            game_count = 10
            multi_number_game = 0

            # Simulation loop
            for i in range(game_number):
                if i % 100 == 0:
                    print(f"Game Number Progress: {i} out of {game_number}")
                if i == game_count + multi_number_game:
                    inc_win_count[int(game_count / 10 - 1)][3] = inc_win_count[int(game_count / 10 - 1)][1] / game_count
                    multi_number_game += game_count
                    game_count += 10

                computer_1 = Computer(cfg, ai_types[u][0])
                computer_2 = Computer(cfg, ai_types[u][1])
                game = Game(cfg, computer_1, computer_2)
                prediction[0] += game.acc_prediction
                prediction[1] += game.innac_prediction

                # Increase the count for the AI model that won or if they tied, at its respective location within a cell.
                if game.winner == 1: inc_win_count[int(game_count / 10 - 1)][0] += 1
                elif game.winner == 2: inc_win_count[int(game_count / 10 - 1)][1] += 1
                elif game.winner == 0: inc_win_count[int(game_count / 10 - 1)][2] += 1

            # Sums the total number of wins for each AI model and the number of ties.
            win_count = [0, 0, 0]
            for i in range(len(inc_win_count)):
                win_count[0] += inc_win_count[i][0]
                win_count[1] += inc_win_count[i][1]
                win_count[2] += inc_win_count[i][2]

            # Appends the result to a list containing all the results of the AI model predictive power assessments.
            overall_result.append(f"Win Count for {ai_types[u][0]}: {win_count[0]}\nWin Count for {ai_types[u][1]}: {win_count[1]}\nNumber of Ties: {win_count[2]}\n")
            overall_result.append(f"Correct Prediction Made by {ai_types[u][1]}: {prediction[0]}\nIncorrect Prediction Made by {ai_types[u][1]}: {prediction[1]}\n")
            overall_result.append(f"Successful Prediction (Ratio): {(prediction[0] / (prediction[0] + prediction[1])) * 100}%\n")
            overall_result.append("\n")

        for i in range(len(overall_result)):
            print(overall_result[i])
        cfg.set_config(action_viewer = True)

    except ValueError:
        print("Invalid value!\n")


def model_existence(model_name):
    """
    Function to check whether an AI model exists or not before initiating the game.
    :param model_name: The core name of the AI model.
    :return: Nothing
    :raises: UserRefusedTraining error to propagate back to start_screen().
    """
    model_path = cfg.query_existence(model_name)
    if model_path is False:
        choice_training = input("Model does not exist.\nRequires training.\nWould you like to proceed?\n1. Yes\n2. No\n").strip().upper()
        if choice_training in {"1", "YES", "Y"}:
            training_set(model_name == "GBC")
        else:
            raise UserRefusedTraining(f"{model_name} does not exist, please train the model first.\nReturning back to main menu.")


# Function to start the program
if __name__ == '__main__':
    start_screen()
    exit()