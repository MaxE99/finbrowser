/**************************************************************
    1. Functions
**************************************************************/

function changeTabsOnPageOpen(index) {
    const tabs = document.querySelectorAll('.pageWrapper .tabsContainer button');
    const tabsContent = document.querySelectorAll('.pageWrapper .tabsContent');
    for (let i = 0, j = tabs.length; i < j; i++) {
        tabs[i].classList.remove('activatedTab');
        tabsContent[i].classList.remove('tabsContentActive');
    }
    tabs[index].classList.add('activatedTab');
    tabsContent[index].classList.add('tabsContentActive');
}

/**************************************************************
    2. Other
**************************************************************/

if (location.href.includes('?commentary=')) {
    changeTabsOnPageOpen(1);
}

if (location.href.includes('?news=')) {
    changeTabsOnPageOpen(2);
}
