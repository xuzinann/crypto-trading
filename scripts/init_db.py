#!/usr/bin/env python3
"""Initialize database with tables"""

from src.database.connection import init_database

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")
