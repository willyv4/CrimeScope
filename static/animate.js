const wittyString =
  "Stay safe with CrimeScope! Quick access to crime data and safety tips to keep you aware.";

const seriousString =
  "Travel confidently. CrimeScope presents tailored safety tips to help you navigate cities with confidence.";

const newToCityString =
  "New to a city? CrimeScope provides crime data and safety tips to make you feel at home.";

const slides = [wittyString, seriousString, newToCityString];

let currentSlide = 0;

function showNextSlide() {
  $("#phrase-container-login-signup").fadeOut(500, function () {
    $(this).text(slides[currentSlide]).fadeIn(500);
    currentSlide = (currentSlide + 1) % slides.length;
  });
}

$("#phrase-container-login-signup").text(slides[1]);

setInterval(showNextSlide, 6000);
