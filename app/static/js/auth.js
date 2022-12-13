// Check user's login state
function checkLoginState() {
    // Send AJAX request to /auth_check route
    $.ajax({
        url: '/auth-check',
        type: 'GET',
        success: function (response) {
            // Check if user logged in
            if (response === "Not logged in") {
                // User not logged in, show login card, hide user profile card & new post card
                $('.not-auth-required').show();
                $('.auth-required').hide();

            } else {
                // User logged in, hide login card, show user profile card & new post card
                $('.auth-required').show();
                $('.not-auth-required').hide();
            }
        }
    });
}

// Check login state when page loaded
$(document).ready(checkLoginState);
