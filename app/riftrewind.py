#!/usr/bin/env python3
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.chat import run_chat
from cli.sync import run_sync

VERSION = "1.0.0"

def print_help():
    print("\nRiftRewind CLI - Available Commands:")
    print("-" * 50)
    print("  chat        Start AI coaching chat (requires session token)")
    print("  sync        Sync databases with Riot API data")
    print("  help        Show this help message")
    print("  version     Show version information")
    print("  exit        Exit RiftRewind CLI")
    print("-" * 50)
    print()

def print_banner():
    print("\n" + "=" * 50)
    print(f"  RiftRewind CLI v{VERSION}")
    print("  League of Legends Analysis & Coaching Tool")
    print("=" * 50)
    print("\nType 'help' for available commands\n")

def main():
    print_banner()

    while True:
        try:
            user_input = input("> ").strip().lower()
            if not user_input:
                continue

            # Parse command and arguments
            parts = user_input.split()
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            # Route commands
            if command == "help":
                print_help()
            elif command == "version":
                print(f"RiftRewind CLI v{VERSION}")
            elif command == "chat":
                if args:
                    run_chat(args[0])
                else:
                    print("Usage: chat <session_token>")
                    print("Example: chat a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6")
            elif command == "sync":
                run_sync()
            elif command in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                break
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
        except KeyboardInterrupt:
            print("\n\nUse 'exit' to quit")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
