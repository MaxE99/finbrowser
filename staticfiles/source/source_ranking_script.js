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

// select tags for filtering from source container
document.querySelectorAll('.thirdRow .tag').forEach((tag) =>
    tag.addEventListener('click', () => {
        document.querySelectorAll('.selectedTagsContainer').forEach((selectedTagsContainer) => {
            const selectedTags = [];
            selectedTagsContainer.querySelectorAll('li').forEach((sTag) => {
                selectedTags.push(sTag.innerText);
            });
            if (!selectedTags.includes(tag.innerText)) {
                const li = document.createElement('li');
                li.classList.add('selectedOption');
                li.setAttribute('value', tag.innerText);
                li.innerText = tag.innerText;
                const input = document.createElement('input');
                input.setAttribute('hidden', true);
                input.setAttribute('name', 'tag');
                input.setAttribute('value', tag.innerText);
                const deleteButton = document.createElement('i');
                li.appendChild(input);
                li.appendChild(deleteButton);
                deleteButton.classList.add('fas', 'fa-times');
                deleteButton.addEventListener('click', () => {
                    li.remove();
                });
                selectedTagsContainer.appendChild(li);
            }
        });
    })
);

// remove selected tags on click
document.querySelectorAll('.selectedTagsContainer li i').forEach((deleteButton) =>
    deleteButton.addEventListener('click', () => {
        deleteButton.closest('li').remove();
    })
);

// prevent enter on search tags = enter form
document.querySelectorAll('form .tagInputSearch').forEach((tagInputSearch) =>
    tagInputSearch.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
        }
    })
);

// dropdowns
const websiteDropdown = document
    .querySelectorAll(
        '.filterSidebar form .websiteDropdown, .horizontalFilterMenu form .websiteDropdown'
    )
    .forEach((websiteDropdown) =>
        websiteDropdown.addEventListener('click', (e) => {
            websiteDropdown.closest('form').querySelector('.sectorList').style.display = 'none';
            websiteDropdown.closest('form').querySelector('.selectionList').style.display = 'none';
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
            sectorDropdown.closest('form').querySelector('.selectionList').style.display = 'none';
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

function selectFilterOption(selection) {
    const selectContainer = selection.closest('.selectContainer');
    const selectedTagsContainer = selection.closest('form').querySelector('.selectedTagsContainer');
    const clonedSelection = selection.cloneNode(true);
    clonedSelection.classList.add('selectedOption');
    const deleteSelectionButton = document.createElement('i');
    deleteSelectionButton.classList.add('fas', 'fa-times');
    deleteSelectionButton.addEventListener('click', () => {
        clonedSelection.remove();
    });
    const hiddenInput = document.createElement('input');
    hiddenInput.setAttribute('hidden', true);
    hiddenInput.setAttribute('name', 'tag');
    hiddenInput.setAttribute('value', clonedSelection.innerText);
    clonedSelection.appendChild(hiddenInput);
    clonedSelection.appendChild(deleteSelectionButton);
    selection.style.display = 'none';
    selectedTagsContainer.appendChild(clonedSelection);
    selectedTagsContainer.style.display = 'flex';
    selectContainer.querySelector('ul').style.display = 'none';
}

// search tags
document.querySelectorAll('form .tagInputSearch').forEach((searchInput) =>
    searchInput.addEventListener('keyup', async function () {
        let search_term = searchInput.value;
        let results_list = searchInput.closest('form').querySelector('#tagAutocomplete_result ul');
        if (search_term && search_term.split(/\s+/).join('') != '') {
            try {
                const res = await fetch(
                    `../../../../../../api/source_tags/?search_term=${search_term}`,
                    get_fetch_settings('GET')
                );
                if (!res.ok) {
                    showMessage('Error: Network request failed unexpectedly!', 'Error');
                } else {
                    const context = await res.json();
                    let selectedTags = [];
                    document
                        .querySelectorAll('.selectedTagsContainer li')
                        .forEach((result) => selectedTags.push(result.innerText));
                    if (context.length > 0) {
                        results_list.style.display = 'block';
                        results_list.innerHTML = '';
                        context.forEach((tag) => {
                            if (!selectedTags.includes(tag.name)) {
                                const tagOption = document.createElement('li');
                                tagOption.setAttribute('value', tag.name);
                                tagOption.innerText = tag.name;
                                tagOption.addEventListener('click', () => {
                                    selectFilterOption(tagOption);
                                });
                                results_list.appendChild(tagOption);
                            }
                        });
                    } else {
                        results_list.style.display = 'none';
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
    })
);

// filter selection
document.querySelectorAll('.selectionList li').forEach((selection) => {
    selection.addEventListener('click', () => {
        selectFilterOption(selection);
    });
});

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
        } else if(!rating && !activatedButton) {
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
