if(location.href.endsWith("#notifications")){let e=document.querySelectorAll(".tabsContainer button"),t=document.querySelectorAll(".tabsContent");for(let i=0,o=e.length;i<o;i++)e[i].classList.remove("activatedTab"),t[i].classList.remove("tabsContentActive");e[2].classList.add("activatedTab"),t[2].classList.add("tabsContentActive")}document.querySelector(".removeProfilePicButton").addEventListener("click",async()=>{let e=document.querySelector(".emailContainer").id.split("#")[1];try{let t=await fetch(`../../api/profiles/${e}/`,get_fetch_settings("PATCH"));t.ok?(showMessage(context="Profile picture has been removed!","Remove"),window.location.reload()):showMessage("Error: Profile picture could not be deleted!","Error")}catch(i){}},{once:!0}),document.querySelectorAll(".notificationContainer .fa-times").forEach(e=>{e.addEventListener("click",async()=>{try{let t=e.id.split("#")[1],i=await fetch(`../../api/notifications/${t}/`,get_fetch_settings("DELETE"));i.ok?(e.closest(".sourceContainer")?e.closest(".sourceContainer").remove():e.closest(".keywordContainer").remove(),showMessage("Notification has been deleted!","Remove")):showMessage("Error: Network request failed unexpectedly!","Error")}catch(o){}})}),document.querySelector(".profilePicInnerContainer .changeProfilePicButton").addEventListener("click",e=>{e.target.closest(".profilePicInnerContainer").querySelector("input").click()}),document.querySelector(".profilePicInnerContainer input").addEventListener("change",async e=>{let t=document.querySelector(".emailContainer").id.split("#")[1];try{let i=new FormData;i.append("profile_pic",e.target.files[0]);let o=await fetch(`../../api/profiles/${t}/`,{method:"PATCH",headers:{"X-CSRFToken":getCookie("csrftoken")},body:i});o.ok?(showMessage(context="Profile picture has been added!","Success"),window.location.reload()):showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){}}),document.querySelectorAll(".sliderWrapper .slider .notificationButton").forEach(e=>{e.addEventListener("click",async()=>{if(e.classList.contains("notificationActivated")){let t=e.id.split("#")[1];try{let i=await fetch(`../../api/notifications/${t}/`,get_fetch_settings("DELETE"));i.ok?(e.classList.remove("notificationActivated"),e.classList.replace("fa-bell-slash","fa-bell"),e.classList.replace("finButtonBlue","finButtonWhite"),showMessage(context="Notification has been removed!","Remove")):showMessage("Error: Network request failed unexpectedly!","Error")}catch(o){}}else try{let r=e.closest(".contentWrapper").id.split("#")[1],a={source:r},n=await fetch("../../api/notifications/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(a)});if(n.ok){let c=await n.json();e.id="nid#"+c.notification_id,e.classList.add("notificationActivated"),e.classList.replace("fa-bell","fa-bell-slash"),e.classList.replace("finButtonWhite","finButtonBlue"),showMessage("Notification has been added!","Success")}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(l){}})});