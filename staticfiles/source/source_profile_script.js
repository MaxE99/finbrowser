const subscribeButtons = document.querySelectorAll(".subscribeButton");

subscribeButtons.forEach((subscribeButton) => {
  subscribeButton.addEventListener("click", async () => {
    if (!subscribeButton.classList.contains("registrationLink")) {
      try {
        const source_id = subscribeButton
          .closest(".upperContainer")
          .querySelector(".upperInnerContainer h3")
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
});

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
    const source_id = document
      .querySelector(".upperInnerContainer h3")
      .id.split("#")[1];
    try {
      const data = { source_id: source_id, rating: rating };
      const res = await fetch(`../../api/source_ratings/`, {
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
document.querySelectorAll(".openRateListButton").forEach((rateListButton) => {
  rateListButton.addEventListener("click", () => {
    const upperContainer = rateListButton.closest(".upperContainer");
    upperContainer.querySelector(".rate-formUpperContainer").style.display =
      "block";
    upperContainer.querySelector(".rating").style.opacity = "0";
    upperContainer.querySelector(".ratingsAmmountContainer").style.opacity =
      "0";
    upperContainer.querySelector(".rateListButton").style.opacity = "0";
    upperContainer.querySelector(".rankingsHeader").style.opacity = "0";
  });
});

//Notifications
const notificationButtons = document.querySelectorAll(
  ".notificationAndSubscribtionContainer .notificationButton"
);
notificationButtons.forEach((notificationButton) => {
  if (notificationButton) {
    notificationButton.addEventListener("click", async () => {
      try {
        const source_id = notificationButton
          .closest(".upperContainer")
          .querySelector(".upperInnerContainer h3")
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
          if (notificationButton.classList.contains("notificationActivated")) {
            notificationButton.classList.remove("notificationActivated");
            notificationButton.classList.replace("fa-bell-slash", "fa-bell");
            showMessage(context, "Remove");
          } else {
            notificationButton.classList.add("notificationActivated");
            notificationButton.classList.replace("fa-bell", "fa-bell-slash");
            showMessage(context, "Success");
          }
        }
      } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
    });
  }
});

//open add list to sources form
document
  .querySelectorAll(".addSourceToListButton")
  .forEach((addSourceButton) => {
    addSourceButton.addEventListener("click", () => {
      addSourceButton
        .closest(".upperContainer")
        .querySelector(".addSourceToListForm").style.display = "block";
    });
  });

//close add list sources form

document
  .querySelectorAll(".addSourceToListForm .fa-times")
  .forEach((closeAddSourceFormButton) => {
    closeAddSourceFormButton.addEventListener("click", () => {
      document.querySelector(".addSourceToListForm").style.display = "none";
    });
  });

// add sources to lists

function check_list_status(saveButton) {
  let add_list_ids = [];
  let remove_list_ids = [];
  const input_list = saveButton
    .closest(".addSourceToListForm")
    .querySelectorAll(".listContainer input");
  for (let i = 0, j = input_list.length; i < j; i++) {
    if (
      input_list[i].className === "sourceInList" &&
      input_list[i].checked === false
    ) {
      remove_list_ids.push(input_list[i].id.split("id_list_")[1]);
    } else if (
      input_list[i].className === "sourceNotInList" &&
      input_list[i].checked
    ) {
      add_list_ids.push(input_list[i].id.split("id_list_")[1]);
    }
  }
  return [add_list_ids, remove_list_ids];
}

document
  .querySelectorAll(".addSourceToListForm .saveButton")
  .forEach((saveButton) => {
    saveButton.addEventListener("click", async () => {
      let source_id = saveButton
        .closest(".upperContainer")
        .querySelector(".upperInnerContainer .sourceName")
        .id.split("#")[1];
      const [add_lists, remove_lists] = check_list_status(saveButton);
      body = {
        source_id: source_id,
        add_lists: add_lists,
        remove_lists: remove_lists,
      };
      try {
        const res = await fetch(
          `../../api/lists/change_source_status_from_lists/`,
          {
            method: "POST",
            headers: {
              "X-CSRFToken": getCookie("csrftoken"),
              Accept: "application/json",
              "Content-Type": "application/json",
            },
            mode: "same-origin",
            body: JSON.stringify(body),
          }
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
    });
  });
