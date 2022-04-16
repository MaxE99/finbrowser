async function load_filters() {
  try {
    const res = await fetch(
      `../api/get_article_filters`,
      get_fetch_settings("GET")
    );
    if (!res.ok) {
      showMessage("Error: Article filters couldn't be fetched!", "Error");
    } else {
      const context = await res.json();
      if (context[0] != null) {
        document.getElementById("timeframe").value = context[0];
        document.getElementById("sector").value = context[1];
        document.getElementById("paywall").value = context[2];
        document.querySelector("summary").innerText = context[3];
      }
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
}

load_filters();

//Filter functionality
document.querySelector(".searchButton").addEventListener("click", async () => {
  const timeframeSelect = document.getElementById("timeframe");
  const timeframe =
    timeframeSelect.options[timeframeSelect.selectedIndex].value;
  const sectorSelect = document.getElementById("sector");
  const sector = sectorSelect.options[sectorSelect.selectedIndex].value;
  const paywallSelect = document.getElementById("paywall");
  const paywall = paywallSelect.options[paywallSelect.selectedIndex].value;
  const sources = document.querySelector("summary").innerText;
  try {
    const res = await fetch(
      `../api/filter_articles/${timeframe}/${sector}/${paywall}/${sources}`,
      get_fetch_settings("GET")
    );
    if (!res.ok) {
      showMessage("Error: List couldn't be filtered!", "Error");
    } else {
      const context = await res.json();
      window.location.href = "../../articles";
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
});

// select sources
document.querySelectorAll(".selectContainer ul li").forEach((choice) => {
  choice.addEventListener("click", () => {
    document.querySelector("summary").innerHTML = choice.innerHTML;
    document.querySelector("details").removeAttribute("open");
  });
});

// article ellipsis options
let previousOptionsContainer;
let previousEllipsis;
document.querySelectorAll(".article .fa-ellipsis-h").forEach((ellipsis) => {
  ellipsis.addEventListener("click", function (e) {
    if (previousOptionsContainer && e.target !== previousEllipsis) {
      previousOptionsContainer.style.display = "none";
    }
    const articleOptionsContainer = ellipsis.nextElementSibling;
    if (articleOptionsContainer.style.display != "block") {
      articleOptionsContainer.style.display = "block";
      document.onclick = function (e) {
        if (
          e.target.className !== ellipsis.nextElementSibling.classList[1] &&
          e.target !== ellipsis
        ) {
          ellipsis.nextElementSibling.style.display = "none";
        }
      };
    } else {
      articleOptionsContainer.style.display = "none";
    }
    previousOptionsContainer = ellipsis.nextElementSibling;
    previousEllipsis = ellipsis;
  });
});

// (un)highlight articles
document.querySelectorAll(".addToHighlighted").forEach((highlighterButton) => {
  highlighterButton.addEventListener("click", async () => {
    const article_id = highlighterButton.id;
    const highlightState = highlighterButton.lastElementChild.innerText;
    let action;
    if (highlightState == "Highlight article") {
      action = "highlight";
    } else {
      action = "unhighlight";
    }
    try {
      const res = await fetch(
        `../api/highlight_article/${article_id}/${action}`,
        get_fetch_settings("POST")
      );
      if (!res.ok) {
        showMessage("Error: List couldn't be filtered!", "Error");
      } else {
        const context = await res.json();
        showMessage(context, "Success");
        if (action == "highlight") {
          highlighterButton.innerHTML = `<i class="fas fa-times"></i><span>Unhighlight article</span>`;
        } else {
          highlighterButton.innerHTML = `<i class="fas fa-highlighter"></i><span>Highlight article</span>`;
        }
      }
    } catch (e) {
      showMessage("Error: Network error detected!", "Error");
    }
  });
});

// open addtolist menu
document.querySelectorAll(".addToList").forEach((element) => {
  element.addEventListener("click", () => {
    const addToListForm = element.parentElement.nextElementSibling;
    addToListForm.style.display = "block";
  });
});

// close addtolist menu
document.querySelectorAll(".addToListForm .fa-times").forEach((element) => {
  element.addEventListener("click", () => {
    element.parentElement.style.display = "none";
  });
});

// add article to lists
document
  .querySelectorAll(".addToListForm .saveButton")
  .forEach((saveButton) => {
    let list_ids;
    saveButton.addEventListener("click", async () => {
      let article_id = saveButton.parentElement.parentElement.parentElement.id;
      article_id = article_id.replace("article", "");
      saveButton.parentElement.previousElementSibling
        .querySelectorAll("input")
        .forEach((input) => {
          if (input.checked) {
            if (list_ids) {
              list_ids += "," + input.value;
            } else {
              list_ids = input.value;
            }
          }
        });
      try {
        const res = await fetch(
          `../api/add_article_to_lists/${article_id}/${list_ids}`,
          get_fetch_settings("POST")
        );
        if (!res.ok) {
          showMessage("Error: Article couldn't be saved!", "Error");
        } else {
          const context = await res.json();
          showMessage(context, "Success");
          window.location.reload();
        }
      } catch (e) {
        showMessage("Error: Network error detected!", "Error");
      }
    });
  });
