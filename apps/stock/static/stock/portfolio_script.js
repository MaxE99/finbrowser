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

// switch portfolio
document.querySelector('.firstRow .nameContainer').addEventListener('click', () => {
    const dropdownSymbol = document.querySelector('.firstRow .nameContainer i');
    const optionsContainer = document.querySelector('.portfolioOptionsContainer');
    if (optionsContainer.style.display === 'block') {
        optionsContainer.style.display = 'none';
        dropdownSymbol.classList.replace('fa-chevron-up', 'fa-chevron-down');
    } else {
        optionsContainer.style.display = 'block';
        dropdownSymbol.classList.replace('fa-chevron-down', 'fa-chevron-up');
    }
});

// create portfolio
document.querySelector('.createPortfolioButton').addEventListener(
    'click',
    async () => {
        try {
            const res = await fetch(`../../api/portfolios/`, get_fetch_settings('POST'));
            if (!res.ok) {
                showMessage('Error: Network request failed unexpectedly!', 'Error');
            } else {
                const context = await res.json();
                window.location.replace(`../../portfolio/${context.portfolio_id}`);
            }
        } catch (e) {
            // showMessage("Error: Unexpected error has occurred!", "Error");
        }
    },
    { once: true }
);

function openAddStocksMenu() {
    document.querySelector('.portfolioMenuWrapper').style.display = 'block';
    document.querySelector('.addStocksContainer').style.display = 'block';
    setModalStyle();
    // add stocks -- selection process
    document
        .querySelector('.addStocksContainer #textInput')
        .addEventListener('keyup', async function (e) {
            const portfolioStocks = [];
            const tickerContainer = document.querySelectorAll('table tr .ticker');
            for (let i = 0, j = tickerContainer.length; i < j; i++) {
                portfolioStocks.push(tickerContainer[i].innerText);
            }
            const textInput = document.querySelector('.addStocksContainer #textInput');
            let search_term = textInput.value;
            let results_list = e.target
                .closest('.addStocksContainer')
                .querySelector('#searchResultsContainer');
            let selected_list = e.target
                .closest('.addStocksContainer')
                .querySelector('.selectionContainer');
            // cancel/reset add stocks to portfolio form
            document
                .querySelector('.addStocksContainer .buttonContainer .cancelButton')
                .addEventListener('click', () => {
                    selectedStocks = [];
                    selected_list.innerHTML = '';
                });
            if (search_term && search_term.split(/\s+/).join('') != '') {
                results_list.style.display = 'block';
                selected_list.style.display = 'none';
                try {
                    const res = await fetch(
                        `../../api/stocks/?search_term=${search_term}`,
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
                                    results_list.appendChild(searchResult);
                                    searchResult.addEventListener(
                                        'click',
                                        function addSelectedStock() {
                                            // Remove the listener from the element the first time the listener is run:
                                            searchResult.removeEventListener(
                                                'click',
                                                addSelectedStock
                                            );
                                            selectedStocks.push(stock.stock_id);
                                            const removeStockButton = document.createElement('i');
                                            removeStockButton.classList.add('fas', 'fa-times');
                                            removeStockButton.addEventListener('click', () => {
                                                removeStockButton.parentElement.remove();
                                                selectedStocks = selectedStocks.filter(function (
                                                    e
                                                ) {
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
                                            selected_list.appendChild(searchResult);
                                            results_list.style.display = 'none';
                                            selected_list.style.display = 'block';
                                            textInput.value = '';
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

let selectedStocks = [];
// open add stocks menu
document.querySelector('.actionButtonContainer .addStocksButton').addEventListener('click', () => {
    openAddStocksMenu();
});

document.querySelectorAll('.emptyInformationContainer button').forEach((addStocksButton) =>
    addStocksButton.addEventListener('click', () => {
        openAddStocksMenu();
    })
);

// close add stock menu
document
    .querySelector('.addStocksContainer .closeAddStockContainer')
    .addEventListener('click', () => {
        document.querySelector('.portfolioMenuWrapper').style.display = 'none';
        document.querySelector('.addStocksContainer').style.display = 'none';
        removeModalStyle();
    });

// open edit menu
document.querySelector('.editPortfolioButton').addEventListener('click', () => {
    document.querySelector('.portfolioMenuWrapper').style.display = 'block';
    document.querySelector('.editMenu').style.display = 'block';
    setModalStyle();
});

// close edit menu
document.querySelector('.editMenu .fa-times').addEventListener('click', () => {
    document.querySelector('.portfolioMenuWrapper').style.display = 'none';
    document.querySelector('.editMenu').style.display = 'none';
    removeModalStyle();
});

// add stocks -- api request
let activatedButton = false;
document
    .querySelector('.portfolioMenuWrapper .addStocksContainer .addStocksButton')
    .addEventListener('click', async () => {
        if (!selectedStocks.length) {
            showMessage('You Need To Select Stocks!', 'Error');
        }
        if (selectedStocks.length && !activatedButton) {
            activatedButton = true;
            try {
                const portfolio_id = document.querySelector('.firstRow .nameContainer h2').id;
                const data = { stocks: selectedStocks, portfolio: portfolio_id };
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
                        activatedButton = false;
                    } else {
                        showMessage('Error: Network request failed unexpectedly!', 'Error');
                    }
                } else {
                    showMessage('Portfolio has been updated!', 'Success');
                    window.location.reload();
                }
            } catch (e) {
                // showMessage("Error: Unexpected error has occurred!", "Error");
            }
        }
    });

// delete portfolio;
document.querySelector('.editMenu .deletePortfolioButton').addEventListener('click', () => {
    const portfolio_id = document.querySelector('.nameContainer h2').id;
    if (document.querySelectorAll('.portfoliosContainer .portfolioOption').length === 1) {
        showMessage('You are not allowed to delete your last portfolio!', 'Error');
    } else {
        document.querySelector('.portfolioMenuWrapper').style.display = 'none';
        document.querySelector('.editMenu').style.display = 'none';
        document.querySelector('.portfolioMenuWrapper').style.display = 'block';
        document.querySelector('.portfolioMenuWrapper .warningMessageContainer').style.display =
            'flex';
        document
            .querySelector('.portfolioMenuWrapper .warningMessageContainer .discardButton')
            .addEventListener('click', () => {
                removeModalStyle();
                document.querySelector('.portfolioMenuWrapper').style.display = 'none';
                document.querySelector(
                    '.portfolioMenuWrapper .warningMessageContainer'
                ).style.display = 'none';
            });
        document
            .querySelector('.portfolioMenuWrapper .warningMessageContainer .confirmButton')
            .addEventListener(
                'click',
                async () => {
                    try {
                        const res = await fetch(
                            `../../api/portfolios/${portfolio_id}/`,
                            get_fetch_settings('DELETE')
                        );
                        if (!res.ok) {
                            showMessage('Error: Network request failed unexpectedly!', 'Error');
                        } else {
                            showMessage('Portfolio has been deleted!', 'Remove');
                            document
                                .querySelectorAll('.portfolioOptionsContainer .portfolioOption')
                                .forEach((portfolioOption) => {
                                    if (portfolioOption.id.replace('wlist', '') !== portfolio_id) {
                                        window.location.replace(
                                            `../../portfolio/${portfolioOption.id.replace(
                                                'wlist',
                                                ''
                                            )}`
                                        );
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

//delete stock from portfolio
document.querySelectorAll('.stockContainer .fa-trash-can').forEach((removeButton) => {
    removeButton.addEventListener('click', async (e) => {
        const pstock_id = e.target.closest('.stockContainer').id.replace('pstock', '');
        try {
            const res = await fetch(
                `../../api/portfolio_stocks/${pstock_id}/`,
                get_fetch_settings('DELETE')
            );
            if (!res.ok) {
                showMessage('Error: Network request failed unexpectedly!', 'Error');
            } else {
                showMessage('Stock has been removed!', 'Remove');
                e.target.closest('.stockContainer').remove();
                if (!document.querySelector('table .stockContainer')) {
                    window.location.reload();
                }
            }
        } catch (e) {
            // showMessage("Error: Unexpected error has occurred!", "Error");
        }
    });
});

// edit portfolio
document.querySelector('.menuContainer .editMenu .saveEditsButton').addEventListener(
    'click',
    async () => {
        const portfolio_id = document.querySelector('.firstRow .nameContainer h2').id;
        const newName = document.querySelector('.editMenu .portfolioNameContainer input').value;
        const mainportfolio = document.querySelector(
            '.editMenu .mainPortfolioContainer input'
        ).checked;
        const data = { name: newName, main: mainportfolio };
        if (newName.trim().length) {
            try {
                const res = await fetch(`../../api/portfolios/${portfolio_id}/`, {
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
                // showMessage("Error: Unexpected error has occurred!", "Error");
            }
        } else {
            showMessage('Please enter a name!', 'Error');
        }
    },
    { once: true }
);

const portfolio_id = document.querySelector('.firstRow .nameContainer h2').id;

// remove source from blacklist
function removeSourceFromBlacklist(button) {
    button.addEventListener('click', async () => {
        const source_id = button.closest('.blacklistedSourceContainer').id.split('#')[1];
        try {
            const data = { source_id: source_id };
            const res = await fetch(`../../api/portfolios/${portfolio_id}/`, {
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
                blacklisted_sources = blacklisted_sources.filter((source) => source !== source_id);
            }
        } catch (e) {
            // showMessage("Error: Unexpected error has occurred!", "Error");
        }
    });
}

document
    .querySelectorAll('.blacklistSourceContainer .blacklistedSourceContainer .fa-times')
    .forEach((button) => {
        removeSourceFromBlacklist(button);
    });

// search for sources to be blacklisted
let blacklisted_sources = [];
document
    .querySelectorAll('.blacklistSourceContainer .blacklistedSourceContainer')
    .forEach((blacklistedSource) => {
        blacklisted_sources.push(blacklistedSource.id.split('#')[1]);
    });

if (document.querySelector('.blacklistSourceContainer #textInput')) {
    document
        .querySelector('.blacklistSourceContainer #textInput')
        .addEventListener('keyup', async function () {
            let search_term = document.querySelector('.blacklistSourceContainer #textInput').value;
            let results_list = document.querySelector(
                '.blacklistSourceContainer #searchResultsContainer'
            );
            let selected_list = document.querySelector(
                '.blacklistSourceContainer .selectionContainer'
            );
            if (search_term && search_term.split(/\s+/).join('') != '') {
                results_list.style.display = 'block';
                selected_list.style.display = 'none';
                try {
                    const res = await fetch(
                        `../../api/sources/?blacklist_search=${search_term}&portfolio_id=${portfolio_id}`,
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
                                if (!blacklisted_sources.includes(source.source_id)) {
                                    const searchResult = document.createElement('div');
                                    searchResult.classList.add('searchResult');
                                    const resultImage = document.createElement('img');
                                    resultImage.src = `https://finbrowser.s3.us-east-2.amazonaws.com/static/${source.favicon_path}`;
                                    const sourceName = document.createElement('span');
                                    sourceName.innerText = source.name;
                                    sourceName.id = `source_id_${source.source_id}`;
                                    searchResult.append(resultImage, sourceName);
                                    results_list.appendChild(searchResult);
                                    searchResult.addEventListener('click', async () => {
                                        try {
                                            const data = { source_id: source.source_id };
                                            const res = await fetch(
                                                `../../api/portfolios/${portfolio_id}/`,
                                                {
                                                    method: 'PATCH',
                                                    headers: {
                                                        'X-CSRFToken': getCookie('csrftoken'),
                                                        Accept: 'application/json',
                                                        'Content-Type': 'application/json',
                                                    },
                                                    mode: 'same-origin',
                                                    body: JSON.stringify(data),
                                                }
                                            );
                                            if (!res.ok) {
                                                showMessage(
                                                    'Error: Network request failed unexpectedly!',
                                                    'Error'
                                                );
                                            } else {
                                                results_list.style.display = 'none';
                                                selected_list.style.display = 'block';
                                                blacklisted_sources.push(source.source_id);
                                                const blacklistedSourceContainer =
                                                    document.createElement('div');
                                                blacklistedSourceContainer.classList.add(
                                                    'blacklistedSourceContainer'
                                                );
                                                blacklistedSourceContainer.id = `blsid#${source.source_id}`;
                                                const img = document.createElement('img');
                                                img.src = `/static/${source.favicon_path}`;
                                                const span = document.createElement('span');
                                                span.innerText = source.name;
                                                const timesButton = document.createElement('i');
                                                timesButton.classList.add('fas', 'fa-times');
                                                blacklistedSourceContainer.append(
                                                    img,
                                                    span,
                                                    timesButton
                                                );
                                                selected_list.appendChild(
                                                    blacklistedSourceContainer
                                                );
                                                removeSourceFromBlacklist(
                                                    blacklistedSourceContainer
                                                );
                                            }
                                        } catch (e) {
                                            // showMessage("Error: Unexpected error has occurred!", "Error");
                                        }
                                    });
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

// blacklist source explanation close button
function closeBlacklistExplanation() {
    document.querySelector('.fullScreenPlaceholder').style.display = 'none';
    document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display = 'none';
    document.querySelector('.portfolioMenuWrapper').style.display = 'flex';
    document.querySelector('.portfolioMenuWrapper .editMenu').style.display = 'block';
}

// blacklist source explanation
document
    .querySelector('.portfolioMenuWrapper .editMenu .blacklistSourceContainer .header .infoLink i')
    .addEventListener('click', () => {
        document.querySelector('.portfolioMenuWrapper').style.display = 'none';
        document.querySelector('.portfolioMenuWrapper .editMenu').style.display = 'none';
        document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
        document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display =
            'block';
        document.querySelector('.fullScreenPlaceholder .explanationContainer h3').innerText =
            'Blacklist Sources';
        document.querySelector(
            '.fullScreenPlaceholder .explanationContainer .explanation'
        ).innerText =
            "If you're seeing content from sources that you don't find helpful or relevant, you can easily remove them from your feed by adding them to your blacklisted sources. By doing so, you'll no longer see content from those sources and can focus on the ones that are most helpful to you.";
        const closeExplanationButton = document.querySelector(
            '.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times'
        );
        closeExplanationButton.addEventListener(
            'click',
            () => {
                closeBlacklistExplanation();
            },
            { once: true }
        );
    });

// main portfolio explanation
document
    .querySelector('.portfolioMenuWrapper .editMenu .mainPortfolioContainer .infoLink i')
    .addEventListener('click', () => {
        document.querySelector('.portfolioMenuWrapper').style.display = 'none';
        document.querySelector('.portfolioMenuWrapper .editMenu').style.display = 'none';
        document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
        document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display =
            'block';
        document.querySelector('.fullScreenPlaceholder .explanationContainer h3').innerText =
            'Main Portfolio';
        document.querySelector(
            '.fullScreenPlaceholder .explanationContainer .explanation'
        ).innerText =
            "Your main portfolio is the one that opens up whenever you click on the Portfolio button in the header. It's important to note that you always need to have at least one main portfolio. If you only have one portfolio, then you won't be able to delete it as it is your main one. But, if you have multiple portfolios and you delete your main one, then the next portfolio in alphabetical order will become your new main portfolio. Don't worry though, you can easily change your main portfolio by opening the edit menu of a portfolio that is currently not your main one and setting it as your new main portfolio. It's as simple as that!";
        const closeExplanationButton = document.querySelector(
            '.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times'
        );
        closeExplanationButton.addEventListener(
            'click',
            () => {
                closeBlacklistExplanation();
            },
            { once: true }
        );
    });

// delete keywords function
async function deleteKeywords(e, keywordButton = false) {
    const pkeyword_id = e.target.closest('.keywordContainer').id.replace('wkw', '');
    try {
        const res = await fetch(
            `../../api/portfolio_keywords/${pkeyword_id}/`,
            get_fetch_settings('DELETE')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            e.target.closest('.keywordContainer').remove();
            showMessage('Keyword has been removed!', 'Remove');
            if (keywordButton) {
                keywordButton.innerText -= 1;
            } else {
                const pstock_id = document
                    .querySelector('.keywordModal .keywordHeader span')
                    .id.replace('psi', '');
                document.querySelectorAll('table tr').forEach((tr) => {
                    if (tr.id == `pstock${pstock_id}`) {
                        tr.querySelector('td .keywordButton').innerText =
                            parseInt(tr.querySelector('td .keywordButton').innerText) - 1;
                    }
                });
            }
        }
    } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
    }
}

function sortKeywords(arr) {
    arr.sort(function (a, b) {
        var keywordA = a.keyword.toUpperCase();
        var keywordB = b.keyword.toUpperCase();
        if (keywordA < keywordB) {
            return -1;
        }
        if (keywordA > keywordB) {
            return 1;
        }
        return 0;
    });
    return arr;
}

async function getKeywords(pstock_id, keywordButton) {
    try {
        const res = await fetch(
            `../../api/portfolio_stocks/${pstock_id}/`,
            get_fetch_settings('GET')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
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
                removeButton.addEventListener('click', (e) => {
                    deleteKeywords(e, keywordButton);
                });
                removeButton.classList.add('fas', 'fa-times');
                keywordContainer.append(span, removeButton);
                keywordsContainer.appendChild(keywordContainer);
            });
        }
    } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
    }
}

// open keywords modal
const addKeywordsButton = document.querySelectorAll('.stockContainer td .keywordButton');
addKeywordsButton.forEach((keywordButton) => {
    keywordButton.addEventListener('click', () => {
        setModalStyle();
        document.querySelector('.portfolioMenuWrapper').style.display = 'block';
        document.querySelector('.portfolioMenuWrapper .keywordModal').style.display = 'block';
        const pstock_id = keywordButton.closest('tr').id.replace('pstock', '');
        document.querySelector('.keywordHeader span').innerText = keywordButton
            .closest('tr')
            .querySelector('.ticker').innerText;
        document.querySelector('.keywordHeader span').id = 'psi' + pstock_id;
        getKeywords(pstock_id, keywordButton);
    });
});

// add keywords
let keywordIsBeingCreated = false;
async function save_portfolio_keyword(element) {
    const newKeyword = document.querySelector('.keywordModal .inputContainer input').value;
    const pstock_id = document
        .querySelector('.keywordModal .keywordHeader span')
        .id.replace('psi', '');
    if (newKeyword.trim().length > 2 && !keywordIsBeingCreated) {
        keywordIsBeingCreated = true;
        try {
            const data = { keyword: newKeyword, pstock_id: pstock_id };
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
                    showMessage(
                        'Maximum limit of 100 stocks and keywords per portfolio has been reached.',
                        'Error'
                    );
                    keywordIsBeingCreated = false;
                } else {
                    showMessage('Error: Network request failed unexpectedly!', 'Error');
                }
            } else {
                const context = await res.json();
                const keywordContainer = document.createElement('div');
                keywordContainer.classList.add('keywordContainer');
                keywordContainer.id = `wkw${context.pkeyword_id}`;
                const keywordSpan = document.createElement('span');
                keywordSpan.innerText = context.keyword;
                const trashButton = document.createElement('i');
                trashButton.addEventListener('click', (e) => deleteKeywords(e));
                trashButton.classList.add('fas', 'fa-times');
                keywordContainer.append(keywordSpan, trashButton);
                element
                    .closest('.keywordModal')
                    .querySelector('.keywordsContainer')
                    .appendChild(keywordContainer);
                element.closest('.keywordModal').querySelector('.inputContainer input').value = '';
                keywordIsBeingCreated = false;
                showMessage('Keyword has been added!', 'Success');
                document.querySelectorAll('table tr').forEach((tr) => {
                    if (tr.id == `pstock${pstock_id}`) {
                        tr.querySelector('td .keywordButton').innerText =
                            parseInt(tr.querySelector('td .keywordButton').innerText) + 1;
                    }
                });
            }
        } catch (e) {
            // showMessage("Error: Unexpected error has occurred!", "Error");
        }
    } else {
        showMessage('A keyword must have at least 3 letters!', 'Error');
    }
}

document.querySelectorAll('.keywordModal .addButton').forEach((addButton) => {
    addButton.addEventListener('click', (e) => {
        save_portfolio_keyword(e.target);
    });
});

document.querySelectorAll('.keywordModal .createKeywordsContainer input').forEach((keywordInput) =>
    keywordInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            save_portfolio_keyword(keywordInput);
        }
    })
);

// close keyword modal
document
    .querySelector('.portfolioMenuWrapper .keywordModal .keywordHeader .fa-times')
    .addEventListener('click', () => {
        removeModalStyle();
        document.querySelector('.portfolioMenuWrapper').style.display = 'none';
        document.querySelector('.portfolioMenuWrapper .keywordModal').style.display = 'none';
    });

// keyword explanation
document
    .querySelector('.portfolioMenuWrapper .keywordModal .createKeywordsContainer .infoLink i')
    .addEventListener('click', (e) => {
        e.target.closest('.keywordModal').style.display = 'none';
        document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
        document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display =
            'block';
        document.querySelector('.fullScreenPlaceholder .explanationContainer h3').innerText =
            'Keywords';
        document.querySelector(
            '.fullScreenPlaceholder .explanationContainer .explanation'
        ).innerText =
            "FinBrowser finds content related to the stocks in your portfolio based on their ticker symbol and company name. If you want to see content that focuses on a specific product or segment within a company, you can enter a keyword here and the results for that keyword will be displayed as well. For instance, let's say you hold Amazon stock and you want to see more information about their cloud computing platform, AWS. Simply enter AWS as your keyword and you'll get all the relevant results. It's that easy!";
        const closeExplanationButton = document.querySelector(
            '.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times'
        );
        closeExplanationButton.addEventListener(
            'click',
            () => {
                e.target.closest('.keywordModal').style.display = 'block';
                document.querySelector('.fullScreenPlaceholder').style.display = 'none';
                document.querySelector(
                    '.fullScreenPlaceholder .explanationContainer'
                ).style.display = 'none';
            },
            { once: true }
        );
    });
