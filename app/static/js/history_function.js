$(function() {
    var History = window.History;
    State = History.getState();
    
    // set initial state to first page that was loaded
    History.pushState({urlPath: window.location.pathname}, $("title").text(), State.urlPath);


    // Content update and back/forward button handler
    History.Adapter.bind(window, "statechange", function() {
        var state = History.getState();
        load_page(state.url, state.title)
    });

    console.log("")
});