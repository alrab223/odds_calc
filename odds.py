import math
import itertools
from typing import List, Dict, Tuple


class Odds:
   def __init__(self):
      # 払戻率の定義
      self.payout_rates = {
         "win": 0.80,  # 単勝
         "place": 0.80,  # 複勝
         "quinella": 0.775,  # 馬連
         "bracket_quinella": 0.775,  # 枠連
         "quinella_place": 0.775,  # ワイド
         "exacta": 0.75,  # 馬単
         "trio": 0.75,  # 三連複
         "trifecta": 0.725,  # 三連単
      }

   def _calculate_basic_odds(self, votes: List[int], bet_type: str) -> List[float]:
      """
      基本的なオッズ計算のための共通メソッド
      """
      total_votes = sum(votes)
      payout_rate = self.payout_rates[bet_type]

      odds_list = []
      for vote in votes:
         if vote == 0:
            odds_list.append(0)
         else:
            odds = (total_votes * payout_rate) / vote
            odds = math.floor(odds * 10) / 10

      return [
         1.0 if x <= 1.0 and bet_type != "trio" and bet_type != "trifecta" else x
         for x in odds_list
      ]

   def calculate_Win_Odds(self, votes: List[int]) -> List[float]:
      return self._calculate_basic_odds(votes, "win")

   def calculate_Exacta_Odds(self, votes: List[int]) -> List[float]:
      return self._calculate_basic_odds(votes, "exacta")

   def calculate_Quinella_Odds(self, votes: List[int]) -> List[float]:
      return self._calculate_basic_odds(votes, "quinella")

   def calculate_Bracket_Quinella(self, votes: List[int]) -> List[float]:
      return self._calculate_basic_odds(votes, "bracket_quinella")

   def calculate_Trio_Odds(self, votes: List[int]) -> List[float]:
      return self._calculate_basic_odds(votes, "trio")

   def calculate_Trifecta_Odds(self, votes: List[int]) -> List[float]:
      return self._calculate_basic_odds(votes, "trifecta")

   def calculate_Place_Odds(self, votes: List[int]) -> List[List[float]]:
      """
      複勝オッズの計算（特殊なロジックのため個別に実装）
      """
      total_votes = sum(votes)
      num_horses = len(votes)
      winning_places = 3 if num_horses >= 8 else 2

      indexed_list = list(enumerate(votes))
      index_combinations = list(itertools.combinations(indexed_list, winning_places))

      odds_by_horse = [[] for _ in range(num_horses)]
      for horse_idx in range(num_horses):
         for combo in index_combinations:
            if any(idx == horse_idx for idx, _ in combo):
               odds_by_horse[horse_idx].append(combo)

      result_odds = []
      for horse_idx, horse_votes in enumerate(votes):
         if horse_votes == 0:
            result_odds.append([0, 0])
            continue

         place_odds = []
         for combo in odds_by_horse[horse_idx]:
            combo_votes = sum(votes[idx] for idx, _ in combo)
            remaining_votes = (total_votes - combo_votes) / winning_places
            odds = (
               (horse_votes + remaining_votes)
               * self.payout_rates["place"]
               / horse_votes
            )
            odds = math.floor(odds * 10) / 10
            place_odds.append(odds)

         if place_odds:
            result_odds.append([min(place_odds), max(place_odds)])
         else:
            result_odds.append([0, 0])

      return result_odds

   def calculate_Quinella_Place_Odds(
      self, votes: Dict[str, int]
   ) -> Dict[Tuple[int, int], List[float]]:
      total_votes = sum(list(votes.values()))
      payout_rate = self.payout_rates.get("quinella_place", 0.0)
      num_horses = 7

      # 全ワイド組み合わせを列挙 (i < j)
      pair_list = list(itertools.combinations(range(1, num_horses + 1), 2))

      # 全ての勝馬のパターンを列挙
      all_three_combos = list(itertools.combinations(range(1, num_horses + 1), 3))
      # ペアごとに、含まれる3頭コンボを集める
      combos_by_pair = {pair: [] for pair in all_three_combos}
      pair_votes = {pair: [] for pair in pair_list}
      for combo in all_three_combos:
         for i in pair_list:
            if all(item in combo for item in i):
               vote_num = votes[f"{i[0]}-{i[1]}"]
               combos_by_pair[combo].append(vote_num)

      # リストの合計を取得
      for key in combos_by_pair:
         combos_by_pair[key] = sum(combos_by_pair[key])
      result = {}

      for i, j in combos_by_pair.items():
         for k in pair_list:
            if all(item in i for item in k):
               remaining_votes = (total_votes - j) / 3.0
               vote_num = votes[f"{k[0]}-{k[1]}"]
               raw_odds = (vote_num + remaining_votes) * payout_rate / vote_num
               floored = math.floor(raw_odds * 10) / 10
               pair_votes[k].append(floored)
      for i, j in pair_votes.items():
         if j:
            result[i] = [min(j), max(j)]
         else:
            result[i] = [0.0, 0.0]

      return result
