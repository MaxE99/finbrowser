if(sessionStorage.getItem("listSearchSettings")){let a=JSON.parse(sessionStorage.getItem("listSearchSettings"));document.getElementById("timeframe").value=a[0],document.getElementById("content").value=a[1],document.getElementById("minimum_rating").value=a[2],document.getElementById("primary_source").value=a[3],sessionStorage.removeItem("listSearchSettings")}document.querySelector(".searchButton").addEventListener("click",async()=>{let a=document.getElementById("timeframe"),b=a.options[a.selectedIndex].value,c=document.getElementById("content"),d=c.options[c.selectedIndex].value,e=document.getElementById("minimum_rating"),f=e.options[e.selectedIndex].value,g=document.getElementById("primary_source"),h=g.options[g.selectedIndex].value,i=[b,d,f,h,];sessionStorage.setItem("listSearchSettings",JSON.stringify(i)),window.location=`../../../../../../lists/${b}/${d}/${f}/${h}/`});const createListButton=document.querySelector(".createListButton");createListButton.addEventListener("click",()=>{createListButton.classList.contains("registrationLink")||(document.querySelector(".searchResultsAndListCreationContainer .createListMenu").style.display="flex")}),document.querySelector(".filterButton").addEventListener("click",()=>{let a=document.querySelector(".filterBarMenu");"flex"==a.style.display?a.style.display="none":a.style.display="flex"}),document.getElementById("search").addEventListener("keyup",async function(g){let c=document.getElementById("search").value;if("Enter"==g.key&&""!=c.replaceAll(/\s/g,""))window.location.href=`../../../../../../search_results/${c}`;else{let d=document.getElementById("autocomplete_list_results");if(c&&""!=c.replaceAll(/\s/g,"")){try{let e=await fetch(`../../../../../../api/search_lists/${c}`,get_fetch_settings("GET"));if(e.ok){let a=await e.json();if(d.style.display="flex",d.innerHTML="",a[0].length>0)for(let b=0,h=a[0].length;b<h;b++){let f="https://finbrowser.s3.us-east-2.amazonaws.com/static/home/media/finbrowser-bigger-logo.png";a[0][b].list_pic&&(f=a[0][b].list_pic);let i=`<div class="searchResult"><img src="${f}"><span>${a[0][b].name}</span><a href="../../../../../..${a[1][b]}"></a></div>`;d.innerHTML+=i}}else showMessage("Error: Network request failed unexpectedly!!","Error")}catch(j){}document.onclick=function(a){"autocomplete_list_results"!==a.target.id&&(d.style.display="none")}}else d.style.display="none"}}),document.querySelector(".searchSelectContainer i").addEventListener("click",()=>{""!=(search_term=document.getElementById("search").value).replaceAll(/\s/g,"")&&(window.location.href=`../../../../../../search_results/${search_term}`)})