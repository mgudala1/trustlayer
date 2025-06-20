// overlay.js for TrustLayer Chrome Extension
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

    // Toggle overlay
    badge.onclick = () => {
      overlay.style.display = overlay.style.display === 'none' ? 'block' : 'none';
    };
    overlay.querySelector('.trust-overlay-close').onclick = () => {
      overlay.style.display = 'none';
    };

    // Fetch trust data and render overlay content
    fetch(chrome.runtime.getURL('data/trustlayer_plugin_data.json'))
      .then(r => r.json())
      .then(data => {
        // Hardcoded for demo: cerave cleanser
        const entry = data.find(e => e.product.toLowerCase() === 'cerave cleanser');
        if (!entry) {
          document.getElementById('trust-content').textContent = 'No data found.';
          return;
        }
        const yt = entry.youtube || {};
        const rd = entry.reddit || {};
        const avg = [yt.trust_score, rd.trust_score].filter(x => typeof x === 'number').reduce((a, b) => a + b, 0) / ([yt.trust_score, rd.trust_score].filter(x => typeof x === 'number').length || 1);
        const pros = (yt.top_pros || []).concat(rd.top_pros || []).slice(0, 3);
        const cons = (yt.top_cons || []).concat(rd.top_cons || []).slice(0, 3);
        let realTalkLink = '#';
        if (entry.source && entry.source.reddit) {
          realTalkLink = entry.source.reddit;
        } else if (entry.source && entry.source.youtube) {
          realTalkLink = entry.source.youtube;
        }
        document.getElementById('trust-content').innerHTML = `
          <div style="font-weight:bold;font-size:1.1em;">cerave cleanser</div>
          <div style="margin:8px 0;">Trust Score: <b>${avg ? avg.toFixed(1) : '?' }%</b></div>
          <div><b>Top Pros:</b> ${pros.length ? pros.map(p => `<span style='color:#1a73e8;'>${p}</span>`).join(', ') : 'N/A'}</div>
          <div><b>Top Cons:</b> ${cons.length ? cons.map(c => `<span style='color:#d93025;'>${c}</span>`).join(', ') : 'N/A'}</div>
          <div style="margin-top:12px;"><a href="${realTalkLink}" target="_blank" rel="noopener" style="color:#1a73e8;text-decoration:underline;">See real talk</a></div>
        `;
      });
  } else {
    console.log('🔒 TrustLayer skipped: unsupported domain');
  }
})();
