
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
            '--config_xxhdpi',
            type=str,
            help='adding xxhdpi files from google api downloader')

    parser.add_argument(
            '--verbose',
            #action="store_true",
            type=str,
            choices=['debug', 'info', 'warning'],
            help='active verbose')

    parser.add_argument(
            '--verbose_position',
            action="store_true",
            help='give verbose position ')

    parser.add_argument(
            '--config',
            type=str,
            help="Load config file")

    parser.add_argument(
            '--output',
            type=str,
            default="none",
            choices=["none", "json"])

    parser.add_argument(
            '--output-file',
            type=str,
            )

    parser.add_argument(
            '--sdktools',
            type=str,
            help='path of the sdktools for the emulation and some android sdk' \
            'tools like the compilation of apk')

    group = parser.add_argument_group('core_static')

    group.add_argument(
            "--tree",
            action="store_true",
            help="Active syntaxical analyse")

    group.add_argument(
            "--tree_path",
            type=str,
            nargs="+",
            help="Analyse only a portion of apk")

    group.add_argument(
            "--tree_exclude",
            type=str,
            nargs="+",
            help="Expludes directory to analyszed")
    
    group.add_argument(
            '--decompiler',
            type=str,
            default="none",
            choices=["none", "jd-gui", "cfr", "procyon", "fernflower", "jadx"])

    group.add_argument(
            '--progress',
            action="store_true",
            help="Display percent when it analyse static code")

    group.add_argument(
            '--graph_ast',
            action="store_true",
            help="Draw a AST graph of the apk source code")
    
    group.add_argument(
            '--debug_ast',
            action="store_true",
            help="print error encounter during the browsing of AST")

    group = parser.add_argument_group('static')

    for name, desc, func, action, nargs in get_static_modules():
        if action == bool:
            group.add_argument(
                    "--%s" % name,
                    action="store_true",
                    help=desc)
        else:
            if nargs == 1:
                group.add_argument(
                        "--%s" % name,
                        type=action,
                        help=desc)
            else:
                group.add_argument(
                        "--%s" % name,
                        type=action,
                        nargs=nargs,
                        help=desc)


    group = parser.add_argument_group('core_dynamic')

    group.add_argument(
            '--env_apks',
            type=str,
            nargs="+")

    group.add_argument(
            '--phone',
            type=str,
            help='phones target emulator -list-avds')

    group.add_argument(
            '--no-emulation',
            action="store_true",
            help="use a physical phone (useful for buetooth option)")
    
    group.add_argument(
            '--noinstall',
            action="store_true",
            help="Application will not be installed and suggest that it was "\
            "already install")

    group.add_argument(
            '--proxy',
            type=str,
            help='setup proxy address <ip>:<port>')

    group.add_argument(
            '--proxy_cert',
            type=str,
            help='setup proxy address <filename>.cer')
    
    group.add_argument(
            '--no_erase',
            action="store_true",
            help='no erase data of phones')


    group = parser.add_argument_group('dynamic')
    for name, desc, func, action, nargs in get_dynamic_modules():
        if action == bool:
            group.add_argument(
                    "--%s" % name,
                    action="store_true",
                    help=desc)
        else:
            if nargs == 1:
                group.add_argument(
                        "--%s" % name,
                        type=action,
                        help=desc)
            else:
                group.add_argument(
                        "--%s" % name,
                        type=action,
                        nargs=nargs,
                        help=desc)
    return parser

