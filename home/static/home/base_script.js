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
            `http://127.0.0.1:8000/api/search_site/${search_term}`,
            get_fetch_settings("GET")
          );
          if (!res.ok) {
            showMessage("Error: Network request failed unexpectedly!", "Error");
          } else {
            document.querySelector(".mainInputSearch").style.borderRadius =
              "8px 8px 0 0";
            const context = await res.json();
            results_list.style.display = "flex";
            results_list.innerHTML = "";
            if (context[0].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Lists</div>`;
              for (let i = 0, j = context[0].length; i < j; i++) {
                let list = context[0][i];
                let list_url = context[4][i];
                let list_pic;
                if (list.list_pic) {
                  list_pic = list.list_pic;
                } else {
                  list_pic = "/static/home/media/bigger_favicon.png";
                }
                const listRes = `<div class="searchResult"><img src="${list_pic}"><span>${list.name}</span><a href="${list_url}"></a></div>`;
                results_list.innerHTML += listRes;
              }
            }
            if (context[1].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Sources</div>`;
              context[1].forEach((source) => {
                const sourceRes = `<div class="searchResult"><img src="/static/${source.favicon_path}"><span>${source.name}</span><a href="../../source/profile/${source.slug}"></a></div>`;
                results_list.innerHTML += sourceRes;
              });
            }
            if (context[2].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Articles</div>`;
              for (let i = 0, j = context[2].length; i < j; i++) {
                let xfavicon = context[3][i];
                let xtitle = context[2][i].title;
                let xlink = context[2][i].link;
                const articleRes = `<div class="searchResult"><img src="/static/${xfavicon}"><span>${xtitle}</span><a href="${xlink}"></a></div>`;
                results_list.innerHTML += articleRes;
              }
            }
          }
        } catch (e) {
          showMessage("Error: Unexpected error has occurred!", "Error");
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
if (dropdownButton) {
  dropdownButton.addEventListener("click", () => {
    const profileMenu = document.querySelector(".profileMenu");
    if (profileMenu.style.display == "flex") {
      profileMenu.style.display = "none";
    } else {
      profileMenu.style.display = "flex";
    }
  });
}

function checkForOpenContainers() {
  let allContainersClosed = true;
  const addToListForms = document.querySelectorAll(".addToListForm");
  // const formContainers = document.querySelectorAll(".formContainer");
  for (let i = 0, j = addToListForms.length; i < j; i++) {
    if (
      addToListForms[i].style.display != "none" &&
      addToListForms[i].style.display
    ) {
      allContainersClosed = false;
      return allContainersClosed;
    }
  }
  // for (let i = 0, j = formContainers.length; i < j; i++) {
  //   if (
  //     formContainers[i].style.display != "none" &&
  //     formContainers[i].style.display
  //   ) {
  //     allContainersClosed = false;
  //     return allContainersClosed;
  //   }
  // }
  return allContainersClosed;
}

// article ellipsis options
let previousOptionsContainer;
let previousEllipsis;
document
  .querySelectorAll(".articleContainer .fa-ellipsis-h")
  .forEach((ellipsis) => {
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
        console.log(highlighterButton.closest(".articleContainer").id);
        const article_id = highlighterButton
          .closest(".articleContainer")
          .id.replace("article_id_", "");
        // const article_id = highlighterButton.id;
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
            `http://127.0.0.1:8000/api/highlighted_articles/`,
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
          showMessage("Error: Unexpected error has occurred!", "Error");
        }
      }
    });
  });

// open addtolist menu
document.querySelectorAll(".addToListButton").forEach((element) => {
  element.addEventListener("click", () => {
    if (!element.classList.contains("registrationLink")) {
      const allContainersClosed = checkForOpenContainers();
      if (allContainersClosed) {
        const addToListForm = element.parentElement.nextElementSibling;
        addToListForm.style.display = "block";
      }
    }
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
    saveButton.addEventListener("click", async () => {
      let article_id =
        saveButton.parentElement.parentElement.parentElement.id.replace(
          "article_id_",
          ""
        );
      let lists_status = [];
      let initial_lists_status = [];
      let list_ids = [];
      const input_list =
        saveButton.parentElement.parentElement.querySelectorAll(
          ".listContainer input"
        );
      for (let i = 0, j = input_list.length; i < j; i++) {
        initial_lists_status.push(input_list[i].className);
        list_ids.push(input_list[i].id.replace("list_id_", ""));
      }
      saveButton.parentElement.previousElementSibling
        .querySelectorAll("input")
        .forEach((input) => {
          if (input.checked) {
            lists_status.push("articleInList");
          } else {
            lists_status.push("articleNotInList");
          }
        });

      for (let i = 0, j = lists_status.length; i < j; i++) {
        if (lists_status[i] != initial_lists_status[i]) {
          if (initial_lists_status[i] == "articleNotInList") {
            let list_id = list_ids[i];
            try {
              const res = await fetch(
                `http://127.0.0.1:8000/api/lists/${list_id}/add_article_to_list/${article_id}/`,
                get_fetch_settings("POST")
              );
              if (!res.ok) {
                showMessage(
                  "Error: Network request failed unexpectedly!",
                  "Error"
                );
              } else {
                const context = await res.json();
                showMessage(context, "Success");
                window.location.reload();
              }
            } catch (e) {
              showMessage("Error: Unexpected error has occurred!", "Error");
            }
          } else {
            try {
              let list_id = list_ids[i];
              const res = await fetch(
                `http://127.0.0.1:8000/api/lists/${list_id}/delete_article_from_list/${article_id}/`,
                get_fetch_settings("DELETE")
              );
              if (!res.ok) {
                showMessage(
                  "Error: Network request failed unexpectedly!",
                  "Error"
                );
              } else {
                const context = await res.json();
                showMessage(context, "Remove");
                window.location.reload();
              }
            } catch (e) {
              showMessage("Error: Unexpected error has occurred!", "Error");
            }
          }
        }
      }
    });
  });

// open List Create Menu
document.querySelectorAll(".createNewListButton").forEach((button) => {
  button.addEventListener("click", () => {
    if (!button.classList.contains("registrationLink")) {
      button.parentElement.parentElement.style.display = "none";
      button.parentElement.parentElement.parentElement.querySelector(
        ".formContainer"
      ).style.display = "flex";
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

// Old:
// open List Create Menu
// document.querySelectorAll(".createNewListButton").forEach((button) => {
//   button.addEventListener("click", () => {
//     if (!button.classList.contains("registrationLink")) {
//       button.parentElement.parentElement.style.display = "none";
//       document.querySelector(".createListMenu").style.display = "flex";
//     }
//   });
// });

// // close list create menu
// if (document.querySelector(".createListMenu .closeFormContainerButton")) {
//   document
//     .querySelector(".createListMenu .closeFormContainerButton")
//     .addEventListener("click", () => {
//       document.querySelector(".createListMenu").style.display = "none";
//     });
// }

// // select sources
// document.querySelectorAll(".selectContainer ul li").forEach((choice) => {
//   choice.addEventListener("click", () => {
//     document.querySelector("summary").innerHTML = choice.innerHTML;
//     document.querySelector("details").removeAttribute("open");
//   });
// });

// if (document.querySelector("details")) {
//   document.querySelector("details").addEventListener("click", () => {
//     document.onclick = function (e) {
//       if (e.target != document.querySelector("summary ul")) {
//         document.querySelector("details").removeAttribute("open");
//       }
//     };
//   });
// }

//activate notification popup
document
  .querySelector(".userSpace .notificationBell")
  .addEventListener("click", async () => {
    const notificationPopup = document.querySelector(
      ".userSpace .notificationContainer"
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
          `http://127.0.0.1:8000/api/notifications/`,
          get_fetch_settings("PUT")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!", "Error");
        }
      } catch (e) {
        showMessage("Error: Unexpected error has occurred!", "Error");
      }
    }
  });

//Notification switch
document
  .querySelectorAll(".notificationHeadersContainer div")
  .forEach((headerContainer) => {
    headerContainer.addEventListener("click", () => {
      document
        .querySelectorAll(".notificationHeadersContainer div")
        .forEach((header) => {
          if (header.classList.contains("activeNotificationCategory")) {
            header.classList.remove("activeNotificationCategory");
          } else {
            header.classList.add("activeNotificationCategory");
          }
        });
      document
        .querySelectorAll(".notificationsContainer")
        .forEach((container) => {
          if (container.classList.contains("activeNotificationContainer")) {
            container.classList.remove("activeNotificationContainer");
          } else {
            container.classList.add("activeNotificationContainer");
          }
        });
    });
  });

// Carousell

document.addEventListener("click", (e) => {
  let handle;
  if (e.target.matches(".handle")) {
    handle = e.target;
  } else {
    handle = e.target.closest(".handle");
  }
  if (handle != null) onHandleClick(handle);
});

const throttleProgressBar = throttle(() => {
  document.querySelectorAll(".progressBar").forEach(calculateProgressBar);
}, 250);
window.addEventListener("resize", throttleProgressBar);

document.querySelectorAll(".progressBar").forEach(calculateProgressBar);

function calculateProgressBar(progressBar) {
  progressBar.innerHTML = "";
  const slider = progressBar.closest(".sliderWrapper").querySelector(".slider");
  const itemCount = slider.children.length;
  const itemsPerScreen = parseInt(
    getComputedStyle(slider).getPropertyValue("--items-per-screen")
  );
  let sliderIndex = parseInt(
    getComputedStyle(slider).getPropertyValue("--slider-index")
  );
  const progressBarItemCount = Math.ceil(itemCount / itemsPerScreen);

  if (sliderIndex >= progressBarItemCount) {
    slider.style.setProperty("--slider-index", progressBarItemCount - 1);
    sliderIndex = progressBarItemCount - 1;
  }

  for (let i = 0; i < progressBarItemCount; i++) {
    const barItem = document.createElement("div");
    barItem.classList.add("progressItem");
    if (i === sliderIndex) {
      barItem.classList.add("active");
    }
    progressBar.append(barItem);
  }
}

function onHandleClick(handle) {
  const progressBar = handle
    .closest(".sliderWrapper")
    .querySelector(".progressBar");
  const slider = handle
    .closest(".sliderContentContainer")
    .querySelector(".slider");
  const sliderIndex = parseInt(
    getComputedStyle(slider).getPropertyValue("--slider-index")
  );
  const progressBarItemCount = progressBar.children.length;
  if (handle.classList.contains("leftHandle")) {
    if (sliderIndex - 1 < 0) {
      slider.style.setProperty("--slider-index", progressBarItemCount - 1);
      progressBar.children[sliderIndex].classList.remove("active");
      progressBar.children[progressBarItemCount - 1].classList.add("active");
    } else {
      slider.style.setProperty("--slider-index", sliderIndex - 1);
      progressBar.children[sliderIndex].classList.remove("active");
      progressBar.children[sliderIndex - 1].classList.add("active");
    }
  }

  if (handle.classList.contains("rightHandle")) {
    if (sliderIndex + 1 >= progressBarItemCount) {
      slider.style.setProperty("--slider-index", 0);
      progressBar.children[sliderIndex].classList.remove("active");
      progressBar.children[0].classList.add("active");
    } else {
      slider.style.setProperty("--slider-index", sliderIndex + 1);
      progressBar.children[sliderIndex].classList.remove("active");
      progressBar.children[sliderIndex + 1].classList.add("active");
    }
  }
}

function throttle(cb, delay = 1000) {
  let shouldWait = false;
  let waitingArgs;
  const timeoutFunc = () => {
    if (waitingArgs == null) {
      shouldWait = false;
    } else {
      cb(...waitingArgs);
      waitingArgs = null;
      setTimeout(timeoutFunc, delay);
    }
  };

  return (...args) => {
    if (shouldWait) {
      waitingArgs = args;
      return;
    }

    cb(...args);
    shouldWait = true;
    setTimeout(timeoutFunc, delay);
  };
}
