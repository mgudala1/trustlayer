fetch(chrome.runtime.getURL("data/trustlayer_plugin_data.json"))
  .then((response) => response.json())
  .then((trustData) => {
    console.log("✅ TrustLayer data loaded:", trustData);

    // Helper to inject badge after a#video-title
    function injectBadges() {
      trustData.forEach((productEntry) => {
        const product = productEntry.product.replace(/_/g, " ");
        const score = productEntry.youtube?.trust_score || productEntry.reddit?.trust_score;
        const selector = "a#video-title";
        document.querySelectorAll(selector).forEach((el) => {
          if (
            el.innerText.toLowerCase().includes(product.toLowerCase()) &&
            !el.nextSibling?.classList?.contains("trust-badge")
          ) {
            const badge = document.createElement("span");
            badge.className = "trust-badge";
            badge.textContent = ` 🔍 Trust: ${score || "?"}%`;
            el.parentNode.insertBefore(badge, el.nextSibling);
          }
        });
      });
    }

    // Initial injection
    injectBadges();

    // Observe for dynamic YouTube search result changes
    const observer = new MutationObserver(() => {
      injectBadges();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  });
