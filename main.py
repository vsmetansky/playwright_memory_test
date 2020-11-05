import asyncio
import logging
import tracemalloc

from sessions import BrowserSession

CONCURRENCY = 10  # number of urls to be processed concurrently
STATS_NUM = 3
TIMEOUT = 60000
GROUP_NUM = 10  # number of url groups
BASE_URL = 'https://www.google.com'  # url that is passed into page.goto

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def log_stats(snapshots, stats_num=STATS_NUM):
    if len(snapshots) > 1:
        stats = snapshots[-1].compare_to(snapshots[-2], 'filename')
        logger.debug('*********************************************')
        logger.debug(f'top {stats_num} stats:')
        for s in stats[:stats_num]:
            logger.debug(s)
            [logger.debug(l) for l in s.traceback]
            logger.debug('---------------------------------------------')
        logger.debug('*********************************************')


async def start(sessions):
    """Starts execution of actions concurrently for each group of urls."""
    snapshots = []
    tracemalloc.start(20)
    await open_sessions(sessions)
    snapshots.append(tracemalloc.take_snapshot())
    for i in range(GROUP_NUM):
        await asyncio.gather(*(action(s) for s in sessions))
        logger.debug(f'{(i + 1) * CONCURRENCY} urls processed')
        snapshots.append(tracemalloc.take_snapshot())
        log_stats(snapshots)


async def open_sessions(sessions):
    await asyncio.gather(*(s.open() for s in sessions))


async def close_sessions(sessions):
    await asyncio.gather(*(s.close() for s in sessions))


async def stop(sessions):
    """Stops execution of actions, closing sessions."""
    await close_sessions(sessions)


async def action(session):
    page = await session.context.newPage()
    await page.goto(BASE_URL, timeout=TIMEOUT)
    await page.waitForSelector('//title', state='attached')
    await page.close()


async def main():
    sessions = [BrowserSession() for _ in range(CONCURRENCY)]
    try:
        await start(sessions)
    except KeyboardInterrupt:
        logger.debug('execution interrupted')
    finally:
        await stop(sessions)
        logger.debug('final stats:')
        stats = tracemalloc.take_snapshot().statistics('filename')
        for s in stats[:STATS_NUM]:
            logger.debug(s)


if __name__ == '__main__':
    asyncio.run(main())
