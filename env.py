import numpy as np
import time
import os
import pyautogui
import threading
from dotenv import load_dotenv
from Actions import Actions
from inference_sdk import InferenceHTTPClient

# Load environment variables from .env file
load_dotenv()

MAX_ENEMIES = 10
MAX_ALLIES = 10

SPELL_CARDS = ["Fireball", "Zap", "Arrows", "Tornado", "Rocket", "Lightning", "Freeze"]

class ClashRoyaleEnv:
    def __init__(self):
        self.actions = Actions()
        self.rf_model = self.setup_roboflow()
        self.card_model = self.setup_card_roboflow()
        self.state_size = 1 + 2 * (MAX_ALLIES + MAX_ENEMIES)
        self.num_cards = 4
        self.grid_width = 18
        self.grid_height = 28
        self.screenshot_path = os.path.join(os.path.dirname(__file__), 'screenshots', "current.png")
        self.available_actions = self.get_available_actions()
        self.action_size = len(self.available_actions)
        self.current_cards = []
        self.game_over_flag = None
        self._endgame_thread = None
        self._endgame_thread_stop = threading.Event()
        self.prev_elixir = None
        self.prev_enemy_presence = None
        self.prev_enemy_princess_towers = None
        self.match_over_detected = False
        self.last_predictions: list = []

    def setup_roboflow(self):
        api_key = os.getenv('ROBOFLOW_API_KEY')
        if not api_key:
            raise ValueError("ROBOFLOW_API_KEY environment variable is not set. Please check your .env file.")
        
        return InferenceHTTPClient(
            api_url="http://localhost:9001",

            api_key="api_key"

        )

    def setup_card_roboflow(self):
        api_key = os.getenv('ROBOFLOW_API_KEY')
        if not api_key:
            raise ValueError("ROBOFLOW_API_KEY environment variable is not set. Please check your .env file.")
        
        return InferenceHTTPClient(
            api_url="http://localhost:9001",

            api_key="api_key"

        )

    def reset(self):
        time.sleep(3)
        self.game_over_flag = None
        self._endgame_thread_stop.clear()
        self._endgame_thread = threading.Thread(target=self._endgame_watcher, daemon=True)
        self._endgame_thread.start()
        self.prev_elixir = None
        self.prev_enemy_presence = None
        self.prev_enemy_princess_towers = self._count_enemy_princess_towers()
        self.match_over_detected = False
        return self._get_state()

    def close(self):
        self._endgame_thread_stop.set()
        if self._endgame_thread:
            self._endgame_thread.join()

    def step(self, action_index):
        if not self.match_over_detected and hasattr(self.actions, "detect_match_over") and self.actions.detect_match_over():
            print("Match over detected (matchover.png), forcing no-op until next game.")
            self.match_over_detected = True

        if self.match_over_detected:
            action_index = len(self.available_actions) - 1

        if self.game_over_flag:
            done = True
            reward = self._compute_reward(self._get_state())
            result = self.game_over_flag
            if result == "victory":
                reward += 100
                print("Victory detected - ending episode")
            elif result == "defeat":
                reward -= 100
                print("Defeat detected - ending episode")
            self.match_over_detected = False
            return self._get_state(), reward, done

        self.current_cards = self.detect_cards_in_hand()
        print("\nCurrent cards in hand:", self.current_cards)

        if all(card == "Unknown" for card in self.current_cards):
            print("All cards are Unknown, clicking at (1611, 831) and skipping move.")
            pyautogui.moveTo(1611, 831, duration=0.2)
            pyautogui.click()
            next_state = self._get_state()
            return next_state, 0, False

        action = self.available_actions[action_index]
        card_index, x_frac, y_frac = action
        print(f"Action selected: card_index={card_index}, x_frac={x_frac:.2f}, y_frac={y_frac:.2f}")

        spell_penalty = 0

        if card_index != -1 and card_index < len(self.current_cards):
            card_name = self.current_cards[card_index]
            print(f"Attempting to play {card_name}")
            target_x_frac, target_y_frac = self._compute_placement(card_name)
            x = int(target_x_frac * self.actions.WIDTH) + self.actions.TOP_LEFT_X
            y = int(target_y_frac * self.actions.HEIGHT) + self.actions.TOP_LEFT_Y
            self.actions.card_play(x, y, card_index)
            time.sleep(1)

            if card_name in SPELL_CARDS:
                state = self._get_state()
                enemy_positions = []
                for i in range(1 + 2 * MAX_ALLIES, 1 + 2 * MAX_ALLIES + 2 * MAX_ENEMIES, 2):
                    ex = state[i]
                    ey = state[i + 1]
                    if ex != 0.0 or ey != 0.0:
                        ex_px = int(ex * self.actions.WIDTH)
                        ey_px = int(ey * self.actions.HEIGHT)
                        enemy_positions.append((ex_px, ey_px))
                radius = 100
                found_enemy = any((abs(ex - x) ** 2 + abs(ey - y) ** 2) ** 0.5 < radius for ex, ey in enemy_positions)
                if not found_enemy:
                    spell_penalty = -5

        current_enemy_princess_towers = self._count_enemy_princess_towers()
        princess_tower_reward = 0
        if self.prev_enemy_princess_towers is not None:
            if current_enemy_princess_towers < self.prev_enemy_princess_towers:
                princess_tower_reward = 20
        self.prev_enemy_princess_towers = current_enemy_princess_towers

        done = False
        reward = self._compute_reward(self._get_state()) + spell_penalty + princess_tower_reward
        next_state = self._get_state()
        return next_state, reward, done

    def _get_state(self):
        self.actions.capture_area(self.screenshot_path)
        elixir = self.actions.count_elixir()
        
        workspace_name = os.getenv('WORKSPACE_TROOP_DETECTION')
        if not workspace_name:
            raise ValueError("WORKSPACE_TROOP_DETECTION environment variable is not set. Please check your .env file.")
        
        results = self.rf_model.run_workflow(

            workspace_name="workspace_name",


            workflow_id="detect-count-and-visualize",
            images={"image": self.screenshot_path}
        )

        print("RAW results:", results)

        predictions = []
        if isinstance(results, dict) and "predictions" in results:
            predictions = results["predictions"]
        elif isinstance(results, list) and results:
            first = results[0]
            if isinstance(first, dict) and "predictions" in first:
                predictions = first["predictions"]
        print("Predictions:", predictions)
        if not predictions:
            print("WARNING: No predictions found in results")
            return None

        if isinstance(predictions, dict) and "predictions" in predictions:
            predictions = predictions["predictions"]

        print("RAW predictions:", predictions)
        print("Detected classes:", [repr(p.get("class", "")) for p in predictions if isinstance(p, dict)])

        self.last_predictions = predictions

        TOWER_CLASSES = {
            "ally king tower",
            "ally princess tower",
            "enemy king tower",
            "enemy princess tower"
        }

        def normalize_class(cls):
            return cls.strip().lower() if isinstance(cls, str) else ""

        allies = [
            (p["x"], p["y"])
            for p in predictions
            if (
                isinstance(p, dict)
                and normalize_class(p.get("class", "")) not in TOWER_CLASSES
                and normalize_class(p.get("class", "")).startswith("ally")
                and "x" in p and "y" in p
            )
        ]

        enemies = [
            (p["x"], p["y"])
            for p in predictions
            if (
                isinstance(p, dict)
                and normalize_class(p.get("class", "")) not in TOWER_CLASSES
                and normalize_class(p.get("class", "")).startswith("enemy")
                and "x" in p and "y" in p
            )
        ]

        print("Allies:", allies)
        print("Enemies:", enemies)

        def normalize(units):
            return [(x / self.actions.WIDTH, y / self.actions.HEIGHT) for x, y in units]

        def pad_units(units, max_units):
            units = normalize(units)
            if len(units) < max_units:
                units += [(0.0, 0.0)] * (max_units - len(units))
            return units[:max_units]

        ally_positions = pad_units(allies, MAX_ALLIES)
        enemy_positions = pad_units(enemies, MAX_ENEMIES)

        ally_flat = [coord for pos in ally_positions for coord in pos]
        enemy_flat = [coord for pos in enemy_positions for coord in pos]

        state = np.array([elixir / 10.0] + ally_flat + enemy_flat, dtype=np.float32)
        return state

    def _compute_reward(self, state):
        if state is None:
            return 0
        elixir = state[0] * 10
        enemy_positions = state[1 + 2 * MAX_ALLIES:]
        enemy_presence = sum(enemy_positions)
        reward = -enemy_presence
        if self.prev_elixir is not None and self.prev_enemy_presence is not None:
            elixir_spent = self.prev_elixir - elixir
            enemy_reduced = self.prev_enemy_presence - enemy_presence
            if elixir_spent > 0 and enemy_reduced > 0:
                reward += 2 * min(elixir_spent, enemy_reduced)
        self.prev_elixir = elixir
        self.prev_enemy_presence = enemy_presence
        return reward

    def detect_cards_in_hand(self):
        try:
            card_paths = self.actions.capture_individual_cards()
            print("\nTesting individual card predictions:")
            cards = []
            workspace_name = os.getenv('WORKSPACE_CARD_DETECTION')
            if not workspace_name:
                raise ValueError("WORKSPACE_CARD_DETECTION environment variable is not set. Please check your .env file.")
            
            for card_path in card_paths:
                results = self.card_model.run_workflow(

                    workspace_name="workspace_name",

                    workflow_id="custom-workflow",
                    images={"image": card_path}
                )
                predictions = []
                if isinstance(results, list) and results:
                    preds_dict = results[0].get("predictions", {})
                    if isinstance(preds_dict, dict):
                        predictions = preds_dict.get("predictions", [])
                if predictions:
                    card_name = predictions[0]["class"]
                    print(f"Detected card: {card_name}")
                    cards.append(card_name)
                else:
                    print("No card detected.")
                    cards.append("Unknown")
            return cards
        except Exception as e:
            print(f"Error in detect_cards_in_hand: {e}")
            return []

    def get_available_actions(self):
        actions = [
            [card, x / (self.grid_width - 1), y / (self.grid_height - 1)]
            for card in range(self.num_cards)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
        ]
        actions.append([-1, 0, 0])
        return actions

    def _endgame_watcher(self):
        while not self._endgame_thread_stop.is_set():
            result = self.actions.detect_game_end()
            if result:
                self.game_over_flag = result
                break
            time.sleep(0.5)

    def _count_enemy_princess_towers(self):
        self.actions.capture_area(self.screenshot_path)
        
        workspace_name = os.getenv('WORKSPACE_TROOP_DETECTION')
        if not workspace_name:
            raise ValueError("WORKSPACE_TROOP_DETECTION environment variable is not set. Please check your .env file.")
        
        results = self.rf_model.run_workflow(

            workspace_name="workspace_name",


            workflow_id="detect-count-and-visualize",
            images={"image": self.screenshot_path}
        )
        predictions = []
        if isinstance(results, dict) and "predictions" in results:
            predictions = results["predictions"]
        elif isinstance(results, list) and results:
            first = results[0]
            if isinstance(first, dict) and "predictions" in first:
                predictions = first["predictions"]
        return sum(1 for p in predictions if isinstance(p, dict) and p.get("class") == "enemy princess tower")

    def _get_enemy_units(self):
        enemy_units = []
        tower_classes = {
            "ally king tower",
            "ally princess tower",
            "enemy king tower",
            "enemy princess tower",
        }
        for p in self.last_predictions:
            if not isinstance(p, dict):
                continue
            cls = p.get("class")
            if not cls:
                continue
            cls_norm = cls.strip().lower()
            if cls_norm in tower_classes:
                continue
            if not cls_norm.startswith("enemy"):
                continue
            x = p.get("x")
            y = p.get("y")
            if x is None or y is None:
                continue
            enemy_units.append({"class": cls, "x": x, "y": y})
        return enemy_units

    def _compute_placement(self, card_name):
        enemy_units = self._get_enemy_units()
        def to_frac(x, y):
            return (x / self.actions.WIDTH, y / self.actions.HEIGHT)
        if card_name in SPELL_CARDS:
            if enemy_units:
                cx = sum(unit["x"] for unit in enemy_units) / len(enemy_units)
                cy = sum(unit["y"] for unit in enemy_units) / len(enemy_units)
                x_frac, y_frac = to_frac(cx, cy)
                x_frac = max(0.0, min(1.0, x_frac))
                y_frac = max(0.0, min(1.0, y_frac))
                return x_frac, y_frac
            return 0.5, 0.5
        if enemy_units:
            nearest = max(enemy_units, key=lambda u: u["y"])
            x_frac, _ = to_frac(nearest["x"], nearest["y"])
            y_frac = 0.75
            x_frac = max(0.0, min(1.0, x_frac))
            return x_frac, y_frac
        return 0.5, 0.8
