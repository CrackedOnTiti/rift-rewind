# Rift Rewind - Database Architecture Guide

Complete guide to the DynamoDB database structure, models, and usage for the League of Legends AI Coach.

## Table of Contents
1. [Database Schema](#database-schema)
2. [Models](#models)
3. [Repositories](#repositories)
4. [Services](#services)
5. [Workflow](#workflow)
6. [Setup and Usage](#setup-and-usage)

---

## Database Schema

### 1. Players Table
**Purpose**: Store main player profile information

**Keys**:
- Partition Key: `puuid` (String)

**Attributes**:
- `puuid` - Player's unique Riot identifier
- `riot_id` - Name#Tag format (e.g., "Faker#KR1")
- `region` - Region code (e.g., "na1", "euw1", "kr")
- `main_role` - Main role played (TOP, JUNGLE, MID, ADC, SUPPORT)
- `main_champions` - List of top 5 champion names
- `winrate` - Overall winrate as percentage (0-100)
- `current_rank` - Map containing {tier, division, lp}
- `created_at` - ISO timestamp
- `updated_at` - ISO timestamp

**Global Secondary Index**:
- `RiotIdIndex` - Allows lookup by riot_id

### 2. MatchHistory Table
**Purpose**: Store individual match data per player (last 20 matches for hackathon)

**Keys**:
- Partition Key: `puuid` (String)
- Sort Key: `match_id` (String)

**Attributes**:
- `puuid` - Player's unique identifier
- `match_id` - Riot match ID (e.g., "NA1_4567890123")
- `timestamp` - Unix timestamp (seconds since epoch)
- `match_data` - Complete match data from Riot API (nested map)
- `created_at` - ISO timestamp

**Local Secondary Index**:
- `TimestampIndex` - Allows sorting matches by time

### 3. Conversations Table
**Purpose**: Store AI chat conversation history per player

**Keys**:
- Partition Key: `puuid` (String)
- Sort Key: `conversation_id` (String)

**Attributes**:
- `puuid` - Player's unique identifier
- `conversation_id` - Timestamp-based or UUID
- `messages` - List of message objects [{role, content, timestamp}]
- `session_id` - Optional session grouping
- `created_at` - ISO timestamp
- `updated_at` - ISO timestamp

### 4. Sessions Table
**Purpose**: Map session tokens to player PUUIDs for authentication

**Keys**:
- Partition Key: `session_token` (String - UUID)

**Attributes**:
- `session_token` - UUID session identifier
- `puuid` - Associated player PUUID
- `riot_id` - Quick reference to riot ID
- `created_at` - ISO timestamp
- `expires_at` - ISO timestamp (default: 7 days)

---

## Models

### Player Model (`db/src/models/player.py`)

```python
@dataclass
class Player:
    puuid: str
    riot_id: str
    region: str
    main_role: Optional[str]
    main_champions: Optional[List[str]]
    winrate: Optional[float]
    current_rank: Optional[RankInfo]
    created_at: Optional[str]
    updated_at: Optional[str]
```

**Methods**:
- `to_dynamodb_item()` - Convert to DynamoDB format
- `from_dynamodb_item(item)` - Create from DynamoDB item
- `update_timestamp()` - Update the updated_at field

### MatchHistory Model (`db/src/models/match_history.py`)

```python
@dataclass
class MatchHistory:
    puuid: str
    match_id: str
    timestamp: int
    match_data: Dict[str, Any]
    created_at: Optional[str]
```

**Methods**:
- `to_dynamodb_item()` - Convert to DynamoDB format
- `from_dynamodb_item(item)` - Create from DynamoDB item
- `from_riot_match(puuid, match_id, match_data)` - Create from Riot API data

### Conversation Model (`db/src/models/conversation.py`)

```python
@dataclass
class Conversation:
    puuid: str
    conversation_id: str
    messages: List[Message]
    session_id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
```

**Methods**:
- `add_message(role, content)` - Add a new message
- `to_dynamodb_item()` - Convert to DynamoDB format
- `from_dynamodb_item(item)` - Create from DynamoDB item
- `create_new(puuid, session_id)` - Create new conversation with generated ID

### Session Model (`db/src/models/session.py`)

```python
@dataclass
class Session:
    session_token: str
    puuid: str
    riot_id: str
    created_at: Optional[str]
    expires_at: Optional[str]
```

**Methods**:
- `is_expired()` - Check if session has expired
- `extend_expiry(days)` - Extend session expiry
- `create_new(puuid, riot_id, expiry_days)` - Create new session with UUID

---

## Repositories

Repository layer provides clean CRUD operations for each table.

### PlayerRepository (`db/src/repositories/player_repository.py`)

**Key Methods**:
- `get_by_puuid(puuid)` - Get player by PUUID
- `get_by_riot_id(riot_id)` - Get player by name#tag (uses GSI)
- `create(player)` - Create new player
- `update(player)` - Update existing player
- `delete(puuid)` - Delete player
- `exists(puuid)` - Check if player exists
- `update_stats(puuid, ...)` - Update player statistics

### MatchRepository (`db/src/repositories/match_repository.py`)

**Key Methods**:
- `get_match(puuid, match_id)` - Get specific match
- `get_player_matches(puuid, limit)` - Get all matches for player
- `get_recent_matches(puuid, count)` - Get N most recent matches
- `save_match(match)` - Save single match
- `save_matches(matches)` - Batch save multiple matches
- `match_exists(puuid, match_id)` - Check if match exists
- `delete_old_matches(puuid, keep_count)` - Clean up old matches

### ConversationRepository (`db/src/repositories/conversation_repository.py`)

**Key Methods**:
- `get_conversation(puuid, conversation_id)` - Get specific conversation
- `get_player_conversations(puuid, limit)` - Get all conversations
- `get_recent_conversations(puuid, count)` - Get N recent conversations
- `create_conversation(conversation)` - Create new conversation
- `update_conversation(conversation)` - Update conversation
- `add_message(puuid, conversation_id, role, content)` - Add message
- `delete_conversation(puuid, conversation_id)` - Delete conversation

### SessionRepository (`db/src/repositories/session_repository.py`)

**Key Methods**:
- `get_session(session_token)` - Get session by token
- `create_session(session)` - Create new session
- `delete_session(session_token)` - Delete session
- `is_valid_session(session_token)` - Check if valid and not expired
- `get_puuid_from_session(session_token)` - Get PUUID from session
- `extend_session(session_token, days)` - Extend session expiry

---

## Services

Service layer integrates Riot API with database operations.

### PlayerService (`db/src/services/player_service.py`)

**Purpose**: Handle player authentication, data fetching, and match syncing

**Key Methods**:

```python
def get_or_create_player(riot_id: str, region: str) -> Tuple[Optional[Player], str]
```
- Checks if player exists in database
- If not, fetches from Riot API and creates new player
- Returns (Player, status_message)

```python
def authenticate_player(riot_id: str, region: str) -> Tuple[Optional[str], Optional[Player]]
```
- Authenticates player and creates session
- Returns (session_token, Player)

```python
def sync_player_matches(puuid: str, match_count: int = 20) -> Tuple[int, str]
```
- Fetches recent matches from Riot API
- Stores new matches in database
- Cleans up old matches beyond match_count
- Returns (number_of_new_matches, status_message)

```python
def update_player_stats(puuid: str, stats: dict) -> Optional[Player]
```
- Updates player statistics (winrate, main_role, main_champions, current_rank)

```python
def get_player_overview(puuid: str) -> Optional[dict]
```
- Returns complete player profile + recent matches

### ConversationService (`db/src/services/conversation_service.py`)

**Purpose**: Manage AI conversation history

**Key Methods**:

```python
def start_new_conversation(puuid: str, session_id: Optional[str] = None) -> Conversation
```
- Creates a new conversation with generated ID

```python
def add_user_message(puuid: str, conversation_id: str, message: str) -> Optional[Conversation]
```
- Adds user message to conversation

```python
def add_assistant_message(puuid: str, conversation_id: str, message: str) -> Optional[Conversation]
```
- Adds AI assistant response to conversation

```python
def get_messages_for_ai(puuid: str, conversation_id: str) -> Optional[List[Dict]]
```
- Returns messages formatted for AI input

---

## Workflow

### Complete User Flow

```
1. User enters name#tag
   ↓
2. PlayerService.authenticate_player(riot_id, region)
   ↓
   → Check if player exists in database (by riot_id)
   → If not, fetch PUUID from Riot API
   → Create Player in database
   → Create Session
   ↓
3. PlayerService.sync_player_matches(puuid, match_count=20)
   ↓
   → Fetch match IDs from Riot API
   → For each match:
      → Check if exists in database
      → If not, fetch match details and store
   → Clean up old matches
   ↓
4. PlayerService.update_player_stats(puuid, stats)
   ↓
   → Analyze matches to calculate stats
   → Update player profile
   ↓
5. ConversationService.start_new_conversation(puuid, session_id)
   ↓
6. User chats with AI
   ↓
   → ConversationService.add_user_message(...)
   → [AI processes message with player context]
   → ConversationService.add_assistant_message(...)
```

---

## Setup and Usage

### 1. Initialize Database Tables

```bash
cd db/src
python init_tables.py
```

This creates all DynamoDB tables with proper schemas and indexes.

### 2. Test Database Connection

```bash
cd db/src
python db_handshake.py
```

### 3. Example Usage

```bash
cd db
python example_usage.py
```

See `example_usage.py` for complete workflow demonstration.

### 4. Integration with Your Application

```python
from db.src.services.player_service import PlayerService
from db.src.services.conversation_service import ConversationService

# Initialize services
player_service = PlayerService()
conversation_service = ConversationService()

# Authenticate player
session_token, player = player_service.authenticate_player("Faker#KR1", "kr")

if player:
    # Sync matches
    new_matches, status = player_service.sync_player_matches(player.puuid, match_count=20)

    # Start conversation
    conversation = conversation_service.start_new_conversation(player.puuid, session_token)

    # Add messages
    conversation_service.add_user_message(
        player.puuid,
        conversation.conversation_id,
        "Help me improve my gameplay"
    )
```

---

## Notes for Hackathon

**Current Settings**:
- 20 matches per player (expandable to 100+ post-hackathon)
- 100 conversation history limit (set high for testing, was 10)
- 7-day session expiration (authentication tokens)
- Simple authentication (no password encryption - demo only)
- No vectorized conversation storage (planned for post-hackathon)

**Security Notice**:
- ⚠️ No password authentication - anyone can "login" as anyone with just Riot ID
- For hackathon demo only - NOT production ready
- Post-hackathon: Implement Riot OAuth or password system

**Python Version**:
- Uses Python 3.12+ timezone-aware datetime (`datetime.now(timezone.utc)`)
- Deprecated `datetime.utcnow()` replaced throughout codebase
- Proper Decimal type handling for DynamoDB (no float types)

**Future Enhancements**:
- Secure authentication (Riot OAuth recommended)
- TTL (Time To Live) on sessions for auto-cleanup
- Vectorized conversation storage for semantic search
- More sophisticated caching strategies
- DynamoDB Streams for real-time analytics

---

## File Structure

```
db/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── player.py
│   │   ├── match_history.py
│   │   ├── conversation.py
│   │   └── session.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── player_repository.py
│   │   ├── match_repository.py
│   │   ├── conversation_repository.py
│   │   └── session_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── player_service.py
│   │   └── conversation_service.py
│   ├── init_tables.py
│   └── db_handshake.py
├── example_usage.py
└── DATABASE_GUIDE.md
```

---

## Support

For issues or questions about the database architecture:
1. Check this guide first
2. Review the example_usage.py script
3. Examine the service layer for integration patterns
4. Check the repository layer for CRUD operations
