import asyncio
import sys
import json

from getpass import getpass
from server import log as logger
from server import web
from server.profiles import *

OUTPUT = "web/cards.json"
UPDATE = 30


async def update(username, password):
    profiles = ProfileApi(username, password)
    while True:
        cards = await profiles.all()
        with open(OUTPUT, 'w') as output:
            logger.log('writing user profiles to {}'.format(OUTPUT))
            output.write(json.dumps(cards, indent=4, sort_keys=False))
        logger.log('user profiles written to file, next update in {}s.'.format(UPDATE))
        await asyncio.sleep(UPDATE)

try:
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = input("username: ")
        password = getpass()

    loop = asyncio.get_event_loop()

    loop.create_task(update(username, password))
    loop.create_task(web.serve())

    loop.run_forever()
except KeyboardInterrupt:
    logger.log('timer was stopped by user.')
    pass
