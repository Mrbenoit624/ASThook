import os

from utils import bprint
from static import StaticAnalysis
from dynamic import DynamicAnalysis
from log import Log
from config import Config
import parser


DIR="temp"

if __name__ == '__main__':
    parser = parser.parser()
    args = parser.parse_args()

    if args.config:
        args = Config.load(args)

    if not os.path.exists(DIR):
        os.mkdir(DIR)
    Log(args.verbose)
    st_analysis = StaticAnalysis(args, DIR)
    DynamicAnalysis(st_analysis.package, args, DIR)
