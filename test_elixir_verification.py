# TO MAKE SURE BLUESTACKS IS ALIGNED FOR PROPER ELIXIR COUNTING!
# This script checks the pixel color at specific coordinates in BlueStacks to verify elixir counts.
from Actions import Actions
import time

def test_elixir_counting():
    actions = Actions()
    
    print("Testing elixir counting with ADB...")
    while True:
        count = actions.count_elixir()
        print(f"Current elixir count: {count}")
        time.sleep(1)

if __name__ == "__main__":
    test_elixir_counting()