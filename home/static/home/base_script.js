// function to get cookie by name; retrieved from https://docs.djangoproject.com/en/3.1/ref/csrf/

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// creates settings necesseary for DRF use

function get_fetch_settings(inputMethod) {
  const settings = {
    method: inputMethod,
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    mode: "same-origin",
  };
  return settings;
}

// Gives user feedback if action that includes DRF has been succesfull or not

function showMessage(message, type) {
  document.querySelectorAll(".messages").forEach((message) => {
    message.innerHTML = "";
  });
  const messages = document.createElement("ul");
  messages.classList.add("messages");
  const state = document.createElement("li");
  state.innerText = message;
  type == "Success"
    ? state.classList.add("success")
    : state.classList.add("error");
  messages.appendChild(state);
  document.querySelector(".overlay").appendChild(messages);
}

// main search with autocomplete
document
  .getElementById("mainAutocomplete")
  .addEventListener("keyup", async function (e) {
    let search_term = document.getElementById("mainAutocomplete").value;
    if (e.key == "Enter" && search_term.replaceAll(/\s/g, "") != "") {
      window.location.href = `../../search_results/${search_term}`;
    } else {
      let results_list = document.getElementById("mainAutocomplete_result");
      if (search_term && search_term.replaceAll(/\s/g, "") != "") {
        try {
          const res = await fetch(
            `../../api/search_site/${search_term}`,
            get_fetch_settings("GET")
          );
          if (!res.ok) {
            showMessage("Error: Site couldn't be searched!", "Error");
          } else {
            document.querySelector(".mainInputSearch").style.borderRadius =
              "8px 8px 0 0";
            const context = await res.json();
            results_list.style.display = "flex";
            results_list.innerHTML = "";
            if (context[0].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Lists</div>`;
              context[0].forEach((list) => {
                const listRes = `<div class="searchResult"><img src="/static/home/media/bigger_favicon.png"><span>${list.name}</span><a href="../../list/${list.list_id}"></a></div>`;
                results_list.innerHTML += listRes;
              });
            }
            if (context[1].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Sources</div>`;
              context[1].forEach((source) => {
                const sourceRes = `<div class="searchResult"><img src="/static/${source.favicon_path}"><span>${source.domain}</span><a href="../../source/profile/${source.domain}"></a></div>`;
                results_list.innerHTML += sourceRes;
              });
            }
            if (context[2].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Articles</div>`;
              context[2].forEach((article) => {
                const articleRes = `<div class="searchResult"><img src="/static/${article.source.favicon_path}"><span>${article.title}</span><a href="${article.link}"></a></div>`;
                results_list.innerHTML += articleRes;
              });
            }
          }
        } catch (e) {
          showMessage("Error: Network error detected!", "Error");
        }
        document.onclick = function (e) {
          if (e.target.id !== "autocomplete_list_results") {
            results_list.style.display = "none";
            document.querySelector(".mainInputSearch").style.borderRadius =
              "8px";
          }
        };
      } else {
        results_list.style.display = "none";
        document.querySelector(".mainInputSearch").style.borderRadius = "8px";
      }
    }
  });

//get search results
document
  .querySelector(".mainSearchContainer i")
  .addEventListener("click", () => {
    search_term = document.querySelector(".mainInputSearch").value;
    if (search_term.replaceAll(/\s/g, "") != "") {
      window.location.href = `../../search_results/${search_term}`;
    }
  });

//Dropdown User Menu
const dropdownButton = document.querySelector(".fa-sort-down");
dropdownButton.addEventListener("click", () => {
  const profileMenu = document.querySelector(".profileMenu");
  if (profileMenu.style.display == "block") {
    profileMenu.style.display = "none";
  } else {
    profileMenu.style.display = "block";
  }
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
    document.querySelectorAll(".addToListForm").forEach((element) => {
      element.style.display = "none";
    });
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
