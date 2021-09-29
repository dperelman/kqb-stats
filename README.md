# kqb-stats
helper scripts for manipulating match stats JSON files for the game Killer Queen Black

## check-match-stats
Checks if file is a valid match in a few ways.
Mainly exists to make sure my definition of "valid match" is correct,
but also has a `-v`/`--verbose` flag for displaying basic match info:
```sh
./check-match-stats.py -v Custom-2021-09-12-17-26-39.json
PLAYERS:
Gold team: PaderBall, Kzoo, ZeroPlus, aebonyne
Blue team: murmurtwin, TexasArchAngel, Pampers, NiceAtPingPong

GAMES:
Game 0: Gold team won by Mil on Throne
Game 1: Blue team won by Eco on BQK
Game 2: Blue team won by Eco on Pod
Game 3: Blue team won by Eco on Spire
```

## drop-game
Removes a game from a match and repairs the summary stats.
Outputs to a new JSON file.
Note the output may be an invalid match if you delete a game won by the winner of the match.
```sh
./drop-game.py 1 Custom-2021-09-12-17-26-39.json out.json
PLAYERS:
Gold team: PaderBall, Kzoo, ZeroPlus, aebonyne
Blue team: murmurtwin, TexasArchAngel, Pampers, NiceAtPingPong

GAMES:
Game 0: Gold team won by Mil on Throne
Game 1: Blue team won by Eco on Pod
Game 2: Blue team won by Eco on Spire

Traceback (most recent call last):
  File "/home/anyoneeb/workspace/kqb-stats/./drop-game.py", line 23, in <module>
    match.verifyMatchGames()
  File "/home/anyoneeb/workspace/kqb-stats/matchJson.py", line 183, in verifyMatchGames
    raise Exception('Incomplete match: neither team won 3 games.')
Exception: Incomplete match: neither team won 3 games.
```

## merge-sets
Creates a new match JSON with all of the games in the first followed by all of the games in the second.
Outputs to a new JSON file.
Note the output may be an invalid match.

Optional `--time-gap SECONDS` argument modifies how to adjust the `startTime` and `endTime` fields of the second file.
Defaults to 1000 seconds.
```sh
./merge-sets.py Custom-2021-09-12-17-26-39.json Custom-2021-09-12-17-26-39.json out2.json
PLAYERS:
Gold team: PaderBall, Kzoo, ZeroPlus, aebonyne
Blue team: murmurtwin, TexasArchAngel, Pampers, NiceAtPingPong

GAMES:
Game 0: Gold team won by Mil on Throne
Game 1: Blue team won by Eco on BQK
Game 2: Blue team won by Eco on Pod
Game 3: Blue team won by Eco on Spire
Game 4: Gold team won by Mil on Throne
Game 5: Blue team won by Eco on BQK
Game 6: Blue team won by Eco on Pod
Game 7: Blue team won by Eco on Spire

Traceback (most recent call last):
  File "/home/anyoneeb/workspace/kqb-stats/./merge-sets.py", line 27, in <module>
    match.verifyMatchGames()
  File "/home/anyoneeb/workspace/kqb-stats/matchJson.py", line 179, in verifyMatchGames
    raise Exception(f'Match has {num_games} games. Max is 5.')
Exception: Match has 8 games. Max is 5.
```
