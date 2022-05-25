document.querySelector(".openAboutButton").addEventListener("click", () => {
  document.querySelector(".bioContainer").style.display = "block";
  document.querySelector(".profileBioOverlay").style.opacity = 0.1;
});

document
  .querySelector(".bioContainer .browserCategory .fa-times")
  .addEventListener("click", () => {
    document.querySelector(".bioContainer").style.display = "none";
    document.querySelector(".profileBioOverlay").style.opacity = 1;
  });
