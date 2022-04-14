const subscribeButton = document.querySelector(".subscribeButton");

subscribeButton.addEventListener("click", async () => {
  try {
    const url = window.location.href;
    const index = url.lastIndexOf("/");
    const domain = url.substring(index + 1);
    const action = subscribeButton.innerText;
    const res = await fetch(
      `../../home/source_change_subscribtion_status/${domain}/${action}`,
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
        const domain = url.substring(index + 1);
        try {
          const res = await fetch(
            `../../home/rate_source/${domain}/${val_num}`,
            get_fetch_settings("POST")
          );
          if (!res.ok) {
            showMessage("Error: Source can't be subscribed!", "Error");
          } else {
            const context = await res.json();
            showMessage(context, "Success");
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
