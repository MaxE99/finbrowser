document.querySelectorAll(".sourceRankingContainer .subscribeButton").forEach(e=>{e.addEventListener("click",async()=>{if(!e.classList.contains("openAuthPrompt"))try{let t=e.closest(".sourceRankingContainer").id.split("#")[1],r=e.innerText,n=await fetch(`../../api/sources/${t}/`,get_fetch_settings("PATCH"));n.ok?"Subscribe"==r?(e.classList.add("subscribed"),e.classList.replace("finButtonWhite","finButtonBlue"),e.innerText="Subscribed",showMessage(context="SOURCE HAS BEEN SUBSCRIBED!","Success")):(e.classList.remove("subscribed"),e.classList.replace("finButtonBlue","finButtonWhite"),e.innerText="Subscribe",showMessage(context="SOURCE HAS BEEN UNSUBSCRIBED!","Remove")):showMessage("Error: Network request failed unexpectedly!","Error")}catch(l){}})}),document.querySelectorAll(".thirdRow .tag").forEach(e=>e.addEventListener("click",()=>{document.querySelectorAll(".selectedTagsContainer").forEach(t=>{let r=[];if(t.querySelectorAll("li").forEach(e=>{r.push(e.innerText)}),!r.includes(e.innerText)){let n=document.createElement("li");n.classList.add("selectedOption"),n.setAttribute("value",e.innerText),n.innerText=e.innerText;let l=document.createElement("input");l.setAttribute("hidden",!0),l.setAttribute("name","tag"),l.setAttribute("value",e.innerText);let o=document.createElement("i");n.appendChild(l),n.appendChild(o),o.classList.add("fas","fa-times"),o.addEventListener("click",()=>{n.remove()}),t.appendChild(n)}})})),document.querySelectorAll(".selectedTagsContainer li i").forEach(e=>e.addEventListener("click",()=>{e.closest("li").remove()})),document.querySelectorAll("form .tagInputSearch").forEach(e=>e.addEventListener("keypress",function(e){"Enter"===e.key&&e.preventDefault()}));const websiteDropdown=document.querySelectorAll(".filterSidebar form .websiteDropdown, .horizontalFilterMenu form .websiteDropdown").forEach(e=>e.addEventListener("click",t=>{e.closest("form").querySelector(".sectorList").style.display="none",e.closest("form").querySelector(".selectionList").style.display="none";let r=t.target.tagName.toUpperCase();"LI"!==r&&"INPUT"!==r&&("block"!==t.target.querySelector("ul").style.display?t.target.querySelector("ul").style.display="block":t.target.querySelector("ul").style.display="none",document.onclick=function(t){t.target.closest(".websiteList")||t.target===e||(e.querySelector("ul").style.display="none")})})),sectorDropdown=document.querySelectorAll(".filterSidebar form .sectorDropdown, .horizontalFilterMenu form .sectorDropdown").forEach(e=>e.addEventListener("click",t=>{e.closest("form").querySelector(".websiteList").style.display="none",e.closest("form").querySelector(".selectionList").style.display="none";let r=t.target.tagName.toUpperCase();"LI"!==r&&"INPUT"!==r&&("block"!==t.target.querySelector("ul").style.display?t.target.querySelector("ul").style.display="block":t.target.querySelector("ul").style.display="none",document.onclick=function(t){t.target.closest(".sectorList")||t.target===e||(e.querySelector("ul").style.display="none")})}));function selectFilterOption(e){let t=e.closest(".selectContainer"),r=e.closest("form").querySelector(".selectedTagsContainer"),n=e.cloneNode(!0);n.classList.add("selectedOption");let l=document.createElement("i");l.classList.add("fas","fa-times"),l.addEventListener("click",()=>{n.remove()});let o=document.createElement("input");o.setAttribute("hidden",!0),o.setAttribute("name","tag"),o.setAttribute("value",n.innerText),n.appendChild(o),n.appendChild(l),e.style.display="none",r.appendChild(n),r.style.display="flex",t.querySelector("ul").style.display="none"}document.querySelectorAll("form .tagInputSearch").forEach(e=>e.addEventListener("keyup",async function(){let t=e.value,r=e.closest("form").querySelector("#tagAutocomplete_result ul");if(t&&""!=t.replaceAll(/\s/g,"")){try{let n=await fetch(`../../../../../../api/source_tags/?search_term=${t}`,get_fetch_settings("GET"));if(n.ok){let l=await n.json(),o=[];document.querySelectorAll(".selectedTagsContainer li").forEach(e=>o.push(e.innerText)),l.length>0?(r.style.display="block",r.innerHTML="",l.forEach(e=>{if(!o.includes(e.name)){let t=document.createElement("li");t.setAttribute("value",e.name),t.innerText=e.name,t.addEventListener("click",()=>{selectFilterOption(t)}),r.appendChild(t)}})):r.style.display="none"}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(a){}document.onclick=function(e){"autocomplete_list_results"!==e.target.id&&(r.style.display="none")}}else r.style.display="none"})),document.querySelectorAll(".selectionList li").forEach(e=>{e.addEventListener("click",()=>{selectFilterOption(e)})}),document.querySelectorAll("form .selectContainer .dropdown li").forEach(e=>e.addEventListener("click",e=>{"INPUT"!==e.target.tagName.toUpperCase()&&(e.target.querySelector("input").checked?e.target.querySelector("input").checked=!1:e.target.querySelector("input").checked=!0)})),document.querySelectorAll("form .choiceContainer").forEach(e=>e.addEventListener("click",e=>{e.target.querySelector("input")&&(e.target.querySelector("input").checked?e.target.querySelector("input").checked=!1:e.target.querySelector("input").checked=!0)})),document.querySelectorAll(".sourceAddToListButton").forEach(e=>{e.addEventListener("click",e=>{if(setModalStyle(),!e.target.classList.contains("openAuthPrompt")){let t=e.target.closest(".sourceRankingContainer").id.split("#")[1],r=e.target.closest(".sourceRankingContainer").querySelector(".firstRow a span:last-of-type").innerText;document.querySelector(".fullScreenPlaceholder .addToListForm h2 span").innerText=r,document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .addSourceToListForm").style.display="block",document.querySelector(".fullScreenPlaceholder .addSourceToListForm").id="source_id"+t;let n=document.querySelectorAll(".fullScreenPlaceholder .listContainer input:first-of-type");n.forEach(e=>{let r=e.closest(".listContainer").querySelector(".sourcesInList").value;JSON.parse(r).includes(parseInt(t))?e.checked=!0:e.checked=!1}),document.querySelector(".fullScreenPlaceholder .addSourceToListForm .cancelButton")?.addEventListener("click",()=>{n.forEach(e=>{let r=e.closest(".listContainer").querySelector(".sourcesInList").value;JSON.parse(r).includes(parseInt(t))?e.checked=!0:e.checked=!1})})}})}),document.querySelector(".openFiltersButton").addEventListener("click",()=>{document.querySelector(".horizontalFilterMenu").style.display="flex",document.querySelector(".pageWrapper").style.opacity="0.1"}),document.querySelector(".horizontalFilterMenu .discardButton").addEventListener("click",()=>{document.querySelector(".horizontalFilterMenu").style.display="none",document.querySelector(".pageWrapper").removeAttribute("style")}),document.querySelectorAll(".sourceRankingContainer .infoContainer .rateSpan").forEach(e=>{e.classList.contains("openAuthPrompt")||e.addEventListener("click",e=>{let t=null;e.target.classList.contains("notRated")||document.querySelectorAll(".sourceRatingsContainer .ratingsButtonContainer button").forEach(r=>{r.innerText==e.target.innerText&&(r.classList.add("selectedRating"),t=e.target.innerText)}),document.querySelector(".sourceRatingsWrapper .ratingsContainer .cancelButton")?.addEventListener("click",()=>{document.querySelectorAll(".sourceRatingsContainer .ratingsButtonContainer button").forEach(e=>{e.classList.remove("selectedRating"),e.innerText==t&&e.classList.add("selectedRating")})});let r=e.target.closest(".sourceRankingContainer").querySelector(".firstRow a span:last-of-type").innerText,n=e.target.closest(".sourceRankingContainer").id.split("#")[1];document.querySelector(".sourceRatingsWrapper").id=n,document.querySelector(".sourceRatingsWrapper").style.display="flex",document.querySelector(".sourceRatingsWrapper .header h3").innerHTML=`Rate <span>${r}</span>`,setModalStyle()})}),document.querySelector(".sourceRatingsWrapper .ratingsContainer .header .fa-times").addEventListener("click",()=>{document.querySelector(".sourceRatingsContainer .ratingsButtonContainer .selectedRating")&&document.querySelector(".sourceRatingsContainer .ratingsButtonContainer .selectedRating").classList.remove("selectedRating"),document.querySelector(".sourceRatingsWrapper").style.display="none",removeModalStyle()});const ratingsButtons=document.querySelectorAll(".sourceRatingsWrapper .ratingsContainer .ratingsButtonContainer button");ratingsButtons.forEach(e=>e.addEventListener("click",()=>{ratingsButtons.forEach(e=>e.classList.remove("selectedRating")),e.classList.add("selectedRating")}));let activatedButton=!1;document.querySelector(".sourceRatingsWrapper .ratingsContainer .rateSourceButton").addEventListener("click",async()=>{let e=document.querySelector(".sourceRatingsWrapper").id,t=document.querySelector(".sourceRatingsWrapper .ratingsContainer .ratingsButtonContainer .selectedRating")?.innerText;if(body={source:e,rating:t},t&&!activatedButton){activatedButton=!0;try{let r=await fetch("../../api/source_ratings/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(body)});r.ok?(showMessage(context="Rating has been saved!","Success"),window.location.reload()):showMessage("Error: Network request failed unexpectedly!","Error")}catch(n){}}else showMessage("Select a rating!","Error")}),document.querySelector(".filterSidebar .selectContainer .infoLink i").addEventListener("click",()=>{setModalStyle(),document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="block",document.querySelector(".fullScreenPlaceholder .explanationContainer h3").innerText="Top Sources",document.querySelector(".fullScreenPlaceholder .explanationContainer .explanation").innerText="I personally select Top Sources based on their outstanding analysis, insightful perspectives, and engaging content. These sources are my go-to for staying informed and entertained, and I highly recommend them.",document.querySelector(".fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times").addEventListener("click",()=>{removeModalStyle(),document.querySelector(".fullScreenPlaceholder").style.display="none",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="none"})});
