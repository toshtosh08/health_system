async function searchClients() {
    const query = document.getElementById('search').value;
    const response = await fetch(`/search_client?query=${encodeURIComponent(query)}`);
    const results = await response.text();
    document.getElementById('search-results').innerHTML = results;
}