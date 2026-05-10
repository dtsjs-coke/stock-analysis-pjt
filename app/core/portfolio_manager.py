import aiosqlite
from models.database import DB_PATH

class PortfolioManager:
    @staticmethod
    async def buy_stock(ticker, name, quantity, price, market):
        async with aiosqlite.connect(DB_PATH) as db:
            # Check if already exists
            async with db.execute("SELECT quantity, avg_price FROM portfolio WHERE ticker = ?", (ticker,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    curr_qty, curr_avg = row
                    new_qty = curr_qty + quantity
                    new_avg = ((curr_qty * curr_avg) + (quantity * price)) / new_qty
                    await db.execute("UPDATE portfolio SET quantity = ?, avg_price = ? WHERE ticker = ?", (new_qty, new_avg, ticker))
                else:
                    await db.execute("INSERT INTO portfolio (ticker, name, quantity, avg_price, market) VALUES (?, ?, ?, ?, ?)", 
                                     (ticker, name, quantity, price, market))
            
            # Record transaction
            await db.execute("INSERT INTO transactions (ticker, type, quantity, price) VALUES (?, ?, ?, ?)", 
                             (ticker, 'BUY', quantity, price))
            await db.commit()

    @staticmethod
    async def sell_stock(ticker, quantity, price):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT id, quantity FROM portfolio WHERE ticker = ?", (ticker,)) as cursor:
                row = await cursor.fetchone()
                if not row or row[1] < quantity:
                    return False, "Insufficient quantity"
                
                row_id, curr_qty = row
                new_qty = curr_qty - quantity
                if new_qty == 0:
                    await db.execute("DELETE FROM portfolio WHERE id = ?", (row_id,))
                else:
                    await db.execute("UPDATE portfolio SET quantity = ? WHERE id = ?", (new_qty, row_id))
            
            await db.execute("INSERT INTO transactions (ticker, type, quantity, price) VALUES (?, ?, ?, ?)", 
                             (ticker, 'SELL', quantity, price))
            await db.commit()
            return True, "Success"

    @staticmethod
    async def get_portfolio():
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM portfolio") as cursor:
                return await cursor.fetchall()
