import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def verify_tables():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            ))
            tables = [row[0] for row in result.fetchall()]
            print(f"Tables found: {tables}")
            
            required_tables = {'tenants', 'messages', 'audit_logs', 'alembic_version'}
            if required_tables.issubset(set(tables)):
                print("All required tables are present.")
            else:
                print(f"Missing tables: {required_tables - set(tables)}")
        except Exception as e:
            print(f"Error verifying tables: {e}")

if __name__ == "__main__":
    asyncio.run(verify_tables())
