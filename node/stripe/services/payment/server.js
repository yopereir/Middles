// Initializations
require("dotenv").config();
const express = require("express");
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);
const bodyParser = require("body-parser");
const path = require("path");

// Middleware setup
const app = express();
const PORT = 3000;
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, "../../frontend")));

// ---------------------------------------------------------------

// Helper functions
async function getPriceForProduct(productId) {
    const product = await stripe.products.retrieve(productId);
    return (await stripe.prices.list({lookup_keys: [product.name]})).data[0]
}

// ---------------------------------------------------------------

// Fetch product and price details using Lookup Key
app.get("/product-info", bodyParser.json(), async (req, res) => {
  try {
    const productId = req.query.productId || req.query.productid
    const product = await stripe.products.retrieve(productId);
    const price = await getPriceForProduct(productId);
    res.json({
      name: product.name,
      description: product.description,
      price_id: price.id,
      unit_amount: price.unit_amount,
      currency: price.currency,
    });
  } catch (error) {
    console.error(error);
    res.status(500).send("Failed to fetch product information.");
  }
});

// Endpoint to handle payment
app.post("/create-checkout-session", bodyParser.json(), async (req, res) => {
  const { email } = req.body;
  const productId = req.query.productId || req.query.productid

  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ["card"],
      line_items: [
        {
          price: (await getPriceForProduct(productId)).id, // Price ID from Stripe Dashboard
          quantity: 1,
        },
      ],
      mode: "payment",
      customer_email: email, // Collect customer email
      customer_creation: "always",
      success_url: "http://localhost:3000/success.html",
      cancel_url: "http://localhost:3000/cancel.html",
    });
    console.log("Created Checkout Session: "+session.id);
    res.json({ id: session.id });
  } catch (error) {
    console.error(error);
    res.status(500).send("Internal Server Error");
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
