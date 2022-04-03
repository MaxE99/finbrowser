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
// Autocomplete for search
document
  .getElementById("mainAutocomplete")
  .addEventListener("keyup", async () => {
    let search_term = document.getElementById("mainAutocomplete").value;
    let results_list = document.getElementById("mainAutocomplete_result");
    if (search_term && search_term.replaceAll(/\s/g, "") != "") {
      try {
        const res = await fetch(
          `../search_site/${search_term}`,
          get_fetch_settings("GET")
        );
        if (!res.ok) {
          showMessage("Error: Site couldn't be searched!", "Error");
        } else {
          const context = await res.json();
          results_list.style.display = "flex";
          results_list.innerHTML = "";
          if (context[0].length > 0) {
            results_list.innerHTML += `<div class="searchResultHeader">Lists</div>`;
            context[0].forEach((list) => {
              const listRes = `<a href="../list/${list.list_id}" class="searchResult">${list.name}</a>`;
              results_list.innerHTML += listRes;
            });
          }
          if (context[1].length > 0) {
            results_list.innerHTML += `<div class="searchResultHeader">Sources</div>`;
            context[1].forEach((source) => {
              const sourceRes = `<a href="../../sourceprofile/${source.domain}" class="searchResult">${source.domain}</a>`;
              results_list.innerHTML += sourceRes;
            });
          }
          if (context[2].length > 0) {
            results_list.innerHTML += `<div class="searchResultHeader">Articles</div>`;
            context[2].forEach((article) => {
              const articleRes = `<a href="${article.link}" class="searchResult">${article.title}</a>`;
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
        }
      };
    } else {
      results_list.style.display = "none";
    }
  });
