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

  * Pre-trained on historical data (`data/GBC_Training_K3_HP5_MP3.csv`).
  * Learns globally optimal strategies from multiple simulated games.
  * Static model — predictions are not updated during play.

---

## Repository Structure

```
DRACS/
│
├── game/
│   ├── main.py                # Launches the game and manages start menu
│   ├── game.py                # Core game loop and win/loss conditions
│   ├── player.py              # Human player logic and state tracking
│   ├── computer.py            # AI model definitions and decision logic
│   ├── config.py              # Game settings and checks to validate existence of the models
│   └── Rules.txt              # Additional gameplay information, mechanics, and general information
│
├── data/
│   └── GBC_Training_K3_HP5_MP3.csv           # Training dataset for the Gradient Boosting model
│
├── models/
│   ├── DRACS_ADAPTIVE_MODEL_K3_HP5_MP3.pkl   # Saved adaptive (SGD) model
│   └── DRACS_GBC_MODEL_K3_HP5_MP3.pkl        # Trained Gradient Boosting model
│
├── requirements.txt           # Python dependencies for the project
├── LICENSE                    # MIT license file
└── README.md                  # Project documentation
```

---

## Data Logging and Training

All game rounds can be logged automatically through the **DataLogger** class, producing a CSV file containing both **features** and **labels**.
To proceed with the training of all the models, please select option "Training" in the main menu.

### Saving and Logs
* All trained models are stored in the /models directory.
* Gameplay data for training the Gradient Boosting model is logged automatically in /data as a CSV file.
* To retrain the GBC model on new data, simply use the training option in the main menu.
  * Currently the GBC model in /models need to be manually deleted for it to be retrained with the new data. 

---

## Usage

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Game

```bash
python game/main.py
```

### Modes

* **Player vs AI**
* **AI vs AI** (for evaluation)
* **Training Mode** (to collect gameplay data)
* **Predictive Algorithm Assessment** (to evaluate the performance of every model against one another)

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
* The trained adaptive model is able to adapt to the player's pattern after approximately 1 game.
* The adaptive model achieves ~63-78% accuracy in test simulations.
* The gradient boosting model achieves ~77–80% prediction accuracy in test simulations.
* The adaptive model overwhelmingly wins over the Simple algorithm, and the gradient boosting model, with ~97-99.9% win rate.

---

## Future Work

* Graphical User Interface (Tkinter or Pygame)
* Additional actions and effects
* Reinforcement Learning agent

---
