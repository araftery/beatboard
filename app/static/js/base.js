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