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
                let list_pic = "/static/home/media/bigger_favicon.png";
                if (list.list_pic) {
                  list_pic = list.list_pic;
                }
                const listRes = `<div class="searchResult"><img src="${list_pic}"><span>${list.name}</span><a href="../../list/${list.list_id}"></a></div>`;
                results_list.innerHTML += listRes;
              });
            }
            if (context[1].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Sources</div>`;
              context[1].forEach((source) => {
                const sourceRes = `<div class="searchResult"><img src="/static/${source.favicon_path}"><span>${source.name}</span><a href="../../source/profile/${source.domain}"></a></div>`;
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
  const formContainers = document.querySelectorAll(".formContainer");
  for (let i = 0, j = addToListForms.length; i < j; i++) {
    if (
      addToListForms[i].style.display != "none" &&
      addToListForms[i].style.display
    ) {
      allContainersClosed = false;
      return allContainersClosed;
    }
  }
  for (let i = 0, j = formContainers.length; i < j; i++) {
    if (
      formContainers[i].style.display != "none" &&
      formContainers[i].style.display
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
document.querySelectorAll(".article .fa-ellipsis-h").forEach((ellipsis) => {
  ellipsis.addEventListener("click", function (e) {
    const allContainersClosed = checkForOpenContainers();
    if (allContainersClosed) {
      if (previousOptionsContainer && e.target !== previousEllipsis) {
        previousOptionsContainer.style.display = "none";
      }
      const articleOptionsContainer = ellipsis.nextElementSibling;
      if (articleOptionsContainer.style.display != "flex") {
        articleOptionsContainer.style.display = "flex";
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
    }
  });
});

// (un)highlight articles
document.querySelectorAll(".addToHighlighted").forEach((highlighterButton) => {
  highlighterButton.addEventListener("click", async () => {
    if (!highlighterButton.classList.contains("registrationLink")) {
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
          `http://127.0.0.1:8000/api/highlight_article/${article_id}`,
          get_fetch_settings("POST")
        );
        if (!res.ok) {
          showMessage("Error: Article couldn't be filtered!", "Error");
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
    }
  });
});

// open addtolist menu
document.querySelectorAll(".addToList").forEach((element) => {
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
          `http://127.0.0.1:8000/api/add_article_to_lists/${article_id}/${list_ids}`,
          get_fetch_settings("POST")
        );
        if (!res.ok) {
          showMessage("Error: Article couldn't be added to list!", "Error");
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

// open List Create Menu
document.querySelectorAll(".createNewListButton").forEach((button) => {
  button.addEventListener("click", () => {
    if (!button.classList.contains("registrationLink")) {
      button.parentElement.parentElement.remove();
      document.querySelector(".createListMenu").style.display = "flex";
    }
  });
});

// close list create menu
if(document
  .querySelector(".createListMenu .closeFormContainerButton")){
    document
    .querySelector(".createListMenu .closeFormContainerButton")
    .addEventListener("click", () => {
      document.querySelector(".createListMenu").style.display = "none";
    });
  }


// select sources
document.querySelectorAll(".selectContainer ul li").forEach((choice) => {
  choice.addEventListener("click", () => {
    document.querySelector("summary").innerHTML = choice.innerHTML;
    document.querySelector("details").removeAttribute("open");
  });
});

if(document.querySelector("details")){
  document.querySelector("details").addEventListener("click", () => {
    document.onclick = function (e) {
      if (e.target != document.querySelector("summary ul")) {
        document.querySelector("details").removeAttribute("open");
      }
    };
  });
}


// Carousell Container Functionality
// const sliderContent = document.querySelector(".slider-content");
// const contentArray = sliderContent.children;
// var isTouched = false;

// var next = function () {
//   sliderContent.classList.add("next-animation");
//   if (isTouched) {
//     sliderContent.style.transform = "translate3d(-200%, 0px, 0px)";
//     sliderContent.addEventListener("transitionend", nextTouched, false);
//   } else if (!isTouched) {
//     sliderContent.style.transform = "translate3d(-100%, 0px, 0px)";
//     sliderContent.addEventListener("transitionend", afterAnimation, false);
//   }
// };

// var prev = function () {
//   if (isTouched) {
//     var content = Array.from(contentArray);
//     var getSplice = content.splice(contentArray.length - 3);
//     var newArr = getSplice.concat(content);

//     for (let i = 0; i < content.length; i++) {
//       content[i].classList.remove("is-active");
//     }

//     for (let j = 3; j < newArr.length && j < 6; j++) {
//       newArr[j].classList.add("is-active");
//     }

//     for (let len = contentArray.length - 1; len >= 0; --len) {
//       sliderContent.insertBefore(newArr[len], sliderContent.firstChild);
//     }

//     sliderContent.style.transform = "translate3d(-200%, 0px, 0px)";

//     setTimeout(function () {
//       sliderContent.classList.add("next-animation");
//       sliderContent.style.transform = "translate3d(-100%, 0px, 0px)";
//       sliderContent.addEventListener("transitionend", afterAnimation, false);
//     });
//   }
// };

// var afterAnimation = function () {
//   sliderContent.classList.remove("next-animation");

//   if (!isTouched) {
//     var icon = document.createElement("i");
//     icon.classList.add("fa", "fa-chevron-left");
//     document.querySelector(".prev").appendChild(icon);
//     isTouched = true;
//   }

//   sliderContent.removeEventListener("transitionend", afterAnimation);
// };

// var nextTouched = function () {
//   var content = Array.from(contentArray);
//   var getSplice = content.splice(0, 3);
//   var newArr = content.concat(getSplice);

//   for (let i = 0; i < content.length; i++) {
//     content[i].classList.remove("is-active");
//   }

//   for (let i = 3; j < newArr.length && j < 6; j++) {
//     newArr[j].classList.add("is-active");
//   }

//   for (let len = contentArray.length - 1; len >= 0; --len) {
//     sliderContent.insertBefore(newArr[len], sliderContent.firstChild);
//   }

//   sliderContent.classList.remove("next-animation");
//   sliderContent.style.transform = "translate3d(-100%, 0px, 0px)";
//   sliderContent.removeEventListener("transitionend", nextTouched);
// };

// const cookieContainer = document.querySelector(".cookie-container");
// const cookieButton = document.querySelector(".cookie-btn");

// if(cookieButton){
//   cookieButton.addEventListener("click", () => {
//     cookieContainer.classList.remove("active");
//     localStorage.setItem("cookieBannerDisplayed", "true");
//   });
// }


// setTimeout(() => {
//   if (!localStorage.getItem("cookieBannerDisplayed")) {
//     cookieContainer.classList.add("active");
//   }
// }, 2000);
