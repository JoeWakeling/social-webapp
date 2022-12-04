// Check user's login state
function checkLoginState() {
  // Send AJAX request to /auth_check route
  $.ajax({
    url: '/auth_check',
    type: 'GET',
    success: function(response) {
      // Check if user logged in
      if (response === "Not logged in") {
        // User not logged in, show login card and hide user profile card
        $('#login-card').show();
        $('#profile-card').hide();

      } else {
        // User logged in, hide login card and show user profile card
        $('#login-card').hide();
        $('#profile-card').show();

      }
    }
  });
}

// Check login state when page loaded
$(document).ready(checkLoginState);
