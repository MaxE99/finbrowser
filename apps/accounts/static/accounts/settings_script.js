/**************************************************************
    1. API Calls
**************************************************************/

async function deleteProfilePic() {
    try {
        const res = await fetch(`../../api/profiles/${PROFILE_ID}/`, getFetchSettings('PATCH'));
        if (!res.ok) {
            showMessage('Error: Profile picture could not be deleted!', 'Error');
        } else {
            showMessage('Profile picture has been removed!', 'Remove');
            window.location.reload();
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function changeProfilePic(file) {
    try {
        const formData = new FormData();
        formData.append('profile_pic', file);
        const res = await fetch(`../../api/profiles/${PROFILE_ID}/`, {
            method: 'PATCH',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData,
        });
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            showMessage('Profile picture has been changed!', 'Success');
            window.location.reload();
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function deleteNotification(deleteButton, isSourceNotification = false) {
    try {
        const notificationsId = deleteButton.id.split('#')[1];
        const res = await fetch(
            `../../api/notifications/${notificationsId}/`,
            getFetchSettings('DELETE')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            // source notifications are not removed upon deletion, allowing the user to re-add a deleted notification
            if (isSourceNotification) {
                deleteButton.classList.remove('notificationActivated');
                deleteButton.classList.replace('fa-bell-slash', 'fa-bell');
                deleteButton.classList.replace('finButtonBlue', 'finButtonWhite');
            } else {
                deleteButton.closest('.sourceContainer')
                    ? deleteButton.closest('.sourceContainer').remove()
                    : deleteButton.closest('.keywordContainer').remove();
            }
            showMessage('Notification has been deleted!', 'Remove');
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function reCreateSourceNotification(notificationButton) {
    try {
        const sourceId = notificationButton.closest('.contentWrapper').id.split('#')[1];
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
            notificationButton.id = 'nid#' + context.notification_id;
            notificationButton.classList.add('notificationActivated');
            notificationButton.classList.replace('fa-bell', 'fa-bell-slash');
            notificationButton.classList.replace('finButtonWhite', 'finButtonBlue');
            showMessage('Notification has been added!', 'Success');
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

/**************************************************************
    2. Other
**************************************************************/

if (location.href.endsWith('#notifications')) {
    changeTabsOnPageOpen(2);
}

const PROFILE_ID = document.querySelector('.emailContainer').id.split('#')[1];

/**************************************************************
    3. EventListener
**************************************************************/

document
    .querySelector('.removeProfilePicButton')
    .addEventListener('click', () => deleteProfilePic(), { once: true });

document
    .querySelector('.profilePicInnerContainer input')
    .addEventListener('change', (e) => changeProfilePic(e.target.files[0]));

document
    .querySelectorAll('.notificationContainer .fa-times')
    .forEach((deleteButton) =>
        deleteButton.addEventListener('click', () => deleteNotification(deleteButton))
    );

document
    .querySelectorAll('.sliderWrapper .slider .notificationButton')
    .forEach((notificationButton) => {
        notificationButton.addEventListener('click', () => {
            !notificationButton.classList.contains('notificationActivated')
                ? reCreateSourceNotification(notificationButton)
                : deleteNotification(notificationButton, true);
        });
    });

// workaround to open image input field with button element
document
    .querySelector('.profilePicInnerContainer .changeProfilePicButton')
    .addEventListener('click', (e) =>
        e.target.closest('.profilePicInnerContainer').querySelector('input').click()
    );
