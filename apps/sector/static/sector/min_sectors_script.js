if(sessionStorage.getItem("listSearchSettings")){let a=JSON.parse(sessionStorage.getItem("listSearchSettings"));document.getElementById("paywall").value=a[0],document.getElementById("type").value=a[1],document.getElementById("minimum_rating").value=a[2],document.getElementById("website").value=a[3],sessionStorage.removeItem("listSearchSettings")}document.querySelector(".searchButton").addEventListener("click",async()=>{let a=document.getElementById("paywall"),b=a.options[a.selectedIndex].value,c=document.getElementById("type"),d=c.options[c.selectedIndex].value,e=document.getElementById("minimum_rating"),f=e.options[e.selectedIndex].value,g=document.getElementById("website"),h=g.options[g.selectedIndex].value,i=[b,d,f,h];sessionStorage.setItem("listSearchSettings",JSON.stringify(i)),window.location=`../../../../../../sectors/${b}/${d}/${f}/${h}/`}),document.querySelector(".filterButton").addEventListener("click",()=>{let a=document.querySelector(".filterBarMenu");"flex"==a.style.display?a.style.display="none":a.style.display="flex"}),document.getElementById("search").addEventListener("keyup",async function(e){let a=document.getElementById("search").value;if("Enter"==e.key&&""!=a.replaceAll(/\s/g,""))window.location.href=`../../../../../../search_results/${a}`;else{let b=document.getElementById("autocomplete_list_results");if(a&&""!=a.replaceAll(/\s/g,"")){try{let c=await fetch(`../../../../../../api/sources/?sectors_search=${a}`,get_fetch_settings("GET"));if(c.ok){let d=await c.json();b.style.display="flex",b.innerHTML="",d.length>0&&d.forEach(a=>{let c=`<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${a.favicon_path}"><span>${a.name}</span><a href="../../source/${a.slug}"></a></div>`;b.innerHTML+=c})}else showMessage("Error: Network request failed unexpectedly!!","Error")}catch(f){console.log(f)}document.onclick=function(a){"autocomplete_list_results"!==a.target.id&&(b.style.display="none")}}else b.style.display="none"}}),document.querySelector(".searchSelectContainer i").addEventListener("click",()=>{console.log("clicked"),""!=(search_term=document.getElementById("search").value).replaceAll(/\s/g,"")&&(window.location.href=`../../../../../../search_results/${search_term}`)})