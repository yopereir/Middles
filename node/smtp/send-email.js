const nodemailer = require('nodemailer');

// Create a transporter using the local SMTP server
let transporter = nodemailer.createTransport({
  host: 'localhost',
  port: 2525,
  secure: false,  // true for 465, false for other ports
  auth: {
    user: 'username',  // You can use authentication if needed
    pass: 'password',
  },
  tls: {
    rejectUnauthorized: false,  // Ignore self-signed certificate warnings
  },
});

// Set up email data with unicode symbols
let mailOptions = {
  from: '"Your Name" <yourname@example.com>',  // Sender address
  to: 'helmer.cremin@ethereal.email',  // List of recipients
  subject: 'Hello ✔',  // Subject line
  text: 'Hello world?',  // Plain text body
  html: '<b>Hello world?</b>',  // HTML body
};

// Send mail with defined transport object
transporter.sendMail(mailOptions, (error, info) => {
  if (error) {
    return console.log(error);
  }
  console.log('Message sent: %s', info.messageId);
});
