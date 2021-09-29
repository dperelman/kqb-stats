#!/usr/bin/env python3

import argparse
import json

from matchJson import MatchJson

parser = argparse.ArgumentParser()
parser.add_argument('infile1', type=argparse.FileType())
parser.add_argument('infile2', type=argparse.FileType())
parser.add_argument('outfile', type=argparse.FileType('w'))
parser.add_argument('--time-gap', type=int, default=1000)
args = parser.parse_args()

with args.infile1 as f:
    match = MatchJson(json.load(f))

with args.infile2 as f:
    to_append = MatchJson(json.load(f))

match.appendGamesFrom(to_append, args.time_gap)

json.dump(match.data, args.outfile)

try:
    match.verifyMatchStats()
    match.verifyMatchGames()
    print(match.summaryString())
except Exception:
    print(match.summaryString())
    raise
