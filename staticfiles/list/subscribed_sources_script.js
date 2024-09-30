/**************************************************************
    1. API Calls
**************************************************************/

async function createList() {
    try {
        const res = await fetch(`../../api/lists/`, getFetchSettings('POST'));
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            window.location.replace(`../../list/${context.list_id}`);
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function changeSourcesSubscriptionStatus() {
    if (selectedSources.length && !isSubscriptionStatusBeingChanged) {
        isSubscriptionStatusBeingChanged = true;
        for (let i = 0, j = selectedSources.length; i < j; i++) {
            try {
                const res = await fetch(
                    `../../api/sources/${selectedSources[i]}/`,
                    getFetchSettings('PATCH')
                );
                if (!res.ok) {
                    showMessage('Error: Network request failed unexpectedly!', 'Error');
                }
            } catch (e) {
                showMessage('Error: Unexpected error has occurred!', 'Error');
            }
        }
        showMessage('Subscribed sources have been updated!', 'Success');
        window.location.reload();
    } else {
        showMessage('You need to select sources!', 'Error');
    }
}

async function searchForNewSubscriptions(searchTerm, resultsList, selectedList) {
    try {
        const res = await fetch(
            `../../api/sources/?subs_search=${searchTerm}`,
            getFetchSettings('GET')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            addSubscriptionsSearchResults(context, resultsList, selectedList);
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

/**************************************************************
    2. Functions
**************************************************************/

function changeLists() {
    const dropdownSymbol = document.querySelector('.firstRow .nameContainer i');
    const optionsContainer = document.querySelector('.listOptionsContainer');
    const isDisplayed = optionsContainer.style.display === 'block';
    optionsContainer.style.display = isDisplayed ? 'none' : 'block';
    dropdownSymbol.classList.toggle('fa-chevron-up', !isDisplayed);
    dropdownSymbol.classList.toggle('fa-chevron-down', isDisplayed);
}

function openAddSubscriptionsMenu() {
    document.querySelector('.listMenuWrapper').style.display = 'block';
    document.querySelector('.addSourceContainer').style.display = 'block';
    setModalStyle();
    if (document.querySelector('.addSourceContainer #textInput')) {
        document.querySelector('.addSourceContainer #textInput').addEventListener('keyup', () => {
            const searchTerm = document.querySelector('.addSourceContainer #textInput').value;
            let resultsList = document.querySelector('.addSourceContainer #searchResultsContainer');
            let selectedList = document.querySelector('.addSourceContainer .selectionContainer');
            document
                .querySelector('.addSourceContainer .cancelButton')
                .addEventListener('click', () => resetAddSubscriptionsMenu(selectedList));
            const isSearchTermValid = (searchTerm || '').split(/\s+/).join('') !== '';
            resultsList.style.display = isSearchTermValid ? 'block' : 'none';
            selectedList.style.display = isSearchTermValid ? 'none' : 'block';
            isSearchTermValid && searchForNewSubscriptions(searchTerm, resultsList, selectedList);
        });
    }
}

function closeAddSubscriptionsMenu() {
    document.querySelector('.listMenuWrapper').style.display = 'none';
    document.querySelector('.addSourceContainer').style.display = 'none';
    removeModalStyle();
}

function resetAddSubscriptionsMenu(selectedList) {
    selectedSources = [];
    selectedList.innerHTML = '';
}

function showNewSubscribedSources(source, resultsList, selectedList) {
    const searchResult = document.createElement('div');
    searchResult.classList.add('searchResult');
    const resultImage = document.createElement('img');
    resultImage.src = `https://finbrowser.s3.us-east-2.amazonaws.com/static/${source.favicon_path}`;
    const sourceName = document.createElement('span');
    sourceName.innerText = source.name;
    sourceName.id = `source_id#${source.source_id}`;
    searchResult.append(resultImage, sourceName);
    resultsList.appendChild(searchResult);
    searchResult.addEventListener('click', function addSelectedSource() {
        // Remove the listener from the element the first time the listener is run:
        searchResult.removeEventListener('click', addSelectedSource);
        selectedSources.push(source.source_id);
        const removeSourceButton = document.createElement('i');
        removeSourceButton.classList.add('fas', 'fa-times');
        removeSourceButton.addEventListener('click', () =>
            removeSourceFromListAndHTML(removeSourceButton)
        );
        searchResult.appendChild(removeSourceButton);
        selectedList.appendChild(searchResult);
        resultsList.style.display = 'none';
        selectedList.style.display = 'block';
        document.querySelector('.listMenuWrapper .addSourceContainer #textInput').value = '';
    });
}

function addSubscriptionsSearchResults(context, resultsList, selectedList) {
    resultsList.innerHTML = '';
    const resultHeader = document.createElement('div');
    resultHeader.classList.add('resultHeader');
    resultHeader.innerText = 'Results:';
    resultsList.append(resultHeader);
    if (context.length > 0) {
        context.forEach((source) => {
            !selectedSources.includes(source.source_id) &&
                showNewSubscribedSources(source, resultsList, selectedList);
        });
    }
}

function removeSourceFromListAndHTML(removeSourceButton) {
    removeSourceButton.parentElement.remove();
    selectedSources = selectedSources.filter(function (e) {
        return (
            e.toString() !==
            removeSourceButton.closest('.searchResult').querySelector('span').id.split('#')[1]
        );
    });
}

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
    3. Other
**************************************************************/

if (location.href.includes('?commentary=')) {
    changeTabsOnPageOpen(1);
}

if (location.href.includes('?news=')) {
    changeTabsOnPageOpen(2);
}

let isSubscriptionStatusBeingChanged = false;

let selectedSources = [];

/**************************************************************
    4. EventListener
**************************************************************/

document.querySelector('.firstRow .nameContainer').addEventListener('click', () => changeLists());

document
    .querySelector('.firstRow .listOptionsContainer .createListButton')
    .addEventListener('click', () => createList());

document
    .querySelector('.addSourceContainer .addSourceButton')
    .addEventListener('click', () => changeSourcesSubscriptionStatus());

document
    .querySelectorAll('.emptyInformationContainer button')
    .forEach((addSourcesButton) =>
        addSourcesButton.addEventListener('click', () => openAddSubscriptionsMenu())
    );

document
    .querySelector('.addSourceContainer .closeAddSourceContainer')
    .addEventListener('click', () => closeAddSubscriptionsMenu());
