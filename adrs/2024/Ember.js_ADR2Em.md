# Architecture Decision Record: Ember .js

## Context
Our mobile application needs to use data from multiple sources at once. 

## Decision
We have decided to use Ember.js to access data across multiple sources for our project.

## Rationale
1.Ember has a fully-featured data access library called Ember Data.
2.Ember Data allows us to access data across multiple sources at once, set up asynchronous relationships, and keep models up-to-date across applications.


## Consequences
Pros:
1.Provides powerful features.
2.Provides conventions for common use cases
3.Manage complex data structures.

Cons:
1.Requires time and practice.
2.Difficult-to-debug problems.
3.Performance issues.


## Sample code
// Example Ember.js
import Component from "@glimmer/component"; 
import { tracked } from "@glimmer/tracking"; 
import fetch from "fetch"; 

export default class ListOfDraftsComponent extends Component { 
   @tracked drafts; 

   constructor() { 
      super(...arguments);

      fetch("/drafts").then((data) => { 
         this.drafts = data;
      });
   } 
}

