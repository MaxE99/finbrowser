const subscribeButton = document.querySelector(".subscribeButton");
subscribeButton.addEventListener("click", async () => {
  if (!subscribeButton.classList.contains("registrationLink"))
    try {
      let c = document
          .querySelector(".upperInnerContainer h3")
          .id.replace("source_id_", ""),
        d = subscribeButton.innerText,
        a = await fetch(
          `https://www.finbrowser.io/api/sources/${c}/source_change_subscribtion_status/`,
          get_fetch_settings("POST")
        );
      if (a.ok) {
        let b = await a.json();
        "Subscribe" == d
          ? (subscribeButton.classList.replace("unsubscribed", "subscribed"),
            (subscribeButton.innerText = "Subscribed"),
            showMessage(b, "Success"))
          : (subscribeButton.classList.replace("subscribed", "unsubscribed"),
            (subscribeButton.innerText = "Subscribe"),
            showMessage(b, "Remove"));
      } else
        showMessage("Error: Network request failed unexpectedly!", "Error");
    } catch (e) {}
});
const one = document.getElementById("first"),
  two = document.getElementById("second"),
  three = document.getElementById("third"),
  four = document.getElementById("fourth"),
  five = document.getElementById("fifth"),
  confirmBox = document.getElementById("confirm-box"),
  handleStarSelect = (c, d) => {
    let b = d.children;
    for (let a = 0; a < b.length; a++)
      a < c ? b[a].classList.add("checked") : b[a].classList.remove("checked");
  },
  handleSelect = (b) => {
    let a = document.querySelector(".rate-form");
    switch (b) {
      case "first":
        handleStarSelect(1, a);
        return;
      case "second":
        handleStarSelect(2, a);
        return;
      case "third":
        handleStarSelect(3, a);
        return;
      case "fourth":
        handleStarSelect(4, a);
        return;
      case "fifth":
        handleStarSelect(5, a);
        return;
      default:
        handleStarSelect(0, a);
    }
  },
  getNumericValue = (a) =>
    "first" === a
      ? 1
      : "second" === a
      ? 2
      : "third" === a
      ? 3
      : "fourth" === a
      ? 4
      : "fifth" === a
      ? 5
      : 0;
if (one) {
  let a = [one, two, three, four, five];
  a.forEach((a) =>
    a.addEventListener("mouseover", (a) => {
      handleSelect(a.target.id);
    })
  );
}
if (
  (document.querySelectorAll(".rankingStar").forEach((a) => {
    a.addEventListener("click", async (b) => {
      let c = b.target.id,
        d = getNumericValue(c),
        e = document
          .querySelector(".upperInnerContainer h3")
          .id.replace("source_id_", "");
      try {
        let f = { source_id: e, rating: d },
          a = await fetch("https://www.finbrowser.io/api/source_ratings/", {
            method: "POST",
            headers: {
              "X-CSRFToken": getCookie("csrftoken"),
              Accept: "application/json",
              "Content-Type": "application/json",
            },
            mode: "same-origin",
            body: JSON.stringify(f),
          });
        if (a.ok) {
          let g = await a.json();
          showMessage(g, "Success"), window.location.reload();
        } else
          showMessage("Error: Network request failed unexpectedly!", "Error");
      } catch (h) {}
    });
  }),
  document.querySelector(".avgRating span"))
) {
  let b = Math.round(document.querySelector(".avgRating span").innerText);
  handleStarSelect(b, document.querySelector(".ratedContainer"));
}
document.querySelector(".openRateListButton").addEventListener("click", () => {
  (document.querySelector(".rate-formUpperContainer").style.display = "block"),
    (document.querySelector(".rating").style.opacity = "0"),
    (document.querySelector(".ratingsAmmountContainer").style.opacity = "0"),
    (document.querySelector(".rateListButton").style.opacity = "0"),
    (document.querySelector(".rankingsHeader").style.opacity = "0");
});
const notificationButton = document.querySelector(
  ".notificationAndSubscribtionContainer .fa-bell"
);
notificationButton &&
  notificationButton.addEventListener("click", async () => {
    try {
      let c = document
          .querySelector(".upperInnerContainer h3")
          .id.replace("source_id_", ""),
        d = { source_id: c },
        a = await fetch("https://www.finbrowser.io/api/notifications/", {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          mode: "same-origin",
          body: JSON.stringify(d),
        });
      if (a.ok) {
        let b = await a.json();
        notificationButton.classList.contains("notificationActivated")
          ? (notificationButton.classList.remove("notificationActivated"),
            showMessage(b, "Remove"))
          : (notificationButton.classList.add("notificationActivated"),
            showMessage(b, "Success"));
      } else
        showMessage("Error: Network request failed unexpectedly!", "Error");
    } catch (e) {}
  }),
  document
    .querySelector(".addSourceToListButton")
    .addEventListener("click", () => {
      document.querySelector(".addSourceToListForm").style.display = "block";
    }),
  document
    .querySelector(".addSourceToListForm .fa-times")
    .addEventListener("click", () => {
      document.querySelector(".addSourceToListForm").style.display = "none";
    }),
  document.querySelectorAll(".addSourceToListForm .saveButton").forEach((a) => {
    a.addEventListener("click", async () => {
      let g = document
          .querySelector(".upperInnerContainer .sourceName")
          .id.replace("source_id_", ""),
        h = [],
        d = [],
        e = [],
        f = a.parentElement.parentElement.querySelectorAll(
          ".listContainer input"
        );
      for (let c = 0, k = f.length; c < k; c++)
        d.push(f[c].className), e.push(f[c].id.replace("id_list_", ""));
      a.parentElement.previousElementSibling
        .querySelectorAll("input")
        .forEach((a) => {
          a.checked ? h.push("sourceInList") : h.push("sourceNotInList");
        });
      for (let b = 0, l = h.length; b < l; b++)
        if (h[b] != d[b]) {
          if ("sourceNotInList" == d[b]) {
            let m = e[b];
            try {
              let i = await fetch(
                `https://www.finbrowser.io/api/lists/${m}/add_source/${g}/`,
                get_fetch_settings("POST")
              );
              if (i.ok) {
                let n = await i.json();
                showMessage(n, "Success"), window.location.reload();
              } else
                showMessage(
                  "Error: Network request failed unexpectedly!",
                  "Error"
                );
            } catch (q) {}
          } else
            try {
              let o = e[b],
                j = await fetch(
                  `https://www.finbrowser.io/api/lists/${o}/delete_source_from_list/${g}/`,
                  get_fetch_settings("DELETE")
                );
              if (j.ok) {
                let p = await j.json();
                showMessage(p, "Success"), window.location.reload();
              } else
                showMessage(
                  "Error: Network request failed unexpectedly!",
                  "Error"
                );
            } catch (r) {}
        }
    });
  });
