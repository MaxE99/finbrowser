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
    const website = socialContainer.querySelector("img").className;
    try {
      const res = await fetch(
        `../api/delete_social_link/${website}`,
        get_fetch_settings("DELETE")
      );
      if (!res.ok) {
        showMessage("Error: Link couldn't be deleted!", "Error");
      } else {
        const context = await res.json();
        showMessage(context, "Success");
      }
    } catch (e) {
      showMessage("Error: Network error detected!", "Error");
    }
  }
}

// add websites to profile
const saveButton = document.querySelector(".editSection .saveButton");
saveButton.addEventListener("click", async () => {
  const website =
    saveButton.previousElementSibling.previousElementSibling.previousElementSibling.querySelector(
      "summary span"
    ).innerText;
  const link = saveButton.previousElementSibling.value;
  try {
    const res = await fetch(
      `../api/profile_add_website_link/${website}/${link}`,
      get_fetch_settings("POST")
    );
    if (!res.ok) {
      showMessage("Error: List couldn't be filtered!", "Error");
    } else {
      const context = await res.json();
      showMessage(context, "Success");
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
});

document
  .querySelector(".removeProfilePicButton")
  .addEventListener("click", async () => {
    try {
      const res = await fetch(
        `../api/delete_profile_pic`,
        get_fetch_settings("DELETE")
      );
      if (!res.ok) {
        showMessage("Error: List couldn't be filtered!", "Error");
      } else {
        const context = await res.json();
        showMessage(context, "Success");
      }
    } catch (e) {
      showMessage("Error: Network error detected!", "Error");
    }
  });

document
  .querySelector(".removeProfileBannerButton")
  .addEventListener("click", async () => {
    try {
      const res = await fetch(
        `../api/delete_profile_banner`,
        get_fetch_settings("DELETE")
      );
      if (!res.ok) {
        showMessage("Error: List couldn't be filtered!", "Error");
      } else {
        const context = await res.json();
        showMessage(context, "Success");
      }
    } catch (e) {
      showMessage("Error: Network error detected!", "Error");
    }
  });

const addSocialLinkButton = document.querySelector(".addSocialLinkButton");
addSocialLinkButton.addEventListener("click", async () => {
  const website_link =
    addSocialLinkButton.parentElement.querySelector("input").value;
  const website_img =
    addSocialLinkButton.parentElement.querySelector("summary img").src;
  const websiteName =
    addSocialLinkButton.parentElement.querySelector("summary img").className;
  const existingSocialContainer = document.createElement("div");
  existingSocialContainer.classList.add(
    "existingSocialContainer",
    "newlyAdded"
  );
  const social_img = document.createElement("img");
  social_img.src = website_img;
  social_img.classList.add(websiteName);
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
    const res = await fetch(
      `../api/add_social_links/${websiteName}/"${website_link}"`,
      get_fetch_settings("POST")
    );
    if (!res.ok) {
      showMessage("Error: List couldn't be filtered!", "Error");
    } else {
      const context = await res.json();
      showMessage(context, "Success");
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
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
    const website = socialLink.parentElement.querySelector("img").className;
    const newLink = socialLink.parentElement.querySelector("input").value;
    try {
      const res = await fetch(
        `../api/change_social_link/${website}/"${newLink}"`,
        get_fetch_settings("POST")
      );
      if (!res.ok) {
        showMessage("Error: Link couldn't be changed!", "Error");
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
