/**************************************************************
    1. API Calls
**************************************************************/

async function createStockNotification() {
    try {
        const data = { stock: STOCK_ID };
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
            NOTIFICATION_BUTTON.id = 'nid#' + context.notification_id;
            NOTIFICATION_BUTTON.classList.add('notificationActivated');
            NOTIFICATION_BUTTON.classList.replace('fa-bell', 'fa-bell-slash');
            showMessage('Notification has been created!', 'Success');
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function deleteStockNotification() {
    const notificationId = NOTIFICATION_BUTTON.id.split('#')[1];
    try {
        const res = await fetch(
            `../../api/notifications/${notificationId}/`,
            getFetchSettings('DELETE')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            NOTIFICATION_BUTTON.classList.remove('notificationActivated');
            NOTIFICATION_BUTTON.classList.replace('fa-bell-slash', 'fa-bell');
            showMessage('Notification has been removed!', 'Remove');
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function addStockToPortfolios(portfolioIds) {
    for (let i = 0; i < portfolioIds.length; i++) {
        try {
            const data = { stock_id: STOCK_ID, portfolios: portfolioIds[i] };
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
                showMessage('Error: Network request failed unexpectedly!', 'Error');
            }
        } catch (e) {
            showMessage('Error: Unexpected error has occurred!', 'Error');
        }
    }
}

async function removeStockFromPortfolios(portfolioIds) {
    for (let i = 0; i < portfolioIds.length; i++) {
        try {
            const res = await fetch(
                `../../api/portfolio_stocks/remove_stock_from_portfolio/${portfolioIds[i]}/${STOCK_ID}`,
                getFetchSettings('DELETE')
            );
            if (!res.ok) {
                showMessage('Error: Network request failed unexpectedly!', 'Error');
            }
        } catch (e) {
            showMessage('Error: Unexpected error has occurred!', 'Error');
        }
    }
}

/**************************************************************
    2. Functions
**************************************************************/

function checkInitialStockInPortfoliosStatus() {
    let initialPortfolioStatus = [];
    let portfolioIds = [];
    document
        .querySelectorAll('.stockMenuWrapper .addStockContainer .portfolioSelectionContainer input')
        .forEach((checkbox) => {
            checkbox.classList.contains('portfolioInList')
                ? initialPortfolioStatus.push(true)
                : initialPortfolioStatus.push(false);
            portfolioIds.push(checkbox.id.replace('id_portfolio_', ''));
        });
    return [initialPortfolioStatus, portfolioIds];
}

function checkNewStockInPortfoliosStatus() {
    let portfoliosStatus = [];
    const checkboxes = document.querySelectorAll(
        '.stockMenuWrapper .addStockContainer .portfolioSelectionContainer input'
    );
    checkboxes.forEach((input) => {
        portfoliosStatus.push(input.checked);
    });
    return portfoliosStatus;
}

function saveStockPortfolioStatuses() {
    const [initialPortfolioStatus, portfolioIds] = checkInitialStockInPortfoliosStatus();
    const portfoliosWithStockAdded = [];
    const portfoliosWithStockRemoved = [];
    const newPortfolioStatus = checkNewStockInPortfoliosStatus();
    for (let i = 0; i < newPortfolioStatus.length; i++) {
        if (newPortfolioStatus[i] !== initialPortfolioStatus[i]) {
            initialPortfolioStatus[i] === false
                ? portfoliosWithStockAdded.push(portfolioIds[i])
                : portfoliosWithStockRemoved.push(portfolioIds[i]);
        }
    }
    const promises = [];
    if (portfoliosWithStockAdded.length) {
        promises.push(addStockToPortfolios(portfoliosWithStockAdded));
    }
    if (portfoliosWithStockRemoved.length) {
        promises.push(removeStockFromPortfolios(portfoliosWithStockRemoved));
    }
    Promise.all(promises).then(() => {
        showMessage('Portfolios have been updated!', 'Success');
        window.location.reload();
    });
}

function changeStockNotificationStatus() {
    if (!NOTIFICATION_BUTTON.classList.contains('openAuthPrompt')) {
        NOTIFICATION_BUTTON.classList.contains('fa-bell')
            ? createStockNotification()
            : deleteStockNotification();
    }
}

function openAddStockToPortfoliosModal(target) {
    if (!target.classList.contains('openAuthPrompt')) {
        setModalStyle();
        document.querySelector('.stockMenuWrapper').style.display = 'flex';
        document.querySelector('.stockMenuWrapper .addStockContainer').style.display = 'block';
        resetAddStockToListForm();
    }
}

function closeAddStockToPortfoliosModal() {
    document.querySelector('.stockMenuWrapper').style.display = 'none';
    document.querySelector('.stockMenuWrapper .addStockContainer').style.display = 'none';
    removeModalStyle();
}

function resetAddStockToListForm() {
    document
        .querySelectorAll('.stockMenuWrapper .addStockContainer .portfolioContainer input')
        .forEach((input) => {
            input.classList.contains('portfolioInList')
                ? (input.checked = true)
                : (input.checked = false);
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

const NOTIFICATION_BUTTON = document.querySelector('.stockActionContainer .notificationButton');

const STOCK_ID = document
    .querySelector('.companyNameAndNotificationHeader .stockHeader')
    .id.split('#')[1];

/**************************************************************
    4. EventListener
**************************************************************/

NOTIFICATION_BUTTON.addEventListener('click', () => changeStockNotificationStatus());

document
    .querySelector('.pageWrapper .stockActionContainer .fa-ellipsis-h')
    .addEventListener('click', (e) => openAddStockToPortfoliosModal(e.target));

document
    .querySelector('.stockMenuWrapper .addStockContainer .cancelButton')
    .addEventListener('click', () => resetAddStockToListForm());

document
    .querySelector('.stockMenuWrapper .addStockContainer .formHeaderContainer .fa-times')
    .addEventListener('click', () => closeAddStockToPortfoliosModal());

document
    .querySelector('.stockMenuWrapper .addStockContainer .saveButton')
    .addEventListener('click', () => saveStockPortfolioStatuses(), { once: true });

// toggle input checkbox on click on portfolio container
document
    .querySelectorAll('.stockMenuWrapper .portfolioSelectionContainer .portfolioContainer')
    .forEach((portfolioContainer) =>
        portfolioContainer.addEventListener('click', () => {
            portfolioContainer.querySelector('input:first-of-type').checked =
                !portfolioContainer.querySelector('input:first-of-type').checked;
        })
    );
