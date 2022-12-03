console.log("nav.js loaded!")

// Add click listener to each nav link
$(".nav-link").click(function() {
    // Remove active class from all links
    $(".nav-link").removeClass("active");
    // Add active class to the clicked link
    $(this).addClass("active");
});
