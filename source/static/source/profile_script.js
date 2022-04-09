const subscribeButton = document.querySelector(".subscribeButton");

subscribeButton.addEventListener("click", async () => {
  try {
    const url = window.location.href;
    const index = url.lastIndexOf("/");
    const domain = url.substring(index + 1);
    const action = subscribeButton.innerText;
    const res = await fetch(
      `../../home/source_change_subscribtion_status/${domain}/${action}`,
      get_fetch_settings("POST")
    );
    if (!res.ok) {
      showMessage("Error: Source can't be subscribed!", "Error");
    } else {
      const context = await res.json();
      showMessage(context, "Success");
      if (action == "Subscribe") {
        subscribeButton.classList.replace("unsubscribed", "subscribed");
        subscribeButton.innerText = "Subscribed";
      } else {
        subscribeButton.classList.replace("subscribed", "unsubscribed");
        subscribeButton.innerText = "Subscribe";
      }
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
});
