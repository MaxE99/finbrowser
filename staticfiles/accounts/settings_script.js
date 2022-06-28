// show only logos that are not already selected
function checkSocialLogos() {
  existingSocialLinks = [];
  document.querySelectorAll(".existingSocialContainer img").forEach((image) => {
    existingSocialLinks.push(image.className);
  });
  document.querySelectorAll(".addSocialLinksContainer img").forEach((image) => {
    if (existingSocialLinks.includes(image.className)) {
      image.parentElement.style.display = "none";
    } else {
      image.parentElement.style.display = "flex";
    }
  });
}

checkSocialLogos();

//change tabs
const categoryTabs = document.querySelectorAll(".settingOption");
const tabsContent = document.querySelectorAll(".tabsContent");
categoryTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    for (let i = 0, j = categoryTabs.length; i < j; i++) {
      categoryTabs[i].classList.remove("activeSettingOption");
      tabsContent[i].classList.remove("tabsContentActive");
    }
    categoryTabs[tab.dataset.forTab].classList.add("activeSettingOption");
    tabsContent[tab.dataset.forTab].classList.add("tabsContentActive");
  });
});

// refresh logos when clicking summary
document.querySelector("summary").addEventListener("click", checkSocialLogos);

// select websites in form
document.querySelectorAll(".selectContainer ul li").forEach((choice) => {
  choice.addEventListener("click", () => {
    document.querySelector("summary").innerHTML = choice.innerHTML;
    // document.querySelector("summary").innerText = choice.lastChild.innerText;
    document.querySelector("details").removeAttribute("open");
  });
});

//delete Social Links in Account Form
async function deleteSocialLinks(e) {
  const socialContainer = e.target.parentElement;
  socialContainer.remove();
  if (!socialContainer.classList.contains("newlyAdded")) {
    const social_link_id = e.target.id.replace("social_link_id_", "");
    try {
      const res = await fetch(
        `https://finbrowser.io/api/social_links/${social_link_id}/`,
        get_fetch_settings("DELETE")
      );
      if (!res.ok) {
        showMessage("Error: Link couldn't be deleted!", "Error");
      } else {
        const context = await res.json();
        showMessage(context, "Remove");
      }
    } catch (e) {
      // showMessage("Error: Unexpected error has occurred!", "Error");
    }
  }
}

document
  .querySelector(".removeProfilePicButton")
  .addEventListener("click", async () => {
    const user = document.querySelector(".emailContainer").id;
    try {
      const res = await fetch(
        `https://finbrowser.io/api/profiles/${user}/profile_pic_delete/`,
        get_fetch_settings("DELETE")
      );
      if (!res.ok) {
        showMessage("Error: List couldn't be filtered!", "Error");
      } else {
        const context = await res.json();
        showMessage(context, "Remove");
        window.location.reload();
      }
    } catch (e) {
      // showMessage("Error: Unexpected error has occurred!", "Error");
    }
  });

const addSocialLinkButton = document.querySelector(".addSocialLinkButton");
addSocialLinkButton.addEventListener("click", async () => {
  const website_link =
    addSocialLinkButton.parentElement.querySelector("input").value;
  const website_img =
    addSocialLinkButton.parentElement.querySelector("summary img").src;
  const websiteID = addSocialLinkButton.parentElement
    .querySelector("summary img")
    .id.replace("website_id_", "");
  const existingSocialContainer = document.createElement("div");
  existingSocialContainer.classList.add(
    "existingSocialContainer",
    "newlyAdded"
  );
  const social_img = document.createElement("img");
  social_img.src = website_img;
  const social_input = document.createElement("input");
  social_input.type = "text";
  social_input.value = website_link;
  const delete_button = document.createElement("button");
  delete_button.type = "button";
  delete_button.classList.add("removeSocialLinkButton");
  delete_button.innerText = "Remove";
  delete_button.addEventListener("click", deleteSocialLinks);
  existingSocialContainer.append(social_img, social_input, delete_button);
  addSocialLinkButton.parentElement.parentElement.insertBefore(
    existingSocialContainer,
    addSocialLinkButton.parentElement
  );
  document.querySelector(
    ".selectContainer summary"
  ).innerHTML = `<i class="fa fa-caret-down"></i>`;
  document.querySelector(".linkInput").value = "";
  try {
    const data = { website: websiteID, url: website_link };
    const res = await fetch(`https://finbrowser.io/api/social_links/`, {
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

// eventListener on all socialLink remove Buttons
document.querySelectorAll(".removeSocialLinkButton").forEach((button) => {
  button.addEventListener("click", deleteSocialLinks);
});

let socialLinkInitialUrls = [];

const socialLinkInput = document.querySelectorAll(
  ".existingSocialContainer input"
);

for (let i = 0, j = socialLinkInput.length; i < j; i++) {
  socialLinkInitialUrls.push(socialLinkInput[i].value);
  socialLinkInput[i].addEventListener("keyup", () => {
    if (socialLinkInput[i].value != socialLinkInitialUrls[i]) {
      socialLinkInput[i].nextElementSibling.style.display = "none";
      socialLinkInput[i].nextElementSibling.nextElementSibling.style.display =
        "block";
    } else {
      socialLinkInput[i].nextElementSibling.style.display = "block";
      socialLinkInput[i].nextElementSibling.nextElementSibling.style.display =
        "none";
    }
  });
}

document.querySelectorAll(".saveSocialLinkChanges").forEach((socialLink) => {
  socialLink.addEventListener("click", async () => {
    const social_link_id = socialLink.previousElementSibling.id.replace(
      "social_link_id_",
      ""
    );
    const websiteID = socialLink.parentElement
      .querySelector("img")
      .id.replace("existing_website_id_", "");
    const website_link = socialLink.parentElement.querySelector("input").value;
    try {
      const data = { website: websiteID, url: website_link };
      const res = await fetch(
        `https://finbrowser.io/api/social_links/${social_link_id}/`,
        {
          method: "PUT",
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
        showMessage(context, "Success");
        window.location.reload();
      }
    } catch (e) {
      // showMessage("Error: Unexpected error has occurred!", "Error");
    }
  });
});

document
  .querySelectorAll(".iconContainer .fa-trash")
  .forEach((deleteButton) => {
    deleteButton.addEventListener("click", async () => {
      try {
        const notifications_id = deleteButton.id.replace(
          "notification_id_",
          ""
        );
        const res = await fetch(
          `http://127.0.0.1:8000/api/notifications/${notifications_id}/`,
          get_fetch_settings("DELETE")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!", "Error");
        } else {
          deleteButton.parentElement.parentElement.remove();
          showMessage("Notification has been deleted!", "Remove");
        }
      } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
    });
  });
