import json
import itertools
from odds_calc.betting_app.utils import assign_frames


def create_vote_data_with_bracket(horse_starters: int) -> dict:
   data = {
      "horse_starters": horse_starters,
      "win": {str(i): 0 for i in range(1, horse_starters + 1)},
      "place": {str(i): 0 for i in range(1, horse_starters + 1)},
   }
   combos2 = [
      "{}-{}".format(i, j)
      for i, j in itertools.combinations(range(1, horse_starters + 1), 2)
   ]
   data["quinella"] = {combo: 0 for combo in combos2}
   data["quinella_place"] = {combo: 0 for combo in combos2}
   if horse_starters >= 8:
      groups = assign_frames(horse_starters)
      frames = list(range(1, 9))
      bracket_combos = [
         "{}-{}".format(i, j) for i, j in itertools.combinations(frames, 2)
      ]
      data["bracket_quinella"] = {combo: 0 for combo in bracket_combos}
   perms2 = [
      "{}-{}".format(i, j)
      for i in range(1, horse_starters + 1)
      for j in range(1, horse_starters + 1)
      if i != j
   ]
   data["exacta"] = {perm: 0 for perm in perms2}
   combos3 = [
      "{}-{}-{}".format(i, j, k)
      for i, j, k in itertools.combinations(range(1, horse_starters + 1), 3)
   ]
   data["trio"] = {combo: 0 for combo in combos3}
   perms3 = [
      "{}-{}-{}".format(i, j, k)
      for i in range(1, horse_starters + 1)
      for j in range(1, horse_starters + 1)
      for k in range(1, horse_starters + 1)
      if i != j and j != k and i != k
   ]
   data["trifecta"] = {perm: 0 for perm in perms3}
   return data


def save_vote_data(filepath: str, data: dict) -> None:
   with open(filepath, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=2)


def load_vote_data(filepath: str) -> dict:
   with open(filepath, "r", encoding="utf-8") as f:
      return json.load(f)
