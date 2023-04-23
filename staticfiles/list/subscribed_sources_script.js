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
document
    .querySelector('.firstRow .listOptionsContainer .createListButton')
    .addEventListener('click', async () => {
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
    });

// add/confirm sources to list
let activatedButton = false;
document
    .querySelector('.addSourceContainer .addSourceButton')
    .addEventListener('click', async () => {
        if (selected_sources.length && !activatedButton) {
            activatedButton = true;
            for (let i = 0, j = selected_sources.length; i < j; i++) {
                try {
                    const res = await fetch(
                        `../../api/sources/${selected_sources[i]}/`,
                        get_fetch_settings('PATCH')
                    );
                    if (!res.ok) {
                        showMessage('Error: Network request failed unexpectedly!', 'Error');
                    }
                } catch (e) {
                    // showMessage("Error: Unexpected error has occurred!", "Error");
                }
            }
            showMessage((context = 'Subscribed sources have been updated!'), 'Success');
            window.location.reload();
        } else {
            showMessage('You need to select sources!', 'Error');
        }
    });

let selected_sources = [];
// open add source menu
document.querySelectorAll('.emptyInformationContainer button').forEach((addSourcesButton) =>
    addSourcesButton.addEventListener('click', () => {
        document.querySelector('.listMenuWrapper').style.display = 'block';
        document.querySelector('.addSourceContainer').style.display = 'block';
        setModalStyle();
        // add Sources Search
        if (document.querySelector('.addSourceContainer #textInput')) {
            document
                .querySelector('.addSourceContainer #textInput')
                .addEventListener('keyup', async function () {
                    let search_term = document.querySelector(
                        '.addSourceContainer #textInput'
                    ).value;
                    let results_list = document.querySelector(
                        '.addSourceContainer #searchResultsContainer'
                    );
                    let selected_list = document.querySelector(
                        '.addSourceContainer .selectionContainer'
                    );
                    // cancel/reset add subscriptions form
                    document
                        .querySelector('.addSourceContainer .cancelButton')
                        .addEventListener('click', () => {
                            selected_sources = [];
                            selected_list.innerHTML = '';
                        });
                    if (search_term && search_term.split(/\s+/).join('') != '') {
                        results_list.style.display = 'block';
                        selected_list.style.display = 'none';
                        try {
                            const res = await fetch(
                                `../../api/sources/?subs_search=${search_term}`,
                                get_fetch_settings('GET')
                            );
                            if (!res.ok) {
                                showMessage('Error: Network request failed unexpectedly!', 'Error');
                            } else {
                                const context = await res.json();
                                results_list.innerHTML = '';
                                const resultHeader = document.createElement('div');
                                resultHeader.classList.add('resultHeader');
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
                                            sourceName.id = `source_id#${source.source_id}`;
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
                                                    const removeSourceButton =
                                                        document.createElement('i');
                                                    removeSourceButton.classList.add(
                                                        'fas',
                                                        'fa-times'
                                                    );
                                                    removeSourceButton.addEventListener(
                                                        'click',
                                                        () => {
                                                            removeSourceButton.parentElement.remove();
                                                            selected_sources =
                                                                selected_sources.filter(function (
                                                                    e
                                                                ) {
                                                                    return (
                                                                        e.toString() !==
                                                                        removeSourceButton
                                                                            .closest(
                                                                                '.searchResult'
                                                                            )
                                                                            .querySelector('span')
                                                                            .id.split('#')[1]
                                                                    );
                                                                });
                                                        }
                                                    );
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
    })
);

// close add source menu
document
    .querySelector('.addSourceContainer .closeAddSourceContainer')
    .addEventListener('click', () => {
        document.querySelector('.listMenuWrapper').style.display = 'none';
        document.querySelector('.addSourceContainer').style.display = 'none';
        removeModalStyle();
    });
