# Title
Web Application

## Context
The decision to utilize Firebase as the backend solution for our web application development project.

The need for a robust and scalable backend solution arose due to:

1. Long development time and resource constraints:

Challenge: Building and managing a custom backend from scratch requires significant development time and resources, delaying launch and stretching the team.

2. Lack of specific functionalities:

Current solution: The current backend lacks features like user authentication, real-time updates, or static file hosting, hindering desired app functionalities.
## Decision
We have decided to utilize Firebase as the backend solution for our web application development project. Firebase provides a comprehensive set of tools and services that will help us overcome the challenges we are facing:

Development Time and Resource Constraints: Firebase offers a set of pre-built backend services that are easy to integrate and require minimal development effort. This will help us reduce the development time and resources needed to build and manage a custom backend.

Lack of Specific Functionalities: Firebase provides a wide range of functionalities out-of-the-box, including user authentication, real-time updates, and static file hosting. By using Firebase, we can easily incorporate these features into our web application, enhancing its functionality and user experience.


## Rationale
Firebase provide multiple tools to web application development, The large community of firebase make it strong beneficial to developer. Firebase provide dependency to many programming language(ie. Javascripts and Java SpringBoot) and the strongest benefit is scalability.

## Consequences
Pros – Firebase, backed by Google, making it a powerful tool for web applications. It's especially beneficial for newbie programmers, as it's user-friendly and free. This platform allows beginners to grasp how their apps function in world scenarios

Cons – for projects requiring intricate backend setups, Firebase might not be the best fit.

## Sample code
This code is a basic Firebase Web App for authentication using Firebase Authentication and Firestore.
```html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Firebase Web App</title>
    <!-- Add Firebase JavaScript SDK -->
    <script src="https://www.gstatic.com/firebasejs/9.1.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.1.0/firebase-auth.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.1.0/firebase-firestore.js"></script>
</head>
<body>
    <h1>Firebase Web App</h1>
    <div id="login">
        <input type="email" id="email" placeholder="Email">
        <input type="password" id="password" placeholder="Password">
        <button onclick="signIn()">Sign In</button>
        <button onclick="signUp()">Sign Up</button>
    </div>
    <div id="user-info" style="display: none;">
        <p id="user-email"></p>
        <button onclick="signOut()">Sign Out</button>
    </div>

    <!-- Initialize Firebase -->
    <script>
        const firebaseConfig = {
            apiKey: "YOUR_API_KEY",
            authDomain: "YOUR_AUTH_DOMAIN",
            projectId: "YOUR_PROJECT_ID",
            storageBucket: "YOUR_STORAGE_BUCKET",
            messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
            appId: "YOUR_APP_ID"
        };
        // Initialize Firebase
        firebase.initializeApp(firebaseConfig);

        const auth = firebase.auth();
        const db = firebase.firestore();

        function signUp() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            auth.createUserWithEmailAndPassword(email, password)
                .then(userCredential => {
                    const user = userCredential.user;
                    console.log('User signed up:', user);
                })
                .catch(error => {
                    console.error('Error signing up:', error);
                });
        }

        function signIn() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            auth.signInWithEmailAndPassword(email, password)
                .then(userCredential => {
                    const user = userCredential.user;
                    console.log('User signed in:', user);
                })
                .catch(error => {
                    console.error('Error signing in:', error);
                });
        }

        function signOut() {
            auth.signOut()
                .then(() => {
                    console.log('User signed out');
                })
                .catch(error => {
                    console.error('Error signing out:', error);
                });
        }

        auth.onAuthStateChanged(user => {
            if (user) {
                // User is signed in
                document.getElementById('login').style.display = 'none';
                document.getElementById('user-info').style.display = 'block';
                document.getElementById('user-email').textContent = 'User: ' + user.email;
            } else {
                // User is signed out
                document.getElementById('login').style.display = 'block';
                document.getElementById('user-info').style.display = 'none';
            }
        });
    </script>
</body>
</html>
