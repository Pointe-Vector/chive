import argparse
import logging

from pointevector.chive import commands

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

root_parser = argparse.ArgumentParser(prog="chive")
root_parser.set_defaults(func=lambda _: root_parser.print_help())
root_subparsers = root_parser.add_subparsers()


commands.init_cfg(root_subparsers)
commands.list_cfg(root_subparsers)
commands.append_cfg(root_subparsers)
commands.verify_cfg(root_subparsers)
commands.remove_cfg(root_subparsers)
commands.check_cfg(root_subparsers)


args, _ = root_parser.parse_known_args()
args.func(args)
