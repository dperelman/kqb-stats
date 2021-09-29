#!/usr/bin/env python3

import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('file', type=argparse.FileType())
args = parser.parse_args()

with args.file as f:
    d = json.load(f)

copied_stats = [
    'nickname',
    'inputID',
    'actorNr',
    'playerId',
    'playerIndex',
    'dropped',
    'team',
    'entityType',
    'entitySkin',
    'ping',
]
summed_stats = {
    'kills': ['totalKillCount'],
    'queenKills': ['totalQueenKillCount'],
    'deaths': ['totalDeathCount'],
    'berries': ['totalBerryDeposits'],
    'berryThrowIns': ['totalBerryThrowIns'],
    'glances': ['totalGlanceCount'],
    'snail': ['totalSnailDistance'],
    'snailDeaths': ['totalSnailDeaths'],
}
max_stats = {
    'mostQueenKillsInAMatch': 'totalQueenKillCount',
    'mostKillsPerLife': 'mostKillsPerLife',
}
special_stats = ['allBerriesInSingleGame']

for idx, stats in enumerate(d['playerMatchStats']):
    computed_stats = {}

    for key in copied_stats:
        computed_stats[key] = stats[key]

    allBerriesInSingleGame = False
    per_game_stats = []
    for game in d['games']:
        game_stats = game['playerStats'][idx]
        if game_stats['nickname'] != stats['nickname']:
            raise Exception("Nickname mismatch: " + game_stats['nickname']
                            + " != " + stats['nickname'])
        per_game_stats.append(game_stats)
        if game_stats['totalBerryDeposits'] == game['berriesNeeded']:
            allBerriesInSingleGame = True

    for key, to_sum in summed_stats.items():
        computed_stats[key] = sum([sum(g[k] for k in to_sum)
                                   for g in per_game_stats])

    for key, max_key in max_stats.items():
        computed_stats[key] = max(g[max_key] for g in per_game_stats)

    computed_stats['allBerriesInSingleGame'] = allBerriesInSingleGame

    if stats != computed_stats:
        print(args.file)
        print(idx)

        for k in stats.keys():
            if stats[k] != computed_stats[k]:
                raise Exception("Failed to recompute " + k
                                + ":\nstats: " + str(stats[k])
                                + "\ncomputed_stats: "
                                + str(computed_stats[k]))
        raise Exception("Failed to recompute stats:\nstats: " + str(stats)
                        + "\ncomputed_stats=" + str(computed_stats))
