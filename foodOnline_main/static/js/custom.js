let autocomplete;

function initAutocomplete(){
    const input = document.getElementById('id_address');
    if (input) {
        autocomplete = new google.maps.places.Autocomplete(
            input,
            {
                types: ['geocode', 'establishment'],
                //default in this app is "IN" - add your country code
                componentRestrictions: {'country': ['IR']},
            });
        // function to specify what should happen when the prediction is clicked
        autocomplete.addListener('place_changed', onPlaceChanged);
    }else {
        console.error('Input element not found');
    }
    
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();
    // console.log('Full place object:', JSON.stringify(place));

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        console.log('place name=>', place.name);
        
    };
    // get the address components and assign them to the fields
    var geocoder = new google.maps.Geocoder()
        var address = document.getElementById('id_address').value

        geocoder.geocode({'address': address}, function(results, status){
            // console.log('results->', results);
            // console.log('status->', status);
            if (status == google.maps.GeocoderStatus.OK) {
                var latitude = results[0].geometry.location.lat();
                var longitude = results[0].geometry.location.lng();

                // console.log('lat=>', latitude);
                // console.log('long=>', longitude);
                $('#id_latitude').val(latitude);
                $('#id_longitude').val(longitude);

                $('#id_address').val(address);
            }
        });

        // loop through the address components and assign other address data
        console.log(place)
        for(var i=0; i<place.address_components.length; i++) {
            for(var j=0; j<place.address_components[i].types.length; j++){
                if (place.address_components[i].types[j] == 'country') {
                    $('#id_country').val(place.address_components[i].long_name);
                }
                //get state 
                if (place.address_components[i].types[j] == 'administrative_area_level_1') {
                    $('#id_state').val(place.address_components[i].long_name);
                }
                //get city
                if (place.address_components[i].types[j] == 'locality') {
                    $('#id_city').val(place.address_components[i].long_name);
                }
                // get pincode
                if (place.address_components[i].types[j] == 'postal_code') {
                    $('#id_pin_code').val(place.address_components[i].long_name);
                }else {
                    $('#id_pin_code').val('');
                }
            }
        }
    
}



$(document).ready(function(){

    initAutocomplete();

    // ADD TO CART
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        // alert(food_id + url)

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response.cart_count['cart_count']);
                if(response.status == 'login required') {
                    swal.fire(response.message, '', 'info').then(function(e){
                        window.location = '/login';
                    })
                }else if(response.status == 'failure'){
                    swal.fire(response.message, '', 'error')
                }
                else {
                    console.log('here in js')
                    $('#cart_counter').html(response.cart_count['cart_count'])
                    $('#qty-'+food_id).html(response.qty)

                    //recalculates the expenses
                    applyCartAmounts(
                        response.cart_amounts['subtotal'],
                        response.cart_amounts['tax'],
                        response.cart_amounts['grand_total']
                    )
                }
            }
        })
    })

    // PLACE THE ITEM QUANTITY ON LOAD
    $('.item-qty').each(function(e){
        var food_id = $(this).attr('id');
        var quantity = $(this).attr('data-qty');
        // console.log(quantity)
        $('#'+food_id).html(quantity)
    })

    // DECREMENT CART
    $('.decrement_cart').on('click', function(e){
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        cartItem_id = $(this).attr('id');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response.cart_count['cart_count']);
                if(response.status == 'login required') {
                    swal.fire(response.message, '', 'info').then(function(e){
                        window.location = '/login';
                    })
                }else if(response.status == 'failure'){
                    swal.fire(response.message, '', 'error')
                }else {
                    $('#cart_counter').html(response.cart_count['cart_count'])
                    $('#qty-'+food_id).html(response.qty)

                    //recalculates the expenses
                    applyCartAmounts(
                        response.cart_amounts['subtotal'],
                        response.cart_amounts['tax'],
                        response.cart_amounts['grand_total']
                    )

                    // only for cart page
                    if (window.location.pathname == '/cart/') {
                        // remove cart item from page if it has zero quantity
                    removeCartItem(response.qty, cartItem_id)
                    // show empty cart messafe if cart is empty
                    checkCartCounter();
                    }
                    
                }
                
            }
        })
    })


    // DELETE CART ITEM
    $('.delete_cart').on('click', function(e){
        e.preventDefault();


        cartItem_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response.cart_count['cart_count']);
                if(response.status == 'failure'){
                    swal.fire(response.message, '', 'error')
                }else {
                    $('#cart_counter').html(response.cart_count['cart_count']);
                    swal.fire(response.status, response.message, );

                    //recalculates the expenses
                    applyCartAmounts(
                        response.cart_amounts['subtotal'],
                        response.cart_amounts['tax'],
                        response.cart_amounts['grand_total']
                    )

                    // removes item from cart page
                    removeCartItem(0, cartItem_id)            

                    // show empty cart
                    checkCartCounter();

                }
                
            }
        })
    })


    //add hour functionality in available hours in vendor panel
    $('.add_hour').on('click', function(e){
        e.preventDefault();

        var day = document.getElementById('id_day').value
        var from_hour = document.getElementById('id_from_hour').value
        var to_hour = document.getElementById('id_to_hour').value
        var is_closed = document.getElementById('id_is_closed').checked
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val()
        var url = document.getElementById('add_hour_url').value

        console.log(day, from_hour, to_hour, is_closed, csrf_token);

        if (is_closed) {
            is_closed = "True"
            condition = "day != ''"
        }else{
            is_closed = "False"
            condition = "day != '' && from_hour != '' && to_hour != ''"
        }

        if (eval(condition)) {
            $.ajax({
                type: 'POST',
                url: url,
                data: {
                    'day': day,
                    'from_hour': from_hour,
                    'to_hour': to_hour,
                    'is_closed': is_closed,
                    'csrfmiddlewaretoken': csrf_token,
                },
                success: function(response){
                    if (response.status == 'success') {
                        if (response.is_closed == 'Closed') {
                            html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>Closed</td><td><a href="" class="remove_hour" data-url="/vendor/available-hours/remove/'+response.id+'/">Remove</a></td></tr>'
                        } else {
                            html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>'+response.from_hour+' - '+response.to_hour+'</td><td><a href="" class="remove_hour" data-url="/vendor/available-hours/remove/'+response.id+'/">Remove</a></td></tr>'
                        }
                        
                        $('.available-hours').append(html)
                        document.getElementById('available-hours').reset()

                    }else{
                        console.log(response.error)
                        swal.fire(response.message, '', 'error');
                    }
                }
            })
        } else {
            swal.fire('Fill all the fields', '', 'info');
        }

    })


    // removes specific available hour
    // $('.remove_hour').on('click', function(e){
    //     e.preventDefault();
    //     url = $(this).attr('data-url');
    //     console.log(url);
    //     $.ajax({
    //         type: 'GET',
    //         url: url,
    //         success: function(response){
    //             if (response.status == 'success') {
    //                 document.getElementById('hour-'+response.id).remove()
    //             }
    //         }
    //     })
    // })

    $(document).on('click', '.remove_hour', function(e){
        e.preventDefault();
        url = $(this).attr('data-url');
        console.log(url);
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if (response.status == 'success') {
                    document.getElementById('hour-'+response.id).remove()
                }
            }
        })
    })

    
    // removes item from cart page
    function removeCartItem(item_qty, cartItem_id){
        if(item_qty <= 0) {
            console.log('here');
            $('#cart-item-'+cartItem_id).remove();
        }
    }

    // check if the cart is empty
    function checkCartCounter() {
        cart_counter = $('#cart_counter').html();
        if(cart_counter == 0){
            $('#empty-cart').css('display', 'block');
        }
    }

    // apply cart amounts changes
    function applyCartAmounts(subtotal, tax, grand_total){
        if (window.location.pathname == '/cart/') {
            $('#subtotal').html(subtotal);
        $('#tax').html(tax);
        $('#total').html(grand_total);
        }
    }


});