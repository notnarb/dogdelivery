dogdelivery = (function () {
    // Embeded variables from django template

    var urlPrefix;
    var stadium;
    var vendor;
    var item;
    
    var csrf_token;

    // The number of ajax queries queued up
    var cart_spinner_counter;

    function init () {
	var pageInfo = pageVariables || {}; //get pageVariables (should be stored by template)
	urlPrefix = pageInfo.urlPrefix;
	stadium = pageInfo.stadium;
	vendor = pageInfo.vendor;
	item = pageInfo.item;

	csrf_token = pageInfo.csrf_token;
	
	// // If there is nothing in the cart, hide it
	// if ($("#cart-button-number").text() === "0")
	//     $("#cart-button").hide();
	$("#cart-button").click(getCart);

	// Vendor page
	if (pageInfo.currentPage == "vendor") {
	    $(".item-incrementer").each( function (i, element) {
		var selectbox = $("#item-quantity-".concat($(element).data('item')));
		$(element).click(function () {increment_item(selectbox);});		
	    });
	    $(".item-decrementer").each( function (i, element) {
		var selectbox = $("#item-quantity-".concat($(element).data('item')));
		$(element).click(function () {decrement_item(selectbox);});		
	    });
	    cart_spinner_counter = 0;
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

    function increment_cart_counter () {
	if (cart_spinner_counter <= 0) {
	    cart_spinner_counter = 0;
	    $('#cart-button-container').spin('small');
	}
	cart_spinner_counter ++;	
    };

    function decrement_cart_counter () {
	cart_spinner_counter--;
	if (cart_spinner_counter <= 0) {
	    $('#cart-button-container').spin(false);
	    cart_spinner_counter = 0;
	}
    }

    /**
     * Increment a selectbox
     */
    function increment_item (selectbox) {
	selectbox.val(+selectbox.val() + 1);
	update_quantity(selectbox);
    };

    /**
     * Increment a selectbox
     * @returns [boolean] returns true if a valid value, false if an invalid (negative) value
     */
    function decrement_item (selectbox) {
	if (selectbox.val() <= 0)
	    return false;
	selectbox.val(+selectbox.val() - 1);
	update_quantity(selectbox);
	return true;
    };

    /**
     * Saves a change to an item's quantity box
     * @param selectbox the jquery selectbox
     */
    function update_quantity (selectbox) {
	var item_name = selectbox.data('name');
	
	increment_cart_counter();

	// var spinner = new Spinner().spin();
	// $("body").appendChild(spinner.el);
	$.ajax(
	    {
		'type':'POST',
		'url' : item_name.concat('/'),
		'dataType': 'json',
		'data': {
		    'quantity' : parseInt(selectbox.val()),
		    'csrfmiddlewaretoken': csrf_token
		},
		'timeout' : 5000, 
		'error' : ajax_error_handler
	    }).done(
		update_quantity_callback
	    );
	return true;
    };

    function update_quantity_callback (response) {
	decrement_cart_counter();
	if (response.error){
	    alert(response.error);
	    return;
	}
	if (!response.cart) {
	    alert("Invalid response from server");
	    return;
	}
	if (!response.cart[stadium][vendor])
	    $("#cart-button-number").text(0);
	else {
	    $("#cart-button-number").text(Object.keys(response.cart[stadium][vendor]).length); //Doesnt work in IE < 9
	}
    };


    function ajax_error_handler (error) {
	if (error.statusText === "timeout"){
	    console.log("Timeout");
	} else {
	    console.log("Unknown error".concat(error));
	}
	decrement_cart_counter();
	if (cart_spinner_counter <= 0) {
	    $('#cart-button-container').spin(false);
	    cart_spinner_counter = 0;
	}
    };

    function cartUrl () {
	if (!stadium)
	    return urlPrefix.concat("cart/");
	if (!vendor)
	    return urlPrefix.concat(["cart", stadium].join("/")).concat("/");
	return urlPrefix.concat(["cart", stadium, vendor].join("/")).concat("/");
    };

     function getCart () {
	 increment_cart_counter();
	 $.ajax({
	     'url': cartUrl(), 
	     dataType: 'json',
	     'timeout': 5000,
	     'error' : ajax_error_handler
	 }).done(
	     renderCart
	 );
     };
    
    function renderCart (response) {
	console.log(response);
	decrement_cart_counter();
	var popup = $('<div>',{'class':'cart-popup'}).appendTo(	$('#cart-button-container'));
	$.each(response.cart, function (stadiumName, vendors) {
	    var stadiumDiv = $('<div>',{'text':stadiumName,'class':'cart-popup-stadium'}).appendTo(popup);
	    $.each(vendors, function (vendorName, items) {
		var vendorDiv = $('<div>',{'text':vendorName,'class':'cart-popup-vendor'}).appendTo(popup);
		var cartCheckoutButton = $('<button>',{'class':'btn btn-success btn-xs cart-popup-checkout-btn','text':'Checkout'}).appendTo(vendorDiv);
		$.each(items, function (itemName, quantity) {
		    $('<div>',{
			'text':itemName.concat(":").concat(quantity),
			'class': 'cart-popup-item'
		    }).appendTo(popup);
		});
	    });
	});
    };

    return {
	'init': init()
    };
}());

$(document).ready(dogdelivery.init);



