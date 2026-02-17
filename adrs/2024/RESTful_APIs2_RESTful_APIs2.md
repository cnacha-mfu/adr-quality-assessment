# Title
Implementing Token-Based Authentication for RESTful APIs
## Context
Our current RESTful API system relies on traditional username and password authentication, which poses security risks and limitations in managing user sessions securely.

## Decision
We propose implementing token-based authentication for our RESTful APIs to enhance security, improve user experience, and provide better session management.

## Rationale
Token-based authentication offers several advantages over traditional methods:

1.Security: Tokens are more secure than storing plain passwords. They can be configured with short expiration times and are less susceptible to brute-force attacks.
2.Statelessness: Token-based authentication makes APIs stateless, allowing for better scalability and ease of deployment across multiple servers.
3.Granular Control: Tokens can be issued with specific scopes and permissions, providing granular control over API access.
Improved User Experience: Users can remain logged in without the need to re-enter credentials for each request, enhancing the overall user experience.

## Consequences
Pros:

1.Enhanced Security: Token-based authentication adds an extra layer of security, reducing the risk of unauthorized access.
2.Improved Scalability: Stateless APIs are more scalable, making it easier to handle a large number of concurrent users.
3.Better User Experience: Users benefit from smoother interactions with the API, as they don't need to repeatedly enter credentials.
4.Granular Access Control: Token scopes allow for fine-grained control over API access, improving data protection.

Cons:

1.Implementation Overhead: Implementing token-based authentication requires additional development effort.
2.Educational Effort: Users and developers need to be informed about the new authentication method.
3.Token Management: Proper management of tokens, including expiration and revocation, is crucial to maintain security.

## Sample code


from flask import Flask, request
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
api = Api(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this to a secure secret key in production
jwt = JWTManager(app)

class UserLogin(Resource):
    def post(self):
        # Validate user credentials (username and password)
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        
        if username == 'sample_user' and password == 'sample_password':
            # Create an access token with a 15-minute expiration time
            access_token = create_access_token(identity=username, expires_delta=False)
            return {'access_token': access_token}, 200
        else:
            return {'message': 'Invalid credentials'}, 401

class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        # Access the current user's identity
        current_user = get_jwt_identity()
        return {'message': f'Hello, {current_user}! This is a protected resource.'}


api.add_resource(UserLogin, '/login')
api.add_resource(ProtectedResource, '/protected')

if __name__ == '__main__':
    app.run(debug=True)
