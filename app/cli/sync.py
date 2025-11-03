import sys
import os
import sqlite3
import aiohttp
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv

# .env
load_dotenv()
# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/league_data.db')

# Data Dragon URL
LATEST_VERSION_URL = os.getenv('LATEST_VERSION_URL')


async def get_latest_patch():
    """Fetch the latest patch version from Data Dragon."""
    async with aiohttp.ClientSession() as session:
        async with session.get(LATEST_VERSION_URL) as response:
            versions = await response.json()
            return versions[0]


async def run_sync():
    """Sync databases with Riot API data."""
    print("db sync")
    await check_release()


async def check_release():
    """Checks stored with curr release, if release different then update"""

    # Get latest patch from Data Dragon
    latest_patch = await get_latest_patch()

    # Get stored patch from DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM patch_version WHERE id = 1")
    result = cursor.fetchone()

    db_patch = result[0] if result else None

    # Compare and update if different
    if db_patch != latest_patch:
        timestamp = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO patch_version (id, version, last_updated)
            VALUES (1, ?, ?)
        """, (latest_patch, timestamp))
        conn.commit()
        print(f"Patch updated: {db_patch} -> {latest_patch}")
    else:
        print(f"Already on latest patch: {latest_patch}")

    conn.close()


if __name__ == "__main__":
    asyncio.run(run_sync())