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

// add/remove notification
const notificationButton = document.querySelector('.stockActionContainer .notificationButton');
notificationButton?.addEventListener('click', async () => {
    if (!notificationButton.classList.contains('openAuthPrompt')) {
        if (notificationButton.classList.contains('fa-bell')) {
            try {
                const stock_id = document
                    .querySelector('.companyNameAndNotificationHeader .stockHeader')
                    .id.split('#')[1];
                const data = { stock: stock_id };
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
                    const context = await res.json();
                    notificationButton.id = 'nid#' + context.notification_id;
                    notificationButton.classList.add('notificationActivated');
                    notificationButton.classList.replace('fa-bell', 'fa-bell-slash');
                    showMessage('Notification has been created!', 'Success');
                }
            } catch (e) {
                // showMessage("Error: Unexpected error has occurred!", "Error");
            }
        } else {
            const notification_id = notificationButton.id.split('#')[1];
            try {
                const res = await fetch(
                    `../../api/notifications/${notification_id}/`,
                    get_fetch_settings('DELETE')
                );
                if (!res.ok) {
                    showMessage('Error: Network request failed unexpectedly!', 'Error');
                } else {
                    notificationButton.classList.remove('notificationActivated');
                    notificationButton.classList.replace('fa-bell-slash', 'fa-bell');
                    showMessage((context = 'Notification has been removed!'), 'Remove');
                }
            } catch (e) {
                // showMessage("Error: Unexpected error has occurred!", "Error");
            }
        }
    }
});

// add stocks
function get_initial_portfolio_statuses() {
    let initial_lists_status = [];
    let list_ids = [];
    const input_list = document.querySelectorAll(
        '.stockMenuWrapper .addStockContainer .portfolioSelectionContainer input'
    );
    for (let i = 0, j = input_list.length; i < j; i++) {
        initial_lists_status.push(input_list[i].checked);
        list_ids.push(input_list[i].id.replace('portfolio_', ''));
    }
    return [initial_lists_status, list_ids];
}

function check_new_portfolio_status() {
    let lists_status = [];
    const input_list = document.querySelectorAll(
        '.stockMenuWrapper .addStockContainer .portfolioSelectionContainer input'
    );
    input_list.forEach((input) => {
        lists_status.push(input.checked);
    });
    return lists_status;
}

async function add_stock_to_portfolio(list_ids, stock_id) {
    for (let i = 0; i < list_ids.length; i++) {
        try {
            const data = { stock_id: stock_id, portfolios: list_ids[i] };
            console.log(data);
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
                console.log(res);
                console.log('response not okay');
                setTimeout(function () {
                    console.log('Resuming application after 30 seconds...');
                }, 30000); // 30 seconds in milliseconds
                showMessage('Error: Network request failed unexpectedly!', 'Error');
            }
        } catch (e) {
            console.log(res);
            console.log('catch');
            setTimeout(function () {
                console.log('Resuming application after 30 seconds...');
            }, 30000); // 30 seconds in milliseconds
            // showMessage("Error: Unexpected error has occurred!", "Error");
        }
    }
}

async function remove_stock_from_portfolio(list_ids, stock_id) {
    for (let i = 0; i < list_ids.length; i++) {
        try {
            const res = await fetch(
                `../../api/portfolio_stocks/remove_stock_from_portfolio/${list_ids[i]}/${stock_id}`,
                get_fetch_settings('DELETE')
            );
            if (!res.ok) {
                showMessage('Error: Network request failed unexpectedly!', 'Error');
            }
        } catch (e) {
            // showMessage("Error: Unexpected error has occurred!", "Error");
        }
    }
}

document
    .querySelector('.pageWrapper .stockActionContainer .fa-ellipsis-h')
    .addEventListener('click', (e) => {
        if (!e.target.classList.contains('openAuthPrompt')) {
            setModalStyle();
            document.querySelector('.stockMenuWrapper').style.display = 'flex';
            document.querySelector('.stockMenuWrapper .addStockContainer').style.display = 'block';
            const initial_lists_statuses = get_initial_portfolio_statuses();
            const initial_lists_status = initial_lists_statuses[0];
            // cancel/reset add stock to list form
            document
                .querySelector('.stockMenuWrapper .addStockContainer .cancelButton')
                .addEventListener('click', () => {
                    document
                        .querySelectorAll(
                            '.stockMenuWrapper .addStockContainer .portfolioContainer input'
                        )
                        .forEach((input) => {
                            if (input.classList.contains('portfolioInList')) {
                                input.checked = true;
                            } else {
                                input.checked = false;
                            }
                        });
                });

            document
                .querySelector('.stockMenuWrapper .addStockContainer .saveButton')
                .addEventListener(
                    'click',
                    () => {
                        const list_ids = initial_lists_statuses[1];
                        const stock_id = document
                            .querySelector('.companyNameAndNotificationHeader .stockHeader')
                            .id.replace('sti#', '');
                        const addStocksToportfolio = [];
                        const removeStocksFromportfolio = [];
                        const lists_status = check_new_portfolio_status();
                        for (let i = 0, j = lists_status.length; i < j; i++) {
                            if (lists_status[i] != initial_lists_status[i]) {
                                if (initial_lists_status[i] == false) {
                                    addStocksToportfolio.push(list_ids[i].replace('id_', ''));
                                } else {
                                    removeStocksFromportfolio.push(list_ids[i].replace('id_', ''));
                                }
                            }
                        }
                        addStocksToportfolio.length &&
                            add_stock_to_portfolio(addStocksToportfolio, stock_id);
                        removeStocksFromportfolio.length &&
                            remove_stock_from_portfolio(removeStocksFromportfolio, stock_id);
                        showMessage('Portfolios have been updated!', 'Success');
                        window.location.reload();
                    },
                    { once: true }
                );
        }
    });

// close add stock to portfolio modal
document
    .querySelector('.stockMenuWrapper .addStockContainer .formHeaderContainer .fa-times')
    .addEventListener('click', () => {
        document.querySelector('.stockMenuWrapper').style.display = 'none';
        document.querySelector('.stockMenuWrapper .addStockContainer').style.display = 'none';
        removeModalStyle();
    });

// click on portfolio container => click on input checkbox
document
    .querySelectorAll('.stockMenuWrapper .portfolioSelectionContainer .portfolioContainer')
    .forEach((portfolioContainer) =>
        portfolioContainer.addEventListener('click', () => {
            portfolioContainer.querySelector('input:first-of-type').checked =
                !portfolioContainer.querySelector('input:first-of-type').checked;
        })
    );
