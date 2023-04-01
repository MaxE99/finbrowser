const subscribeButtons=document.querySelectorAll(".subscribeButton");subscribeButtons.forEach(e=>{e.addEventListener("click",async()=>{if(!e.classList.contains("openAuthPrompt"))try{let t=e.closest(".firstRow").querySelector("h2").id.split("#")[1],i=e.innerText,r=await fetch(`../../api/sources/${t}/`,get_fetch_settings("PATCH"));r.ok?"Subscribe"==i?(e.classList.replace("unsubscribed","subscribed"),e.innerText="Subscribed",showMessage(context="SOURCE HAS BEEN SUBSCRIBED!","Success")):(e.classList.replace("subscribed","unsubscribed"),e.innerText="Subscribe",showMessage(context="SOURCE HAS BEEN UNSUBSCRIBED!","Remove")):showMessage("Error: Network request failed unexpectedly!","Error")}catch(o){}})});const notificationButton=document.querySelector(".firstRow .notificationButton");notificationButton.classList.contains("openAuthPrompt")||notificationButton.addEventListener("click",async()=>{if(notificationButton.classList.contains("fa-bell"))try{let e=notificationButton.closest(".firstRow").querySelector("h2").id.split("#")[1],t={source:e},i=await fetch("../../api/notifications/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(t)});if(i.ok){let r=await i.json();notificationButton.id="nid#"+r.notification_id,notificationButton.classList.add("notificationActivated"),notificationButton.classList.replace("fa-bell","fa-bell-slash"),showMessage("Notification has been added!","Success")}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(o){}else{let n=notificationButton.id.split("#")[1];try{let a=await fetch(`../../api/notifications/${n}/`,get_fetch_settings("DELETE"));a.ok?(notificationButton.classList.remove("notificationActivated"),notificationButton.classList.replace("fa-bell-slash","fa-bell"),showMessage(context="Notification has been removed!","Remove")):showMessage("Error: Network request failed unexpectedly!","Error")}catch(s){}}}),document.querySelectorAll(".rightSideContainer .ratingContainer .infoContainer .rateSpan").forEach(e=>{e.classList.contains("openAuthPrompt")||e.addEventListener("click",()=>{let e=document.querySelector(".pageWrapper .firstRow h2").innerText;document.querySelector(".sourceRatingsWrapper").style.display="flex",document.querySelector(".sourceRatingsWrapper .header h3").innerText="Rate "+e,setModalStyle()})}),document.querySelector(".sourceRatingsWrapper .ratingsContainer .header .fa-times").addEventListener("click",()=>{document.querySelector(".sourceRatingsWrapper").style.display="none",removeModalStyle()});const ratingsButtons=document.querySelectorAll(".sourceRatingsWrapper .ratingsContainer .ratingsButtonContainer button");ratingsButtons.forEach(e=>e.addEventListener("click",()=>{ratingsButtons.forEach(e=>e.classList.remove("selectedRating")),e.classList.add("selectedRating")}));let activatedButton=!1;document.querySelector(".sourceRatingsWrapper .ratingsContainer .rateSourceButton").addEventListener("click",async()=>{let e=document.querySelector(".firstRow h2").id.split("#")[1],t=document.querySelector(".sourceRatingsWrapper .ratingsContainer .ratingsButtonContainer .selectedRating")?.innerText;if(body={source:e,rating:t},t&&!activatedButton){activatedButton=!0;try{let i=await fetch("../../api/source_ratings/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(body)});i.ok?(showMessage(context="Rating has been saved!","Success"),window.location.reload()):showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){}}else showMessage("Select a rating!","Error")}),document.querySelector(".pageWrapper .firstRow .notificationAndSubscribtionContainer  .fa-ellipsis-h").addEventListener("click",e=>{if(!e.target.classList.contains("openAuthPrompt")){setModalStyle();let t=document.querySelector(".pageWrapper .firstRow h2").id.split("#")[1],i=document.querySelector(".pageWrapper .firstRow h2").innerText;document.querySelector(".fullScreenPlaceholder .addToListForm h2 span").innerText=i,document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .addSourceToListForm").style.display="block",document.querySelector(".fullScreenPlaceholder .addSourceToListForm").id="source_id"+t;let r=document.querySelectorAll(".fullScreenPlaceholder .listContainer input:first-of-type");r.forEach(e=>{let i=e.closest(".listContainer").querySelector(".sourcesInList").value;JSON.parse(i).includes(parseInt(t))?e.checked=!0:e.checked=!1})}});