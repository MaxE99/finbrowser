async function createRecommendedContent(){try{let e=document.querySelectorAll(".pageWrapper .longFormContentContainer .recommendedContentContainer .smallFormContentWrapper .articleContainer").length,t=await fetch(`../../api/articles/?feed_content=${e}`,getFetchSettings("GET"));if(t.ok){let a=await t.json();a.forEach(e=>addNewContentToContainer(e)),document.querySelector(".recommendedContentContainer .loader").remove(),isContentLoading=!1}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(n){showMessage("Error: Unexpected error has occurred!","Error")}}async function createStockPitches(){try{let e=document.querySelectorAll(".pageWrapper .tweetsContainer .smallFormContentWrapper .articleContainer").length,t=await fetch(`../../api/articles/?stock_pitches=${e}`,getFetchSettings("GET"));if(t.ok){let a=await t.json();a.forEach(e=>addNewContentToContainer(e,!0)),document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper .loader").remove(),isContentLoading=!1}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(n){showMessage("Error: Unexpected error has occurred!","Error")}}function stockPitchesScroll(){if(Math.ceil(STOCK_PITCHES_CONTAINER.scrollTop+STOCK_PITCHES_CONTAINER.clientHeight)>=STOCK_PITCHES_CONTAINER.scrollHeight&&!isContentLoading){let e=document.createElement("div");e.classList.add("loader"),document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper").appendChild(e),createStockPitches(),isContentLoading=!0}}function contentScroll(){let e=document.querySelector(".pageWrapper .longFormContentContainer .activatedTab")?.innerText,t=document.createElement("div");if(t.classList.add("loader"),!isContentLoading){isContentLoading=!0;let a="Stock Pitches"===e?document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper"):document.querySelector(".pageWrapper .longFormContentContainer .recommendedContentContainer");a.appendChild(t),"Stock Pitches"===e?createStockPitches():createRecommendedContent()}}function addNewContentToContainer(e,t=!1){let a=document.createElement("div");a.classList.add("articleContainer"),a.id="cc#"+e.article_id;let n=document.createElement("div");n.classList.add("leftContentSide");let r=document.createElement("div");r.classList.add("profileImageContainer");let l=document.createElement("img");l.src="https://finbrowser.s3.us-east-2.amazonaws.com/static/"+e.source.favicon_path;let o=document.createElement("a");o.classList.add("sourceProfile"),o.href="/source/"+e.source.slug,r.append(l,o),n.appendChild(r),a.appendChild(n);let i=document.createElement("div");i.classList.add("rightContentSide");let s=document.createElement("div");s.classList.add("contentInfoContainer");let c=document.createElement("div");c.classList.add("sourceAndWebsiteContainer");let d=document.createElement("a");d.classList.add("sourceProfile"),d.href="/source/"+e.source.slug,d.innerText=e.source.name;let p=document.createElement("div");p.classList.add("sourceWebsiteProfileContainer");let C=document.createElement("img");C.src="https://finbrowser.s3.us-east-2.amazonaws.com/static/"+e.source.website.logo;let m=document.createElement("a");m.href=e.source.url,p.append(C,m),c.append(d,p),s.appendChild(c);let h=document.createElement("i");h.classList.add("fas","fa-ellipsis-h"),document.querySelector(".articleContainer .fa-ellipsis-h").classList.contains("openAuthPrompt")&&(h.classList.add("openAuthPrompt","ap6"),h.addEventListener("click",()=>openAuthPrompt(h))),h.addEventListener("click",e=>openContentOptionsMenu(e,h));let E=document.createElement("div");E.classList.add("articleOptionsContainer");let u=document.createElement("div");u.classList.add("addToListButton");let L=document.createElement("i");L.classList.add("fas","fa-list");let g=document.createElement("span");g.innerText="Add to list",u.append(L,g),u.addEventListener("click",e=>openAddArticleToListMenu(e));let f=document.createElement("div");f.classList.add("addToHighlightedButton");let T=document.createElement("i");T.classList.add("fas","fa-highlighter");let S=document.createElement("span");e.is_highlighted?S.innerText="Unhighlight Article":S.innerText="Highlight article",f.append(T,S),f.addEventListener("click",()=>changeHighlightedStatus(f)),E.append(u,f),s.append(h,E);let y=document.createElement("div");y.classList.add("contentBody"),y.id="cc#"+e.article_id;let w=document.createElement("p");w.innerText=e.title,y.appendChild(w);let v=document.createElement("div");v.classList.add("timeContainer");let P=document.createElement("p");P.innerText=e.pub_date,v.appendChild(P);let k=document.createElement("div");k.classList.add("tooltipContainer");let W=document.createElement("i");W.classList.add("fa-solid","fa-lock");let x=document.createElement("span");x.classList.add("tooltiptext"),"No"===e.source.paywall?(W.classList.add("noPaywall"),x.innerText="No Paywall",k.classList.add("noPaywallTooltip")):"Semi"===e.source.paywall?(W.classList.add("semiPaywall"),x.innerText="Some Paywall",k.classList.add("semiPaywallTooltip")):(W.classList.add("yesPaywall"),x.innerText="Paywall",k.classList.add("yesPaywallTooltip")),k.appendChild(W),k.appendChild(x),v.appendChild(k);let N=document.createElement("a");N.classList.add("contentLink"),N.href=e.link,N.target="_blank",i.append(s,y,N),i.appendChild(v),a.appendChild(i);let q=t?document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper"):document.querySelector(".pageWrapper .longFormContentContainer .recommendedContentContainer .smallFormContentWrapper");q.appendChild(a)}function observeDOM(){let e=new IntersectionObserver(e=>{e[0].isIntersecting&&contentScroll()},{threshold:0,rootMargin:"0px 0px 30px 0px"});e.observe(document.querySelector("footer"))}let isContentLoading=!1;const STOCK_PITCHES_CONTAINER=document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper");document.addEventListener("DOMContentLoaded",observeDOM),STOCK_PITCHES_CONTAINER.addEventListener("scroll",stockPitchesScroll);
