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

// add websites to profile
const saveButton = document.querySelector(".addLinksContainer .saveButton");
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
    console.log(e);
    setTimeout(console.log(e), 500000);
    showMessage("Error: Network error detected!", "Error");
  }
});

document
  .querySelector(".removeProfilePicButton")
  .addEventListener("click", async () => {
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
      console.log(e);
      setTimeout(console.log(e), 500000);
      showMessage("Error: Network error detected!", "Error");
    }
  });
