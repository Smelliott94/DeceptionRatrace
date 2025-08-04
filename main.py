from contextlib import asynccontextmanager
import json
from fastapi import FastAPI
import aiohttp
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import libsql
import os
from dotenv import load_dotenv
from pandas import DataFrame as df

load_dotenv()
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect(database=url, auth_token=auth_token)


class Player(BaseModel):
    id: int
    discord: str
    main_name: str
    spec: str
    score: float | None
    name: str
    thumbnail: str | None
    score_color: str | None


class SpecResult(BaseModel):
    score: float
    color: str


baseurl = "https://raider.io/api/v1/characters/profile?region=eu"
report: list[Player]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global report
    report = get_players()
    asyncio.create_task(refresh_scores())
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


def get_players() -> list[Player]:
    players = conn.execute("select * from players").fetchall()
    return [
        Player(
            id=p[0],
            discord=p[1],
            main_name=p[2],
            spec=p[3],
            name=p[4],
            score=p[5],
            thumbnail=p[6],
            score_color=p[7],
        )
        for p in players
    ]


def sync_report():
    db_ids = {p.id for p in get_players()}
    report_ids = {p.id for p in report}
    to_delete = db_ids - report_ids
    if to_delete:
        placeholders = ",".join("?" * len(to_delete))
        conn.execute(
            f"DELETE FROM players WHERE id IN ({placeholders})", list(to_delete)
        )

    cols = list(report[0].model_dump().keys())
    col_names = ", ".join(cols)
    placeholders = ", ".join("?" * len(cols))
    update_assignments = ", ".join([f"{c}=excluded.{c}" for c in cols if c != "id"])

    sql = f"""
    INSERT INTO players ({col_names})
    VALUES ({placeholders})
    ON CONFLICT(id) DO UPDATE SET {update_assignments};
    """
    values = [tuple(p.model_dump()[c] for c in cols) for p in report]
    conn.executemany(sql, values)
    conn.commit()
    print(f"Synced {len(report)} players — {len(to_delete)} removed.")


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
            return SpecResult(**season_data["segments"][spec_id])
    return None


async def refresh_scores():
    global report
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = []
            for character in report:
                tasks.append(
                    asyncio.ensure_future(
                        get_character_profile(session, character.name)
                    )
                )
            profiles = await asyncio.gather(*tasks)
            print(profiles)
            for character, profile in zip(report, profiles):
                if profile:
                    score = get_spec_score(profile, character.spec)
                    character.thumbnail = profile["thumbnail_url"]
                    character.score = score.score
                    character.score_color = score.color
            print(json.dumps([p.model_dump() for p in report], indent=2))
            print("syncing")
            sync_report()
            await asyncio.sleep(300)


@app.get("/report")
async def get_report():
    sorted_report: list[Player] = sorted(
        report,
        key=lambda player: player.score if player.score is not None else float("-inf"),
        reverse=True,
    )
    return sorted_report
