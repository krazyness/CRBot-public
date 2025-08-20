import os
from src.env import ClashRoyaleEnv
import time

def test_card_detection():
    env = ClashRoyaleEnv()
    
    print("Testing card detection...")
    print("-" * 50)
    
    # Test 1: Capture and save card area
    print("1. Capturing card area...")
    card_area_path = os.path.join(os.path.dirname(__file__), 'screenshots', "cards.png")
    env.actions.capture_card_area(card_area_path)
    print(f"Card area screenshot saved to: {card_area_path}")
    
    # Test 2: Detect cards
    print("\n2. Detecting cards...")
    env.current_cards = env.detect_cards_in_hand()
    print(f"Detected cards: {env.current_cards}")

    if not env.current_cards:
        print("No cards detected. Stopping test.")
        return
    
    # # Test 3: Check card positions
    # print("\nCard positions in hand:")
    # for card, position in env.actions.current_card_positions.items():
    #     print(f"Card {card} is in position {position} (Key: {env.actions.card_keys[position]})")
    
    # Test 4: Try to play each card
    print("\nTesting card placement...")
    for card in env.current_cards:
        print(f"\nTrying to play card: {card}")
        x = env.actions.WIDTH // 2
        y = env.actions.HEIGHT * 3 // 4
        env.actions.card_play(x, y, env.current_cards.index(card))
        time.sleep(2)  # Wait between card plays

if __name__ == "__main__":
    test_card_detection()
