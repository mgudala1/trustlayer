// overlay.js for TrustLayer Chrome Extension
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

function stringSimilarity(a, b) {
  const aWords = a.split(" ");
  const bWords = b.split(" ");
  const matches = aWords.filter(word => bWords.includes(word)).length;
  return matches / Math.max(aWords.length, bWords.length);
}

function roughFuzzyMatchScore(a, b) {
  const aWords = new Set(a.split(" "));
  const bWords = new Set(b.split(" "));
  const shared = [...aWords].filter(w => bWords.has(w));
  return (shared.length / Math.max(aWords.size, bWords.size)) * 100;
}

function getBestMatch(currentProduct, data) {
  let bestMatch = null;
  let bestScore = 0;
  for (const entry of data) {
    const allNames = [entry.product_id].concat(entry.aliases || []);
    for (const name of allNames) {
      const score = roughFuzzyMatchScore(currentProduct, normalizeTitle(name));
      console.log(`🔬 Comparing "${name}" with "${currentProduct}" → Score: ${score}`);
      if (score > bestScore && score >= 60) {
        bestMatch = entry;
        bestScore = score;
      }
    }
  }
  console.log("🎯 Best match found:", bestMatch?.product_id || "none");
  return bestMatch;
}

function showFallbackOverlay() {
  const trustContent = document.getElementById('trust-content');
  if (trustContent) {
    trustContent.innerHTML = `
      <div style="font-weight:bold;font-size:1.1em;">❌ No trust data found for this product.</div>
      <div style="margin:8px 0; color:#888;">We couldn’t find Reddit or YouTube trust insights yet.</div>
    `;
  }
  const ytElem = document.getElementById('trust-tooltip-yt');
  if (ytElem) ytElem.textContent = '?';
  const rdElem = document.getElementById('trust-tooltip-rd');
  if (rdElem) rdElem.textContent = '?';
}

function injectBadgeAndOverlay(match) {
  // Remove old badge, overlay, and tooltip if they exist
  document.querySelector('.trust-badge-float')?.remove();
  document.querySelector('.trust-overlay')?.remove();
  document.querySelector('.trust-tooltip')?.remove();

  // Create floating badge
  const badge = document.createElement('div');
  badge.className = 'trust-badge-float';
  badge.textContent = '🔍 TrustLayer';
  badge.style.cursor = 'pointer';
  document.body.appendChild(badge);

  // Create overlay panel
  const overlay = document.createElement('div');
  overlay.className = 'trust-overlay';
  overlay.style.display = 'none';
  overlay.innerHTML = `
    <button class="trust-overlay-close">×</button>
    <div id="trust-content">Loading...</div>
  `;
  document.body.appendChild(overlay);

  // Tooltip element
  const tooltip = document.createElement('div');
  tooltip.className = 'trust-tooltip';
  tooltip.style.display = 'none';
  tooltip.innerHTML = `
    <div>YouTube: <span id="trust-tooltip-yt">?</span>%</div>
    <div>Reddit: <span id="trust-tooltip-rd">?</span>%</div>
    <div style="margin-top:4px;color:#1a73e8;">Click to see more</div>
  `;
  document.body.appendChild(tooltip);

  badge.addEventListener('mouseover', () => {
    if (overlay.style.display === 'none') {
      tooltip.style.display = 'block';
    }
  });
  badge.addEventListener('mouseout', () => {
    tooltip.style.display = 'none';
  });

  // Hide tooltip when overlay opens
  badge.onclick = () => {
    overlay.style.display = overlay.style.display === 'none' ? 'block' : 'none';
    if (overlay.style.display === 'block') {
      tooltip.style.display = 'none';
    }
  };
  overlay.querySelector('.trust-overlay-close').onclick = () => {
    overlay.style.display = 'none';
  };

  // Position tooltip near badge
  function positionTooltip() {
    const rect = badge.getBoundingClientRect();
    tooltip.style.right = '20px';
    tooltip.style.bottom = '70px';
  }
  positionTooltip();
  window.addEventListener('resize', positionTooltip);

  // Render overlay content
  const yt = match.youtube || {};
  const rd = match.reddit || {};
  const avg = [yt.trust_score, rd.trust_score].filter(x => typeof x === 'number').reduce((a, b) => a + b, 0) / ([yt.trust_score, rd.trust_score].filter(x => typeof x === 'number').length || 1);
  const pros = (yt.top_pros || []).concat(rd.top_pros || []).slice(0, 3);
  const cons = (yt.top_cons || []).concat(rd.top_cons || []).slice(0, 3);
  let realTalkLink = '#';
  if (match.source && match.source.reddit) {
    realTalkLink = match.source.reddit;
  } else if (match.source && match.source.youtube) {
    realTalkLink = match.source.youtube;
  }
  const trustContent = document.getElementById('trust-content');
  if (trustContent) {
    trustContent.innerHTML = `
      <div style="font-weight:bold;font-size:1.1em;">${match.product_id}</div>
      <div style="margin:8px 0;">Trust Score: <b>${avg ? avg.toFixed(1) : '?' }%</b></div>
      <div><b>Top Pros:</b> ${pros.length ? pros.map(p => `<span style='color:#1a73e8;'>${p}</span>`).join(', ') : 'N/A'}</div>
      <div><b>Top Cons:</b> ${cons.length ? cons.map(c => `<span style='color:#d93025;'>${c}</span>`).join(', ') : 'N/A'}</div>
      <div style="margin-top:12px;"><a href="${realTalkLink}" target="_blank" rel="noopener" style="color:#1a73e8;text-decoration:underline;">See real talk</a></div>
      <button class="trust-feedback">👍 Was this helpful?</button>
    `;
  }
  const ytElem = document.getElementById('trust-tooltip-yt');
  if (ytElem) ytElem.textContent = yt.trust_score !== undefined ? yt.trust_score : '?';
  const rdElem = document.getElementById('trust-tooltip-rd');
  if (rdElem) rdElem.textContent = rd.trust_score !== undefined ? rd.trust_score : '?';
  const feedbackBtn = document.querySelector('.trust-feedback');
  if (feedbackBtn) {
    feedbackBtn.onclick = () => {
      const feedbackKey = `feedback_${match.product_id.toLowerCase()}`;
      chrome.storage && chrome.storage.local && chrome.storage.local.set({ [feedbackKey]: true }, () => {
        console.log(`📝 Feedback submitted for ${match.product_id.toLowerCase()}`);
      });
    };
  }
}

document.addEventListener("DOMContentLoaded", detectAndRender);
const observer = new MutationObserver(detectAndRender);
observer.observe(document.body, { childList: true, subtree: true });

async function detectAndRender() {
  const productTitle = detectProductName();
  console.log("🔍 Product (normalized):", productTitle);

  const files = ["skincare.json", "food.json", "household.json"];
  const base = chrome.runtime.getURL("data/categories/");
  let allEntries = [];

  for (const file of files) {
    try {
      const res = await fetch(base + file);
      if (res.ok) {
        const entries = await res.json();
        allEntries = allEntries.concat(entries);
      }
    } catch (e) {
      console.warn("❌ Failed to load", file, e);
    }
  }

  const match = getBestMatch(productTitle, allEntries);
  if (match) {
    injectBadgeAndOverlay(match);
  } else {
    showFallbackOverlay();
  }
}
