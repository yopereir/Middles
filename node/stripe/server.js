require("dotenv").config();
const express = require("express");
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);
const bodyParser = require("body-parser");
const path = require("path");

const app = express();
const PORT = 3000;

async function getPriceForProduct(productId) {
    const product = await stripe.products.retrieve(productId);
    return (await stripe.prices.list({lookup_keys: [product.name]})).data[0]
}

// Middleware setup
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, "frontend-test")));

// Fetch product and price details using Lookup Key
app.get("/product-info", async (req, res) => {
  try {
    const productId = req.query.productId || req.query.productid
    const product = await stripe.products.retrieve(productId);
    const price = getPriceForProduct(productId);
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
app.post("/create-checkout-session", async (req, res) => {
  const { email } = req.body;
  const productId = req.query.productId || req.query.productid

  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ["card"],
      line_items: [
        {
          price: getPriceForProduct(productId), // Price ID from Stripe Dashboard
          quantity: 1,
        },
      ],
      mode: "payment",
      customer_email: email, // Collect customer email
      success_url: "http://localhost:3000/success.html",
      cancel_url: "http://localhost:3000/cancel.html",
    });

    res.json({ id: session.id });
  } catch (error) {
    console.error(error);
    res.status(500).send("Internal Server Error");
  }
});

// Webhook to handle successful payment and create an invoice
app.post("/webhook", express.raw({ type: "application/json" }), async (req, res) => {
  const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;

  let event;

  try {
    event = stripe.webhooks.constructEvent(
      req.body,
      req.headers["stripe-signature"],
      endpointSecret
    );
  } catch (err) {
    console.error(err.message);
    return res.status(400).send(`Webhook error: ${err.message}`);
  }

  // Handle the event
  if (event.type === "checkout.session.completed") {
    const session = event.data.object;

    try {
      const invoice = await stripe.invoices.create({
        customer: session.customer,
        auto_advance: true, // Automatically finalize the invoice
      });

      console.log("Invoice created:", invoice.id);
    } catch (error) {
      console.error("Failed to create invoice:", error);
    }
  }

  res.json({ received: true });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
