let contentIsLoading=!1;function createTwitterPart(e,t){if("Retweet"===e.tweet_type.type){let a=document.createElement("div");a.className="retweetWrapper";let n=document.createElement("span");n.textContent=`@${e.tweet_type.author}`,a.appendChild(document.createTextNode("Retweeted post by ")),a.appendChild(n),t.appendChild(a)}if("Reply"===e.tweet_type.type){let r=document.createElement("div");r.className="replyWrapper";let l=document.createElement("span");l.textContent=`@${e.tweet_type.author}`,r.appendChild(document.createTextNode("Replying to ")),r.appendChild(l),t.appendChild(r)}if(e.tweet_type.image_path){let i=document.createElement("img");i.className="tweetImage",i.setAttribute("src","https://finbrowser.s3.us-east-2.amazonaws.com/static/"+e.tweet_type.image_path),i.setAttribute("alt","Tweet Image"),t.appendChild(i)}if("Quote"===e.tweet_type.type||"Retweet"===e.tweet_type.type||"Reply"===e.tweet_type.type){let o=document.createElement("div");o.className="quoteWrapper";let s=document.createElement("div");s.className="quoteUpperContainer";let c=document.createElement("div");c.className="quoteAuthor",c.textContent=e.tweet_type.author,s.appendChild(c),o.appendChild(s);let d=document.createElement("div");if(d.className="quoteText",d.textContent=e.tweet_type.text,o.appendChild(d),e.tweet_type.initial_tweet_img_path){let p=document.createElement("img");p.className="tweetImage",p.setAttribute("src","https://finbrowser.s3.us-east-2.amazonaws.com/static/"+e.tweet_type.initial_tweet_img_path),p.setAttribute("alt","Tweet Reply Image"),o.appendChild(p)}t.appendChild(o),t.appendChild(contentLink)}}function addNewContentToContainer(e,t=!1){let a=document.createElement("div");a.classList.add("articleContainer"),a.id="cc#"+e.article_id;let n=document.createElement("div");n.classList.add("leftContentSide");let r=document.createElement("div");r.classList.add("profileImageContainer");let l=document.createElement("img");l.src="https://finbrowser.s3.us-east-2.amazonaws.com/static/"+e.source.favicon_path;let i=document.createElement("a");i.classList.add("sourceProfile"),i.href="/source/"+e.source.slug,r.append(l,i),n.appendChild(r),a.appendChild(n);let o=document.createElement("div");o.classList.add("rightContentSide");let s=document.createElement("div");s.classList.add("contentInfoContainer");let c=document.createElement("div");c.classList.add("sourceAndWebsiteContainer");let d=document.createElement("a");d.classList.add("sourceProfile"),d.href="/source/"+e.source.slug,d.innerText=e.source.name;let p=document.createElement("div");p.classList.add("sourceWebsiteProfileContainer");let m=document.createElement("img");m.src="https://finbrowser.s3.us-east-2.amazonaws.com/static/"+e.source.website.logo;let C=document.createElement("a");C.href=e.source.url,p.append(m,C),c.append(d,p),s.appendChild(c);let h=document.createElement("i");h.classList.add("fas","fa-ellipsis-h"),document.querySelector(".articleContainer .fa-ellipsis-h").classList.contains("openAuthPrompt")&&(h.classList.add("openAuthPrompt","ap6"),h.addEventListener("click",()=>{openAuthPrompt(h)})),h.addEventListener("click",e=>{openContentOptionsMenu(e,h)});let u=document.createElement("div");u.classList.add("articleOptionsContainer");let w=document.createElement("div");w.classList.add("addToListButton");let g=document.createElement("i");g.classList.add("fas","fa-list");let E=document.createElement("span");E.innerText="Add to list",w.append(g,E),w.addEventListener("click",e=>{openAddToListMenu(e)});let f=document.createElement("div");f.classList.add("addToHighlightedButton");let y=document.createElement("i");y.classList.add("fas","fa-highlighter");let L=document.createElement("span");e.is_highlighted?L.innerText="Unhighlight Article":L.innerText="Highlight article",f.append(y,L),f.addEventListener("click",()=>{highlightContent(f)}),u.append(w,f),s.append(h,u);let T=document.createElement("div");T.classList.add("contentBody"),T.id="cc#"+e.article_id;let v=document.createElement("p");v.innerText=e.title,T.appendChild(v);let W=document.createElement("div");W.classList.add("timeContainer");let b=document.createElement("p");b.innerText=e.pub_date,W.appendChild(b),(contentLink=document.createElement("a")).classList.add("contentLink"),contentLink.href=e.link,o.append(s,T,contentLink),t?(createTwitterPart(e,o),o.appendChild(W),a.appendChild(o),document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper").appendChild(a)):(o.appendChild(W),a.appendChild(o),document.querySelector(".pageWrapper .longFormContentContainer .recommendedContentContainer .smallFormContentWrapper").appendChild(a))}const scrollableContentContainer=document.querySelector(".pageWrapper .recommendedContentContainer .smallFormContentWrapper"),scrollableTweetContainer=document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper");async function createContent(){try{let e=document.querySelectorAll(".pageWrapper .longFormContentContainer .recommendedContentContainer .smallFormContentWrapper .articleContainer").length,t=await fetch(`../../api/articles/?feed_content=${e}`,get_fetch_settings("GET"));if(t.ok){let a=await t.json();a.forEach(e=>{addNewContentToContainer(e)}),document.querySelector(".recommendedContentContainer .loader").remove(),contentIsLoading=!1}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(n){}}async function createTweets(){try{let e=document.querySelectorAll(".pageWrapper .tweetsContainer .smallFormContentWrapper .articleContainer").length,t=await fetch(`../../api/articles/?best_tweets=${e}`,get_fetch_settings("GET"));if(t.ok){let a=await t.json();a.forEach(e=>{addNewContentToContainer(e,!0)}),document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper .loader").remove(),contentIsLoading=!1}else showMessage("Error: Network request failed unexpectedly!","Error")}catch(n){}}function twitterScroll(){if(Math.ceil(scrollableTweetContainer.scrollTop+scrollableTweetContainer.clientHeight)>=scrollableTweetContainer.scrollHeight&&!contentIsLoading){let e=document.createElement("div");e.classList.add("loader"),document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper").appendChild(e),createTweets(),contentIsLoading=!0}}function contentScroll(){let e=document.querySelector(".pageWrapper .longFormContentContainer .activatedTab")?.innerText,t=document.createElement("div");t.classList.add("loader"),contentIsLoading||("Recommended Tweets"===e?(contentIsLoading=!0,document.querySelector(".pageWrapper .tweetsContainer .smallFormContentWrapper").appendChild(t),createTweets()):(contentIsLoading=!0,document.querySelector(".pageWrapper .longFormContentContainer .recommendedContentContainer").appendChild(t),createContent()))}document.addEventListener("DOMContentLoaded",function(){let e=document.querySelector("footer"),t=new IntersectionObserver(function(e){e[0].isIntersecting&&contentScroll()},{threshold:0,rootMargin:"0px 0px 30px 0px"});t.observe(e)}),scrollableTweetContainer.addEventListener("scroll",function(){twitterScroll()});
