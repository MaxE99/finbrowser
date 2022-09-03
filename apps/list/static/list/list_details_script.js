const subscribeButton = document.querySelector(".subscribeButton");

if (subscribeButton) {
  subscribeButton.addEventListener("click", async () => {
    if (!subscribeButton.classList.contains("registrationLink")) {
      try {
        const list_id = document
          .querySelector(".rightFirstRowContainer h3")
          .id.replace("list_detail_for_", "");
        let action = subscribeButton.innerText;
        const res = await fetch(
          `../../api/lists/${list_id}/list_change_subscribtion_status/`,
          get_fetch_settings("POST")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!", "Error");
        } else {
          const context = await res.json();
          if (action == "Subscribe") {
            subscribeButton.classList.replace("unsubscribed", "subscribed");
            subscribeButton.innerText = "Subscribed";
            showMessage(context, "Success");
          } else {
            subscribeButton.classList.replace("subscribed", "unsubscribed");
            subscribeButton.innerText = "Subscribe";
            showMessage(context, "Remove");
          }
        }
      } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
    }
  });
}


//check if createListMenu at 7nth spot
function check_interaction_wrapper_at_last_spot(sliderWrapper, closeMenu) {
  spot = sliderWrapper.querySelectorAll(".contentWrapper").length;
  items_per_screen = getComputedStyle(
    sliderWrapper.querySelector(".slider")
  ).getPropertyValue("--items-per-screen");
  if (spot % items_per_screen == 0) {
    if (closeMenu) {
      sliderWrapper.querySelector(".slider").style.zIndex = "";
    } else {
      sliderWrapper.querySelector(".slider").style.zIndex = "1000";
    }
  }
}


const editButton = document.querySelector(".editButton");
const listName = document.querySelector(".rightFirstRowContainer h3").innerText;

function openEditMenu() {
  editButton.remove();
  if (check_device_width_below(500)) {
    document.querySelector(
      ".notificationAndSubscribtionContainer .fa-bell"
    ).style.display = "none";
  }
  document.querySelector(".rightFirstRowContainer h3").style.display = "none";
  document.querySelector(".nameChangeContainer").style.display = "block";
  document.querySelector(".nameChangeContainer #id_name").value = listName;
  document.querySelector(".listPictureContainer #id_list_pic").style.display =
    "block";
  document.querySelector(".fa-camera").style.display = "block";
  document.querySelector(".buttonContainer").style.display = "flex";
  document.querySelector(".addSourcesButton").style.display = "flex";
  document
    .querySelectorAll(".highlightedArticlesContainer .article .fa-ellipsis-h")
    .forEach((ellipsis) => {
      ellipsis.style.display = "none";
    });
  const deleteArticlesButton = document.querySelectorAll(".article .fa-times");
  deleteArticlesButton.forEach((closeButton) => {
    closeButton.style.display = "block";
    closeButton.addEventListener("click", async () => {
      try {
        const list_id = document
          .querySelector(".rightFirstRowContainer h3")
          .id.replace("list_detail_for_", "");
        const article_id = closeButton.parentElement.id.replace("article", "");
        const res = await fetch(
          `../../api/lists/${list_id}/delete_article_from_list/${article_id}/`,
          get_fetch_settings("DELETE")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!", "Error");
        } else {
          const context = await res.json();
          showMessage(context, "Remove");
          closeButton.parentElement.remove();
        }
      } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
    });
  });
  document.querySelectorAll(".sourceDeleteOption").forEach((trashButton) => {
    if (trashButton.style.display == "none" || !trashButton.style.display) {
      trashButton.style.display = "block";
      trashButton.addEventListener("click", async () => {
        try {
          const list_id = document
            .querySelector(".rightFirstRowContainer h3")
            .id.replace("list_detail_for_", "");
          const source_id = trashButton.id.replace("source_id_", "");
          const res = await fetch(
            `../../api/lists/${list_id}/delete_source_from_list/${source_id}/`,
            get_fetch_settings("DELETE")
          );
          if (!res.ok) {
            showMessage("Error: Network request failed unexpectedly!", "Error");
          } else {
            const context = await res.json();
            showMessage(context, "Remove");
            trashButton.parentElement.parentElement.remove();
          }
        } catch (e) {
          // showMessage("Error: Unexpected error has occurred!", "Error");
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
if (sources.length === 1) {
  openEditMenu();
}

if (document.querySelector(".deleteListButton")) {
  document
    .querySelector(".deleteListButton")
    .addEventListener("click", async () => {
      try {
        const list_id = document
          .querySelector(".rightFirstRowContainer h3")
          .id.replace("list_detail_for_", "");
        const res = await fetch(
          `../../api/lists/${list_id}/`,
          get_fetch_settings("DELETE")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!", "Error");
        } else {
          const context = await res.json();
          showMessage(context, "Remove");
          window.location.href = "../../lists";
        }
      } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
    });
}

//open add sources menu
if (document.querySelector(".addSourcesButton")) {
  document.querySelector(".addSourcesButton").addEventListener("click", () => {
    document.querySelector(".addSourcesForm").style.display = "flex";
    check_interaction_wrapper_at_last_spot(
      document.querySelector(".sliderWrapper"),
      false
    );
  });
}

//close add sources menu
if (document.querySelector(".addSourcesForm .closeFormContainerButton")) {
  document
    .querySelector(".addSourcesForm .closeFormContainerButton")
    .addEventListener("click", () => {
      document.querySelector(".addSourcesForm").style.display = "none";
      check_interaction_wrapper_at_last_spot(
        document.querySelector(".sliderWrapper"),
        true
      );
    });
}

// add Sources Search
let selected_sources = [];
if (document.querySelector(".addSourcesForm #textInput")) {
  document
    .querySelector(".addSourcesForm #textInput")
    .addEventListener("keyup", async function (e) {
      let search_term = document.querySelector(
        ".addSourcesForm #textInput"
      ).value;
      let results_list = document.querySelector(
        ".addSourcesForm #searchResultsContainer"
      );
      let selected_list = document.querySelector(
        ".addSourcesForm .selectionContainer"
      );
      const list_id = document
        .querySelector(".rightFirstRowContainer h3")
        .id.replace("list_detail_for_", "");
      if (search_term && search_term.replaceAll(/\s/g, "") != "") {
        results_list.style.display = "block";
        selected_list.style.display = "none";
        try {
          const res = await fetch(
            `../../api/sources/?list_search=${search_term}&list_id=${list_id}`,
            get_fetch_settings("GET")
          );
          if (!res.ok) {
            showMessage("Error: Network request failed unexpectedly!", "Error");
          } else {
            const context = await res.json();
            results_list.innerHTML = "";
            const resultHeader = document.createElement("div");
            resultHeader.innerText = "Results:";
            results_list.append(resultHeader);
            if (context.length > 0) {
              context.forEach((source) => {
                if (selected_sources.includes(source.source_id) == false) {
                  const searchResult = document.createElement("div");
                  searchResult.classList.add("searchResult");
                  const resultImage = document.createElement("img");
                  resultImage.src = `https://finbrowser.s3.us-east-2.amazonaws.com/static/${source.favicon_path}`;
                  const sourceName = document.createElement("span");
                  sourceName.innerText = source.name;
                  sourceName.id = `source_id_${source.source_id}`;
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
                      selected_sources.push(source.source_id);
                      const removeSourceButton = document.createElement("i");
                      removeSourceButton.classList.add("fas", "fa-trash");
                      removeSourceButton.addEventListener("click", () => {
                        removeSourceButton.parentElement.remove();
                        selected_sources = selected_sources.filter(function (
                          e
                        ) {
                          return (
                            e.toString() !==
                            removeSourceButton.previousElementSibling.id.replace(
                              "source_id_",
                              ""
                            )
                          );
                        });
                      });
                      searchResult.appendChild(removeSourceButton);
                      selected_list.appendChild(searchResult);
                      results_list.style.display = "none";
                      selected_list.style.display = "block";
                      document.querySelector(
                        ".addSourcesForm #textInput"
                      ).value = "";
                    }
                  );
                }
              });
            }
          }
        } catch (e) {
          // showMessage("Error: Unexpected error has occurred!", "Error");
        }
      } else {
        results_list.style.display = "none";
        selected_list.style.display = "block";
      }
    });
}

// add/confirm sources to list
if (document.querySelector(".addSourcesForm button")) {
  document
    .querySelector(".addSourcesForm button")
    .addEventListener("click", async () => {
      const list_id = document
        .querySelector(".rightFirstRowContainer h3")
        .id.replace("list_detail_for_", "");
      if (selected_sources.length) {
        selected_sources = selected_sources.join();
        try {
          const res = await fetch(
            `../../api/lists/${list_id}/add_sources/${selected_sources}/`,
            get_fetch_settings("POST")
          );
          if (!res.ok) {
            showMessage("Error: Network request failed unexpectedly!", "Error");
          } else {
            const context = await res.json();
            showMessage(context, "Success");
            window.location.reload();
          }
        } catch (e) {
          // showMessage("Error: Unexpected error has occurred!", "Error");
        }
      } else {
        showMessage("You need to select sources!", "Error");
      }
    });
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
    const rating = getNumericValue(id);
    const list_id = document
      .querySelector(".rightFirstRowContainer h3")
      .id.replace("list_detail_for_", "");
    try {
      const data = { list_id: list_id, rating: rating };
      const res = await fetch(`../../api/list_ratings/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        mode: "same-origin",
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        showMessage("Error: Network request failed unexpectedly!", "Error");
      } else {
        const context = await res.json();
        showMessage(context, "Success");
        window.location.reload();
      }
    } catch (e) {
      // showMessage("Error: Unexpected error has occurred!", "Error");
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
const rateListButton = document.querySelector(".rateListButton");
if (rateListButton) {
  rateListButton.addEventListener("click", () => {
    if (!rateListButton.classList.contains("registrationLink")) {
      document.querySelector(".rate-formUpperContainer").style.display =
        "block";
      document.querySelector(".rating").style.opacity = "0";
      document.querySelector(".ratingsAmmountContainer").style.opacity = "0";
      document.querySelector(".rateListButton").style.opacity = "0";
      document.querySelector(".rankingsHeader").style.opacity = "0";
    }
  });
}
