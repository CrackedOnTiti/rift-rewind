# RiftRewind: Jinx's Magical Rewind Machine

> An AI League of Legends coach: an interactive Summoner's Rift map with AI-written feedback for each zone, a chat coach that remembers you, and a shareable player card. Every part works in Coach or Roast mode.

🏆 **Winner of the Roast Master 3000 Prize ($1,000)** at the [AWS × Riot Games Rift Rewind hackathon](https://riftrewind.devpost.com/).

- **Devpost submission:** [Jinx's Magical Rewind Machine](https://devpost.com/software/jinx-s-workshop/)
- **Submission video:** [YouTube](https://www.youtube.com/watch?v=93rt1HThGxk)
- **Live demo:** offline. The hackathon deployment on AWS Elastic Beanstalk has been shut down. See [Run it locally](#run-it-locally).

> RiftRewind isn't affiliated with or endorsed by Riot Games. It was built for the Rift Rewind hackathon that Riot Games and AWS hosted.

## Features

All of these exist in the current code:

- **Ignite the Rewind: interactive map** (`interactive_map.html`)
  - Enter a Riot ID, a platform (16 are supported, e.g. `euw1`, `na1`, `kr`) and a mode.
  - The backend fetches the player's recent matches and timelines from the Riot API (default 10, allowed range 5–50).
  - It computes statistics for an overview plus 7 map zones: top, mid and bot lane, jungle, river, dragon pit and Baron pit.
  - Click a zone to get a 2–3 sentence story written by Claude.
  - Only the overview story is written up front. The other stories are written the first time you click their zone, then cached in DynamoDB for 7 days.
  - The map has LoL-style controls: edge-of-screen panning and zoom centred on the cursor. There's also a hidden monkey-bomb easter-egg counter.
- **Coach / Roast modes.** Coach mode gives constructive advice. Roast mode is brutally honest but still ends with something actionable. Switching modes discards the cached stories and rewrites them.
- **Player card** (`/api/generate-card`)
  - Unlocks once every zone has been discovered.
  - Pillow renders a card with your most-played champion's loading-screen art (from CommunityDragon), plus your level, rank, games played and KDA.
  - Claude writes a title and a short story for the card. If that call fails, fixed fallback text is used.
  - You can download the card, copy a share link or share it to Twitter.
- **Vi's coaching session: AI chat** (`coaching_session.html`, `/api/coach`)
  - Logging in creates a 7-day session token and stores up to 20 recent matches in DynamoDB.
  - The chat runs Claude Sonnet 4.5 on Amazon Bedrock through LangChain, with a tool-calling loop of up to 10 rounds.
  - It has 8 tools: search/get champions, search/get items, search runes, recommended builds, champion counters (all read the local SQLite database), and the player's recent matches (read from DynamoDB).
  - **Memory:** every exchange is saved to DynamoDB. Each new chat request starts with excerpts from your 3 most recent conversations plus the last 6 messages of the current chat.
- **Static game data sync.** The SQLite database is filled from Riot Data Dragon: 171 champions, 511 items and 61 runes (in 5 trees) for patch 15.22.1. A CLI command checks for a newer patch and re-syncs.
- **CLI** (`app/riftrewind.py`) for running the chat and sync pipelines from a terminal, without the frontend.

## Architecture

```
Browser (static HTML/JS served by Flask)
  index.html ──► /api/analyze ─────────┐           /api/authenticate ──► coaching_session.html
  interactive_map.html ──► /api/generate-story, /api/generate-card, /api/refresh
  coaching_session.html ──► /api/coach  │
                                        ▼
Flask app (app/backend/src/main.py), Docker on AWS Elastic Beanstalk
  ├─ API/            Riot API client (Pulsefire), Player model, match/timeline analytics,
  │                  zone stats, story + card prompt building, Bedrock client
  ├─ app/backend/src ai_chat.py (system prompt, Bedrock chat), league_tools.py (8 AI tools),
  │                  image_creation.py (Pillow player card), utils/input_validator.py
  ├─ app/cli/        client_check (login → player/match/session sync), sync (patch sync), chat
  ├─ app/data/       league_data.db (SQLite static data) + init/populate/reset scripts
  └─ db/src/         DynamoDB models, repositories, services, queries, table init
                │                        │                          │
                ▼                        ▼                          ▼
        Riot Games API          Amazon Bedrock (Claude      DynamoDB: Players, MatchHistory,
        + Data Dragon /         Sonnet 4.5, EU cross-       Conversations, Sessions,
        CommunityDragon         region inference profile)   MapStories, PlayerTitles
```

There are two databases:
- **SQLite** holds read-only game reference data, which ships in the repo as `app/data/league_data.db`.
- **DynamoDB** (on-demand billing) holds per-player state.

`db/src/init_tables.py` defines 6 tables. The `PlayerTitles` table and its query helpers exist but the web app doesn't use them.

Leftover code from development:
- `app/html_ai/` is an earlier copy of `app/cli/`.
- `app/frontend/public/js/*.js` belongs to an earlier frontend. The current pages don't load it.

## Tech stack

Versions are the ones pinned in `requirements.txt` and the `Dockerfile`. "Unpinned" means pip installs the latest version.

| Area | Technology |
|---|---|
| Language / runtime | Python 3.12 (`python:3.12-slim` image) |
| Web | Flask 3.1.2, Werkzeug 3.1.3, Jinja2 3.1.6 |
| AI | Claude Sonnet 4.5 on Amazon Bedrock (`eu.anthropic.claude-sonnet-4-5-20250929-v1:0`), LangChain + langchain-aws (unpinned) |
| AWS | boto3 / botocore 1.40.53, DynamoDB, Elastic Beanstalk (Docker on 64-bit Amazon Linux 2023, `eu-west-3`) |
| Riot data | Pulsefire (unpinned) for the Riot API, aiohttp (unpinned) for Data Dragon and CommunityDragon |
| Data / analytics | pandas 2.3.3, numpy (unpinned), SQLite |
| Images | Pillow (unpinned) with FreeType, Teko font family |
| Frontend | Vanilla HTML/CSS/JS, Tailwind CSS (Play CDN), GSAP 3.12.5, Google Fonts (Cinzel, Inter) |
| Other | python-dotenv 1.2.1, cryptography, requests 2.32.5 |
| DevOps | Docker, Docker Compose, GitHub Actions (mirrors `main` to the team members' portfolio repos) |

## Run it locally

You need:
- a Riot API key;
- AWS credentials with DynamoDB access and Bedrock access to Claude Sonnet 4.5;
- an **EU AWS region**, because the code calls the `eu.` cross-region inference profile. The project used `eu-west-3`.

Without AWS the app won't start, because the DynamoDB client is created when the app module is imported.

**1. Environment variables.** Export these in your shell or put them in a `.env` file. Never commit real values.

| Variable | Used by |
|---|---|
| `RIOT_API_KEY` | Riot API client (`API/Core.py`) |
| `AWS_DEFAULT_REGION` | DynamoDB and Bedrock. Required: startup fails without it. Use an EU region. |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | boto3 / Bedrock (or any other standard AWS credential source) |
| `LATEST_VERSION_URL` | `sync` CLI only: the Data Dragon versions endpoint, `https://ddragon.leagueoflegends.com/api/versions.json` |

**2. Create the DynamoDB tables (once).** Tables that already exist are skipped.

```bash
python db/setup_new_tables.py
```

**3a. Run with Docker Compose.** Compose uses the variables from your shell or a root `.env`. Set `AWS_DEFAULT_REGION` explicitly, because the compose default is `us-east-1`.

```bash
docker compose up --build        # serves on http://localhost (host port 80 → container 5000)
```

The Dockerfile copies `app/` wholesale. A `.env` file inside `app/` would end up in the image, so pass the variables through the environment instead.

**3b. Or run Flask directly:**

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app/backend/src/main.py   # http://localhost:5000, debug mode
```

**CLI (optional):**

```bash
python app/riftrewind.py          # commands: chat, sync, help, version, exit
```

`GET /health` returns a basic health check.

## Status and known issues

This is a finished hackathon project, built in October–November 2025. It isn't actively maintained, and the production deployment is offline. Known issues in the current code:

- **The mock-AI mode is broken.** `USE_MOCK_AI=true` makes `API/story/bedrock_client.py` import `testing.mocks.mock_ai`, but there's no `testing/` folder in the repository, so the app fails at startup. `API/story/README_MOCK_MODE.md` also refers to a `mock_client.py` that doesn't exist. Leave `USE_MOCK_AI=false`.
- **`USE_MOCK_DB` does nothing.** It appears in `docker-compose.yml` and the docs, but no code reads it, so DynamoDB is always used.
- **The coaching page's match sidebar is empty.** It calls `POST /api/matches`, but that route isn't in `main.py`: it was added on 9 Nov 2025 and lost in a late merge. The chat itself still works.
- **Two AI tools return no data.** The `recommended_builds` and `champion_counters` tables are empty in the shipped `league_data.db`, so the build and counter tools come back empty.
- **Benchmarks are hardcoded.** `API/benchmarks/benchmark_cache.json` isn't committed, so the analytics use the fallback values in `fallback_data.py`.
- **Some docs describe planned features.** Parts of the mdBook describe planned or earlier designs, and a few details differ from the code, such as the story cache TTL. Where they disagree, trust this README and the code.

## Documentation

The project's mdBook is in [`docs/JinxRiftRewind/`](docs/JinxRiftRewind/src/SUMMARY.md). It covers the problem, the features, the architecture, data management, AI integration and the team's notes on challenges. It isn't hosted anywhere; to build it locally:

```bash
mdbook serve docs/JinxRiftRewind   # requires mdbook
```

`docs/database/diagram.uml` holds the early database diagram.

## Team

| Member | Role | Responsibilities |
|--------|------|------------------|
| **Thierry B.** | Backend & Cloud Infrastructure Lead | Python/Flask backend, AWS infrastructure (Elastic Beanstalk, DynamoDB, Bedrock), AI integration with Claude Sonnet 4.5, database architecture, CLI testing tools |
| **Aymeric L.** | Riot API Integration & Frontend Lead | Riot Games API integration with Pulsefire, match data processing, map-zone analytics and story generation, interactive map implementation, frontend development (HTML/CSS/JS), coaching session interface |
| **Hugo P.** | Image Generation & DevOps Lead | Player card generation with Pillow, AI card content, Docker containerization, custom font rendering, Docker Compose setup |

There's more detail in [Team & Credits](docs/JinxRiftRewind/src/team.md).

## Acknowledgments

- **Riot Games** for organising the hackathon and providing API access and Data Dragon
- **Amazon Web Services** for the cloud infrastructure and sponsorship
- **Anthropic** for Claude Sonnet 4.5, via Amazon Bedrock
- **Open-source libraries:** Pulsefire, Flask, LangChain, Pillow, pandas, GSAP, Tailwind CSS and more
- **CommunityDragon** for the champion artwork used on player cards

## License

MIT. See [LICENSE](LICENSE).

---

*Built during a hackathon. From League players, for League players.*
