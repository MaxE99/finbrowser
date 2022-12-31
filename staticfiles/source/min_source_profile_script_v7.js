const subscribeButtons=document.querySelectorAll(".subscribeButton");subscribeButtons.forEach(e=>{e.addEventListener("click",async()=>{if(!e.classList.contains("registrationLink"))try{let t=e.closest(".upperContainer").querySelector(".upperInnerContainer h3").id.split("#")[1],r=e.innerText,o=await fetch(`../../api/sources/${t}/source_change_subscribtion_status/`,get_fetch_settings("POST"));if(o.ok){let i=await o.json();"Subscribe"==r?(e.classList.replace("unsubscribed","subscribed"),e.innerText="Subscribed",showMessage(i,"Success")):(e.classList.replace("subscribed","unsubscribed"),e.innerText="Subscribe",showMessage(i,"Remove"))}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(s){}})});const one=document.getElementById("first"),two=document.getElementById("second"),three=document.getElementById("third"),four=document.getElementById("fourth"),five=document.getElementById("fifth"),confirmBox=document.getElementById("confirm-box"),handleStarSelect=(e,t)=>{let r=t.children;for(let o=0;o<r.length;o++)o<e?r[o].classList.add("checked"):r[o].classList.remove("checked")},handleSelect=e=>{let t=document.querySelector(".rate-form");switch(e){case"first":handleStarSelect(1,t);return;case"second":handleStarSelect(2,t);return;case"third":handleStarSelect(3,t);return;case"fourth":handleStarSelect(4,t);return;case"fifth":handleStarSelect(5,t);return;default:handleStarSelect(0,t)}},getNumericValue=e=>{let t;return"first"===e?1:"second"===e?2:"third"===e?3:"fourth"===e?4:"fifth"===e?5:0};if(one){let e=[one,two,three,four,five];e.forEach(e=>e.addEventListener("mouseover",e=>{handleSelect(e.target.id)}))}if(document.querySelectorAll(".rankingStar").forEach(e=>{e.addEventListener("click",async e=>{let t=e.target.id,r=getNumericValue(t),o=document.querySelector(".upperInnerContainer h3").id.split("#")[1];try{let i={source_id:o,rating:r},s=await fetch("../../api/source_ratings/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(i)});if(s.ok){let n=await s.json();showMessage(n,"Success"),window.location.reload()}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(c){}})}),document.querySelector(".avgRating span")){let t=Math.round(document.querySelector(".avgRating span").innerText);handleStarSelect(t,document.querySelector(".ratedContainer"))}document.querySelectorAll(".openRateListButton").forEach(e=>{e.addEventListener("click",()=>{let t=e.closest(".upperContainer");t.querySelector(".rate-formUpperContainer").style.display="block",t.querySelector(".rating").style.opacity="0",t.querySelector(".ratingsAmmountContainer").style.opacity="0",t.querySelector(".rateListButton").style.opacity="0",t.querySelector(".rankingsHeader").style.opacity="0"})});const notificationButtons=document.querySelectorAll(".notificationAndSubscribtionContainer .notificationButton");function check_list_status(e){let t=[],r=[],o=e.closest(".addSourceToListForm").querySelectorAll(".listContainer input");for(let i=0,s=o.length;i<s;i++)"sourceInList"===o[i].className&&!1===o[i].checked?r.push(o[i].id.split("id_list_")[1]):"sourceNotInList"===o[i].className&&o[i].checked&&t.push(o[i].id.split("id_list_")[1]);return[t,r]}notificationButtons.forEach(e=>{e&&e.addEventListener("click",async()=>{try{let t=e.closest(".upperContainer").querySelector(".upperInnerContainer h3").id.split("#")[1],r={source_id:t},o=await fetch("../../api/notifications/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(r)});if(o.ok){let i=await o.json();e.classList.contains("notificationActivated")?(e.classList.remove("notificationActivated"),e.classList.replace("fa-bell-slash","fa-bell"),showMessage(i,"Remove")):(e.classList.add("notificationActivated"),e.classList.replace("fa-bell","fa-bell-slash"),showMessage(i,"Success"))}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(s){}})}),document.querySelectorAll(".addSourceToListButton").forEach(e=>{e.addEventListener("click",()=>{e.closest(".upperContainer").querySelector(".addSourceToListForm").style.display="block"})}),document.querySelectorAll(".addSourceToListForm .fa-times").forEach(e=>{e.addEventListener("click",()=>{document.querySelector(".addSourceToListForm").style.display="none"})}),document.querySelectorAll(".addSourceToListForm .saveButton").forEach(e=>{e.addEventListener("click",async()=>{let t=e.closest(".upperContainer").querySelector(".upperInnerContainer .sourceName").id.split("#")[1],[r,o]=check_list_status(e);body={source_id:t,add_lists:r,remove_lists:o};try{let i=await fetch("../../api/lists/change_source_status_from_lists/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(body)});if(i.ok){let s=await i.json();showMessage(s,"Success"),window.location.reload()}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(n){}})});