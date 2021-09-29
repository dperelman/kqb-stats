#!/usr/bin/env python3

import argparse
import json

from matchJson import MatchJson

parser = argparse.ArgumentParser()
parser.add_argument('file', type=argparse.FileType())
args = parser.parse_args()

with args.file as f:
    match = MatchJson(json.load(f))

try:
    match.verifyMatchStats()
    match.verifyMatchGames()
except Exception:
    print(args.file)
    print(match.summaryString())
    raise
