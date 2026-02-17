# Architecture Decision Record: Angular 
## Context
- Our web application which is client-based requires the two-way data binding and the selection of a UI framework to be built.

## Decision
- We have decided to use Angular as the front-end framework for our web application because of two-way data binding. 

## Rationale
1. Angular provides two-way data binding, which means that changes to the model (data) automatically reflect in the view (UI), and vice versa. This simplifies the development process and reduces the amount of boilerplate code needed to synchronize the model and the view. 
2. It also provides built-in UI component which is needed.


## Consequences
- Pros:
1.  Angular's two-way data binding and built-in UI components reduce development time and effort.
2. Maintainability and consistency of the application, making it easier to add new features and maintain existing ones.
3. Angular being maintained by Google provides confidence in its stability, updates, and long-term support.

- Cons:
1. Angular has a relatively steep learning curve.
2. The inclusion of Angular's framework and built-in features may result in larger bundle sizes.

## Sample code

import { Component } from '@angular/core';

@Component({
  selector: 'app-example',
  template: `
    <h1>{{ title }}</h1>
    <input [(ngModel)]="name" placeholder="Enter your name">
    <button (click)="greet()">Greet</button>
    <p>{{ greeting }}</p>
  `
})
export class ExampleComponent {
  title = 'Two-Way Data Binding Example';
  name: string = '';
  greeting: string = '';

  greet() {
    this.greeting = `Hello, ${this.name}!`;
  }
}