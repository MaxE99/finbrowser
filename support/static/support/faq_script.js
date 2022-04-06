$(document).ready(function(){
    $('.questionBarTab').on('click',function(e){
        $current = $(this);
        tabs = document.querySelectorAll('.questionBarTab');
        tabsData = document.querySelectorAll('.tabsContent');
        tabNumber = $current[0].dataset.forTab;
        for(let i=0, j=tabs.length; i<j; i++){
            tabs[i].classList.remove('questionBarTabActive')
            tabsData[i].classList.remove('tabsContentActive');
        }
        tabs[tabNumber-1].classList.add('questionBarTabActive');
        tabsData[tabNumber-1].classList.add('tabsContentActive');

    })
})

// Open Button
$(document).ready(function(){
    $('.collapsibleCategory').on('click', function(e){
        e.stopImmediatePropagation();
        $current = $(this);
        const collapsibleText = $current.next()[0];
        if (collapsibleText.style.maxHeight){
            collapsibleText.style.maxHeight = null;
            collapsibleText.style.margin = '0px auto 0px 15px';
            let plusSign = $current.find('.fa-minus')[0];
            plusSign.classList.add('fa-plus');
            plusSign.classList.remove('fa-minus');
            } 
        else {
            collapsibleText.style.maxHeight = "1800px";
            collapsibleText.style.margin = '10px auto 10px 15px';
            let plusSign = $current.find('.fa-plus')[0];
            plusSign.classList.add('fa-minus');
            plusSign.classList.remove('fa-plus');
        }
    });
}); 
        
