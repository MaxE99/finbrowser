/**************************************************************
    1. API Calls
**************************************************************/

async function removeSourceFromListLD(deleteButton) {
    try {
        const sourceId = deleteButton.closest('.contentWrapper').id.split('#')[1];
        const data = { source_id: sourceId };
        const res = await fetch(`../../api/lists/${LIST_ID}/`, getFetchSettings('PATCH', data));
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            showMessage('Source has been removed!', 'Remove');
            deleteButton.closest('.contentWrapper').remove();
            if (!document.querySelector('.slider .contentWrapper')) {
                window.location.reload();
            }
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function addSourcesToList() {
    if (selectedSources.length && !areSourcesBeingAddedToList) {
        areSourcesBeingAddedToList = true;
        for (let i = 0, j = selectedSources.length; i < j; i++) {
            try {
                const data = { source_id: selectedSources[i] };
                const res = await fetch(
                    `../../api/lists/${LIST_ID}/`,
                    getFetchSettings('PATCH', data)
                );
                if (!res.ok) {
                    showMessage('Error: Network request failed unexpectedly!', 'Error');
                } else {
                    showMessage('List has been updated!', 'Success');
                }
            } catch (e) {
                showMessage('Error: Unexpected error has occurred!', 'Error');
            }
        }
        showMessage('List has been updated!', 'Success');
        window.location.reload();
    } else {
        showMessage('You need to select sources!', 'Error');
    }
}

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

async function deleteList() {
    try {
        const res = await fetch(`../../api/lists/${LIST_ID}/`, getFetchSettings('DELETE'));
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            showMessage('List has been deleted!', 'Remove');
            document.querySelectorAll('.listOptionsContainer .listOption').forEach((listOption) => {
                listOption.id.replace('list', '') !== LIST_ID &&
                    window.location.replace(`../../lists`);
            });
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function editList() {
    const newName = document.querySelector('.editMenu .listNameContainer input').value;
    const isMainList = document.querySelector('.editMenu .mainListContainer input').checked;
    const data = { name: newName, main: isMainList };
    if (newName.trim().length) {
        try {
            const res = await fetch(`../../api/lists/${LIST_ID}/`, {
                method: 'PATCH',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    Accept: 'application/json',
                    'Content-Type': 'application/json',
                },
                mode: 'same-origin',
                body: JSON.stringify(data),
            });
            if (!res.ok) {
                showMessage('Error: Network request failed unexpectedly!', 'Error');
            } else {
                showMessage('List has been updated!', 'Success');
                window.location.reload();
            }
        } catch (e) {
            showMessage('Error: Unexpected error has occurred!', 'Error');
        }
    } else {
        showMessage('Please enter a name!', 'Error');
    }
}

async function searchAddSourcesToList(searchTerm, resultsList, selectedList) {
    try {
        const res = await fetch(
            `../../api/sources/?list_search=${searchTerm}&list_id=${LIST_ID}`,
            getFetchSettings('GET')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            showAddSourcesToListSearchResults(context, resultsList, selectedList);
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
    if (optionsContainer.style.display === 'block') {
        optionsContainer.style.display = 'none';
        dropdownSymbol.classList.replace('fa-chevron-up', 'fa-chevron-down');
    } else {
        optionsContainer.style.display = 'block';
        dropdownSymbol.classList.replace('fa-chevron-down', 'fa-chevron-up');
    }
}

function openDeleteListMenu() {
    document.querySelector('.listMenuWrapper').style.display = 'none';
    document.querySelector('.editMenu').style.display = 'none';
    document.querySelector('.listMenuWrapper').style.display = 'block';
    document.querySelector('.listMenuWrapper .warningMessageContainer').style.display = 'flex';
    document
        .querySelector('.listMenuWrapper .warningMessageContainer .discardButton')
        .addEventListener('click', () => closeDeleteListMenu());
    document
        .querySelector('.listMenuWrapper .warningMessageContainer .confirmButton')
        .addEventListener('click', () => deleteList(), { once: true });
}

function closeDeleteListMenu() {
    removeModalStyle();
    document.querySelector('.listMenuWrapper').style.display = 'none';
    document.querySelector('.listMenuWrapper .warningMessageContainer').style.display = 'none';
}

function openEditListMenu() {
    document.querySelector('.listMenuWrapper').style.display = 'block';
    document.querySelector('.editMenu').style.display = 'block';
    setModalStyle();
}

function closeEditListMenu() {
    document.querySelector('.listMenuWrapper').style.display = 'none';
    document.querySelector('.editMenu').style.display = 'none';
    removeModalStyle();
}

function openMainListExplanation() {
    document.querySelector('.listMenuWrapper').style.display = 'none';
    document.querySelector('.listMenuWrapper .editMenu').style.display = 'none';
    createExplanationContainer(
        'Main List',
        "Your main list is the one that opens up whenever you click on the Lists button in the header. It's important to note that you always need to have at least one main list. If you only have one list, then you won't be able to delete it as it is your main one. But, if you have multiple lists and you delete your main one, then the next list in alphabetical order will become your new main list. Don't worry though, you can easily change your main list by opening the edit menu of a list that is currently not your main one and setting it as your new main list. It's as simple as that!"
    );
    document
        .querySelector('.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times')
        .addEventListener('click', () => closeMainListExplanation());
}

function closeMainListExplanation() {
    document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display = 'none';
    document.querySelector('.listMenuWrapper').style.display = 'flex';
    document.querySelector('.listMenuWrapper .editMenu').style.display = 'block';
}

function closeAddSourceToListMenu() {
    document.querySelector('.listMenuWrapper').style.display = 'none';
    document.querySelector('.addSourceContainer').style.display = 'none';
    removeModalStyle();
}

function showListSearchResults(source, resultsList, selectedList) {
    const searchResult = document.createElement('div');
    searchResult.classList.add('searchResult');
    const resultImage = document.createElement('img');
    resultImage.src = `${ENV.S3_BUCKET}/${source.favicon_path}`;
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
            removeSourceFromListAndDOM(removeSourceButton)
        );
        searchResult.appendChild(removeSourceButton);
        selectedList.appendChild(searchResult);
        resultsList.style.display = 'none';
        selectedList.style.display = 'block';
        document.querySelector('.listMenuWrapper .addSourceContainer #textInput').value = '';
    });
}

function showAddSourcesToListSearchResults(context, resultsList, selectedList) {
    resultsList.innerHTML = '';
    const resultHeader = document.createElement('div');
    resultHeader.classList.add('resultHeader');
    resultHeader.innerText = 'Results:';
    resultsList.append(resultHeader);
    if (context.length > 0) {
        context.forEach((source) => {
            !selectedSources.includes(source.source_id) &&
                showListSearchResults(source, resultsList, selectedList);
        });
    }
}

function resetAddSourceToListMenu(selectedList) {
    selectedSources = [];
    selectedList.innerHTML = '';
}

function openAddSourceToListMenu() {
    document.querySelector('.listMenuWrapper').style.display = 'block';
    document.querySelector('.addSourceContainer').style.display = 'block';
    setModalStyle();
    if (document.querySelector('.addSourceContainer #addSources')) {
        document.querySelector('.addSourceContainer #addSources').addEventListener('keyup', () => {
            const searchTerm = document.querySelector('.addSourceContainer #addSources').value;
            let resultsList = document.querySelector('.addSourceContainer #searchResultsContainer');
            let selectedList = document.querySelector('.addSourceContainer .selectionContainer');
            document
                .querySelector('.addSourceContainer .buttonContainer .cancelButton')
                .addEventListener('click', () => resetAddSourceToListMenu(selectedList));
            const isSearchTermValid = (searchTerm || '').split(/\s+/).join('') !== '';
            resultsList.style.display = isSearchTermValid ? 'block' : 'none';
            selectedList.style.display = isSearchTermValid ? 'none' : 'block';
            isSearchTermValid && searchAddSourcesToList(searchTerm, resultsList, selectedList);
        });
    }
}

function removeSourceFromListAndDOM(removeSourceButton) {
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

if (location.href.includes('?saved_content=')) {
    changeTabsOnPageOpen(3);
}

let areSourcesBeingAddedToList = false;

const LIST_ID = document.querySelector('.firstRow .nameContainer h2').id;

let selectedSources = [];

/**************************************************************
    4. EventListener
**************************************************************/

document
    .querySelectorAll('.sliderWrapper .slider .removeFromListButton')
    .forEach((deleteButton) => {
        deleteButton.addEventListener('click', () => removeSourceFromListLD(deleteButton));
    });

document
    .querySelector('.addSourceContainer .addSourceButton')
    .addEventListener('click', () => addSourcesToList());

document.querySelector('.firstRow .nameContainer').addEventListener('click', () => changeLists());

document
    .querySelector('.firstRow .listOptionsContainer .createListButton')
    .addEventListener('click', () => createList(), { once: true });

document.querySelector('.editMenu .deleteListButton').addEventListener('click', () => {
    document.querySelectorAll('.listsContainer .listOption').length === 1
        ? showMessage('You are not allowed to delete your last watchlist!', 'Error')
        : openDeleteListMenu();
});

document
    .querySelector('.actionButtonContainer .addSourceButton')
    .addEventListener('click', () => openAddSourceToListMenu());

document
    .querySelectorAll('.emptyInformationContainer button')
    .forEach((addSourcesButton) =>
        addSourcesButton.addEventListener('click', () => openAddSourceToListMenu())
    );

document
    .querySelector('.listMenuWrapper .addSourceContainer .closeAddSourceContainer')
    .addEventListener('click', () => closeAddSourceToListMenu());

document.querySelector('.editListButton').addEventListener('click', () => openEditListMenu());

document.querySelector('.editMenu .fa-times').addEventListener('click', () => closeEditListMenu());

document
    .querySelector('.menuContainer .editMenu .saveEditsButton')
    .addEventListener('click', () => editList(), { once: true });

document
    .querySelector('.listMenuWrapper .editMenu .mainListContainer .infoLink i')
    .addEventListener('click', () => openMainListExplanation());
