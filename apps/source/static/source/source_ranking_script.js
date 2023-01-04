// document
//   .querySelectorAll(".sliderWrapper .slider .subscribeButton")
//   .forEach((subscribeButton) => {
//     subscribeButton.addEventListener("click", async () => {
//       try {
//         const source_id = subscribeButton
//           .closest(".contentWrapper")
//           .id.split("#")[1];
//         const action = subscribeButton.innerText;
//         const res = await fetch(
//           `../../api/sources/${source_id}/source_change_subscribtion_status/`,
//           get_fetch_settings("POST")
//         );
//         if (!res.ok) {
//           showMessage("Error: Network request failed unexpectedly!", "Error");
//         } else {
//           const context = await res.json();
//           if (action == "Subscribe") {
//             subscribeButton.classList.add("subscribed");
//             subscribeButton.innerText = "Subscribed";
//             showMessage(context, "Success");
//           } else {
//             subscribeButton.classList.remove("subscribed");
//             subscribeButton.innerText = "Subscribe";
//             showMessage(context, "Remove");
//           }
//         }
//       } catch (e) {
//         // showMessage("Error: Unexpected error has occurred!", "Error");
//       }
//     });
//   });
