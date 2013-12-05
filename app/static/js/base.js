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

    var History = window.History;
    State = History.getState();
    
    // set initial state to first page that was loaded
    History.pushState({urlPath: window.location.pathname}, $("title").text(), State.urlPath);


    // Content update and back/forward button handler
    History.Adapter.bind(window, 'statechange', function() {
        var state = History.getState();
        load_page(state.url, state.title)
    });



    function load_page(url, title, history) 
    {

        $.ajax(
            {
                url: url,
                type: 'POST',
                data: { 'ajax': 'true' },
                success:function(result) {
                            $("#block").html(result);
                        }
            }
            );
    }

    $("ul.nav li a:not(.logout)").click(function (){
        var title = $(this).data('title');
        var href = $(this).data('href');
        $('ul.nav li').removeClass('active')
        $(this).parent().addClass('active');
        
        History.pushState(href, title, href);

        load_page(href, title);
        
        return false;
    });



    
    $(document).on("click", 'a:not(.ignore, .upvote, .star)', function(event) { 
        event.preventDefault(); 
        var title = 'BeatBoard'
        var href = $(this).attr('href');

        History.pushState(href, title, href);

        load_page(href, title);
        return false;
    });

    $('#search_form').submit(function(){
        var query = $('.search_query').val();
        load_page('/search/' + query, 'Search');
        return false;
    });


});
