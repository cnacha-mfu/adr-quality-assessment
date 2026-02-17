# Flask framework 

# Context
We need a framework that supports rapid development, is flexible, scalable and easy to use for our web application.

# Decision
We chose the Flask framework because it is lightweight, simple and offers an extensive ecosystem of extensions.

# Rationale
When it comes to integrating Flask with other frameworks and libraries, Flask's lightweight design is very simple. In addition, Flask's integrated micro-framework approach allows us to customize the application architecture and include only the components required for each use case.

# Consequences
Pros:
*Flask's simplicity and minimalist design allow for rapid development of web applications and prototypes.
*Due to its modular design, Flask can be easily integrated with third-party libraries and extensions, allowing customization to project specifications.
Cons:
*Developers are more responsible for selecting and integrating components with Flask than with other frameworks, which can lead to long development times.
*Some advanced functions may be more complex to implement than with other frameworks.

# Sample code
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
   return 'Hello Flask!'

if __name__ == '__main__':
app.run()
