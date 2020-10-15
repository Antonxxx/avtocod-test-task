import argparse
import time
from requests_html import AsyncHTMLSession
import asyncio
from typing import Tuple
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Load:

    def __init__(self, depth, root):
        self.depth = depth
        self.root = root
        self.session = None

    @staticmethod
    async def get_children(url, session):
        r = await session.get(url)
        title = r.html.find("title")
        logger.info(f"{url}, {title[0].full_text}, {title}")
        return r.html.absolute_links

    @staticmethod
    async def get_root(root, session) -> Tuple[set, str, str]:
        r = await session.get(root)
        return r.html.absolute_links, r.html.html, r.html.find("title")[0].full_text

    async def cycle_start(self, links):
        tasks = []
        for link in links:
            if not link.find(self.root) and not link.endswith("xml"):
                tasks.append(self.get_children(link, self.session))
        result = await asyncio.gather(*tasks)
        return result

    async def start(self):
        self.session = AsyncHTMLSession()
        links, html, title = await self.get_root(self.root, self.session)
        if self.depth == 0:
            return
        elif self.depth == 1:
            await self.cycle_start(links)
            return
        elif self.depth == 2:
            result = await self.cycle_start(links)
            for item in result:
                if item:
                    await self.cycle_start(item)
        else:
            logger.error("depth > 2")
            return


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", dest="depth", type=int, help='Specify a depth from 0 to 2 default 0', default=0, )
    parser.add_argument("--command", dest="command", type=str, help='enter command Enum[load, GET]')
    parser.add_argument("--root", dest="root", type=str, help='Enter the root link')
    parser.add_argument("--number", dest="number", type=str, help='Number of results', default=0)

    args = parser.parse_args()
    start_time = time.monotonic()
    if args.command.lower() == "load":
        load = Load(root=args.root, depth=args.depth)
        asyncio.run(load.start())
    logger.info(f" lead time: {time.monotonic() - start_time}, depth: {args.depth}, command: {args.command.lower()}")
