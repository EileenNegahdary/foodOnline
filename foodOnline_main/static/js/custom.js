$(document).ready(function(){

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