# Architecture Decision Record: Angular
## Context
- Our web application which is client-based requires dependencies injection and the selection of a UI framework to be built.

## Decision
- We have decided to use Angular as the front-end framework for our web application because of dependency injection. 

## Rationale
1. We choose angular because Angular provides dependency injection, which can helps us to improve the modularity and testability of our codebase.
2. It allows us to inject the same service instande into multiple components or service throughout our application. This promotes code reuse and share common functionality across different parts of the application without duplicating code.

## Consequences
- Pros:
1.  Components become more modular and easier to maintain because they are no longer responsible for creating their own service dependencies and it also reduces coupling between components.
2. With dependencies inhected from the outside, it beecomes easier to mock dependencies during unit testing.

- Cons:
1. Angular has a relatively steep learning curve.
2. The inclusion of Angular's framework and built-in features may result in larger bundle sizes.

## Sample code
// data.service.ts

import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class DataService {

  constructor() { }

  getData(): string {
    return 'Some data from the service';
  }
}

// data.component.ts

import { Component, OnInit } from '@angular/core';
import { DataService } from './data.service';

@Component({
  selector: 'app-data',
  template: `
    <div>
      <p>{{ data }}</p>
    </div>
  `,
  styleUrls: ['./data.component.css']
})
export class DataComponent implements OnInit {
  data: string;

  constructor(private dataService: DataService) { }

  ngOnInit(): void {
    this.data = this.dataService.getData();
  }
}

