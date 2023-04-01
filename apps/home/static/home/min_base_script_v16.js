function setModalStyle(){document.querySelector("body").style.overflow="hidden",document.querySelector(".pageWrapper").style.opacity="0.1"}function removeModalStyle(){document.querySelector("body").style.removeProperty("overflow"),document.querySelector(".pageWrapper").style.removeProperty("opacity")}function getCookie(e){let t=null;if(document.cookie&&""!==document.cookie){let l=document.cookie.split(";");for(let r=0;r<l.length;r++){let o=l[r].trim();if(o.substring(0,e.length+1)===e+"="){t=decodeURIComponent(o.substring(e.length+1));break}}}return t}function get_fetch_settings(e,t=!1){let l={method:e,headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin"};return t&&(l.body=JSON.stringify(t)),l}function showMessage(e,t){document.querySelectorAll(".messages").forEach(e=>{e.remove()});let l=document.createElement("ul");l.classList.add("messages");let r=document.createElement("li");r.innerText=e,"Success"==t?r.classList.add("success"):"Remove"==t?r.classList.add("remove"):r.classList.add("error"),l.appendChild(r),document.querySelector(".overlay").appendChild(l)}async function getSearchResults(e,t,l=!1){try{let r=await fetch(`../../../../../../api/search_site/${e}`,get_fetch_settings("GET"));if(r.ok){let o=await r.json();if(l&&o[0].length||o[1].length||o[2].length?document.querySelector(".smallScreenSearchContainer .recommendedContainer").style.display="none":!l||o[0].length||o[1].length||o[2].length||(document.querySelector(".smallScreenSearchContainer .noResultsFound").style.display="block",document.querySelector(".smallScreenSearchContainer .noResultsFound").innerText="I'm sorry but there are no results for "+e),t.style.display="flex",t.innerHTML="",o[0].length>0&&(t.innerHTML+='<div class="searchResultHeader">Stocks</div>',o[0].forEach(e=>{let l=`<div class="searchResult"><div class="stockContainer"><div class="stockTicker">${e.ticker}</div><div class="companyName">${e.full_company_name}</div><a href="../../../../../../stock/${e.ticker}"></a></div></div>`;t.innerHTML+=l})),o[1].length>0&&(t.innerHTML+='<div class="searchResultHeader">Sources</div>',o[1].forEach(e=>{let l=`<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${e.favicon_path}"><span>${e.name}</span><a href="../../../../../../source/${e.slug}"></a></div>`;t.innerHTML+=l})),o[2].length>0){t.innerHTML+='<div class="searchResultHeader">Articles</div>';for(let n=0,s=o[2].length;n<s;n++){let a=o[2][n].source.favicon_path,i=o[2][n].title,c=o[2][n].link,d=`<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${a}"><span>${i}</span><a href="${c}" target="_blank"></a></div>`;t.innerHTML+=d}}}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(u){}}function closeAllPotentialOpenPopups(){document.querySelector(".fullScreenPlaceholder .addToListForm").style.display="none",document.querySelector(".fullScreenPlaceholder .authPromptContainer").style.display="none",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="none",document.querySelector(".portfolioMenuWrapper")&&(document.querySelector(".portfolioMenuWrapper").style.display="none",document.querySelector(".portfolioMenuWrapper .addStocksContainer").style.display="none",document.querySelector(".portfolioMenuWrapper .editMenu").style.display="none",document.querySelector(".portfolioMenuWrapper .warningMessageContainer").style.display="none"),document.querySelector(".listMenuWrapper")&&(document.querySelector(".listMenuWrapper").style.display="none",document.querySelector(".listMenuWrapper .addSourceContainer").style.display="none",document.querySelector(".listMenuWrapper .editMenu").style.display="none",document.querySelector(".listMenuWrapper .warningMessageContainer").style.display="none"),document.querySelector(".stockMenuWrapper")&&(document.querySelector(".stockMenuWrapper").style.display="none",document.querySelector(".stockMenuWrapper .addStockContainer").style.display="none"),document.querySelector(".keywordCreationWrapper")&&(document.querySelector(".keywordCreationWrapper").style.display="none"),document.querySelector(".notificationPopupWrapper").style.display="none",document.querySelector(".sourceRatingsWrapper")&&(document.querySelector(".sourceRatingsWrapper").style.display="none")}document.querySelector(".headerContainer .fa-bars").addEventListener("click",e=>{e.target.classList.contains("fa-bars")?(e.target.classList.replace("fa-bars","fa-times"),e.target.classList.add("closeNavMenuButton")):(e.target.classList.replace("fa-times","fa-bars"),e.target.classList.remove("closeNavMenuButton"));let t=document.querySelector(".horizontalNavigation");"flex"!==t.style.display?t.style.display="flex":t.style.display="none"}),document.querySelectorAll("input").forEach(e=>{e.setAttribute("autocomplete","off")}),document.querySelector("header #mainAutocomplete").addEventListener("keyup",async function(e){let t=document.querySelector("header #mainAutocomplete").value;if("Enter"==e.key&&""!=t.replaceAll(/\s/g,""))window.location.href=`../../../../../../search_results/${t}`;else{let l=document.querySelector("header #mainAutocomplete_result");t&&""!=t.replaceAll(/\s/g,"")?(getSearchResults(t,l),document.onclick=function(e){"autocomplete_list_results"!==e.target.id&&(l.style.display="none")}):l.style.display="none"}}),document.querySelector("header .smallScreenSearchIcon").addEventListener("click",()=>{setModalStyle(),closeAllPotentialOpenPopups(),document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .smallScreenSearchContainer").style.display="block",document.querySelector(".fullScreenPlaceholder .closeImageButton").style.display="flex"}),document.querySelector(".smallScreenSearchContainer #mainAutocomplete").addEventListener("keyup",async function(e){let t=document.querySelector(".smallScreenSearchContainer #mainAutocomplete").value;if("Enter"==e.key&&""!=t.replaceAll(/\s/g,""))window.location.href=`../../../../../../search_results/${t}`;else{let l=document.querySelector(".smallScreenSearchContainer .recommendedContainer"),r=document.querySelector(".smallScreenSearchContainer .smallFormContentWrapper #mainAutocomplete_result");t&&""!=t.replaceAll(/\s/g,"")?(getSearchResults(t,r,!0),document.querySelector(".smallScreenSearchContainer .noResultsFound").style.display="none"):(r.style.display="none",l.style.display="block",document.querySelector(".smallScreenSearchContainer .noResultsFound").style.display="none")}}),document.querySelector(".mainSearchContainer i").addEventListener("click",()=>{""!=(search_term=document.querySelector(".mainInputSearch").value).replaceAll(/\s/g,"")&&(window.location.href=`../../../../../../search_results/${search_term}`)});const dropdownButton=document.querySelector(".userProfile");function checkForOpenContainers(){let e=!0,t=document.querySelectorAll(".addToListForm");for(let l=0,r=t.length;l<r;l++)if("none"!=t[l].style.display&&t[l].style.display){e=!1;break}return e}dropdownButton&&dropdownButton.addEventListener("click",()=>{let e=document.querySelector(".profileMenu");"flex"==e.style.display?e.style.display="none":(document.querySelector(".userSpace .notificationPopupWrapper").style.display="none",e.style.display="flex",document.onclick=function(t){let l=t.target.closest(".profileMenu"),r=t.target.closest(".userProfile");l||r||(e.style.display="none")})}),document.querySelector(".headerContainer .profileMenu .profileMenuOption:last-of-type")?.addEventListener("click",e=>{e.target.querySelector("button").click()});let previousOptionsContainer,previousEllipsis;function openContentOptionsMenu(e,t){if(!t.classList.contains("openAuthPrompt")){let l=checkForOpenContainers();if(l){previousOptionsContainer&&e.target!==previousEllipsis&&(previousOptionsContainer.style.display="none");let r=t.parentElement.querySelector(".articleOptionsContainer");"flex"!=r.style.display?(r.style.display="flex",document.onclick=function(e){e.target!==t&&(t.parentElement.querySelector(".articleOptionsContainer").style.display="none")}):r.style.display="none",previousOptionsContainer=t.parentElement.querySelector(".articleOptionsContainer"),previousEllipsis=t}}}async function highlightContent(e){if(!e.classList.contains("openAuthPrompt")){let t=e.closest(".articleContainer").id.split("#")[1],l=e.lastElementChild.innerText,r;r="Highlight article"==l?"highlight":"unhighlight";try{let o=await fetch("../../../../../../api/highlighted_articles/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify({article:t})});if(o.ok){let n=await o.json();"highlight"==r?(showMessage(n,"Success"),e.innerHTML='<i class="fas fa-times"></i><span>Unhighlight article</span>'):(showMessage(n,"Remove"),e.innerHTML='<i class="fas fa-highlighter"></i><span>Highlight article</span>')}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(s){}}}document.querySelectorAll(".contentInfoContainer .fa-ellipsis-h").forEach(e=>{e.addEventListener("click",function(t){openContentOptionsMenu(t,e)})}),document.querySelectorAll(".addToHighlightedButton").forEach(e=>{e.addEventListener("click",()=>{highlightContent(e)})}),document.querySelector(".userSpace .notificationBell")&&document.querySelector(".userSpace .notificationBell").addEventListener("click",async()=>{"block"==document.querySelector(".fullScreenPlaceholder .smallScreenSearchContainer").style.display&&(document.querySelector(".fullScreenPlaceholder").style.display="none",document.querySelector(".fullScreenPlaceholder .smallScreenSearchContainer").style.display="none",document.querySelector(".fullScreenPlaceholder .closeImageButton").style.display="none",removeModalStyle());let e=document.querySelector(".notificationPopupWrapper");if("block"==e.style.display)e.style.display="none",document.querySelector(".unseenNotifications").remove(),document.querySelectorAll(".unseenNotification").forEach(e=>{e.classList.remove("unseenNotification")});else{e.style.display="block";try{let t=await fetch("../../../../../../api/notifications/",get_fetch_settings("PUT"));t.ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(l){}}});const notificationTabs=document.querySelectorAll(".notificationHeadersContainer button"),notificationContent=document.querySelectorAll(".notificationsContainer");notificationTabs.forEach(e=>{e.addEventListener("click",()=>{for(let t=0,l=notificationTabs.length;t<l;t++)notificationTabs[t].classList.remove("activeNotificationCategory"),notificationContent[t].classList.remove("activeNotificationContainer");notificationTabs[e.dataset.forTab].classList.add("activeNotificationCategory"),notificationContent[e.dataset.forTab].classList.add("activeNotificationContainer")})}),document.querySelectorAll(".handle").forEach(e=>{e.addEventListener("click",t=>{let l=t.target.closest(".sliderWrapper").querySelector(".slider"),r=parseInt(getComputedStyle(l).getPropertyValue("--slider-index")),o=parseInt(getComputedStyle(l).getPropertyValue("--items-per-screen")),n=Math.ceil(l.querySelectorAll(".contentWrapper").length/o);e.classList.contains("leftHandle")&&(r-1<0?l.style.setProperty("--slider-index",n-1):l.style.setProperty("--slider-index",r-1)),e.classList.contains("rightHandle")&&(r+1>=n?l.style.setProperty("--slider-index",0):l.style.setProperty("--slider-index",r+1))})}),document.querySelectorAll(".sliderWrapper .slider .subscribeButton").forEach(e=>{e.addEventListener("click",async()=>{if(!e.classList.contains("openAuthPrompt"))try{let t=e.closest(".contentWrapper").id.split("#")[1],l=e.innerText,r=await fetch(`../../api/sources/${t}/`,get_fetch_settings("PATCH"));r.ok?"Subscribe"==l?(e.classList.add("subscribed"),e.innerText="Subscribed",showMessage(context="SOURCE HAS BEEN SUBSCRIBED!","Success")):(e.classList.remove("subscribed"),e.innerText="Subscribe",showMessage(context="SOURCE HAS BEEN UNSUBSCRIBED!","Remove")):showMessage("Error: Network request failed unexpectedly!","Error")}catch(o){}})});const tabs=document.querySelectorAll(".tabsContainer button"),tabsContent=document.querySelectorAll(".tabsContent");async function save_keyword(){let e=document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal input");if(e.value.trim().length>2)try{let t={keyword:e.value},l=await fetch("../../api/notifications/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(t)});l.ok?(e.value="",showMessage("A new keyword has been created!","Success")):showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){}else showMessage("A keyword must consist of at least 3 letters!","Error")}function getAuthPromptMsg(e){if(e.classList.contains("ap1"))return"Add this source to your lists to stay up to date with the latest content";if(e.classList.contains("ap2"))return"Subscribe to this source to your lists to stay up to date with the latest content";if(e.classList.contains("ap3"))return"Get instant notifications when new content is available";if(e.classList.contains("ap4"))return"Add this stock to your portfolios to stay up to date with the latest analysis and news";if(e.classList.contains("ap5"))return"Add this stock to your lists";else if(e.classList.contains("ap6"))return"Add content to your lists";else if(e.classList.contains("ap7"))return"Rate this source"}function openAuthPrompt(e){let t=document.querySelector(".fullScreenPlaceholder");document.querySelector(".fullScreenPlaceholder .authPromptContainer").style.display="block",t.style.display="flex";let l=getAuthPromptMsg(e);document.querySelector(".fullScreenPlaceholder .authPromptContainer h3").innerText=l,setModalStyle()}function check_list_status(e){let t=[],l=[],r=e.closest(".addSourceToListForm").querySelectorAll(".listContainer input:first-of-type"),o=document.querySelector(".fullScreenPlaceholder .addSourceToListForm").id.replace("source_id","");return r.forEach(e=>{let r=e.closest(".listContainer").querySelector(".sourcesInList").value;JSON.parse(r).includes(parseInt(o))&&!e.checked?l.push(e.id.split("id_list_")[1]):e.checked&&!JSON.parse(r).includes(parseInt(o))&&t.push(e.id.split("id_list_")[1])}),[t,l]}async function update_articles_in_list(e,t){try{let l=await fetch(`../../../../../../api/lists/${e}/`,get_fetch_settings("PATCH",{article_id:t}));l.ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){}}function openAddToListMenu(e){document.querySelector(".fullScreenPlaceholder .smallScreenSearchContainer").style.display="none",document.querySelector(".fullScreenPlaceholder .closeImageButton").style.display="none";let t=e.target.closest(".articleContainer").id.split("cc#")[1],l=document.querySelectorAll(".fullScreenPlaceholder .listContainer input:first-of-type");l.forEach(e=>{let l=e.closest(".listContainer").querySelector(".articlesInList").value;JSON.parse(l).includes(parseInt(t))?e.checked=!0:e.checked=!1});let r=e.target.closest(".articleContainer").querySelector(".contentBody p")?.innerText;document.querySelector(".fullScreenPlaceholder .addToListForm h2 span").innerText=r,setModalStyle(),document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .addToListForm").id="article_id"+t,document.querySelector(".fullScreenPlaceholder .addToListForm").style.display="block";let o=document.querySelector(".fullScreenPlaceholder .addSourceToListForm .saveButton");o.addEventListener("click",()=>{if(document.querySelector(".fullScreenPlaceholder .addToListForm").id.includes("article_id")){let e=o.closest(".addSourceToListForm").querySelectorAll(".listContainer input:first-of-type");e.forEach(e=>{let l=e.closest(".listContainer").querySelector(".articlesInList").value;(JSON.parse(l).includes(parseInt(t))&&!e.checked||e.checked&&!JSON.parse(l).includes(parseInt(t)))&&update_articles_in_list(e.id.split("id_list_")[1],t)}),showMessage("Lists have been updated!","Success"),window.location.reload()}},{once:!0})}tabs.forEach(e=>{e.addEventListener("click",()=>{for(let t=0,l=tabs.length;t<l;t++)tabs[t].classList.remove("activatedTab"),tabsContent[t].classList.remove("tabsContentActive");tabs[e.dataset.forTab].classList.add("activatedTab"),tabsContent[e.dataset.forTab].classList.add("tabsContentActive")})}),document.querySelector(".notificationPopupWrapper .addKeywordsContainer button")?.addEventListener("click",()=>{document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal").style.display="flex"}),document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal .saveButton")?.addEventListener("click",()=>{save_keyword()}),document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal input")?.addEventListener("keypress",function(e){"Enter"===e.key&&save_keyword()}),document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal .discardButton")?.addEventListener("click",()=>{document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal").style.display="none"}),document.querySelectorAll(".openAuthPrompt").forEach(e=>e.addEventListener("click",()=>{openAuthPrompt(e)})),document.querySelector(".fullScreenPlaceholder .authPromptContainer .fa-times").addEventListener("click",()=>{document.querySelector(".fullScreenPlaceholder .authPromptContainer").style.display="none",document.querySelector(".fullScreenPlaceholder").style.display="none",removeModalStyle()}),document.querySelectorAll(".sourceAddToListButton").forEach(e=>{!e.classList.contains("openAuthPrompt")&&e.closest(".contentWrapper")&&e.addEventListener("click",()=>{setModalStyle();let t=e.closest(".contentWrapper").id.split("#")[1],l=e.closest(".contentWrapper").querySelector(".nameContainer span").innerText;document.querySelector(".fullScreenPlaceholder .addToListForm h2 span").innerText=l,document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .addSourceToListForm").style.display="block",document.querySelector(".fullScreenPlaceholder .addSourceToListForm").id="source_id"+t;let r=document.querySelectorAll(".fullScreenPlaceholder .listContainer input:first-of-type");r.forEach(e=>{let l=e.closest(".listContainer").querySelector(".sourcesInList").value;JSON.parse(l).includes(parseInt(t))?e.checked=!0:e.checked=!1})})}),document.querySelectorAll(".fullScreenPlaceholder .addSourceToListForm .fa-times").forEach(e=>{e.addEventListener("click",()=>{removeModalStyle(),document.querySelector(".addSourceToListForm").style.display="none",document.querySelector(".fullScreenPlaceholder").style.display="none"})}),document.querySelector(".fullScreenPlaceholder .addSourceToListForm .cancelButton")?.addEventListener("click",()=>{removeModalStyle(),document.querySelector(".addSourceToListForm").style.display="none",document.querySelector(".fullScreenPlaceholder").style.display="none"}),document.querySelectorAll(".fullScreenPlaceholder .addSourceToListForm .saveButton").forEach(e=>{e.addEventListener("click",async()=>{if(document.querySelector(".fullScreenPlaceholder .addToListForm").id.includes("source_id")){let t=document.querySelector(".fullScreenPlaceholder .addSourceToListForm").id.replace("source_id",""),[l,r]=check_list_status(e);for(let o=0,n=l.length;o<n;o++)try{let s={source_id:t},a=await fetch(`../../api/lists/${l[o]}/`,get_fetch_settings("PATCH",s));a.ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(i){}for(let c=0,d=r.length;c<d;c++)try{let u={source_id:t},y=await fetch(`../../api/lists/${r[c]}/`,get_fetch_settings("PATCH",u));y.ok||showMessage("Error: Network request failed unexpectedly!","Error")}catch(p){}showMessage(context="Lists have been updated!","Success"),window.location.reload()}},{once:!0})}),document.querySelectorAll(".addToListButton").forEach(e=>{e.addEventListener("click",e=>{openAddToListMenu(e)})}),document.querySelectorAll(".addToListForm .listSelectionContainer .listContainer").forEach(e=>e.addEventListener("click",()=>{e.querySelector("input:first-of-type").checked=!e.querySelector("input:first-of-type").checked})),document.querySelector(".notificationPopupWrapper .createKeywordNotificationModal .infoLink i")?.addEventListener("click",()=>{closeAllPotentialOpenPopups(),setModalStyle(),document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="block",document.querySelector(".fullScreenPlaceholder .explanationContainer h3").innerText="Keywords",document.querySelector(".fullScreenPlaceholder .explanationContainer .explanation").innerText="If you want to be notified when new content is published on a specific topic, add a keyword and you will receive an alert when any of the sources publish content containing that keyword on FinBrowser.";let e=document.querySelector(".fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times");e.addEventListener("click",()=>{removeModalStyle(),document.querySelector(".fullScreenPlaceholder").style.display="none",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="none"})}),document.querySelectorAll(".tweetImage").forEach(e=>{e.addEventListener("click",()=>{setModalStyle();let t=document.querySelector(".fullScreenPlaceholder");t.style.display="flex";let l=document.createElement("img");l.classList.add("fullScreenImage"),l.src=e.src,t.appendChild(l),t.querySelector(".closeImageButton").style.display="flex"})}),document.querySelector(".fullScreenPlaceholder .closeImageButton").addEventListener("click",()=>{removeModalStyle(),document.querySelector(".fullScreenPlaceholder").style.display="none",document.querySelector(".fullScreenPlaceholder .smallScreenSearchContainer").style.display="none",document.querySelector(".fullScreenPlaceholder .fullScreenImage")?.remove(),document.querySelector(".fullScreenPlaceholder .closeImageButton").style.display="none"});