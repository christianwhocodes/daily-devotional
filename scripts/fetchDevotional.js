// Load latest devotional
fetch("data/latest.json")
  .then((response) => response.json())
  .then((devotional) => {
    document.getElementById("latest-devotional").innerHTML = `
                    <div class="devotional">
                        <div class="date">${devotional.date}</div>
                        <div class="title">${
                          devotional.title || "Daily Devotional"
                        }</div>
                        ${
                          devotional.scripture
                            ? `<div class="scripture">"${devotional.scripture}"</div>`
                            : ""
                        }
                        ${
                          devotional.scripture_reference
                            ? `<div class="scripture-ref">${devotional.scripture_reference}</div>`
                            : ""
                        }
                        <div class="content">${devotional.content}</div>
                    </div>
                `;
  })
  .catch((error) => {
    document.getElementById("latest-devotional").innerHTML =
      "<p>Error loading devotional. Please try again later.</p>";
  });

// Load devotional archive
fetch("data/devotionals.json")
  .then((response) => response.json())
  .then((devotionals) => {
    const archiveHtml = devotionals
      .slice(1, 31)
      .map(
        (d) => `
                    <div class="archive-item" onclick="loadDevotional('${
                      d.date
                    }')">
                        <strong>${d.title || d.date}</strong><br>
                        <small>${d.date}</small>
                    </div>
                `
      )
      .join("");

    document.getElementById("archive-list").innerHTML = archiveHtml;
  })
  .catch((error) => {
    document.getElementById("archive-list").innerHTML =
      "<p>Error loading archive.</p>";
  });

function loadDevotional(date) {
  // Implementation for loading specific devotional
  console.log("Loading devotional for:", date);
}
