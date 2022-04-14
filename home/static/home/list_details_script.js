// async function get_sources() {
//   try {
//     const res = await fetch(
//       `../list_change_subscribtion_status/${list_id}/${action}`,
//       get_fetch_settings("POST")
//     );
//     if (!res.ok) {
//       showMessage("Error: List can't be subscribed!", "Error");
//     } else {
//       const context = await res.json();
//       showMessage(context, "Success");
//       if (action == "Subscribe") {
//         subscribeButton.classList.replace("unsubscribed", "subscribed");
//         subscribeButton.innerText = "Unsubscribe";
//       } else {
//         subscribeButton.classList.replace("subscribed", "unsubscribed");
//         subscribeButton.innerText = "Subscribe";
//       }
//     }
//   } catch (e) {
//     showMessage("Error: Network error detected!", "Error");
//   }
// }

const subscribeButton = document.querySelector(".subscribeButton");

if (subscribeButton) {
  subscribeButton.addEventListener("click", async () => {
    try {
      const url = window.location.href;
      const index = url.lastIndexOf("/");
      const list_id = url.substring(index + 1);
      const action = subscribeButton.innerText;
      const res = await fetch(
        `../list_change_subscribtion_status/${list_id}/${action}`,
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

if (editButton) {
  editButton.addEventListener("click", () => {
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
            const source =
              trashButton.nextElementSibling.nextElementSibling.children[0]
                .innerText;
            const res = await fetch(
              `../delete_source_from_list/${listName}/${source}`,
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
  });
}

document
  .querySelector(".deleteListButton")
  .addEventListener("click", async () => {
    try {
      const url = window.location.href;
      const index = url.lastIndexOf("/");
      const list_id = url.substring(index + 1);
      const res = await fetch(
        `../delete_list/${list_id}`,
        get_fetch_settings("DELETE")
      );
      if (!res.ok) {
        showMessage("Error: List can't be deleted!", "Error");
      } else {
        const context = await res.json();
        showMessage(context, "Success");
      }
    } catch (e) {
      showMessage("Error: Network error detected!", "Error");
    }
  });

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
          `../../home/search_sources/${list_id}/${search_term}`,
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
document.querySelector(".addSourcesButton").addEventListener("click", () => {
  document.querySelector(".addSourcesForm").style.display = "flex";
  document.querySelector(".listOverlay").style.opacity = "0.5";
});

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
          `../add_sources/${selected_sources}/${list_id}`,
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

// get all the stars
const one = document.getElementById("first");
const two = document.getElementById("second");
const three = document.getElementById("third");
const four = document.getElementById("fourth");
const five = document.getElementById("fifth");

// get the form, confirm-box and csrf token
const form = document.querySelector(".rate-form");
const confirmBox = document.getElementById("confirm-box");
const csrf = document.getElementsByName("csrfmiddlewaretoken");

const handleStarSelect = (size) => {
  const children = form.children;
  for (let i = 0; i < children.length; i++) {
    if (i <= size) {
      children[i].classList.add("checked");
    } else {
      children[i].classList.remove("checked");
    }
  }
};

const handleSelect = (selection) => {
  switch (selection) {
    case "first": {
      handleStarSelect(1);
      return;
    }
    case "second": {
      handleStarSelect(2);
      return;
    }
    case "third": {
      handleStarSelect(3);
      return;
    }
    case "fourth": {
      handleStarSelect(4);
      return;
    }
    case "fifth": {
      handleStarSelect(5);
      return;
    }
    default: {
      handleStarSelect(0);
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

  arr.forEach((item) =>
    item.addEventListener("click", (event) => {
      // value of the rating not numeric
      const val = event.target.id;

      let isSubmit = false;
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (isSubmit) {
          return;
        }
        isSubmit = true;
        // picture id
        const id = e.target.id;
        // value of the rating translated into numeric
        const val_num = getNumericValue(val);
        const url = window.location.href;
        const index = url.lastIndexOf("/");
        const list_id = url.substring(index + 1);
        try {
          const res = await fetch(
            `../../home/list_source/${list_id}/${val_num}`,
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
    })
  );
}

// if user already rated source = set stars to this rating
const user_rating = document.getElementById("user-rating").innerText;
handleStarSelect(user_rating);
