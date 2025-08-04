<script lang="ts">
  import { onMount } from "svelte";
  import { PUBLIC_API_URL } from "$env/static/public";

  interface Player {
    Discord: string;
    "Main Char. Name": string;
    "Rolled Spec": string;
    Role: string;
    "Challenge Char. Name": string;
    Score: number;
    "Score Color": string;
    Thumbnail: string;
  }
  type PlayerKey = keyof Player;
  const headings: PlayerKey[] = [
    "Discord",
    "Main Char. Name",
    "Rolled Spec",
    "Role",
    "Challenge Char. Name",
    "Score",
  ];
  let players: Player[] = [];

  onMount(async () => {
    try {
      const response = await fetch(`${PUBLIC_API_URL}/report`);
      if (!response.ok) {
        throw new Error("Failed to fetch data");
      }
      const data = await response.json();
      players = data.sort((a: Player, b: Player) => b.Score - a.Score);
    } catch (error) {
      console.error(error);
    }
  });

  // helper: build raider.io URL for a character string
  function makeCharacterUrl(charName: string) {
    if (charName.includes("-")) {
      const [name, realm] = charName.split("-");
      return `https://raider.io/characters/eu/${realm}/${name}`;
    }
    return `https://raider.io/characters/eu/Silvermoon/${charName}`;
  }
</script>

<h1>🐀 Zero to Hero Scores 🐀</h1>

<table>
  <thead>
    <tr>
      {#each headings as heading}
        <th>{heading}</th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each players as player}
      <tr>
        {#each headings as key}
          {#if key === "Challenge Char. Name"}
            <td>
              <img
                src={player.Thumbnail}
                alt="Thumbnail of {player[key]}"
                width="24"
                height="24"
                style="vertical-align: middle; margin-right: 8px;"
              />
              <a href={makeCharacterUrl(player[key])}>
                {player[key]}
              </a>
            </td>
          {:else if key === "Main Char. Name"}
            <td><a href={makeCharacterUrl(player[key])}>{player[key]}</a></td>
          {:else if key === "Score"}
            <td style="color: {player['Score Color']}">
              {player[key]}
            </td>
          {:else}
            <td>{player[key] ?? "-"}</td>
          {/if}
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

<style>
  :global(html),
  :global(body) {
    background-color: #242222;
    color: white;
    margin: 0;
  }

  :global(a) {
    color: #4da6ff;
    text-decoration: none;
  }

  :global(a:hover) {
    color: #80cfff;
    text-decoration: underline;
  }

  * {
    font-family: "Segoe UI", Arial, Helvetica, sans-serif;
    background-color: transparent;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th,
  td {
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid;
  }
</style>
