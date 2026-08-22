/**
 * Clientside helper functions
 */

$(document).ready(function() {
  var amounts = document.getElementsByClassName("amount");

  // iterate through all "amount" elements and convert from cents to dollars
  for (var i = 0; i < amounts.length; i++) {
    var amount = amounts[i].getAttribute('data-amount') / 100;
    amounts[i].innerHTML = amount.toFixed(2);
  }

  var paymentForm = document.getElementById('payment-form');

  if (!paymentForm) {
    return;
  }

  var stripe = Stripe(paymentForm.dataset.publishableKey);
  var elements = stripe.elements({ clientSecret: paymentForm.dataset.clientSecret });
  var paymentElement = elements.create('payment');
  var submitButton = document.getElementById('submit');
  var paymentMessage = document.getElementById('payment-message');

  paymentElement.mount('#payment-element');

  paymentForm.addEventListener('submit', function(event) {
    event.preventDefault();

    submitButton.disabled = true;
    paymentMessage.textContent = '';

    stripe.confirmPayment({
      elements: elements,
      confirmParams: {
        payment_method_data: {
          billing_details: {
            email: document.getElementById('email').value,
          },
        },
        return_url: paymentForm.dataset.returnUrl,
      },
    }).then(function(result) {
      if (result.error) {
        paymentMessage.textContent = result.error.message;
        submitButton.disabled = false;
      }
    });
  });
});