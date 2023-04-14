// open settings with notifications open
if (location.href.endsWith('#notifications')) {
    const tabs = document.querySelectorAll('.tabsContainer button');
    const tabsContent = document.querySelectorAll('.tabsContent');
    for (let i = 0, j = tabs.length; i < j; i++) {
        tabs[i].classList.remove('activatedTab');
        tabsContent[i].classList.remove('tabsContentActive');
    }
    tabs[2].classList.add('activatedTab');
    tabsContent[2].classList.add('tabsContentActive');
}

//delete profile pic
document.querySelector('.removeProfilePicButton').addEventListener(
    'click',
    async () => {
        const profile_id = document.querySelector('.emailContainer').id.split('#')[1];
        try {
            const res = await fetch(
                `../../api/profiles/${profile_id}/`,
                get_fetch_settings('PATCH')
            );
            if (!res.ok) {
                showMessage('Error: Profile picture could not be deleted!', 'Error');
            } else {
                showMessage((context = 'Profile picture has been removed!'), 'Remove');
                window.location.reload();
            }
        } catch (e) {
            // showMessage("Error: Unexpected error has occurred!", "Error");
        }
    },
    { once: true }
);

document.querySelectorAll('.notificationContainer .fa-times').forEach((deleteButton) => {
    deleteButton.addEventListener('click', async () => {
        try {
            const notifications_id = deleteButton.id.split('#')[1];
            const res = await fetch(
                `../../api/notifications/${notifications_id}/`,
                get_fetch_settings('DELETE')
            );
            if (!res.ok) {
                showMessage('Error: Network request failed unexpectedly!', 'Error');
            } else {
                deleteButton.closest('.sourceContainer')
                    ? deleteButton.closest('.sourceContainer').remove()
                    : deleteButton.closest('.keywordContainer').remove();
                showMessage('Notification has been deleted!', 'Remove');
            }
        } catch (e) {
            // showMessage("Error: Unexpected error has occurred!", "Error");
        }
    });
});

// change profile pic
document
    .querySelector('.profilePicInnerContainer .changeProfilePicButton')
    .addEventListener('click', (e) => {
        e.target.closest('.profilePicInnerContainer').querySelector('input').click();
    });

document.querySelector('.profilePicInnerContainer input').addEventListener('change', async (e) => {
    const profile_id = document.querySelector('.emailContainer').id.split('#')[1];
    try {
        const formData = new FormData();
        formData.append('profile_pic', e.target.files[0]);
        const res = await fetch(`../../api/profiles/${profile_id}/`, {
            method: 'PATCH',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData,
        });
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            showMessage((context = 'Profile picture has been added!'), 'Success');
            window.location.reload();
        }
    } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
    }
});

//add/remove notifications
document
    .querySelectorAll('.sliderWrapper .slider .notificationButton')
    .forEach((notificationButton) => {
        notificationButton.addEventListener('click', async () => {
            if (!notificationButton.classList.contains('notificationActivated')) {
                try {
                    const source_id = notificationButton
                        .closest('.contentWrapper')
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
                        notificationButton.classList.replace('finButtonWhite', 'finButtonBlue');
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
                        notificationButton.classList.replace('finButtonBlue', 'finButtonWhite');
                        showMessage((context = 'Notification has been removed!'), 'Remove');
                    }
                } catch (e) {
                    // showMessage("Error: Unexpected error has occurred!", "Error");
                }
            }
        });
    });
