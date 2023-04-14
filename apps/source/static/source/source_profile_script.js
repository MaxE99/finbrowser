const subscribeButtons = document.querySelectorAll('.subscribeButton');

subscribeButtons.forEach((subscribeButton) => {
    subscribeButton.addEventListener('click', async () => {
        if (!subscribeButton.classList.contains('openAuthPrompt')) {
            try {
                const source_id = subscribeButton
                    .closest('.firstRow')
                    .querySelector('h2')
                    .id.split('#')[1];
                const action = subscribeButton.innerText;
                const res = await fetch(
                    `../../api/sources/${source_id}/`,
                    get_fetch_settings('PATCH')
                );
                if (!res.ok) {
                    showMessage('Error: Network request failed unexpectedly!', 'Error');
                } else {
                    if (action == 'Subscribe') {
                        subscribeButton.classList.replace('unsubscribed', 'subscribed');
                        subscribeButton.classList.replace('finButtonWhite', 'finButtonBlue');
                        subscribeButton.innerText = 'Subscribed';
                        showMessage((context = 'SOURCE HAS BEEN SUBSCRIBED!'), 'Success');
                    } else {
                        subscribeButton.classList.replace('subscribed', 'unsubscribed');
                        subscribeButton.classList.replace('finButtonBlue', 'finButtonWhite');
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

//add/remove notifications
const notificationButton = document.querySelector('.firstRow .notificationButton');
if (!notificationButton.classList.contains('openAuthPrompt')) {
    notificationButton.addEventListener('click', async () => {
        if (notificationButton.classList.contains('fa-bell')) {
            try {
                const source_id = notificationButton
                    .closest('.firstRow')
                    .querySelector('h2')
                    .id.split('#')[1];
                const data = { source: source_id };
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
                    showMessage('Notification has been added!', 'Success');
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
    });
}

// open source ratings modal
document
    .querySelectorAll('.rightSideContainer .ratingContainer .infoContainer .rateSpan')
    .forEach((rateSpan) => {
        if (!rateSpan.classList.contains('openAuthPrompt')) {
            rateSpan.addEventListener('click', () => {
                const sourceName = document.querySelector('.pageWrapper .firstRow h2').innerText;
                document.querySelector('.sourceRatingsWrapper').style.display = 'flex';
                document.querySelector(
                    '.sourceRatingsWrapper .header h3'
                ).innerHTML = `Rate <span>${sourceName}</span>`;
                setModalStyle();
            });
        }
    });

// close source ratings modal
document
    .querySelectorAll(
        '.sourceRatingsWrapper .ratingsContainer .header .fa-times, .sourceRatingsWrapper .ratingsContainer .cancelButton'
    )
    .forEach((element) => {
        element.addEventListener('click', () => {
            document.querySelector('.sourceRatingsWrapper').style.display = 'none';
            removeModalStyle();
        });
    });

// select source rating
const ratingsButtons = document.querySelectorAll(
    '.sourceRatingsWrapper .ratingsContainer .ratingsButtonContainer button'
);
ratingsButtons.forEach((ratingButton) =>
    ratingButton.addEventListener('click', () => {
        ratingsButtons.forEach((button) => button.classList.remove('selectedRating'));
        ratingButton.classList.add('selectedRating');
    })
);

// rate source
let activatedButton = false;
document
    .querySelector('.sourceRatingsWrapper .ratingsContainer .rateSourceButton')
    .addEventListener('click', async () => {
        const source_id = document.querySelector('.firstRow h2').id.split('#')[1];
        const rating = document.querySelector(
            '.sourceRatingsWrapper .ratingsContainer .ratingsButtonContainer .selectedRating'
        )?.innerText;
        body = {
            source: source_id,
            rating: rating,
        };
        if (rating && !activatedButton) {
            activatedButton = true;
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
                    showMessage((context = 'Rating has been saved!'), 'Success');
                    window.location.reload();
                }
            } catch (e) {
                // showMessage("Error: Unexpected error has occurred!", "Error");
            }
        } else {
            showMessage('Select a rating!', 'Error');
        }
    });

//open add list to sources form
document
    .querySelector('.pageWrapper .firstRow .notificationAndSubscribtionContainer  .fa-ellipsis-h')
    .addEventListener('click', (e) => {
        if (!e.target.classList.contains('openAuthPrompt')) {
            setModalStyle();
            const sourceId = document.querySelector('.pageWrapper .firstRow h2').id.split('#')[1];
            const sourceName = document.querySelector('.pageWrapper .firstRow h2').innerText;
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
        }
    });
