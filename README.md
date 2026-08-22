# Stripe Press Shop

Stripe Press Shop is a small Flask e-commerce demo that lets a customer choose one of three books, pay with Stripe's Payment Element, and see a purchase confirmation that includes the total charge and Stripe Payment Intent ID.

## What the app does

- Displays a catalog of three Stripe Press books.
- Creates a server-side Stripe PaymentIntent for the selected book and amount.
- Uses Stripe.js and the Payment Element to collect and confirm payment details in the browser.
- Redirects to a confirmation page after payment confirmation.
- Retrieves the PaymentIntent on the server and displays the total amount charged, PaymentIntent ID, and status.

## Requirements

- Python 3.9+ (this app was tested with Python 3.9)
- A Stripe account
- Stripe sandbox API keys

## Create a Stripe Sandbox and Test API Keys

You can test this app without a real credit card by using a Stripe sandbox, an isolated test environment with its own working API keys.

1. If you don't already have one, [sign up for a free Stripe account](https://dashboard.stripe.com/register).
2. Log in to the [Stripe Dashboard](https://dashboard.stripe.com) and create a new sandbox (if you don't have an existing one).
3. Go to **Developers > API keys** to view the Publishable and Secret keys which are automatically created when the sandbox is created. Use these keys in the `.env` file described below.
4. Use [Stripe's test cards](https://docs.stripe.com/testing) (for example `4242 4242 4242 4242`) to simulate payments in the sandbox—no real money movement or card networks are involved.

## Build, Configure, and Run

1. Install dependencies:

	```bash
	pip3 install -r requirements.txt
	```

2. Create the local environment file:

	```bash
	cp sample.env .env
	```
> This app should only be run with Stripe sandbox API keys during local development. Do not commit your `.env` file or live API keys.

3. Add your Stripe test keys to `.env`:

	```bash
	STRIPE_SECRET_KEY=sk_test_...
	STRIPE_PUBLISHABLE_KEY=pk_test_...
	```



4. Start the Flask app:

	```bash
	flask run
	```

5. Open the app at [http://localhost:5000](http://localhost:5000).

6. Use a Stripe test card, such as `4242 4242 4242 4242`, with any future expiration date, any CVC, and any postal code.

## How the Solution Works

The app uses a simple Flask architecture:

- [app.py](app.py) owns the product catalog, route handling, and Stripe API calls.
- [views/index.html](views/index.html) renders the book catalog and links each book to checkout with an item ID.
- [views/checkout.html](views/checkout.html) renders the checkout page with the selected book, total, and Payment Element container.
- [public/js/custom.js](public/js/custom.js) initializes Stripe.js, mounts the Payment Element, and calls `stripe.confirmPayment`.
- [views/success.html](views/success.html) shows the confirmed payment details returned by the server.

The application intentionally keeps pricing on the server. The browser only sends the selected item ID through the checkout URL; the server looks up the title and amount from the `BOOKS` dictionary in [app.py](app.py). This avoids trusting client-provided prices.

## Stripe APIs Used

This project uses the [Payment Intents API](https://docs.stripe.com/api/payment_intents) with [Stripe Elements](https://docs.stripe.com/payments/elements):

- [`stripe.PaymentIntent.create(...)`](https://docs.stripe.com/api/payment_intents/create): creates a PaymentIntent for the selected book amount in USD.
- [`payment_method_types=['card']`](https://docs.stripe.com/api/payment_intents/create#create_payment_intent-payment_method_types): configures the PaymentIntent for card payments in this demo.
- [`client_secret`](https://docs.stripe.com/api/payment_intents/object#payment_intent_object-client_secret): passed to Stripe.js so the browser can securely render and confirm the Payment Element.
- [`stripe.elements({ clientSecret })`](https://docs.stripe.com/js/elements_object/create): initializes an Elements group on the client using the PaymentIntent's client secret.
- [`elements.create('payment')`](https://docs.stripe.com/js/elements_object/create_payment_element): creates the Payment Element and mounts it to the checkout page.
- [`stripe.confirmPayment(...)`](https://docs.stripe.com/js/payment_intents/confirm_payment): confirms the PaymentIntent from the browser and redirects to the success page.
- [`stripe.PaymentIntent.retrieve(...)`](https://docs.stripe.com/api/payment_intents/retrieve): retrieves the PaymentIntent on the success page so the app can display the final charge amount, PaymentIntent ID, and payment status.

## Approach

I started with the existing Flask app as the source of truth and added payments at the smallest useful integration points:

1. Centralized the hardcoded book data into a `BOOKS` dictionary so prices are consistently controlled server-side.
2. Added PaymentIntent creation to the existing `/checkout` route.
3. Replaced the checkout placeholder with the Payment Element.
4. Added client-side confirmation using Stripe.js.
5. Updated `/success` to retrieve and display the PaymentIntent details after redirect.
6. Preserved the original Bootstrap-based UI so the app still feels like the provided starter project.

The main challenge was balancing simplicity with a structure that can grow later. For this take-home, there is no database or order table, so the PaymentIntent metadata stores the selected item and title. In a production app, that metadata would be backed by an internal order record.

## Documentation Used

- Stripe Payment Element documentation: https://docs.stripe.com/payments/payment-element
- Stripe Payment Intents API documentation: https://docs.stripe.com/api/payment_intents
- Stripe.js `confirmPayment` documentation: https://docs.stripe.com/js/payment_intents/confirm_payment
- Flask documentation: https://flask.palletsprojects.com/

## How I Would Extend This

For a more robust version of the app, I would:

- Migrate from the Payment Intents API to the [Checkout Sessions API](https://docs.stripe.com/api/checkout/sessions) with the Payment Element. Checkout Sessions covers the same payment collection use case with less code to build and maintain, and adds built-in tax calculation (Stripe Tax), coupons/discounts, shipping cost calculation, address collection, order/receipt tracking, automatic session expiration, and webhook events for the full checkout lifecycle instead of payment status only.
- Add a database-backed product catalog, order table, and customer table.
- Add authentication to save/retrieve customer records for repeat purchases.
- A server endpoint that creates PaymentIntents with POST requests instead of creating one on checkout page load (applies only if continuing with Payment Intents/Elements).
- Webhook handling for `payment_intent.succeeded` and related events so fulfillment does not depend on the customer returning to the success page (applies only if continuing with Payment Intents/Elements).
- Inventory, tax, and shipping at check out (applies only if continuing with Payment Intents/Elements; built in with Checkout Sessions).
- Email invoices/receipts
- Add automated tests for item selection, PaymentIntent creation, and success page rendering.


## Challenges

An issue with this project is a Flask/Werkzeug version mismatch. The `requirements.txt` file pins `Flask==2.0.0`. When Flask 2.0.0 is installed, it automatically installs a newer Werkzeug version (Werkzeug v3.1.8 as of this writing). If a newer `Werkzeug` is installed in the environment, Flask was failing at startup with the below error message:

```python
ImportError: cannot import name 'url_quote' from 'werkzeug.urls'
```

The fix was to downgrade and install an older compatible version, such as `Werkzeug==2.0.3`, and add it to the `requirements.txt` and reinstall the python packages and dependencies

```bash
pip install --upgrade --force-reinstall -r requirements.txt
```


