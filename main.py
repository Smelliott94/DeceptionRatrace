import json
from fastapi import FastAPI
import aiohttp
import asyncio
from fastapi_utilities import repeat_every
from fastapi.middleware.cors import CORSMiddleware

baseurl = "https://raider.io/api/v1/characters/profile?region=eu"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with a list of allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

with open('data/rats.json') as characters_file:
    report = json.load(characters_file)


async def get_character_profile(session, character_name):
    if '-' in character_name:
        character, realm = character_name.split('-')
    else:
        character = character_name
        realm = "Silvermoon"
    url = f"{baseurl}&realm={realm}&name={character}&fields=mythic_plus_scores_by_season:current"
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
    return None
    
def get_spec_score(profile, spec, season=4):
    with open('data/specs.json') as spec_map_file:
        spec_map = json.load(spec_map_file)
    spec_id = spec_map[spec]
    if profile:
        for season_data in profile['mythic_plus_scores_by_season']:
            if season_data['season'] == f'season-df-{season}':
                return season_data['scores'][spec_id]
    return None

async def refresh_scores():
    global report
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = []
            for character in report:
                tasks.append(asyncio.ensure_future(get_character_profile(session, character['Character'])))
            profiles = await asyncio.gather(*tasks)
            print(profiles)
            for character, profile in zip(report, profiles):
                if profile:
                    score = get_spec_score(profile, character['Rolled Spec'])
                    character['Score'] = score
            print(json.dumps(report, indent=2))

@app.on_event("startup")
@repeat_every(seconds=600)
async def startup_event():
    asyncio.create_task(refresh_scores())

@app.get('/report')
async def get_report():
    return report

