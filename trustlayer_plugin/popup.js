function normalizeTitle(raw) {
  return raw
    .toLowerCase()
    .replace(/(amazon\.com|walmart\.com|–|:).*/g, "")
    .replace(/\b\d+(mg|ml|oz|count|pack|tablets|pills|ct)\b/g, "")
    .replace(/[^a-z0-9 ]/g, "")
    .split(" ")
    .filter(w => !["the", "and", "vs", "for", "with", "by", "of", "daily", "non", "drowsy"].includes(w))
    .slice(0, 8)
    .join(" ")
    .trim();
}

function detectProductName() {
  const h1 = document.querySelector("h1");
  const fallback = document.title;
  const raw = h1?.textContent || fallback;
  const cleaned = normalizeTitle(raw);
  console.log("🔍 Detected product (raw):", raw);
  console.log("✅ Normalized product:", cleaned);
  return cleaned;
}

const productTitle = detectProductName();
const fetchUrl = `https://curly-chainsaw-jjjjv4qpqj7fp474-8000.app.github.dev/match?title=${encodeURIComponent(productTitle)}`;
console.log('TrustLayer fetch URL:', fetchUrl);
fetch(fetchUrl)
  .then(res => {
    if (!res.ok) throw new Error('No match');
    return res.json();
  })
  .then(match => {
    renderPopup(match);
  })
  .catch((err) => {
    console.error('TrustLayer fetch error:', err);
    showFallbackMessage();
  });

function showFallbackMessage() {
  const output = document.getElementById("output");
  output.innerHTML = `
    <p><strong>❌ No trust data found for this product.</strong><br>
    We couldn’t find Reddit or YouTube trust insights yet.</p>
  `;
}

function renderPopup(match) {
  const output = document.getElementById("output");
  output.innerHTML = `
    <div class="score">
      <div class="label"><strong>${match.product_id}</strong></div>
      <div>🧠 Sentiment: ${match.sentiment_label}</div>
      <div>✅ Authenticity: ${Math.round(match.authenticity_score * 100)}%</div>
      <div><b>Summary:</b> ${match.summary_text ?? "N/A"}</div>
    </div>
  `;
}
