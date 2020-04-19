
import argparse

from dynamic.module.register import get_dynamic_modules
from static.module.register import get_static_modules

def parser():
    parser = argparse.ArgumentParser(
            description='Analysis for smartphone')

    parser.add_argument(
            'app',
            type=str,
            help='app target <filename.apk>')

    parser.add_argument(
            '--verbose',
            action="store_true",
            help='active verbose')

    parser.add_argument(
            '--config',
            type=str,
            help="Load config file")

    group = parser.add_argument_group('core_static')

    group.add_argument(
            "--tree",
            action="store_true",
            help="Active syntaxical analyse")

    group.add_argument(
            "--tree_path",
            type=str,
            help="Analyse only a portion of apk")

    group = parser.add_argument_group('static')

    for name, desc, func, action, nargs in get_static_modules():
        if action == "bool":
            group.add_argument(
                    "--%s" % name,
                    action="store_true",
                    help=desc)
        elif action == "str":
            if nargs == 1:
                group.add_argument(
                        "--%s" % name,
                        type=str,
                        help=desc)
            else:
                group.add_argument(
                        "--%s" % name,
                        type=str,
                        nargs=nargs,
                        help=desc)


                group = parser.add_argument_group('core_dynamic')

    group.add_argument(
            '--emulator',
            type=str,
            help='path of the emulator if used')

    group.add_argument(
            '--phone',
            type=str,
            help='phones target emulator -list-avds')

    group.add_argument(
            '--proxy',
            type=str,
            help='setup proxy address <ip>:<port>')

    group.add_argument(
            '--proxy_cert',
            type=str,
            help='setup proxy address <filename>.cer')


    group = parser.add_argument_group('dynamic')
    for name, desc, func, action in get_dynamic_modules():
        if action == "bool":
            group.add_argument(
                    "--%s" % name,
                    action="store_true",
                    help=desc)
        elif action == "str":
            group.add_argument(
                    "--%s" % name,
                    type=str,
                    help=desc)
    return parser

