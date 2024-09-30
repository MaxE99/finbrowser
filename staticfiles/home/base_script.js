/**************************************************************
    1. API Calls
**************************************************************/

async function getSearchResults(searchTerm, resultsList, smallScreen = false) {
    try {
        const res = await fetch(
            `../../../../../../api/search_site/${searchTerm}`,
            getFetchSettings('GET')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            console.log(context);
            if (
                (smallScreen && context['stocks'].length) ||
                context['sources'].length ||
                context['articles'].length
            ) {
                document.querySelector(
                    '.smallScreenSearchContainer .recommendedContainer'
                ).style.display = 'none';
            } else if (
                smallScreen &&
                !context['stocks'].length &&
                !context['sources'].length &&
                !context['articles'].length
            ) {
                document.querySelector(
                    '.smallScreenSearchContainer .noResultsFound'
                ).style.display = 'block';
                document.querySelector('.smallScreenSearchContainer .noResultsFound').innerText =
                    "I'm sorry but there are no results for " + searchTerm;
            }
            showSearchResults(context, resultsList);
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function updateArticleStatusesInList(listId, articleId) {
    try {
        const data = { article_id: articleId };
        const res = await fetch(
            `../../../../../../api/lists/${listId}/`,
            getFetchSettings('PATCH', data)
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function saveKeyword() {
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
                if (res.status === 403) {
                    res.json().then((json) => {
                        showMessage(json.detail, 'Error');
                    });
                } else {
                    showMessage('Error: Network request failed unexpectedly!', 'Error');
                }
            } else {
                input.value = '';
                showMessage('A new keyword has been created!', 'Success');
            }
        } catch (e) {
            showMessage('Error: Unexpected error has occurred!', 'Error');
        }
    } else {
        showMessage('A keyword must consist of at least 3 letters!', 'Error');
    }
}

async function changeHighlightedStatus(highlighterButton) {
    if (!highlighterButton.classList.contains('openAuthPrompt')) {
        const articleId = highlighterButton.closest('.articleContainer').id.split('#')[1];
        const action =
            highlighterButton.lastElementChild.innerText == 'Highlight article'
                ? 'highlight'
                : 'unhighlight';
        try {
            const data = { article: articleId };
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
                showHighlightedStatus(action, highlighterButton, context);
            }
        } catch (e) {
            showMessage('Error: Unexpected error has occurred!', 'Error');
        }
    }
}

async function updateNotificationSeenStatus() {
    try {
        const res = await fetch(`../../../../../../api/notifications/`, getFetchSettings('PUT'));
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function subscribeToSource(subscribeButton) {
    if (!subscribeButton.classList.contains('openAuthPrompt')) {
        try {
            const sourceId = subscribeButton.closest('.contentWrapper').id.split('#')[1];
            const res = await fetch(`../../api/sources/${sourceId}/`, getFetchSettings('PATCH'));
            if (!res.ok) {
                showMessage('Error: Network request failed unexpectedly!', 'Error');
            } else {
                showSubscriptionStatus(subscribeButton);
            }
        } catch (e) {
            showMessage('Error: Unexpected error has occurred!', 'Error');
        }
    }
}

async function addSourceToList(sourceId, listId) {
    try {
        const data = { source_id: sourceId };
        const res = await fetch(`../../api/lists/${listId}/`, getFetchSettings('PATCH', data));
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function removeSourceFromList(sourceId, listId) {
    try {
        const data = { source_id: sourceId };
        const res = await fetch(`../../api/lists/${listId}/`, getFetchSettings('PATCH', data));
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

/**************************************************************
    2. Functions
**************************************************************/

function saveSourceListsStatus(saveButton) {
    const addToListForm = document.querySelector('.fullScreenPlaceholder .addToListForm');
    if (addToListForm.id.includes('source_id')) {
        const sourceId = addToListForm.id.replace('source_id', '');
        const [addLists, removeLists] = checkListStatus(saveButton);
        addLists.forEach((list) => addSourceToList(sourceId, list));
        removeLists.forEach((list) => removeSourceFromList(sourceId, list));
        showMessage('Lists have been updated!', 'Success');
        window.location.reload();
    }
}

function showSearchResults(context, resultsList) {
    resultsList.style.display = 'flex';
    resultsList.innerHTML = '';
    if (context['stocks'].length) {
        resultsList.innerHTML += `<div class="searchResultHeader">Stocks</div>`;
        context['stocks'].forEach((stock) => {
            const sourceRes = `<div class="searchResult"><div class="stockContainer"><div class="stockTicker">${stock.ticker}</div><div class="companyName">${stock.full_company_name}</div><a href="../../../../../../stock/${stock.ticker}"></a></div></div>`;
            resultsList.innerHTML += sourceRes;
        });
    }
    if (context['sources'].length) {
        resultsList.innerHTML += `<div class="searchResultHeader">Sources</div>`;
        context['sources'].forEach((source) => {
            const sourceRes = `<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${source.favicon_path}"><span>${source.name}</span><a href="../../../../../../source/${source.slug}"></a></div>`;
            resultsList.innerHTML += sourceRes;
        });
    }
    if (context['articles'].length > 0) {
        resultsList.innerHTML += `<div class="searchResultHeader">Articles</div>`;
        for (let i = 0, j = context['articles'].length; i < j; i++) {
            let xfavicon = context['articles'][i].source.favicon_path;
            let xtitle = context['articles'][i].title;
            let xlink = context['articles'][i].link;
            const articleRes = `<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${xfavicon}"><span>${xtitle}</span><a href="${xlink}" target="_blank"></a></div>`;
            resultsList.innerHTML += articleRes;
        }
    }
}

function getScrollbarWidth() {
    // Creating invisible container
    const outer = document.createElement('div');
    outer.style.visibility = 'hidden';
    outer.style.overflow = 'scroll'; // forcing scrollbar to appear
    outer.style.msOverflowStyle = 'scrollbar'; // needed for WinJS apps
    document.body.appendChild(outer);
    // Creating inner element and placing it in the container
    const inner = document.createElement('div');
    outer.appendChild(inner);
    // Calculating difference between container's full width and the child width
    const scrollbarWidth = outer.offsetWidth - inner.offsetWidth;
    // Removing temporary elements from the DOM
    outer.parentNode.removeChild(outer);
    return scrollbarWidth;
}

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

function getFetchSettings(inputMethod, data = false) {
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

function showMessage(message, type) {
    document.querySelectorAll('.messages').forEach((message) => message.remove());
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
    if (document.querySelector('.horizontalNavigation').style.display == 'flex') {
        document.querySelector('.horizontalNavigation').style.display = 'none';
        const hamburgerSwitch = document.querySelector('.headerContainer .closeNavMenuButton');
        hamburgerSwitch.classList.replace('fa-times', 'fa-bars');
        hamburgerSwitch.classList.remove('closeNavMenuButton');
    }
}

function checkAreAllContainerClosed() {
    const addToListForms = document.querySelectorAll('.addToListForm');
    return Array.from(addToListForms).every(
        (form) => form.style.display === 'none' || !form.style.display
    );
}

function checkListStatus(saveButton) {
    const addListIds = [];
    const removeListIds = [];
    const inputList = saveButton
        .closest('.addSourceToListForm')
        .querySelectorAll('.listContainer input:first-of-type');
    const sourceId = document
        .querySelector('.fullScreenPlaceholder .addSourceToListForm')
        .id.replace('source_id', '');
    inputList.forEach((checkbox) => {
        const sourcesOriginallyInList = checkbox
            .closest('.listContainer')
            .querySelector('.sourcesInList').value;
        const isChecked = checkbox.checked;
        const listId = checkbox.id.split('id_list_')[1];
        const parsedSourcesOriginallyInList = JSON.parse(sourcesOriginallyInList);
        if (parsedSourcesOriginallyInList.includes(parseInt(sourceId)) && !isChecked) {
            removeListIds.push(listId);
        } else if (isChecked && !parsedSourcesOriginallyInList.includes(parseInt(sourceId))) {
            addListIds.push(listId);
        }
    });
    return [addListIds, removeListIds];
}

function modifyURLAfterTabSwitch(content_type) {
    const currentURL = window.location.href.split('?')[0];
    const modifiedURL = `${currentURL}?${content_type}=1#content`;
    window.history.replaceState({}, document.title, modifiedURL);
}

function changeNotificationTab(tab) {
    const notificationContent = document.querySelectorAll('.notificationsContainer');
    for (let i = 0, j = NOTIFICATION_TABS.length; i < j; i++) {
        NOTIFICATION_TABS[i].classList.remove('activeNotificationCategory');
        notificationContent[i].classList.remove('activeNotificationContainer');
    }
    NOTIFICATION_TABS[tab.dataset.forTab].classList.add('activeNotificationCategory');
    notificationContent[tab.dataset.forTab].classList.add('activeNotificationContainer');
}

function moveSourceSlider(target, handle) {
    const slider = target.closest('.sliderWrapper').querySelector('.slider');
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
}

function openSmallScreenSearchbar() {
    setModalStyle();
    closeAllPotentialOpenPopups();
    document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
    document.querySelector('.fullScreenPlaceholder .smallScreenSearchContainer').style.display =
        'block';
    const outerCloseButton = document.querySelector('.fullScreenPlaceholder .outerCloseButton');
    // without custom design close button would be overlapping
    outerCloseButton.classList.add('specialCloseButton');
    outerCloseButton.style.display = 'flex';
}

function smallScreenSearch(key) {
    let searchTerm = document.querySelector(
        '.smallScreenSearchContainer #mainAutocompleteSmallScreen'
    ).value;
    if (key == 'Enter' && searchTerm.split(/\s+/).join('') != '') {
        window.location.href = `../../../../../../search_results/${searchTerm}`;
    } else {
        const recommendedContainer = document.querySelector(
            '.smallScreenSearchContainer .recommendedContainer'
        );
        let results_list = document.querySelector(
            '.smallScreenSearchContainer .smallFormContentWrapper #mainAutocomplete_result'
        );
        if (searchTerm && searchTerm.split(/\s+/).join('') != '') {
            getSearchResults(searchTerm, results_list, true);
            document.querySelector('.smallScreenSearchContainer .noResultsFound').style.display =
                'none';
        } else {
            results_list.style.display = 'none';
            recommendedContainer.style.display = 'block';
            document.querySelector('.smallScreenSearchContainer .noResultsFound').style.display =
                'none';
        }
    }
}

function openSearchResultPage() {
    const search_term = document.querySelector('.mainInputSearch').value;
    if (search_term.split(/\s+/).join('') != '') {
        window.location.href = `../../../../../../search_results/${search_term}`;
    }
}

function searchWithAutocomplete(key) {
    let search_term = document.querySelector('header #mainAutocomplete').value;
    if (key == 'Enter' && search_term.split(/\s+/).join('') != '') {
        window.location.href = `../../../../../../search_results/${search_term}`;
    } else {
        let results_list = document.querySelector('header #mainAutocomplete_result');
        if (search_term && search_term.split(/\s+/).join('') != '') {
            clearTimeout(delayTimer);
            delayTimer = setTimeout(function () {
                // extra check necesseary to prevent deletion to trigger a search with last letter + search_term has value from 350msec ago
                if (document.querySelector('header #mainAutocomplete').value) {
                    getSearchResults(search_term, results_list);
                }
            }, 350); // Set a 350ms delay before sending the request
            document.onclick = function (e) {
                if (e.target.id !== 'autocomplete_list_results') {
                    results_list.style.display = 'none';
                }
            };
        } else {
            results_list.style.display = 'none';
        }
    }
}

function toggleDropdownUserMenu() {
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
}

function changeTab(tab, target) {
    const tabsContent = document.querySelectorAll('.tabsContent');
    for (let i = 0, j = TABS.length; i < j; i++) {
        TABS[i].classList.remove('activatedTab');
        tabsContent[i].classList.remove('tabsContentActive');
    }
    TABS[tab.dataset.forTab].classList.add('activatedTab');
    tabsContent[tab.dataset.forTab].classList.add('tabsContentActive');
    !['Sources', 'Stocks'].includes(target.innerText) &&
        modifyURLAfterTabSwitch(target.innerText.toLowerCase());
}

function createExplanationContainer(header, explanation) {
    document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
    document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display = 'block';
    document.querySelector('.fullScreenPlaceholder .explanationContainer h3').innerText = header;
    document.querySelector('.fullScreenPlaceholder .explanationContainer .explanation').innerText =
        explanation;
}

function showHighlightedStatus(action, highlighterButton, context) {
    if (action == 'highlight') {
        showMessage(context, 'Success');
        highlighterButton.innerHTML = `<i class="fas fa-times"></i><span>Unhighlight article</span>`;
    } else {
        showMessage(context, 'Remove');
        highlighterButton.innerHTML = `<i class="fas fa-highlighter"></i><span>Highlight article</span>`;
    }
}

function showSubscriptionStatus(subscribeButton) {
    if (subscribeButton.innerText == 'Subscribe') {
        subscribeButton.classList.add('subscribed');
        subscribeButton.classList.replace('finButtonWhite', 'finButtonBlue');
        subscribeButton.innerText = 'Subscribed';
        showMessage('SOURCE HAS BEEN SUBSCRIBED!', 'Success');
    } else {
        subscribeButton.classList.remove('subscribed');
        subscribeButton.classList.replace('finButtonBlue', 'finButtonWhite');
        subscribeButton.innerText = 'Subscribe';
        showMessage('SOURCE HAS BEEN UNSUBSCRIBED!', 'Remove');
    }
}

function setModalStyle() {
    const scrollbarWidth = getScrollbarWidth();
    document.querySelector('header').style.pointerEvents = 'none';
    document.querySelector('body').style.overflow = 'hidden';
    // prevents layout shift
    document.querySelector('body').style.paddingRight = scrollbarWidth + 'px';
    document.querySelector('.outerHeaderContainer').style.paddingRight = scrollbarWidth + 'px';
    document.querySelector('.fullScreenPlaceholder').style.display = 'block';
}

function removeModalStyle() {
    document.querySelector('header').style.removeProperty('pointer-events');
    document.querySelector('body').style.removeProperty('overflow');
    document.querySelector('.fullScreenPlaceholder').style.display = 'none';
    document.querySelector('body').style.removeProperty('padding-right');
    document.querySelector('.outerHeaderContainer').style.removeProperty('padding-right');
}

function saveArticleToListSelection(saveButton, articleId) {
    if (document.querySelector('.fullScreenPlaceholder .addToListForm').id.includes('article_id')) {
        const input_list = saveButton
            .closest('.addSourceToListForm')
            .querySelectorAll('.listContainer input:first-of-type');
        input_list.forEach((checkbox) => {
            const articlesOriginallyInList = checkbox
                .closest('.listContainer')
                .querySelector('.articlesInList').value;
            if (
                (JSON.parse(articlesOriginallyInList).includes(parseInt(articleId)) &&
                    !checkbox.checked) ||
                (checkbox.checked &&
                    !JSON.parse(articlesOriginallyInList).includes(parseInt(articleId)))
            ) {
                updateArticleStatusesInList(checkbox.id.split('id_list_')[1], articleId);
            }
        });
        showMessage('Lists have been updated!', 'Success');
        window.location.reload();
    }
}

function resetAddArticlesToListMenu(articleId) {
    const checkboxes = document.querySelectorAll(
        '.fullScreenPlaceholder .listContainer input:first-of-type'
    );
    checkboxes.forEach((checkbox) => {
        const articlesInList = checkbox
            .closest('.listContainer')
            .querySelector('.articlesInList').value;
        if (JSON.parse(articlesInList).includes(parseInt(articleId))) {
            checkbox.checked = true;
        } else {
            checkbox.checked = false;
        }
    });
}

function openAddArticleToListMenu(e) {
    document.querySelector('.fullScreenPlaceholder .smallScreenSearchContainer').style.display =
        'none';
    document.querySelector('.fullScreenPlaceholder .outerCloseButton').style.display = 'none';
    const articleId = e.target.closest('.articleContainer').id.split('#')[1];
    resetAddArticlesToListMenu(articleId);
    const articleName = e.target
        .closest('.articleContainer')
        .querySelector('.contentBody p')?.innerText;
    articleName
        ? (document.querySelector('.fullScreenPlaceholder .addToListForm h3 span').innerText =
              articleName)
        : (document.querySelector('.fullScreenPlaceholder .addToListForm h3 span').innerText =
              'Retweet/Reply');
    setModalStyle();
    document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
    document.querySelector('.fullScreenPlaceholder .addToListForm').id = 'article_id' + articleId;
    document.querySelector('.fullScreenPlaceholder .addToListForm').style.display = 'block';
    const saveButton = document.querySelector(
        '.fullScreenPlaceholder .addSourceToListForm .saveButton'
    );
    saveButton.addEventListener('click', () => saveArticleToListSelection(saveButton, articleId), {
        once: true,
    });
    document
        .querySelector('.fullScreenPlaceholder .addSourceToListForm .cancelButton')
        ?.addEventListener('click', () => resetAddArticlesToListMenu(articleId));
}

function resetAddSourceToListsForm(sourceId) {
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
}

function openAddSourceToListsForm(addSourceButton) {
    setModalStyle();
    const sourceId = addSourceButton.closest('.contentWrapper').id.split('#')[1];
    const sourceName = addSourceButton
        .closest('.contentWrapper')
        .querySelector('.nameContainer span').innerText;
    document.querySelector('.fullScreenPlaceholder .addToListForm h3 span').innerText = sourceName;
    document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
    document.querySelector('.fullScreenPlaceholder .addSourceToListForm').style.display = 'block';
    document.querySelector('.fullScreenPlaceholder .addSourceToListForm').id =
        'source_id' + sourceId;
    resetAddSourceToListsForm(sourceId);
    document
        .querySelector('.fullScreenPlaceholder .addSourceToListForm .cancelButton')
        ?.addEventListener('click', () => resetAddSourceToListsForm(sourceId));
}

function closeAddSourceToListsForm() {
    removeModalStyle();
    document.querySelector('.addSourceToListForm').style.display = 'none';
    document.querySelector('.fullScreenPlaceholder').style.display = 'none';
}

function getAuthPromptMessage(button) {
    if (button.classList.contains('ap1')) {
        return 'Add Sources To Your Lists';
    } else if (button.classList.contains('ap2')) {
        return 'Subscribe To Sources';
    } else if (button.classList.contains('ap3')) {
        return 'Create Notifications';
    } else if (button.classList.contains('ap4')) {
        return 'Add Stocks To Your Portfolios';
    } else if (button.classList.contains('ap6')) {
        return 'Add Content To Your Lists';
    } else if (button.classList.contains('ap7')) {
        return 'Rate This Source';
    }
}

function openAuthPrompt(promptButton) {
    const fullScreenPlaceholder = document.querySelector('.fullScreenPlaceholder');
    document.querySelector('.fullScreenPlaceholder .authPromptContainer').style.display = 'block';
    fullScreenPlaceholder.style.display = 'flex';
    const promptMsg = getAuthPromptMessage(promptButton);
    document.querySelector('.fullScreenPlaceholder .authPromptContainer h3').innerText = promptMsg;
    setModalStyle();
}

function openImageFullscreenMode(tweetImage) {
    setModalStyle();
    const fullScreenPlaceholder = document.querySelector('.fullScreenPlaceholder');
    fullScreenPlaceholder.style.display = 'flex';
    const img = document.createElement('img');
    img.classList.add('fullScreenImage');
    img.src = tweetImage.src;
    fullScreenPlaceholder.appendChild(img);
    fullScreenPlaceholder.querySelector('.outerCloseButton').style.display = 'flex';
    document.onclick = (e) => e.target.nodeName !== 'IMG' && closeImageFullscreenMode();
}

function closeImageFullscreenMode() {
    removeModalStyle();
    document.querySelector('.fullScreenPlaceholder').style.display = 'none';
    document.querySelector('.fullScreenPlaceholder .smallScreenSearchContainer').style.display =
        'none';
    document.querySelector('.fullScreenPlaceholder .fullScreenImage')?.remove();
    document.querySelector('.fullScreenPlaceholder .outerCloseButton').style.display = 'none';
}

function closeAuthPrompt() {
    document.querySelector('.fullScreenPlaceholder .authPromptContainer').style.display = 'none';
    document.querySelector('.fullScreenPlaceholder').style.display = 'none';
    removeModalStyle();
}

function closeNotificationKeywordExplanation() {
    removeModalStyle();
    document.querySelector('.fullScreenPlaceholder').style.display = 'none';
    document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display = 'none';
}

function openNotificationKeywordExplanation() {
    closeAllPotentialOpenPopups();
    setModalStyle();
    createExplanationContainer(
        'Keywords',
        "If you want to stay up-to-date on a particular topic, just add a keyword and I'll make sure you're notified as soon as any of your sources publish content containing that keyword on FinBrowser."
    );
    document
        .querySelector('.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times')
        .addEventListener('click', () => closeNotificationKeywordExplanation());
}

function toggleNotificationSideMenu() {
    if (
        document.querySelector('.fullScreenPlaceholder .smallScreenSearchContainer').style
            .display == 'block'
    ) {
        document.querySelector('.fullScreenPlaceholder').style.display = 'none';
        document.querySelector('.fullScreenPlaceholder .smallScreenSearchContainer').style.display =
            'none';
        document.querySelector('.fullScreenPlaceholder .outerCloseButton').style.display = 'none';
        removeModalStyle();
    }
    const notificationPopup = document.querySelector('.notificationPopupWrapper');
    if (notificationPopup.style.display == 'block') {
        notificationPopup.style.display = 'none';
        document.querySelector('.unseenNotifications')?.remove();
        document.querySelectorAll('.unseenNotification').forEach((notification) => {
            notification.classList.remove('unseenNotification');
        });
    } else {
        notificationPopup.style.display = 'block';
        updateNotificationSeenStatus();
    }
}

function openContentOptionsMenu(e, ellipsis) {
    const { classList, parentElement } = ellipsis;
    const { style } = parentElement.querySelector('.articleOptionsContainer');
    if (!classList.contains('openAuthPrompt')) {
        const allContainersClosed = checkAreAllContainerClosed();
        if (allContainersClosed) {
            if (previousOptionsContainer && e.target !== previousEllipsis) {
                previousOptionsContainer.style.display = 'none';
            }
            const articleOptionsContainer = parentElement.querySelector('.articleOptionsContainer');
            style.display = style.display !== 'flex' ? 'flex' : 'none';
            document.onclick = (e) => {
                if (e.target !== ellipsis) {
                    parentElement.querySelector('.articleOptionsContainer').style.display = 'none';
                }
            };
            previousOptionsContainer = articleOptionsContainer;
            previousEllipsis = ellipsis;
        }
    }
}

function toggleHamburgerMenu(target) {
    const isBars = target.classList.contains('fa-bars');
    target.classList.replace(isBars ? 'fa-bars' : 'fa-times', isBars ? 'fa-times' : 'fa-bars');
    target.classList.toggle('closeNavMenuButton');
    const horizontalNavigation = document.querySelector('.horizontalNavigation');
    horizontalNavigation.style.display =
        horizontalNavigation.style.display === 'flex' ? 'none' : 'flex';
}

/**************************************************************
    3. Other
**************************************************************/

let previousOptionsContainer;
let previousEllipsis;

const NOTIFICATION_TABS = document.querySelectorAll('.notificationHeadersContainer button');
const TABS = document.querySelectorAll('.tabsContainer button');

let delayTimer;

document.querySelectorAll('input').forEach((input) => input.setAttribute('autocomplete', 'off'));

/**************************************************************
    4. EventListener
**************************************************************/

document
    .querySelector('header #mainAutocomplete')
    .addEventListener('keyup', (e) => searchWithAutocomplete(e.key));

document
    .querySelector('header .smallScreenSearchIcon')
    .addEventListener('click', () => openSmallScreenSearchbar());

document
    .querySelector('.smallScreenSearchContainer #mainAutocompleteSmallScreen')
    .addEventListener('keyup', (e) => smallScreenSearch(e.key));

document
    .querySelector('.mainSearchContainer i')
    .addEventListener('click', () => openSearchResultPage());

// workaround to trigger logout button
document
    .querySelector('.headerContainer .profileMenu .profileMenuOption:last-of-type')
    ?.addEventListener('click', (e) => e.target.querySelector('button').click());

document
    .querySelectorAll('.contentInfoContainer .fa-ellipsis-h')
    .forEach((ellipsis) =>
        ellipsis.addEventListener('click', (e) => openContentOptionsMenu(e, ellipsis))
    );

document
    .querySelectorAll('.addToHighlightedButton')
    .forEach((highlighterButton) =>
        highlighterButton.addEventListener('click', () =>
            changeHighlightedStatus(highlighterButton)
        )
    );

document
    .querySelector('.userSpace .notificationBell')
    ?.addEventListener('click', () => toggleNotificationSideMenu());

NOTIFICATION_TABS.forEach((tab) => tab.addEventListener('click', () => changeNotificationTab(tab)));

document
    .querySelectorAll('.handle')
    .forEach((handle) =>
        handle.addEventListener('click', (e) => moveSourceSlider(e.target, handle))
    );

document.querySelectorAll('.sliderWrapper .slider .subscribeButton').forEach((subscribeButton) => {
    subscribeButton.addEventListener('click', () => subscribeToSource(subscribeButton));
});

// open create keyword notification menu
document
    .querySelector('.notificationPopupWrapper .addKeywordsContainer button')
    ?.addEventListener(
        'click',
        () =>
            (document.querySelector(
                '.notificationPopupWrapper .createKeywordNotificationModal'
            ).style.display = 'flex')
    );

// close keyword notification menu
document
    .querySelector('.notificationPopupWrapper .createKeywordNotificationModal .discardButton')
    ?.addEventListener(
        'click',
        () =>
            (document.querySelector(
                '.notificationPopupWrapper .createKeywordNotificationModal'
            ).style.display = 'none')
    );

document
    .querySelector('.notificationPopupWrapper .createKeywordNotificationModal .saveButton')
    ?.addEventListener('click', () => saveKeyword());

document
    .querySelector('.notificationPopupWrapper .createKeywordNotificationModal input')
    ?.addEventListener('keypress', (e) => {
        e.key === 'Enter' && saveKeyword();
    });

document
    .querySelectorAll('.openAuthPrompt')
    .forEach((promptButton) =>
        promptButton.addEventListener('click', () => openAuthPrompt(promptButton))
    );

document
    .querySelector('.fullScreenPlaceholder .authPromptContainer .fa-times')
    .addEventListener('click', () => closeAuthPrompt());

document.querySelectorAll('.sourceAddToListButton').forEach((addSourceButton) => {
    if (
        !addSourceButton.classList.contains('openAuthPrompt') &&
        addSourceButton.closest('.contentWrapper')
    ) {
        addSourceButton.addEventListener('click', () => openAddSourceToListsForm(addSourceButton));
    }
});

document
    .querySelectorAll('.fullScreenPlaceholder .addSourceToListForm .fa-times')
    .forEach((closeAddSourceFormButton) =>
        closeAddSourceFormButton.addEventListener('click', () => closeAddSourceToListsForm())
    );

document
    .querySelectorAll('.fullScreenPlaceholder .addSourceToListForm .saveButton')
    .forEach((saveButton) =>
        saveButton.addEventListener('click', () => saveSourceListsStatus(saveButton), {
            once: true,
        })
    );

document
    .querySelectorAll('.addToListButton')
    .forEach((element) => element.addEventListener('click', (e) => openAddArticleToListMenu(e)));

// check input checkbox on click on list container
document
    .querySelectorAll('.addToListForm .listSelectionContainer .listContainer')
    .forEach((listContainer) =>
        listContainer.addEventListener('click', () => {
            listContainer.querySelector('input:first-of-type').checked =
                !listContainer.querySelector('input:first-of-type').checked;
        })
    );

document
    .querySelector('.notificationPopupWrapper .createKeywordNotificationModal .infoLink i')
    ?.addEventListener('click', () => openNotificationKeywordExplanation());

document
    .querySelectorAll('.tweetImage')
    .forEach((tweetImage) =>
        tweetImage.addEventListener('click', () => openImageFullscreenMode(tweetImage))
    );

document
    .querySelector('.fullScreenPlaceholder .outerCloseButton')
    .addEventListener('click', (e) => {
        e.target.classList.contains('specialCloseButton') &&
            e.target.classList.remove('specialCloseButton');
        closeImageFullscreenMode();
    });

document
    .querySelector('.headerContainer .fa-bars')
    .addEventListener('click', (e) => toggleHamburgerMenu(e.target));

document.querySelector('.userProfile')?.addEventListener('click', () => toggleDropdownUserMenu());

TABS.forEach((tab) => tab.addEventListener('click', (e) => changeTab(tab, e.target)));
