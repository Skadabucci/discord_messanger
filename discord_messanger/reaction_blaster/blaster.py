import pyautogui
import time


reactions = [
    'cator_g',
    'cator_n',
    'cator_o',
    'cator_m',
    'cator_e',
    'cator_s'
]


def reaction_word(word: str) -> list:
    duplicate_letters: set = set()
    reactions: list[str] = []
    for letter in word:
        if letter in duplicate_letters:
            print(f'Skipping duplicate letter: {letter}')
            continue
        duplicate_letters.add(letter)
        reactions.append(f'cator_{letter}')
    return reactions


def main(reactions: list):
    # Get the current mouse position
    original_position = pyautogui.position()

    for reaction in reactions:
        # Right-click the screen
        pyautogui.rightClick()
        time.sleep(0.25)

        # Move the mouse down and right
        pyautogui.moveRel(100, 100)
        time.sleep(0.25)

        # Click the "Add Reaction" button
        pyautogui.click()
        time.sleep(0.25)

        # Type the name of the reaction
        reaction_name = reaction
        pyautogui.typewrite(reaction_name)
        time.sleep(0.25)

        # Hit return
        pyautogui.press('enter')

        # Return the mouse to the original position
        pyautogui.moveTo(original_position)
        time.sleep(0.25)

    
if __name__ == "__main__":
    # Delay 2 seconds before starting
    time.sleep(2)
    # main(reactions)
    main(reaction_word('sabcdef'))
