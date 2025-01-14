# Stripe
Repo containing middleware to query Stripe API.

## Deploy:
* Run `npm run payment` to start stripe-payment server.
* Run `npm run webhook` to start stripe-webhook server.
* Run `stripe listen --events invoice.payment_succeeded,checkout.session.completed,charge.succeeded --forward-to http://localhost:4242/webhook` to forward webhooks to local webhook server. Copy webhook secret generated to `STRIPE_WEBHOOK_SECRET` in `.env` file.
* Go to http://localhost:3000 to view `index.html` page. Optionally, trigger events for stripe using `stripe trigger invoice.payment_succeeded`.

## Conventions:
* Frontend pages lie in `frontend` folder, where `index.html` is landing page, `success.html` and `cancel.html` are for successful and errored payment respectively.

* Each micro-service is religated to it's own folder within `services` folder- Payment Checkout to payment folder, Stripe Webhooks to webhook folder.

* When building Docker images or to Kubernetes, use the naming convention `Language-Framework-ServiceName` for the main Image name and Namespace name.