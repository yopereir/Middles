# Stripe
Repo containing middleware to query Stripe API.

## Deploy:
* Run `npm run start` to start stripe-query+webhook server.
* Run `stripe listen --events invoice.payment_succeeded,checkout.session.completed,charge.succeeded --forward-to http://localhost:3000/webhook` to listen for webhooks.
* Go to http://localhost:3000 to view `index.html` page. Optionally trigger events for stripe using `stripe trigger invoice.payment_succeeded`.

## Conventions:
* Frontend pages lie in `frontend` folder, where `index.html` is landing page, `success.html` and `cancel.html` are for successful and errored payment respectively.

* Each Project should have a README.md file with instructions on how to get the service running.

* When building Docker images or to Kubernetes, use the naming convention `Language-Framework-ServiceName` for the main Image name and Namespace name.