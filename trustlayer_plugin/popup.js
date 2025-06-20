fetch(chrome.runtime.getURL("data/trustlayer_plugin_data.json"))
  .then(r => r.json())
  .then(data => {
    document.getElementById('loading').style.display = 'none';
    const productsDiv = document.getElementById('products');
    productsDiv.style.display = '';
    data.forEach(entry => {
      const div = document.createElement('div');
      div.className = 'product';
      div.innerHTML = `
        <div class="product-name">${entry.product}</div>
        <div class="score yt">🟦 YouTube: ${entry.youtube?.trust_score ?? '?'}%</div>
        <div class="score rd">🔴 Reddit: ${entry.reddit?.trust_score ?? '?'}%</div>
      `;
      productsDiv.appendChild(div);
    });
  });
