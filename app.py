import os
import stripe

from dotenv import load_dotenv
from flask import Flask, request, render_template

load_dotenv()

app = Flask(__name__,
  static_url_path='',
  template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "views"),
  static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"))

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

BOOKS = {
  '1': {
    'title': 'The Art of Doing Science and Engineering',
    'author': 'Richard Hamming',
    'amount': 2300,
  },
  '2': {
    'title': 'The Making of Prince of Persia: Journals 1985-1993',
    'author': 'Jordan Mechner',
    'amount': 2500,
  },
  '3': {
    'title': 'Working in Public: The Making and Maintenance of Open Source',
    'author': 'Nadia Eghbal',
    'amount': 2800,
  },
}

# Home route
@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

# Checkout route
@app.route('/checkout', methods=['GET'])
def checkout():
  item = request.args.get('item')
  book = BOOKS.get(item)
  error = None
  payment_intent = None

  if not book:
    error = 'No item selected'
  elif not stripe.api_key or not os.getenv('STRIPE_PUBLISHABLE_KEY'):
    error = 'Stripe API keys are not configured'
  else:
    payment_intent = stripe.PaymentIntent.create(
      amount=book['amount'],
      currency='usd',
      payment_method_types=['card'],
      metadata={
        'item': item,
        'title': book['title'],
      },
    )

  return render_template(
    'checkout.html',
    title=book['title'] if book else None,
    amount=book['amount'] if book else None,
    error=error,
    stripe_publishable_key=os.getenv('STRIPE_PUBLISHABLE_KEY'),
    client_secret=payment_intent.client_secret if payment_intent else None,
  )

# Success route
@app.route('/success', methods=['GET'])
def success():
  payment_intent_id = request.args.get('payment_intent')
  error = None
  payment_intent = None

  if not payment_intent_id:
    error = 'Missing payment confirmation details'
  elif not stripe.api_key:
    error = 'Stripe secret key is not configured'
  else:
    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

  return render_template(
    'success.html',
    error=error,
    payment_intent=payment_intent,
  )


if __name__ == '__main__':
  app.run(port=5000, host='0.0.0.0', debug=True)