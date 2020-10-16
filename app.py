import argparse
import time
from contextlib import asynccontextmanager
import json
import aioredis as aioredis
from requests_html import AsyncHTMLSession
import asyncio
from typing import Tuple, AsyncGenerator
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def connect_redis() -> AsyncGenerator:
    conn = await aioredis.create_redis_pool(
        ("redis", 6379),
        db=0,
        password="redis",
    )
    yield conn
    conn.close()
    await conn.wait_closed()


class Load:

    def __init__(self, depth, root):
        self.depth = depth
        self.root = root
        self.session = None

    @staticmethod
    async def get_children(url, session, conn, root):
        r = await session.get(url)
        await conn.rpush(root, json.dumps({"html": r.html.html, "title": r.html.find("title")[0].full_text, "url": url}))
        return r.html.absolute_links

    @staticmethod
    async def get_root(root, session, conn):
        r = await session.get(root)
        await conn.rpush(root, json.dumps({"html": r.html.html, "title": r.html.find("title")[0].full_text, "url": root}))
        return r.html.absolute_links

    async def cycle_start(self, links, conn):
        tasks = []
        for link in links:
            if not link.find(self.root) and not link.endswith("xml"):
                tasks.append(self.get_children(link, self.session, conn, self.root))
        result = await asyncio.gather(*tasks)
        return result

    async def start(self):
        async with connect_redis() as conn:
            self.session = AsyncHTMLSession()
            links = await self.get_root(self.root, self.session, conn)
            if self.depth == 0:
                return
            elif self.depth == 1:
                await self.cycle_start(links, conn)
                return
            elif self.depth == 2:
                result = await self.cycle_start(links, conn)
                for item in result:
                    if item:
                        await self.cycle_start(item, conn)
            else:
                logger.error("depth > 2")
                return


class GET:

    def __init__(self, number, root):
        self.root = root
        self.number = number

    async def start(self):
        async with connect_redis() as conn:
            result = await conn.lrange(self.root, 0, self.number)
            for item in result:
                data = json.loads(item)
                logger.info(f" url: {data['url']}, title: {data['title']}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", dest="depth", type=int, help='Specify a depth from 0 to 2 default 0', default=0, )
    parser.add_argument("--command", dest="command", type=str, help='enter command Enum[load, GET]')
    parser.add_argument("--root", dest="root", type=str, help='Enter the root link')
    parser.add_argument("--number", dest="number", type=int, help='Number of results', default=0)

    args = parser.parse_args()
    start_time = time.monotonic()
    if args.command.lower() == "load":
        cmd = Load(root=args.root, depth=args.depth)
    elif args.command.lower() == "get":
        cmd = GET(number=args.number, root=args.root)
    asyncio.run(cmd.start())
    logger.info(f" lead time: {time.monotonic() - start_time}, depth: {args.depth}, command: {args.command.lower()}")
