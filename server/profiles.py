import asyncio
import json
import time

import aiohttp
from bs4 import BeautifulSoup
from server.log import log


class ProfileApi:
    """ Jira API to retrieve information about profile cards. """
    api_url = 'https://intranet.idainfront.se/rest/api/content'
    profiles_list = api_url + '/search?cql=(label=%22profile-card%22)&limit=255'
    profile_load = api_url + '/{}?expand=body.storage'

    def __init__(self, user, password):
        self.user = user
        self.password = password

    async def all(self):
        """ lists all profiles and then resolves each. """
        log('retrieving profile cards..')
        start = time.monotonic()
        profiles = await asyncio.gather(*list(
            map(lambda profile: self.retrieve(str(profile['id'])), await self.list())
        ))
        elapsed = "%0.2fs" % (time.monotonic() - start,)
        log("retrieved {} profile cards in {}".format(len(profiles), elapsed))
        return {
            "hits": len(profiles),
            "updated": time.time() * 1000,
            "time": elapsed,
            "applicants": list(filter(None, map(self.parse, profiles)))
        }

    async def list(self):
        """ list all profiles tagged with the 'profile-card' label. """
        all = (await self.get(self.profiles_list))['results']
        log("retrieved participant metadata.")
        return all

    async def retrieve(self, profile_id):
        """ parse information from a profile-card page as json """
        profile = await self.get(self.profile_load.format(profile_id))
        log("retrieved card for {}".format(profile['title']))
        return profile

    async def get(self, url):
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(self.user, self.password)) as session:
            return json.loads(await (await session.get(url)).text())

    def parse(self, profile):
        try:
            result = self.decode_html(profile['body']['storage']['value'])
            result['name'] = profile['title']
            result['id'] = profile['id']
            return result
        except:
            log("skipped broken profile {}".format(profile['title']))
            return None

    @staticmethod
    def decode_html(html):
        """ parses the pseudo-html as xml to support namespaces and performs string matching
            as elements are not properly tagged in this format, avoids calling the convert API
            for each profile but breaks if the labels in the macro is updated.
        """
        soup = BeautifulSoup(html, 'xml')
        return {
            'personality': ProfileApi.get_personality(soup),
            'ida_years': ProfileApi.get_ida_years(soup),
            'years': ProfileApi.get_years(soup),
            'choices': ProfileApi.get_choices(soup)
        }

    @staticmethod
    def get_personality(soup):
        return soup.select('.content-wrapper *[name="Personality"]')[0].get_text()

    @staticmethod
    def get_ida_years(soup):
        return soup.find('th', string='Years at Ida').next_sibling.get_text()

    @staticmethod
    def get_years(soup):
        return soup.find('th', string='Years in IT').next_sibling.get_text()

    @staticmethod
    def get_choices(soup):
        choices = soup.find('h1', string='Choices')
        if choices is not None and choices.next_sibling is not None:
            choices = choices.next_sibling
            return list(map(lambda element: element.get_text(), choices.find_all('li')))
        return []
