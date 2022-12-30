//delete profile pic
document
  .querySelector(".removeProfilePicButton")
  .addEventListener("click", async () => {
    const user = document.querySelector(".emailContainer").id.split("#")[1];
    try {
      const res = await fetch(
        `../../api/profiles/${user}/profile_pic_delete/`,
        get_fetch_settings("DELETE")
      );
      if (!res.ok) {
        showMessage("Error: Profile picture could not be deleted!", "Error");
      } else {
        const context = await res.json();
        showMessage(context, "Remove");
        window.location.reload();
      }
    } catch (e) {
      // showMessage("Error: Unexpected error has occurred!", "Error");
    }
  });

document
  .querySelectorAll(".notificationContainer .fa-times")
  .forEach((deleteButton) => {
    deleteButton.addEventListener("click", async () => {
      try {
        const notifications_id = deleteButton.id.split("#")[1];
        const res = await fetch(
          `../../api/notifications/${notifications_id}/`,
          get_fetch_settings("DELETE")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!", "Error");
        } else {
          deleteButton.closest(".sourceContainer")
            ? deleteButton.closest(".sourceContainer").remove()
            : deleteButton.closest(".keywordContainer").remove();
          showMessage("Notification has been deleted!", "Remove");
        }
      } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
    });
  });
