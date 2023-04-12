const wittyString =
  "Stay street smart with CrimeScope! Quick access to crime data and safety tips to help you travel confidently.";

const seriousString =
  "Stay safe with ease. CrimeScope presents you with real-time crime data and tailored safety tips to help you navigate your city with confidence.";

const catchyString =
  "Stay safe, stay sharp, stay smart! CrimeScope helps you make informed decisions about your safety with just a tap.";

const funnyString =
  "Be smarter than the criminals (or at least pretend to be)! CrimeScope gives you the lowdown on crime hotspots and safety tips.";

const newToCityString =
  "New to a city? CrimeScope is provides crime data and safety tips to keep you protected.";

const slides = [
  wittyString,
  seriousString,
  catchyString,
  funnyString,
  newToCityString,
];

let currentSlide = 0;

function showNextSlide() {
  $("#phrase-container").fadeOut(500, function () {
    $(this).text(slides[currentSlide]).fadeIn(500);
    currentSlide = (currentSlide + 1) % slides.length;
  });
}

$("#phrase-container").text(slides[0]);

setInterval(showNextSlide, 5000);
