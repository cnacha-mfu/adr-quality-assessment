ADR 1: Using Flask for API Development 
Context 
Our project requires a lightweight, flexible web framework that integrates seamlessly with our 
existing Python-based ecosystem. Flask's simplicity and extensibility make it ideal for building 
customizable web APIs, especially in environments where fine-grained control over components 
is necessary. 
Decision 
We will use Flask to develop our web APIs due to its widespread adoption, simplicity in creating 
routes, and the ability to integrate numerous extensions tailored to our specific requirements. 
Rationale 
●​ Ease of Use: Flask's simplicity allows for quick setup and easy route handling, making it 
ideal for projects that need to be up and running promptly without a steep learning curve. 
●​ Flexibility and Extensibility: Flask's design is non-opinionated, giving developers the 
freedom to choose their tools and extensions to build a custom app architecture. 
●​ Community and Support: With a large community of developers, finding support, 
tutorials, and plugins is easier, ensuring robust community-driven support and quick 
troubleshooting. 
Consequences 
●​ Pros: 
○​ Increased developer productivity due to its simplicity and the large number of 
available plugins. 
○​ Flexible app architecture that can be as minimal or as complex as needed, 
allowing for tailored solutions that fit project-specific requirements. 
●​ Cons: 
○​ Not inherently asynchronous, which can be a bottleneck for handling multiple 
simultaneous requests efficiently. 
○​ Might require additional configuration and setup to integrate various components 
and ensure scalability. 
 
from flask import Flask, request, jsonify 
 
app = Flask(__name__) 
items = [] 
 

@app.route('/api/items', methods=['POST']) 
def add_item(): 
   item = request.json 
   items.append(item) 
   return jsonify(item), 201 
 
@app.route('/api/items', methods=['GET']) 
def get_items(): 
   return jsonify(items) 
 
@app.route('/api/items/<int:index>', methods=['PUT']) 
def update_item(index): 
   item = request.json 
   items[index] = item 
   return jsonify(item) 
 
@app.route('/api/items/<int:index>', methods=['DELETE']) 
def delete_item(index): 
   items.pop(index) 
   return '', 204 
 
if __name__ == '__main__': 
   app.run(debug=True)
