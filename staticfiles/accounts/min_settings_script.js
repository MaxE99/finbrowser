function checkSocialLogos() {
  (existingSocialLinks = []),
    document.querySelectorAll(".existingSocialContainer img").forEach((a) => {
      existingSocialLinks.push(a.className);
    }),
    document.querySelectorAll(".addSocialLinksContainer img").forEach((a) => {
      existingSocialLinks.includes(a.className)
        ? (a.parentElement.style.display = "none")
        : (a.parentElement.style.display = "flex");
    });
}
checkSocialLogos();
const categoryTabs = document.querySelectorAll(".settingOption"),
  tabsContent = document.querySelectorAll(".tabsContent");
async function deleteSocialLinks(a) {
  let b = a.target.parentElement;
  if ((b.remove(), !b.classList.contains("newlyAdded"))) {
    let d = a.target.id.replace("social_link_id_", "");
    try {
      let c = await fetch(
        `https://www.finbrowser.io/api/social_links/${d}/`,
        get_fetch_settings("DELETE")
      );
      if (c.ok) {
        let e = await c.json();
        showMessage(e, "Remove");
      } else showMessage("Error: Link couldn't be deleted!", "Error");
    } catch (f) {}
  }
}
categoryTabs.forEach((a) => {
  a.addEventListener("click", () => {
    for (let b = 0, c = categoryTabs.length; b < c; b++)
      categoryTabs[b].classList.remove("activeSettingOption"),
        tabsContent[b].classList.remove("tabsContentActive");
    categoryTabs[a.dataset.forTab].classList.add("activeSettingOption"),
      tabsContent[a.dataset.forTab].classList.add("tabsContentActive");
  });
}),
  document.querySelector("summary").addEventListener("click", checkSocialLogos),
  document.querySelectorAll(".selectContainer ul li").forEach((a) => {
    a.addEventListener("click", () => {
      (document.querySelector("summary").innerHTML = a.innerHTML),
        document.querySelector("details").removeAttribute("open");
    });
  }),
  document
    .querySelector(".removeProfilePicButton")
    .addEventListener("click", async () => {
      let b = document.querySelector(".emailContainer").id;
      try {
        let a = await fetch(
          `https://www.finbrowser.io/api/profiles/${b}/profile_pic_delete/`,
          get_fetch_settings("DELETE")
        );
        if (a.ok) {
          let c = await a.json();
          showMessage(c, "Remove"), window.location.reload();
        } else showMessage("Error: List couldn't be filtered!", "Error");
      } catch (d) {}
    });
const addSocialLinkButton = document.querySelector(".addSocialLinkButton");
addSocialLinkButton.addEventListener("click", async () => {
  let d = addSocialLinkButton.parentElement.querySelector("input").value,
    g = addSocialLinkButton.parentElement.querySelector("summary img").src,
    h = addSocialLinkButton.parentElement
      .querySelector("summary img")
      .id.replace("website_id_", ""),
    b = document.createElement("div");
  b.classList.add("existingSocialContainer", "newlyAdded");
  let e = document.createElement("img");
  e.src = g;
  let c = document.createElement("input");
  (c.type = "text"), (c.value = d);
  let a = document.createElement("button");
  (a.type = "button"),
    a.classList.add("removeSocialLinkButton"),
    (a.innerText = "Remove"),
    a.addEventListener("click", deleteSocialLinks),
    b.append(e, c, a),
    addSocialLinkButton.parentElement.parentElement.insertBefore(
      b,
      addSocialLinkButton.parentElement
    ),
    (document.querySelector(".selectContainer summary").innerHTML =
      '<i class="fa fa-caret-down"></i>'),
    (document.querySelector(".linkInput").value = "");
  try {
    let k = { website: h, url: d },
      f = await fetch("https://www.finbrowser.io/api/social_links/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        mode: "same-origin",
        body: JSON.stringify(k),
      });
    if (f.ok) {
      let l = await f.json();
      showMessage(l, "Success"), window.location.reload();
    } else showMessage("Error: Network request failed unexpectedly!", "Error");
  } catch (m) {}
}),
  document.querySelectorAll(".removeSocialLinkButton").forEach((a) => {
    a.addEventListener("click", deleteSocialLinks);
  });
let socialLinkInitialUrls = [];
const socialLinkInput = document.querySelectorAll(
  ".existingSocialContainer input"
);
for (let i = 0, j = socialLinkInput.length; i < j; i++)
  socialLinkInitialUrls.push(socialLinkInput[i].value),
    socialLinkInput[i].addEventListener("keyup", () => {
      socialLinkInput[i].value != socialLinkInitialUrls[i]
        ? ((socialLinkInput[i].nextElementSibling.style.display = "none"),
          (socialLinkInput[
            i
          ].nextElementSibling.nextElementSibling.style.display = "block"))
        : ((socialLinkInput[i].nextElementSibling.style.display = "block"),
          (socialLinkInput[
            i
          ].nextElementSibling.nextElementSibling.style.display = "none"));
    });
document.querySelectorAll(".saveSocialLinkChanges").forEach((a) => {
  a.addEventListener("click", async () => {
    let c = a.previousElementSibling.id.replace("social_link_id_", ""),
      d = a.parentElement
        .querySelector("img")
        .id.replace("existing_website_id_", ""),
      e = a.parentElement.querySelector("input").value;
    try {
      let f = { website: d, url: e },
        b = await fetch(`https://www.finbrowser.io/api/social_links/${c}/`, {
          method: "PUT",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          mode: "same-origin",
          body: JSON.stringify(f),
        });
      if (b.ok) {
        let g = await b.json();
        showMessage(g, "Success"), window.location.reload();
      } else
        showMessage("Error: Network request failed unexpectedly!", "Error");
    } catch (h) {}
  });
}),
  document.querySelectorAll(".iconContainer .fa-trash").forEach((a) => {
    a.addEventListener("click", async () => {
      try {
        let b = a.id.replace("notification_id_", ""),
          c = await fetch(
            `http://127.0.0.1:8000/api/notifications/${b}/`,
            get_fetch_settings("DELETE")
          );
        c.ok
          ? (a.parentElement.parentElement.remove(),
            showMessage("Notification has been deleted!", "Remove"))
          : showMessage("Error: Network request failed unexpectedly!", "Error");
      } catch (d) {}
    });
  });
