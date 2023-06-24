let contentIsLoading=!1;function addNewContentToContainer(e,t=!1){let a=document.createElement("div");a.classList.add("articleContainer"),a.id="cc#"+e.article_id;let n=document.createElement("div");n.classList.add("leftContentSide");let l=document.createElement("div");l.classList.add("profileImageContainer");let r=document.createElement("img");r.src="https://finbrowser.s3.us-east-2.amazonaws.com/static/"+e.source.favicon_path;let o=document.createElement("a");o.classList.add("sourceProfile"),o.href="/source/"+e.source.slug,l.append(r,o),n.appendChild(l),a.appendChild(n);let i=document.createElement("div");i.classList.add("rightContentSide");let s=document.createElement("div");s.classList.add("contentInfoContainer");let c=document.createElement("div");c.classList.add("sourceAndWebsiteContainer");let d=document.createElement("a");d.classList.add("sourceProfile"),d.href="/source/"+e.source.slug,d.innerText=e.source.name;let p=document.createElement("div");p.classList.add("sourceWebsiteProfileContainer");let m=document.createElement("img");m.src="https://finbrowser.s3.us-east-2.amazonaws.com/static/"+e.source.website.logo;let C=document.createElement("a");C.href=e.source.url,p.append(m,C),c.append(d,p),s.appendChild(c);let h=document.createElement("i");h.classList.add("fas","fa-ellipsis-h"),document.querySelector(".articleContainer .fa-ellipsis-h").classList.contains("openAuthPrompt")&&(h.classList.add("openAuthPrompt","ap6"),h.addEventListener("click",()=>{openAuthPrompt(h)})),h.addEventListener("click",e=>{openContentOptionsMenu(e,h)});let u=document.createElement("div");u.classList.add("articleOptionsContainer");let L=document.createElement("div");L.classList.add("addToListButton");let g=document.createElement("i");g.classList.add("fas","fa-list");let E=document.createElement("span");E.innerText="Add to list",L.append(g,E),L.addEventListener("click",e=>{openAddToListMenu(e)});let f=document.createElement("div");f.classList.add("addToHighlightedButton");let w=document.createElement("i");w.classList.add("fas","fa-highlighter");let y=document.createElement("span");e.is_highlighted?y.innerText="Unhighlight Article":y.innerText="Highlight article",f.append(w,y),f.addEventListener("click",()=>{highlightContent(f)}),u.append(L,f),s.append(h,u);let T=document.createElement("div");T.classList.add("contentBody"),T.id="cc#"+e.article_id;let v=document.createElement("p");v.innerText=e.title,T.appendChild(v);let S=document.createElement("div");S.classList.add("timeContainer");let W=document.createElement("p");W.innerText=e.pub_date,S.appendChild(W);let P=document.createElement("div");P.classList.add("tooltipContainer");let k=document.createElement("i");k.classList.add("fa-solid","fa-lock");let x=document.createElement("span");x.classList.add("tooltiptext"),"No"===e.source.paywall?(k.classList.add("noPaywall"),x.innerText="No Paywall",P.classList.add("noPaywallTooltip")):"Semi"===e.source.paywall?(k.classList.add("semiPaywall"),x.innerText="Some Paywall",P.classList.add("semiPaywallTooltip")):(k.classList.add("yesPaywall"),x.innerText="Paywall",P.classList.add("yesPaywallTooltip")),P.appendChild(k),P.appendChild(x),S.appendChild(P),(contentLink=document.createElement("a")).classList.add("contentLink"),contentLink.href=e.link,contentLink.target="_blank",i.append(s,T,contentLink),i.appendChild(S),a.appendChild(i),t?document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper").appendChild(a):document.querySelector(".pageWrapper .longFormContentContainer .recommendedContentContainer .smallFormContentWrapper").appendChild(a)}const scrollableContentContainer=document.querySelector(".pageWrapper .recommendedContentContainer .smallFormContentWrapper"),scrollableTweetContainer=document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper");async function createContent(){try{let e=document.querySelectorAll(".pageWrapper .longFormContentContainer .recommendedContentContainer .smallFormContentWrapper .articleContainer").length,t=await fetch(`../../api/articles/?feed_content=${e}`,get_fetch_settings("GET"));if(t.ok){let a=await t.json();a.forEach(e=>{addNewContentToContainer(e)}),document.querySelector(".recommendedContentContainer .loader").remove(),contentIsLoading=!1}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(n){}}async function createStockPitches(){try{let e=document.querySelectorAll(".pageWrapper .tweetsContainer .smallFormContentWrapper .articleContainer").length,t=await fetch(`../../api/articles/?stock_pitches=${e}`,get_fetch_settings("GET"));if(t.ok){let a=await t.json();a.forEach(e=>{addNewContentToContainer(e,!0)}),document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper .loader").remove(),contentIsLoading=!1}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(n){}}function stockPitchesScroll(){if(Math.ceil(scrollableTweetContainer.scrollTop+scrollableTweetContainer.clientHeight)>=scrollableTweetContainer.scrollHeight&&!contentIsLoading){let e=document.createElement("div");e.classList.add("loader"),document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper").appendChild(e),createStockPitches(),contentIsLoading=!0}}function contentScroll(){let e=document.querySelector(".pageWrapper .longFormContentContainer .activatedTab")?.innerText,t=document.createElement("div");t.classList.add("loader"),contentIsLoading||("Stock Pitches"===e?(contentIsLoading=!0,document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper").appendChild(t),createStockPitches()):(contentIsLoading=!0,document.querySelector(".pageWrapper .longFormContentContainer .recommendedContentContainer").appendChild(t),createContent()))}document.addEventListener("DOMContentLoaded",function(){let e=document.querySelector("footer"),t=new IntersectionObserver(function(e){e[0].isIntersecting&&contentScroll()},{threshold:0,rootMargin:"0px 0px 30px 0px"});t.observe(e)}),scrollableTweetContainer.addEventListener("scroll",function(){stockPitchesScroll()});
