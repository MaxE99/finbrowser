const createListMenu = document.querySelector(".createListMenu");
const overlay = document.querySelector(".overlay");

// Open settings menu
document.querySelector(".createListButton").addEventListener("click", () => {
  overlay.style.opacity = "0.5";
  createListMenu.style.display = "flex";
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

$(function () {
  $("#search").autocomplete({
    source: function (request, response) {
      $.ajax({
        url: "/home/api/lists/?search=" + request.term,
        type: "GET",
        success: function (data) {
          response(
            $.map(data, function (item) {
              return {
                label: item.name,
              };
            })
          );
        },
      });
    },
    select: function (event, ui) {
      $("#search").val(ui.item.label);
      return false;
    },
  });
});

document.querySelector(".searchButton").addEventListener("click", async () => {
  const timeframeSelect = document.getElementById("timeframe");
  const timeframe =
    timeframeSelect.options[timeframeSelect.selectedIndex].value;
  const contentTypeSelect = document.getElementById("content");
  const contentType =
    contentTypeSelect.options[contentTypeSelect.selectedIndex].innerText;
  const sourcesSelect = document.getElementById("sources");
  const sources = sourcesSelect.options[sourcesSelect.selectedIndex].innerText;
  console.log(timeframe);
  console.log(contentType);
  console.log(sources);
  try {
    const res = await fetch(
      `../filter_list/${timeframe}/${contentType}/${sources}`,
      get_fetch_settings("GET")
    );
    if (!res.ok) {
      showMessage("Error: List couldn't be filtered!", "Error");
    } else {
      const context = await res.json();
      window.location.href = "../../home/lists";
    }
  } catch (e) {
    console.log(e);
    showMessage("Error: Network error detected!", "Error");
  }
});
