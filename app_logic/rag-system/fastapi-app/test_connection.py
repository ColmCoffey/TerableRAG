import asyncio
import asyncpg

async def test_connect():
    try:
        conn = await asyncpg.connect(
            host="127.0.0.1",  # Change this from "localhost"
            port=5433,
            user="postgres",
            password="postgres",
            database="ragdb"
        )
        print("Connected successfully!")
        result = await conn.fetchval("SELECT current_user")
        print(f"Current user: {result}")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_connect())