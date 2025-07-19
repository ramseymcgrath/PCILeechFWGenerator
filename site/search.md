---
layout: page
title: Search
permalink: /search/
---

<div id="search-container">
  <input type="text" id="search-input" placeholder="Search documentation...">
  <ul id="results-container"></ul>
</div>

<script src="{{ '/assets/js/simple-jekyll-search.min.js' | relative_url }}"></script>
<script>
  SimpleJekyllSearch({
    searchInput: document.getElementById('search-input'),
    resultsContainer: document.getElementById('results-container'),
    json: '{{ '/search.json' | relative_url }}',
    searchResultTemplate: '<li><a href="{url}" title="{desc}">{title}</a></li>',
    noResultsText: 'No results found',
    limit: 10,
    fuzzy: false,
    exclude: ['Welcome']
  })
</script>

<style>
#search-container {
  max-width: 600px;
  margin: 0 auto;
}

#search-input {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

#results-container {
  list-style: none;
  padding: 0;
  margin-top: 10px;
}

#results-container li {
  padding: 5px;
  border-bottom: 1px solid #eee;
}

#results-container li a {
  text-decoration: none;
  color: #333;
}

#results-container li a:hover {
  color: #0366d6;
}
</style>
