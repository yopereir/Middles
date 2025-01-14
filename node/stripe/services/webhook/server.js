// Initializations
require("dotenv").config();
const express = require("express");
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
const bodyParser = require("body-parser");

// Middleware setup
const app = express();
const PORT = 4242;

// ---------------------------------------------------------------

// Webhook to handle successful payment and create an invoice
app.post("/webhook", bodyParser.raw({type: 'application/json'}), async (req, res) => {
  let event;
  // Verify event came from Stripe
  try{
    event = await stripe.webhooks.constructEvent(req.body, req.headers['stripe-signature'], webhookSecret);
  } catch (err) {
    // On error, log and return the error message
    console.log(`❌ Error message: ${err.message}`);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }
  // Handle the event
  switch (event.type) {
    // Handle checkout complete event
    case "checkout.session.completed":
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
        break;
    // Handle invoice paid event
    case "invoice.payment_succeeded":
        const invoice = event.data.object; // The invoice object
        const customerId = invoice.customer;
        const amountPaid = invoice.amount_paid / 100;

        console.log(`Invoice for Customer ${customerId} paid: $${amountPaid}`);

        // Optional: Fetch customer details
        const customer = await stripe.customers.retrieve(customerId);
        console.log(`Email sent to: ${customer.email}`);
        break;
    // Handle other event types as needed
    default:
        console.log(`Unhandled event type: ${event.type}`);
  }
  res.json({ received: true });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
