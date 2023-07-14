async function deleteProfilePic(){try{let e=await fetch(`../../api/profiles/${PROFILE_ID}/`,getFetchSettings("PATCH"));e.ok?(showMessage("Profile picture has been removed!","Remove"),window.location.reload()):showMessage("Error: Profile picture could not be deleted!","Error")}catch(t){showMessage("Error: Unexpected error has occurred!","Error")}}async function changeProfilePic(e){try{let t=new FormData;t.append("profile_pic",e);let r=await fetch(`../../api/profiles/${PROFILE_ID}/`,{method:"PATCH",headers:{"X-CSRFToken":getCookie("csrftoken")},body:t});r.ok?(showMessage("Profile picture has been changed!","Success"),window.location.reload()):showMessage("Error: Network request failed unexpectedly!","Error")}catch(i){showMessage("Error: Unexpected error has occurred!","Error")}}async function deleteNotification(e,t=!1){try{let r=e.id.split("#")[1],i=await fetch(`../../api/notifications/${r}/`,getFetchSettings("DELETE"));i.ok?(t?(e.classList.remove("notificationActivated"),e.classList.replace("fa-bell-slash","fa-bell"),e.classList.replace("finButtonBlue","finButtonWhite")):e.closest(".sourceContainer")?e.closest(".sourceContainer").remove():e.closest(".keywordContainer").remove(),showMessage("Notification has been deleted!","Remove")):showMessage("Error: Network request failed unexpectedly!","Error")}catch(o){showMessage("Error: Unexpected error has occurred!","Error")}}async function reCreateSourceNotification(e){try{let t=e.closest(".contentWrapper").id.split("#")[1],r=await fetch("../../api/notifications/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify({source:t})});if(r.ok){let i=await r.json();e.id="nid#"+i.notification_id,e.classList.add("notificationActivated"),e.classList.replace("fa-bell","fa-bell-slash"),e.classList.replace("finButtonWhite","finButtonBlue"),showMessage("Notification has been added!","Success")}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(o){showMessage("Error: Unexpected error has occurred!","Error")}}location.href.endsWith("#notifications")&&changeTabsOnPageOpen(2);const PROFILE_ID=document.querySelector(".emailContainer").id.split("#")[1];document.querySelector(".removeProfilePicButton").addEventListener("click",()=>deleteProfilePic(),{once:!0}),document.querySelector(".profilePicInnerContainer input").addEventListener("change",e=>changeProfilePic(e.target.files[0])),document.querySelectorAll(".notificationContainer .fa-times").forEach(e=>e.addEventListener("click",()=>deleteNotification(e))),document.querySelectorAll(".sliderWrapper .slider .notificationButton").forEach(e=>{e.addEventListener("click",()=>{e.classList.contains("notificationActivated")?deleteNotification(e,!0):reCreateSourceNotification(e)})}),document.querySelector(".profilePicInnerContainer .changeProfilePicButton").addEventListener("click",e=>e.target.closest(".profilePicInnerContainer").querySelector("input").click());
