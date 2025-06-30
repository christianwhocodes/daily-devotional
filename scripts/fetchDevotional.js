// Load latest devotional
fetch("data/latest.json")
  .then((response) => response.json())
  .then((devotional) => {
    document.getElementById("latest-devotional").innerHTML = `
      <div class="devotional mb-4">
        <div class="d-flex align-items-center mb-2">
          <i class="bi bi-calendar3 text-muted me-2"></i>
          <small class="text-muted">${devotional.date}</small>
        </div>
        
        <h3 class="fw-bold text-dark mb-3">${
          devotional.title || "Daily Devotional"
        }</h3>
        
        ${
          devotional.scripture
            ? `
          <div class="scripture-section mb-4 p-3 bg-light rounded border-start border-primary border-4">
            <p class="fst-italic text-dark mb-2 fs-5">"${
              devotional.scripture
            }"</p>
            ${
              devotional.scripture_reference
                ? `<p class="fw-bold text-dark mb-0 small">— ${devotional.scripture_reference}</p>`
                : ""
            }
          </div>
        `
            : ""
        }
        
        <div class="content">
          <p class="text-dark lh-lg">${devotional.content}</p>
        </div>
      </div>
    `;
  })
  .catch((error) => {
    document.getElementById("latest-devotional").innerHTML = `
      <div class="alert alert-danger d-flex align-items-center" role="alert">
        <i class="bi bi-exclamation-triangle me-2"></i>
        <div>Error loading devotional. Please try again later.</div>
      </div>
    `;
  });

// Load devotional archive
fetch("data/devotionals.json")
  .then((response) => response.json())
  .then((devotionals) => {
    const archiveHtml = devotionals
      .slice(1, 31)
      .map(
        (d) => `
          <div class="archive-item p-3 border-bottom" style="cursor: pointer;" 
               onclick="loadDevotional('${d.date}')"
               onmouseover="this.classList.add('bg-light')" 
               onmouseout="this.classList.remove('bg-light')">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="fw-semibold text-dark">${d.title || d.date}</div>
                <small class="text-muted">${d.date}</small>
              </div>
              <i class="bi bi-chevron-right text-muted"></i>
            </div>
          </div>
        `
      )
      .join("");

    document.getElementById("archive-list").innerHTML = archiveHtml;
  })
  .catch((error) => {
    document.getElementById("archive-list").innerHTML = `
      <div class="alert alert-danger d-flex align-items-center" role="alert">
        <i class="bi bi-exclamation-triangle me-2"></i>
        <div>Error loading archive.</div>
      </div>
    `;
  });

function loadDevotional(date) {
  // Implementation for loading specific devotional
  console.log("Loading devotional for:", date);
}
