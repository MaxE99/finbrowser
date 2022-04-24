const subscribeButton = document.querySelector(".subscribeButton");

subscribeButton.addEventListener("click", async () => {
  try {
    const url = window.location.href;
    const index = url.lastIndexOf("/");
    const domain = url.substring(index + 1);
    const action = subscribeButton.innerText;
    const res = await fetch(
      `../../api/source_change_subscribtion_status/${domain}/${action}`,
      get_fetch_settings("POST")
    );
    if (!res.ok) {
      showMessage("Error: Source can't be subscribed!", "Error");
    } else {
      const context = await res.json();
      showMessage(context, "Success");
      if (action == "Subscribe") {
        subscribeButton.classList.replace("unsubscribed", "subscribed");
        subscribeButton.innerText = "Subscribed";
      } else {
        subscribeButton.classList.replace("subscribed", "unsubscribed");
        subscribeButton.innerText = "Subscribe";
      }
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
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
    const val_num = getNumericValue(id);
    const url = window.location.href;
    const index = url.lastIndexOf("/");
    const list_id = url.substring(index + 1);
    try {
      const res = await fetch(
        `../../api/rate_source/${list_id}/${val_num}`,
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

//Notifications
const notificationButton = document.querySelector(
  ".notificationAndSubscribtionContainer .fa-bell"
);
if (notificationButton) {
  notificationButton.addEventListener("click", async () => {
    try {
      const source_id = document
        .querySelector("h3")
        .id.replace("source_id_", "");
      const res = await fetch(
        `../../api/change_source_notification/${source_id}`,
        get_fetch_settings("POST")
      );
      if (!res.ok) {
        showMessage("Error: Source can't be subscribed!", "Error");
      } else {
        const context = await res.json();
        showMessage(context, "Success");
        if (notificationButton.classList.contains("notificationActivated")) {
          notificationButton.classList.remove("notificationActivated");
        } else {
          notificationButton.classList.add("notificationActivated");
        }
      }
    } catch (e) {
      showMessage("Error: Network error detected!", "Error");
    }
  });
}
