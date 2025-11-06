# Rift Rewind - Database Architecture

## Overview

This document provides a visual overview of the complete database architecture and data flow.

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                        │
│  (CLI, Flask Backend, Frontend)                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                            │
│  ┌──────────────────┐        ┌───────────────────────┐      │
│  │ PlayerService    │        │ ConversationService   │      │
│  │                  │        │                       │      │
│  │ - authenticate   │        │ - start_conversation  │      │
│  │ - sync_matches   │        │ - add_message         │      │
│  │ - update_stats   │        │ - get_history         │      │
│  └──────────────────┘        └───────────────────────┘      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                   REPOSITORY LAYER                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Player   │  │ Match    │  │ Conver-  │  │ Session  │    │
│  │ Repo     │  │ Repo     │  │ sation   │  │ Repo     │    │
│  │          │  │          │  │ Repo     │  │          │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                       MODEL LAYER                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Player   │  │ Match    │  │ Conver-  │  │ Session  │    │
│  │ Model    │  │ History  │  │ sation   │  │ Model    │    │
│  │          │  │ Model    │  │ Model    │  │          │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                    AWS DYNAMODB                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Players  │  │ Match    │  │ Conver-  │  │ Sessions │    │
│  │ Table    │  │ History  │  │ sations  │  │ Table    │    │
│  │          │  │ Table    │  │ Table    │  │          │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow: Complete User Journey

```
┌────────────────────────────────────────────────────────────────┐
│ STEP 1: User Authentication                                     │
└────────────────────────────────────────────────────────────────┘

User enters: "Faker#KR1"
         ↓
┌─────────────────────────────────────────┐
│ PlayerService.authenticate_player()     │
│                                         │
│ 1. Check Players table (RiotIdIndex)   │
│    ├─ Found? → Return existing player  │
│    └─ Not found? ↓                     │
│                                         │
│ 2. Query Riot API for PUUID            │
│    (API/riot/account.py)               │
│                                         │
│ 3. Create Player in database           │
│                                         │
│ 4. Create Session token                │
│    Store in Sessions table             │
└─────────────────────────────────────────┘
         ↓
    session_token + player object


┌────────────────────────────────────────────────────────────────┐
│ STEP 2: Match History Sync                                      │
└────────────────────────────────────────────────────────────────┘

PlayerService.sync_player_matches(puuid, count=20)
         ↓
┌─────────────────────────────────────────┐
│ 1. Query Riot API for match IDs        │
│    (API/league/match.py)               │
│    → Get list of 20 match IDs          │
│                                         │
│ 2. For each match_id:                  │
│    ├─ Check if exists in MatchHistory │
│    │   table (match_exists())          │
│    │                                    │
│    ├─ If not exists:                   │
│    │   ├─ Fetch match details from API│
│    │   └─ Store in MatchHistory table │
│    │                                    │
│    └─ If exists: Skip                  │
│                                         │
│ 3. Clean up old matches                │
│    (keep only 20 most recent)          │
└─────────────────────────────────────────┘
         ↓
    20 matches stored in database


┌────────────────────────────────────────────────────────────────┐
│ STEP 3: Stats Calculation & Update                             │
└────────────────────────────────────────────────────────────────┘

PlayerService.update_player_stats(puuid, stats)
         ↓
┌─────────────────────────────────────────┐
│ Calculate from 20 matches:              │
│ - Overall winrate                       │
│ - Most played role                      │
│ - Top 5 champions                       │
│ - Current rank                          │
│                                         │
│ Update Players table                    │
└─────────────────────────────────────────┘
         ↓
    Updated player profile


┌────────────────────────────────────────────────────────────────┐
│ STEP 4: AI Conversation                                         │
└────────────────────────────────────────────────────────────────┘

ConversationService.start_new_conversation(puuid, session_id)
         ↓
┌─────────────────────────────────────────┐
│ 1. Create Conversation with ID          │
│    (timestamp + UUID)                   │
│                                         │
│ 2. Store in Conversations table        │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ User types message                      │
│                                         │
│ ConversationService.add_user_message()  │
│ - Append to messages list              │
│ - Update Conversations table           │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ AI processes with context:              │
│ - Player profile                        │
│ - Match history                         │
│ - Previous conversation                 │
│                                         │
│ (AWS Bedrock - Claude)                  │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ ConversationService.                    │
│     add_assistant_message()             │
│                                         │
│ - Append AI response                   │
│ - Update Conversations table           │
└─────────────────────────────────────────┘
         ↓
    Complete conversation history stored
```

## Database Schema Relationships

```
┌──────────────────────────────────────────────────────────────┐
│                         PUUID (Primary Key)                   │
│                               ↓                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                                                         │  │
│  ↓                          ↓                             ↓  │
┌──────────────┐    ┌──────────────────┐    ┌────────────────┐│
│   Players    │    │  MatchHistory    │    │ Conversations  ││
│              │    │                  │    │                ││
│ PK: puuid    │    │ PK: puuid        │    │ PK: puuid      ││
│              │    │ SK: match_id     │    │ SK: conv_id    ││
│ riot_id      │    │                  │    │                ││
│ region       │    │ timestamp        │    │ messages[]     ││
│ main_role    │    │ match_data       │    │ session_id     ││
│ main_champs  │    │                  │    │                ││
│ winrate      │    │ [20 matches]     │    │ [N convos]     ││
│ current_rank │    │                  │    │                ││
└──────────────┘    └──────────────────┘    └────────────────┘
       │                                              ↑
       │                                              │
       │ riot_id                           session_id│
       │ puuid                                        │
       ↓                                              │
┌────────────────┐                                   │
│   Sessions     │───────────────────────────────────┘
│                │
│ PK: sess_token │
│                │
│ puuid          │
│ riot_id        │
│ expires_at     │
│                │
│ [Auth tokens]  │
└────────────────┘
```

## Query Patterns

### 1. Player Lookup by Name#Tag
```
Query: Players table → RiotIdIndex (GSI)
Input: riot_id = "Faker#KR1"
Output: Player object with PUUID
```

### 2. Get Player's Recent Matches
```
Query: MatchHistory table → TimestampIndex (LSI)
Input: puuid = "xxx", sort by timestamp DESC, limit = 20
Output: List of 20 most recent matches
```

### 3. Get Player's Conversation History
```
Query: Conversations table
Input: puuid = "xxx", sort by conversation_id DESC, limit = 100
Output: List of 100 most recent conversations (configurable for testing)
```

### 4. Validate Session
```
Query: Sessions table
Input: session_token = "uuid"
Check: expires_at > now()
Output: Boolean (valid/invalid)
```

## Index Strategy

### Global Secondary Index (GSI)
- **Players.RiotIdIndex**: Allows quick lookup by riot_id without knowing PUUID
- **Use Case**: Initial authentication when user enters name#tag

### Local Secondary Index (LSI)
- **MatchHistory.TimestampIndex**: Sort matches chronologically
- **Use Case**: Get most recent matches for analysis

## Caching Strategy

```
┌────────────────────────────────────────────────────────────┐
│ Application requests player data                            │
└────────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────────┐
│ 1. Check DynamoDB (Players table)                          │
│    ├─ Found? → Return from database (fast!)               │
│    └─ Not found? ↓                                         │
└────────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────────┐
│ 2. Fetch from Riot API (slower, rate-limited)             │
│    └─ Store in database for future use                    │
└────────────────────────────────────────────────────────────┘
                        ↓
                   Return data

Benefits:
- Reduces Riot API calls (rate limits!)
- Faster response times
- Historical data preservation
- Works offline with cached data
```

## Scalability Considerations

### Current (Hackathon)
- 20 matches per player
- Simple session tokens
- No data encryption

### Future (Post-Hackathon)
- 100+ matches per player
- TTL on sessions for auto-cleanup
- Encrypted sensitive data
- DynamoDB Streams for real-time analytics
- Vectorized conversation storage for semantic search
- CloudWatch monitoring and alerting

## Cost Optimization

**PAY_PER_REQUEST Billing Mode**:
- No provisioned capacity needed
- Pay only for actual reads/writes
- Perfect for variable workload (hackathon demo)
- Auto-scales with demand

**Best Practices**:
- Use batch operations when possible (batch_writer)
- Query with indexes (avoid full scans)
- Implement pagination for large result sets
- Clean up old data regularly (delete_old_matches)
