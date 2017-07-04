$(document ).ready(function() {

$( window ).load(function() {
	setTimeout(function(){ $(".customer_icon").parent().prependTo(".oe_systray"); console.log("document ready function");}, 10000);
});
});

