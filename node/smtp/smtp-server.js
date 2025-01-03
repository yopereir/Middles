const { SMTPServer } = require('smtp-server');

// Create an instance of an SMTP server
const server = new SMTPServer({
  // Disable authentication for testing purposes (you can implement it as needed)
  authOptional: true,
  
  // Event handler for receiving emails
  onData(stream, session, callback) {
    let emailData = '';
    stream.on('data', (chunk) => {
      emailData += chunk;
    });

    stream.on('end', () => {
      console.log(`Received email:\n${emailData}`);
      callback(null);  // Indicate success
    });
  },

  onAuth(auth, session, callback) {
    if (auth.username === 'username' && auth.password === 'password') {
      callback(null, { user: 'user' });  // Authentication success
    } else {
      callback(new Error('Invalid username or password'));
    }
  },
});

// Start listening on port 25 (default SMTP port) or another port (e.g., 2525)
server.listen(2525, () => {
  console.log('SMTP Server is running on port 2525');
});
