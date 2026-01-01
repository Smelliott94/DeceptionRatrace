<script lang="ts">
  import { onMount } from "svelte";
  import { PUBLIC_API_URL } from "$env/static/public";

  interface Player {
    discord: string;
    main_name: string;
    spec: string;
    name: string;
    score: number;
    score_color: string;
    thumbnail: string;
  }

  // Map of Heading → Player key
  const headings: { label: string; key: keyof Player | null }[] = [
    { label: "discord", key: "discord" },
    { label: "main_name", key: "main_name" },
    { label: "spec", key: "spec" },
    { label: "name", key: "name" },
    { label: "Score", key: "score" },
  ];

  let players: Player[] = [];

  onMount(async () => {
    try {
      const response = await fetch(`${PUBLIC_API_URL}/report`);
      if (!response.ok) {
        throw new Error("Failed to fetch data");
      }
      const data: Player[] = await response.json();
      players = data.sort((a, b) => b.score - a.score);
      players.forEach( (player) => {
          console.log(player)
      });
    } catch (error) {
      console.error(error);
    }
  });

  // helper: build raider.io URL for a character string
  function makeCharacterUrl(charName: string) {
    console.log(`charName ${charName}`)
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
        <th>{heading.label}</th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each players ?? [] as player}
      {#if !player?.name}
        {@debug player}
      {/if}
      {#if player}
      <tr>
        {#each headings as heading}
          {#if heading.key === "name"}
            <td>
              <a href={makeCharacterUrl(player.name)}>
                {player.name}
              </a>
            </td>
          {:else if heading.key === "main_name"}
            <td>
              <a href={makeCharacterUrl(player.main_name)}>
                {player.main_name}
              </a>
            </td>
          {:else if heading.key === "score"}
            <td style="color: {player.score_color}">
              {player.score}
            </td>
          {:else if heading.key}
            <td>{player[heading.key] ?? "-"}</td>
          {:else}
            <td>-</td>
          {/if}
        {/each}
      </tr>
      {/if}
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
