from API.riot.account import RiotAccountAPI
from API.league.summoner import Summoner
from API.league.rank import Rank
from API.league.match import Match
from API.league.mastery import ChampionMastery


class Player:
    def __init__(self, game_name, tag_line, region="europe", platform="euw1"):
        self.game_name = game_name
        self.tag_line = tag_line
        self.region = region
        self.platform = platform

        # API clients
        self._account_api = RiotAccountAPI()
        self._summoner_api = Summoner()
        self._rank_api = Rank()
        self._match_api = Match()
        self._mastery_api = ChampionMastery()

        # Data storage
        self.puuid = None
        self.summoner_info = None
        self.rank_info = None
        self.match_history = []
        self.matches = []
        self.champion_mastery = None

    def load_profile(self):
        print(f"Loading profile: {self.game_name}#{self.tag_line}")

        self.puuid = self._account_api.get_puuid(
            self.game_name, self.tag_line, self.region
        )
        if not self.puuid:
            print("Failed to get PUUID")
            return False

        self.summoner_info = self._summoner_api.get_summoner_infos(
            self.puuid, self.platform
        )
        self.rank_info = self._rank_api.get_rank_info(
            self.puuid, self.platform, by_puuid=True
        )
        self.champion_mastery = self._mastery_api.get_top_masteries(
            self.puuid, self.platform, count=5
        )

        print(f"Profile loaded")
        return True

    def load_year_matches(self, year=2024):
        self.match_history = self._match_api.get_year_match_history(
            self.puuid, self.region, year
        )
        return self.match_history

    def load_match_details(self):
        self.matches = self._match_api.get_bulk_match_details(
            self.match_history, self.region
        )
        return self.matches

    def __str__(self):
        rank_str = "Unranked"
        if self.rank_info:
            for queue in self.rank_info:
                if queue["queueType"] == "RANKED_SOLO_5x5":
                    rank_str = f"{queue['tier']} {queue['rank']}"
        return f"Player({self.game_name}#{self.tag_line}, {rank_str})"
