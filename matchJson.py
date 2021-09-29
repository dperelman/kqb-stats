#!/usr/bin/env python3

import json


class MatchJson:
    def __init__(self, data):
        self.data = data

    def asJson(self):
        return json.stringify(self.data)

    def summaryString(self):
        # From https://github.com/achhabra2/kqb-json-viewer/
        #      blob/main/stats/json_type.go
        win_conditions = {
            1: "Mil",
            2: "Eco",
            3: "Snail",
        }
        map_names = {
            2:  "Pod",
            4:  "BQK",
            7:  "Helix",
            11: "Tally",
            14: "Spire",
            15: "Split",
            17: "Nest",
            18: "Throne",
        }
        team_number = {
            1: "Gold",
            2: "Blue",
        }

        res = 'PLAYERS:\n'
        for num, name in team_number.items():
            nicknames = [p['nickname']
                         for p in self.data['playerMatchStats']
                         if p['team'] == num]
            res += name + ' team: ' + ', '.join(nicknames) + '\n'
        res += '\nGAMES:\n'
        for idx, game in enumerate(self.data['games']):
            res += ('Game ' + str(idx) + ': '
                    + team_number[self.data['gameWinners'][idx]]
                    + ' team won by '
                    + win_conditions[self.data['winConditions'][idx]]
                    + ' on ' + map_names[self.data['mapPool'][idx]]
                    + '\n')

        return res

    def recomputeMatchStats(self):
        self.data['playerMatchStats'] = self.recomputedMatchStats()

    def deleteGameAt(self, idx):
        per_game_arrays = ['gameWinners', 'winConditions', 'mapPool', 'games']
        for key in per_game_arrays:
            del self.data[key][idx]

        self.recomputeMatchStats()

    def recomputedMatchStats(self):
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

        all_computed_stats = []
        for idx, stats in enumerate(self.data['playerMatchStats']):
            computed_stats = {}

            for key in copied_stats:
                computed_stats[key] = stats[key]

            allBerriesInSingleGame = False
            per_game_stats = []
            for game_idx, game in enumerate(self.data['games']):
                try:
                    game_stats = game['playerStats'][idx]
                except IndexError:
                    raise Exception(stats['nickname'] + ' not in '
                                    + f'game {game_idx}. Players joining '
                                    + 'mid-match is unsupported.')
                if game_stats['nickname'] != stats['nickname']:
                    raise Exception("Nickname mismatch: "
                                    + game_stats['nickname']
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
            all_computed_stats.append(computed_stats)

        return all_computed_stats

    # Checks that the playerMatchStats is computed as expected.
    def verifyMatchStats(self):
        all_computed_stats = self.recomputedMatchStats()

        for stats, computed_stats in zip(self.data['playerMatchStats'],
                                         all_computed_stats):
            if stats != computed_stats:
                for k in stats.keys():
                    if stats[k] != computed_stats[k]:
                        raise Exception("Failed to recompute " + k
                                        + ":\nstats: " + str(stats[k])
                                        + "\ncomputed_stats: "
                                        + str(computed_stats[k]))
                raise Exception("Failed to recompute stats:\nstats: "
                                + str(stats)
                                + "\ncomputed_stats=" + str(computed_stats))

    def verifyMatchGames(self):
        num_games = len(self.data['games'])
        num_game_winners = len(self.data['gameWinners'])
        num_win_conditions = len(self.data['winConditions'])
        num_map_pool = len(self.data['mapPool'])

        if num_game_winners != num_games:
            raise Exception(f'{num_games} games, but '
                            + f'{num_game_winners} winner entries.')

        if num_win_conditions != num_games:
            raise Exception(f'{num_games} games, but '
                            + f'{num_win_conditions} win condition entries.')

        if num_map_pool < num_games:
            raise Exception(f'{num_games} games, but only '
                            + f'{num_map_pool} map pool entries.')

        win_conditions = {
            1: "Mil",
            2: "Eco",
            3: "Snail",
        }
        for idx in range(num_games):
            game_condition = self.data['games'][idx]['winCondition']
            win_condition = self.data['winConditions'][idx]

            if game_condition != win_condition:
                raise Exception(f'Game {idx} has win condition recorded '
                                + 'as both ' + win_conditions[game_condition]
                                + ' in the game and '
                                + win_conditions[win_condition]
                                + ' in the win conditions list.')

        if num_games > 5:
            raise Exception(f'Match has {num_games} games. Max is 5.')

        if self.data['gameWinners'].count(1) != 3\
                and self.data['gameWinners'].count(2) != 3:
            raise Exception('Incomplete match: neither team won 3 games.')

    def appendGamesFrom(self, other, time_gap=1000):
        per_game_arrays = ['gameWinners', 'winConditions', 'mapPool']
        # truncate mapPool
        self.data['mapPool'] = self.data['mapPool'][:len(self.data['games'])]
        for key in per_game_arrays:
            self.data[key] += other.data[key]

        last_end_time = self.data['games'][-1]['endTime']
        time_offset = last_end_time + time_gap

        example_player_stats = {player_stats['nickname']: player_stats
                                for player_stats
                                in self.data['games'][0]['playerStats']}
        keys_copied_from_example = set(['actorNr', 'inputID',
                                        'playerIndex',
                                        'playerId', 'externalPlayerId'])

        def fix_player(player):
            example = example_player_stats[player['nickname']]

            fixed_player = {}
            for key in player.keys():
                if key in keys_copied_from_example:
                    fixed_player[key] = example[key]
                else:
                    fixed_player[key] = player[key]

            return (example['playerIndex'], fixed_player)

        for game in other.data['games']:
            new_player_stats_dict = dict(map(fix_player, game['playerStats']))
            new_player_stats = [new_player_stats_dict[i]
                                for i in sorted(new_player_stats_dict.keys())]

            new_game = dict(game)
            new_game['playerStats'] = new_player_stats
            new_game['startTime'] += time_offset
            new_game['endTime'] += time_offset

            self.data['games'].append(new_game)

        self.recomputeMatchStats()
