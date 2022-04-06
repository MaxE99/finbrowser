const resetButton = document.querySelector('.resetButton');
resetButton.addEventListener('click', ()=>{
    const reportForm = document.querySelector('.reportBugForm');
    reportForm.reset();
    submitButton.disabled = true;
})


const reportType = document.querySelector('.reportTopic');
const reportExplanation = document.querySelector('#reportExplanation'); 
const submitButton = document.querySelector('#submitbutton');
const categorySelected = document.querySelector('.multiselectBlock');

categorySelected.addEventListener('click', ()=>{
    checkValidationForm();
})

reportType.addEventListener('keyup', ()=>{
    checkValidationForm();
})

reportExplanation.addEventListener('keyup', ()=>{
    checkValidationForm();
})

function checkValidationForm() {
    if(reportType.value != "" && reportExplanation.value !="" && categorySelected.value !="") { 
        submitButton.disabled = false;
    } 
    else { 
        submitButton.disabled = true;
    }
}