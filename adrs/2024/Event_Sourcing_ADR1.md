# Title
Assuming that your website is a web blog service.
## Context
What is the issue that we're seeing that is motivating this decision or change?

-If one day we want to add a feature that allows users to view the history of their profile name changes or see a detailed history of what they have read, with specific timestamps, it's something we currently have no way of knowing.
## Decision
What is the solution that we're proposing and/or doing?

-Therefore, we use the event sourcing architecture to address the issue.
## Rationale
Why do we choose this solution?

-You can examine all the data that occurs and answer questions about who did what and when.
## Consequences
Pros – What becomes easier?

-Enable the examination of the entire history of changes in the past data.

Cons – What becomes more difficult?

-The code becomes more complex, and it requires integrating with a database to store additional events separately.
## Sample code
Give some sample code related to this decision.

``` java
addProfileName(String Jay, Datetime date)
{
   eventAddProfileName(Jay,date);
   addProfileNameToDB(Jay,date);
}
```
// On the 4th of March 2019, at 15:04:23, you named your profile "Jay" right after completing the registration.

```java
updateProfileName(String Mice, Datetime date)
{
   eventAddProfileName(Mice,date);
   updateProfileNameToDB(Mice,date);
}
```
// On the 19th of April 2019, at 08:49:01, you changed your profile name from "Jay" to "Mice."

```java
updateProfileName(String JayMice, Datetime date)
{
   eventAddProfileName(JayMice,date);
   updateProfileNameToDB(JayMice,date);
}
```
// On the 31st of May 2019, at 22:22:18, you changed your profile name from "Mice" to "JayMice."


//From the example, naming the profile "Jay," then overwriting it with "Mice," and subsequently overwriting it again with "JayMice," you can observe that each occurrence of adding or updating the profile name is associated with a specific timestamp. In reality, each update is not a modification but an addition of an event, recorded in the database with a timestamp reflecting the time of the update.