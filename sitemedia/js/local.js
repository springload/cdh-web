$(document).ready(function () {
    var $ribbon = $('.ribbon');
    if ($ribbon) {
        var faded = sessionStorage.getItem('fade-test-banner', true);
        if (!faded) {
            $('.ribbon-box').removeClass('fade');
        }
        $ribbon.on('click', function () {
            $('.ribbon-box').addClass('fade');
            sessionStorage.setItem('fade-test-banner', true);
        });
    }

    var scroll = 0;
    /*
      Check every time the window scrolls. If it's by 25px or more and
      the scroll is below 90px, hide the navi. If the scroll down isn't
      those, leave it as is.
      If the scroll is up by 5 px, bring the menu back.
    */
    $(window).scroll(function () {
        scrolled = $(document).scrollTop();
        if (scrolled - scroll > 25 && scrolled > scroll && scrolled >
            90) {
            $('header').addClass('hidden');
            hideCards()
        }
        else if (scrolled > scroll) {
            // Do nothing since the scroll was either
            // too high or not 'enough'
        }
        else if (scrolled < scroll && scroll - scrolled > 5) {
            $('header').removeClass('hidden');
        }

        scroll = scrolled;

    });


    $('.menu-toggle').on('click', function (e) {
        e.preventDefault();
        // toggle footer to act as main mobile nav
        $('footer').toggleClass('mobile-nav');
        $('body').toggleClass('fixed');
        // swap hamburger icon with close icon
        $(e.target).toggleClass('fa-bars').toggleClass('fa-times')
    });
    $('a.toggle').on('click', function (e) {
        $(this).parent().toggleClass('open');
        $(this).parent().find('.submenu').toggle();
    });


    /*
     * Main navigation
     */

    // keybindings for primary nav
    // see https://www.w3.org/TR/wai-aria-practices-1.1/examples/menubar/menubar-1/menubar-1.html
    $('.primary-nav > li > a')
        .keydown(function (e) {
            switch (e.which) {
                case 35: { // home
                    hideCard(e.target.id)
                    var firstCard = $('.primary-nav > li > a').first()
                    firstCard.focus()
                    break
                }
                case 36: { // end
                    hideCard(e.target.id)
                    var lastCard = $('.primary-nav > li > a').last()
                    lastCard.focus()
                    break
                }
                case 37: { // left arrow
                    hideCard(e.target.id)
                    var prevCard = $(e.target).parent().prev('li').find('a')
                    prevCard.focus()
                    break
                }
                case 38: { // up arrow
                    e.preventDefault()
                    showCard(e.target.id)
                    var lastLink = $('#' + e.target.id + '-secondary > li > a').last()
                    lastLink.focus()
                    break
                }
                case 39: { // right arrow
                    hideCard(e.target.id)
                    var nextCard = $(e.target).parent().next('li').find('a')
                    nextCard.focus()
                    break
                }
                case 40: { // down arrow
                    e.preventDefault()
                    showCard(e.target.id)
                    var firstLink = $('#' + e.target.id + '-secondary > li > a').first()
                    firstLink.focus()
                    break
                }
                case 13: // enter
                case 32: { // spacebar
                    $(e.target).click()
                    break
                }
            }
        })

    // keybindings for secondary nav (cards)
    // see https://www.w3.org/TR/wai-aria-practices-1.1/examples/menubar/menubar-1/menubar-1.html
    $('.secondary-nav > li > a')
        .keydown(function (e) {
            switch (e.which) {
                case 27: { // escape
                    var parentMenu = $(e.target).parents('.secondary-nav').get()[0]
                    var parentMenuName = parentMenu.id.split('-secondary')[0]
                    hideCard(parentMenuName)
                    $('#' + parentMenuName).focus()
                }
                case 35: { // home
                    var firstLink = $(e.target).parent().first('li').find('a')
                    firstLink.focus()
                    break
                }
                case 36: { // end
                    var lastLink = $(e.target).parent().last('li').find('a')
                    lastLink.focus()
                    break
                }
                case 37: { // left arrow
                    var prevLink = $(e.target).parent().prev('li').find('a')
                    prevLink.focus()
                    break
                }
                case 38: { // up arrow
                    e.preventDefault()
                    break
                }
                case 39: { // right arrow
                    var nextLink = $(e.target).parent().next('li').find('a')
                    nextLink.focus()
                    break
                }
                case 40: { // down arrow
                    e.preventDefault()
                    break
                }
                case 13: // enter
                case 32: { // spacebar
                    $(e.target).click()
                    break
                }
            }
        })

    // show nav card on mouseover for main menu entry
    $('.primary-nav a')
        .mouseenter(function (e) { showCard(e.target.id) })

    // hide all nav cards when we leave the nav
    $('.nav-wrap')
        .mouseleave(function () { hideCards() })

    function hideCard(id) {
        $('.nav-card.menu-' + id).hide()
        $('#' + id).attr('aria-expanded', false)
    }

    function showCard(id) {
        hideCards() // hide others
        $('.nav-card.menu-' + id).show()
        $('#' + id).attr('aria-expanded', true)
    }

    function hideCards() {
        $('.primary-nav a').attr('aria-expanded', false)
        $('.nav-card').hide()
    }

    /*
     * Homepage carousel
     */

    var changeSlide = function (toIndex) {
        // show the slide
        $('#carousel .post-update.active').removeClass('active')
        $('#carousel .post-update').eq(toIndex).addClass('active')
        // highlight the button
        $('#post-controls a div.active').removeClass('active')
        $('#post-controls a div').eq(toIndex).addClass('active')
    }

    $('#post-controls a').each(function (i, button) {
        $(button).click(function () {
            changeSlide(i)
            // restart the autoplay "timer" from zero
            clearInterval(playerID)
            playerID = startAutoplay()
        })
    })

    // TODO maybe make mouseenter/mouseleave clear/reset autoplay - 
    // thus hovering would "freeze" the slideshow

    // autoplay function
    var startAutoplay = function () {
        return setInterval(function () {
            var activeIndex = $('#post-controls a div.active').data('index')
            var newIndex = (activeIndex + 1) % $('#post-controls a').length
            changeSlide(newIndex)
        }, 5000) // autoplay slide time is 5s
    }

    // start autoplay if there's more than one slide
    if ($('#carousel .post-update').length > 1) {
        var playerID = startAutoplay()
    }

});
