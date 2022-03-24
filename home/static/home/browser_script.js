const searchSettingsMenu = document.querySelector(".searchSettingsMenu");
const addSourcesMenu = document.querySelector(".addSourcesMenu");
const overlay = document.querySelector(".overlay");
let isPopUpOpen = false;
let isCategoryDeleteOptionOpen = false;
let currentDraggedObject;

function preparePageForMenu() {
  document.querySelectorAll(".popUpMenu").forEach((menu) => {
    menu.style.display = "none";
  });
  overlay.style.settings = "0.5";
}

// Open settings menu
document.querySelector(".settingsButton").addEventListener("click", () => {
  preparePageForMenu();
  searchSettingsMenu.style.display = "flex";
});

//Open add source Menu
document.querySelector(".addSourceButton").addEventListener("click", () => {
  preparePageForMenu();
  addSourcesMenu.style.display = "block";
});

// Close menus
document
  .querySelectorAll(".closeMenuButton, .closeButton")
  .forEach((button) => {
    button.addEventListener("click", () => {
      overlay.style.opacity = "1";
      document.querySelectorAll(".popUpMenu").forEach((menu) => {
        menu.style.display = "none";
      });
    });
  });

// use DRF to delete sources from database

document
  .querySelector(".deleteSourceButton")
  .addEventListener("click", async () => {
    if (!isPopUpOpen) {
      isPopUpOpen = true;
      document
        .querySelectorAll(".sourceDeleteOptionOff")
        .forEach((deleteOption) =>
          deleteOption.classList.replace(
            "sourceDeleteOptionOff",
            "sourceDeleteOptionOn"
          )
        );
      document
        .querySelectorAll(".sourceDeleteOptionOn")
        .forEach((deleteOption) => {
          deleteOption.addEventListener("click", async () => {
            try {
              domain = deleteOption.parentElement.nextElementSibling.innerText;
              const res = await fetch(
                `../delete_source/${domain}`,
                get_fetch_settings("DELETE")
              );
              if (!res.ok) {
                showMessage("Error: Source couldn't be deleted!", "Error");
              } else {
                const context = await res.json();
                showMessage(context, "Success");
                deleteOption.parentElement.parentElement.remove();
                //remove deleted source from search settings menu
                const sourceOptions =
                  document.querySelectorAll("#id_sources label");
                for (let i = 0, j = sourceOptions.length; i < j; i++) {
                  if (sourceOptions[i].innerText.trim() == domain) {
                    sourceOptions[i].parentElement.remove();
                    break;
                  }
                }
              }
            } catch (e) {
              showMessage("Error: Network error detected!", "Error");
            }
          });
        });
    }
    // close delete options when delete sources button is clicked again
    else {
      document
        .querySelectorAll(".sourceDeleteOptionOn")
        .forEach((deleteOption) =>
          deleteOption.classList.replace(
            "sourceDeleteOptionOn",
            "sourceDeleteOptionOff"
          )
        );
      isPopUpOpen = false;
    }
  });

// use DRF to add new category to database

document.querySelector(".addCategoryButton").addEventListener("click", () => {
  async function addCategory() {
    browserCategory.innerText = categoryNameInput.value;
    browserCategory.innerHTML +=
      '<i class="fas fa-times categoryDeleteOptionOff"></i>';
    categoryNameInput.remove();
    newCategory = browserCategory.innerText;
    activateDragAndDrop();
    try {
      const res = await fetch(
        `../add_category/${newCategory}`,
        get_fetch_settings("POST")
      );
      if (!res.ok) {
        showMessage("Error: Category couldn't be added!", "Error");
      } else {
        const context = await res.json();
        showMessage(context, "Success");
        //Add option to add sources selects
        const options = document.querySelectorAll("#id_category option");
        const newOption = document.createElement("option");
        newOption.value = newCategory;
        newOption.innerText = newCategory;
        if (options.length < 2) {
          document.querySelector("#id_category").appendChild(newOption);
        } else {
          for (let i = 1, j = options.length; i < j; i++) {
            if (options[i].innerText > newCategory) {
              options[i].parentElement.insertBefore(newOption, options[i]);
              break;
            } else if (i == options.length - 1) {
              document.querySelector("#id_category").appendChild(newOption);
            }
          }
        }
      }
    } catch (e) {
      showMessage("Error: Network error detected!", "Error");
    }
  }
  const browserCategory = document.createElement("div");
  browserCategory.classList.add("browserCategory");
  const categoryNameInput = document.createElement("input");
  categoryNameInput.placeholder = "Add name of category";
  categoryNameInput.classList.add("categoryNameInput");
  categoryNameInput.addEventListener("blur", () => {
    addCategory();
  });
  categoryNameInput.addEventListener("keyup", function (event) {
    if (event.key == "Enter") {
      addCategory();
    }
  });
  browserCategory.appendChild(categoryNameInput);
  const categoryContainer = document.createElement("div");
  categoryContainer.classList.add("categoryContainer");
  const browserSourcesContainer = document.querySelector(
    ".browserSourcesContainer"
  );
  browserSourcesContainer.append(browserCategory, categoryContainer);
});

// use DRF to delete categories from database

document
  .querySelector(".deleteCategoryButton")
  .addEventListener("click", () => {
    // make delete Button visible
    if (!isCategoryDeleteOptionOpen) {
      isCategoryDeleteOptionOpen = true;
      document
        .querySelectorAll(".categoryDeleteOptionOff")
        .forEach((deleteOption) =>
          deleteOption.classList.replace(
            "categoryDeleteOptionOff",
            "categoryDeleteOptionOn"
          )
        );
      document
        .querySelectorAll(".categoryDeleteOptionOn")
        .forEach((deleteOption) => {
          deleteOption.addEventListener("click", async () => {
            const removedCategory = deleteOption.parentElement.innerText;
            // remove Category and Category Container
            deleteOption.parentElement.nextElementSibling.remove();
            deleteOption.parentElement.remove();
            try {
              const res = await fetch(
                `../delete_category/${removedCategory}`,
                get_fetch_settings("DELETE")
              );
              if (!res.ok) {
                showMessage("Error: Category couldn't be deleted!", "Error");
              } else {
                const context = await res.json();
                showMessage(context, "Success");
                const options = document.querySelectorAll(
                  "#id_category option"
                );
                for (let i = 0, j = options.length; i < j; i++) {
                  if (options[i].innerText == removedCategory) {
                    options[i].remove();
                    break;
                  }
                }
              }
            } catch (e) {
              showMessage("Error: Network error detected!", "Error");
            }
          });
        });
    } else {
      document
        .querySelectorAll(".categoryDeleteOptionOn")
        .forEach((deleteOption) =>
          deleteOption.classList.replace(
            "categoryDeleteOptionOn",
            "categoryDeleteOptionOff"
          )
        );
      isCategoryDeleteOptionOpen = false;
    }
  });

// Drag and drop functionality is used as a function so that when new category is added
// function can be called to allow sources to be dropped into the new category
function activateDragAndDrop() {
  document.querySelectorAll(".categoryContainer").forEach((container) => {
    container.addEventListener("dragover", function (e) {
      e.preventDefault();
    });
    container.addEventListener("dragenter", function (e) {
      e.preventDefault();
      this.className += " hovered";
    });
    container.addEventListener("dragleave", function (e) {
      this.className = "categoryContainer";
    });
    container.addEventListener("drop", async function (e) {
      this.className = "categoryContainer";
      this.append(currentDraggedObject);
      const sourceName = currentDraggedObject.querySelector(
        ".sourceNameContainer"
      ).innerText;
      const newCategory = this.previousElementSibling.innerText;
      // use DRF to update category of dropped source in the database
      try {
        const res = await fetch(
          `../change_category/${sourceName}/${newCategory}`,
          get_fetch_settings("POST")
        );
        if (!res.ok) {
          showMessage("Error: Category couldn't be changed!", "Error");
        } else {
          const context = await res.json();
          showMessage(context, "Success");
        }
      } catch (e) {
        showMessage("Error: Network error detected!", "Error");
      }
    });
  });
  document.querySelectorAll(".sourceContainer").forEach((dragSource) => {
    dragSource.addEventListener("dragstart", function (e) {
      currentDraggedObject = this;
    });
  });
}

activateDragAndDrop();
