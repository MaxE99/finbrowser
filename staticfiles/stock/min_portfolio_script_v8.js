if(location.href.includes("?commentary=")){let e=document.querySelectorAll(".pageWrapper .tabsContainer button"),t=document.querySelectorAll(".pageWrapper .tabsContent");for(let o=0,r=e.length;o<r;o++)e[o].classList.remove("activatedTab"),t[o].classList.remove("tabsContentActive");e[1].classList.add("activatedTab"),t[1].classList.add("tabsContentActive")}if(location.href.includes("?news=")){let l=document.querySelectorAll(".pageWrapper .tabsContainer button"),n=document.querySelectorAll(".pageWrapper .tabsContent");for(let a=0,i=l.length;a<i;a++)l[a].classList.remove("activatedTab"),n[a].classList.remove("tabsContentActive");l[2].classList.add("activatedTab"),n[2].classList.add("tabsContentActive")}function openAddStocksMenu(){document.querySelector(".portfolioMenuWrapper").style.display="block",document.querySelector(".addStocksContainer").style.display="block",setModalStyle(),document.querySelector(".addStocksContainer #textInput").addEventListener("keyup",async function(e){let t=[],o=document.querySelectorAll("table tr .ticker");for(let r=0,l=o.length;r<l;r++)t.push(o[r].innerText);let n=document.querySelector(".addStocksContainer #textInput"),a=n.value,i=e.target.closest(".addStocksContainer").querySelector("#searchResultsContainer"),s=e.target.closest(".addStocksContainer").querySelector(".selectionContainer");if(document.querySelector(".addStocksContainer .buttonContainer .cancelButton").addEventListener("click",()=>{selectedStocks=[],s.innerHTML=""}),a&&""!=a.split(/\s+/).join("")){i.style.display="block",s.style.display="none";try{let c=await fetch(`../../api/stocks/?search_term=${a}`,get_fetch_settings("GET"));if(c.ok){let d=await c.json();i.innerHTML="";let p=document.createElement("div");p.classList.add("resultHeader"),p.innerText="Results:",i.append(p),d.length>0&&d.forEach(e=>{if(!selectedStocks.includes(e.stock_id)&&!t.includes(e.ticker)){let o=document.createElement("div");o.classList.add("searchResult");let r=document.createElement("div");r.classList.add("stockContainer");let l=document.createElement("div");l.innerText=e.ticker,l.id="pssi#"+e.stock_id,l.classList.add("stockTicker");let a=document.createElement("div");a.innerText=e.full_company_name,a.classList.add("companyName"),r.append(l,a),o.appendChild(r),i.appendChild(o),o.addEventListener("click",function t(){o.removeEventListener("click",t),selectedStocks.push(e.stock_id);let r=document.createElement("i");r.classList.add("fas","fa-times"),r.addEventListener("click",()=>{r.parentElement.remove(),selectedStocks=selectedStocks.filter(function(e){return e.toString()!==r.closest(".searchResult").querySelector(".stockTicker").id.split("#")[1]})}),o.appendChild(r),s.appendChild(o),i.style.display="none",s.style.display="block",n.value=""})}})}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(y){}}else i.style.display="none",s.style.display="block"})}document.querySelector(".firstRow .nameContainer").addEventListener("click",()=>{let e=document.querySelector(".firstRow .nameContainer i"),t=document.querySelector(".portfolioOptionsContainer");"block"===t.style.display?(t.style.display="none",e.classList.replace("fa-chevron-up","fa-chevron-down")):(t.style.display="block",e.classList.replace("fa-chevron-down","fa-chevron-up"))}),document.querySelector(".createPortfolioButton").addEventListener("click",async()=>{try{let e=await fetch("../../api/portfolios/",get_fetch_settings("POST"));if(e.ok){let t=await e.json();window.location.replace(`../../portfolio/${t.portfolio_id}`)}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(o){}},{once:!0});let selectedStocks=[];document.querySelector(".actionButtonContainer .addStocksButton").addEventListener("click",()=>{openAddStocksMenu()}),document.querySelectorAll(".emptyInformationContainer button").forEach(e=>e.addEventListener("click",()=>{openAddStocksMenu()})),document.querySelector(".addStocksContainer .closeAddStockContainer").addEventListener("click",()=>{document.querySelector(".portfolioMenuWrapper").style.display="none",document.querySelector(".addStocksContainer").style.display="none",removeModalStyle()}),document.querySelector(".editPortfolioButton").addEventListener("click",()=>{document.querySelector(".portfolioMenuWrapper").style.display="block",document.querySelector(".editMenu").style.display="block",setModalStyle()}),document.querySelector(".editMenu .fa-times").addEventListener("click",()=>{document.querySelector(".portfolioMenuWrapper").style.display="none",document.querySelector(".editMenu").style.display="none",removeModalStyle()});let activatedButton=!1;document.querySelector(".portfolioMenuWrapper .addStocksContainer .addStocksButton").addEventListener("click",async()=>{if(selectedStocks.length||showMessage("You Need To Select Stocks!","Error"),selectedStocks.length&&!activatedButton){activatedButton=!0;try{let e=document.querySelector(".firstRow .nameContainer h2").id,t={stocks:selectedStocks,portfolio:e},o=await fetch("../../api/portfolio_stocks/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(t)});o.ok?(showMessage("Portfolio has been updated!","Success"),window.location.reload()):showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){}}}),document.querySelector(".editMenu .deletePortfolioButton").addEventListener("click",()=>{let e=document.querySelector(".nameContainer h2").id;1===document.querySelectorAll(".portfoliosContainer .portfolioOption").length?showMessage("You are not allowed to delete your last portfolio!","Error"):(document.querySelector(".portfolioMenuWrapper").style.display="none",document.querySelector(".editMenu").style.display="none",document.querySelector(".portfolioMenuWrapper").style.display="block",document.querySelector(".portfolioMenuWrapper .warningMessageContainer").style.display="flex",document.querySelector(".portfolioMenuWrapper .warningMessageContainer .discardButton").addEventListener("click",()=>{removeModalStyle(),document.querySelector(".portfolioMenuWrapper").style.display="none",document.querySelector(".portfolioMenuWrapper .warningMessageContainer").style.display="none"}),document.querySelector(".portfolioMenuWrapper .warningMessageContainer .confirmButton").addEventListener("click",async()=>{try{let t=await fetch(`../../api/portfolios/${e}/`,get_fetch_settings("DELETE"));t.ok?(showMessage("Portfolio has been deleted!","Remove"),document.querySelectorAll(".portfolioOptionsContainer .portfolioOption").forEach(t=>{t.id.replace("wlist","")!==e&&window.location.replace(`../../portfolio/${t.id.replace("wlist","")}`)})):showMessage("Error: Network request failed unexpectedly!","Error")}catch(o){}},{once:!0}))}),document.querySelectorAll(".stockContainer .fa-trash-can").forEach(e=>{e.addEventListener("click",async e=>{let t=e.target.closest(".stockContainer").id.replace("pstock","");try{let o=await fetch(`../../api/portfolio_stocks/${t}/`,get_fetch_settings("DELETE"));o.ok?(showMessage("Stock has been removed!","Remove"),e.target.closest(".stockContainer").remove(),document.querySelector("table .stockContainer")||window.location.reload()):showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){}})}),document.querySelector(".menuContainer .editMenu .saveEditsButton").addEventListener("click",async()=>{let e=document.querySelector(".firstRow .nameContainer h2").id,t=document.querySelector(".editMenu .portfolioNameContainer input").value,o=document.querySelector(".editMenu .mainPortfolioContainer input").checked,r={name:t,main:o};if(t.trim().length)try{let l=await fetch(`../../api/portfolios/${e}/`,{method:"PATCH",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(r)});l.ok?(showMessage("Portfolio has been updated!","Success"),window.location.reload()):showMessage("Error: Network request failed unexpectedly!","Error")}catch(n){}else showMessage("Please enter a name!","Error")},{once:!0});const portfolio_id=document.querySelector(".firstRow .nameContainer h2").id;function removeSourceFromBlacklist(e){e.addEventListener("click",async()=>{let t=e.closest(".blacklistedSourceContainer").id.split("#")[1];try{let o=await fetch(`../../api/portfolios/${portfolio_id}/`,{method:"PATCH",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify({source_id:t})});o.ok?(e.closest(".blacklistedSourceContainer").remove(),blacklisted_sources=blacklisted_sources.filter(e=>e!==t)):showMessage("Error: Network request failed unexpectedly!","Error")}catch(r){}})}document.querySelectorAll(".blacklistSourceContainer .blacklistedSourceContainer .fa-times").forEach(e=>{removeSourceFromBlacklist(e)});let blacklisted_sources=[];function closeBlacklistExplanation(){document.querySelector(".fullScreenPlaceholder").style.display="none",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="none",document.querySelector(".portfolioMenuWrapper").style.display="flex",document.querySelector(".portfolioMenuWrapper .editMenu").style.display="block"}async function deleteKeywords(e,t=!1){let o=e.target.closest(".keywordContainer").id.replace("wkw","");try{let r=await fetch(`../../api/portfolio_keywords/${o}/`,get_fetch_settings("DELETE"));if(r.ok){if(e.target.closest(".keywordContainer").remove(),showMessage("Keyword has been removed!","Remove"),t)t.innerText-=1;else{let l=document.querySelector(".keywordModal .keywordHeader span").id.replace("psi","");document.querySelectorAll("table tr").forEach(e=>{e.id==`pstock${l}`&&(e.querySelector("td .keywordButton").innerText=parseInt(e.querySelector("td .keywordButton").innerText)-1)})}}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(n){}}function sortKeywords(e){return e.sort(function(e,t){var o=e.keyword.toUpperCase(),r=t.keyword.toUpperCase();return o<r?-1:o>r?1:0}),e}async function getKeywords(e,t){try{let o=await fetch(`../../api/portfolio_stocks/${e}/`,get_fetch_settings("GET"));if(o.ok){let r=await o.json(),l=sortKeywords(r.keywords),n=document.querySelector(".portfolioMenuWrapper .keywordModal .keywordsContainer");n.innerHTML="",l.forEach(e=>{let o=document.createElement("div");o.classList.add("keywordContainer"),o.id="wkw"+e.pkeyword_id;let r=document.createElement("span");r.innerText=e.keyword;let l=document.createElement("i");l.addEventListener("click",e=>{deleteKeywords(e,t)}),l.classList.add("fas","fa-times"),o.append(r,l),n.appendChild(o)})}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(a){}}document.querySelectorAll(".blacklistSourceContainer .blacklistedSourceContainer").forEach(e=>{blacklisted_sources.push(e.id.split("#")[1])}),document.querySelector(".blacklistSourceContainer #textInput")&&document.querySelector(".blacklistSourceContainer #textInput").addEventListener("keyup",async function(){let e=document.querySelector(".blacklistSourceContainer #textInput").value,t=document.querySelector(".blacklistSourceContainer #searchResultsContainer"),o=document.querySelector(".blacklistSourceContainer .selectionContainer");if(e&&""!=e.split(/\s+/).join("")){t.style.display="block",o.style.display="none";try{let r=await fetch(`../../api/sources/?blacklist_search=${e}&portfolio_id=${portfolio_id}`,get_fetch_settings("GET"));if(r.ok){let l=await r.json();t.innerHTML="";let n=document.createElement("div");n.innerText="Results:",t.append(n),l.length>0&&l.forEach(e=>{if(!blacklisted_sources.includes(e.source_id)){let r=document.createElement("div");r.classList.add("searchResult");let l=document.createElement("img");l.src=`https://finbrowser.s3.us-east-2.amazonaws.com/static/${e.favicon_path}`;let n=document.createElement("span");n.innerText=e.name,n.id=`source_id_${e.source_id}`,r.append(l,n),t.appendChild(r),r.addEventListener("click",async()=>{try{let r={source_id:e.source_id},l=await fetch(`../../api/portfolios/${portfolio_id}/`,{method:"PATCH",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(r)});if(l.ok){t.style.display="none",o.style.display="block",blacklisted_sources.push(e.source_id);let n=document.createElement("div");n.classList.add("blacklistedSourceContainer"),n.id=`blsid#${e.source_id}`;let a=document.createElement("img");a.src=`/static/${e.favicon_path}`;let i=document.createElement("span");i.innerText=e.name;let s=document.createElement("i");s.classList.add("fas","fa-times"),n.append(a,i,s),o.appendChild(n),removeSourceFromBlacklist(n)}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(c){}})}})}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(a){}}else t.style.display="none",o.style.display="block"}),document.querySelector(".portfolioMenuWrapper .editMenu .blacklistSourceContainer .header .infoLink i").addEventListener("click",()=>{document.querySelector(".portfolioMenuWrapper").style.display="none",document.querySelector(".portfolioMenuWrapper .editMenu").style.display="none",document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="block",document.querySelector(".fullScreenPlaceholder .explanationContainer h3").innerText="Blacklist Sources",document.querySelector(".fullScreenPlaceholder .explanationContainer .explanation").innerText="If you're seeing content from sources that you don't find helpful or relevant, you can easily remove them from your feed by adding them to your blacklisted sources. By doing so, you'll no longer see content from those sources and can focus on the ones that are most helpful to you.";let e=document.querySelector(".fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times");e.addEventListener("click",()=>{closeBlacklistExplanation()},{once:!0})}),document.querySelector(".portfolioMenuWrapper .editMenu .mainPortfolioContainer .infoLink i").addEventListener("click",()=>{document.querySelector(".portfolioMenuWrapper").style.display="none",document.querySelector(".portfolioMenuWrapper .editMenu").style.display="none",document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="block",document.querySelector(".fullScreenPlaceholder .explanationContainer h3").innerText="Main Portfolio",document.querySelector(".fullScreenPlaceholder .explanationContainer .explanation").innerText="Your main portfolio is the one that opens up whenever you click on the Portfolio button in the header. It's important to note that you always need to have at least one main portfolio. If you only have one portfolio, then you won't be able to delete it as it is your main one. But, if you have multiple portfolios and you delete your main one, then the next portfolio in alphabetical order will become your new main portfolio. Don't worry though, you can easily change your main portfolio by opening the edit menu of a portfolio that is currently not your main one and setting it as your new main portfolio. It's as simple as that!";let e=document.querySelector(".fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times");e.addEventListener("click",()=>{closeBlacklistExplanation()},{once:!0})});const addKeywordsButton=document.querySelectorAll(".stockContainer td .keywordButton");addKeywordsButton.forEach(e=>{e.addEventListener("click",()=>{setModalStyle(),document.querySelector(".portfolioMenuWrapper").style.display="block",document.querySelector(".portfolioMenuWrapper .keywordModal").style.display="block";let t=e.closest("tr").id.replace("pstock","");document.querySelector(".keywordHeader span").innerText=e.closest("tr").querySelector(".ticker").innerText,document.querySelector(".keywordHeader span").id="psi"+t,getKeywords(t,e)})});let keywordIsBeingCreated=!1;async function save_portfolio_keyword(e){let t=document.querySelector(".keywordModal .inputContainer input").value,o=document.querySelector(".keywordModal .keywordHeader span").id.replace("psi","");if(t.trim().length>2&&!keywordIsBeingCreated){keywordIsBeingCreated=!0;try{let r=await fetch("../../api/portfolio_keywords/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken"),Accept:"application/json","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify({keyword:t,pstock_id:o})});if(r.ok){let l=await r.json(),n=document.createElement("div");n.classList.add("keywordContainer"),n.id=`wkw${l.pkeyword_id}`;let a=document.createElement("span");a.innerText=l.keyword;let i=document.createElement("i");i.addEventListener("click",e=>deleteKeywords(e)),i.classList.add("fas","fa-times"),n.append(a,i),e.closest(".keywordModal").querySelector(".keywordsContainer").appendChild(n),e.closest(".keywordModal").querySelector(".inputContainer input").value="",keywordIsBeingCreated=!1,showMessage("Keyword has been added!","Success"),document.querySelectorAll("table tr").forEach(e=>{e.id==`pstock${o}`&&(e.querySelector("td .keywordButton").innerText=parseInt(e.querySelector("td .keywordButton").innerText)+1)})}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(s){}}else showMessage("A keyword must have at least 3 letters!","Error")}document.querySelectorAll(".keywordModal .addButton").forEach(e=>{e.addEventListener("click",e=>{save_portfolio_keyword(e.target)})}),document.querySelectorAll(".keywordModal .createKeywordsContainer input").forEach(e=>e.addEventListener("keypress",function(t){"Enter"===t.key&&save_portfolio_keyword(e)})),document.querySelector(".portfolioMenuWrapper .keywordModal .keywordHeader .fa-times").addEventListener("click",()=>{removeModalStyle(),document.querySelector(".portfolioMenuWrapper").style.display="none",document.querySelector(".portfolioMenuWrapper .keywordModal").style.display="none"}),document.querySelector(".portfolioMenuWrapper .keywordModal .createKeywordsContainer .infoLink i").addEventListener("click",e=>{e.target.closest(".keywordModal").style.display="none",document.querySelector(".fullScreenPlaceholder").style.display="flex",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="block",document.querySelector(".fullScreenPlaceholder .explanationContainer h3").innerText="Keywords",document.querySelector(".fullScreenPlaceholder .explanationContainer .explanation").innerText="FinBrowser finds content related to the stocks in your portfolio based on their ticker symbol and company name. If you want to see content that focuses on a specific product or segment within a company, you can enter a keyword here and the results for that keyword will be displayed as well. For instance, let's say you hold Amazon stock and you want to see more information about their cloud computing platform, AWS. Simply enter AWS as your keyword and you'll get all the relevant results. It's that easy!";let t=document.querySelector(".fullScreenPlaceholder .fullScreenWrapper .explanationContainer .fa-times");t.addEventListener("click",()=>{e.target.closest(".keywordModal").style.display="block",document.querySelector(".fullScreenPlaceholder").style.display="none",document.querySelector(".fullScreenPlaceholder .explanationContainer").style.display="none"},{once:!0})});