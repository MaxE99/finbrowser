// open create keyword notification modal
document.querySelector('.tabsContent .addKeywordsButton').addEventListener('click', () => {
    setModalStyle();
    document.querySelector('.keywordCreationWrapper').style.display = 'flex';
});

// close keyword notification modal
document
    .querySelector('.keywordCreationWrapper .createKeywordNotificationModal .discardButton')
    .addEventListener('click', () => {
        removeModalStyle();
        document.querySelector('.keywordCreationWrapper').style.display = 'none';
    });

async function save_keyword_standalone_page() {
    const input = document.querySelector(
        '.keywordCreationWrapper .createKeywordNotificationModal input'
    );
    if (input.value.trim().length > 2) {
        try {
            const data = { keyword: input.value };
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
                input.value = '';
                showMessage('A new keyword has been created!', 'Success');
            }
        } catch (e) {
            // showMessage("Error: Unexpected error has occurred!", "Error");
        }
    } else {
        showMessage('A keyword must consist of at least 3 letters!', 'Error');
    }
}

//save new keyword
document
    .querySelector('.keywordCreationWrapper .createKeywordNotificationModal .saveButton')
    .addEventListener('click', () => {
        save_keyword_standalone_page();
    });

document
    .querySelector('.keywordCreationWrapper .createKeywordNotificationModal input')
    .addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            save_keyword_standalone_page();
        }
    });

// notification popup keyword notification explanation
document
    .querySelector('.overlay .keywordCreationWrapper .createKeywordNotificationModal .infoLink i')
    .addEventListener('click', () => {
        document.querySelector('.overlay .keywordCreationWrapper').style.display = 'none';
        document.querySelector('.fullScreenPlaceholder').style.display = 'flex';
        document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display =
            'block';
        document.querySelector('.fullScreenPlaceholder .explanationContainer h3').innerText =
            'Keywords';
        document.querySelector(
            '.fullScreenPlaceholder .explanationContainer .explanation'
        ).innerText =
            "If you want to stay up-to-date on a particular topic, just add a keyword and I'll make sure you're notified as soon as any of your sources publish content containing that keyword on FinBrowser.";
        const closeExplanationButton = document.querySelector(
            '.fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times'
        );
        closeExplanationButton.addEventListener('click', () => {
            document.querySelector('.overlay .keywordCreationWrapper').style.display = 'flex';
            document.querySelector('.fullScreenPlaceholder').style.display = 'none';
            document.querySelector('.fullScreenPlaceholder .explanationContainer').style.display =
                'none';
        });
    });
