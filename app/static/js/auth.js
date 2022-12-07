// Check user's login state
function checkLoginState() {
  // Send AJAX request to /auth_check route
  $.ajax({
    url: '/auth_check',
    type: 'GET',
    success: function(response) {
      // Check if user logged in
      if (response === "Not logged in") {
        // User not logged in, show login card, hide user profile card & new post card
        $('#login-card').show();
        $('#profile-card').hide();
        $('#new-post-card').hide();


      } else {
        // User logged in, hide login card, show user profile card & new post card
        $('#login-card').hide();
        $('#profile-card').show();
        $('#new-post-card').show();
      }
    }
  });
}

// Check login state when page loaded
$(document).ready(checkLoginState);
