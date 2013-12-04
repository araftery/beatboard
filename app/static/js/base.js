var callback = function(data) {
    if (data.upvoted == true)
    {
        data.upvoted_int = 1;
    }
    else
    {
        data.upvoted_int = 0;
    } 

    if (data.starred == true)
    {
        data.starred_int = 1;
    }
    else
    {
        data.starred_int = 0;
    }
    url = '/vote/' + data.id + '/' + data.upvoted_int + '/' + data.starred_int
    $.ajax({
        url: '/vote/' + data.id + '/' + data.upvoted_int + '/' + data.starred_int,
        type: 'GET'
    });
};


$(function() {

    function load_page(url, title) 
    {
        window.history.pushState("Updating URL to " + title, title, url);

        $.ajax(
            {
                url: url,
                type: 'POST',
                data: { 'ajax': 'true' },
                success:function(result) {
                            $("#block").html(result);
                            console.log(result);
                        }
            }
            );
    }
    $('ul.nav li a').click(function (){
        var title = $(this).data('title');
        var href = $(this).data('href');
        $('ul.nav li').removeClass('active')
        $(this).parent().addClass('active');
        load_page(href, title);
        return false;
    });
    
$(document).on("click", 'a:not(.ignore)', function(event) { 
        event.preventDefault(); 
        var title = 'BeatBoard'
        var href = $(this).attr('href');
        load_page(href, title);
        return false;
    });

    $('#search_form').submit(function(){
        var query = $('.search_query').val();
        load_page('/search/' + query, 'Search');
        return false;
    });

});