(function ($) {

    //Preloader
    $(function () {
        setTimeout(function () {
            $('#preloader').fadeOut('slow', function () {
                $(this).remove();
            });
        }, 1500);
    });

})(jQuery);