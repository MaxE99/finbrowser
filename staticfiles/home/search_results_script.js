/**************************************************************
    1. API Calls
**************************************************************/

async function searchSP(searchTerm, resultsList) {
    try {
        const res = await fetch(`../../api/search_site/${searchTerm}`, getFetchSettings('GET'));
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!!', 'Error');
        } else {
            const context = await res.json();
            showSearchResults(context, resultsList);
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

/**************************************************************
    2. Functions
**************************************************************/

function searchWithSearchSymbol() {
    const search_term = document.querySelector('.searchWrapper .mainInputSearch').value;
    if (search_term.split(/\s+/).join('') != '') {
        window.location.href = `../../search_results/${search_term}`;
    }
}

function searchSPWrapper(key) {
    let searchTerm = document.querySelector('.searchWrapper #searchResultsAutocomplete').value;
    if (key == 'Enter' && searchTerm.split(/\s+/).join('') != '') {
        window.location.href = `../../search_results/${searchTerm}`;
    } else {
        let resultsList = document.querySelector('.searchWrapper #autocomplete_list_results');
        if (searchTerm?.split(/\s+/).join('') != '') {
            clearTimeout(searchDelayTimerSP);
            searchDelayTimerSP = setTimeout(async function () {
                // extra check necesseary to prevent deletion to trigger a search with last letter + search_term has value from 350msec ago
                if (document.querySelector('.searchWrapper #searchResultsAutocomplete').value) {
                    searchSP(searchTerm, resultsList);
                }
            }, 350); // Set a 350ms delay before sending the request
            document.onclick = (e) => {
                if (e.target.id !== 'autocomplete_list_results') {
                    resultsList.style.display = 'none';
                }
            };
        } else {
            resultsList.style.display = 'none';
        }
    }
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

let searchDelayTimerSP;

/**************************************************************
    4. EventListener
**************************************************************/

document
    .querySelector('.searchWrapper #searchResultsAutocomplete')
    .addEventListener('keyup', (e) => searchSPWrapper(e.key));

document
    .querySelector('.searchWrapper .mainSearchContainer i')
    .addEventListener('click', () => searchWithSearchSymbol());
