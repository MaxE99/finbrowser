// switch list
document
  .querySelector(".firstRow .nameContainer")
  .addEventListener("click", () => {
    const dropdownSymbol = document.querySelector(".firstRow .nameContainer i");
    const optionsContainer = document.querySelector(".listOptionsContainer");
    if (optionsContainer.style.display === "block") {
      optionsContainer.style.display = "none";
      dropdownSymbol.classList.replace("fa-chevron-up", "fa-chevron-down");
    } else {
      optionsContainer.style.display = "block";
      dropdownSymbol.classList.replace("fa-chevron-down", "fa-chevron-up");
    }
  });

// create list
document
  .querySelector(".firstRow .listOptionsContainer .createListButton")
  .addEventListener("click", async () => {
    try {
      const res = await fetch(`../../api/lists/`, get_fetch_settings("POST"));
      if (!res.ok) {
        showMessage("Error: Network request failed unexpectedly!", "Error");
      } else {
        const context = await res.json();
        window.location.replace(`../../list/${context.list_id}`);
      }
    } catch (e) {
      // showMessage("Error: Unexpected error has occurred!", "Error");
    }
  });
