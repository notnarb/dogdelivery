dogdelivery = (function () {
    var urlPrefix;
    var stadium;
    var vendor;
    var item;

    function init () {
	var pageInfo = pageVariables || {}; //get pageVariables (should be stored by template)
	urlPrefix = pageInfo.urlPrefix;
	stadium = pageInfo.stadium;
	vendor = pageInfo.vendor;
	item = pageInfo.item;
	// If there is nothing in the cart, hide it
	if ($("#cart-button-number").text() === "0")
	    $("#cart-button").hide();
	$("#cart-button").click(getCart);

	// Vendor page
	if (pageInfo.currentPage == "vendor") {
	    // Add observers to all incrementing buttons
	    // $(".item-container-quantity").each( function (i, element) {
	    // 	$(element).empty();
	    // 	var incrementSide = $("<div>", {'class':"input-group-btn"}).appendTo($(element));
	    // 	var incrementButton = $("<button>",{'class':"btn btn-default item-incrementer","text":"+"}).appendTo(incrementSide);
	    // 	var quantitySelector = $("<input>", {
	    // 	    'class':'form-control quantity-selector',
	    // 	    'type': 'text'
	    // 	}).appendTo($(element));
	    // 	var decrementSide = $("<div>", {'class':"input-group-btn"}).appendTo($(element));
	    // 	var decrementButton = $("<button>",{'class':"btn btn-default item-incrementer","text":"-"}).appendTo(decrementSide);
	    // 	// console.log($(element).parent().parent().data('item'));

	    // }); 

	}
    };

    function update_id (selectbox) {
	var item_name = selectbox.data('name');
	$.ajax(
	    {'type':'POST',
	     'url' : item_name.concat('/'),
	     'data': {
		 'quantity' : parseInt(selectbox.val()),
		 'csrfmiddlewaretoken': '{{csrf_token}}'
	     }}).done(
		 function (response) {
		     if (response.error)
			 alert(response.error);
		 }
	     );
    };


    function cart_url () {
	if (!stadium)
	    return urlPrefix.concat("cart/");
	if (!vendor)
	    return urlPrefix.concat(["cart", stadium].join("/")).concat("/");
	return urlPrefix.concat(["cart", stadium, vendor].join("/")).concat("/");
    };

     function getCart () {
	$.ajax({
	    'url': cartUrl(), 
	    dataType: 'json'});
    };

    return {
	'init': init()
    };
}());

$(document).ready(dogdelivery.init);



