function getCookie(e){let t=null;if(document.cookie&&""!==document.cookie){let r=document.cookie.split(";");for(let i=0;i<r.length;i++){let n=r[i].trim();if(n.substring(0,e.length+1)===e+"="){t=decodeURIComponent(n.substring(e.length+1));break}}}return t}function get_fetch_settings(e){let t={method:e,headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin"};return t}function showMessage(e,t){document.querySelectorAll(".messages").forEach(e=>{e.remove()});let r=document.createElement("ul");r.classList.add("messages");let i=document.createElement("li");i.innerText=e,"Success"==t?i.classList.add("success"):"Remove"==t?i.classList.add("remove"):i.classList.add("error"),r.appendChild(i),document.querySelector(".overlay").appendChild(r)}document.querySelector(".headerContainer .fa-bars").addEventListener("click",()=>{let e=document.querySelector(".horizontalNavigation");"ON"==e.value?(e.style.maxHeight="0",e.value="OFF"):(e.style.maxHeight="100rem",e.value="ON")}),document.querySelectorAll("input").forEach(e=>{e.setAttribute("autocomplete","off")}),document.querySelector(".headerContainer #mainAutocomplete").addEventListener("click",()=>{if(check_device_width_below(500)&&!document.querySelector(".headerContainer .mainSearchWrapper .closeSearchIcon")){document.querySelector(".headerContainer .logoContainer").style.display="none",document.querySelector(".headerContainer .fa-bars").style.display="none",document.querySelector(".headerContainer .mainSearchWrapper").style.width="100%",document.querySelector(".headerContainer .mainSearchContainer").style.display="flex",document.querySelector(".headerContainer .mainSearchContainer").style.justifyContent="center",document.querySelector(".headerContainer .mainSearchContainer").style.position="relative",document.querySelector(".headerContainer .mainSearchContainer").style.width="90%",document.querySelector(".headerContainer #mainAutocomplete").style.width="97.5%",document.querySelector(".headerContainer #mainAutocomplete").style.maxWidth="unset";let e=document.createElement("i");e.classList.add("fas","fa-times","closeSearchIcon"),document.querySelector(".headerContainer .mainSearchWrapper").appendChild(e),e.addEventListener("click",()=>{document.querySelector(".headerContainer .mainSearchWrapper .closeSearchIcon").remove(),document.querySelector(".headerContainer .logoContainer").style.display="",document.querySelector(".headerContainer .fa-bars").style.display="",document.querySelector(".headerContainer .mainSearchWrapper").style.width="",document.querySelector(".headerContainer .mainSearchContainer").style.display="",document.querySelector(".headerContainer .mainSearchContainer").style.justifyContent="",document.querySelector(".headerContainer .mainSearchContainer").style.position="",document.querySelector(".headerContainer .mainSearchContainer").style.width="",document.querySelector(".headerContainer #mainAutocomplete").style.width="",document.querySelector(".headerContainer #mainAutocomplete").style.maxWidth=""})}}),document.getElementById("mainAutocomplete").addEventListener("keyup",async function(e){let t=document.getElementById("mainAutocomplete").value;if("Enter"==e.key&&""!=t.replaceAll(/\s/g,""))window.location.href=`../../../../../../search_results/${t}`;else{let r=document.getElementById("mainAutocomplete_result");if(t&&""!=t.replaceAll(/\s/g,"")){try{let i=await fetch(`../../../../../../api/search_site/${t}`,get_fetch_settings("GET"));if(i.ok){document.querySelector(".mainInputSearch").style.borderRadius="0.8rem 0.8rem 0 0";let n=await i.json();if(r.style.display="flex",r.innerHTML="",n[0].length>0&&(r.innerHTML+='<div class="searchResultHeader">Stocks</div>',n[0].forEach(e=>{let t=`<div class="searchResult"><div class="stockContainer"><div class="stockTicker">${e.ticker}</div><div class="companyName">${e.full_company_name}</div><a href="../../../../../../stock/${e.ticker}"></a></div></div>`;r.innerHTML+=t})),n[1].length>0&&(r.innerHTML+='<div class="searchResultHeader">Sources</div>',n[1].forEach(e=>{let t=`<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${e.favicon_path}"><span>${e.name}</span><a href="../../../../../../source/${e.slug}"></a></div>`;r.innerHTML+=t})),n[2].length>0){r.innerHTML+='<div class="searchResultHeader">Articles</div>';for(let a=0,l=n[2].length;a<l;a++){let s=n[3][a],o=n[2][a].title,c=n[2][a].link,d=`<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${s}"><span>${o}</span><a href="${c}" target="_blank"></a></div>`;r.innerHTML+=d}}}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(u){}document.onclick=function(e){"autocomplete_list_results"!==e.target.id&&(r.style.display="none",document.querySelector(".mainInputSearch").style.borderRadius="0.8rem")}}else r.style.display="none",document.querySelector(".mainInputSearch").style.borderRadius="0.8rem"}}),document.querySelector(".mainSearchContainer i").addEventListener("click",()=>{""!=(search_term=document.querySelector(".mainInputSearch").value).replaceAll(/\s/g,"")&&(window.location.href=`../../../../../../search_results/${search_term}`)});const dropdownButton=document.querySelector(".fa-sort-down");function checkForOpenContainers(){let e=!0,t=document.querySelectorAll(".addToListForm");for(let r=0,i=t.length;r<i;r++)if("none"!=t[r].style.display&&t[r].style.display){e=!1;break}return e}dropdownButton&&dropdownButton.addEventListener("click",()=>{let e=document.querySelector(".profileMenu");"flex"==e.style.display?e.style.display="none":e.style.display="flex"});let previousOptionsContainer,previousEllipsis;function get_initial_list_statuses(e){let t=[],r=[],i=e.parentElement.nextElementSibling.querySelectorAll(".listContainer input");for(let n=0,a=i.length;n<a;n++)t.push(i[n].checked),r.push(i[n].id.split("#")[1]);return[t,r]}function check_new_list_status(e){let t=[];return e.parentElement.previousElementSibling.querySelectorAll("input").forEach(e=>{t.push(e.checked)}),t}async function add_article_to_list(e,t){try{let r=await fetch(`../../../../../../api/lists/${e}/add_article_to_list/${t}/`,get_fetch_settings("POST"));r.ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(i){}}async function remove_article_from_list(e,t){try{let r=await fetch(`../../../../../../api/lists/${e}/delete_article_from_list/${t}/`,get_fetch_settings("DELETE"));r.ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(i){}}function check_device_width_below(e){let t=window.innerWidth||document.documentElement.clientWidth||document.body.clientWidth;return t<e}document.querySelectorAll(".fa-ellipsis-h").forEach(e=>{e.addEventListener("click",function(t){let r=checkForOpenContainers();if(r){previousOptionsContainer&&t.target!==previousEllipsis&&(previousOptionsContainer.style.display="none");let i=e.parentElement.querySelector(".articleOptionsContainer");"flex"!=i.style.display?(i.style.display="flex",document.onclick=function(t){t.target!==e&&(e.parentElement.querySelector(".articleOptionsContainer").style.display="none")}):i.style.display="none",previousOptionsContainer=e.parentElement.querySelector(".articleOptionsContainer"),previousEllipsis=e}})}),document.querySelectorAll(".addToHighlightedButton").forEach(e=>{e.addEventListener("click",async()=>{if(!e.classList.contains("registrationLink")){let t=e.closest(".articleContainer").id.split("#")[1],r=e.lastElementChild.innerText,i;i="Highlight article"==r?"highlight":"unhighlight";try{let n={article_id:t},a=await fetch("../../../../../../api/highlighted_articles/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(n)});if(a.ok){let l=await a.json();"highlight"==i?(showMessage(l,"Success"),e.innerHTML='<i class="fas fa-times"></i><span>Unhighlight article</span>'):(showMessage(l,"Remove"),e.innerHTML='<i class="fas fa-highlighter"></i><span>Highlight article</span>')}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(s){}}})}),document.querySelectorAll(".addToListButton").forEach(e=>{e.addEventListener("click",()=>{if(!e.classList.contains("registrationLink")){let t=checkForOpenContainers();t&&(e.parentElement.nextElementSibling.style.display="block");let r=get_initial_list_statuses(e),i=r[0],n=e.parentElement.parentElement.querySelector(".addToListForm");if(n.querySelector(".saveButton")){let a=n.querySelector(".saveButton");a.addEventListener("click",()=>{let e=r[1],t=a.closest(".articleContainer").id.split("#")[1],l=check_new_list_status(a);for(let s=0,o=l.length;s<o;s++)l[s]!=i[s]&&(!1==i[s]?add_article_to_list(e[s],t):remove_article_from_list(e[s],t));showMessage("Lists have been updated!","Success"),n.style.display="none"})}}})}),document.querySelectorAll(".addToListForm .fa-times").forEach(e=>{e.addEventListener("click",()=>{e.parentElement.parentElement.style.display="none"})}),document.querySelectorAll(".createNewListButton").forEach(e=>{e.addEventListener("click",()=>{e.classList.contains("registrationLink")||(e.parentElement.parentElement.parentElement.querySelector(".addToListForm").style.display="none",check_device_width_below(500)?document.querySelector(".smartphoneCreateListMenu").style.display="flex":e.parentElement.parentElement.parentElement.querySelector(".createListMenu").style.display="flex")})}),document.querySelectorAll(".createListMenu .closeFormContainerButton").forEach(e=>{e.addEventListener("click",()=>{document.querySelectorAll(".createListMenu").forEach(e=>{e.style.display="none"})})}),document.querySelector(".userSpace .notificationBell")&&document.querySelector(".userSpace .notificationBell").addEventListener("click",async()=>{let e=document.querySelector(".userSpace .notificationContainer");if("block"==e.style.display)e.style.display="none",document.querySelector(".unseenNotifications").remove(),document.querySelectorAll(".unseenNotification").forEach(e=>{e.classList.remove("unseenNotification")});else{e.style.display="block";try{let t=await fetch("../../../../../../api/notifications/",get_fetch_settings("PUT"));t.ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){}}});const notificationTabs=document.querySelectorAll(".notificationHeadersContainer div"),notificationContent=document.querySelectorAll(".notificationsContainer");notificationTabs.forEach(e=>{e.addEventListener("click",()=>{for(let t=0,r=notificationTabs.length;t<r;t++)notificationTabs[t].classList.remove("activeNotificationCategory"),notificationContent[t].classList.remove("activeNotificationContainer");notificationTabs[e.dataset.forTab].classList.add("activeNotificationCategory"),notificationContent[e.dataset.forTab].classList.add("activeNotificationContainer")})}),document.addEventListener("click",e=>{let t;null!=(t=e.target.matches(".handle")?e.target:e.target.closest(".handle"))&&onHandleClick(t)});const throttleProgressBar=throttle(()=>{document.querySelectorAll(".progressBar").forEach(calculateProgressBar)},250);function calculateProgressBar(e){e.innerHTML="";let t=e.closest(".sliderWrapper").querySelector(".slider"),r=t.children.length,i=parseInt(getComputedStyle(t).getPropertyValue("--items-per-screen")),n=parseInt(getComputedStyle(t).getPropertyValue("--slider-index")),a=Math.ceil(r/i);n>=a&&(t.style.setProperty("--slider-index",a-1),n=a-1);for(let l=0;l<a;l++){let s=document.createElement("div");s.classList.add("progressItem"),l===n&&s.classList.add("active"),e.append(s)}}function onHandleClick(e){let t=e.closest(".sliderWrapper").querySelector(".progressBar"),r=e.closest(".sliderContentContainer").querySelector(".slider"),i=parseInt(getComputedStyle(r).getPropertyValue("--slider-index")),n=t.children.length;e.classList.contains("leftHandle")&&(i-1<0?(r.style.setProperty("--slider-index",n-1),t.children[i].classList.remove("active"),t.children[n-1].classList.add("active")):(r.style.setProperty("--slider-index",i-1),t.children[i].classList.remove("active"),t.children[i-1].classList.add("active"))),e.classList.contains("rightHandle")&&(i+1>=n?(r.style.setProperty("--slider-index",0),t.children[i].classList.remove("active"),t.children[0].classList.add("active")):(r.style.setProperty("--slider-index",i+1),t.children[i].classList.remove("active"),t.children[i+1].classList.add("active")))}function throttle(e,t=1e3){let r=!1,i,n=()=>{null==i?r=!1:(e(...i),i=null,setTimeout(n,t))};return(...a)=>{if(r){i=a;return}e(...a),r=!0,setTimeout(n,t)}}window.addEventListener("resize",throttleProgressBar),document.querySelectorAll(".progressBar").forEach(calculateProgressBar);