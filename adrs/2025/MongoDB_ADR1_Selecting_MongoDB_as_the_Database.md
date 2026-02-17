ADR1: Selecting MongoDB as the Database 
 
Title 
Selecting MongoDB as the Database 
 
Context 
We need to select a database for our application, which requires efficient handling of 
semi-structured data, scalability, and flexibility for future feature expansions. The system 
deals with frequently changing data structures and high read/write operations. 
 
Decision 
After evaluating various database options, we have decided to use MongoDB due to its 
schema flexibility, scalability, and high read/write performance. Given our application's 
requirements, handling semi-structured data, frequent updates, and future scalability. 
MongoDB provides the best balance of flexibility, performance, and ease of 
development. 
 
Rationale 
●​ Schema Flexibility: MongoDB’s document-based model supports dynamic and 
evolving data structures, making it ideal for applications with changing 
requirements. 
●​ Scalability: MongoDB provides horizontal scaling via sharding, ensuring efficient 
handling of large datasets. 
●​ Performance: Optimized for high-speed read/write operations, making it suitable 
for frequent updates and fast queries. 
●​ Ease of Development: The JSON-like document format integrates seamlessly 
with JavaScript/Node.js and modern web frameworks. 
●​ Rich Querying Capabilities: Supports aggregation pipelines, text search, and 
geospatial queries for advanced data retrieval. 
●​ Cloud Support: MongoDB Atlas offers a fully managed cloud solution, reducing 
infrastructure overhead. 
 
Consequences 
Pros: 
●​ Flexible Schema: Allows schema-less data storage, making it easy to evolve 
data structures over time. 
●​ Scalability: Designed for horizontal scaling, efficiently distributing data across 
multiple servers. 
●​ Indexing for Performance: Proper indexing significantly improves query speed. 
 

Cons: 
●​ Data Consistency Risks: The lack of strict schemas can lead to inconsistent data 
if proper validation (e.g., Mongoose, application-level validation) is not enforced. 
●​ Complex Queries: Unlike SQL databases, MongoDB does not support joins 
natively, requiring manual aggregation for complex relationships. 
●​ Indexing Overhead: Too many indexes can slow down write operations due to 
frequent updates. 
 
Sample Code 
Setting Up MongoDB in Spring Boot 
1.​ Add Dependency 
<dependency>​
    <groupId>org.springframework.boot</groupId>​
    <artifactId>spring-boot-starter-data-mongodb</artifactId>​
</dependency> 
 
2.​ Configure Connection (application.properties) 
spring.data.mongodb.uri=mongodb://localhost:27017/mydatabase 
 
3.​ Define a Flexible Schema 
import org.springframework.data.annotation.Id;​
import org.springframework.data.mongodb.core.mapping.Document;​
import java.util.List;​
​
@Document(collection = "users")​
public class User {​
    @Id​
    private String id;​
    private String username;​
    private String email;​
    private Profile profile;​
​
    public User(String username, String email, Profile profile) {​
        this.username = username;​
        this.email = email;​
        this.profile = profile;​
    }​
​

    // Getters and Setters...​
​
    public static class Profile {​
        private Integer age;​
        private List<String> interests;​
​
        public Profile(Integer age, List<String> interests) {​
            this.age = age;​
            this.interests = interests;​
        }​
​
        // Getters and Setters...​
    }​
} 
 
4.​ Create a Repository for CRUD Operations 
import org.springframework.data.mongodb.repository.MongoRepository;​
​
public interface UserRepository extends MongoRepository<User, String> 
{​
    User findByUsername(String username);​
} 
 
5.​ Implement User Service for CRUD Operations 
import org.springframework.beans.factory.annotation.Autowired;​
import org.springframework.stereotype.Service;​
import java.util.List;​
​
@Service​
public class UserService {​
​
    @Autowired​
    private UserRepository userRepository;​
​
    // Create (Insert a User)​
    public void createUser(String username, String email, Integer 
age, List<String> interests) {​
        User.Profile profile = new User.Profile(age, interests);​

        User user = new User(username, email, profile);​
        userRepository.save(user);​
        System.out.println("User Created: " + username);​
    }​
​
    // Read (Find a User)​
    public User getUserByUsername(String username) {​
        return userRepository.findByUsername(username);​
    }​
​
    // Update (Modify User Data)​
    public void updateUserAge(String username, Integer newAge) {​
        User user = userRepository.findByUsername(username);​
        if (user != null) {​
            user.getProfile().setAge(newAge);​
            userRepository.save(user);​
            System.out.println("User Updated: " + username);​
        }​
    }​
​
    // Delete (Remove a User)​
    public void deleteUser(String username) {​
        User user = userRepository.findByUsername(username);​
        if (user != null) {​
            userRepository.delete(user);​
            System.out.println("User Deleted: " + username);​
        }​
    }​
}
