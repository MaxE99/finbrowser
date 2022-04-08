const subscribeButton = document.querySelector(".subscribeButton");

subscribeButton.addEventListener("click", async () => {
  try {
    const url = window.location.href;
    const index = url.lastIndexOf("/");
    const list_id = url.substring(index + 1);
    const action = subscribeButton.innerText;
    console.log(action);
    const res = await fetch(
      `../list_change_subscribtion_status/${list_id}/${action}`,
      get_fetch_settings("POST")
    );
    if (!res.ok) {
      showMessage("Error: List can't be subscribed!", "Error");
    } else {
      const context = await res.json();
      showMessage(context, "Success");
      if (action == "Subscribe") {
        subscribeButton.classList.replace("unsubscribed", "subscribed");
        subscribeButton.innerText = "Unsubscribe";
      } else {
        subscribeButton.classList.replace("subscribed", "unsubscribed");
        subscribeButton.innerText = "Subscribe";
      }
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
});
