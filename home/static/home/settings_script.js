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
