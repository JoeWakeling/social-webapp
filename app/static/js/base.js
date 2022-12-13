console.log("base.js loaded!")

// Add click listener to each nav link
$(".nav-link").click(function () {
    // Remove active class from all links
    $(".nav-link").removeClass("active");
    // Add active class to the clicked link
    $(this).addClass("active");
});

// Function to help resize post input window as it overflows
function setHeight(element) {
    let postInputBox = $('#' + element);
    postInputBox.css('height', '5px');
    postInputBox.css('height', postInputBox.prop('scrollHeight') + 'px');
}

// Function to replace pfp with fallback if one doesnt exist
$('.profile-img').on('error', function () {
    $(this).attr('src', '/static/images/default-profile-img.jpg');
});
