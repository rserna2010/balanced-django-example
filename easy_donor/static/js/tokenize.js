$(document).ready(function () {
    // Callback for handling responses from Balanced
    function handleResponse(response) {
        // Successful tokenization
        if (response.status_code === 201) {
            var fundingInstrument = response.cards != null ? response.cards[0] : response.bank_accounts[0];
            if ( $('#ba-name').length ){
                var charity_id = $('#ba-name').attr('data-charity_id');
                jQuery.post("/easy_donor/add_funding_instrument/", {
                    href: fundingInstrument.href,
                    charity_id: charity_id
                }, function(r) {
                    // Check your backend response
                    if (r.location === 'finished') {
                        $(location).attr('href', '/easy_donor');
                    } else {
                    }
                });
            } else {
                var charity_id = $('#cc-name').attr('data-charity_id')
                var amount = $('#amount').val();
                if (valid_amount(amount)) {
                    jQuery.post("/easy_donor/donate/", {
                        href: fundingInstrument.href,
                        amount: amount,
                        charity_id: charity_id
                    }, function(r) {
                        // Check your backend response
                        if (r.location === 'finished') {
                            $(location).attr('href', '/easy_donor');
                        } else {
                        }
                    });
                }
            }
        } else {
            alert(response.errors[0]['description'])
        }

        // Debuging, just displays the tokenization result in a pretty div
        $('#response .panel-body pre').html(JSON.stringify(response, false, 4));
        $('#response').slideDown(300);
    }

    // Click event for tokenize credit card
    $('#cc-submit').click(function (e) {
        e.preventDefault();

        $('#response').hide();

        var payload = {
            name: $('#cc-name').val(),
            number: $('#cc-number').val(),
            expiration_month: $('#cc-ex-month').val(),
            expiration_year: $('#cc-ex-year').val(),
            cvv: $('#cc-cvv').val(),
            address: {
                postal_code: $('#ex-postal-code').val()
            }
        };

        // Tokenize credit card
        balanced.card.create(payload, handleResponse);
    });

    // Click event for tokenize bank account
    $('#ba-submit').click(function (e) {
        e.preventDefault();

        $('#response').hide();
        var account_owner_name = $('#ba-name').val()
        var account_number = $('#ba-number').val()
        var routing_number = $('#ba-routing').val()

        if (account_owner_name == "" || account_number == "" ||
            routing_number =="") {
            alert('Please ensure all fields are complete');

        } else {
            var payload = {
                name: account_owner_name,
                account_number: account_number,
                routing_number: routing_number
            };
            // Tokenize bank account
            balanced.bankAccount.create(payload, handleResponse);
        }
    });



});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function valid_amount(amount) {
    var regex = /(?=.)^\$?(([1-9][0-9]{0,2}(,[0-9]{3})*)|[0-9]+)?(\.[0-9]{1,2})?$/g;
    if(regex.test(amount)) {
        return true
    } else {
        alert("Please input valid amount");
    }
}