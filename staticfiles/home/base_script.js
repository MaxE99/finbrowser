function setModalStyle() {
    document.querySelector('body').style.overflow = 'hidden';
    document.querySelector('.pageWrapper').style.opacity = '0.1';
    document.querySelector('header').style.opacity = 0.1;
    document.querySelector('header . outerHeaderContainer').style.zIndex = 0;
}

function removeModalStyle() {
    document.querySelector('body').style.removeProperty('overflow');
    document.querySelector('.pageWrapper').style.removeProperty('opacity');
    document.querySelector('header').style.removeProperty('opacity');
    document.querySelector('header . outerHeaderContainer').style.zIndex = 1000;
}

// open hamburger menu
document.querySelector('.headerContainer .fa-bars').addEventListener('click', (e) => {
    if (e.target.classList.contains('fa-bars')) {
        e.target.classList.replace('fa-bars', 'fa-times');
        e.target.classList.add('closeNavMenuButton');
    } else {
        e.target.classList.replace('fa-times', 'fa-bars');
        e.target.classList.remove('closeNavMenuButton');
    }
    const horizontalNavigation = document.querySelector('.horizontalNavigation');
    horizontalNavigation.style.display !== 'flex'
        ? (horizontalNavigation.style.display = 'flex')
        : (horizontalNavigation.style.display = 'none');
});

// deactivate autocomplete for all inputs
document.querySelectorAll('input').forEach((input) => {
    input.setAttribute('autocomplete', 'off');
});

// creates crsf token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function get_fetch_settings(inputMethod, data = false) {
    const settings = {
        method: inputMethod,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            Accept: 'application/json',
            'Content-Type': 'application/json',
        },
        mode: 'same-origin',
    };
    if (data) {
        settings['body'] = JSON.stringify(data);
    }
    return settings;
}

// Gives user feedback if action that includes DRF has been succesfull or not
function showMessage(message, type) {
    document.querySelectorAll('.messages').forEach((message) => {
        message.remove();
    });
    const messages = document.createElement('ul');
    messages.classList.add('messages');
    const state = document.createElement('li');
    state.innerText = message;
    if (type == 'Success') {
        state.classList.add('success');
    } else if (type == 'Remove') {
        state.classList.add('remove');
    } else {
        state.classList.add('error');
    }
    messages.appendChild(state);
    document.querySelector('.overlay').appendChild(messages);
}

// search site api request with creation
async function getSearchResults(search_term, results_list, smallScreen = false) {
    try {
        const res = await fetch(
            `../../../../../../api/search_site/${search_term}`,
            get_fetch_settings('GET')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            if ((smallScreen && context[0].length) || context[1].length || context[2].length) {
                document.querySelector(
                    '.smallScreenSearchContainer .recommendedContainer'
                ).style.display = 'none';
            } else if (
                smallScreen &&
                !context[0].length &&
                !context[1].length &&
                !context[2].length
            ) {
                document.querySelector(
                    '.smallScreenSearchContainer .noResultsFound'
                ).style.display = 'block';
                document.querySelector('.smallScreenSearchContainer .noResultsFound').innerText =
                    "I'm sorry but there are no results for " + search_term;
            }
            results_list.style.display = 'flex';
            results_list.innerHTML = '';
            if (context[0].length > 0) {
                results_list.innerHTML += `<div class="searchResultHeader">Stocks</div>`;
                context[0].forEach((stock) => {
                    const sourceRes = `<div class="searchResult"><div class="stockContainer"><div class="stockTicker">${stock.ticker}</div><div class="companyName">${stock.full_company_name}</div><a href="../../../../../../stock/${stock.ticker}"></a></div></div>`;
                    results_list.innerHTML += sourceRes;
                });
            }
            if (context[1].length > 0) {
                results_list.innerHTML += `<div class="searchResultHeader">Sources</div>`;
                context[1].forEach((source) => {
                    const sourceRes = `<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${source.favicon_path}"><span>${source.name}</span><a href="../../../../../../source/${source.slug}"></a></div>`;
                    results_list.innerHTML += sourceRes;
                });
            }
            if (context[2].length > 0) {
                results_list.innerHTML += `<div class="searchResultHeader">Articles</div>`;
                for (let i = 0, j = context[2].length; i < j; i++) {
                    let xfavicon = context[2][i].source.favicon_path;
                    let xtitle = context[2][i].title;
                    let xlink = context[2][i].link;
                    const articleRes = `<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${xfavicon}"><span>${xtitle}</span><a href="${xlink}" target="_blank"></a></div>`;
                    results_list.innerHTML += articleRes;
                }
            }
        }
    } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
    }
}

// main search with autocomplete
document.querySelector('header #mainAutocomplete').addEventListener('keyup', async function (e) {
    let search_term = document.querySelector('header #mainAutocomplete').value;
    if (e.key == 'Enter' && search_term.replaceAll(/\s/g, '') != '') {
        window.location.href = `../../../../../../search_results/${search_term}`;
    } else {
        let results_list = document.querySelector('header #mainAutocomplete_result');
        if (search_term && search_term.replaceAll(/\s/g, '') != '') {
            getSearchResults(search_term, results_list);
            document.onclick = function (e) {
                if (e.target.id !== 'autocomplete_list_results') {
                    results_list.style.display = 'none';
                }
            };
        } else {
            results_list.style.display = 'none';
        }
    }
});

function closeAllPotentialOpenPopups() {
    document.querySelector('.fullScreenPlaceholder .addToListForm').style.display = 'none';
    document.querySelector('.fullScreenPlaceholder .authPromptContainer').style.display = 'none';
    document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display = 'none';
    if (document.querySelector('.portfolioMenuWrapper')) {
        document.querySelector('.portfolioMenuWrapper').style.display = 'none';
        document.querySelector('.portfolioMenuWrapper .addStocksContainer').style.display = 'none';
        document.querySelector('.portfolioMenuWrapper .editMenu').style.display = 'none';
        document.querySelector('.portfolioMenuWrapper .warningMessageContainer').style.display =
            'none';
    }
    if (document.querySelector('.listMenuWrapper')) {
        document.querySelector('.listMenuWrapper').style.display = 'none';
        document.querySelector('.listMenuWrapper .addSourceContainer').style.display = 'none';
        document.querySelector('.listMenuWrapper .editMenu').style.display = 'none';
        document.querySelector('.listMenuWrapper .warningMessageContainer').style.display = 'none';
    }
    if (document.querySelector('.stockMenuWrapper')) {
        document.querySelector('.stockMenuWrapper').style.display = 'none';
        document.querySelector('.stockMenuWrapper .addStockContainer').style.display = 'none';
    }
    if (document.querySelector('.keywordCreationWrapper')) {
        document.querySelector('.keywordCreationWrapper').style.display = 'none';
    }
    if (document.querySelector('.notificationPopupWrapper')) {
        document.querySelector('.notificationPopupWrapper').style.display = 'none';
    }
    if (document.querySelector('.sourceRatingsWrapper')) {
        document.querySelector('.sourceRatingsWrapper').style.display = 'none';
    }
}

// small screen searchbar
document.querySelector('header .smallScreenSearchIcon').addEventListener('click', () => {
    setModalStyle();
    closeAllPotentialOpenPopups();
    document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
    document.querySelector('.fullScreenPlaceholder .smallScreenSearchContainer').style.display =
        'block';
    document.querySelector('.fullScreenPlaceholder .closeImageButton').style.display = 'flex';
});

document
    .querySelector('.smallScreenSearchContainer #mainAutocomplete')
    .addEventListener('keyup', async function (e) {
        let search_term = document.querySelector(
            '.smallScreenSearchContainer #mainAutocomplete'
        ).value;
        if (e.key == 'Enter' && search_term.replaceAll(/\s/g, '') != '') {
            window.location.href = `../../../../../../search_results/${search_term}`;
        } else {
            const recommendedContainer = document.querySelector(
                '.smallScreenSearchContainer .recommendedContainer'
            );
            let results_list = document.querySelector(
                '.smallScreenSearchContainer .smallFormContentWrapper #mainAutocomplete_result'
            );
            if (search_term && search_term.replaceAll(/\s/g, '') != '') {
                getSearchResults(search_term, results_list, true);
                document.querySelector(
                    '.smallScreenSearchContainer .noResultsFound'
                ).style.display = 'none';
            } else {
                results_list.style.display = 'none';
                recommendedContainer.style.display = 'block';
                document.querySelector(
                    '.smallScreenSearchContainer .noResultsFound'
                ).style.display = 'none';
            }
        }
    });

//get search results
document.querySelector('.mainSearchContainer i').addEventListener('click', () => {
    search_term = document.querySelector('.mainInputSearch').value;
    if (search_term.replaceAll(/\s/g, '') != '') {
        window.location.href = `../../../../../../search_results/${search_term}`;
    }
});

//Dropdown User Menu
const dropdownButton = document.querySelector('.userProfile');
if (dropdownButton) {
    dropdownButton.addEventListener('click', () => {
        const profileMenu = document.querySelector('.profileMenu');
        if (profileMenu.style.display == 'flex') {
            profileMenu.style.display = 'none';
        } else {
            document.querySelector('.userSpace .notificationPopupWrapper').style.display = 'none';
            profileMenu.style.display = 'flex';
            document.onclick = function (e) {
                const withinProfileMenu = e.target.closest('.profileMenu');
                const withinUserProfile = e.target.closest('.userProfile');
                if (!withinProfileMenu && !withinUserProfile) {
                    profileMenu.style.display = 'none';
                }
            };
        }
    });
}

// logout button click
document
    .querySelector('.headerContainer .profileMenu .profileMenuOption:last-of-type')
    ?.addEventListener('click', (e) => {
        e.target.querySelector('button').click();
    });

function checkForOpenContainers() {
    let allContainersClosed = true;
    const addToListForms = document.querySelectorAll('.addToListForm');
    for (let i = 0, j = addToListForms.length; i < j; i++) {
        if (addToListForms[i].style.display != 'none' && addToListForms[i].style.display) {
            allContainersClosed = false;
            return allContainersClosed;
        }
    }
    return allContainersClosed;
}

// article ellipsis options
let previousOptionsContainer;
let previousEllipsis;
function openContentOptionsMenu(e, ellipsis) {
    if (!ellipsis.classList.contains('openAuthPrompt')) {
        const allContainersClosed = checkForOpenContainers();
        if (allContainersClosed) {
            if (previousOptionsContainer && e.target !== previousEllipsis) {
                previousOptionsContainer.style.display = 'none';
            }
            const articleOptionsContainer = ellipsis.parentElement.querySelector(
                '.articleOptionsContainer'
            );
            if (articleOptionsContainer.style.display != 'flex') {
                articleOptionsContainer.style.display = 'flex';
                document.onclick = function (e) {
                    if (e.target !== ellipsis) {
                        ellipsis.parentElement.querySelector(
                            '.articleOptionsContainer'
                        ).style.display = 'none';
                    }
                };
            } else {
                articleOptionsContainer.style.display = 'none';
            }
            previousOptionsContainer = ellipsis.parentElement.querySelector(
                '.articleOptionsContainer'
            );
            previousEllipsis = ellipsis;
        }
    }
}

document.querySelectorAll('.contentInfoContainer .fa-ellipsis-h').forEach((ellipsis) => {
    ellipsis.addEventListener('click', function (e) {
        openContentOptionsMenu(e, ellipsis);
    });
});

// (un)highlight articles
async function highlightContent(highlighterButton) {
    if (!highlighterButton.classList.contains('openAuthPrompt')) {
        const article_id = highlighterButton.closest('.articleContainer').id.split('#')[1];
        const highlightState = highlighterButton.lastElementChild.innerText;
        let action;
        if (highlightState == 'Highlight article') {
            action = 'highlight';
        } else {
            action = 'unhighlight';
        }
        try {
            const data = { article: article_id };
            const res = await fetch(`../../../../../../api/highlighted_articles/`, {
                method: 'POST',
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
                const context = await res.json();
                if (action == 'highlight') {
                    showMessage(context, 'Success');
                    highlighterButton.innerHTML = `<i class="fas fa-times"></i><span>Unhighlight article</span>`;
                } else {
                    showMessage(context, 'Remove');
                    highlighterButton.innerHTML = `<i class="fas fa-highlighter"></i><span>Highlight article</span>`;
                }
            }
        } catch (e) {
            // // showMessage("Error: Unexpected error has occurred!", "Error");
        }
    }
}

document.querySelectorAll('.addToHighlightedButton').forEach((highlighterButton) => {
    highlighterButton.addEventListener('click', () => {
        highlightContent(highlighterButton);
    });
});

//activate notification popup
if (document.querySelector('.userSpace .notificationBell')) {
    document.querySelector('.userSpace .notificationBell').addEventListener('click', async () => {
        if (
            document.querySelector('.fullScreenPlaceholder .smallScreenSearchContainer').style
                .display == 'block'
        ) {
            document.querySelector('.fullScreenPlaceholder').style.display = 'none';
            document.querySelector(
                '.fullScreenPlaceholder .smallScreenSearchContainer'
            ).style.display = 'none';
            document.querySelector('.fullScreenPlaceholder .closeImageButton').style.display =
                'none';
            removeModalStyle();
        }
        const notificationPopup = document.querySelector('.notificationPopupWrapper');
        if (notificationPopup.style.display == 'block') {
            notificationPopup.style.display = 'none';
            document.querySelector('.unseenNotifications').remove();
            document.querySelectorAll('.unseenNotification').forEach((notification) => {
                notification.classList.remove('unseenNotification');
            });
        } else {
            notificationPopup.style.display = 'block';
            try {
                const res = await fetch(
                    `../../../../../../api/notifications/`,
                    get_fetch_settings('PUT')
                );
                if (!res.ok) {
                    showMessage('Error: Network request failed unexpectedly!', 'Error');
                }
            } catch (e) {
                // showMessage("Error: Unexpected error has occurred!", "Error");
            }
        }
    });
}

//Notification switch
const notificationTabs = document.querySelectorAll('.notificationHeadersContainer button');
const notificationContent = document.querySelectorAll('.notificationsContainer');
notificationTabs.forEach((tab) => {
    tab.addEventListener('click', () => {
        for (let i = 0, j = notificationTabs.length; i < j; i++) {
            notificationTabs[i].classList.remove('activeNotificationCategory');
            notificationContent[i].classList.remove('activeNotificationContainer');
        }
        notificationTabs[tab.dataset.forTab].classList.add('activeNotificationCategory');
        notificationContent[tab.dataset.forTab].classList.add('activeNotificationContainer');
    });
});

// Carousell

document.querySelectorAll('.handle').forEach((handle) => {
    handle.addEventListener('click', (e) => {
        const slider = e.target.closest('.sliderWrapper').querySelector('.slider');
        const sliderIndex = parseInt(getComputedStyle(slider).getPropertyValue('--slider-index'));
        const itemsPerScreen = parseInt(
            getComputedStyle(slider).getPropertyValue('--items-per-screen')
        );
        const progressBarItemCount = Math.ceil(
            slider.querySelectorAll('.contentWrapper').length / itemsPerScreen
        );
        if (handle.classList.contains('leftHandle')) {
            sliderIndex - 1 < 0
                ? slider.style.setProperty('--slider-index', progressBarItemCount - 1)
                : slider.style.setProperty('--slider-index', sliderIndex - 1);
        }
        if (handle.classList.contains('rightHandle')) {
            sliderIndex + 1 >= progressBarItemCount
                ? slider.style.setProperty('--slider-index', 0)
                : slider.style.setProperty('--slider-index', sliderIndex + 1);
        }
    });
});

// Source Subscribtion function
document.querySelectorAll('.sliderWrapper .slider .subscribeButton').forEach((subscribeButton) => {
    subscribeButton.addEventListener('click', async () => {
        if (!subscribeButton.classList.contains('openAuthPrompt')) {
            try {
                const source_id = subscribeButton.closest('.contentWrapper').id.split('#')[1];
                const action = subscribeButton.innerText;
                const res = await fetch(
                    `../../api/sources/${source_id}/`,
                    get_fetch_settings('PATCH')
                );
                if (!res.ok) {
                    showMessage('Error: Network request failed unexpectedly!', 'Error');
                } else {
                    if (action == 'Subscribe') {
                        subscribeButton.classList.add('subscribed');
                        subscribeButton.innerText = 'Subscribed';
                        showMessage((context = 'SOURCE HAS BEEN SUBSCRIBED!'), 'Success');
                    } else {
                        subscribeButton.classList.remove('subscribed');
                        subscribeButton.innerText = 'Subscribe';
                        showMessage((context = 'SOURCE HAS BEEN UNSUBSCRIBED!'), 'Remove');
                    }
                }
            } catch (e) {
                // showMessage("Error: Unexpected error has occurred!", "Error");
            }
        }
    });
});

//change tabs
const tabs = document.querySelectorAll('.tabsContainer button');
const tabsContent = document.querySelectorAll('.tabsContent');

tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
        for (let i = 0, j = tabs.length; i < j; i++) {
            tabs[i].classList.remove('activatedTab');
            tabsContent[i].classList.remove('tabsContentActive');
        }
        tabs[tab.dataset.forTab].classList.add('activatedTab');
        tabsContent[tab.dataset.forTab].classList.add('tabsContentActive');
    });
});

// open create keyword notification modal
document
    .querySelector('.notificationPopupWrapper .addKeywordsContainer button')
    ?.addEventListener('click', () => {
        document.querySelector(
            '.notificationPopupWrapper .createKeywordNotificationModal'
        ).style.display = 'flex';
    });

async function save_keyword() {
    const input = document.querySelector(
        '.notificationPopupWrapper .createKeywordNotificationModal input'
    );
    if (input.value.trim().length > 2) {
        try {
            const data = { keyword: input.value };
            const res = await fetch(`../../api/notifications/`, {
                method: 'POST',
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
                input.value = '';
                showMessage('A new keyword has been created!', 'Success');
            }
        } catch (e) {
            // showMessage("Error: Unexpected error has occurred!", "Error");
        }
    } else {
        showMessage('A keyword must consist of at least 3 letters!', 'Error');
    }
}

//save new keyword
document
    .querySelector('.notificationPopupWrapper .createKeywordNotificationModal .saveButton')
    ?.addEventListener('click', () => {
        save_keyword();
    });

document
    .querySelector('.notificationPopupWrapper .createKeywordNotificationModal input')
    ?.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            save_keyword();
        }
    });

// close keyword notification modal
document
    .querySelector('.notificationPopupWrapper .createKeywordNotificationModal .discardButton')
    ?.addEventListener('click', () => {
        document.querySelector(
            '.notificationPopupWrapper .createKeywordNotificationModal'
        ).style.display = 'none';
    });

// auth prompt msg mapping
function getAuthPromptMsg(button) {
    if (button.classList.contains('ap1')) {
        return 'Add this source to your lists to stay up to date with the latest content';
    } else if (button.classList.contains('ap2')) {
        return 'Subscribe to this source to your lists to stay up to date with the latest content';
    } else if (button.classList.contains('ap3')) {
        return 'Get instant notifications when new content is available';
    } else if (button.classList.contains('ap4')) {
        return 'Add this stock to your portfolios to stay up to date with the latest analysis and news';
    } else if (button.classList.contains('ap5')) {
        return 'Add this stock to your lists';
    } else if (button.classList.contains('ap6')) {
        return 'Add content to your lists';
    } else if (button.classList.contains('ap7')) {
        return 'Rate this source';
    }
}

//open auth prompt
function openAuthPrompt(promptButton) {
    const fullScreenPlaceholder = document.querySelector('.fullScreenPlaceholder');
    document.querySelector('.fullScreenPlaceholder .authPromptContainer').style.display = 'block';
    fullScreenPlaceholder.style.display = 'flex';
    const promptMsg = getAuthPromptMsg(promptButton);
    document.querySelector('.fullScreenPlaceholder .authPromptContainer h3').innerText = promptMsg;
    setModalStyle();
}

document.querySelectorAll('.openAuthPrompt').forEach((promptButton) =>
    promptButton.addEventListener('click', () => {
        openAuthPrompt(promptButton);
    })
);

//close auth prompt
document
    .querySelector('.fullScreenPlaceholder .authPromptContainer .fa-times')
    .addEventListener('click', () => {
        document.querySelector('.fullScreenPlaceholder .authPromptContainer').style.display =
            'none';
        document.querySelector('.fullScreenPlaceholder').style.display = 'none';
        removeModalStyle();
    });

//open add list to sources form
document.querySelectorAll('.sourceAddToListButton').forEach((addSourceButton) => {
    if (
        !addSourceButton.classList.contains('openAuthPrompt') &&
        addSourceButton.closest('.contentWrapper')
    ) {
        addSourceButton.addEventListener('click', () => {
            setModalStyle();
            const sourceId = addSourceButton.closest('.contentWrapper').id.split('#')[1];
            const sourceName = addSourceButton
                .closest('.contentWrapper')
                .querySelector('.nameContainer span').innerText;
            document.querySelector('.fullScreenPlaceholder .addToListForm h2 span').innerText =
                sourceName;
            document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
            document.querySelector('.fullScreenPlaceholder .addSourceToListForm').style.display =
                'block';
            document.querySelector('.fullScreenPlaceholder .addSourceToListForm').id =
                'source_id' + sourceId;
            const checkboxes = document.querySelectorAll(
                '.fullScreenPlaceholder .listContainer input:first-of-type'
            );
            checkboxes.forEach((checkbox) => {
                const sourcesInList = checkbox
                    .closest('.listContainer')
                    .querySelector('.sourcesInList').value;
                if (JSON.parse(sourcesInList).includes(parseInt(sourceId))) {
                    checkbox.checked = true;
                } else {
                    checkbox.checked = false;
                }
            });
        });
    }
});

//close add list sources form
document
    .querySelectorAll('.fullScreenPlaceholder .addSourceToListForm .fa-times')
    .forEach((closeAddSourceFormButton) => {
        closeAddSourceFormButton.addEventListener('click', () => {
            removeModalStyle();
            document.querySelector('.addSourceToListForm').style.display = 'none';
            document.querySelector('.fullScreenPlaceholder').style.display = 'none';
        });
    });

//cancel button
document
    .querySelector('.fullScreenPlaceholder .addSourceToListForm .cancelButton')
    ?.addEventListener('click', () => {
        removeModalStyle();
        document.querySelector('.addSourceToListForm').style.display = 'none';
        document.querySelector('.fullScreenPlaceholder').style.display = 'none';
    });

// // add sources to lists

function check_list_status(saveButton) {
    let add_list_ids = [];
    let remove_list_ids = [];
    const input_list = saveButton
        .closest('.addSourceToListForm')
        .querySelectorAll('.listContainer input:first-of-type');
    const source_id = document
        .querySelector('.fullScreenPlaceholder .addSourceToListForm')
        .id.replace('source_id', '');
    input_list.forEach((checkbox) => {
        const sourcesOriginallyInList = checkbox
            .closest('.listContainer')
            .querySelector('.sourcesInList').value;
        if (
            JSON.parse(sourcesOriginallyInList).includes(parseInt(source_id)) &&
            !checkbox.checked
        ) {
            remove_list_ids.push(checkbox.id.split('id_list_')[1]);
        } else if (
            checkbox.checked &&
            !JSON.parse(sourcesOriginallyInList).includes(parseInt(source_id))
        ) {
            add_list_ids.push(checkbox.id.split('id_list_')[1]);
        }
    });
    return [add_list_ids, remove_list_ids];
}

document
    .querySelectorAll('.fullScreenPlaceholder .addSourceToListForm .saveButton')
    .forEach((saveButton) => {
        saveButton.addEventListener(
            'click',
            async () => {
                if (
                    document
                        .querySelector('.fullScreenPlaceholder .addToListForm')
                        .id.includes('source_id')
                ) {
                    const source_id = document
                        .querySelector('.fullScreenPlaceholder .addSourceToListForm')
                        .id.replace('source_id', '');
                    const [add_lists, remove_lists] = check_list_status(saveButton);
                    for (let i = 0, j = add_lists.length; i < j; i++) {
                        try {
                            const data = { source_id: source_id };
                            const res = await fetch(
                                `../../api/lists/${add_lists[i]}/`,
                                get_fetch_settings('PATCH', data)
                            );
                            if (!res.ok) {
                                showMessage('Error: Network request failed unexpectedly!', 'Error');
                            }
                        } catch (e) {
                            // showMessage("Error: Unexpected error has occurred!", "Error");
                        }
                    }
                    for (let i = 0, j = remove_lists.length; i < j; i++) {
                        try {
                            const data = { source_id: source_id };
                            const res = await fetch(
                                `../../api/lists/${remove_lists[i]}/`,
                                get_fetch_settings('PATCH', data)
                            );
                            if (!res.ok) {
                                showMessage('Error: Network request failed unexpectedly!', 'Error');
                            }
                        } catch (e) {
                            // showMessage("Error: Unexpected error has occurred!", "Error");
                        }
                    }
                    showMessage((context = 'Lists have been updated!'), 'Success');
                    window.location.reload();
                }
            },
            { once: true }
        );
    });

async function update_articles_in_list(list_id, article_id) {
    try {
        const data = { article_id: article_id };
        const res = await fetch(
            `../../../../../../api/lists/${list_id}/`,
            get_fetch_settings('PATCH', data)
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        }
    } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
    }
}

// open addtolist menu
function openAddToListMenu(e) {
    document.querySelector('.fullScreenPlaceholder .smallScreenSearchContainer').style.display =
        'none';
    document.querySelector('.fullScreenPlaceholder .closeImageButton').style.display = 'none';
    const article_id = e.target.closest('.articleContainer').id.split('cc#')[1];
    const checkboxes = document.querySelectorAll(
        '.fullScreenPlaceholder .listContainer input:first-of-type'
    );
    checkboxes.forEach((checkbox) => {
        const articlesInList = checkbox
            .closest('.listContainer')
            .querySelector('.articlesInList').value;
        if (JSON.parse(articlesInList).includes(parseInt(article_id))) {
            checkbox.checked = true;
        } else {
            checkbox.checked = false;
        }
    });
    const articleName = e.target
        .closest('.articleContainer')
        .querySelector('.contentBody p')?.innerText;
    if (articleName) {
        document.querySelector('.fullScreenPlaceholder .addToListForm h2 span').innerText =
            articleName;
    } else {
        document.querySelector('.fullScreenPlaceholder .addToListForm h2 span').innerText =
            'Retweet/Reply';
    }
    setModalStyle();
    document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
    document.querySelector('.fullScreenPlaceholder .addToListForm').id = 'article_id' + article_id;
    document.querySelector('.fullScreenPlaceholder .addToListForm').style.display = 'block';
    const saveButton = document.querySelector(
        '.fullScreenPlaceholder .addSourceToListForm .saveButton'
    );
    saveButton.addEventListener(
        'click',
        () => {
            if (
                document
                    .querySelector('.fullScreenPlaceholder .addToListForm')
                    .id.includes('article_id')
            ) {
                const input_list = saveButton
                    .closest('.addSourceToListForm')
                    .querySelectorAll('.listContainer input:first-of-type');
                input_list.forEach((checkbox) => {
                    const articlesOriginallyInList = checkbox
                        .closest('.listContainer')
                        .querySelector('.articlesInList').value;
                    if (
                        (JSON.parse(articlesOriginallyInList).includes(parseInt(article_id)) &&
                            !checkbox.checked) ||
                        (checkbox.checked &&
                            !JSON.parse(articlesOriginallyInList).includes(parseInt(article_id)))
                    ) {
                        update_articles_in_list(checkbox.id.split('id_list_')[1], article_id);
                    }
                });
                showMessage('Lists have been updated!', 'Success');
                window.location.reload();
            }
        },
        { once: true }
    );
}

document.querySelectorAll('.addToListButton').forEach((element) => {
    element.addEventListener('click', (e) => {
        openAddToListMenu(e);
    });
});

// click on list container => click on input checkbox
document
    .querySelectorAll('.addToListForm .listSelectionContainer .listContainer')
    .forEach((listContainer) =>
        listContainer.addEventListener('click', () => {
            listContainer.querySelector('input:first-of-type').checked =
                !listContainer.querySelector('input:first-of-type').checked;
        })
    );

// notification popup keyword notification explanation
document
    .querySelector('.notificationPopupWrapper .createKeywordNotificationModal .infoLink i')
    ?.addEventListener('click', () => {
        closeAllPotentialOpenPopups();
        setModalStyle();
        document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
        document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display =
            'block';
        document.querySelector('.fullScreenPlaceholder .explanationContainer h3').innerText =
            'Keywords';
        document.querySelector(
            '.fullScreenPlaceholder .explanationContainer .explanation'
        ).innerText =
            'If you want to be notified when new content is published on a specific topic, add a keyword and you will receive an alert when any of the sources publish content containing that keyword on FinBrowser.';
        const closeExplanationButton = document.querySelector(
            '.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times'
        );
        closeExplanationButton.addEventListener('click', () => {
            removeModalStyle();
            document.querySelector('.fullScreenPlaceholder').style.display = 'none';
            document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display =
                'none';
        });
    });

// image on click fullscreen
document.querySelectorAll('.tweetImage').forEach((tweetImage) => {
    tweetImage.addEventListener('click', () => {
        setModalStyle();
        const fullScreenPlaceholder = document.querySelector('.fullScreenPlaceholder');
        fullScreenPlaceholder.style.display = 'flex';
        const img = document.createElement('img');
        img.classList.add('fullScreenImage');
        img.src = tweetImage.src;
        fullScreenPlaceholder.appendChild(img);
        fullScreenPlaceholder.querySelector('.closeImageButton').style.display = 'flex';
    });
});

// close image Container
document.querySelector('.fullScreenPlaceholder .closeImageButton').addEventListener('click', () => {
    removeModalStyle();
    document.querySelector('.fullScreenPlaceholder').style.display = 'none';
    document.querySelector('.fullScreenPlaceholder .smallScreenSearchContainer').style.display =
        'none';
    document.querySelector('.fullScreenPlaceholder .fullScreenImage')?.remove();
    document.querySelector('.fullScreenPlaceholder .closeImageButton').style.display = 'none';
});
