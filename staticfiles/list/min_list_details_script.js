const subscribeButton=document.querySelector(".subscribeButton");subscribeButton&&subscribeButton.addEventListener("click",async()=>{if(!subscribeButton.classList.contains("registrationLink"))try{let c=document.querySelector(".rightFirstRowContainer h3").id.replace("list_detail_for_",""),d=subscribeButton.innerText,a=await fetch(`https://www.finbrowser.ior.io/api/lists/${c}/list_change_subscribtion_status/`,get_fetch_settings("POST"));if(a.ok){let b=await a.json();"Subscribe"==d?(subscribeButton.classList.replace("unsubscribed","subscribed"),subscribeButton.innerText="Subscribed",showMessage(b,"Success")):(subscribeButton.classList.replace("subscribed","unsubscribed"),subscribeButton.innerText="Subscribe",showMessage(b,"Remove"))}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(e){}});const editButton=document.querySelector(".editButton"),listName=document.querySelector(".rightFirstRowContainer h3").innerText;function openEditMenu(){editButton.remove(),check_device_width_below(500)&&(document.querySelector(".notificationAndSubscribtionContainer .fa-bell").style.display="none"),document.querySelector(".rightFirstRowContainer h3").style.display="none",document.querySelector(".nameChangeContainer").style.display="block",document.querySelector(".nameChangeContainer #id_name").value=listName,document.querySelector(".listPictureContainer #id_list_pic").style.display="block",document.querySelector(".fa-camera").style.display="block",document.querySelector(".buttonContainer").style.display="flex",document.querySelector(".addSourcesButton").style.display="flex",document.querySelectorAll(".highlightedArticlesContainer .article .fa-ellipsis-h").forEach(a=>{a.style.display="none"}),document.querySelectorAll(".article .fa-times").forEach(a=>{a.style.display="block",a.addEventListener("click",async()=>{try{let b=await fethttps://www.finbrowser.ioowser.io/api/lists/${document.querySelector(".rightFirstRowContainer h3").id.replace("list_detail_for_","")}/delete_article_from_list/${a.parentElement.id.replace("article","")}/`,get_fetch_settings("DELETE"));if(b.ok){let c=await b.json();showMessage(c,"Remove"),a.parentElement.remove()}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(d){}})}),document.querySelectorAll(".sourceDeleteOption").forEach(a=>{"none"!=a.style.display&&a.style.display||(a.style.display="block",a.addEventListener("click",async()=>{try{let b=awaithttps://www.finbrowser.ioinbrowser.io/api/lists/${document.querySelector(".rightFirstRowContainer h3").id.replace("list_detail_for_","")}/delete_source_from_list/${a.id.replace("source_id_","")}/`,get_fetch_settings("DELETE"));if(b.ok){let c=await b.json();showMessage(c,"Remove"),a.parentElement.parentElement.remove()}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(d){}}))})}editButton&&editButton.addEventListener("click",openEditMenu);const sources=document.querySelectorAll(".slider-content li");1===sources.length&&openEditMenu(),document.querySelector(".deleteListButton")&&document.querySelector(".deleteListButton").addEventListener("click",async()=>{try{let a=ahttps://www.finbrowser.ioww.finbrowser.io/api/lists/${document.querySelector(".rightFirstRowContainer h3").id.replace("list_detail_for_","")}/`,get_fetch_settings("DELETE"));if(a.ok){let b=await a.json();showMessage(b,"Remove"),windowhttps://www.finbrowser.io://www.finbrowser.io/lists"}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(c){}}),document.querySelector(".addSourcesButton")&&document.querySelector(".addSourcesButton").addEventListener("click",()=>{document.querySelector(".addSourcesForm").style.display="flex"}),document.querySelector(".addSourcesForm .closeFormContainerButton")&&document.querySelector(".addSourcesForm .closeFormContainerButton").addEventListener("click",()=>{document.querySelector(".addSourcesForm").style.display="none"});let selected_sources=[];document.querySelector(".addSourcesForm #textInput")&&document.querySelector(".addSourcesForm #textInput").addEventListener("keyup",async function(h){let b=document.querySelector(".addSourcesForm #textInput").value,a=document.querySelector(".addSourcesForm #searchResultsContainer"),c=document.querySelector(".addSourcesForm .selectionContainer"),g=document.querySelector(".rightFirstRowContainer h3").id.replace("list_detail_for_","");if(b&&""!=b.replaceAll(/\s/g,"")){a.style.display="block",c.style.display="none";tryhttps://www.finbrowser.iottps://www.finbrowser.io/api/sources/?list_search=${b}&list_id=${g}`,get_fetch_settings("GET"));if(d.ok){let e=await d.json();a.innerHTML="";let f=document.createElement("div");f.innerText="Results:",a.append(f),e.length>0&&e.forEach(b=>{if(!1==selected_sources.includes(b.source_id)){let d=document.createElement("div");d.classList.add("searchResult");let f=document.createElement("img");f.src=`/static/${b.favicon_path}`;let e=document.createElement("span");e.innerText=b.name,e.id=`source_id_${b.source_id}`,d.append(f,e),a.appendChild(d),d.addEventListener("click",function f(){d.removeEventListener("click",f),selected_sources.push(b.source_id);let e=document.createElement("i");e.classList.add("fas","fa-trash"),e.addEventListener("click",()=>{e.parentElement.remove(),selected_sources=selected_sources.filter(function(a){return a.toString()!==e.previousElementSibling.id.replace("source_id_","")})}),d.appendChild(e),c.appendChild(d),a.style.display="none",c.style.display="block",document.querySelector(".addSourcesForm #textInput").value=""})}})}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(i){}}else a.style.display="none",c.style.display="block"}),document.querySelector(".addSourcesForm button")&&document.querySelector(".addSourcesForm button").addEventListener("click",async()=>{let b=document.querySelector(".rightFirstRowContainer h3").id.replace("list_detail_for_","");if(selected_sources.length){selected_sources=selected_sources.join()https://www.finbrowser.ioh(`https://www.finbrowser.io/api/lists/${b}/add_sources_to_list/${selected_sources}/`,get_fetch_settings("POST"));if(a.ok){let c=await a.json();showMessage(c,"Success"),window.location.reload()}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(d){}}else showMessage("You need to select sources!","Error")});const notificationButton=document.querySelector(".notificationAndSubscribtionContainer .fa-bell");notificationButton&&notificationButton.addEventListener("click",asynchttps://www.finbrowser.iofetch("https://www.finbrowser.io/api/notifications/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify({list_id:document.querySelector(".rightFirstRowContainer h3").id.replace("list_detail_for_","")})});if(a.ok){let b=await a.json();notificationButton.classList.contains("notificationActivated")?(notificationButton.classList.remove("notificationActivated"),showMessage(b,"Remove")):(notificationButton.classList.add("notificationActivated"),showMessage(b,"Success"))}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(c){}});const one=document.getElementById("first"),two=document.getElementById("second"),three=document.getElementById("third"),four=document.getElementById("fourth"),five=document.getElementById("fifth"),confirmBox=document.getElementById("confirm-box"),handleStarSelect=(c,d)=>{let b=d.children;for(let a=0;a<b.length;a++)a<c?b[a].classList.add("checked"):b[a].classList.remove("checked")},handleSelect=b=>{let a=document.querySelector(".rate-form");switch(b){case"first":handleStarSelect(1,a);return;case"second":handleStarSelect(2,a);return;case"third":handleStarSelect(3,a);return;case"fourth":handleStarSelect(4,a);return;case"fifth":handleStarSelect(5,a);return;default:handleStarSelect(0,a)}},getNumericValue=a=>"first"===a?1:"second"===a?2:"third"===a?3:"fourth"===a?4:"fifth"===a?5:0;one&&[one,two,three,four,five].forEach(a=>a.addEventListener("mouseover",a=>{handleSelect(a.target.id)})),document.querySelectorAll(".rankingStar").forEach(a=>{a.addEventListener("click",async b=>{let c=getNumericValue(b.target.id),d=document.querySelector(".rightFirstRowContainer h3").id.replace("list_detail_fhttps://www.finbrowser.ioait fetch("https://www.finbrowser.io/api/list_ratings/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify({list_id:d,rating:c})});if(a.ok){let e=await a.json();showMessage(e,"Success"),window.location.reload()}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(f){}})}),document.querySelector(".avgRating span")&&handleStarSelect(Math.round(document.querySelector(".avgRating span").innerText),document.querySelector(".ratedContainer"));const rateListButton=document.querySelector(".rateListButton");rateListButton&&rateListButton.addEventListener("click",()=>{rateListButton.classList.contains("registrationLink")||(document.querySelector(".rate-formUpperContainer").style.display="block",document.querySelector(".rating").style.opacity="0",document.querySelector(".ratingsAmmountContainer").style.opacity="0",document.querySelector(".rateListButton").style.opacity="0",document.querySelector(".rankingsHeader").style.opacity="0")})
