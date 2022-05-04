var firebaseConfig = {
   apiKey: "AIzaSyAPwdK0M1VOfbU-220fNi059EMC6xDXKxk",
   authDomain: "coffee-card-website.firebaseapp.com",
   databaseURL: "https://coffee-card-website.firebaseio.com",
   projectId: "coffee-card-website",
   storageBucket: "coffee-card-website.appspot.com",
 };

// Initialize your Firebase app
firebase.initializeApp(firebaseConfig);

// Reference to your entire Firebase database
var myFirebase = firebase.database().ref();

// Get a reference to the recommendations object of your Firebase.
// Note: this doesn't exist yet. But when we write to our Firebase using
// this reference, it will create this object for us!
var messages = myFirebase.child("messages");

// Push our first recommendation to the end of the list and assign it a
// unique ID automatically.
var submitRecommendation = function () {

  // Get input values from each of the form elements
  var title = $("#message").val();

  // Push a new recommendation to the database using those values
  messages.push({
    "message": title
  });
};

$(window).load(function () {

  // Find the HTML element with the id recommendationForm, and when the submit
  // event is triggered on that element, call submitRecommendation.
  $("#message_form").submit(submitRecommendation);

});
