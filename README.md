# M607-Computer-Science-Application-Lab
Ecommerce Project

# MyStore - E-commerce Application

MyStore is a modern e-commerce web application built with Flask, featuring a clean and intuitive user interface. The application allows users to browse products, add items to their cart, and complete purchases. It also includes an admin dashboard for product management.

## Features

### User Interface
- Modern and responsive design
- Mobile-friendly interface
- Category-based product filtering
- Search functionality with real-time results
- Toast notifications for user feedback
- Dropdown menus for user profile and navigation
- Shopping cart icon with quantity indicator

### User Authentication
- User registration with email verification
- Secure login system
- Password hashing using bcrypt
- Session management
- Profile management
- Logout functionality

### Product Management
- Product browsing with grid layout
- Product categories and filtering
- Product search functionality
- Detailed product information display
- Stock management
- Product images with thumbnails
- Price formatting and display

### Shopping Cart
- Add products to cart with quantity selection
- Real-time cart updates
- Cart item quantity modification
- Remove items from cart
- Cart total calculation
- Empty cart handling
- Cart persistence across sessions

### Order Processing
- Secure checkout process
- Order confirmation page
- Order history tracking
- Order status updates
- Order number generation
- Order summary display

### Admin Dashboard
- Product management (add/edit/delete)
- Stock management
- Category management
- Image upload functionality
- Admin-only access control
- Product table view
- Bulk product operations

### Security Features
- Password hashing
- Session management
- Input validation
- Secure file upload handling
- Admin access control
- XSS protection
- CSRF protection

### Database Features
- SQLite database integration
- Automatic database creation
- Efficient data queries
- Transaction management
- Data integrity checks

### Additional Features
- Responsive navigation bar
- User profile dropdown
- Category filtering system
- Product image handling
- Error handling and user feedback
- Loading states and animations
- Form validation
- Mobile menu toggle
- Search bar with suggestions

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mystore
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Project Structure

```
mystore/
├── app.py              # Main application file
├── database_manager.py # Database operations
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── script.js
│   └── images/
├── templates/
│   ├── index.html
│   ├── cart.html
│   ├── admin.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   └── order_confirmation.html
└── ecommerce.db       # SQLite database
```

## Database Setup

The application uses SQLite as its database. The database will be automatically created when you run the application for the first time. The database includes the following tables:

- users: Store user information
- products: Store product details
- cart: Manage shopping cart items
- orders: Track user orders
- order_items: Store individual items in orders

## Running the Application

1. Ensure your virtual environment is activated
2. Run the Flask application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

## Admin Access

To access the admin dashboard:
1. Register a new user with the username "admin"
2. Log in with the admin credentials
3. Navigate to `/admin` to access the admin dashboard

## Key Features Explained

### User Authentication
- Users can register with username, email, and password
- Passwords are securely hashed using bcrypt
- Session management for logged-in users

### Product Management
- Admin can add, edit, and delete products
- Product images are stored in the static/images directory
- Products can be categorized and filtered

### Shopping Cart
- Users can add products to their cart
- Quantity selection for each product
- Real-time cart updates
- Remove items from cart

### Order Processing
- Secure checkout process
- Order confirmation page
- Order history tracking

## Security Features

- Password hashing using bcrypt
- Session management
- Input validation
- Secure file upload handling
- Admin access control

## Customization

### Styling
- The application uses custom CSS in `static/css/styles.css`
- Modern and responsive design
- Mobile-friendly interface

### JavaScript Functionality
- Client-side validation
- Dynamic cart updates
- Toast notifications
- Search functionality

## Troubleshooting

1. Database Issues
   - Ensure the application has write permissions in the project directory
   - Check if the database file is not locked by another process

2. Image Upload Issues
   - Verify the static/images directory exists and has proper permissions
   - Check if the uploaded file is in an allowed format (png, jpg, jpeg, gif)

3. Login Problems
   - Clear browser cookies and cache
   - Ensure the correct username and password are used
   - Check if the database connection is working

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the maintainers. 
