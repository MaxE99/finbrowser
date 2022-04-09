const sliderContent = document.querySelector(".slider-content");
const contentArray = sliderContent.children;
var isTouched = false;

var next = function () {
  sliderContent.classList.add("next-animation");
  if (isTouched) {
    sliderContent.style.transform = "translate3d(-200%, 0px, 0px)";
    sliderContent.addEventListener("transitionend", nextTouched, false);
  } else if (!isTouched) {
    sliderContent.style.transform = "translate3d(-100%, 0px, 0px)";

    sliderContent.addEventListener("transitionend", afterAnimation, false);
  }
};

var prev = function () {
  if (isTouched) {
    var content = Array.from(contentArray);
    var getSplice = content.splice(contentArray.length - 3);
    var newArr = getSplice.concat(content);

    var i;
    for (i = 0; i < content.length; i++) {
      content[i].classList.remove("is-active");
    }

    var j;
    for (j = 3; j < newArr.length && j < 6; j++) {
      newArr[j].classList.add("is-active");
    }

    var len;
    for (len = contentArray.length - 1; len >= 0; --len) {
      sliderContent.insertBefore(newArr[len], sliderContent.firstChild);
    }

    sliderContent.style.transform = "translate3d(-200%, 0px, 0px)";

    setTimeout(function () {
      sliderContent.classList.add("next-animation");
      sliderContent.style.transform = "translate3d(-100%, 0px, 0px)";
      sliderContent.addEventListener("transitionend", afterAnimation, false);
    });
  }
};

var afterAnimation = function () {
  sliderContent.classList.remove("next-animation");

  if (!isTouched) {
    var icon = document.createElement("i");
    icon.classList.add("fa", "fa-chevron-left");
    document.querySelector(".prev").appendChild(icon);
    isTouched = true;
  }

  sliderContent.removeEventListener("transitionend", afterAnimation);
};

var nextTouched = function () {
  var content = Array.from(contentArray);
  var getSplice = content.splice(0, 3);
  var newArr = content.concat(getSplice);

  var i;
  for (i = 0; i < content.length; i++) {
    content[i].classList.remove("is-active");
  }

  var j;
  for (j = 3; j < newArr.length && j < 6; j++) {
    newArr[j].classList.add("is-active");
  }

  var len;
  for (len = contentArray.length - 1; len >= 0; --len) {
    sliderContent.insertBefore(newArr[len], sliderContent.firstChild);
  }

  sliderContent.classList.remove("next-animation");
  sliderContent.style.transform = "translate3d(-100%, 0px, 0px)";
  sliderContent.removeEventListener("transitionend", nextTouched);
};
