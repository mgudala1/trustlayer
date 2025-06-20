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
  const normCurrent = normalizeTitle(currentProduct);
  for (const entry of data) {
    const allNames = [entry.product].concat(entry.aliases || []);
    for (const name of allNames) {
      const normName = normalizeTitle(name);
      const score = roughFuzzyMatchScore(normCurrent, normName);
      console.log(`🔬 Comparing "${normName}" with "${normCurrent}" → Score: ${score}`);
      if (score > highestScore && score >= 75) {
        bestMatch = entry;
        highestScore = score;
      }
    }
  }
  console.log("🎯 Best match found:", bestMatch?.product || "none");
  return bestMatch;
}

function showFallbackMessage() {
  const output = document.getElementById("output");
  output.innerHTML = `
    <p><strong>❌ No trust data found for this product.</strong><br>
    We couldn’t find Reddit or YouTube trust insights yet.</p>
  `;
}

fetch(chrome.runtime.getURL("data/trustlayer_plugin_data.json"))
  .then(res => res.json())
  .then(data => {
    const match = getBestMatch(currentProduct, data);
    const output = document.getElementById("output");
    output.innerHTML = "";
    if (!match) {
      console.log("❌ No valid product match found for:", currentProduct);
      showFallbackMessage();
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
