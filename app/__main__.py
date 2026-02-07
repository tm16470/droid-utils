from app import open as ardctl_open
from app import swipe as ardctl_swipe
from app import align as ardctl_align
from app import recover as ardctl_recover

def main():
    import argparse
    parser = argparse.ArgumentParser(prog='droid-utils')
    subparsers = parser.add_subparsers(dest='command')

    # open
    open_parser = subparsers.add_parser('open')
    open_parser.add_argument("-s", "--small-screen", action="store_true", default=False)
    open_parser.add_argument("-m", "--mid-screen", action="store_true", default=False)
    open_parser.add_argument("-l", "--large-screen", action="store_true", default=False)

    # swipe
    swipe_parser = subparsers.add_parser('swipe')
    swipe_parser.add_argument("-c", "--count", type=int, help="Swipe loop count before waiting")

    # align
    align_parser = subparsers.add_parser('align')

    # recover
    recover_parser = subparsers.add_parser('recover')

    args = parser.parse_args()

    if args.command == 'open':
        ardctl_open.run(args)
    elif args.command == 'swipe':
        ardctl_swipe.run(args)
    elif args.command == 'align':
        ardctl_align.run(args)
    elif args.command == 'recover':
        ardctl_recover.run(args)
    else:
        parser.print_help()
