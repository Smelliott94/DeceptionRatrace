from contextlib import asynccontextmanager
import json
from fastapi import FastAPI
import aiohttp
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class SpecResult(BaseModel):
    score: float
    color: str

baseurl = "https://raider.io/api/v1/characters/profile?region=eu"


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(refresh_scores())
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with a list of allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

with open("data/rats.json") as characters_file:
    report = json.load(characters_file)


async def get_character_profile(session, character_name):
    if "-" in character_name:
        character, realm = character_name.split("-")
    else:
        character = character_name
        realm = "Silvermoon"
    url = f"{baseurl}&realm={realm}&name={character}&fields=mythic_plus_scores_by_season:current"
    print(url)
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
    return None


def get_spec_score(profile, spec, season=2):
    with open("data/specs.json") as spec_map_file:
        spec_map = json.load(spec_map_file)
    spec_id = spec_map[spec]
    if profile:
        for season_data in profile["mythic_plus_scores_by_season"]:
            return SpecResult(**season_data['segments'][spec_id])
    return None


async def refresh_scores():
    global report
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = []
            for character in report:
                tasks.append(
                    asyncio.ensure_future(
                        get_character_profile(
                            session, character["Challenge Char. Name"]
                        )
                    )
                )
            profiles = await asyncio.gather(*tasks)
            print(profiles)
            for character, profile in zip(report, profiles):
                if profile:
                    score = get_spec_score(profile, character["Rolled Spec"])
                    character["Thumbnail"] = profile["thumbnail_url"]
                    character["Score"] = score.score
                    character["Score Color"] =  score.color
            print(json.dumps(report, indent=2))
            await asyncio.sleep(300)


@app.get("/report")
async def get_report():
    sorted_report = sorted(
        report, key=lambda x: x.get("Score", float("-inf")), reverse=True
    )
    return sorted_report
