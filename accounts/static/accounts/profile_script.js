document.querySelector(".openAboutButton").addEventListener("click", () => {
  document.querySelector(".bioContainer").style.display = "block";
});

document
  .querySelector(".bioContainer .fa-times")
  .addEventListener("click", () => {
    document.querySelector(".bioContainer").style.display = "none";
  });
