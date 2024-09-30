/**************************************************************
    1. API Calls
**************************************************************/

async function changeSubscriptionStatusSR(subscribeButton) {
    if (!subscribeButton.classList.contains('openAuthPrompt')) {
        try {
            const source_id = subscribeButton.closest('.sourceRankingContainer').id.split('#')[1];
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

async function rateSourceSR() {
    const sourceId = document.querySelector('.sourceRatingsWrapper').id;
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

function createDropdown(dropdownName, dropdown, target) {
    if (dropdownName !== 'website') {
        dropdown.closest('form').querySelector('.websiteList').style.display = 'none';
    }
    if (dropdownName !== 'sector') {
        dropdown.closest('form').querySelector('.sectorList').style.display = 'none';
    }
    if (dropdownName !== 'tag') {
        dropdown.closest('form').querySelector('.tagList').style.display = 'none';
    }
    // this eventListener is also triggered when an li or input inside the dropdown is clicked, this prevents an error
    const tagName = target.tagName.toUpperCase();
    if (tagName !== 'LI' && tagName !== 'INPUT') {
        target.querySelector('ul').style.display !== 'block'
            ? (target.querySelector('ul').style.display = 'block')
            : (target.querySelector('ul').style.display = 'none');
        document.onclick = (e) => {
            if (
                (dropdownName === 'website' &&
                    !e.target.closest('.websiteList') &&
                    e.target !== dropdown) ||
                (dropdownName === 'sector' &&
                    !e.target.closest('.sectorList') &&
                    e.target !== dropdown) ||
                (dropdownName === 'tag' && !e.target.closest('.tagList') && e.target !== dropdown)
            ) {
                dropdown.querySelector('ul').style.display = 'none';
            }
        };
    }
}

function selectDropdown(target) {
    // is sometimes triggered on click on input
    if (target.tagName.toUpperCase() !== 'INPUT') {
        target.querySelector('input').checked
            ? (target.querySelector('input').checked = false)
            : (target.querySelector('input').checked = true);
    }
}

function openAddSourceToListsFormSR(target) {
    setModalStyle();
    if (!target.classList.contains('openAuthPrompt')) {
        const sourceId = target.closest('.sourceRankingContainer').id.split('#')[1];
        const sourceName = target
            .closest('.sourceRankingContainer')
            .querySelector('.firstRow a span:last-of-type').innerText;
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
            ?.addEventListener('click', () => resetAddSourceToListsForm());
    }
}

function resetSourceRatingMenu(initialUserRating) {
    document
        .querySelectorAll('.sourceRatingsContainer .ratingsButtonContainer button')
        .forEach((button) => {
            button.classList.remove('selectedRating');
            button.innerText == initialUserRating && button.classList.add('selectedRating');
        });
}

function openSourceRatingMenu(target) {
    let initialUserRating = null;
    if (!target.classList.contains('notRated')) {
        document
            .querySelectorAll('.sourceRatingsContainer .ratingsButtonContainer button')
            .forEach((button) => {
                if (button.innerText == target.innerText) {
                    button.classList.add('selectedRating');
                    initialUserRating = target.innerText;
                }
            });
    }
    document
        .querySelector('.sourceRatingsWrapper .ratingsContainer .cancelButton')
        ?.addEventListener('click', () => resetSourceRatingMenu(initialUserRating));
    const sourceName = target
        .closest('.sourceRankingContainer')
        .querySelector('.firstRow a span:last-of-type').innerText;
    const sourceId = target.closest('.sourceRankingContainer').id.split('#')[1];
    document.querySelector('.sourceRatingsWrapper').id = sourceId;
    document.querySelector('.sourceRatingsWrapper').style.display = 'flex';
    document.querySelector(
        '.sourceRatingsWrapper .header h3'
    ).innerHTML = `Rate <span>${sourceName}</span>`;
    setModalStyle();
}

function closeSourceRatingMenu() {
    document
        .querySelector('.sourceRatingsContainer .ratingsButtonContainer .selectedRating')
        ?.classList.remove('selectedRating');
    document.querySelector('.sourceRatingsWrapper').style.display = 'none';
    removeModalStyle();
}

function openTopSourceExplanation() {
    setModalStyle();
    createExplanationContainer(
        'Top Sources',
        'I personally select Top Sources based on their outstanding analysis, insightful perspectives, and engaging content. These sources are my go-to for staying informed and entertained, and I highly recommend them.'
    );
    document
        .querySelector('.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times')
        .addEventListener('click', () => closeTopSourceExplanation());
}

function closeTopSourceExplanation() {
    removeModalStyle();
    document.querySelector('.fullScreenPlaceholder').style.display = 'none';
    document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display = 'none';
}

function selectSourceRating(ratingButton) {
    RATING_BUTTONS.forEach((button) => button.classList.remove('selectedRating'));
    ratingButton.classList.add('selectedRating');
}

function openSourceFilterMenu() {
    document.querySelector('.horizontalFilterMenu').style.display = 'flex';
    document.querySelector('.pageWrapper').style.opacity = '0.1';
}

function closeSourceFilterMenu() {
    document.querySelector('.horizontalFilterMenu').style.display = 'none';
    document.querySelector('.pageWrapper').removeAttribute('style');
}

/**************************************************************
    3. Other
**************************************************************/

let isSourceBeingRated = false;

const RATING_BUTTONS = document.querySelectorAll(
    '.sourceRatingsWrapper .ratingsContainer .ratingsButtonContainer button'
);

/**************************************************************
    4. EventListener
**************************************************************/

document
    .querySelectorAll('.sourceRankingContainer .subscribeButton')
    .forEach((subscribeButton) =>
        subscribeButton.addEventListener('click', () => changeSubscriptionStatusSR(subscribeButton))
    );

document
    .querySelectorAll(
        '.filterSidebar form .websiteDropdown, .horizontalFilterMenu form .websiteDropdown'
    )
    .forEach((websiteDropdown) =>
        websiteDropdown.addEventListener('click', (e) =>
            createDropdown('website', websiteDropdown, e.target)
        )
    );

document
    .querySelectorAll(
        '.filterSidebar form .sectorDropdown, .horizontalFilterMenu form .sectorDropdown'
    )
    .forEach((sectorDropdown) =>
        sectorDropdown.addEventListener('click', (e) =>
            createDropdown('sector', sectorDropdown, e.target)
        )
    );

document
    .querySelectorAll('.filterSidebar form .tagDropdown, .horizontalFilterMenu form .tagDropdown')
    .forEach((tagDropdown) =>
        tagDropdown.addEventListener('click', (e) => createDropdown('tag', tagDropdown, e.target))
    );

document
    .querySelectorAll('form .selectContainer .dropdown li')
    .forEach((option) => option.addEventListener('click', (e) => selectDropdown(e.target)));

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

document
    .querySelectorAll('.sourceAddToListButton')
    .forEach((button) =>
        button.addEventListener('click', (e) => openAddSourceToListsFormSR(e.target))
    );

document
    .querySelector('.openFiltersButton')
    .addEventListener('click', () => openSourceFilterMenu());

document
    .querySelector('.horizontalFilterMenu .discardButton')
    .addEventListener('click', () => closeSourceFilterMenu());

document
    .querySelectorAll('.sourceRankingContainer .infoContainer .rateSpan')
    .forEach((ratingButton) => {
        !ratingButton.classList.contains('openAuthPrompt') &&
            ratingButton.addEventListener('click', (e) => openSourceRatingMenu(e.target));
    });

document
    .querySelector('.sourceRatingsWrapper .ratingsContainer .header .fa-times')
    .addEventListener('click', () => closeSourceRatingMenu());

RATING_BUTTONS.forEach((ratingButton) =>
    ratingButton.addEventListener('click', () => selectSourceRating(ratingButton))
);

document
    .querySelector('.sourceRatingsWrapper .ratingsContainer .rateSourceButton')
    .addEventListener('click', () => rateSourceSR());

document
    .querySelector('.filterSidebar .selectContainer .infoLink i')
    .addEventListener('click', () => openTopSourceExplanation());
