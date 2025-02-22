async function createList(){try{let e=await fetch("../../api/lists/",getFetchSettings("POST"));if(e.ok){let t=await e.json();window.location.replace(`../../list/${t.list_id}`)}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){showMessage("Error: Unexpected error has occurred!","Error")}}async function changeSourcesSubscriptionStatus(){if(selectedSources.length&&!isSubscriptionStatusBeingChanged){isSubscriptionStatusBeingChanged=!0;for(let e=0,t=selectedSources.length;e<t;e++)try{(await fetch(`../../api/sources/${selectedSources[e]}/`,getFetchSettings("PATCH"))).ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){showMessage("Error: Unexpected error has occurred!","Error")}showMessage("Subscribed sources have been updated!","Success"),window.location.reload()}else showMessage("You need to select sources!","Error")}async function searchForNewSubscriptions(e,t,r){try{let n=await fetch(`../../api/sources/?subs_search=${e}`,getFetchSettings("GET"));if(n.ok){let s=await n.json();addSubscriptionsSearchResults(s,t,r)}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(c){showMessage("Error: Unexpected error has occurred!","Error")}}function changeLists(){let e=document.querySelector(".firstRow .nameContainer i"),t=document.querySelector(".listOptionsContainer"),r="block"===t.style.display;t.style.display=r?"none":"block",e.classList.toggle("fa-chevron-up",!r),e.classList.toggle("fa-chevron-down",r)}function openAddSubscriptionsMenu(){document.querySelector(".listMenuWrapper").style.display="block",document.querySelector(".addSourceContainer").style.display="block",setModalStyle(),document.querySelector(".addSourceContainer #textInput")&&document.querySelector(".addSourceContainer #textInput").addEventListener("keyup",()=>{let e=document.querySelector(".addSourceContainer #textInput").value,t=document.querySelector(".addSourceContainer #searchResultsContainer"),r=document.querySelector(".addSourceContainer .selectionContainer");document.querySelector(".addSourceContainer .cancelButton").addEventListener("click",()=>resetAddSubscriptionsMenu(r));let n=""!==(e||"").split(/\s+/).join("");t.style.display=n?"block":"none",r.style.display=n?"none":"block",n&&searchForNewSubscriptions(e,t,r)})}function closeAddSubscriptionsMenu(){document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".addSourceContainer").style.display="none",removeModalStyle()}function resetAddSubscriptionsMenu(e){selectedSources=[],e.innerHTML=""}function showNewSubscribedSources(e,t,r){let n=document.createElement("div");n.classList.add("searchResult");let s=document.createElement("img");s.src=`${ENV.CLOUDFRONT_DIST}/${e.favicon_path}`;let c=document.createElement("span");c.innerText=e.name,c.id=`source_id#${e.source_id}`,n.append(s,c),t.appendChild(n),n.addEventListener("click",function s(){n.removeEventListener("click",s),selectedSources.push(e.source_id);let c=document.createElement("i");c.classList.add("fas","fa-times"),c.addEventListener("click",()=>removeSourceFromListAndHTML(c)),n.appendChild(c),r.appendChild(n),t.style.display="none",r.style.display="block",document.querySelector(".listMenuWrapper .addSourceContainer #textInput").value=""})}function addSubscriptionsSearchResults(e,t,r){t.innerHTML="";let n=document.createElement("div");n.classList.add("resultHeader"),n.innerText="Results:",t.append(n),e.length>0&&e.forEach(e=>{selectedSources.includes(e.source_id)||showNewSubscribedSources(e,t,r)})}function removeSourceFromListAndHTML(e){e.parentElement.remove(),selectedSources=selectedSources.filter(function(t){return t.toString()!==e.closest(".searchResult").querySelector("span").id.split("#")[1]})}function changeTabsOnPageOpen(e){let t=document.querySelectorAll(".pageWrapper .tabsContainer button"),r=document.querySelectorAll(".pageWrapper .tabsContent");for(let n=0,s=t.length;n<s;n++)t[n].classList.remove("activatedTab"),r[n].classList.remove("tabsContentActive");t[e].classList.add("activatedTab"),r[e].classList.add("tabsContentActive")}location.href.includes("?commentary=")&&changeTabsOnPageOpen(1),location.href.includes("?news=")&&changeTabsOnPageOpen(2);let isSubscriptionStatusBeingChanged=!1,selectedSources=[];document.querySelector(".firstRow .nameContainer").addEventListener("click",()=>changeLists()),document.querySelector(".firstRow .listOptionsContainer .createListButton").addEventListener("click",()=>createList()),document.querySelector(".addSourceContainer .addSourceButton").addEventListener("click",()=>changeSourcesSubscriptionStatus()),document.querySelectorAll(".emptyInformationContainer button").forEach(e=>e.addEventListener("click",()=>openAddSubscriptionsMenu())),document.querySelector(".addSourceContainer .closeAddSourceContainer").addEventListener("click",()=>closeAddSubscriptionsMenu());