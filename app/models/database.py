import aiosqlite
import os

DB_PATH = "data/stock_analysis.db"

async def init_db():
    """Initialize the database tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        # 1. Portfolio table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                name TEXT,
                quantity REAL NOT NULL,
                avg_price REAL NOT NULL,
                market TEXT
            )
        """)
        
        # 2. Transaction history
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                type TEXT NOT NULL, -- BUY/SELL
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Saved analysis results
        await db.execute("""
            CREATE TABLE IF NOT EXISTS saved_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                sentiment_label TEXT,
                sentiment_score REAL,
                rsi REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def get_db():
    return await aiosqlite.connect(DB_PATH)
