# Title: Adopting Microservices Architecture to the Hotel booking system 

## Context

The hotel booking system was previously built as a monolithic architecture. All functionalities, such as user authentication, room booking, payment processing, and inventory management are tightly coupled within a single codebase. This architecture simplifies development and deployment initially but becomes increasingly complex and difficult to maintain over time as the system grows. To enhance the user experience and provide end-to-end solutions, a new microservice architecture implementation is introduced.

## Decision

We have decided to transition from monolithic architecture to microservices architecture of the system.

## Rationale

Why do we choose this solution?
Hotel booking systems initially use the monolithic architecture design which is the traditional design architecture for a small software application with a small number of users. Using monolithic architecture seemed to be convenient at first as the system was not yet used by many users. As the number of users has increased, our booking system is experiencing high traffic during the seasonal holidays. Many users are facing the problem of not being able to make a reservation. Besides, the software system will be adding additional services, so microservices would be more suitable for this situation. 


## Consequences

Pros – What becomes easier?
- Pros
    * In monolith applications, if one program or service needs to be updated, other parts of the program are required to be recompiled and retested. This might be a difficulty when a new service is added to the system. 
    * As microservices communicate with each other via RESTful APIs. And as long as a microservice exchanges information via this communication pattern, how it is implemented under the covers is of no concern to its consumers 
    * Microservices allow for scaling individual components of a system independently based on demand. During peak traffic times, specific microservices handling critical functions can be scaled up to accommodate the increased load, thereby distributing the traffic load more effectively and reducing the likelihood of website jams.

Cons – What becomes more difficult?
- Cons
    * Increased maintenance cost as the system becomes more complicated compared to monolithic architecture. 
    * There may be a chance of failure during communication between different services. 
    * Adding more services can be painful as they require multiple databases and transactions.


## Sample code

Here are the sample codes for the Hotel Booking System that uses microservices. 

**AuthenticationService.java**
```
public interface AuthenticationService {
    public String authenticateUser(String username, String password);
    public boolean isUserAuthenticated(String token);
    public String logoutUser(String token);
}
```

**BookingService.java**
```
public interface BookingService {
    public String bookRoom(String hotelId, String userId,Booking booking);
    public Booking getBookingById(String bookingId);
    public List<Booking> getAllBooking();
    public String cancelBooking(String bookingId);
    public String completeBooking(String bookingId);
}
```

**PaymentService.java**
```
public interface PaymentService {
    public String makePayment(String userId, Payment payment);
    public Payment getPaymentById(String paymentId);
    public String cancelPayment(String paymentId);
    public String refundPayment(String paymentId);
}
```

**HotelFoodService.java**
```
public interface HotelFoodService {
    public List<FoodItem> getAllFoodItems();
    public FoodItem getFoodItemById(String foodItemId);
    public String orderFood(String userId, String foodItemId, int quantity);
    public String cancelFoodOrder(String orderId);
    public List<String> getAvailableFoodCategories();
    public List<FoodItem> getFoodItemsByCategory(String category);
}
```



