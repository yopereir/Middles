// Initialization
require("dotenv").config();
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);
const bodyParser = require("body-parser");
const path = require("path");

// Tests
test('Get price using lookup key', async () => {
  const LOOKUP_KEY = 'testProduct'
  const price = await stripe.prices.list({
    currency: 'usd',
    lookup_keys: [LOOKUP_KEY],
  });
});