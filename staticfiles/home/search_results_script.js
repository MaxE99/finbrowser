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

// main search with autocomplete
document
    .querySelector('.searchWrapper #mainAutocomplete')
    .addEventListener('keyup', async function (e) {
        let search_term = document.querySelector('.searchWrapper #mainAutocomplete').value;
        if (e.key == 'Enter' && search_term.replaceAll(/\s/g, '') != '') {
            window.location.href = `../../search_results/${search_term}`;
        } else {
            let results_list = document.querySelector('.searchWrapper #autocomplete_list_results');
            if (search_term && search_term.replaceAll(/\s/g, '') != '') {
                try {
                    const res = await fetch(
                        `../../api/search_site/${search_term}`,
                        get_fetch_settings('GET')
                    );
                    if (!res.ok) {
                        showMessage('Error: Network request failed unexpectedly!!', 'Error');
                    } else {
                        const context = await res.json();
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
                                const sourceRes = `<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${source.favicon_path}"><span>${source.name}</span><a href="../../source/${source.slug}"></a></div>`;
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

//get search results
document.querySelector('.searchWrapper .mainSearchContainer i').addEventListener('click', () => {
    search_term = document.querySelector('.searchWrapper .mainInputSearch').value;
    if (search_term.replaceAll(/\s/g, '') != '') {
        window.location.href = `../../search_results/${search_term}`;
    }
});
