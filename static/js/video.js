$(function() {
    $('.tv-video').each(function() {
        let image = $(this).attr('data-video');
        $(this).html('<img alt="" src="https://i.ytimg.com/vi/'+ image +'/hq720.jpg" />');
    });
    $('.tv-video').click(function() {
        $(this).addClass('show');
        let video = $(this).attr('data-video');
        $(this).html('<iframe width="560" height="315" src="https://www.youtube.com/embed/'+ video +'?autoplay=1" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>');
    });
});