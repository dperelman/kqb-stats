#!/usr/bin/env python3

import argparse
import json

from matchJson import MatchJson

parser = argparse.ArgumentParser()
parser.add_argument('game_idx', type=int)
parser.add_argument('infile', type=argparse.FileType())
parser.add_argument('outfile', type=argparse.FileType('w'))
args = parser.parse_args()

with args.infile as f:
    match = MatchJson(json.load(f))

match.deleteGameAt(args.game_idx)

json.dump(match.data, args.outfile)

try:
    match.verifyMatchStats()
    match.verifyMatchGames()
    print(match.summaryString())
except Exception:
    print(match.summaryString())
    raise
