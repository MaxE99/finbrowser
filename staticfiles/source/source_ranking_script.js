document.querySelectorAll('.sourceRankingContainer .subscribeButton').forEach((subscribeButton) => {
    subscribeButton.addEventListener('click', async () => {
        if (!subscribeButton.classList.contains('openAuthPrompt')) {
            try {
                const source_id = subscribeButton
                    .closest('.sourceRankingContainer')
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
                        subscribeButton.classList.add('subscribed');
                        subscribeButton.classList.replace('finButtonWhite', 'finButtonBlue');
                        subscribeButton.innerText = 'Subscribed';
                        showMessage((context = 'SOURCE HAS BEEN SUBSCRIBED!'), 'Success');
                    } else {
                        subscribeButton.classList.remove('subscribed');
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

// dropdowns
const websiteDropdown = document
    .querySelectorAll(
        '.filterSidebar form .websiteDropdown, .horizontalFilterMenu form .websiteDropdown'
    )
    .forEach((websiteDropdown) =>
        websiteDropdown.addEventListener('click', (e) => {
            websiteDropdown.closest('form').querySelector('.sectorList').style.display = 'none';
            websiteDropdown.closest('form').querySelector('.tagList').style.display = 'none';
            // this eventListener is also triggered when an li or input inside the dropdown is clicked, this prevents an error
            const tagName = e.target.tagName.toUpperCase();
            if (tagName !== 'LI' && tagName !== 'INPUT') {
                e.target.querySelector('ul').style.display !== 'block'
                    ? (e.target.querySelector('ul').style.display = 'block')
                    : (e.target.querySelector('ul').style.display = 'none');
                document.onclick = function (e) {
                    if (!e.target.closest('.websiteList') && e.target !== websiteDropdown) {
                        websiteDropdown.querySelector('ul').style.display = 'none';
                    }
                };
            }
        })
    );

const sectorDropdown = document
    .querySelectorAll(
        '.filterSidebar form .sectorDropdown, .horizontalFilterMenu form .sectorDropdown'
    )
    .forEach((sectorDropdown) =>
        sectorDropdown.addEventListener('click', (e) => {
            sectorDropdown.closest('form').querySelector('.websiteList').style.display = 'none';
            sectorDropdown.closest('form').querySelector('.tagList').style.display = 'none';
            // this eventListener is also triggered when an li inside the dropdown is clicked, this prevents an error
            const tagName = e.target.tagName.toUpperCase();
            if (tagName !== 'LI' && tagName !== 'INPUT') {
                e.target.querySelector('ul').style.display !== 'block'
                    ? (e.target.querySelector('ul').style.display = 'block')
                    : (e.target.querySelector('ul').style.display = 'none');
                document.onclick = function (e) {
                    if (!e.target.closest('.sectorList') && e.target !== sectorDropdown) {
                        sectorDropdown.querySelector('ul').style.display = 'none';
                    }
                };
            }
        })
    );

const tagDropdown = document
    .querySelectorAll('.filterSidebar form .tagDropdown, .horizontalFilterMenu form .tagDropdown')
    .forEach((tagDropdown) =>
        tagDropdown.addEventListener('click', (e) => {
            tagDropdown.closest('form').querySelector('.websiteList').style.display = 'none';
            tagDropdown.closest('form').querySelector('.sectorList').style.display = 'none';
            // this eventListener is also triggered when an li inside the dropdown is clicked, this prevents an error
            const tagName = e.target.tagName.toUpperCase();
            if (tagName !== 'LI' && tagName !== 'INPUT') {
                e.target.querySelector('ul').style.display !== 'block'
                    ? (e.target.querySelector('ul').style.display = 'block')
                    : (e.target.querySelector('ul').style.display = 'none');
                document.onclick = function (e) {
                    if (!e.target.closest('.tagList') && e.target !== tagDropdown) {
                        tagDropdown.querySelector('ul').style.display = 'none';
                    }
                };
            }
        })
    );

// select dropdown
document.querySelectorAll('form .selectContainer .dropdown li').forEach((option) =>
    option.addEventListener('click', (e) => {
        // wird manchmal auch bei click auf input getriggered
        if (e.target.tagName.toUpperCase() !== 'INPUT') {
            e.target.querySelector('input').checked
                ? (e.target.querySelector('input').checked = false)
                : (e.target.querySelector('input').checked = true);
        }
    })
);

// choice container input auswählen --- needs refactoring
document.querySelectorAll('form .choiceContainer').forEach((choiceContainer) =>
    choiceContainer.addEventListener('click', (e) => {
        if (e.target.querySelector('input')) {
            e.target.querySelector('input').checked
                ? (e.target.querySelector('input').checked = false)
                : (e.target.querySelector('input').checked = true);
        }
    })
);

//open add list to sources form
document.querySelectorAll('.sourceAddToListButton').forEach((button) => {
    button.addEventListener('click', (e) => {
        setModalStyle();
        if (!e.target.classList.contains('openAuthPrompt')) {
            const sourceId = e.target.closest('.sourceRankingContainer').id.split('#')[1];
            const sourceName = e.target
                .closest('.sourceRankingContainer')
                .querySelector('.firstRow a span:last-of-type').innerText;
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
            // cancel/reset add to sources form
            document
                .querySelector('.fullScreenPlaceholder .addSourceToListForm .cancelButton')
                ?.addEventListener('click', () => {
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
});

// openFiltersMenu
document.querySelector('.openFiltersButton').addEventListener('click', () => {
    document.querySelector('.horizontalFilterMenu').style.display = 'flex';
    document.querySelector('.pageWrapper').style.opacity = '0.1';
});

// closeFiltersMenu
document.querySelector('.horizontalFilterMenu .discardButton').addEventListener('click', () => {
    document.querySelector('.horizontalFilterMenu').style.display = 'none';
    document.querySelector('.pageWrapper').removeAttribute('style');
});

// open source ratings modal
document
    .querySelectorAll('.sourceRankingContainer .infoContainer .rateSpan')
    .forEach((ratingButton) => {
        if (!ratingButton.classList.contains('openAuthPrompt')) {
            ratingButton.addEventListener('click', (e) => {
                let initialUserRating = null;
                if (!e.target.classList.contains('notRated')) {
                    document
                        .querySelectorAll('.sourceRatingsContainer .ratingsButtonContainer button')
                        .forEach((button) => {
                            if (button.innerText == e.target.innerText) {
                                button.classList.add('selectedRating');
                                initialUserRating = e.target.innerText;
                            }
                        });
                }
                // cancel/reset source rating form
                document
                    .querySelector('.sourceRatingsWrapper .ratingsContainer .cancelButton')
                    ?.addEventListener('click', () => {
                        document
                            .querySelectorAll(
                                '.sourceRatingsContainer .ratingsButtonContainer button'
                            )
                            .forEach((button) => {
                                button.classList.remove('selectedRating');
                                if (button.innerText == initialUserRating) {
                                    button.classList.add('selectedRating');
                                }
                            });
                    });
                const sourceName = e.target
                    .closest('.sourceRankingContainer')
                    .querySelector('.firstRow a span:last-of-type').innerText;
                const sourceId = e.target.closest('.sourceRankingContainer').id.split('#')[1];
                document.querySelector('.sourceRatingsWrapper').id = sourceId;
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
    .querySelector('.sourceRatingsWrapper .ratingsContainer .header .fa-times')
    .addEventListener('click', () => {
        if (
            document.querySelector(
                '.sourceRatingsContainer .ratingsButtonContainer .selectedRating'
            )
        ) {
            document
                .querySelector('.sourceRatingsContainer .ratingsButtonContainer .selectedRating')
                .classList.remove('selectedRating');
        }
        document.querySelector('.sourceRatingsWrapper').style.display = 'none';
        removeModalStyle();
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
        const source_id = document.querySelector('.sourceRatingsWrapper').id;
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
        } else if (!rating && !activatedButton) {
            showMessage('Select a rating!', 'Error');
        }
    });

// top sources explanation
document
    .querySelector('.filterSidebar .selectContainer .infoLink i')
    .addEventListener('click', () => {
        setModalStyle();
        document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
        document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display =
            'block';
        document.querySelector('.fullScreenPlaceholder .explanationContainer h3').innerText =
            'Top Sources';
        document.querySelector(
            '.fullScreenPlaceholder .explanationContainer .explanation'
        ).innerText =
            'I personally select Top Sources based on their outstanding analysis, insightful perspectives, and engaging content. These sources are my go-to for staying informed and entertained, and I highly recommend them.';
        document
            .querySelector(
                '.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times'
            )
            .addEventListener('click', () => {
                removeModalStyle();
                document.querySelector('.fullScreenPlaceholder').style.display = 'none';
                document.querySelector(
                    '.fullScreenPlaceholder .explanationContainer'
                ).style.display = 'none';
            });
    });
