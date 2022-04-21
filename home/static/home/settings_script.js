//change tabs
const categoryTabs = document.querySelectorAll(".settingOption");
const tabsContent = document.querySelectorAll(".tabsContent");
categoryTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    console.log(tab);
    for (let i = 0, j = categoryTabs.length; i < j; i++) {
      categoryTabs[i].classList.remove("activeSettingOption");
      tabsContent[i].classList.remove("tabsContentActive");
    }
    categoryTabs[tab.dataset.forTab].classList.add("activeSettingOption");
    tabsContent[tab.dataset.forTab].classList.add("tabsContentActive");
  });
});

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
    const website = socialContainer.querySelector("img").id;
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

//look for added social links when saving and if new links exist add them to database
// document
//   .querySelector(".changeProfileForm .saveButton")
//   .addEventListener("click", async () => {
//     const newlyAdded = document.querySelectorAll(".newlyAdded");
//     if (newlyAdded) {
//       for (let i = 0, j = newlyAdded.length; i < j; i++) {
//         const website = newlyAdded[i].document.querySelector("img").className;
//         const url = newlyAdded[i].document.querySelector("input").value;
//         try {
//           const res = await fetch(
//             `../api/add_social_links/${website}/${url}`,
//             get_fetch_settings("POST")
//           );
//           if (!res.ok) {
//             showMessage("Error: List couldn't be filtered!", "Error");
//           } else {
//             const context = await res.json();
//             showMessage(context, "Success");
//           }
//         } catch (e) {
//           showMessage("Error: Network error detected!", "Error");
//         }
//       }
//     }
//   });
