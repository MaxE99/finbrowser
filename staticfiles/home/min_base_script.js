function getCookie(a) {
  let c = null;
  if (document.cookie && "" !== document.cookie) {
    let d = document.cookie.split(";");
    for (let b = 0; b < d.length; b++) {
      let e = d[b].trim();
      if (e.substring(0, a.length + 1) === a + "=") {
        c = decodeURIComponent(e.substring(a.length + 1));
        break;
      }
    }
  }
  return c;
}
function get_fetch_settings(a) {
  let b = {
    method: a,
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    mode: "same-origin",
  };
  return b;
}
function showMessage(d, c) {
  document.querySelectorAll(".messages").forEach((a) => {
    a.innerHTML = "";
  });
  let b = document.createElement("ul");
  b.classList.add("messages");
  let a = document.createElement("li");
  (a.innerText = d),
    "Success" == c
      ? a.classList.add("success")
      : "Remove" == c
      ? a.classList.add("remove")
      : a.classList.add("error"),
    b.appendChild(a),
    document.querySelector(".overlay").appendChild(b);
}
document
  .querySelector(".headerContainer .fa-bars")
  .addEventListener("click", () => {
    let a = document.querySelector(".horizontalNavigation");
    "ON" == a.value
      ? ((a.style.maxHeight = "0"), (a.value = "OFF"))
      : ((a.style.maxHeight = "100rem"), (a.value = "ON"));
  }),
  document.querySelectorAll("input").forEach((a) => {
    a.setAttribute("autocomplete", "off");
  }),
  document
    .getElementById("mainAutocomplete")
    .addEventListener("keyup", async function (i) {
      let c = document.getElementById("mainAutocomplete").value;
      if ("Enter" == i.key && "" != c.replaceAll(/\s/g, ""))
        window.location.href = `https://www.finbrowser.io/search_results/${c}`;
      else {
        let b = document.getElementById("mainAutocomplete_result");
        if (c && "" != c.replaceAll(/\s/g, "")) {
          try {
            let g = await fetch(
              `https://www.finbrowser.io/api/search_site/${c}`,
              get_fetch_settings("GET")
            );
            if (g.ok) {
              document.querySelector(".mainInputSearch").style.borderRadius =
                "0.8rem 0.8rem 0 0";
              let a = await g.json();
              if (
                ((b.style.display = "flex"),
                (b.innerHTML = ""),
                a[0].length > 0)
              ) {
                b.innerHTML += '<div class="searchResultHeader">Lists</div>';
                for (let e = 0, j = a[0].length; e < j; e++) {
                  let f = a[0][e],
                    k = a[4][e],
                    h;
                  h = f.list_pic
                    ? f.list_pic
                    : "/static/home/media/finbrowser-bigger-logoger-logo.png";
                  let l = `<div class="searchResult"><img src="${h}"><span>${f.name}</span><a href="${k}"></a></div>`;
                  b.innerHTML += l;
                }
              }
              if (
                (a[1].length > 0 &&
                  ((b.innerHTML +=
                    '<div class="searchResultHeader">Sources</div>'),
                  a[1].forEach((a) => {
                    let c = `<div class="searchResult"><img src="/static/${a.favicon_path}"><span>${a.name}</span><a href="../../source/profile/${a.slug}"></a></div>`;
                    b.innerHTML += c;
                  })),
                a[2].length > 0)
              ) {
                b.innerHTML += '<div class="searchResultHeader">Articles</div>';
                for (let d = 0, m = a[2].length; d < m; d++) {
                  let n = a[3][d],
                    o = a[2][d].title,
                    p = a[2][d].link,
                    q = `<div class="searchResult"><img src="/static/${n}"><span>${o}</span><a href="${p}"></a></div>`;
                  b.innerHTML += q;
                }
              }
            } else
              showMessage(
                "Error: Network request failed unexpectedly!",
                "Error"
              );
          } catch (r) {}
          document.onclick = function (a) {
            "autocomplete_list_results" !== a.target.id &&
              ((b.style.display = "none"),
              (document.querySelector(".mainInputSearch").style.borderRadius =
                "0.8rem"));
          };
        } else
          (b.style.display = "none"),
            (document.querySelector(".mainInputSearch").style.borderRadius =
              "0.8rem");
      }
    }),
  document
    .querySelector(".mainSearchContainer i")
    .addEventListener("click", () => {
      "" !=
        (search_term =
          document.querySelector(".mainInputSearch").value).replaceAll(
          /\s/g,
          ""
        ) &&
        (window.location.href = `https://www.finbrowser.io/search_results/${search_term}`);
    });
const dropdownButton = document.querySelector(".fa-sort-down");
function checkForOpenContainers() {
  let c = !0,
    b = document.querySelectorAll(".addToListForm");
  for (let a = 0, d = b.length; a < d; a++)
    if ("none" != b[a].style.display && b[a].style.display) {
      c = !1;
      break;
    }
  return c;
}
dropdownButton &&
  dropdownButton.addEventListener("click", () => {
    let a = document.querySelector(".profileMenu");
    "flex" == a.style.display
      ? (a.style.display = "none")
      : (a.style.display = "flex");
  });
let previousOptionsContainer, previousEllipsis;
function get_initial_list_statuses(e) {
  let c = [],
    d = [],
    b = e.parentElement.nextElementSibling.querySelectorAll(
      ".listContainer input"
    );
  for (let a = 0, f = b.length; a < f; a++)
    c.push(b[a].checked), d.push(b[a].id.replace("list_id_", ""));
  return [c, d];
}
function check_new_list_status(a) {
  let b = [];
  return (
    a.parentElement.previousElementSibling
      .querySelectorAll("input")
      .forEach((a) => {
        b.push(a.checked);
      }),
    b
  );
}
async function add_article_to_list(a, b) {
  try {
    let c = await fetch(
      `https://www.finbrowser.io/api/lists/${a}/add_article_to_list/${b}/`,
      get_fetch_settings("POST")
    );
    c.ok || showMessage("Error: Network request failed unexpectedly!", "Error");
  } catch (d) {}
}
async function remove_article_from_list(a, b) {
  try {
    let c = await fetch(
      `https://www.finbrowser.io/api/lists/${a}/delete_article_from_list/${b}/`,
      get_fetch_settings("DELETE")
    );
    c.ok || showMessage("Error: Network request failed unexpectedly!", "Error");
  } catch (d) {}
}
function check_device_width_below(a) {
  let b =
    window.innerWidth ||
    document.documentElement.clientWidth ||
    document.body.clientWidth;
  return b < a;
}
document.querySelectorAll(".fa-ellipsis-h").forEach((a) => {
  a.addEventListener("click", function (c) {
    let d = checkForOpenContainers();
    if (d) {
      previousOptionsContainer &&
        c.target !== previousEllipsis &&
        (previousOptionsContainer.style.display = "none");
      let b = a.parentElement.querySelector(".articleOptionsContainer");
      "flex" != b.style.display
        ? ((b.style.display = "flex"),
          (document.onclick = function (b) {
            b.target !== a &&
              (a.parentElement.querySelector(
                ".articleOptionsContainer"
              ).style.display = "none");
          }))
        : (b.style.display = "none"),
        (previousOptionsContainer = a.parentElement.querySelector(
          ".articleOptionsContainer"
        )),
        (previousEllipsis = a);
    }
  });
}),
  document.querySelectorAll(".addToHighlightedButton").forEach((a) => {
    a.addEventListener("click", async () => {
      if (!a.classList.contains("registrationLink")) {
        let e = a.closest(".articleContainer").id.replace("article_id_", ""),
          f = a.lastElementChild.innerText,
          b;
        b = "Highlight article" == f ? "highlight" : "unhighlight";
        try {
          let g = { article_id: e },
            c = await fetch(
              "https://www.finbrowser.io/api/highlighted_articles/",
              {
                method: "POST",
                headers: {
                  "X-CSRFToken": getCookie("csrftoken"),
                  Accept: "application/json",
                  "Content-Type": "application/json",
                },
                mode: "same-origin",
                body: JSON.stringify(g),
              }
            );
          if (c.ok) {
            let d = await c.json();
            "highlight" == b
              ? (showMessage(d, "Success"),
                (a.innerHTML =
                  '<i class="fas fa-times"></i><span>Unhighlight article</span>'))
              : (showMessage(d, "Remove"),
                (a.innerHTML =
                  '<i class="fas fa-highlighter"></i><span>Highlight article</span>'));
          } else
            showMessage("Error: Network request failed unexpectedly!", "Error");
        } catch (h) {}
      }
    });
  }),
  document.querySelectorAll(".addToListButton").forEach((a) => {
    a.addEventListener("click", () => {
      if (!a.classList.contains("registrationLink")) {
        let c = checkForOpenContainers();
        c && (a.parentElement.nextElementSibling.style.display = "block");
        let d = get_initial_list_statuses(a),
          f = d[0],
          b = a.parentElement.parentElement.querySelector(".addToListForm");
        if (b.querySelector(".saveButton")) {
          let e = b.querySelector(".saveButton");
          e.addEventListener("click", () => {
            let c = d[1],
              g = e.closest(".articleContainer").id.replace("article_id_", ""),
              h = check_new_list_status(e);
            for (let a = 0, i = h.length; a < i; a++)
              h[a] != f[a] &&
                (!1 == f[a]
                  ? add_article_to_list(c[a], g)
                  : remove_article_from_list(c[a], g));
            showMessage("Lists have been updated!", "Success"),
              (b.style.display = "none");
          });
        }
      }
    });
  }),
  document.querySelectorAll(".addToListForm .fa-times").forEach((a) => {
    a.addEventListener("click", () => {
      a.parentElement.parentElement.style.display = "none";
    });
  }),
  document.querySelectorAll(".createNewListButton").forEach((a) => {
    a.addEventListener("click", () => {
      a.classList.contains("registrationLink") ||
        ((a.parentElement.parentElement.parentElement.querySelector(
          ".addToListForm"
        ).style.display = "none"),
        check_device_width_below(500)
          ? (document.querySelector(".smartphoneCreateListMenu").style.display =
              "flex")
          : (a.parentElement.parentElement.parentElement.querySelector(
              ".createListMenu"
            ).style.display = "flex"));
    });
  }),
  document
    .querySelectorAll(".createListMenu .closeFormContainerButton")
    .forEach((a) => {
      a.addEventListener("click", () => {
        document.querySelectorAll(".createListMenu").forEach((a) => {
          a.style.display = "none";
        });
      });
    }),
  document.querySelector(".userSpace .notificationBell") &&
    document
      .querySelector(".userSpace .notificationBell")
      .addEventListener("click", async () => {
        let a = document.querySelector(".userSpace .notificationContainer");
        if ("block" == a.style.display)
          (a.style.display = "none"),
            document.querySelector(".unseenNotifications").remove(),
            document.querySelectorAll(".unseenNotification").forEach((a) => {
              a.classList.remove("unseenNotification");
            });
        else {
          a.style.display = "block";
          try {
            let b = await fetch(
              "https://www.finbrowser.io/api/notifications/",
              get_fetch_settings("PUT")
            );
            b.ok ||
              showMessage(
                "Error: Network request failed unexpectedly!",
                "Error"
              );
          } catch (c) {}
        }
      }),
  document
    .querySelectorAll(".notificationHeadersContainer div")
    .forEach((a) => {
      a.addEventListener("click", () => {
        document
          .querySelectorAll(".notificationHeadersContainer div")
          .forEach((a) => {
            a.classList.contains("activeNotificationCategory")
              ? a.classList.remove("activeNotificationCategory")
              : a.classList.add("activeNotificationCategory");
          }),
          document.querySelectorAll(".notificationsContainer").forEach((a) => {
            a.classList.contains("activeNotificationContainer")
              ? a.classList.remove("activeNotificationContainer")
              : a.classList.add("activeNotificationContainer");
          });
      });
    }),
  document.addEventListener("click", (a) => {
    let b;
    null !=
      (b = a.target.matches(".handle")
        ? a.target
        : a.target.closest(".handle")) && onHandleClick(b);
  });
const throttleProgressBar = throttle(() => {
  document.querySelectorAll(".progressBar").forEach(calculateProgressBar);
}, 250);
function calculateProgressBar(c) {
  c.innerHTML = "";
  let a = c.closest(".sliderWrapper").querySelector(".slider"),
    g = a.children.length,
    h = parseInt(getComputedStyle(a).getPropertyValue("--items-per-screen")),
    d = parseInt(getComputedStyle(a).getPropertyValue("--slider-index")),
    b = Math.ceil(g / h);
  d >= b && (a.style.setProperty("--slider-index", b - 1), (d = b - 1));
  for (let e = 0; e < b; e++) {
    let f = document.createElement("div");
    f.classList.add("progressItem"),
      e === d && f.classList.add("active"),
      c.append(f);
  }
}
function onHandleClick(d) {
  let b = d.closest(".sliderWrapper").querySelector(".progressBar"),
    c = d.closest(".sliderContentContainer").querySelector(".slider"),
    a = parseInt(getComputedStyle(c).getPropertyValue("--slider-index")),
    e = b.children.length;
  d.classList.contains("leftHandle") &&
    (a - 1 < 0
      ? (c.style.setProperty("--slider-index", e - 1),
        b.children[a].classList.remove("active"),
        b.children[e - 1].classList.add("active"))
      : (c.style.setProperty("--slider-index", a - 1),
        b.children[a].classList.remove("active"),
        b.children[a - 1].classList.add("active"))),
    d.classList.contains("rightHandle") &&
      (a + 1 >= e
        ? (c.style.setProperty("--slider-index", 0),
          b.children[a].classList.remove("active"),
          b.children[0].classList.add("active"))
        : (c.style.setProperty("--slider-index", a + 1),
          b.children[a].classList.remove("active"),
          b.children[a + 1].classList.add("active")));
}
function throttle(a, b = 1e3) {
  let c = !1,
    d,
    e = () => {
      null == d ? (c = !1) : (a(...d), (d = null), setTimeout(e, b));
    };
  return (...f) => {
    if (c) {
      d = f;
      return;
    }
    a(...f), (c = !0), setTimeout(e, b);
  };
}
window.addEventListener("resize", throttleProgressBar),
  document.querySelectorAll(".progressBar").forEach(calculateProgressBar);
