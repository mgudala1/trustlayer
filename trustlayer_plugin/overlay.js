// overlay.js for TrustLayer Chrome Extension
function detectProductName() {
  // 1. Check the document title
  const fromTitle = document.title;
  if (fromTitle && fromTitle.length > 5) return fromTitle.toLowerCase();

  // 2. Check open graph metadata
  const ogTitle = document.querySelector('meta[property="og:title"]')?.content;
  if (ogTitle && ogTitle.length > 5) return ogTitle.toLowerCase();

  // 3. Check Amazon product title (if on amazon)
  const amazonTitle = document.getElementById("productTitle")?.innerText;
  if (amazonTitle && amazonTitle.length > 5) return amazonTitle.toLowerCase();

  return "unknown";
}

function stringSimilarity(a, b) {
  const aWords = a.split(" ");
  const bWords = b.split(" ");
  const matches = aWords.filter(word => bWords.includes(word)).length;
  return matches / Math.max(aWords.length, bWords.length);
}

function getBestMatch(currentProduct, data) {
  let highestScore = 0;
  let bestMatch = null;
  for (let entry of data) {
    const score = stringSimilarity(currentProduct, entry.product.toLowerCase());
    console.log(`🔬 Comparing '${entry.product}' with '${currentProduct}': Score = ${score}`);
    if (score > highestScore) {
      highestScore = score;
      bestMatch = entry;
    }
  }
  console.log("🔧 Final match score:", highestScore);
  return highestScore >= 0.9 ? bestMatch : null;
}

(function() {
  function isSupportedDomain() {
    const host = window.location.hostname;
    return (
      host.includes('amazon.') ||
      host.includes('youtube.') ||
      host.includes('target.com')
    );
  }

  if (isSupportedDomain()) {
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

    // Fetch trust data and render overlay content
    fetch(chrome.runtime.getURL('data/trustlayer_plugin_data.json'))
      .then(res => res.json())
      .then(data => {
        const currentProduct = detectProductName();
        const match = getBestMatch(currentProduct, data);
        if (!match) {
          console.log("❌ No valid match found");
          document.getElementById('trust-content').innerHTML = `
            <div style="font-weight:bold;font-size:1.1em;">No trust data found for this product</div>
            <div style="margin:8px 0; color:#888;">We couldn't find any Reddit or YouTube trust insights for this product yet.</div>
          `;
          document.getElementById('trust-tooltip-yt').textContent = '?';
          document.getElementById('trust-tooltip-rd').textContent = '?';
          return;
        }
        console.log("🎯 Best match found:", match.product);
        // ...inject badge and overlay for match only...
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
        document.getElementById('trust-content').innerHTML = `
          <div style="font-weight:bold;font-size:1.1em;">${match.product}</div>
          <div style="margin:8px 0;">Trust Score: <b>${avg ? avg.toFixed(1) : '?' }%</b></div>
          <div><b>Top Pros:</b> ${pros.length ? pros.map(p => `<span style='color:#1a73e8;'>${p}</span>`).join(', ') : 'N/A'}</div>
          <div><b>Top Cons:</b> ${cons.length ? cons.map(c => `<span style='color:#d93025;'>${c}</span>`).join(', ') : 'N/A'}</div>
          <div style="margin-top:12px;"><a href="${realTalkLink}" target="_blank" rel="noopener" style="color:#1a73e8;text-decoration:underline;">See real talk</a></div>
          <button class="trust-feedback">👍 Was this helpful?</button>
        `;
        document.getElementById('trust-tooltip-yt').textContent = yt.trust_score !== undefined ? yt.trust_score : '?';
        document.getElementById('trust-tooltip-rd').textContent = rd.trust_score !== undefined ? rd.trust_score : '?';
        const feedbackBtn = document.querySelector('.trust-feedback');
        if (feedbackBtn) {
          feedbackBtn.onclick = () => {
            const feedbackKey = `feedback_${match.product.toLowerCase()}`;
            chrome.storage && chrome.storage.local && chrome.storage.local.set({ [feedbackKey]: true }, () => {
              console.log(`📝 Feedback submitted for ${match.product.toLowerCase()}`);
            });
          };
        }
      });
  } else {
    console.log('🔒 TrustLayer skipped: unsupported domain');
  }
})();
