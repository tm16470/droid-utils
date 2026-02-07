import pywinctl
import pyautogui
import time
import platform
import math
import random
import argparse
from logzero import logger
from tqdm import tqdm

second_per_unit = 0.1
pyautogui.FAILSAFE = False

def run(args=None):
    max_loops = args.count if args and args.count else None
    coordinate = get_coordinates()
    count = 1

    if max_loops:
        logger.info(f"Starting swipe loop: {max_loops} iterations")
    else:
        logger.info("Starting infinite swipe loop (press Ctrl+C to stop)")

    while True:
        for n in range(len(coordinate)):
            x = coordinate[n][0]
            y_start = coordinate[n][1]
            y_end = coordinate[n][2]
            logger.info(f"count {count}: {n + 1}: swiping from ({x}, {y_start}) to ({x}, {y_end})")
            pyautogui.moveTo(x, y_start)
            pyautogui.mouseDown()
            pyautogui.moveTo(x, y_end)
            pyautogui.mouseUp()
            time.sleep(second_per_unit)

        # max_loopsが指定されている場合、カウントをチェック
        if max_loops and count >= max_loops:
            logger.info(f"Completed {max_loops} loop(s). Exiting.")
            break

        wait_second = round(random.uniform(10.0, 12.0), 1)
        logger.info(f"Waiting {wait_second} seconds before next swipe set...")
        for _ in tqdm(range(int(wait_second * 10))):
            time.sleep(0.1)

        count += 1

def get_coordinates():
    coordinate = []
    windows = [w for w in pywinctl.getAllWindows() if '_' in w.title and len(w.title) >= 5]

    for win in windows:
        try:
            box = win.getClientFrame()
            x = box.left + (box.right - box.left) // 2
            y_start = box.top + (box.bottom - box.top) // 2
            y_end = box.top  # swipe to the top of the window
            coordinate.append([x, y_start, y_end])
        except Exception as e:
            logger.warning(f"Could not get window geometry for '{win.title}': {e}")

    if not coordinate:
        logger.error("No usable scrcpy windows found.")
        exit(1)

    return coordinate

def main():
    parser = argparse.ArgumentParser(
        prog='droid-swipe',
        description='Simulate swipe-down gestures on all scrcpy windows using pyautogui.\n'
                    'This command automates the swipe gesture on detected scrcpy windows,\n'
                    'useful for refreshing content or automating repetitive tasks.\n'
                    '\n'
                    'By default, runs infinitely until interrupted with Ctrl+C.',
        epilog='Examples:\n'
               '  droid-swipe             # Run infinite swipe loop (press Ctrl+C to stop)\n'
               '  droid-swipe -c 5        # Run exactly 5 swipe loops then exit\n'
               '  droid-swipe -c 10       # Run exactly 10 swipe loops then exit\n'
               '  droid-swipe --count 3   # Run exactly 3 swipe loops then exit\n'
               '\n'
               'Behavior:\n'
               '  - Detects all scrcpy windows automatically\n'
               '  - Swipes from center to top of each window\n'
               '  - Wait 10-12 seconds (random) between loop sets\n'
               '  - Shows progress bar during wait time\n'
               '\n'
               'Options:\n'
               '  No -c option:  Runs forever until Ctrl+C\n'
               '  With -c N:     Runs exactly N loops then exits\n'
               '\n'
               'Safety:\n'
               '  - PyAutoGUI FAILSAFE is disabled\n'
               '  - Use Ctrl+C to safely interrupt infinite loops\n'
               '\n'
               'Requirements:\n'
               '  - Active scrcpy windows must be visible on screen\n'
               '  - Windows must have title format: {model}_{serial}',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-c", "--count", 
        type=int, 
        metavar='N',
        help="Number of loop iterations to run (omit for infinite loop)"
    )
    args = parser.parse_args()
    
    try:
        run(args)
    except KeyboardInterrupt:
        logger.info("\nSwipe loop interrupted by user. Exiting.")
        exit(0)

