/*
var current_page = 1;
var wait = false;

$(window).scroll(function(){
	if ($(window).scrollTop() == $(document).height() - $(window).height() && wait == false)
	{
		$('.scroll').append('<div id="loading"><img src="/static/loading.gif /></div>"');
		load_more_posts();
		wait = true;
	}
});

function load_more_posts()
{
	$.ajax(
	{
		type: "GET",
		url: "/load/" + (current_page + 1),
		success: function(html)
		{
			$('#loadig').remove();
			$('.scroll').append(html);
			current_page++;
			wait = false;
		}
	});
}
*/