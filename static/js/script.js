$(document).ready(function () {

         /*Start Input Image*/
     // ADD IMAGE
     $('.image-uploader').change(function (event) {
         $(this).parents('.images-upload-block').append('<div class="uploaded-block"><img src="' + URL.createObjectURL(event.target.files[0]) + '"><button class="close">&times;</button></div>');
     });

     // REMOVE IMAGE
     $('.images-upload-block').on('click', '.close', function () {
         $(this).parents('.uploaded-block').remove();
     });
     /*End Input Image*/

    /// loading website

    jQuery(window).load(function () {
        $(".loader").fadeOut(500, function () {
            $(".loading").fadeOut(500);
//            $(".loading img").slideUp(1000);
            $("body").css("overflow-y", "auto");
        });
    });

    /* Start Smooth Scroll */
        $('.navbar a').click(function (e) {
            $('html, body').animate({scrollTop: $($(this).attr('href')).offset().top}, 1000);
            e.preventDefault();
        });
    /* End Smooth Scroll */
            
    /// navbar button
	$('#nav-icon1').click(function(){
		$(this).toggleClass('open');
        $(".navy").toggleClass("back");
        $(".body-overlay").toggleClass("back");
        $("body").toggleClass("body-over");
        });
        
          $(".body-overlay").click(function(){
            $(this).toggleClass("back");
            $('#nav-icon1').toggleClass('open');
            $(".navy").toggleClass("back");
            $("body").toggleClass("body-over");
        });

            
    
    //////////////////////////////
    'use strict';

    var scrollButton,
        i,
        atr;

    scrollButton = $("#scroll-top");

    $(window).scroll(function () {
        if ($(this).scrollTop() >= 500) {
            scrollButton.show();
        } else {
            scrollButton.hide();
        }
    });


    $("#scroll-top").click(function () {
        $("html,body").animate({
            scrollTop: 0
        }, 600);
    });


        $(function () {
        $('.bookmarks .test li').on('click', function () {
            $(this).parent().find('li.active').removeClass('active');
            $(this).addClass('active');
        });
    });

});


