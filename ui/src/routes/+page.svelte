<script>
import { onMount } from 'svelte';

/**
 * @type {any[]}
 */
let players = [];

onMount(async () => {
    try {
    const response = await fetch('https://deceptionratrace.onrender.com/report');
    if (!response.ok) {
        throw new Error('Failed to fetch data');
    }
    const data = await response.json();
    // Assuming the data structure is an array of players
    players = data;

    // Sort players by score in descending order
    players = players.sort((a, b) => b.Score - a.Score);
    } catch (error) {
    console.error(error);
    }
});
</script>

<h1>Player Scores</h1>

<table>
<thead>
    <tr>
    <th>Discord</th>
    <th>Main Char. Name</th>
    <th>Main Char. Spec</th>
    <th>Rolled Spec</th>
    <th>Challenge Char. Name</th>
    <th>Role</th>
    <th>Character</th>
    <th>Score</th>
    </tr>
</thead>
<tbody>
    {#each players as player}
    <tr>
        {#each Object.keys(player) as key}
        <td>{player[key]}</td>
        {/each}
    </tr>
    {/each}
</tbody>
</table>

<style>
table {
    width: 100%;
    border-collapse: collapse;
}
th, td {
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}
th {
    background-color: #f2f2f2;
}
</style>
  