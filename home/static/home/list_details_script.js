const subscribeButton = document.querySelector(".subscribeButton");

if (subscribeButton) {
  subscribeButton.addEventListener("click", async () => {
    try {
      const url = window.location.href;
      const index = url.lastIndexOf("/");
      const list_id = url.substring(index + 1);
      let action = subscribeButton.innerText;
      if (action === "Subscribed") {
        action = "Unsubscribe";
      } else {
        action = "Subscribe";
      }
      const res = await fetch(
        `../api/list_change_subscribtion_status/${list_id}/${action}`,
        get_fetch_settings("POST")
      );
      if (!res.ok) {
        showMessage("Error: List can't be subscribed!", "Error");
      } else {
        const context = await res.json();
        showMessage(context, "Success");
        if (action == "Subscribe") {
          subscribeButton.classList.replace("unsubscribed", "subscribed");
          subscribeButton.innerText = "Unsubscribe";
        } else {
          subscribeButton.classList.replace("subscribed", "unsubscribed");
          subscribeButton.innerText = "Subscribe";
        }
      }
    } catch (e) {
      showMessage("Error: Network error detected!", "Error");
    }
  });
}

const editButton = document.querySelector(".editButton");
const listName = document.querySelector(".rightFirstRowContainer h3").innerText;

function openEditMenu() {
  editButton.remove();
  document.querySelector(".rightFirstRowContainer h3").style.display = "none";
  document.querySelector(".nameChangeContainer").style.display = "block";
  document.querySelector(".nameChangeContainer #id_name").value = listName;
  document.getElementById("id_list_pic").style.display = "block";
  document.querySelector(".fa-camera").style.display = "block";
  document.querySelector(".buttonContainer").style.display = "flex";
  document.querySelector(".addSourcesButton").style.display = "flex";
  document.querySelectorAll(".sourceDeleteOption").forEach((trashButton) => {
    if (trashButton.style.display == "none" || !trashButton.style.display) {
      trashButton.style.display = "block";
      trashButton.addEventListener("click", async () => {
        try {
          const list_id = document
            .querySelector(".rightFirstRowContainer h3")
            .id.replace("list_detail_for_", "");
          const source =
            trashButton.nextElementSibling.nextElementSibling.children[0]
              .innerText;
          const res = await fetch(
            `../api/delete_source_from_list/${list_id}/${source}`,
            get_fetch_settings("DELETE")
          );
          if (!res.ok) {
            showMessage("Error: List can't be subscribed!", "Error");
          } else {
            const context = await res.json();
            showMessage(context, "Success");
            trashButton.parentElement.parentElement.remove();
          }
        } catch (e) {
          showMessage("Error: Network error detected!", "Error");
        }
      });
    }
  });
}

if (editButton) {
  editButton.addEventListener("click", openEditMenu);
}

// If list has no sources = directly open edit menu
const sources = document.querySelectorAll(".slider-content li");
if (!sources.length) {
  openEditMenu();
}

if (document.querySelector(".deleteListButton")) {
  document
    .querySelector(".deleteListButton")
    .addEventListener("click", async () => {
      try {
        const url = window.location.href;
        const index = url.lastIndexOf("/");
        const list_id = url.substring(index + 1);
        const res = await fetch(
          `../api/delete_list/${list_id}`,
          get_fetch_settings("DELETE")
        );
        if (!res.ok) {
          showMessage("Error: List can't be deleted!", "Error");
        } else {
          const context = await res.json();
          showMessage(context, "Success");
          window.location.href = "../lists";
        }
      } catch (e) {
        showMessage("Error: Network error detected!", "Error");
      }
    });
}

// add Sources Search
let selected_sources = [];
document
  .getElementById("addSourcesInput")
  .addEventListener("keyup", async function (e) {
    let search_term = document.getElementById("addSourcesInput").value;
    let results_list = document.getElementById("sourceSearchResults");
    let selected_list = document.querySelector(".selectedSourcesContainer");
    const url = window.location.href;
    const index = url.lastIndexOf("/");
    const list_id = url.substring(index + 1);
    if (search_term && search_term.replaceAll(/\s/g, "") != "") {
      results_list.style.display = "block";
      selected_list.style.display = "none";
      try {
        const res = await fetch(
          `../../api/search_sources_for_list/${list_id}/${search_term}`,
          get_fetch_settings("GET")
        );
        if (!res.ok) {
          showMessage("Error: Site couldn't be searched!", "Error");
        } else {
          const context = await res.json();
          results_list.innerHTML = "";
          if (context.length > 0) {
            const resultHeader = document.createElement("div");
            resultHeader.innerText = "Results:";
            results_list.append(resultHeader);
            context.forEach((source) => {
              if (selected_sources.includes(source.domain) == false) {
                const searchResult = document.createElement("div");
                searchResult.classList.add("searchResult");
                const resultImage = document.createElement("img");
                resultImage.src = `/static/${source.favicon_path}`;
                const sourceName = document.createElement("span");
                sourceName.innerText = source.domain;
                searchResult.append(resultImage, sourceName);
                results_list.appendChild(searchResult);
                searchResult.addEventListener(
                  "click",
                  function addSelectedSource() {
                    // Remove the listener from the element the first time the listener is run:
                    searchResult.removeEventListener(
                      "click",
                      addSelectedSource
                    );
                    selected_sources.push(source.domain);
                    const removeSourceButton = document.createElement("i");
                    removeSourceButton.classList.add("fas", "fa-trash");
                    removeSourceButton.addEventListener("click", () => {
                      removeSourceButton.parentElement.remove();
                      selected_sources = selected_sources.filter(function (e) {
                        return (
                          e !==
                          removeSourceButton.previousElementSibling.innerText
                        );
                      });
                    });
                    searchResult.appendChild(removeSourceButton);
                    selected_list.appendChild(searchResult);
                    results_list.style.display = "none";
                    selected_list.style.display = "block";
                    document.getElementById("addSourcesInput").value = "";
                  }
                );
              }
            });
          }
        }
      } catch (e) {
        showMessage("Error: Network error detected!", "Error");
      }
    } else {
      results_list.style.display = "none";
      selected_list.style.display = "block";
    }
  });

//open add sources menu
if (document.querySelector(".addSourcesButton")) {
  document.querySelector(".addSourcesButton").addEventListener("click", () => {
    document.querySelector(".addSourcesForm").style.display = "flex";
    document.querySelector(".listOverlay").style.opacity = "0.5";
  });
}

//close add sources menu
document
  .querySelector(".addSourcesCloseButton")
  .addEventListener("click", () => {
    document.querySelector(".addSourcesForm").style.display = "none";
    document.querySelector(".listOverlay").style.opacity = "1";
  });

// add/confirm sources to list
document
  .querySelector(".addSourcesForm button")
  .addEventListener("click", async () => {
    const url = window.location.href;
    const index = url.lastIndexOf("/");
    const list_id = url.substring(index + 1);
    if (selected_sources.length) {
      try {
        const res = await fetch(
          `../api/add_sources/${selected_sources}/${list_id}`,
          get_fetch_settings("POST")
        );
        if (!res.ok) {
          showMessage("Error: List can't be subscribed!", "Error");
        } else {
          const context = await res.json();
          showMessage(context, "Success");
          window.location.reload();
        }
      } catch (e) {
        showMessage("Error: Network error detected!", "Error");
      }
    } else {
      showMessage("You need to select sources!", "Error");
    }
  });

const highlightedArticles = document.querySelector(
  ".highlightedArticlesContainer"
);

// If there are no highlightedArticles change style of container so that flex-wrap is effective
if (!highlightedArticles) {
  document.querySelector(".articleSpace").style.display = "block";
}

// rating functions
const one = document.getElementById("first");
const two = document.getElementById("second");
const three = document.getElementById("third");
const four = document.getElementById("fourth");
const five = document.getElementById("fifth");

// get the form, confirm-box and csrf token
// const form = document.querySelector(".rate-form");
const confirmBox = document.getElementById("confirm-box");
// const csrf = document.getElementsByName("csrfmiddlewaretoken");

const handleStarSelect = (size, form) => {
  const children = form.children;
  for (let i = 0; i < children.length; i++) {
    if (i < size) {
      children[i].classList.add("checked");
    } else {
      children[i].classList.remove("checked");
    }
  }
};

const handleSelect = (selection) => {
  let form = document.querySelector(".rate-form");
  switch (selection) {
    case "first": {
      handleStarSelect(1, form);
      return;
    }
    case "second": {
      handleStarSelect(2, form);
      return;
    }
    case "third": {
      handleStarSelect(3, form);
      return;
    }
    case "fourth": {
      handleStarSelect(4, form);
      return;
    }
    case "fifth": {
      handleStarSelect(5, form);
      return;
    }
    default: {
      handleStarSelect(0, form);
    }
  }
};

const getNumericValue = (stringValue) => {
  let numericValue;
  if (stringValue === "first") {
    numericValue = 1;
  } else if (stringValue === "second") {
    numericValue = 2;
  } else if (stringValue === "third") {
    numericValue = 3;
  } else if (stringValue === "fourth") {
    numericValue = 4;
  } else if (stringValue === "fifth") {
    numericValue = 5;
  } else {
    numericValue = 0;
  }
  return numericValue;
};

if (one) {
  const arr = [one, two, three, four, five];

  arr.forEach((item) =>
    item.addEventListener("mouseover", (event) => {
      handleSelect(event.target.id);
    })
  );
}

document.querySelectorAll(".rankingStar").forEach((star) => {
  star.addEventListener("click", async (e) => {
    const id = e.target.id;
    // value of the rating translated into numeric
    const val_num = getNumericValue(id);
    const url = window.location.href;
    const index = url.lastIndexOf("/");
    const list_id = url.substring(index + 1);
    try {
      const res = await fetch(
        `../../api/rate_list/${list_id}/${val_num}`,
        get_fetch_settings("POST")
      );
      if (!res.ok) {
        showMessage("Error: Source can't be subscribed!", "Error");
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

//set stars to average rating
if (document.querySelector(".avgRating span")) {
  const average_rating = Math.round(
    document.querySelector(".avgRating span").innerText
  );
  handleStarSelect(average_rating, document.querySelector(".ratedContainer"));
}

// open rate list menu
document.querySelector(".rateListButton").addEventListener("click", () => {
  document.querySelector(".rate-formUpperContainer").style.display = "block";
  document.querySelector(".rating").style.opacity = "0";
  document.querySelector(".ratingsAmmountContainer").style.opacity = "0";
  document.querySelector(".rateListButton").style.opacity = "0";
  document.querySelector(".rankingsHeader").style.opacity = "0";
});

// if user already rated source = set stars to this rating
const user_rating = document.getElementById("user-rating").innerText;
let form = document.querySelector(".rate-form");
handleStarSelect(user_rating, form);
