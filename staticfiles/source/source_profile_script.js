/**************************************************************
    1. API Calls
**************************************************************/

async function changeSubscriptionStatus(subscribeButton) {
    if (!subscribeButton.classList.contains('openAuthPrompt')) {
        try {
            const source_id = subscribeButton
                .closest('.firstRow')
                .querySelector('h2')
                .id.split('#')[1];
            const res = await fetch(`../../api/sources/${source_id}/`, getFetchSettings('PATCH'));
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

async function createNotification() {
    try {
        const sourceId = NOITIFICATION_BUTTON.closest('.firstRow')
            .querySelector('h2')
            .id.split('#')[1];
        const data = { source: sourceId };
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
            NOITIFICATION_BUTTON.id = 'nid#' + context.notification_id;
            NOITIFICATION_BUTTON.classList.add('notificationActivated');
            NOITIFICATION_BUTTON.classList.replace('fa-bell', 'fa-bell-slash');
            showMessage('Notification has been added!', 'Success');
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function deleteNotification() {
    const notificationId = NOITIFICATION_BUTTON.id.split('#')[1];
    try {
        const res = await fetch(
            `../../api/notifications/${notificationId}/`,
            getFetchSettings('DELETE')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            NOITIFICATION_BUTTON.classList.remove('notificationActivated');
            NOITIFICATION_BUTTON.classList.replace('fa-bell-slash', 'fa-bell');
            showMessage('Notification has been removed!', 'Remove');
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function rateSource() {
    const sourceId = document.querySelector('.firstRow h2').id.split('#')[1];
    const rating = document.querySelector(
        '.sourceRatingsWrapper .ratingsContainer .ratingsButtonContainer .selectedRating'
    )?.innerText;
    const body = {
        source: sourceId,
        rating: rating,
    };
    if (rating && !isSourceBeingRated) {
        isSourceBeingRated = true;
        try {
            const res = await fetch(`../../api/source_ratings/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    Accept: 'application/json',
                    'Content-Type': 'application/json',
                },
                mode: 'same-origin',
                body: JSON.stringify(body),
            });
            if (!res.ok) {
                showMessage('Error: Network request failed unexpectedly!', 'Error');
            } else {
                showMessage('Rating has been saved!', 'Success');
                window.location.reload();
            }
        } catch (e) {
            showMessage('Error: Unexpected error has occurred!', 'Error');
        }
    } else if (!rating && !isSourceBeingRated) {
        showMessage('Select a rating!', 'Error');
    }
}

/**************************************************************
    2. Functions
**************************************************************/

function openAddSourceToListsMenu(target) {
    if (!target.classList.contains('openAuthPrompt')) {
        setModalStyle();
        const sourceId = document.querySelector('.pageWrapper .firstRow h2').id.split('#')[1];
        const sourceName = document.querySelector('.pageWrapper .firstRow h2').innerText;
        document.querySelector('.fullScreenPlaceholder .addToListForm h3 span').innerText =
            sourceName;
        document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
        document.querySelector('.fullScreenPlaceholder .addSourceToListForm').style.display =
            'block';
        document.querySelector('.fullScreenPlaceholder .addSourceToListForm').id =
            'source_id' + sourceId;
        resetAddSourceToListsForm(sourceId);
        document
            .querySelector('.fullScreenPlaceholder .addSourceToListForm .cancelButton')
            ?.addEventListener('click', () => resetAddSourceToListsForm(sourceId));
    }
}

function openSourceRatingsMenu() {
    const sourceName = document.querySelector('.pageWrapper .firstRow h2').innerText;
    document.querySelector('.sourceRatingsWrapper').style.display = 'flex';
    document.querySelector(
        '.sourceRatingsWrapper .header h3'
    ).innerHTML = `Rate <span>${sourceName}</span>`;
    setModalStyle();
    document
        .querySelector('.sourceRatingsWrapper .ratingsContainer .cancelButton')
        ?.addEventListener('click', () => resetSourceRatingsMenu());
}

function closeSourceRatingsMenu() {
    document.querySelector('.sourceRatingsWrapper').style.display = 'none';
    removeModalStyle();
}

function resetSourceRatingsMenu() {
    document
        .querySelectorAll('.sourceRatingsContainer .ratingsButtonContainer button')
        .forEach((button) => {
            button.classList.remove('selectedRating');
            if (button.innerText == INITIAL_USER_RATING) {
                button.classList.add('selectedRating');
            }
        });
}

function selectSourceRating(ratingButton) {
    RATING_BUTTONS.forEach((button) => button.classList.remove('selectedRating'));
    ratingButton.classList.add('selectedRating');
}

/**************************************************************
    3. Other
**************************************************************/

const NOITIFICATION_BUTTON = document.querySelector('.firstRow .notificationButton');

const RATING_BUTTONS = document.querySelectorAll(
    '.sourceRatingsWrapper .ratingsContainer .ratingsButtonContainer button'
);

const INITIAL_USER_RATING = document.querySelector(
    '.sourceRatingsContainer .ratingsButtonContainer .selectedRating'
)?.innerText;

let isSourceBeingRated = false;

/**************************************************************
    4. EventListener
**************************************************************/

document
    .querySelectorAll('.subscribeButton')
    .forEach((subscribeButton) =>
        subscribeButton.addEventListener('click', () => changeSubscriptionStatus(subscribeButton))
    );

if (!NOITIFICATION_BUTTON.classList.contains('openAuthPrompt')) {
    NOITIFICATION_BUTTON.addEventListener('click', () =>
        NOITIFICATION_BUTTON.classList.contains('fa-bell')
            ? createNotification()
            : deleteNotification()
    );
}

document
    .querySelectorAll('.rightSideContainer .ratingContainer .infoContainer .rateSpan')
    .forEach(
        (rateSpan) =>
            !rateSpan.classList.contains('openAuthPrompt') &&
            rateSpan.addEventListener('click', () => openSourceRatingsMenu())
    );

document
    .querySelector('.sourceRatingsWrapper .ratingsContainer .header .fa-times')
    .addEventListener('click', () => closeSourceRatingsMenu());

RATING_BUTTONS.forEach((ratingButton) =>
    ratingButton.addEventListener('click', () => selectSourceRating(ratingButton))
);

document
    .querySelector('.sourceRatingsWrapper .ratingsContainer .rateSourceButton')
    .addEventListener('click', () => rateSource());

document
    .querySelector('.pageWrapper .firstRow .notificationAndSubscribtionContainer  .fa-ellipsis-h')
    .addEventListener('click', (e) => openAddSourceToListsMenu(e.target));
