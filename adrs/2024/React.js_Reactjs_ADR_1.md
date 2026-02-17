## Title
Implementation of component-based architecture for our application

## Context
One of the issues for applying component-based architecture is the complex components with complicated interfaces as a mobile application project grows. 

## Decision
To enforce the use of component-based architecture for better code organization and code reusability. 

## Rationale
Since we are developing a mobile application with interactive user interfaces, we need a well maintained architecture. Therefore, to prevent abundant components and messy code, we have decided to apply component-based architecture, in which each component encapsulates a specific piece of UI, functionality, or behavior.

## Consequences
Pros
Improve codebase maintainability for developers. The modulated components are without a doubt, easier to be fixed. Therefore, the risk of messing the code up or developing a bug by accident is reduced as well.

Cons
There are numerous libraries and tools available in the React ecosystem for a variety of uses. But occasionally, this fragmentation causes indecision or makes it difficult to select the appropriate tools for a given task.

## Sample code
//components/Header.js
const Header = () => {
  return (
    <header className="header">
      <h1>Header Component</h1>
    </header>
  );
};
export default Header;

//components/Footer.js
const Footer = () => {
  return (
    <footer className="footer">
      <p>Footer Component</p>
    </footer>
  );
};
export default Footer