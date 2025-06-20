function normalizeTitle(raw) {
  let title = raw.toLowerCase();
  title = title.replace(/amazon\.com|youtube\.com|target\.com/g, "");
  title = title.replace(/[^a-z0-9 ]/g, " ");
  title = title.replace(/\b(vs|with|for|and|the|a|an|review|official|site|homepage|home|buy|shop|on|in|by|from)\b/g, " ");
  title = title.replace(/\s+/g, " ").trim();
  console.log('🔍 Normalized title:', title);
  return title;
}

function detectCurrentProduct() {
  const title = normalizeTitle(document.title);
  return title;
}

function getBestMatch(currentProduct, data) {
  let bestMatch = null;
  let highestScore = 0;

  for (const entry of data) {
    const entryName = entry.product.toLowerCase();
    const score = stringSimilarity(currentProduct, entryName);
    if (score > highestScore && score >= 0.9) {
      bestMatch = entry;
      highestScore = score;
    }
  }

  return bestMatch;
}

function stringSimilarity(a, b) {
  const aWords = a.split(" ");
  const bWords = b.split(" ");
  const shared = aWords.filter(word => bWords.includes(word));
  return shared.length / Math.max(aWords.length, bWords.length);
}

const currentProduct = detectCurrentProduct();

fetch(chrome.runtime.getURL("data/trustlayer_plugin_data.json"))
  .then(res => res.json())
  .then(data => {
    const match = getBestMatch(currentProduct, data);
    const output = document.getElementById("output");
    output.innerHTML = "";

    if (!match) {
      output.innerHTML = `
        <p><strong>No trust data found</strong><br>
        We couldn't find any Reddit or YouTube trust insights for this product yet.</p>
      `;
      return;
    }

    output.innerHTML = `
      <div class="score">
        <div class="label">${match.product}</div>
        🟦 YouTube: ${match.youtube?.trust_score ?? "N/A"}%<br>
        🔴 Reddit: ${match.reddit?.trust_score ?? "N/A"}%
      </div>
    `;
  });
