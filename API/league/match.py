from ..Core import Core


class Match(Core):
    def get_match_history(
        self, puuid, region="europe", count=20, start_time=None, end_time=None
    ):
        base_url = self.REGION_URLS[region]
        url = f"{base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids"

        params = {"count": count}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        return self._make_request(url, params=params)

    def get_match_details(self, match_id, region="europe"):
        base_url = self.REGION_URLS[region]
        url = f"{base_url}/lol/match/v5/matches/{match_id}"

        return self._make_request(url)

    def get_match_timeline(self, match_id, region="europe"):
        base_url = self.REGION_URLS[region]
        url = f"{base_url}/lol/match/v5/matches/{match_id}/timeline"

        return self._make_request(url)
