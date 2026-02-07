import pywinctl
import subprocess
import re
from logzero import logger

def run(args=None):
    connected = subprocess.check_output('adb devices -l', shell=True, text=True).split('\n')
    connected = [re.sub(r'[\s]+', ' ', line).strip() for line in connected if line.strip()]
    connected = [line.split(' ') for line in connected if 'device' in line]
    connected = [line for line in connected if line[1] == 'device']

    expected_titles = []
    for device in connected:
        serial = device[0]
        model = next((part[6:] for part in device if part.startswith("model:")), serial[-4:])
        title = f"{model}_{serial[-4:]}"
        expected_titles.append(title)

    logger.info(f"Looking for window titles: {expected_titles}")

    windows = []
    for title in expected_titles:
        try:
            win = pywinctl.getWindowsWithTitle(title)[0]
            windows.append(win)
        except Exception as e:
            logger.warning(f"Could not find window '{title}': {e}")

    if not windows:
        logger.warning("No matching scrcpy windows found.")
        return

    windows.sort(key=lambda w: w.title)
    position = get_position(len(windows))

    for i, win in enumerate(windows):
        logger.info(f"Aligning: '{win.title}' → X:{position[i][0]} Y:{position[i][1]}")
        try:
            win.moveTo(position[i][0], position[i][1])
        except Exception as e:
            logger.warning(f"Failed to move '{win.title}': {e}")

def get_position(count):
    position = []
    x, y = 0, 0
    width, height = 200, 440  # Default size used in open.py

    for i in range(count):
        if i == 0:
            pass
        elif i == 1:
            y = height + 37
        else:
            if i % 2 == 0:
                x += width
                y = 0
            else:
                y = height + 37
        position.append([x, y])
    return position

def main():
    parser = argparse.ArgumentParser(
        prog='droid-align',
        description='Arrange all active scrcpy windows in a grid layout on the screen.\n'
                    'This command automatically detects scrcpy windows by their title format\n'
                    'and positions them in an organized grid pattern for easy viewing.',
        epilog='Examples:\n'
               '  droid-align             # Arrange all scrcpy windows\n'
               '\n'
               'Window Detection:\n'
               '  - Searches for windows with title format: {model}_{serial}\n'
               '  - Only processes windows launched by scrcpy\n'
               '\n'
               'Grid Layout:\n'
               '  - Windows are sorted alphabetically by title\n'
               '  - Arranged in a 2-column grid (left/right)\n'
               '  - Default window size: 200x440 pixels\n'
               '  - Vertical spacing: 37 pixels (for title bar)\n'
               '\n'
               'Usage:\n'
               '  1. Launch devices with droid-open\n'
               '  2. Run droid-align to organize windows\n'
               '\n'
               'Note: This command takes no additional arguments.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    run()

