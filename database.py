from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import secrets

db = SQLAlchemy()

class Topic(db.Model):
    """Topic model"""
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    content = db.relationship('Content', back_populates='topic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Topic {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

class APIKey(db.Model):
    """API Key model for Wikipedia access"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), nullable=False, unique=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    requests_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<APIKey {self.name}>'
    
    @staticmethod
    def generate_key():
        """Generate a unique API key"""
        return 'wk_' + secrets.token_urlsafe(32)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'name': self.name,
            'requests_count': self.requests_count,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None
        }

class WikipediaContent(db.Model):
    """Cached Wikipedia content"""
    __tablename__ = 'wikipedia_content'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(255), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(512), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    categories = db.Column(db.Text, nullable=True)  # JSON stored as text
    references = db.Column(db.Text, nullable=True)  # JSON stored as text
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WikipediaContent {self.title}>'
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'topic_name': self.topic_name,
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'summary': self.summary,
            'categories': json.loads(self.categories) if self.categories else [],
            'references': json.loads(self.references) if self.references else [],
            'fetched_at': self.fetched_at.isoformat()
        }

class Content(db.Model):
    """Content model"""
    __tablename__ = 'content'

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    code_examples = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    topic = db.relationship('Topic', back_populates='content')
    downloads = db.relationship('Download', back_populates='content', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Content {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'title': self.title,
            'explanation': self.explanation,
            'code_examples': self.code_examples,
            'created_at': self.created_at.isoformat()
        }

class Download(db.Model):
    """Download tracking model"""
    __tablename__ = 'downloads'

    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    format = db.Column(db.String(10), nullable=False)  # pdf, text, markdown
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_name = db.Column(db.String(255), nullable=False)

    # Relationship
    content = db.relationship('Content', back_populates='downloads')

    def __repr__(self):
        return f'<Download {self.file_name} ({self.format})>'

    def to_dict(self):
        return {
            'id': self.id,
            'content_id': self.content_id,
            'format': self.format,
            'downloaded_at': self.downloaded_at.isoformat(),
            'file_name': self.file_name
        }

def init_db(app):
    """Initialize the database"""
    with app.app_context():
        db.create_all()

def seed_db(app):
    """Seed the database with sample data"""
    with app.app_context():
        # Check if data already exists
        if Topic.query.first() is not None:
            return

        # Create default API key
        default_key = APIKey(
            key=APIKey.generate_key(),
            name='Default API Key',
            is_active=True
        )
        db.session.add(default_key)
        db.session.flush()

        # Java Programming
        java_topic = Topic(
            name='Java Programming',
            description='Learn Java programming from basics to advanced OOP concepts'
        )
        db.session.add(java_topic)
        db.session.flush()

        java_content = Content(
            topic_id=java_topic.id,
            title='Java Programming: Complete Guide',
            explanation="""
Java is a powerful, object-oriented programming language widely used for building scalable applications.

**Key Concepts:**

1. **Object-Oriented Programming (OOP)**: Java is built on OOP principles including encapsulation, inheritance, and polymorphism.

2. **Platform Independence**: Java code is compiled to bytecode and runs on the Java Virtual Machine (JVM), making it platform-independent.

3. **Strong Typing**: Java is strongly typed, which helps catch errors at compile time.

4. **Memory Management**: Automatic garbage collection manages memory, reducing memory leaks.

5. **Collections Framework**: Java provides powerful data structures like ArrayList, HashMap, and HashSet for managing groups of objects.

6. **Exception Handling**: Java's robust exception handling mechanism helps handle errors gracefully.

**Best Practices:**
- Follow naming conventions (camelCase for variables/methods, PascalCase for classes)
- Use access modifiers (public, private, protected) to control visibility
- Write reusable, modular code
- Handle exceptions appropriately
- Use generics for type safety
""",
            code_examples="""
// Example 1: Basic Class Definition
public class Person {
    private String name;
    private int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public void displayInfo() {
        System.out.println("Name: " + name + ", Age: " + age);
    }
}

// Example 2: Using Collections
import java.util.*;

public class CollectionsExample {
    public static void main(String[] args) {
        List<String> fruits = new ArrayList<>();
        fruits.add("Apple");
        fruits.add("Banana");
        fruits.add("Orange");

        for (String fruit : fruits) {
            System.out.println(fruit);
        }
    }
}

// Example 3: Exception Handling
public class ExceptionHandling {
    public static void main(String[] args) {
        try {
            int[] numbers = {1, 2, 3};
            System.out.println(numbers[5]); // This will throw ArrayIndexOutOfBoundsException
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("Array index out of bounds: " + e.getMessage());
        } finally {
            System.out.println("Cleanup code here");
        }
    }
}
"""
        )
        db.session.add(java_content)

        # Python Fundamentals
        python_topic = Topic(
            name='Python Fundamentals',
            description='Master Python basics, functions, and data structures'
        )
        db.session.add(python_topic)
        db.session.flush()

        python_content = Content(
            topic_id=python_topic.id,
            title='Python Fundamentals: A Complete Overview',
            explanation="""
Python is a versatile, easy-to-learn programming language known for its readability and powerful libraries.

**Key Concepts:**

1. **Dynamic Typing**: Variables in Python don't require explicit type declarations.

2. **Indentation-based Syntax**: Python uses indentation to define code blocks, making code more readable.

3. **Functions**: Functions are first-class objects that can be passed as arguments and returned from other functions.

4. **Data Structures**: Python provides built-in data structures like lists, tuples, dictionaries, and sets.

5. **List Comprehensions**: Concise way to create and modify lists.

6. **Modules and Packages**: Python's modular architecture allows you to organize code into reusable modules.

**Key Features:**
- Simple and expressive syntax
- Extensive standard library
- Support for multiple programming paradigms (OOP, functional, procedural)
- Strong community and ecosystem
- Great for web development, data science, and automation
""",
            code_examples="""
# Example 1: Function Definition and Usage
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

result = greet("Alice")
print(result)  # Output: Hello, Alice!

# Example 2: List Comprehension
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers if x % 2 == 0]
print(squares)  # Output: [4, 16]

# Example 3: Working with Dictionaries
student = {
    'name': 'Bob',
    'age': 20,
    'courses': ['Math', 'Science', 'English']
}

for key, value in student.items():
    print(f"{key}: {value}")

# Example 4: Exception Handling
try:
    file = open('data.txt', 'r')
    content = file.read()
except FileNotFoundError:
    print("File not found!")
finally:
    file.close()
"""
        )
        db.session.add(python_content)

        # Web Development
        web_topic = Topic(
            name='Web Development',
            description='Learn HTML, CSS, and JavaScript fundamentals'
        )
        db.session.add(web_topic)
        db.session.flush()

        web_content = Content(
            topic_id=web_topic.id,
            title='Web Development Fundamentals',
            explanation="""
Web development involves creating websites and web applications using HTML, CSS, and JavaScript.

**HTML (Structure):**
- Provides the structure and content of web pages
- Uses semantic tags for better accessibility and SEO
- Forms enable user input and interaction

**CSS (Styling):**
- Controls the visual presentation of HTML elements
- Flexbox and CSS Grid for modern layouts
- Media queries for responsive design
- CSS preprocessors like SASS for advanced styling

**JavaScript (Interactivity):**
- Adds interactivity and dynamic behavior to web pages
- DOM manipulation for runtime changes
- Event handling for user interactions
- Asynchronous programming with Promises and async/await

**Key Concepts:**
- Responsive Design: Websites that work on all device sizes
- Progressive Enhancement: Build a basic experience, enhance with JavaScript
- Web Accessibility: Make websites usable for everyone
- Performance Optimization: Load times and rendering speed
- Security: Protect against XSS, CSRF, and other vulnerabilities
""",
            code_examples="""
<!-- Example 1: Semantic HTML -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width">
    <title>My Website</title>
</head>
<body>
    <header>
        <h1>Welcome</h1>
    </header>
    <main>
        <article>
            <h2>Article Title</h2>
            <p>Article content here...</p>
        </article>
    </main>
</body>
</html>

/* Example 2: Responsive CSS */
.container {
    display: flex;
    justify-content: space-between;
}

@media (max-width: 768px) {
    .container {
        flex-direction: column;
    }
}

// Example 3: JavaScript DOM Manipulation
document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('myButton');
    button.addEventListener('click', function() {
        alert('Button clicked!');
    });
});

// Example 4: Async/Await with Fetch
async function fetchData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.error('Error:', error);
    }
}
"""
        )
        db.session.add(web_content)

        db.session.commit()
        print("Database seeded successfully!")
