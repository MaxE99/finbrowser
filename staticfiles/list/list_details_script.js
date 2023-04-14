// open the right tab when opening the page
if (location.href.includes('?commentary=')) {
    const tabs = document.querySelectorAll('.pageWrapper .tabsContainer button');
    const tabsContent = document.querySelectorAll('.pageWrapper .tabsContent');
    for (let i = 0, j = tabs.length; i < j; i++) {
        tabs[i].classList.remove('activatedTab');
        tabsContent[i].classList.remove('tabsContentActive');
    }
    tabs[1].classList.add('activatedTab');
    tabsContent[1].classList.add('tabsContentActive');
}

if (location.href.includes('?news=')) {
    const tabs = document.querySelectorAll('.pageWrapper .tabsContainer button');
    const tabsContent = document.querySelectorAll('.pageWrapper .tabsContent');
    for (let i = 0, j = tabs.length; i < j; i++) {
        tabs[i].classList.remove('activatedTab');
        tabsContent[i].classList.remove('tabsContentActive');
    }
    tabs[2].classList.add('activatedTab');
    tabsContent[2].classList.add('tabsContentActive');
}

if (location.href.includes('?saved_content=')) {
    const tabs = document.querySelectorAll('.pageWrapper .tabsContainer button');
    const tabsContent = document.querySelectorAll('.pageWrapper .tabsContent');
    for (let i = 0, j = tabs.length; i < j; i++) {
        tabs[i].classList.remove('activatedTab');
        tabsContent[i].classList.remove('tabsContentActive');
    }
    tabs[3].classList.add('activatedTab');
    tabsContent[3].classList.add('tabsContentActive');
}

// remove source from list
document
    .querySelectorAll('.sliderWrapper .slider .removeFromListButton')
    .forEach((deleteButton) => {
        deleteButton.addEventListener('click', async () => {
            try {
                const list_id = document.querySelector('.firstRow .nameContainer h2').id;
                const source_id = deleteButton.closest('.contentWrapper').id.split('#')[1];
                const data = { source_id: source_id };
                const res = await fetch(
                    `../../api/lists/${list_id}/`,
                    get_fetch_settings('PATCH', data)
                );
                if (!res.ok) {
                    showMessage('Error: Network request failed unexpectedly!', 'Error');
                } else {
                    showMessage((context = 'Source has been removed!'), 'Remove');
                    deleteButton.closest('.contentWrapper').remove();
                    if (!document.querySelector('.slider .contentWrapper')) {
                        window.location.reload();
                    }
                }
            } catch (e) {
                // showMessage("Error: Unexpected error has occurred!", "Error");
            }
        });
    });

// add Sources Search
let selected_sources = [];
if (document.querySelector('.addSourceContainer #textInput')) {
    document
        .querySelector('.addSourceContainer #textInput')
        .addEventListener('keyup', async function () {
            let search_term = document.querySelector('.addSourceContainer #textInput').value;
            let results_list = document.querySelector(
                '.addSourceContainer #searchResultsContainer'
            );
            let selected_list = document.querySelector('.addSourceContainer .selectionContainer');
            const list_id = document.querySelector('.firstRow .nameContainer h2').id;
            if (search_term && search_term.replaceAll(/\s/g, '') != '') {
                results_list.style.display = 'block';
                selected_list.style.display = 'none';
                try {
                    const res = await fetch(
                        `../../api/sources/?list_search=${search_term}&list_id=${list_id}`,
                        get_fetch_settings('GET')
                    );
                    if (!res.ok) {
                        showMessage('Error: Network request failed unexpectedly!', 'Error');
                    } else {
                        const context = await res.json();
                        results_list.innerHTML = '';
                        const resultHeader = document.createElement('div');
                        resultHeader.innerText = 'Results:';
                        results_list.append(resultHeader);
                        if (context.length > 0) {
                            context.forEach((source) => {
                                if (selected_sources.includes(source.source_id) == false) {
                                    const searchResult = document.createElement('div');
                                    searchResult.classList.add('searchResult');
                                    const resultImage = document.createElement('img');
                                    resultImage.src = `https://finbrowser.s3.us-east-2.amazonaws.com/static/${source.favicon_path}`;
                                    const sourceName = document.createElement('span');
                                    sourceName.innerText = source.name;
                                    sourceName.id = `source_id_${source.source_id}`;
                                    searchResult.append(resultImage, sourceName);
                                    results_list.appendChild(searchResult);
                                    searchResult.addEventListener(
                                        'click',
                                        function addSelectedSource() {
                                            // Remove the listener from the element the first time the listener is run:
                                            searchResult.removeEventListener(
                                                'click',
                                                addSelectedSource
                                            );
                                            selected_sources.push(source.source_id);
                                            const removeSourceButton = document.createElement('i');
                                            removeSourceButton.classList.add('fas', 'fa-times');
                                            removeSourceButton.addEventListener('click', () => {
                                                removeSourceButton.parentElement.remove();
                                                selected_sources = selected_sources.filter(
                                                    function (e) {
                                                        return (
                                                            e.toString() !==
                                                            removeSourceButton.previousElementSibling.id.split(
                                                                '#'
                                                            )[1]
                                                        );
                                                    }
                                                );
                                            });
                                            searchResult.appendChild(removeSourceButton);
                                            selected_list.appendChild(searchResult);
                                            results_list.style.display = 'none';
                                            selected_list.style.display = 'block';
                                            document.querySelector(
                                                '.listMenuWrapper .addSourceContainer #textInput'
                                            ).value = '';
                                        }
                                    );
                                }
                            });
                        }
                    }
                } catch (e) {
                    // showMessage("Error: Unexpected error has occurred!", "Error");
                }
            } else {
                results_list.style.display = 'none';
                selected_list.style.display = 'block';
            }
        });
}

// add/confirm sources to list
let activatedButton = false;
document
    .querySelector('.addSourceContainer .addSourceButton')
    .addEventListener('click', async () => {
        const list_id = document.querySelector('.firstRow .nameContainer h2').id;
        if (selected_sources.length && !activatedButton) {
            activatedButton = true;
            for (let i = 0, j = selected_sources.length; i < j; i++) {
                try {
                    const data = { source_id: selected_sources[i] };
                    const res = await fetch(
                        `../../api/lists/${list_id}/`,
                        get_fetch_settings('PATCH', data)
                    );
                    if (!res.ok) {
                        showMessage('Error: Network request failed unexpectedly!', 'Error');
                    } else {
                        showMessage('List has been updated!', 'Success');
                    }
                } catch (e) {
                    // showMessage("Error: Unexpected error has occurred!", "Error");
                }
            }
            showMessage((context = 'List has been updated!'), 'Success');
            window.location.reload();
        } else {
            showMessage('You need to select sources!', 'Error');
        }
    });

// switch list
document.querySelector('.firstRow .nameContainer').addEventListener('click', () => {
    const dropdownSymbol = document.querySelector('.firstRow .nameContainer i');
    const optionsContainer = document.querySelector('.listOptionsContainer');
    if (optionsContainer.style.display === 'block') {
        optionsContainer.style.display = 'none';
        dropdownSymbol.classList.replace('fa-chevron-up', 'fa-chevron-down');
    } else {
        optionsContainer.style.display = 'block';
        dropdownSymbol.classList.replace('fa-chevron-down', 'fa-chevron-up');
    }
});

// create list
document.querySelector('.firstRow .listOptionsContainer .createListButton').addEventListener(
    'click',
    async () => {
        try {
            const res = await fetch(`../../api/lists/`, get_fetch_settings('POST'));
            if (!res.ok) {
                showMessage('Error: Network request failed unexpectedly!', 'Error');
            } else {
                const context = await res.json();
                window.location.replace(`../../list/${context.list_id}`);
            }
        } catch (e) {
            // showMessage("Error: Unexpected error has occurred!", "Error");
        }
    },
    { once: true }
);

// delete list
document.querySelector('.editMenu .deleteListButton').addEventListener('click', () => {
    const list_id = document.querySelector('.nameContainer h2').id;
    if (document.querySelectorAll('.listsContainer .listOption').length === 1) {
        showMessage('You are not allowed to delete your last watchlist!', 'Error');
    } else {
        document.querySelector('.listMenuWrapper').style.display = 'none';
        document.querySelector('.editMenu').style.display = 'none';
        document.querySelector('.listMenuWrapper').style.display = 'block';
        document.querySelector('.listMenuWrapper .warningMessageContainer').style.display = 'flex';
        document
            .querySelector('.listMenuWrapper .warningMessageContainer .discardButton')
            .addEventListener('click', () => {
                removeModalStyle();
                document.querySelector('.listMenuWrapper').style.display = 'none';
                document.querySelector('.listMenuWrapper .warningMessageContainer').style.display =
                    'none';
            });
        document
            .querySelector('.listMenuWrapper .warningMessageContainer .confirmButton')
            .addEventListener(
                'click',
                async () => {
                    try {
                        const res = await fetch(
                            `../../api/lists/${list_id}/`,
                            get_fetch_settings('DELETE')
                        );
                        if (!res.ok) {
                            showMessage('Error: Network request failed unexpectedly!', 'Error');
                        } else {
                            showMessage('List has been deleted!', 'Remove');
                            document
                                .querySelectorAll('.listOptionsContainer .listOption')
                                .forEach((listOption) => {
                                    if (listOption.id.replace('list', '') !== list_id) {
                                        window.location.replace(`../../lists`);
                                    }
                                });
                        }
                    } catch (e) {
                        // showMessage("Error: Unexpected error has occurred!", "Error");
                    }
                },
                { once: true }
            );
    }
});

// open add source menu
document.querySelector('.actionButtonContainer .addSourceButton').addEventListener('click', () => {
    document.querySelector('.listMenuWrapper').style.display = 'block';
    document.querySelector('.addSourceContainer').style.display = 'block';
    setModalStyle();
});

document.querySelectorAll('.emptyInformationContainer button').forEach((addSourcesButton) =>
    addSourcesButton.addEventListener('click', () => {
        document.querySelector('.listMenuWrapper').style.display = 'block';
        document.querySelector('.addSourceContainer').style.display = 'block';
        setModalStyle();
    })
);

// close add source menu
document
    .querySelectorAll(
        '.listMenuWrapper .addSourceContainer .closeAddSourceContainer, .listMenuWrapper .addSourceContainer .buttonContainer .cancelButton'
    )
    .forEach((element) =>
        element.addEventListener('click', () => {
            document.querySelector('.listMenuWrapper').style.display = 'none';
            document.querySelector('.addSourceContainer').style.display = 'none';
            removeModalStyle();
        })
    );

// open edit menu
document.querySelector('.editListButton').addEventListener('click', () => {
    document.querySelector('.listMenuWrapper').style.display = 'block';
    document.querySelector('.editMenu').style.display = 'block';
    setModalStyle();
});

// close edit menu
document.querySelector('.editMenu .fa-times').addEventListener('click', () => {
    document.querySelector('.listMenuWrapper').style.display = 'none';
    document.querySelector('.editMenu').style.display = 'none';
    removeModalStyle();
});

// edit list
document.querySelector('.menuContainer .editMenu .saveEditsButton').addEventListener(
    'click',
    async () => {
        const list_id = document.querySelector('.firstRow .nameContainer h2').id;
        const newName = document.querySelector('.editMenu .listNameContainer input').value;
        const mainList = document.querySelector('.editMenu .mainListContainer input').checked;
        const data = { name: newName, main: mainList };
        if (newName.trim().length) {
            try {
                const res = await fetch(`../../api/lists/${list_id}/`, {
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
                // showMessage("Error: Unexpected error has occurred!", "Error");
            }
        } else {
            showMessage('Please enter a name!', 'Error');
        }
    },
    { once: true }
);

// main list explanation
document
    .querySelector('.listMenuWrapper .editMenu .mainListContainer .infoLink i')
    .addEventListener('click', () => {
        document.querySelector('.listMenuWrapper').style.display = 'none';
        document.querySelector('.listMenuWrapper .editMenu').style.display = 'none';
        document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
        document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display =
            'block';
        document.querySelector('.fullScreenPlaceholder .explanationContainer h3').innerText =
            'Main List';
        document.querySelector(
            '.fullScreenPlaceholder .explanationContainer .explanation'
        ).innerText =
            "Your main list is the one that opens up whenever you click on the Lists button in the header. It's important to note that you always need to have at least one main list. If you only have one list, then you won't be able to delete it as it is your main one. But, if you have multiple lists and you delete your main one, then the next list in alphabetical order will become your new main list. Don't worry though, you can easily change your main list by opening the edit menu of a list that is currently not your main one and setting it as your new main list. It's as simple as that!";
        document
            .querySelector(
                '.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times'
            )
            .addEventListener('click', () => {
                document.querySelector('.fullScreenPlaceholder').style.display = 'none';
                document.querySelector(
                    '.fullScreenPlaceholder .explanationContainer'
                ).style.display = 'none';
                document.querySelector('.listMenuWrapper').style.display = 'flex';
                document.querySelector('.listMenuWrapper .editMenu').style.display = 'block';
            });
    });
