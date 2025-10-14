# DRACS — Defend, Rest, Attack, Counter, Steal

## Overview

**DRACS** (Defend, Rest, Attack, Counter, Steal) is a turn-based strategy game that integrates fundamental concepts of **machine learning** and **game theory**.
Players compete using limited resources—Health Points (HP) and Mana Points (MP)—to outsmart their opponent through five possible actions.

The project demonstrates adaptive decision-making through both **online** and **offline learning**, showing how artificial intelligence can evolve strategies against deterministic and random opponents.

---

## Game Rules

Each player starts with **5 HP** and **0 MP**. The game ends when one player’s HP reaches zero.
Players may choose one of five possible actions each turn:

| Action      | Description                                                       | MP Cost | Effect                  |
| ----------- | ----------------------------------------------------------------- | ------- | ----------------------- |
| **Attack**  | Deals 1 HP damage to the opponent.                                | 0       | Direct damage.          |
| **Defend**  | Negates incoming damage. If the opponent attacks, they lose 1 MP. | 0       | Reduces risk.           |
| **Rest**    | Regenerates 2 MP.                                                 | 0       | Resource gain.          |
| **Counter** | If attacked, reflects 1 HP damage back to the attacker.           | 1       | Reactive defense.       |
| **Steal**   | Takes HP/MP from the opponent depending on their action.          | 3       | High-risk, high-reward. |

A balance mechanism prevents infinite defense loops: if a defending player has 0 MP, and the opponent uses **Steal**, they lose 1 HP instead of 1 MP.

---

## Artificial Intelligence

DRACS includes multiple AI models of increasing complexity.
Each model is defined in `computer.py` and can play either against a human player or another AI.

| Model                        | Type             | Description                                           |
| ---------------------------- | ---------------- | ----------------------------------------------------- |
| **Random**                   | Baseline         | Chooses a random legal move.                          |
| **Heuristic/Simple**         | Rule-based       | Uses fixed rules based on HP and MP thresholds.       |
| **Adaptive (SGDClassifier)** | Online Learning  | Learns dynamically using stochastic gradient descent. |
| **Gradient Boosting (GBC)**  | Offline Learning | Trained from pre-recorded data for static evaluation. |

### Machine Learning Details

* **Adaptive (SGDClassifier)**

  * Uses incremental updates (`partial_fit`) each round.
  * Learns patterns in player behavior from features including:

    * Player HP and MP
    * Opponent HP and MP
    * Last *k* pairs of actions (history window)
  * Predicts the opponent’s next move and selects a counteraction based on **expected value**.

* **Gradient Boosting (GBC)**

  * Pre-trained on historical data (`data/GBC_Training.csv`).
  * Learns globally optimal strategies from multiple simulated games.
  * Static model — predictions are not updated during play.

---

## Repository Structure

```
DRACS_ML_GAME_Project/
│
├── game/
│   ├── main.py            # Launches the game and manages start menu
│   ├── game.py            # Core game loop and win/loss conditions
│   ├── player.py          # Human player logic and state tracking
│   ├── computer.py        # AI model definitions and decision logic
│   └── Rules.txt          # Extra Information about the game
│
├── data/
│   └── GBC_Training.csv    # Training dataset for the GBC model
│
├── models/
│   ├── DRACS_ADPT_model_AIvsAI_TRAINED.pkl        # Saved adaptive model
│   └── DRACS_GBC_model_AIvsAI_TRAINED.pkl         # Trained gradient boosting model
│
└── README.md           # Project documentation
```

---

## Data Logging and Training

All game rounds can be logged automatically through the **DataLogger** class, producing a CSV file containing both **features** and **labels**.
To proceed with the training of all the models, please select option "Training" in the main menu.

---

## Usage

### Running the Game

```bash
python main.py
```

### Modes

* **Player vs AI**
* **AI vs AI** (for evaluation)
* **Training Mode** (to collect gameplay data)

### Gameplay

* Input one of: `Attack`, `Defense`, `Counter`, `Rest`, or `Steal`
* Monitor HP and MP each round
* The AI adapts in real time (Only for the Adaptive model)

---

## Model Evaluation

Performance is measured across:

* **Prediction accuracy** — proportion of correct action predictions.
* **Win/Loss ratio** — success rate against heuristic or random bots.

Experiments show that:

* The adaptive model improves steadily after 50–100 rounds.
* The gradient boosting model achieves ~77–80% prediction accuracy in test simulations.

---

## Future Work

* Graphical User Interface (Tkinter or Pygame)
* Additional actions and effects
* Reinforcement Learning agent
* Parameter tuning and model comparison utilities

---
