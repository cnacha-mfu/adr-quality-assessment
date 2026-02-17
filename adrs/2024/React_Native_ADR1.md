# Title
-Build Mobile Application 

## Context
What is the issue that we're seeing that is motivating this decision or change?
-the current mobile application is experiencing performance issues such as slow loading times, unresponsive UI, or high resource consumption, it may be motivating the decision to rebuild the application using a different technology stack that offers better performance.

## Decision
What is the solution that we're proposing and/or doing?
-Use React Native for building mobile applications.

## Rationale
Why do we choose this solution?
-Hot Reloading: React Native supports hot reloading, which allows developers to see the changes they make in real-time without restarting the application. This feature speeds up the development process and facilitates rapid iteration.

## Consequences
Pros – What becomes easier?
-easier testing as developers can quickly test changes and see their effects without disrupting the testing process.
Cons – What becomes more difficult?
-Continuous reloading during development may impact performance, especially on slower devices or when dealing with resource-intensive applications. Developers need to be mindful of performance issues and optimize their code accordingly.

## Sample code
Give some sample code related to this decision.
import React, { useState } from 'react';
import { View, Text, Button } from 'react-native';

// Functional component for the app
const App = () => {
  // State variable to track the visibility of the text component
  const [isVisible, setIsVisible] = useState(true);

  // Function to toggle the visibility of the text component
  const toggleVisibility = () => {
    setIsVisible(!isVisible);
  };

  // JSX to render the app UI
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      {/* Button to toggle visibility */}
      <Button title={isVisible ? 'Hide Text' : 'Show Text'} onPress={toggleVisibility} />
      {/* Conditional rendering of the text component */}
      {isVisible && <Text style={{ marginTop: 20 }}>Hello, world!</Text>}
    </View>
  );
};

export default App;