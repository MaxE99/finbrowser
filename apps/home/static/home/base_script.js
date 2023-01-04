// open hamburger menu
document
  .querySelector(".headerContainer .fa-bars")
  .addEventListener("click", (e) => {
    if (e.target.classList.contains("fa-bars")) {
      e.target.classList.replace("fa-bars", "fa-times");
      e.target.classList.add("closeNavMenuButton");
    } else {
      e.target.classList.replace("fa-times", "fa-bars");
      e.target.classList.remove("closeNavMenuButton");
    }
    const horizontalNavigation = document.querySelector(
      ".horizontalNavigation"
    );
    horizontalNavigation.style.display !== "flex"
      ? (horizontalNavigation.style.display = "flex")
      : (horizontalNavigation.style.display = "none");
  });

// deactivate autocomplete for all inputs
document.querySelectorAll("input").forEach((input) => {
  input.setAttribute("autocomplete", "off");
});

// creates crsf token
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
    message.remove();
  });
  const messages = document.createElement("ul");
  messages.classList.add("messages");
  const state = document.createElement("li");
  state.innerText = message;
  if (type == "Success") {
    state.classList.add("success");
  } else if (type == "Remove") {
    state.classList.add("remove");
  } else {
    state.classList.add("error");
  }
  messages.appendChild(state);
  document.querySelector(".overlay").appendChild(messages);
}

// increase search bar width on smaller screens (onclick)
document
  .querySelector(".headerContainer #mainAutocomplete")
  .addEventListener("click", () => {
    if (
      check_device_width_below(500) &&
      document.querySelector(".headerContainer .mainSearchWrapper .fa-times")
        .style.display !== "flex"
    ) {
      const logoContainer = document.querySelector(
        ".headerContainer .logoContainer"
      );
      const switchButton = document.querySelector(".headerContainer .fa-bars");
      const mainSearchWrapper = document.querySelector(
        ".headerContainer .mainSearchWrapper"
      );
      const searchButton = document.querySelector(
        ".headerContainer .mainSearchWrapper .fa-search"
      );
      const closeButton = document.querySelector(
        ".headerContainer .mainSearchWrapper .fa-times"
      );
      logoContainer.style.display = "none";
      switchButton.style.display = "none";
      mainSearchWrapper.classList.add("fullWidthSearchWrapper");
      searchButton.style.display = "none";
      closeButton.style.display = "flex";
      closeButton.addEventListener("click", () => {
        logoContainer.style.display = "flex";
        switchButton.style.display = "flex";
        mainSearchWrapper.classList.remove("fullWidthSearchWrapper");
        closeButton.style.display = "none";
        searchButton.style.display = "flex";
      });
    }
  });

// document
//   .querySelector(".headerContainer #mainAutocomplete")
//   .addEventListener("click", () => {
//     if (
//       check_device_width_below(500) &&
//       !document.querySelector(
//         ".headerContainer .mainSearchWrapper .closeSearchIcon"
//       )
//     ) {
//       document.querySelector(".headerContainer .logoContainer").style.display =
//         "none";
//       document.querySelector(".headerContainer .fa-bars").style.display =
//         "none";
//       document.querySelector(
//         ".headerContainer .mainSearchWrapper"
//       ).style.width = "100%";
//       document.querySelector(
//         ".headerContainer .mainSearchContainer"
//       ).style.display = "flex";
//       document.querySelector(
//         ".headerContainer .mainSearchContainer"
//       ).style.justifyContent = "center";
//       document.querySelector(
//         ".headerContainer .mainSearchContainer"
//       ).style.position = "relative";
//       document.querySelector(
//         ".headerContainer .mainSearchContainer"
//       ).style.width = "90%";
//       document.querySelector(".headerContainer #mainAutocomplete").style.width =
//         "97.5%";
//       document.querySelector(
//         ".headerContainer #mainAutocomplete"
//       ).style.maxWidth = "unset";
//       const closeSearchIcon = document.createElement("i");
//       closeSearchIcon.classList.add("fas", "fa-times", "closeSearchIcon");
//       document
//         .querySelector(".headerContainer .mainSearchWrapper")
//         .appendChild(closeSearchIcon);
//       closeSearchIcon.addEventListener("click", () => {
//         document
//           .querySelector(".headerContainer .mainSearchWrapper .closeSearchIcon")
//           .remove();
//         document.querySelector(
//           ".headerContainer .logoContainer"
//         ).style.display = "";
//         document.querySelector(".headerContainer .fa-bars").style.display = "";
//         document.querySelector(
//           ".headerContainer .mainSearchWrapper"
//         ).style.width = "";
//         document.querySelector(
//           ".headerContainer .mainSearchContainer"
//         ).style.display = "";
//         document.querySelector(
//           ".headerContainer .mainSearchContainer"
//         ).style.justifyContent = "";
//         document.querySelector(
//           ".headerContainer .mainSearchContainer"
//         ).style.position = "";
//         document.querySelector(
//           ".headerContainer .mainSearchContainer"
//         ).style.width = "";
//         document.querySelector(
//           ".headerContainer #mainAutocomplete"
//         ).style.width = "";
//         document.querySelector(
//           ".headerContainer #mainAutocomplete"
//         ).style.maxWidth = "";
//       });
//     }
//   });

// main search with autocomplete
document
  .getElementById("mainAutocomplete")
  .addEventListener("keyup", async function (e) {
    let search_term = document.getElementById("mainAutocomplete").value;
    if (e.key == "Enter" && search_term.replaceAll(/\s/g, "") != "") {
      window.location.href = `../../../../../../search_results/${search_term}`;
    } else {
      let results_list = document.getElementById("mainAutocomplete_result");
      if (search_term && search_term.replaceAll(/\s/g, "") != "") {
        try {
          const res = await fetch(
            `../../../../../../api/search_site/${search_term}`,
            get_fetch_settings("GET")
          );
          if (!res.ok) {
            showMessage("Error: Network request failed unexpectedly!", "Error");
          } else {
            document.querySelector(".mainInputSearch").style.borderRadius =
              "0.8rem 0.8rem 0 0";
            const context = await res.json();
            results_list.style.display = "flex";
            results_list.innerHTML = "";
            if (context[0].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Stocks</div>`;
              context[0].forEach((stock) => {
                const sourceRes = `<div class="searchResult"><div class="stockContainer"><div class="stockTicker">${stock.ticker}</div><div class="companyName">${stock.full_company_name}</div><a href="../../../../../../stock/${stock.ticker}"></a></div></div>`;
                results_list.innerHTML += sourceRes;
              });
            }
            if (context[1].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Sources</div>`;
              context[1].forEach((source) => {
                const sourceRes = `<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${source.favicon_path}"><span>${source.name}</span><a href="../../../../../../source/${source.slug}"></a></div>`;
                results_list.innerHTML += sourceRes;
              });
            }
            if (context[2].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Articles</div>`;
              for (let i = 0, j = context[2].length; i < j; i++) {
                let xfavicon = context[3][i];
                let xtitle = context[2][i].title;
                let xlink = context[2][i].link;
                const articleRes = `<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${xfavicon}"><span>${xtitle}</span><a href="${xlink}" target="_blank"></a></div>`;
                results_list.innerHTML += articleRes;
              }
            }
          }
        } catch (e) {
          // showMessage("Error: Unexpected error has occurred!", "Error");
        }
        document.onclick = function (e) {
          if (e.target.id !== "autocomplete_list_results") {
            results_list.style.display = "none";
            document.querySelector(".mainInputSearch").style.borderRadius =
              "0.8rem";
          }
        };
      } else {
        results_list.style.display = "none";
        document.querySelector(".mainInputSearch").style.borderRadius =
          "0.8rem";
      }
    }
  });

//get search results
document
  .querySelector(".mainSearchContainer i")
  .addEventListener("click", () => {
    search_term = document.querySelector(".mainInputSearch").value;
    if (search_term.replaceAll(/\s/g, "") != "") {
      window.location.href = `../../../../../../search_results/${search_term}`;
    }
  });

//Dropdown User Menu
const dropdownButton = document.querySelector(".userProfile");
if (dropdownButton) {
  dropdownButton.addEventListener("click", () => {
    const profileMenu = document.querySelector(".profileMenu");
    if (profileMenu.style.display == "flex") {
      profileMenu.style.display = "none";
    } else {
      profileMenu.style.display = "flex";
      document.onclick = function (e) {
        const withinProfileMenu = e.target.closest(".profileMenu");
        const withinUserProfile = e.target.closest(".userProfile");
        if (!withinProfileMenu && !withinUserProfile) {
          profileMenu.style.display = "none";
        }
      };
    }
  });
}

// logout button click
document
  .querySelector(
    ".headerContainer .profileMenu .profileMenuOption:last-of-type"
  )
  .addEventListener("click", (e) => {
    e.target.querySelector("button").click();
  });

function checkForOpenContainers() {
  let allContainersClosed = true;
  const addToListForms = document.querySelectorAll(".addToListForm");
  for (let i = 0, j = addToListForms.length; i < j; i++) {
    if (
      addToListForms[i].style.display != "none" &&
      addToListForms[i].style.display
    ) {
      allContainersClosed = false;
      return allContainersClosed;
    }
  }
  return allContainersClosed;
}

// article ellipsis options
let previousOptionsContainer;
let previousEllipsis;
document.querySelectorAll(".fa-ellipsis-h").forEach((ellipsis) => {
  ellipsis.addEventListener("click", function (e) {
    const allContainersClosed = checkForOpenContainers();
    if (allContainersClosed) {
      if (previousOptionsContainer && e.target !== previousEllipsis) {
        previousOptionsContainer.style.display = "none";
      }
      const articleOptionsContainer = ellipsis.parentElement.querySelector(
        ".articleOptionsContainer"
      );
      if (articleOptionsContainer.style.display != "flex") {
        articleOptionsContainer.style.display = "flex";
        document.onclick = function (e) {
          if (e.target !== ellipsis) {
            ellipsis.parentElement.querySelector(
              ".articleOptionsContainer"
            ).style.display = "none";
          }
        };
      } else {
        articleOptionsContainer.style.display = "none";
      }
      previousOptionsContainer = ellipsis.parentElement.querySelector(
        ".articleOptionsContainer"
      );
      previousEllipsis = ellipsis;
    }
  });
});

// (un)highlight articles
document
  .querySelectorAll(".addToHighlightedButton")
  .forEach((highlighterButton) => {
    highlighterButton.addEventListener("click", async () => {
      if (!highlighterButton.classList.contains("registrationLink")) {
        const article_id = highlighterButton
          .closest(".articleContainer")
          .id.split("#")[1];
        const highlightState = highlighterButton.lastElementChild.innerText;
        let action;
        if (highlightState == "Highlight article") {
          action = "highlight";
        } else {
          action = "unhighlight";
        }
        try {
          const data = { article_id: article_id };
          const res = await fetch(
            `../../../../../../api/highlighted_articles/`,
            {
              method: "POST",
              headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                Accept: "application/json",
                "Content-Type": "application/json",
              },
              mode: "same-origin",
              body: JSON.stringify(data),
            }
          );
          if (!res.ok) {
            showMessage("Error: Network request failed unexpectedly!", "Error");
          } else {
            const context = await res.json();
            if (action == "highlight") {
              showMessage(context, "Success");
              highlighterButton.innerHTML = `<i class="fas fa-times"></i><span>Unhighlight article</span>`;
            } else {
              showMessage(context, "Remove");
              highlighterButton.innerHTML = `<i class="fas fa-highlighter"></i><span>Highlight article</span>`;
            }
          }
        } catch (e) {
          // // showMessage("Error: Unexpected error has occurred!", "Error");
        }
      }
    });
  });

// start of decompositioning code
function get_initial_list_statuses(element) {
  let initial_lists_status = [];
  let list_ids = [];
  const input_list = element.parentElement.nextElementSibling.querySelectorAll(
    ".listContainer input"
  );
  for (let i = 0, j = input_list.length; i < j; i++) {
    initial_lists_status.push(input_list[i].checked);
    list_ids.push(input_list[i].id.split("#")[1]);
  }
  return [initial_lists_status, list_ids];
}

function check_new_list_status(saveButton) {
  let lists_status = [];
  saveButton.parentElement.previousElementSibling
    .querySelectorAll("input")
    .forEach((input) => {
      lists_status.push(input.checked);
    });
  return lists_status;
}

async function add_article_to_list(list_id, article_id) {
  try {
    const res = await fetch(
      `../../../../../../api/lists/${list_id}/add_article_to_list/${article_id}/`,
      get_fetch_settings("POST")
    );
    if (!res.ok) {
      showMessage("Error: Network request failed unexpectedly!", "Error");
    }
  } catch (e) {
    // showMessage("Error: Unexpected error has occurred!", "Error");
  }
}

async function remove_article_from_list(list_id, article_id) {
  try {
    const res = await fetch(
      `../../../../../../api/lists/${list_id}/delete_article_from_list/${article_id}/`,
      get_fetch_settings("DELETE")
    );
    if (!res.ok) {
      showMessage("Error: Network request failed unexpectedly!", "Error");
    }
  } catch (e) {
    // showMessage("Error: Unexpected error has occurred!", "Error");
  }
}

// open addtolist menu
document.querySelectorAll(".addToListButton").forEach((element) => {
  element.addEventListener("click", () => {
    if (!element.classList.contains("registrationLink")) {
      const allContainersClosed = checkForOpenContainers();
      if (allContainersClosed) {
        let addToListForm = element.parentElement.nextElementSibling;
        addToListForm.style.display = "block";
      }
      let initial_lists_statuses = get_initial_list_statuses(element);
      let initial_lists_status = initial_lists_statuses[0];
      let addToListForm =
        element.parentElement.parentElement.querySelector(".addToListForm");
      if (addToListForm.querySelector(".saveButton")) {
        let saveButton = addToListForm.querySelector(".saveButton");
        saveButton.addEventListener("click", () => {
          let list_ids = initial_lists_statuses[1];
          let article_id = saveButton
            .closest(".articleContainer")
            .id.split("#")[1];
          let lists_status = check_new_list_status(saveButton);
          for (let i = 0, j = lists_status.length; i < j; i++) {
            if (lists_status[i] != initial_lists_status[i]) {
              if (initial_lists_status[i] == false) {
                add_article_to_list(list_ids[i], article_id);
              } else {
                remove_article_from_list(list_ids[i], article_id);
              }
            }
          }
          showMessage("Lists have been updated!", "Success");
          addToListForm.style.display = "none";
        });
      }
    }
  });
});

// close addtolist menu
document.querySelectorAll(".addToListForm .fa-times").forEach((element) => {
  element.addEventListener("click", () => {
    element.parentElement.parentElement.style.display = "none";
  });
});

// check window width
function check_device_width_below(check_width) {
  const current_screen_width =
    window.innerWidth ||
    document.documentElement.clientWidth ||
    document.body.clientWidth;
  if (current_screen_width < check_width) {
    return true;
  }
  return false;
}

// open List Create Menu
document.querySelectorAll(".createNewListButton").forEach((button) => {
  button.addEventListener("click", () => {
    if (!button.classList.contains("registrationLink")) {
      button.parentElement.parentElement.parentElement.querySelector(
        ".addToListForm"
      ).style.display = "none";
      if (check_device_width_below(500)) {
        document.querySelector(".smartphoneCreateListMenu").style.display =
          "flex";
      } else {
        button.parentElement.parentElement.parentElement.querySelector(
          ".createListMenu"
        ).style.display = "flex";
      }
    }
  });
});

// // close list create menu
document
  .querySelectorAll(".createListMenu .closeFormContainerButton")
  .forEach((closeButton) => {
    closeButton.addEventListener("click", () => {
      document.querySelectorAll(".createListMenu").forEach((menu) => {
        menu.style.display = "none";
      });
    });
  });

//activate notification popup
if (document.querySelector(".userSpace .notificationBell")) {
  document
    .querySelector(".userSpace .notificationBell")
    .addEventListener("click", async () => {
      const notificationPopup = document.querySelector(
        ".notificationPopupWrapper"
      );
      if (notificationPopup.style.display == "block") {
        notificationPopup.style.display = "none";
        document.querySelector(".unseenNotifications").remove();
        document
          .querySelectorAll(".unseenNotification")
          .forEach((notification) => {
            notification.classList.remove("unseenNotification");
          });
      } else {
        notificationPopup.style.display = "block";
        try {
          const res = await fetch(
            `../../../../../../api/notifications/`,
            get_fetch_settings("PUT")
          );
          if (!res.ok) {
            showMessage("Error: Network request failed unexpectedly!", "Error");
          }
        } catch (e) {
          // showMessage("Error: Unexpected error has occurred!", "Error");
        }
      }
    });
}

//Notification switch
const notificationTabs = document.querySelectorAll(
  ".notificationHeadersContainer div"
);
const notificationContent = document.querySelectorAll(
  ".notificationsContainer"
);
notificationTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    for (let i = 0, j = notificationTabs.length; i < j; i++) {
      notificationTabs[i].classList.remove("activeNotificationCategory");
      notificationContent[i].classList.remove("activeNotificationContainer");
    }
    notificationTabs[tab.dataset.forTab].classList.add(
      "activeNotificationCategory"
    );
    notificationContent[tab.dataset.forTab].classList.add(
      "activeNotificationContainer"
    );
  });
});

// Carousell

document.querySelectorAll(".handle").forEach((handle) => {
  handle.addEventListener("click", (e) => {
    const slider = e.target.closest(".sliderWrapper").querySelector(".slider");
    const sliderIndex = parseInt(
      getComputedStyle(slider).getPropertyValue("--slider-index")
    );
    const itemsPerScreen = parseInt(
      getComputedStyle(slider).getPropertyValue("--items-per-screen")
    );
    const progressBarItemCount = Math.ceil(
      slider.querySelectorAll(".contentWrapper").length / itemsPerScreen
    );
    if (handle.classList.contains("leftHandle")) {
      sliderIndex - 1 < 0
        ? slider.style.setProperty("--slider-index", progressBarItemCount - 1)
        : slider.style.setProperty("--slider-index", sliderIndex - 1);
    }
    if (handle.classList.contains("rightHandle")) {
      sliderIndex + 1 >= progressBarItemCount
        ? slider.style.setProperty("--slider-index", 0)
        : slider.style.setProperty("--slider-index", sliderIndex + 1);
    }
  });
});

// Source Subscribtion function
document
  .querySelectorAll(".sliderWrapper .slider .subscribeButton")
  .forEach((subscribeButton) => {
    subscribeButton.addEventListener("click", async () => {
      try {
        const source_id = subscribeButton
          .closest(".contentWrapper")
          .id.split("#")[1];
        const action = subscribeButton.innerText;
        const res = await fetch(
          `../../api/sources/${source_id}/source_change_subscribtion_status/`,
          get_fetch_settings("POST")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!", "Error");
        } else {
          const context = await res.json();
          if (action == "Subscribe") {
            subscribeButton.classList.add("subscribed");
            subscribeButton.innerText = "Subscribed";
            showMessage(context, "Success");
          } else {
            subscribeButton.classList.remove("subscribed");
            subscribeButton.innerText = "Subscribe";
            showMessage(context, "Remove");
          }
        }
      } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
    });
  });

//Notifications
document
  .querySelectorAll(".sliderWrapper .slider .notificationButton")
  .forEach((notificationButton) => {
    if (notificationButton) {
      notificationButton.addEventListener("click", async () => {
        try {
          const source_id = notificationButton
            .closest(".contentWrapper")
            .id.split("#")[1];
          const data = { source_id: source_id };
          const res = await fetch(`../../api/notifications/`, {
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
            if (
              notificationButton.classList.contains("notificationActivated")
            ) {
              notificationButton.classList.remove("notificationActivated");
              notificationButton.innerText = "Notification On";
              showMessage(context, "Remove");
            } else {
              notificationButton.classList.add("notificationActivated");
              notificationButton.innerText = "Notification Off";
              showMessage(context, "Success");
            }
          }
        } catch (e) {
          // showMessage("Error: Unexpected error has occurred!", "Error");
        }
      });
    }
  });

//change tabs
const tabs = document.querySelectorAll(".tabsContainer button");
const tabsContent = document.querySelectorAll(".tabsContent");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    for (let i = 0, j = tabs.length; i < j; i++) {
      tabs[i].classList.remove("activatedTab");
      tabsContent[i].classList.remove("tabsContentActive");
    }
    tabs[tab.dataset.forTab].classList.add("activatedTab");
    tabsContent[tab.dataset.forTab].classList.add("tabsContentActive");
  });
});
