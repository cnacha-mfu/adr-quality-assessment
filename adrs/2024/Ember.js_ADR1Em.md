# Architecture Decision Record: Ember.js

## Context
Our mobile application requires the selection of a front-end framework to be built.


## Decision
We have decided to use Ember.js as the front-end framework for our application.

## Rationale
1.Ember has automatic version upgrades in case we need to update deprecated codes.
2.Ember gives us a better way of working by reducing complexity in the app and has given us a clear and concise way to structure our code. Make it ten times easier to onboard new developers into the team allowing them to start adding new functionality.


## Consequences
Pros:
1.Consistent project structure.
2.Built-in solutions for common challenges.
3.Long-term support and stability.

Cons:
1.Ember is not suitable for small projects.
2.Learning curve is steep.

## Sample code
// Example Ember.js component
import Component from '@ember/component';

export default Component.extend({
  // Component logic and properties go here
  actions: {
    // Example action
    handleClick() {
      // Handle click event
    }
  }
});
