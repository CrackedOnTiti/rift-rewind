from ..Core import Core
from datetime import datetime
import time


class Match(Core):
    """Handles all match-related API calls"""

    # ========== BASIC API CALLS ==========

    def get_match_history(
        self, puuid, region="europe", count=20, start=0, start_time=None, end_time=None
    ):
        """Get a batch of match IDs"""
        url = self._build_region_url(
            region, f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        )

        params = {"count": count, "start": start}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        return self._make_request(url, params=params)

    def get_match_details(self, match_id, region="europe"):
        """Get detailed info about a single match"""
        url = self._build_region_url(region, f"/lol/match/v5/matches/{match_id}")
        return self._make_request(url)

    def get_match_timeline(self, match_id, region="europe"):
        """Get timeline for a single match"""
        url = self._build_region_url(
            region, f"/lol/match/v5/matches/{match_id}/timeline"
        )
        return self._make_request(url)

    # ========== COMPLEX FETCHING METHODS ==========

    def get_year_match_history(self, puuid, region="europe", year=2024):
        """
        Fetch ALL match IDs for an entire year

        Args:
            puuid: Player's PUUID
            region: Regional routing
            year: Year to fetch

        Returns:
            List of all match IDs
        """
        print(f"\n{'=' * 60}")
        print(f"  Fetching all matches for {year}")
        print(f"{'=' * 60}\n")

        all_match_ids = []

        for month in range(1, 13):
            start_time, end_time = self._get_month_timestamps(year, month)
            month_name = self._get_month_name(year, month)

            print(f"📅 {month_name}...", end=" ")

            month_matches = self._fetch_matches_with_pagination(
                puuid, region, start_time, end_time
            )

            all_match_ids.extend(month_matches)
            print(f"✓ {len(month_matches)} matches")

            time.sleep(0.5)

        print(f"\n{'=' * 60}")
        print(f"  ✅ Total: {len(all_match_ids)} matches")
        print(f"{'=' * 60}\n")

        return all_match_ids

    def get_bulk_match_details(self, match_ids, region="europe"):
        """
        Fetch details for multiple matches efficiently

        Args:
            match_ids: List of match IDs
            region: Regional routing

        Returns:
            List of match detail objects
        """
        print(f"Fetching details for {len(match_ids)} matches...")

        matches = []
        for i, match_id in enumerate(match_ids):
            match_data = self.get_match_details(match_id, region)
            if match_data:
                matches.append(match_data)

            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{len(match_ids)}")

        print(f"✓ Loaded {len(matches)} match details")
        return matches

    # ========== HELPER METHODS ==========

    def _fetch_matches_with_pagination(self, puuid, region, start_time, end_time):
        """Fetch all matches in time range with pagination"""
        all_matches = []
        start_index = 0
        batch_size = 100

        while True:
            batch = self.get_match_history(
                puuid=puuid,
                region=region,
                count=batch_size,
                start=start_index,
                start_time=start_time,
                end_time=end_time,
            )

            if not batch or len(batch) == 0:
                break

            all_matches.extend(batch)

            if len(batch) < batch_size:
                break

            start_index += batch_size
            time.sleep(0.1)

        return all_matches

    def _get_month_timestamps(self, year, month):
        """Get Unix timestamps for start/end of month"""
        start_date = datetime(year, month, 1)

        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        return int(start_date.timestamp()), int(end_date.timestamp())

    def _get_month_name(self, year, month):
        """Get formatted month name"""
        date = datetime(year, month, 1)
        return date.strftime("%B %Y")
