async function removeSourceFromListLD(e){try{let t=e.closest(".contentWrapper").id.split("#")[1],r=await fetch(`../../api/lists/${LIST_ID}/`,getFetchSettings("PATCH",{source_id:t}));r.ok?(showMessage("Source has been removed!","Remove"),e.closest(".contentWrapper").remove(),document.querySelector(".slider .contentWrapper")||window.location.reload()):showMessage("Error: Network request failed unexpectedly!","Error")}catch(n){showMessage("Error: Unexpected error has occurred!","Error")}}async function addSourcesToList(){if(selectedSources.length&&!areSourcesBeingAddedToList){areSourcesBeingAddedToList=!0;for(let e=0,t=selectedSources.length;e<t;e++)try{let r={source_id:selectedSources[e]},n=await fetch(`../../api/lists/${LIST_ID}/`,getFetchSettings("PATCH",r));n.ok?showMessage("List has been updated!","Success"):showMessage("Error: Network request failed unexpectedly!","Error")}catch(o){showMessage("Error: Unexpected error has occurred!","Error")}showMessage("List has been updated!","Success"),window.location.reload()}else showMessage("You need to select sources!","Error")}async function createList(){try{let e=await fetch("../../api/lists/",getFetchSettings("POST"));if(e.ok){let t=await e.json();window.location.replace(`../../list/${t.list_id}`)}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){showMessage("Error: Unexpected error has occurred!","Error")}}async function deleteList(){try{let e=await fetch(`../../api/lists/${LIST_ID}/`,getFetchSettings("DELETE"));e.ok?(showMessage("List has been deleted!","Remove"),document.querySelectorAll(".listOptionsContainer .listOption").forEach(e=>{e.id.replace("list","")!==LIST_ID&&window.location.replace("../../lists")})):showMessage("Error: Network request failed unexpectedly!","Error")}catch(t){showMessage("Error: Unexpected error has occurred!","Error")}}async function editList(){let e=document.querySelector(".editMenu .listNameContainer input").value,t=document.querySelector(".editMenu .mainListContainer input").checked;if(e.trim().length)try{let r=await fetch(`../../api/lists/${LIST_ID}/`,{method:"PATCH",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify({name:e,main:t})});r.ok?(showMessage("List has been updated!","Success"),window.location.reload()):showMessage("Error: Network request failed unexpectedly!","Error")}catch(n){showMessage("Error: Unexpected error has occurred!","Error")}else showMessage("Please enter a name!","Error")}async function searchAddSourcesToList(e,t,r){try{let n=await fetch(`../../api/sources/?list_search=${e}&list_id=${LIST_ID}`,getFetchSettings("GET"));if(n.ok){let o=await n.json();showAddSourcesToListSearchResults(o,t,r)}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(s){showMessage("Error: Unexpected error has occurred!","Error")}}function changeLists(){let e=document.querySelector(".firstRow .nameContainer i"),t=document.querySelector(".listOptionsContainer");"block"===t.style.display?(t.style.display="none",e.classList.replace("fa-chevron-up","fa-chevron-down")):(t.style.display="block",e.classList.replace("fa-chevron-down","fa-chevron-up"))}function openDeleteListMenu(){document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".editMenu").style.display="none",document.querySelector(".listMenuWrapper").style.display="block",document.querySelector(".listMenuWrapper .warningMessageContainer").style.display="flex",document.querySelector(".listMenuWrapper .warningMessageContainer .discardButton").addEventListener("click",()=>closeDeleteListMenu()),document.querySelector(".listMenuWrapper .warningMessageContainer .confirmButton").addEventListener("click",()=>deleteList(),{once:!0})}function closeDeleteListMenu(){removeModalStyle(),document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".listMenuWrapper .warningMessageContainer").style.display="none"}function openEditListMenu(){document.querySelector(".listMenuWrapper").style.display="block",document.querySelector(".editMenu").style.display="block",setModalStyle()}function closeEditListMenu(){document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".editMenu").style.display="none",removeModalStyle()}function openMainListExplanation(){document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".listMenuWrapper .editMenu").style.display="none",createExplanationContainer("Main List","Your main list is the one that opens up whenever you click on the Lists button in the header. It's important to note that you always need to have at least one main list. If you only have one list, then you won't be able to delete it as it is your main one. But, if you have multiple lists and you delete your main one, then the next list in alphabetical order will become your new main list. Don't worry though, you can easily change your main list by opening the edit menu of a list that is currently not your main one and setting it as your new main list. It's as simple as that!"),document.querySelector(".fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times").addEventListener("click",()=>closeMainListExplanation())}function closeMainListExplanation(){document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="none",document.querySelector(".listMenuWrapper").style.display="flex",document.querySelector(".listMenuWrapper .editMenu").style.display="block"}function closeAddSourceToListMenu(){document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".addSourceContainer").style.display="none",removeModalStyle()}function showListSearchResults(e,t,r){let n=document.createElement("div");n.classList.add("searchResult");let o=document.createElement("img");o.src=`https://finbrowser.s3.us-east-2.amazonaws.com/static/${e.favicon_path}`;let s=document.createElement("span");s.innerText=e.name,s.id=`source_id#${e.source_id}`,n.append(o,s),t.appendChild(n),n.addEventListener("click",function o(){n.removeEventListener("click",o),selectedSources.push(e.source_id);let s=document.createElement("i");s.classList.add("fas","fa-times"),s.addEventListener("click",()=>removeSourceFromListAndDOM(s)),n.appendChild(s),r.appendChild(n),t.style.display="none",r.style.display="block",document.querySelector(".listMenuWrapper .addSourceContainer #textInput").value=""})}function showAddSourcesToListSearchResults(e,t,r){t.innerHTML="";let n=document.createElement("div");n.classList.add("resultHeader"),n.innerText="Results:",t.append(n),e.length>0&&e.forEach(e=>{selectedSources.includes(e.source_id)||showListSearchResults(e,t,r)})}function resetAddSourceToListMenu(e){selectedSources=[],e.innerHTML=""}function openAddSourceToListMenu(){document.querySelector(".listMenuWrapper").style.display="block",document.querySelector(".addSourceContainer").style.display="block",setModalStyle(),document.querySelector(".addSourceContainer #addSources")&&document.querySelector(".addSourceContainer #addSources").addEventListener("keyup",()=>{let e=document.querySelector(".addSourceContainer #addSources").value,t=document.querySelector(".addSourceContainer #searchResultsContainer"),r=document.querySelector(".addSourceContainer .selectionContainer");document.querySelector(".addSourceContainer .buttonContainer .cancelButton").addEventListener("click",()=>resetAddSourceToListMenu(r));let n=""!==(e||"").split(/\s+/).join("");t.style.display=n?"block":"none",r.style.display=n?"none":"block",n&&searchAddSourcesToList(e,t,r)})}function removeSourceFromListAndDOM(e){e.parentElement.remove(),selectedSources=selectedSources.filter(function(t){return t.toString()!==e.closest(".searchResult").querySelector("span").id.split("#")[1]})}function changeTabsOnPageOpen(e){let t=document.querySelectorAll(".pageWrapper .tabsContainer button"),r=document.querySelectorAll(".pageWrapper .tabsContent");for(let n=0,o=t.length;n<o;n++)t[n].classList.remove("activatedTab"),r[n].classList.remove("tabsContentActive");t[e].classList.add("activatedTab"),r[e].classList.add("tabsContentActive")}location.href.includes("?commentary=")&&changeTabsOnPageOpen(1),location.href.includes("?news=")&&changeTabsOnPageOpen(2),location.href.includes("?saved_content=")&&changeTabsOnPageOpen(3);let areSourcesBeingAddedToList=!1;const LIST_ID=document.querySelector(".firstRow .nameContainer h2").id;let selectedSources=[];document.querySelectorAll(".sliderWrapper .slider .removeFromListButton").forEach(e=>{e.addEventListener("click",()=>removeSourceFromListLD(e))}),document.querySelector(".addSourceContainer .addSourceButton").addEventListener("click",()=>addSourcesToList()),document.querySelector(".firstRow .nameContainer").addEventListener("click",()=>changeLists()),document.querySelector(".firstRow .listOptionsContainer .createListButton").addEventListener("click",()=>createList(),{once:!0}),document.querySelector(".editMenu .deleteListButton").addEventListener("click",()=>{1===document.querySelectorAll(".listsContainer .listOption").length?showMessage("You are not allowed to delete your last watchlist!","Error"):openDeleteListMenu()}),document.querySelector(".actionButtonContainer .addSourceButton").addEventListener("click",()=>openAddSourceToListMenu()),document.querySelectorAll(".emptyInformationContainer button").forEach(e=>e.addEventListener("click",()=>openAddSourceToListMenu())),document.querySelector(".listMenuWrapper .addSourceContainer .closeAddSourceContainer").addEventListener("click",()=>closeAddSourceToListMenu()),document.querySelector(".editListButton").addEventListener("click",()=>openEditListMenu()),document.querySelector(".editMenu .fa-times").addEventListener("click",()=>closeEditListMenu()),document.querySelector(".menuContainer .editMenu .saveEditsButton").addEventListener("click",()=>editList(),{once:!0}),document.querySelector(".listMenuWrapper .editMenu .mainListContainer .infoLink i").addEventListener("click",()=>openMainListExplanation());
