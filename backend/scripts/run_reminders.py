import asyncio

from db import close_db, get_db
from reminders import run_reminders


async def main():
    get_db()
    sent = await run_reminders()
    print(f"WhatsApp reminders sent: {sent}")
    close_db()


if __name__ == "__main__":
    asyncio.run(main())
