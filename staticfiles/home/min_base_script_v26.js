function getScrollbarWidth(){let e=document.createElement("div");e.style.visibility="hidden",e.style.overflow="scroll",e.style.msOverflowStyle="scrollbar",document.body.appendChild(e);let t=document.createElement("div");e.appendChild(t);let r=e.offsetWidth-t.offsetWidth;return e.parentNode.removeChild(e),r}function setModalStyle(){let e=getScrollbarWidth();document.querySelector("header").style.pointerEvents="none",document.querySelector("body").style.overflow="hidden",document.querySelector("body").style.paddingRight=e+"px",document.querySelector(".outerHeaderContainer").style.paddingRight=e+"px",document.querySelector(".fullScreenPlaceholder").style.display="block"}function removeModalStyle(){document.querySelector("header").style.removeProperty("pointer-events"),document.querySelector("body").style.removeProperty("overflow"),document.querySelector(".fullScreenPlaceholder").style.display="none",document.querySelector("body").style.removeProperty("padding-right"),document.querySelector(".outerHeaderContainer").style.removeProperty("padding-right")}function getCookie(e){let t=null;if(document.cookie&&""!==document.cookie){let r=document.cookie.split(";");for(let l=0;l<r.length;l++){let o=r[l].trim();if(o.substring(0,e.length+1)===e+"="){t=decodeURIComponent(o.substring(e.length+1));break}}}return t}function get_fetch_settings(e,t=!1){let r={method:e,headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin"};return t&&(r.body=JSON.stringify(t)),r}function showMessage(e,t){document.querySelectorAll(".messages").forEach(e=>{e.remove()});let r=document.createElement("ul");r.classList.add("messages");let l=document.createElement("li");l.innerText=e,"Success"==t?l.classList.add("success"):"Remove"==t?l.classList.add("remove"):l.classList.add("error"),r.appendChild(l),document.querySelector(".overlay").appendChild(r)}async function getSearchResults(e,t,r=!1){try{let l=await fetch(`../../../../../../api/search_site/${e}`,get_fetch_settings("GET"));if(l.ok){let o=await l.json();if(r&&o[0].length||o[1].length||o[2].length?document.querySelector(".smallScreenSearchContainer .recommendedContainer").style.display="none":!r||o[0].length||o[1].length||o[2].length||(document.querySelector(".smallScreenSearchContainer .noResultsFound").style.display="block",document.querySelector(".smallScreenSearchContainer .noResultsFound").innerText="I'm sorry but there are no results for "+e),t.style.display="flex",t.innerHTML="",o[0].length>0&&(t.innerHTML+='<div class="searchResultHeader">Stocks</div>',o[0].forEach(e=>{let r=`<div class="searchResult"><div class="stockContainer"><div class="stockTicker">${e.ticker}</div><div class="companyName">${e.full_company_name}</div><a href="../../../../../../stock/${e.ticker}"></a></div></div>`;t.innerHTML+=r})),o[1].length>0&&(t.innerHTML+='<div class="searchResultHeader">Sources</div>',o[1].forEach(e=>{let r=`<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${e.favicon_path}"><span>${e.name}</span><a href="../../../../../../source/${e.slug}"></a></div>`;t.innerHTML+=r})),o[2].length>0){t.innerHTML+='<div class="searchResultHeader">Articles</div>';for(let n=0,s=o[2].length;n<s;n++){let a=o[2][n].source.favicon_path,i=o[2][n].title,c=o[2][n].link,d=`<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${a}"><span>${i}</span><a href="${c}" target="_blank"></a></div>`;t.innerHTML+=d}}}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(u){}}function closeAllPotentialOpenPopups(){if(document.querySelector(".fullScreenPlaceholder .addToListForm").style.display="none",document.querySelector(".fullScreenPlaceholder .authPromptContainer").style.display="none",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="none",document.querySelector(".portfolioMenuWrapper")&&(document.querySelector(".portfolioMenuWrapper").style.display="none",document.querySelector(".portfolioMenuWrapper .addStocksContainer").style.display="none",document.querySelector(".portfolioMenuWrapper .editMenu").style.display="none",document.querySelector(".portfolioMenuWrapper .warningMessageContainer").style.display="none"),document.querySelector(".listMenuWrapper")&&(document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".listMenuWrapper .addSourceContainer").style.display="none",document.querySelector(".listMenuWrapper .editMenu").style.display="none",document.querySelector(".listMenuWrapper .warningMessageContainer").style.display="none"),document.querySelector(".stockMenuWrapper")&&(document.querySelector(".stockMenuWrapper").style.display="none",document.querySelector(".stockMenuWrapper .addStockContainer").style.display="none"),document.querySelector(".keywordCreationWrapper")&&(document.querySelector(".keywordCreationWrapper").style.display="none"),document.querySelector(".notificationPopupWrapper")&&(document.querySelector(".notificationPopupWrapper").style.display="none"),document.querySelector(".sourceRatingsWrapper")&&(document.querySelector(".sourceRatingsWrapper").style.display="none"),"flex"==document.querySelector(".horizontalNavigation").style.display){document.querySelector(".horizontalNavigation").style.display="none";let e=document.querySelector(".headerContainer .closeNavMenuButton");e.classList.replace("fa-times","fa-bars"),e.classList.remove("closeNavMenuButton")}}document.querySelector(".headerContainer .fa-bars").addEventListener("click",e=>{e.target.classList.contains("fa-bars")?(e.target.classList.replace("fa-bars","fa-times"),e.target.classList.add("closeNavMenuButton")):(e.target.classList.replace("fa-times","fa-bars"),e.target.classList.remove("closeNavMenuButton"));let t=document.querySelector(".horizontalNavigation");"flex"!==t.style.display?t.style.display="flex":t.style.display="none"}),document.querySelectorAll("input").forEach(e=>{e.setAttribute("autocomplete","off")}),document.querySelector("header #mainAutocomplete").addEventListener("keyup",async function(e){let t=document.querySelector("header #mainAutocomplete").value;if("Enter"==e.key&&""!=t.split(/\s+/).join(""))window.location.href=`../../../../../../search_results/${t}`;else{let r=document.querySelector("header #mainAutocomplete_result");t&&""!=t.split(/\s+/).join("")?(getSearchResults(t,r),document.onclick=function(e){"autocomplete_list_results"!==e.target.id&&(r.style.display="none")}):r.style.display="none"}}),document.querySelector("header .smallScreenSearchIcon").addEventListener("click",()=>{setModalStyle(),closeAllPotentialOpenPopups(),document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .smallScreenSearchContainer").style.display="block",document.querySelector(".fullScreenPlaceholder .outerCloseButton").style.display="flex"}),document.querySelector(".smallScreenSearchContainer #mainAutocompleteSmallScreen").addEventListener("keyup",async function(e){let t=document.querySelector(".smallScreenSearchContainer #mainAutocompleteSmallScreen").value;if("Enter"==e.key&&""!=t.split(/\s+/).join(""))window.location.href=`../../../../../../search_results/${t}`;else{let r=document.querySelector(".smallScreenSearchContainer .recommendedContainer"),l=document.querySelector(".smallScreenSearchContainer .smallFormContentWrapper #mainAutocomplete_result");t&&""!=t.split(/\s+/).join("")?(getSearchResults(t,l,!0),document.querySelector(".smallScreenSearchContainer .noResultsFound").style.display="none"):(l.style.display="none",r.style.display="block",document.querySelector(".smallScreenSearchContainer .noResultsFound").style.display="none")}}),document.querySelector(".mainSearchContainer i").addEventListener("click",()=>{""!=(search_term=document.querySelector(".mainInputSearch").value).split(/\s+/).join("")&&(window.location.href=`../../../../../../search_results/${search_term}`)});const dropdownButton=document.querySelector(".userProfile");function checkForOpenContainers(){let e=!0,t=document.querySelectorAll(".addToListForm");for(let r=0,l=t.length;r<l;r++)if("none"!=t[r].style.display&&t[r].style.display){e=!1;break}return e}dropdownButton&&dropdownButton.addEventListener("click",()=>{let e=document.querySelector(".profileMenu");"flex"==e.style.display?e.style.display="none":(document.querySelector(".userSpace .notificationPopupWrapper").style.display="none",e.style.display="flex",document.onclick=function(t){let r=t.target.closest(".profileMenu"),l=t.target.closest(".userProfile");r||l||(e.style.display="none")})}),document.querySelector(".headerContainer .profileMenu .profileMenuOption:last-of-type")?.addEventListener("click",e=>{e.target.querySelector("button").click()});let previousOptionsContainer,previousEllipsis;function openContentOptionsMenu(e,t){if(!t.classList.contains("openAuthPrompt")){let r=checkForOpenContainers();if(r){previousOptionsContainer&&e.target!==previousEllipsis&&(previousOptionsContainer.style.display="none");let l=t.parentElement.querySelector(".articleOptionsContainer");"flex"!=l.style.display?(l.style.display="flex",document.onclick=function(e){e.target!==t&&(t.parentElement.querySelector(".articleOptionsContainer").style.display="none")}):l.style.display="none",previousOptionsContainer=t.parentElement.querySelector(".articleOptionsContainer"),previousEllipsis=t}}}async function highlightContent(e){if(!e.classList.contains("openAuthPrompt")){let t=e.closest(".articleContainer").id.split("#")[1],r=e.lastElementChild.innerText,l;l="Highlight article"==r?"highlight":"unhighlight";try{let o=await fetch("../../../../../../api/highlighted_articles/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify({article:t})});if(o.ok){let n=await o.json();"highlight"==l?(showMessage(n,"Success"),e.innerHTML='<i class="fas fa-times"></i><span>Unhighlight article</span>'):(showMessage(n,"Remove"),e.innerHTML='<i class="fas fa-highlighter"></i><span>Highlight article</span>')}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(s){}}}document.querySelectorAll(".contentInfoContainer .fa-ellipsis-h").forEach(e=>{e.addEventListener("click",function(t){openContentOptionsMenu(t,e)})}),document.querySelectorAll(".addToHighlightedButton").forEach(e=>{e.addEventListener("click",()=>{highlightContent(e)})}),document.querySelector(".userSpace .notificationBell")&&document.querySelector(".userSpace .notificationBell").addEventListener("click",async()=>{"block"==document.querySelector(".fullScreenPlaceholder .smallScreenSearchContainer").style.display&&(document.querySelector(".fullScreenPlaceholder").style.display="none",document.querySelector(".fullScreenPlaceholder .smallScreenSearchContainer").style.display="none",document.querySelector(".fullScreenPlaceholder .outerCloseButton").style.display="none",removeModalStyle());let e=document.querySelector(".notificationPopupWrapper");if("block"==e.style.display)e.style.display="none",document.querySelector(".unseenNotifications")?.remove(),document.querySelectorAll(".unseenNotification").forEach(e=>{e.classList.remove("unseenNotification")});else{e.style.display="block";try{let t=await fetch("../../../../../../api/notifications/",get_fetch_settings("PUT"));t.ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){}}});const notificationTabs=document.querySelectorAll(".notificationHeadersContainer button"),notificationContent=document.querySelectorAll(".notificationsContainer");notificationTabs.forEach(e=>{e.addEventListener("click",()=>{for(let t=0,r=notificationTabs.length;t<r;t++)notificationTabs[t].classList.remove("activeNotificationCategory"),notificationContent[t].classList.remove("activeNotificationContainer");notificationTabs[e.dataset.forTab].classList.add("activeNotificationCategory"),notificationContent[e.dataset.forTab].classList.add("activeNotificationContainer")})}),document.querySelectorAll(".handle").forEach(e=>{e.addEventListener("click",t=>{let r=t.target.closest(".sliderWrapper").querySelector(".slider"),l=parseInt(getComputedStyle(r).getPropertyValue("--slider-index")),o=parseInt(getComputedStyle(r).getPropertyValue("--items-per-screen")),n=Math.ceil(r.querySelectorAll(".contentWrapper").length/o);e.classList.contains("leftHandle")&&(l-1<0?r.style.setProperty("--slider-index",n-1):r.style.setProperty("--slider-index",l-1)),e.classList.contains("rightHandle")&&(l+1>=n?r.style.setProperty("--slider-index",0):r.style.setProperty("--slider-index",l+1))})}),document.querySelectorAll(".sliderWrapper .slider .subscribeButton").forEach(e=>{e.addEventListener("click",async()=>{if(!e.classList.contains("openAuthPrompt"))try{let t=e.closest(".contentWrapper").id.split("#")[1],r=e.innerText,l=await fetch(`../../api/sources/${t}/`,get_fetch_settings("PATCH"));l.ok?"Subscribe"==r?(e.classList.add("subscribed"),e.classList.replace("finButtonWhite","finButtonBlue"),e.innerText="Subscribed",showMessage(context="SOURCE HAS BEEN SUBSCRIBED!","Success")):(e.classList.remove("subscribed"),e.classList.replace("finButtonBlue","finButtonWhite"),e.innerText="Subscribe",showMessage(context="SOURCE HAS BEEN UNSUBSCRIBED!","Remove")):showMessage("Error: Network request failed unexpectedly!","Error")}catch(o){}})});const tabs=document.querySelectorAll(".tabsContainer button"),tabsContent=document.querySelectorAll(".tabsContent");async function save_keyword(){let e=document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal input");if(e.value.trim().length>2)try{let t={keyword:e.value},r=await fetch("../../api/notifications/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(t)});r.ok?(e.value="",showMessage("A new keyword has been created!","Success")):showMessage("Error: Network request failed unexpectedly!","Error")}catch(l){}else showMessage("A keyword must consist of at least 3 letters!","Error")}function getAuthPromptMsg(e){if(e.classList.contains("ap1"))return"Add Sources To Your Lists";if(e.classList.contains("ap2"))return"Subscribe To Sources";if(e.classList.contains("ap3"))return"Create Notifications";if(e.classList.contains("ap4"))return"Add Stocks To Your Portfolios";if(e.classList.contains("ap6"))return"Add Content To Your Lists";else if(e.classList.contains("ap7"))return"Rate This Source"}function openAuthPrompt(e){let t=document.querySelector(".fullScreenPlaceholder");document.querySelector(".fullScreenPlaceholder .authPromptContainer").style.display="block",t.style.display="flex";let r=getAuthPromptMsg(e);document.querySelector(".fullScreenPlaceholder .authPromptContainer h3").innerText=r,setModalStyle()}function check_list_status(e){let t=[],r=[],l=e.closest(".addSourceToListForm").querySelectorAll(".listContainer input:first-of-type"),o=document.querySelector(".fullScreenPlaceholder .addSourceToListForm").id.replace("source_id","");return l.forEach(e=>{let l=e.closest(".listContainer").querySelector(".sourcesInList").value;JSON.parse(l).includes(parseInt(o))&&!e.checked?r.push(e.id.split("id_list_")[1]):e.checked&&!JSON.parse(l).includes(parseInt(o))&&t.push(e.id.split("id_list_")[1])}),[t,r]}async function update_articles_in_list(e,t){try{let r=await fetch(`../../../../../../api/lists/${e}/`,get_fetch_settings("PATCH",{article_id:t}));r.ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(l){}}function openAddToListMenu(e){document.querySelector(".fullScreenPlaceholder .smallScreenSearchContainer").style.display="none",document.querySelector(".fullScreenPlaceholder .outerCloseButton").style.display="none";let t=e.target.closest(".articleContainer").id.split("#")[1],r=document.querySelectorAll(".fullScreenPlaceholder .listContainer input:first-of-type");r.forEach(e=>{let r=e.closest(".listContainer").querySelector(".articlesInList").value;JSON.parse(r).includes(parseInt(t))?e.checked=!0:e.checked=!1});let l=e.target.closest(".articleContainer").querySelector(".contentBody p")?.innerText;l?document.querySelector(".fullScreenPlaceholder .addToListForm h2 span").innerText=l:document.querySelector(".fullScreenPlaceholder .addToListForm h2 span").innerText="Retweet/Reply",setModalStyle(),document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .addToListForm").id="article_id"+t,document.querySelector(".fullScreenPlaceholder .addToListForm").style.display="block";let o=document.querySelector(".fullScreenPlaceholder .addSourceToListForm .saveButton");o.addEventListener("click",()=>{if(document.querySelector(".fullScreenPlaceholder .addToListForm").id.includes("article_id")){let e=o.closest(".addSourceToListForm").querySelectorAll(".listContainer input:first-of-type");e.forEach(e=>{let r=e.closest(".listContainer").querySelector(".articlesInList").value;(JSON.parse(r).includes(parseInt(t))&&!e.checked||e.checked&&!JSON.parse(r).includes(parseInt(t)))&&update_articles_in_list(e.id.split("id_list_")[1],t)}),showMessage("Lists have been updated!","Success"),window.location.reload()}},{once:!0}),document.querySelector(".fullScreenPlaceholder .addSourceToListForm .cancelButton")?.addEventListener("click",()=>{r.forEach(e=>{let r=e.closest(".listContainer").querySelector(".articlesInList").value;JSON.parse(r).includes(parseInt(t))?e.checked=!0:e.checked=!1})})}function closeFullScreenImage(){removeModalStyle(),document.querySelector(".fullScreenPlaceholder").style.display="none",document.querySelector(".fullScreenPlaceholder .smallScreenSearchContainer").style.display="none",document.querySelector(".fullScreenPlaceholder .fullScreenImage")?.remove(),document.querySelector(".fullScreenPlaceholder .outerCloseButton").style.display="none"}tabs.forEach(e=>{e.addEventListener("click",()=>{for(let t=0,r=tabs.length;t<r;t++)tabs[t].classList.remove("activatedTab"),tabsContent[t].classList.remove("tabsContentActive");tabs[e.dataset.forTab].classList.add("activatedTab"),tabsContent[e.dataset.forTab].classList.add("tabsContentActive")})}),document.querySelector(".notificationPopupWrapper .addKeywordsContainer button")?.addEventListener("click",()=>{document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal").style.display="flex"}),document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal .saveButton")?.addEventListener("click",()=>{save_keyword()}),document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal input")?.addEventListener("keypress",function(e){"Enter"===e.key&&save_keyword()}),document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal .discardButton")?.addEventListener("click",()=>{document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal").style.display="none"}),document.querySelectorAll(".openAuthPrompt").forEach(e=>e.addEventListener("click",()=>{openAuthPrompt(e)})),document.querySelector(".fullScreenPlaceholder .authPromptContainer .fa-times").addEventListener("click",()=>{document.querySelector(".fullScreenPlaceholder .authPromptContainer").style.display="none",document.querySelector(".fullScreenPlaceholder").style.display="none",removeModalStyle()}),document.querySelectorAll(".sourceAddToListButton").forEach(e=>{!e.classList.contains("openAuthPrompt")&&e.closest(".contentWrapper")&&e.addEventListener("click",()=>{setModalStyle();let t=e.closest(".contentWrapper").id.split("#")[1],r=e.closest(".contentWrapper").querySelector(".nameContainer span").innerText;document.querySelector(".fullScreenPlaceholder .addToListForm h2 span").innerText=r,document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .addSourceToListForm").style.display="block",document.querySelector(".fullScreenPlaceholder .addSourceToListForm").id="source_id"+t;let l=document.querySelectorAll(".fullScreenPlaceholder .listContainer input:first-of-type");l.forEach(e=>{let r=e.closest(".listContainer").querySelector(".sourcesInList").value;JSON.parse(r).includes(parseInt(t))?e.checked=!0:e.checked=!1}),document.querySelector(".fullScreenPlaceholder .addSourceToListForm .cancelButton")?.addEventListener("click",()=>{l.forEach(e=>{let r=e.closest(".listContainer").querySelector(".sourcesInList").value;JSON.parse(r).includes(parseInt(t))?e.checked=!0:e.checked=!1})})})}),document.querySelectorAll(".fullScreenPlaceholder .addSourceToListForm .fa-times").forEach(e=>{e.addEventListener("click",()=>{removeModalStyle(),document.querySelector(".addSourceToListForm").style.display="none",document.querySelector(".fullScreenPlaceholder").style.display="none"})}),document.querySelectorAll(".fullScreenPlaceholder .addSourceToListForm .saveButton").forEach(e=>{e.addEventListener("click",async()=>{if(document.querySelector(".fullScreenPlaceholder .addToListForm").id.includes("source_id")){let t=document.querySelector(".fullScreenPlaceholder .addSourceToListForm").id.replace("source_id",""),[r,l]=check_list_status(e);for(let o=0,n=r.length;o<n;o++)try{let s={source_id:t},a=await fetch(`../../api/lists/${r[o]}/`,get_fetch_settings("PATCH",s));a.ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(i){}for(let c=0,d=l.length;c<d;c++)try{let u={source_id:t},y=await fetch(`../../api/lists/${l[c]}/`,get_fetch_settings("PATCH",u));y.ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(p){}showMessage(context="Lists have been updated!","Success"),window.location.reload()}},{once:!0})}),document.querySelectorAll(".addToListButton").forEach(e=>{e.addEventListener("click",e=>{openAddToListMenu(e)})}),document.querySelectorAll(".addToListForm .listSelectionContainer .listContainer").forEach(e=>e.addEventListener("click",()=>{e.querySelector("input:first-of-type").checked=!e.querySelector("input:first-of-type").checked})),document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal .infoLink i")?.addEventListener("click",()=>{closeAllPotentialOpenPopups(),setModalStyle(),document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="block",document.querySelector(".fullScreenPlaceholder .explanationContainer h3").innerText="Keywords",document.querySelector(".fullScreenPlaceholder .explanationContainer .explanation").innerText="If you want to stay up-to-date on a particular topic, just add a keyword and I'll make sure you're notified as soon as any of your sources publish content containing that keyword on FinBrowser.";let e=document.querySelector(".fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times");e.addEventListener("click",()=>{removeModalStyle(),document.querySelector(".fullScreenPlaceholder").style.display="none",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="none"})}),document.querySelectorAll(".tweetImage").forEach(e=>{e.addEventListener("click",()=>{setModalStyle();let t=document.querySelector(".fullScreenPlaceholder");t.style.display="flex";let r=document.createElement("img");r.classList.add("fullScreenImage"),r.src=e.src,t.appendChild(r),t.querySelector(".outerCloseButton").style.display="flex",document.onclick=function(e){"IMG"!==e.target.nodeName&&closeFullScreenImage()}})}),document.querySelector(".fullScreenPlaceholder .outerCloseButton").addEventListener("click",()=>{closeFullScreenImage()});
