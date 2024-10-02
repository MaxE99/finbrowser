/**************************************************************
    1. API Calls
**************************************************************/

async function editPortfolio() {
    const newName = document.querySelector('.editMenu .portfolioNameContainer input').value;
    const isMainPortfolio = document.querySelector(
        '.editMenu .mainPortfolioContainer input'
    ).checked;
    const data = { name: newName, main: isMainPortfolio };
    if (newName.trim().length) {
        try {
            const res = await fetch(`../../api/portfolios/${PORTFOLIO_ID}/`, {
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
                showMessage('Portfolio has been updated!', 'Success');
                window.location.reload();
            }
        } catch (e) {
            showMessage('Error: Unexpected error has occurred!', 'Error');
        }
    } else {
        showMessage('Please enter a name!', 'Error');
    }
}

async function createPortfolio() {
    try {
        const res = await fetch(`../../api/portfolios/`, getFetchSettings('POST'));
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            window.location.replace(`../../portfolio/${context.portfolio_id}`);
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function deletePortfolio() {
    try {
        const res = await fetch(
            `../../api/portfolios/${PORTFOLIO_ID}/`,
            getFetchSettings('DELETE')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            showMessage('Portfolio has been deleted!', 'Remove');
            document
                .querySelectorAll('.portfolioOptionsContainer .portfolioOption')
                .forEach((portfolioOption) => {
                    const portfolioOptionId = portfolioOption.id.replace('wlist', '');
                    if (portfolioOptionId !== PORTFOLIO_ID) {
                        window.location.replace(`../../portfolio/${portfolioOptionId}`);
                    }
                });
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function createPortfolioKeyword(element) {
    const newKeyword = document.querySelector('.keywordModal .inputContainer input').value;
    const pstockId = document
        .querySelector('.keywordModal .keywordHeader span')
        .id.replace('psi', '');
    if (newKeyword.trim().length > 2 && !isKeywordBeingCreated) {
        isKeywordBeingCreated = true;
        try {
            const data = { keyword: newKeyword, pstock_id: pstockId };
            const res = await fetch(`../../api/portfolio_keywords/`, {
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
                    isKeywordBeingCreated = false;
                } else {
                    showMessage('Error: Network request failed unexpectedly!', 'Error');
                }
            } else {
                const context = await res.json();
                showNewPortfolioKeywords(context, element, pstockId);
            }
        } catch (e) {
            showMessage('Error: Unexpected error has occurred!', 'Error');
        }
    } else {
        showMessage('A keyword must have at least 3 letters!', 'Error');
    }
}

async function deletePortfolioKeywords(e, keywordButton = false) {
    const pkeywordId = e.target.closest('.keywordContainer').id.replace('wkw', '');
    try {
        const res = await fetch(
            `../../api/portfolio_keywords/${pkeywordId}/`,
            getFetchSettings('DELETE')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            e.target.closest('.keywordContainer').remove();
            showMessage('Keyword has been removed!', 'Remove');
            if (keywordButton) {
                keywordButton.innerText -= 1;
            } else {
                const pstockId = document
                    .querySelector('.keywordModal .keywordHeader span')
                    .id.replace('psi', '');
                document.querySelectorAll('table tr').forEach((tr) => {
                    if (tr.id == `pstock${pstockId}`) {
                        tr.querySelector('td .keywordButton').innerText =
                            parseInt(tr.querySelector('td .keywordButton').innerText) - 1;
                    }
                });
            }
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function getPortfolioKeywords(pstockId, keywordButton) {
    try {
        const res = await fetch(`../../api/portfolio_stocks/${pstockId}/`, getFetchSettings('GET'));
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            showPortfolioKeywords(context, keywordButton);
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function addStocksToPortfolio() {
    if (!selectedStocks.length) {
        showMessage('You Need To Select Stocks!', 'Error');
    }
    if (selectedStocks.length && !areNewStocksBeingAdded) {
        areNewStocksBeingAdded = true;
        try {
            const data = { stocks: selectedStocks, portfolio: PORTFOLIO_ID };
            const res = await fetch(`../../api/portfolio_stocks/`, {
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
                    showMessage(
                        'Maximum limit of 100 stocks and keywords per portfolio has been reached.',
                        'Error'
                    );
                    areNewStocksBeingAdded = false;
                } else {
                    showMessage('Error: Network request failed unexpectedly!', 'Error');
                }
            } else {
                showMessage('Portfolio has been updated!', 'Success');
                window.location.reload();
            }
        } catch (e) {
            showMessage('Error: Unexpected error has occurred!', 'Error');
        }
    }
}

async function removeStockFromPortfolio(target) {
    const pstockId = target.closest('.stockContainer').id.replace('pstock', '');
    try {
        const res = await fetch(
            `../../api/portfolio_stocks/${pstockId}/`,
            getFetchSettings('DELETE')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            showMessage('Stock has been removed!', 'Remove');
            target.closest('.stockContainer').remove();
            if (!document.querySelector('table .stockContainer')) {
                window.location.reload();
            }
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function addSourceToBlacklist(source, resultsList, selectedList) {
    try {
        const data = { source_id: source.source_id };
        const res = await fetch(`../../api/portfolios/${PORTFOLIO_ID}/`, {
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
            showNewBlacklistedSources(resultsList, selectedList, source);
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function removeSourceFromBlacklist(button) {
    const sourceId = button.closest('.blacklistedSourceContainer').id.split('#')[1];
    try {
        const data = { source_id: sourceId };
        const res = await fetch(`../../api/portfolios/${PORTFOLIO_ID}/`, {
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
            button.closest('.blacklistedSourceContainer').remove();
            blacklistedSources = blacklistedSources.filter((source) => source !== sourceId);
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function searchForNotBlacklistedSources(searchTerm, resultsList, selectedList) {
    try {
        const res = await fetch(
            `../../api/sources/?blacklist_search=${searchTerm}&portfolio_id=${PORTFOLIO_ID}`,
            getFetchSettings('GET')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            showBlacklistSearchResults(resultsList, selectedList, context);
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function searchForNewPortfolioStocks(
    searchTerm,
    resultsList,
    portfolioStocks,
    selectedList,
    textInput
) {
    try {
        const res = await fetch(
            `../../api/stocks/?search_term=${searchTerm}`,
            getFetchSettings('GET')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            showPortfolioStocksSearchResults(
                resultsList,
                context,
                portfolioStocks,
                selectedList,
                textInput
            );
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

/**************************************************************
    2. Functions
**************************************************************/

function changePortfolio() {
    const dropdownSymbol = document.querySelector('.firstRow .nameContainer i');
    const portfolioOptionsContainer = document.querySelector('.portfolioOptionsContainer');
    const isDisplayed = portfolioOptionsContainer.style.display === 'block';
    portfolioOptionsContainer.style.display = isDisplayed ? 'none' : 'block';
    dropdownSymbol.classList.toggle('fa-chevron-up', !isDisplayed);
    dropdownSymbol.classList.toggle('fa-chevron-down', isDisplayed);
}

function sortKeywords(arr) {
    arr.sort((a, b) => a.keyword.toUpperCase().localeCompare(b.keyword.toUpperCase()));
    return arr;
}

function openEditPortfolioMenu() {
    document.querySelector('.portfolioMenuWrapper').style.display = 'block';
    document.querySelector('.editMenu').style.display = 'block';
    setModalStyle();
}

function closeEditPortfolioMenu() {
    document.querySelector('.portfolioMenuWrapper').style.display = 'none';
    document.querySelector('.editMenu').style.display = 'none';
    removeModalStyle();
}

function openPortfolioKeywordsMenu(keywordButton) {
    setModalStyle();
    document.querySelector('.portfolioMenuWrapper').style.display = 'block';
    document.querySelector('.portfolioMenuWrapper .keywordModal').style.display = 'block';
    const pstockId = keywordButton.closest('tr').id.replace('pstock', '');
    document.querySelector('.keywordHeader span').innerText = keywordButton
        .closest('tr')
        .querySelector('.ticker').innerText;
    document.querySelector('.keywordHeader span').id = 'psi' + pstockId;
    getPortfolioKeywords(pstockId, keywordButton);
}

function closePortfolioKeywordsMenu() {
    removeModalStyle();
    document.querySelector('.portfolioMenuWrapper').style.display = 'none';
    document.querySelector('.portfolioMenuWrapper .keywordModal').style.display = 'none';
}

function openPortfolioKeywordExplanation(target) {
    document.querySelector('.portfolioMenuWrapper').style.display = 'none';
    target.closest('.keywordModal').style.display = 'none';
    createExplanationContainer(
        'Keywords',
        "FinBrowser finds content related to the stocks in your portfolio based on their ticker symbol and company name. If you want to see content that focuses on a specific product or segment within a company, you can enter a keyword here and the results for that keyword will be displayed as well. For instance, let's say you hold Amazon stock and you want to see more information about their cloud computing platform, AWS. Simply enter AWS as your keyword and you'll get all the relevant results. It's that easy!"
    );
    document
        .querySelector('.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times')
        .addEventListener('click', () => closePortfolioKeywordExplanation(target), {
            once: true,
        });
}

function closePortfolioKeywordExplanation(target) {
    document.querySelector('.portfolioMenuWrapper').style.display = 'block';
    target.closest('.keywordModal').style.display = 'block';
    document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display = 'none';
}

function openBlacklistExplanation() {
    document.querySelector('.portfolioMenuWrapper').style.display = 'none';
    document.querySelector('.portfolioMenuWrapper .editMenu').style.display = 'none';
    createExplanationContainer(
        'Blacklist Sources',
        "If you're seeing content from sources that you don't find helpful or relevant, you can easily remove them from your feed by adding them to your blacklisted sources. By doing so, you'll no longer see content from those sources and can focus on the ones that are most helpful to you."
    );
    document
        .querySelector('.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times')
        .addEventListener('click', () => closeBlacklistExplanation(), { once: true });
}

function closeBlacklistExplanation() {
    document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display = 'none';
    document.querySelector('.portfolioMenuWrapper').style.display = 'flex';
    document.querySelector('.portfolioMenuWrapper .editMenu').style.display = 'block';
}

function openPortfolioDeletionWarning() {
    document.querySelector('.portfolioMenuWrapper').style.display = 'none';
    document.querySelector('.editMenu').style.display = 'none';
    document.querySelector('.portfolioMenuWrapper').style.display = 'block';
    document.querySelector('.portfolioMenuWrapper .warningMessageContainer').style.display = 'flex';
    document
        .querySelector('.portfolioMenuWrapper .warningMessageContainer .discardButton')
        .addEventListener('click', () => closePortfolioDeletionWarning());
}

function closePortfolioDeletionWarning() {
    removeModalStyle();
    document.querySelector('.portfolioMenuWrapper').style.display = 'none';
    document.querySelector('.portfolioMenuWrapper .warningMessageContainer').style.display = 'none';
}

function openMainPortfolioExplanation() {
    document.querySelector('.portfolioMenuWrapper').style.display = 'none';
    document.querySelector('.portfolioMenuWrapper .editMenu').style.display = 'none';
    createExplanationContainer(
        'Main Portfolio',
        "Your main portfolio is the one that opens up whenever you click on the Portfolio button in the header. It's important to note that you always need to have at least one main portfolio. If you only have one portfolio, then you won't be able to delete it as it is your main one. But, if you have multiple portfolios and you delete your main one, then the next portfolio in alphabetical order will become your new main portfolio. Don't worry though, you can easily change your main portfolio by opening the edit menu of a portfolio that is currently not your main one and setting it as your new main portfolio. It's as simple as that!"
    );
    document
        .querySelector('.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times')
        .addEventListener('click', () => closeBlacklistExplanation(), { once: true });
}

function closeAddStocksToPortfolioMenu() {
    document.querySelector('.portfolioMenuWrapper').style.display = 'none';
    document.querySelector('.addStocksContainer').style.display = 'none';
    removeModalStyle();
}

function startPortfolioDeletionProcess() {
    if (document.querySelectorAll('.portfoliosContainer .portfolioOption').length === 1) {
        showMessage('You are not allowed to delete your last portfolio!', 'Error');
    } else {
        openPortfolioDeletionWarning();
        document
            .querySelector('.portfolioMenuWrapper .warningMessageContainer .confirmButton')
            .addEventListener('click', () => deletePortfolio(), { once: true });
    }
}

function showNewBlacklistedSources(resultsList, selectedList, source) {
    document.querySelector('.blacklistSourceContainer #textInput').value = '';
    resultsList.style.display = 'none';
    selectedList.style.display = 'block';
    blacklistedSources.push(source.source_id);
    const blacklistedSourceContainer = document.createElement('div');
    blacklistedSourceContainer.classList.add('blacklistedSourceContainer');
    blacklistedSourceContainer.id = `blsid#${source.source_id}`;
    const img = document.createElement('img');
    img.src = `${ENV.S3_BUCKET}/${source.favicon_path}`;
    const span = document.createElement('span');
    span.innerText = source.name;
    const timesButton = document.createElement('i');
    timesButton.classList.add('fas', 'fa-times');
    timesButton.addEventListener('click', () =>
        removeSourceFromBlacklist(blacklistedSourceContainer)
    );
    blacklistedSourceContainer.append(img, span, timesButton);
    selectedList.appendChild(blacklistedSourceContainer);
}

function showBlacklistSearchResults(resultsList, selectedList, context) {
    resultsList.innerHTML = '';
    const resultHeader = document.createElement('div');
    resultHeader.innerText = 'Results:';
    resultsList.append(resultHeader);
    if (context.length > 0) {
        context.forEach((source) => {
            if (!blacklistedSources.includes(source.source_id)) {
                const searchResult = document.createElement('div');
                searchResult.classList.add('searchResult');
                const resultImage = document.createElement('img');
                resultImage.src = `${ENV.S3_BUCKET}/${source.favicon_path}`;
                const sourceName = document.createElement('span');
                sourceName.innerText = source.name;
                sourceName.id = `source_id_${source.source_id}`;
                searchResult.append(resultImage, sourceName);
                resultsList.appendChild(searchResult);
                searchResult.addEventListener('click', () =>
                    addSourceToBlacklist(source, resultsList, selectedList)
                );
            }
        });
    }
}

function showPortfolioStocksSearchResults(
    resultsList,
    context,
    portfolioStocks,
    selectedList,
    textInput
) {
    resultsList.innerHTML = '';
    const resultHeader = document.createElement('div');
    resultHeader.classList.add('resultHeader');
    resultHeader.innerText = 'Results:';
    resultsList.append(resultHeader);
    if (context.length > 0) {
        context.forEach((stock) => {
            if (
                !selectedStocks.includes(stock.stock_id) &&
                !portfolioStocks.includes(stock.ticker)
            ) {
                const searchResult = document.createElement('div');
                searchResult.classList.add('searchResult');
                const stockContainer = document.createElement('div');
                stockContainer.classList.add('stockContainer');
                const ticker = document.createElement('div');
                ticker.innerText = stock.ticker;
                ticker.id = 'pssi#' + stock.stock_id;
                ticker.classList.add('stockTicker');
                const companyName = document.createElement('div');
                companyName.innerText = stock.full_company_name;
                companyName.classList.add('companyName');
                stockContainer.append(ticker, companyName);
                searchResult.appendChild(stockContainer);
                resultsList.appendChild(searchResult);
                searchResult.addEventListener('click', function addSelectedStock() {
                    // Remove the listener from the element the first time the listener is run:
                    searchResult.removeEventListener('click', addSelectedStock);
                    selectedStocks.push(stock.stock_id);
                    const removeStockButton = document.createElement('i');
                    removeStockButton.classList.add('fas', 'fa-times');
                    removeStockButton.addEventListener('click', () => {
                        removeStockButton.parentElement.remove();
                        selectedStocks = selectedStocks.filter(function (e) {
                            return (
                                e.toString() !==
                                removeStockButton
                                    .closest('.searchResult')
                                    .querySelector('.stockTicker')
                                    .id.split('#')[1]
                            );
                        });
                    });
                    searchResult.appendChild(removeStockButton);
                    selectedList.appendChild(searchResult);
                    resultsList.style.display = 'none';
                    selectedList.style.display = 'block';
                    textInput.value = '';
                });
            }
        });
    }
}

function resetAddStocksToPortfolioMenu(selectedList) {
    selectedStocks = [];
    selectedList.innerHTML = '';
}

function openAddStocksToPortfolioMenu() {
    document.querySelector('.portfolioMenuWrapper').style.display = 'block';
    document.querySelector('.addStocksContainer').style.display = 'block';
    setModalStyle();
    document
        .querySelector('.addStocksContainer #addStocks')
        .addEventListener('keyup', function (e) {
            const portfolioStocks = [];
            const tickerContainer = document.querySelectorAll('table tr .ticker');
            for (let i = 0, j = tickerContainer.length; i < j; i++) {
                portfolioStocks.push(tickerContainer[i].innerText);
            }
            const textInput = document.querySelector('.addStocksContainer #addStocks');
            let searchTerm = textInput.value;
            let resultsList = e.target
                .closest('.addStocksContainer')
                .querySelector('#searchResultsContainer');
            let selectedList = e.target
                .closest('.addStocksContainer')
                .querySelector('.selectionContainer');
            document
                .querySelector('.addStocksContainer .buttonContainer .cancelButton')
                .addEventListener('click', () => resetAddStocksToPortfolioMenu(selectedList));
            const isSearchTermValid = searchTerm?.split(/\s+/).join('') !== '';
            resultsList.style.display = isSearchTermValid ? 'block' : 'none';
            selectedList.style.display = isSearchTermValid ? 'none' : 'block';
            isSearchTermValid &&
                searchForNewPortfolioStocks(
                    searchTerm,
                    resultsList,
                    portfolioStocks,
                    selectedList,
                    textInput
                );
        });
}

function showNewPortfolioKeywords(context, element, pstockId) {
    const keywordContainer = document.createElement('div');
    keywordContainer.classList.add('keywordContainer');
    keywordContainer.id = `wkw${context.pkeyword_id}`;
    const keywordSpan = document.createElement('span');
    keywordSpan.innerText = context.keyword;
    const trashButton = document.createElement('i');
    trashButton.addEventListener('click', (e) => deletePortfolioKeywords(e));
    trashButton.classList.add('fas', 'fa-times');
    keywordContainer.append(keywordSpan, trashButton);
    element
        .closest('.keywordModal')
        .querySelector('.keywordsContainer')
        .appendChild(keywordContainer);
    element.closest('.keywordModal').querySelector('.inputContainer input').value = '';
    isKeywordBeingCreated = false;
    showMessage('Keyword has been added!', 'Success');
    document.querySelectorAll('table tr').forEach((tr) => {
        if (tr.id == `pstock${pstockId}`) {
            tr.querySelector('td .keywordButton').innerText =
                parseInt(tr.querySelector('td .keywordButton').innerText) + 1;
        }
    });
}

function showPortfolioKeywords(context, keywordButton) {
    const portfolioKeywords = sortKeywords(context.keywords);
    const keywordsContainer = document.querySelector(
        '.portfolioMenuWrapper .keywordModal .keywordsContainer'
    );
    keywordsContainer.innerHTML = '';
    portfolioKeywords.forEach((keyword) => {
        const keywordContainer = document.createElement('div');
        keywordContainer.classList.add('keywordContainer');
        keywordContainer.id = 'wkw' + keyword.pkeyword_id;
        const span = document.createElement('span');
        span.innerText = keyword.keyword;
        const removeButton = document.createElement('i');
        removeButton.addEventListener('click', (e) => deletePortfolioKeywords(e, keywordButton));
        removeButton.classList.add('fas', 'fa-times');
        keywordContainer.append(span, removeButton);
        keywordsContainer.appendChild(keywordContainer);
    });
}

function startBlacklistSearchProcess() {
    let searchTerm = document.querySelector('.blacklistSourceContainer #textInput').value;
    let resultsList = document.querySelector('.blacklistSourceContainer #searchResultsContainer');
    let selectedList = document.querySelector('.blacklistSourceContainer .selectionContainer');
    const isSearchTermValid = searchTerm && searchTerm.split(/\s+/).join('') !== '';
    resultsList.style.display = isSearchTermValid ? 'block' : 'none';
    selectedList.style.display = isSearchTermValid ? 'none' : 'block';
    isSearchTermValid && searchForNotBlacklistedSources(searchTerm, resultsList, selectedList);
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

let selectedStocks = [];

let isKeywordBeingCreated = false;

let areNewStocksBeingAdded = false;

let blacklistedSources = [];

document
    .querySelectorAll('.blacklistSourceContainer .blacklistedSourceContainer')
    .forEach((blacklistedSource) => blacklistedSources.push(blacklistedSource.id.split('#')[1]));

const PORTFOLIO_ID = document.querySelector('.firstRow .nameContainer h2').id;

/**************************************************************
    4. EventListener
**************************************************************/

document
    .querySelector('.firstRow .nameContainer')
    .addEventListener('click', () => changePortfolio());

document
    .querySelector('.createPortfolioButton')
    .addEventListener('click', () => createPortfolio(), { once: true });

document
    .querySelector('.actionButtonContainer .addStocksButton')
    .addEventListener('click', () => openAddStocksToPortfolioMenu());

document
    .querySelectorAll('.emptyInformationContainer button')
    .forEach((addStocksButton) =>
        addStocksButton.addEventListener('click', () => openAddStocksToPortfolioMenu())
    );

document
    .querySelector('.addStocksContainer .closeAddStockContainer')
    .addEventListener('click', () => closeAddStocksToPortfolioMenu());

document
    .querySelector('.editPortfolioButton')
    .addEventListener('click', () => openEditPortfolioMenu());

document
    .querySelector('.editMenu .fa-times')
    .addEventListener('click', () => closeEditPortfolioMenu());

document
    .querySelector('.portfolioMenuWrapper .addStocksContainer .addStocksButton')
    .addEventListener('click', () => addStocksToPortfolio());

document
    .querySelectorAll('.blacklistSourceContainer .blacklistedSourceContainer .fa-times')
    .forEach((button) => button.addEventListener('click', () => removeSourceFromBlacklist(button)));

document
    .querySelectorAll('.stockContainer td .keywordButton')
    .forEach((keywordButton) =>
        keywordButton.addEventListener('click', () => openPortfolioKeywordsMenu(keywordButton))
    );

document
    .querySelectorAll('.keywordModal .addButton')
    .forEach((addButton) =>
        addButton.addEventListener('click', (e) => createPortfolioKeyword(e.target))
    );

document.querySelectorAll('.keywordModal .createKeywordsContainer input').forEach((keywordInput) =>
    keywordInput.addEventListener('keypress', function (event) {
        event.key === 'Enter' && createPortfolioKeyword(keywordInput);
    })
);

document
    .querySelector('.portfolioMenuWrapper .keywordModal .keywordHeader .fa-times')
    .addEventListener('click', () => closePortfolioKeywordsMenu());

document
    .querySelector('.portfolioMenuWrapper .keywordModal .createKeywordsContainer .infoLink i')
    .addEventListener('click', (e) => openPortfolioKeywordExplanation(e.target));

document
    .querySelector('.portfolioMenuWrapper .editMenu .blacklistSourceContainer .header .infoLink i')
    .addEventListener('click', () => openBlacklistExplanation());

document
    .querySelector('.portfolioMenuWrapper .editMenu .mainPortfolioContainer .infoLink i')
    .addEventListener('click', () => openMainPortfolioExplanation());

document
    .querySelector('.blacklistSourceContainer #textInput')
    .addEventListener('keyup', () => startBlacklistSearchProcess());

document
    .querySelector('.editMenu .deletePortfolioButton')
    .addEventListener('click', () => startPortfolioDeletionProcess());

document.querySelectorAll('.stockContainer .fa-trash-can').forEach((removeButton) => {
    removeButton.addEventListener('click', (e) => removeStockFromPortfolio(e.target));
});

document
    .querySelector('.menuContainer .editMenu .saveEditsButton')
    .addEventListener('click', () => editPortfolio(), { once: true });
