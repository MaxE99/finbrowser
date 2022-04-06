const resetButton = document.querySelector('.resetButton');
resetButton.addEventListener('click', ()=>{
    const reportForm = document.querySelector('.suggestionForm');
    reportForm.reset();
    submitButton.disabled = true;
})


const suggestionType = document.querySelector('.suggestionType');
const suggestionExplanation = document.querySelector('#suggestionExplanation'); 
const submitButton = document.querySelector('#submitbutton');
const categorySelected = document.querySelector('.multiselectBlock');

categorySelected.addEventListener('click', ()=>{
    checkValidationForm();
})

suggestionType.addEventListener('keyup', ()=>{
    checkValidationForm();
})

suggestionExplanation.addEventListener('keyup', ()=>{
    checkValidationForm();
})

function checkValidationForm() {
    if(suggestionType.value != "" && suggestionExplanation.value !="" && categorySelected.value !="") { 
        submitButton.disabled = false;
    } 
    else { 
        submitButton.disabled = true;
    }
}