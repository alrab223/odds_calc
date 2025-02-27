import math
import itertools
from typing import List, Dict, Tuple

def make_calculate_method(bet_type: str):
   def calculate_method(self, votes: Dict[str, Dict[str, int]]) -> List[float]:
      return self._calculate_basic_odds(votes, bet_type)
   calculate_method.__name__ = f"calculate_{bet_type.capitalize()}_Odds"
   return calculate_method

class OddsMeta(type):
   def __new__(mcls, name, bases, attrs):
      basic_bet_types = (
         "win",
         "exacta",
         "quinella",
         "bracket_quinella",
         "trio",
         "trifecta",
      )
      for bet in basic_bet_types:
         method_name = f"calculate_{bet.capitalize()}_Odds"
         if method_name not in attrs:
            attrs[method_name] = make_calculate_method(bet)
      return super().__new__(mcls, name, bases, attrs)

class Odds(metaclass=OddsMeta):
   def __init__(self):
      self.payout_rates = {
         "win": 0.80,
         "place": 0.80,
         "quinella": 0.775,
         "bracket_quinella": 0.775,
         "quinella_place": 0.775,
         "exacta": 0.75,
         "trio": 0.75,
         "trifecta": 0.725,
      }

   def _calculate_basic_odds(self, votes: Dict[str, Dict[str, int]], bet_type: str) -> List[float]:
      total_votes = sum(votes[bet_type].values())
      payout_rate = self.payout_rates[bet_type]
      odds_list = []
      for vote in votes[bet_type].values():
         if vote == 0:
            odds_list.append(0)
         else:
            odds = (total_votes * payout_rate) / vote
            odds = math.floor(odds * 10) / 10
            odds = odds if odds >= 1.0 else 1.0
            odds_list.append(odds)
      return odds_list

   def calculate_Place_Odds(self, votes: Dict[str, any]) -> List[List[float]]:
      votes_num = list(votes["place"].values())
      total_votes = sum(votes["place"].values())
      num_horses = votes["horse_starters"]
      winning_places = 3 if num_horses >= 8 else 2

      indexed_list = list(enumerate(votes_num))
      index_combinations = list(itertools.combinations(indexed_list, winning_places))
      odds_by_horse = [[] for _ in range(num_horses)]
      for horse_idx in range(num_horses):
         for combo in index_combinations:
            if any(idx == horse_idx for idx, _ in combo):
               odds_by_horse[horse_idx].append(combo)

      result_odds = []
      for horse_idx, horse_votes in enumerate(votes_num):
         if horse_votes == 0:
            result_odds.append([0, 0])
            continue
         place_odds = []
         for combo in odds_by_horse[horse_idx]:
            combo_votes = sum(votes_num[idx] for idx, _ in combo)
            remaining_votes = (total_votes - combo_votes) / winning_places
            odds = ((horse_votes + remaining_votes) * self.payout_rates["place"]) / horse_votes
            odds = math.floor(odds * 10) / 10
            odds = odds if odds >= 1.0 else 1.0
            place_odds.append(odds)
         result_odds.append([min(place_odds), max(place_odds)] if place_odds else [0, 0])
      return result_odds

   def calculate_Quinella_Place_Odds(self, votes: Dict[str, any]) -> Dict[Tuple[int, int], List[float]]:
      total_votes = sum(votes["quinella_place"].values())
      payout_rate = self.payout_rates["quinella_place"]
      num_horses = votes["horse_starters"]
      pair_list = list(itertools.combinations(range(1, num_horses + 1), 2))
      all_three_combos = list(itertools.combinations(range(1, num_horses + 1), 3))
      combos_by_pair = {combo: [] for combo in all_three_combos}
      pair_votes = {pair: [] for pair in pair_list}
      for combo in all_three_combos:
         for pair in pair_list:
            if all(item in combo for item in pair):
               vote_num = votes["quinella_place"][f"{pair[0]}-{pair[1]}"]
               combos_by_pair[combo].append(vote_num)
      for key in combos_by_pair:
         combos_by_pair[key] = sum(combos_by_pair[key])
      result = {}
      for combo, combo_votes in combos_by_pair.items():
         for pair in pair_list:
            if all(item in combo for item in pair):
               remaining_votes = (total_votes - combo_votes) / 3.0
               vote_num = votes["quinella_place"][f"{pair[0]}-{pair[1]}"]
               if vote_num == 0:
                  pair_votes[pair].append(0.0)
                  continue
               raw_odds = (vote_num + remaining_votes) * payout_rate / vote_num
               floored = math.floor(raw_odds * 10) / 10
               floored = floored if floored >= 1.0 else 1.0
               pair_votes[pair].append(floored)
      for pair, odds_list in pair_votes.items():
         result[pair] = [min(odds_list), max(odds_list)] if odds_list else [0.0, 0.0]
      return result
