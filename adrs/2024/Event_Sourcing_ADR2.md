# Title
Tracking the history and balance of a bank.
## Context
What is the issue that we're seeing that is motivating this decision or change?

-Financial statements are crucial pieces of information. If we need to maintain clear financial data and fail to record it, it could lead to potential fraud or significant financial losses.
## Decision
What is the solution that we're proposing and/or doing?

-Therefore, we use the event sourcing architecture to address the problem and store additional data separately to enhance accuracy and precision.
## Rationale
Why do we choose this solution?

-Because we can track financial history accurately, including numerical data and timestamps, ensuring precision and accuracy.
## Consequences
Pros – What becomes easier?

-Using event sourcing allows for the ability to audit and examine the complete history of changes within an account, providing a comprehensive record of all past modifications.

Cons – What becomes more difficult?

-The code becomes more complex and challenging based on how it is used and the design choices made by the developer. Managing events, recording data, retrieving information, and maintaining data accuracy throughout the system all require careful consideration.
## Sample code
Give some sample code related to this decision.

``` java
updateMoneyStatement(String Gon, Datetime date,Int money=500,000)
{
   eventAddMoneyStatement(Gon,date,money=500,000);
   updateMoneyStatementToDB(Gon,date,money=500,000);
}
```
// On the 7th of March 2020, at 15:00:59, you received 500,000 baht in your Gon account, shortly after completing the registration.

```java
updateMoneyStatement(String Gon, Datetime date,Int money=480,000)
{
   eventAddMoneyStatement(Gon,date,money=480,000);
   updateMoneyStatementToDB(Gon,date,money=480,000);
}
```
// On the 20th of April 2020, at 10:44:09, you withdrew 20,000 baht from your Gon account, leaving a balance of 480,000 baht.

```java
updateMoneyStatement(String Gon, Datetime date,Int money=510,000)
{
   eventAddMoneyStatement(Gon,date,money=510,000);
   updateMoneyStatementToDB(Gon,date,money=510,000);
}
```
// On the 31st of May 2020, at 11:54:03, you received 30,000 baht in your Gon account, and the remaining balance is 510,000 baht.

//From the example where Gon received 500,000 baht, then overwrote the old amount with 480,000, and subsequently overwrote it again with 510,000, notice that each occurrence of `updateMoneyStatement` is associated with a timestamp for every event that takes place. In reality, each update is not a modification of an event but an addition of a new event recorded in the database with a timestamp reflecting the time of the update.