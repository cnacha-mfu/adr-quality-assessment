# Title
Using ActiveRecord for Database Management

## Context
We need to choose an ORM (Object-Relational Mapping) library for managing database interactions within our Ruby on Rails application.

## Decision
We will use ActiveRecord, which is Ruby on Rails default ORM, for managing database interactions.

## Rationale
-Integration with Rails: ActiveRecord is tightly integrated with Ruby on Rails and is the default library for managing the database in a Rails application. This tight integration reduces boilerplate code and makes development faster and simpler.
-Active Record pattern: ActiveRecord follows the Active Record pattern, which means it maps database records to objects in the application. This abstraction makes it easy to work with database data using familiar object-oriented programming techniques.
-Migration support: ActiveRecord comes with built-in support for database migrations, allowing developers to manage changes to the database schema over time in a version-controlled manner.

## Consequences
Pros
-Simplified database interactions through object-oriented abstractions.
-Comes with built-in support for database migrations.
-Easy integration with other parts of the Rails framework.

Cons
-Tight coupling with Rails may limit flexibility for using other ORM libraries.
-Performance overhead compared to more lightweight ORM solutions for certain use cases.

## Sample code

# app/models/post.rb
class Post < ApplicationRecord
  validates :title, presence: true
  validates :body, presence: true
end

The code snippet defines a Ruby class named Post, which inherits from ApplicationRecord. In Ruby on Rails, ApplicationRecord is a special class that serves as the base class for all models in the application.

Inside the Post class, there are two validates statements:

validates :title, presence: true: This line specifies that the title attribute of a Post instance must be present (i.e., not blank) in order for the record to be considered valid. If a Post instance is created or updated without a title, it will fail validation and not be saved to the database.

validates :body, presence: true: Similarly, this line specifies that the body attribute of a Post instance must be present for the record to be valid.