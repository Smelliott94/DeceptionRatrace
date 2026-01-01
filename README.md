# DeceptionRatRace
simple current Mythic+ season raider.io score lookup for  a specific spec.

Displayed as a leaderboard with a basic UI.

## Setup and Data
Since participants aren't expected to change we just do a one-time data preparation then source
the characters from the resulting `rats.json`.

```bash
uv sync --group data-prep
uv run dataprep # First time only

# Serve the API
uv run uvicorn main:app --reload

# Serve UI in dev mode
cd ui
npm install
npm run dev
```
