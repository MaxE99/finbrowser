//Notifications
const notificationButton = document.querySelector(
    ".companyNameAndNotificationHeader .fa-bell"
  );
  if (notificationButton) {
    notificationButton.addEventListener("click", async () => {
      try {
        const stock_id = document
          .querySelector(".companyNameAndNotificationHeader .stockHeader")
          .id.replace("stock_id_", "");
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
            showMessage(context, "Remove");
          } else {
            notificationButton.classList.add("notificationActivated");
            showMessage(context, "Success");
          }
        }
      } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
    });
  }