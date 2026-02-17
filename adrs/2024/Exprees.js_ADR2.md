
## ADR 2: Structuring the Application Using MVC Pattern with Express.js
# Context
Anticipating the growth in complexity of our application, we require a scalable and maintainable architecture. A clear separation of concerns is essential for efficient development among different teams.

# Decision
We have opted to structure our Express.js application using the Model-View-Controller (MVC) architectural pattern.

# Rationale
Separation of Concerns: MVC enhances modularity by dividing the application into three interconnected components, simplifying management and scaling.
Ease of Maintenance: This pattern facilitates updates and maintenance of each component independently, reducing the risk of unintended side effects.
Enhanced Collaboration: MVC supports parallel development, allowing for faster development cycles and improved team collaboration.
Framework Support: Express.js natively supports the MVC pattern through its routing and middleware functionalities, easing the implementation.
Consequences

Pros:

Improved modularity and ease of application scaling.
Simplified maintenance and updates.

Cons:

Requires adherence to the MVC pattern, potentially necessitating training.
Evaluation and integration of templating engines for view rendering might be needed.

# sample code

// app.js - Entry point
const express = require('express');
const app = express();
// MVC components
const routes = require('./routes'); // Controller
app.use('/', routes);
app.listen(3000, () => console.log('Server started'));

// routes/index.js - Controller example
const express = require('express');
const router = express.Router();
router.get('/', (req, res) => res.send('MVC with Express.js'));
module.exports = router;

// Further model and view examples would be structured similarly.
