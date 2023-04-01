// open the right tab when opening the page
if (location.href.includes("?commentary=")) {
  const tabs = document.querySelectorAll(".pageWrapper .tabsContainer button");
  const tabsContent = document.querySelectorAll(".pageWrapper .tabsContent");
  for (let i = 0, j = tabs.length; i < j; i++) {
    tabs[i].classList.remove("activatedTab");
    tabsContent[i].classList.remove("tabsContentActive");
  }
  tabs[1].classList.add("activatedTab");
  tabsContent[1].classList.add("tabsContentActive");
}

if (location.href.includes("?news=")) {
  const tabs = document.querySelectorAll(".pageWrapper .tabsContainer button");
  const tabsContent = document.querySelectorAll(".pageWrapper .tabsContent");
  for (let i = 0, j = tabs.length; i < j; i++) {
    tabs[i].classList.remove("activatedTab");
    tabsContent[i].classList.remove("tabsContentActive");
  }
  tabs[2].classList.add("activatedTab");
  tabsContent[2].classList.add("tabsContentActive");
}
