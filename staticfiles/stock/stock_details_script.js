//Notifications
const notificationButton = document.querySelector(
  ".companyNameAndNotificationHeader .notificationButton"
);
if (notificationButton) {
  notificationButton.addEventListener("click", async () => {
    try {
      const stock_id = document
        .querySelector(".companyNameAndNotificationHeader .stockHeader")
        .id.split("#")[1];
      const data = { stock_id: stock_id };
      const res = await fetch(`../../api/notifications/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        mode: "same-origin",
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        showMessage("Error: Network request failed unexpectedly!", "Error");
      } else {
        const context = await res.json();
        if (notificationButton.classList.contains("notificationActivated")) {
          notificationButton.classList.remove("notificationActivated");
          notificationButton.classList.replace("fa-bell-slash", "fa-bell");
          showMessage(context, "Remove");
        } else {
          notificationButton.classList.add("notificationActivated");
          notificationButton.classList.replace("fa-bell", "fa-bell-slash");
          showMessage(context, "Success");
        }
      }
    } catch (e) {
      // showMessage("Error: Unexpected error has occurred!", "Error");
    }
  });
}
