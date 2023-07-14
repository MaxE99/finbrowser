/**************************************************************
    1. API Calls
**************************************************************/

async function createList() {
    try {
        const res = await fetch(`../../api/lists/`, getFetchSettings('POST'));
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            window.location.replace(`../../list/${context.list_id}`);
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

/**************************************************************
    2. Functions
**************************************************************/

function changeLists() {
    const dropdownSymbol = document.querySelector('.firstRow .nameContainer i');
    const optionsContainer = document.querySelector('.listOptionsContainer');
    const isDisplayed = optionsContainer.style.display === 'block';
    optionsContainer.style.display = isDisplayed ? 'none' : 'block';
    dropdownSymbol.classList.toggle('fa-chevron-up', !isDisplayed);
    dropdownSymbol.classList.toggle('fa-chevron-down', isDisplayed);
}

/**************************************************************
    3. EventListener
**************************************************************/

document.querySelector('.firstRow .nameContainer').addEventListener('click', () => changeLists());

document
    .querySelector('.firstRow .listOptionsContainer .createListButton')
    .addEventListener('click', () => createList());
