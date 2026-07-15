# Clean Architecture, Onion Architecture, Hexagonal Architecture, and Repository Pattern

## Why this matters

Imagine you are building a restaurant.

If you put the stove, the cash register, the dining tables, and the inventory clipboard all in one big room with no walls, anyone can do anything. The chef might handle payments, the waiter might start cooking, and a change to the menu means redesigning the entire building.

Clean Architecture, Onion Architecture, Hexagonal Architecture, and the Repository Pattern are architectural rules that create clear boundaries so your code stays organized, flexible, and easy to maintain as it grows.

---

## 1. What are these architectures?

These three architectures — Clean, Onion, and Hexagonal — are very similar in spirit. They all follow the same core idea:

> Keep your business rules protected from technical details.

### The core idea: layers and circles

Think of your application as a set of nested circles:

```text
+---------------------------------------------+
| OUTER LAYER: UI, Database, Frameworks       |
| +-----------------------------------------+ |
| | MIDDLE LAYER: Use Cases (App Logic)     | |
| | +-------------------------------------+ | |
| | | INNER CORE: Entities (Rules)       | | |
| | +-------------------------------------+ | |
| +-----------------------------------------+ |
+---------------------------------------------+
```

### The layers

- Inner Core (Domain / Entities)
  - The heart of your business rules.
  - Example: "An order must have at least one item" or "A discount cannot exceed 20%".
  - This layer does not care about databases, HTML, or cloud services.

- Middle Layer (Use Cases / Application)
  - Contains the actions or workflows a user can perform.
  - Example: PlaceOrder, CancelSubscription, RegisterUser.

- Outer Layer (Infrastructure / Delivery)
  - The technical tools around your app.
  - Example: web servers, PostgreSQL, MongoDB, Stripe, PayPal, APIs.

### The golden rule

- Dependencies only point inward.
- The core should not know about the database, UI, or framework.
- The database and UI depend on the core, not the other way around.

---

## 2. What is the Repository Pattern?

The Repository Pattern acts as a mediator between your business logic and your storage system.

Instead of putting raw database code directly inside your business rules, you define an interface such as:

```csharp
public interface IUserRepository
{
    User GetById(int id);
    void Save(User user);
}
```

Your business logic simply says:

- "Give me the user with ID 5"
- "Save this user"

It does not care whether the data comes from:

- SQL
- MongoDB
- a text file
- an in-memory test cache

---

## 3. Why do we need these patterns?

Without architecture, applications often become a "Big Ball of Mud".

### Main reasons

- Isolate business logic
  - Protect the rules that make your business unique.

- Make code testable
  - You can test business rules without needing a real database or server.

- Swap technologies more easily
  - Change the database or framework with less pain.

---

## 4. What could happen if we do not use them?

If you build a non-trivial app without clear separation of concerns, problems appear quickly.

### Common problems

- Tightly coupled code
  - Database logic, API calls, and business rules all get mixed together.

- Painful upgrades
  - Switching from SQL to MongoDB or changing frameworks may break a lot of code.

- Slow and fragile testing
  - Tests need real databases and external systems, so they become slow and unreliable.

- High technical debt
  - As the team grows, changes create ripple effects and break other parts of the system.

---

## 5. What happens if we do use them?

When these patterns are applied properly, your application becomes easier to manage.

### Benefits

- Framework independence
  - Your business logic is not locked to one web framework or database.

- Faster unit tests
  - You can test core rules in milliseconds using simple mocks or fakes.

- Future-proof flexibility
  - Changing Stripe to PayPal or moving from SQL to DynamoDB becomes a smaller change.

- Better teamwork
  - Front-end, back-end, and database developers can work with less conflict.

---

## 6. Beginner-friendly summary checklist

| Concept            | Simple meaning                  | Restaurant analogy                        |
| ------------------ | ------------------------------- | ----------------------------------------- |
| Entities (Core)    | The real business rules         | Food recipes and food safety rules        |
| Use Cases          | The steps to complete an action | Take order → notify kitchen → serve       |
| Repository Pattern | A middle layer for data access  | The pantry clerk who provides ingredients |
| Infrastructure     | The actual tools and systems    | Ovens, POS machines, tables               |

---

## 7. What is the difference between Clean Architecture and the Repository Pattern?

These are related, but they are not the same thing.

### Simple explanation

- Clean Architecture is the overall blueprint.
- Repository Pattern is one tool used inside that blueprint.

### Side-by-side comparison

| Topic      | Clean Architecture                      | Repository Pattern                              |
| ---------- | --------------------------------------- | ----------------------------------------------- |
| What it is | An architectural style                  | A design pattern                                |
| Scope      | Entire application structure            | How data access is handled                      |
| Goal       | Separate business rules from technology | Hide storage details from business logic        |
| Analogy    | The floor plan of a hospital            | The system for sending patient files to records |

### How they relate

Clean Architecture says:

- "My business core should not know about SQL, MongoDB, or web frameworks."

Repository Pattern helps achieve that by saying:

- "I will define an interface in the core, and the real database implementation will live outside it."

You can use the Repository Pattern without full Clean Architecture, but in most real-world clean designs, they work very well together.

---

## 8. A quick code mental model

### Without the Repository Pattern

Your business logic directly talks to the database:

```csharp
public class OrderService
{
    public void PlaceOrder(int orderId)
    {
        // Business logic mixed with database code!
        using (var connection = new SqlConnection("..."))
        {
            var sql = "SELECT * FROM Orders WHERE Id = " + orderId;
            // Execute SQL query directly...
        }
    }
}
```

If you change databases or want to test the logic quickly, everything becomes messy.

### With Clean Architecture + Repository Pattern

#### Core layer

```csharp
public interface IOrderRepository
{
    Order GetById(int id);
    void Save(Order order);
}
```

#### Infrastructure layer

```csharp
public class SqlOrderRepository : IOrderRepository
{
    public Order GetById(int id)
    {
        // SQL-specific code happens here
        return new Order();
    }
}
```

#### Application logic

```csharp
public class PlaceOrderUseCase
{
    private readonly IOrderRepository _repository;

    public PlaceOrderUseCase(IOrderRepository repository)
    {
        _repository = repository;
    }

    public void Execute(int orderId)
    {
        var order = _repository.GetById(orderId);
        order.Fulfill();
        _repository.Save(order);
    }
}
```

---

## 9. Final takeaway

- Clean Architecture is the overall philosophy:
  - Keep your business core pure and isolated from outside technology.

- Repository Pattern is a practical tool:
  - Hide database access behind a simple interface so your core does not depend on SQL or ORMs.
