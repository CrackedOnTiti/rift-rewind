from ..Core import Core


class Summoner(Core):
    def get_summoner_infos(self, puuid, platform="euw1"):
        base_url = self.SERVERS_URLS[platform]
        url = f"{base_url}/lol/summoner/v4/summoners/by-puuid/{puuid}"

        return self._make_request(url)
