document.querySelector(".firstRow .nameContainer").addEventListener("click",()=>{let e=document.querySelector(".firstRow .nameContainer i"),t=document.querySelector(".listOptionsContainer");"block"===t.style.display?(t.style.display="none",e.classList.replace("fa-chevron-up","fa-chevron-down")):(t.style.display="block",e.classList.replace("fa-chevron-down","fa-chevron-up"))}),document.querySelector(".firstRow .listOptionsContainer .createListButton").addEventListener("click",async()=>{try{let e=await fetch("../../api/lists/",get_fetch_settings("POST"));if(e.ok){let t=await e.json();window.location.replace(`../../list/${t.list_id}`)}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){}});let activatedButton=!1;document.querySelector(".addSourceContainer .addSourceButton").addEventListener("click",async()=>{if(selected_sources.length&&!activatedButton){activatedButton=!0;for(let e=0,t=selected_sources.length;e<t;e++)try{let r=await fetch(`../../api/sources/${selected_sources[e]}/`,get_fetch_settings("PATCH"));r.ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(s){}showMessage(context="Subscribed sources have been updated!","Success"),window.location.reload()}else showMessage("You need to select sources!","Error")});let selected_sources=[];document.querySelectorAll(".emptyInformationContainer button").forEach(e=>e.addEventListener("click",()=>{document.querySelector(".listMenuWrapper").style.display="block",document.querySelector(".addSourceContainer").style.display="block",setModalStyle(),document.querySelector(".addSourceContainer #textInput")&&document.querySelector(".addSourceContainer #textInput").addEventListener("keyup",async function(){let e=document.querySelector(".addSourceContainer #textInput").value,t=document.querySelector(".addSourceContainer #searchResultsContainer"),r=document.querySelector(".addSourceContainer .selectionContainer");if(document.querySelector(".addSourceContainer .cancelButton").addEventListener("click",()=>{selected_sources=[],r.innerHTML=""}),e&&""!=e.replaceAll(/\s/g,"")){t.style.display="block",r.style.display="none";try{let s=await fetch(`../../api/sources/?subs_search=${e}`,get_fetch_settings("GET"));if(s.ok){let n=await s.json();t.innerHTML="";let l=document.createElement("div");l.classList.add("resultHeader"),l.innerText="Results:",t.append(l),n.length>0&&n.forEach(e=>{if(!1==selected_sources.includes(e.source_id)){let s=document.createElement("div");s.classList.add("searchResult");let n=document.createElement("img");n.src=`https://finbrowser.s3.us-east-2.amazonaws.com/static/${e.favicon_path}`;let l=document.createElement("span");l.innerText=e.name,l.id=`source_id#${e.source_id}`,s.append(n,l),t.appendChild(s),s.addEventListener("click",function n(){s.removeEventListener("click",n),selected_sources.push(e.source_id);let l=document.createElement("i");l.classList.add("fas","fa-times"),l.addEventListener("click",()=>{l.parentElement.remove(),selected_sources=selected_sources.filter(function(e){return e.toString()!==l.closest(".searchResult").querySelector("span").id.split("#")[1]})}),s.appendChild(l),r.appendChild(s),t.style.display="none",r.style.display="block",document.querySelector(".listMenuWrapper .addSourceContainer #textInput").value=""})}})}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(a){}}else t.style.display="none",r.style.display="block"})})),document.querySelector(".addSourceContainer .closeAddSourceContainer").addEventListener("click",()=>{document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".addSourceContainer").style.display="none",removeModalStyle()});
