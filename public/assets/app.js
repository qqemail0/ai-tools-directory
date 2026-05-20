
const input = document.querySelector('#toolSearch');
const results = document.querySelector('#searchResults');
if (input && results) {
  fetch('assets/search-index.json')
    .then(response => response.json())
    .then(items => {
      input.addEventListener('input', () => {
        const query = input.value.trim().toLowerCase();
        if (!query) { results.innerHTML = ''; return; }
        const hits = items.filter(item =>
          [item.name, item.title, item.category, item.keyword, item.description].join(' ').toLowerCase().includes(query)
        ).slice(0, 12);
        results.innerHTML = hits.map(item => `
          <a class="search-hit" href="${item.url}">
            <strong>${escapeHtml(item.name)}</strong>
            <span>${escapeHtml(item.category)} · ${escapeHtml(item.keyword)}</span>
          </a>
        `).join('');
      });
    });
}
function escapeHtml(value) {
  return value.replace(/[&<>"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
}
