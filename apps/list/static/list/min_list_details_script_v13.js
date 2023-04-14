if(location.href.includes("?commentary=")){let e=document.querySelectorAll(".pageWrapper .tabsContainer button"),t=document.querySelectorAll(".pageWrapper .tabsContent");for(let r=0,n=e.length;r<n;r++)e[r].classList.remove("activatedTab"),t[r].classList.remove("tabsContentActive");e[1].classList.add("activatedTab"),t[1].classList.add("tabsContentActive")}if(location.href.includes("?news=")){let l=document.querySelectorAll(".pageWrapper .tabsContainer button"),a=document.querySelectorAll(".pageWrapper .tabsContent");for(let i=0,o=l.length;i<o;i++)l[i].classList.remove("activatedTab"),a[i].classList.remove("tabsContentActive");l[2].classList.add("activatedTab"),a[2].classList.add("tabsContentActive")}if(location.href.includes("?saved_content=")){let s=document.querySelectorAll(".pageWrapper .tabsContainer button"),c=document.querySelectorAll(".pageWrapper .tabsContent");for(let d=0,u=s.length;d<u;d++)s[d].classList.remove("activatedTab"),c[d].classList.remove("tabsContentActive");s[3].classList.add("activatedTab"),c[3].classList.add("tabsContentActive")}document.querySelectorAll(".sliderWrapper .slider .removeFromListButton").forEach(e=>{e.addEventListener("click",async()=>{try{let t=document.querySelector(".firstRow .nameContainer h2").id,r=e.closest(".contentWrapper").id.split("#")[1],n={source_id:r},l=await fetch(`../../api/lists/${t}/`,get_fetch_settings("PATCH",n));l.ok?(showMessage(context="Source has been removed!","Remove"),e.closest(".contentWrapper").remove(),document.querySelector(".slider .contentWrapper")||window.location.reload()):showMessage("Error: Network request failed unexpectedly!","Error")}catch(a){}})});let selected_sources=[];document.querySelector(".addSourceContainer #textInput")&&document.querySelector(".addSourceContainer #textInput").addEventListener("keyup",async function(){let e=document.querySelector(".addSourceContainer #textInput").value,t=document.querySelector(".addSourceContainer #searchResultsContainer"),r=document.querySelector(".addSourceContainer .selectionContainer"),n=document.querySelector(".firstRow .nameContainer h2").id;if(e&&""!=e.replaceAll(/\s/g,"")){t.style.display="block",r.style.display="none";try{let l=await fetch(`../../api/sources/?list_search=${e}&list_id=${n}`,get_fetch_settings("GET"));if(l.ok){let a=await l.json();t.innerHTML="";let i=document.createElement("div");i.innerText="Results:",t.append(i),a.length>0&&a.forEach(e=>{if(!1==selected_sources.includes(e.source_id)){let n=document.createElement("div");n.classList.add("searchResult");let l=document.createElement("img");l.src=`https://finbrowser.s3.us-east-2.amazonaws.com/static/${e.favicon_path}`;let a=document.createElement("span");a.innerText=e.name,a.id=`source_id_${e.source_id}`,n.append(l,a),t.appendChild(n),n.addEventListener("click",function l(){n.removeEventListener("click",l),selected_sources.push(e.source_id);let a=document.createElement("i");a.classList.add("fas","fa-times"),a.addEventListener("click",()=>{a.parentElement.remove(),selected_sources=selected_sources.filter(function(e){return e.toString()!==a.previousElementSibling.id.split("#")[1]})}),n.appendChild(a),r.appendChild(n),t.style.display="none",r.style.display="block",document.querySelector(".listMenuWrapper .addSourceContainer #textInput").value=""})}})}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(o){}}else t.style.display="none",r.style.display="block"});let activatedButton=!1;document.querySelector(".addSourceContainer .addSourceButton").addEventListener("click",async()=>{let e=document.querySelector(".firstRow .nameContainer h2").id;if(selected_sources.length&&!activatedButton){activatedButton=!0;for(let t=0,r=selected_sources.length;t<r;t++)try{let n={source_id:selected_sources[t]},l=await fetch(`../../api/lists/${e}/`,get_fetch_settings("PATCH",n));l.ok?showMessage("List has been updated!","Success"):showMessage("Error: Network request failed unexpectedly!","Error")}catch(a){}showMessage(context="List has been updated!","Success"),window.location.reload()}else showMessage("You need to select sources!","Error")}),document.querySelector(".firstRow .nameContainer").addEventListener("click",()=>{let e=document.querySelector(".firstRow .nameContainer i"),t=document.querySelector(".listOptionsContainer");"block"===t.style.display?(t.style.display="none",e.classList.replace("fa-chevron-up","fa-chevron-down")):(t.style.display="block",e.classList.replace("fa-chevron-down","fa-chevron-up"))}),document.querySelector(".firstRow .listOptionsContainer .createListButton").addEventListener("click",async()=>{try{let e=await fetch("../../api/lists/",get_fetch_settings("POST"));if(e.ok){let t=await e.json();window.location.replace(`../../list/${t.list_id}`)}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){}},{once:!0}),document.querySelector(".editMenu .deleteListButton").addEventListener("click",()=>{let e=document.querySelector(".nameContainer h2").id;1===document.querySelectorAll(".listsContainer .listOption").length?showMessage("You are not allowed to delete your last watchlist!","Error"):(document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".editMenu").style.display="none",document.querySelector(".listMenuWrapper").style.display="block",document.querySelector(".listMenuWrapper .warningMessageContainer").style.display="flex",document.querySelector(".listMenuWrapper .warningMessageContainer .discardButton").addEventListener("click",()=>{removeModalStyle(),document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".listMenuWrapper .warningMessageContainer").style.display="none"}),document.querySelector(".listMenuWrapper .warningMessageContainer .confirmButton").addEventListener("click",async()=>{try{let t=await fetch(`../../api/lists/${e}/`,get_fetch_settings("DELETE"));t.ok?(showMessage("List has been deleted!","Remove"),document.querySelectorAll(".listOptionsContainer .listOption").forEach(t=>{t.id.replace("list","")!==e&&window.location.replace("../../lists")})):showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){}},{once:!0}))}),document.querySelector(".actionButtonContainer .addSourceButton").addEventListener("click",()=>{document.querySelector(".listMenuWrapper").style.display="block",document.querySelector(".addSourceContainer").style.display="block",setModalStyle()}),document.querySelectorAll(".emptyInformationContainer button").forEach(e=>e.addEventListener("click",()=>{document.querySelector(".listMenuWrapper").style.display="block",document.querySelector(".addSourceContainer").style.display="block",setModalStyle()})),document.querySelectorAll(".listMenuWrapper .addSourceContainer .closeAddSourceContainer, .listMenuWrapper .addSourceContainer .buttonContainer .cancelButton").forEach(e=>e.addEventListener("click",()=>{document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".addSourceContainer").style.display="none",removeModalStyle()})),document.querySelector(".editListButton").addEventListener("click",()=>{document.querySelector(".listMenuWrapper").style.display="block",document.querySelector(".editMenu").style.display="block",setModalStyle()}),document.querySelector(".editMenu .fa-times").addEventListener("click",()=>{document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".editMenu").style.display="none",removeModalStyle()}),document.querySelector(".menuContainer .editMenu .saveEditsButton").addEventListener("click",async()=>{let e=document.querySelector(".firstRow .nameContainer h2").id,t=document.querySelector(".editMenu .listNameContainer input").value,r=document.querySelector(".editMenu .mainListContainer input").checked,n={name:t,main:r};if(t.trim().length)try{let l=await fetch(`../../api/lists/${e}/`,{method:"PATCH",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(n)});l.ok?(showMessage("List has been updated!","Success"),window.location.reload()):showMessage("Error: Network request failed unexpectedly!","Error")}catch(a){}else showMessage("Please enter a name!","Error")},{once:!0}),document.querySelector(".listMenuWrapper .editMenu .mainListContainer .infoLink i").addEventListener("click",()=>{document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".listMenuWrapper .editMenu").style.display="none",document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="block",document.querySelector(".fullScreenPlaceholder .explanationContainer h3").innerText="Main List",document.querySelector(".fullScreenPlaceholder .explanationContainer .explanation").innerText="Your main list is the one that opens up whenever you click on the Lists button in the header. It's important to note that you always need to have at least one main list. If you only have one list, then you won't be able to delete it as it is your main one. But, if you have multiple lists and you delete your main one, then the next list in alphabetical order will become your new main list. Don't worry though, you can easily change your main list by opening the edit menu of a list that is currently not your main one and setting it as your new main list. It's as simple as that!",document.querySelector(".fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times").addEventListener("click",()=>{document.querySelector(".fullScreenPlaceholder").style.display="none",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="none",document.querySelector(".listMenuWrapper").style.display="flex",document.querySelector(".listMenuWrapper .editMenu").style.display="block"})});