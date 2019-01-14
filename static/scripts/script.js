jQuery(document).ready(function($) {
  $.noConflict();

  $(".blog-card").click(function() {
    if ($("#postID").length) {
      var postID = $(this)
        .children("span")
        .first()
        .html();

      if (postID !== undefined) {
        window.location = "/posts/" + postID;
      }
    }
  });
});
