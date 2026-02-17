# Title
Choice of Templating Engine

## Context
In order to begin rendering dynamic content in our views, we will need to decide which templating engine to use in our "Hello World!" Rails application.

## Decision
We will use ERB (Embedded Ruby) as our templating engine for rendering dynamic content in our views

## Rationale
ERB is the default templating engine in Ruby on Rails. It provides a straightforward method for embedding Ruby code, which makes it a natural fit for embedding Ruby within our HTML templates. As our application is quite simple and does not require any advanced templating features, ERB is a perfect fit for our use case, and its use keeps our codebase lightweight and easy to understand.

## Consequences
Pros
-ERB is easy to learn and use, especially for developers familiar with HTML and Ruby.
-No additional setup or configuration is required, as ERB comes built-in with Rails.
-Integrates seamlessly with Rails helpers and conventions.

Cons
-ERB can become verbose and less maintainable for complex views with a lot of logic embedded within them.
-Limited templating features compared to more modern templating engines like Haml or Slim.

## Sample code
<!-- app/views/pages/home.html.erb -->
<!DOCTYPE html>
<html>
<head>
  <title>Hello World</title>
</head>
<body>
  <h1>Hello, <%= @name %>!</h1> 
</body>
</html>

The code snippet is an HTML file using Embedded Ruby (ERB) syntax within a Ruby on Rails application. ERB is a templating engine that allows developers to embed Ruby code within HTML files to generate dynamic content.

The file is located at 'app/views/pages/home.html.erb' , which is a view file in a Ruby on Rails application. Views are responsible for rendering HTML content to be sent back to the client's browser.

This HTML file contains standard HTML markup, including a doctype declaration, an HTML element, a head section, and a body section.

Within the body section, there is a '<h1>' element that contains the text "Hello, <%= @name %>!". The <%= %> syntax is ERB syntax, which allows Ruby code to be embedded within HTML. In this case, '@name' is a variable that will be replaced with its value when the view is rendered.

The '@name' variable is expected to be provided by the controller when rendering this view. For example, if the controller sets @name = "Katy", the resulting HTML output will be "Hello, Katy!".