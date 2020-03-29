import argparse
import os

from utils import bprint
from static import StaticAnalysis
from dynamic import DynamicAnalysis
from log import Log


DIR="temp"

if __name__ == '__main__':
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


    group = parser.add_argument_group('dynamic')

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

    group.add_argument(
            '--files_store',
            action="store_true",
            help='store all files read or written by application')

    args = parser.parse_args()

    if not os.path.exists(DIR):
        os.mkdir(DIR)
    Log(args.verbose)
    st_analysis = StaticAnalysis(args.app, DIR)
    DynamicAnalysis(st_analysis.package, args, DIR)
