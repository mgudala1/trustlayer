function normalizeTitle(raw) {
  let title = raw.toLowerCase();
  title = title.replace(/(amazon\.com|youtube\.com|walmart\.com)/g, "");
  title = title.replace(/[^a-z0-9 ]/g, " ");
  let words = title.split(/\s+/).filter(Boolean);
  const filler = ["the", "and", "vs", "for", "with", "by", "of", "a", "an", "in", "on", "at", "to", "from", "review", "official", "site", "homepage", "home", "buy", "shop"];
  words = words.filter(w => !filler.includes(w));
  const cleaned = words.join(" ").trim();
  console.log("🔍 Cleaned product title:", cleaned);
  return cleaned;
}

const currentProduct = normalizeTitle(document.title);
console.log("🔍 Cleaned product title:", currentProduct);

function roughFuzzyMatchScore(a, b) {
  const aWords = a.split(" ").filter(Boolean);
  const bWords = b.split(" ").filter(Boolean);
  const shared = aWords.filter(word => bWords.includes(word));
  return (shared.length / Math.max(aWords.length, bWords.length)) * 100;
}

function getBestMatch(currentProduct, data) {
  let bestMatch = null;
  let highestScore = 0;

  for (const entry of data) {
    const names = [entry.product].concat(entry.aliases || []);
    for (const name of names) {
      const score = roughFuzzyMatchScore(currentProduct, name.toLowerCase());
      console.log(`🔬 Comparing "${name}" with "${currentProduct}" → score = ${score}`);
      if (score > highestScore && score >= 80) {
        bestMatch = entry;
        highestScore = score;
      }
    }
  }

  console.log("🔧 Final match score:", highestScore);
  return bestMatch;
}

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
