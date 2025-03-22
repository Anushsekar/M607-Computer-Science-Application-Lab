import sqlite3
import bcrypt
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='ecommerce.db'):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        """Create all necessary database tables."""
        conn = self.connect()
        cursor = conn.cursor()
        
        #Just in case you need to drop the tables and recreate them with the new schema unco
        # cursor.execute("DROP TABLE IF EXISTS order_items")
        # cursor.execute("DROP TABLE IF EXISTS orders")
        # cursor.execute("DROP TABLE IF EXISTS cart")
        # cursor.execute("DROP TABLE IF EXISTS products")
        # cursor.execute("DROP TABLE IF EXISTS users")
        
        # Enhanced users table with more fields
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          username TEXT UNIQUE NOT NULL,
                          password TEXT NOT NULL,
                          email TEXT UNIQUE,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          last_login TIMESTAMP)''')

        # Enhanced products table with more details
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          price REAL NOT NULL,
                          category TEXT NOT NULL,
                          description TEXT,
                          stock INTEGER DEFAULT 0,
                          image_url TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        # Enhanced cart table with quantity
        cursor.execute('''CREATE TABLE IF NOT EXISTS cart (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          product_id INTEGER NOT NULL,
                          quantity INTEGER DEFAULT 1,
                          added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (user_id) REFERENCES users(id),
                          FOREIGN KEY (product_id) REFERENCES products(id))''')

        # New table for order history
        cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          total_amount REAL NOT NULL,
                          status TEXT DEFAULT 'pending',
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (user_id) REFERENCES users(id))''')

        # New table for order items
        cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          order_id INTEGER NOT NULL,
                          product_id INTEGER NOT NULL,
                          quantity INTEGER NOT NULL,
                          price_at_time REAL NOT NULL,
                          FOREIGN KEY (order_id) REFERENCES orders(id),
                          FOREIGN KEY (product_id) REFERENCES products(id))''')

        conn.commit()
        conn.close()

    def register_user(self, username, password, email=None):
        """Register a new user with enhanced security and validation."""
        try:
            # Ensure password is encoded before hashing
            if isinstance(password, str):
                password = password.encode('utf-8')
            
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password, salt)
            
            # Store the hashed password as a string
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, email, created_at) VALUES (?, ?, ?, ?)",
                    (username, hashed_password.decode('utf-8'), email, datetime.now())
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error registering user: {e}")
            return False

    def authenticate_user(self, username, password):
        """Authenticate user and update last login timestamp."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, password, username = 'admin' as is_admin 
                    FROM users WHERE username = ?
                """, (username,))
                result = cursor.fetchone()
                
                if result:
                    user_id, stored_password, is_admin = result
                    # Ensure password is in bytes for comparison
                    if isinstance(password, str):
                        password = password.encode('utf-8')
                    if isinstance(stored_password, str):
                        stored_password = stored_password.encode('utf-8')
                    
                    if bcrypt.checkpw(password, stored_password):
                        # Update last login timestamp
                        cursor.execute(
                            "UPDATE users SET last_login = ? WHERE id = ?",
                            (datetime.now(), user_id)
                        )
                        conn.commit()
                        return {"id": user_id, "is_admin": bool(is_admin)}
                return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None

    def get_user(self, user_id):
        """Get user details with enhanced information."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, username, email, created_at, last_login 
                    FROM users WHERE id = ?
                """, (user_id,))
                user = cursor.fetchone()
                if user:
                    return {
                        "id": user[0],
                        "username": user[1],
                        "email": user[2],
                        "created_at": user[3],
                        "last_login": user[4]
                    }
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def get_all_products(self, include_out_of_stock=False):
        """Get all products with enhanced information."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                if include_out_of_stock:
                    cursor.execute("""
                        SELECT id, name, price, category, description, stock, image_url 
                        FROM products
                    """)
                else:
                    cursor.execute("""
                        SELECT id, name, price, category, description, stock, image_url 
                        FROM products
                        WHERE stock > 0
                    """)
                products = cursor.fetchall()
                return [{
                    "id": p[0],
                    "name": p[1],
                    "price": p[2],
                    "category": p[3],
                    "description": p[4],
                    "stock": p[5],
                    "image_url": p[6]
                } for p in products]
        except Exception as e:
            print(f"Error getting products: {e}")
            return []

    def get_cart_items(self, user_id):
        """Get cart items with enhanced information."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT c.id, p.name, p.price, p.image_url, c.quantity, p.stock
                    FROM cart c
                    JOIN products p ON c.product_id = p.id
                    WHERE c.user_id = ?
                ''', (user_id,))
                return [{
                    'id': item[0],
                    'name': item[1],
                    'price': item[2],
                    'image_url': item[3],
                    'quantity': item[4],
                    'stock': item[5],
                    'total': item[2] * item[4]
                } for item in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting cart items: {e}")
            return []

    def add_to_cart(self, user_id, product_id, quantity=1):
        """Add or update product quantity in cart."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                # Check if product already in cart
                cursor.execute("""
                    SELECT id, quantity FROM cart 
                    WHERE user_id = ? AND product_id = ?
                """, (user_id, product_id))
                existing = cursor.fetchone()

                if existing:
                    # Update quantity
                    new_quantity = existing[1] + quantity
                    cursor.execute("""
                        UPDATE cart SET quantity = ? 
                        WHERE id = ?
                    """, (new_quantity, existing[0]))
                else:
                    # Add new item
                    cursor.execute("""
                        INSERT INTO cart (user_id, product_id, quantity) 
                        VALUES (?, ?, ?)
                    """, (user_id, product_id, quantity))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding to cart: {e}")
            return False

    def insert_products(self):
        """Insert sample products with enhanced information."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM products")
                if cursor.fetchone()[0] == 0:
                    products = [
                        ('Laptop Pro', 1299.99, 'Electronics', 
                         'High-performance laptop with latest specs', 50, 'laptop.jpg'),
                        ('Smartphone X', 799.99, 'Electronics',
                         'Latest smartphone with advanced features', 100, 'phone.jpg'),
                        ('Wireless Headphones', 199.99, 'Accessories',
                         'Premium wireless headphones with noise cancellation', 75, 'headphones.jpg'),
                        ('Smart Watch', 299.99, 'Accessories',
                         'Feature-rich smartwatch with health monitoring', 60, 'smartwatch.jpg')
                    ]
                    cursor.executemany("""
                        INSERT INTO products (name, price, category, description, stock, image_url)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, products)
                    conn.commit()
        except Exception as e:
            print(f"Error inserting products: {e}")

    def update_cart_quantity(self, cart_id, quantity):
        """Update quantity of item in cart."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE cart SET quantity = ? WHERE id = ?", (quantity, cart_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating cart quantity: {e}")
            return False

    def create_order(self, user_id, cart_items):
        """Create a new order from cart items."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                # Calculate total amount
                total_amount = sum(item['total'] for item in cart_items)
                
                # Create order
                cursor.execute("""
                    INSERT INTO orders (user_id, total_amount, status)
                    VALUES (?, ?, 'pending')
                """, (user_id, total_amount))
                order_id = cursor.lastrowid

                # Add order items
                for item in cart_items:
                    cursor.execute("""
                        INSERT INTO order_items (order_id, product_id, quantity, price_at_time)
                        VALUES (?, ?, ?, ?)
                    """, (order_id, item['id'], item['quantity'], item['price']))

                # Clear user's cart
                cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
                conn.commit()
                return order_id
        except Exception as e:
            print(f"Error creating order: {e}")
            return None

    def remove_from_cart(self, cart_id, user_id):
        """Remove item from cart."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                # Verify the cart item belongs to the user before deleting
                cursor.execute("""
                    DELETE FROM cart 
                    WHERE id = ? AND user_id = ?
                """, (cart_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing from cart: {e}")
            return False

    def add_product(self, name, price, category, description, stock, image_url):
        """Add a new product."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO products (name, price, category, description, stock, image_url)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, price, category, description, stock, image_url))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding product: {e}")
            return False

    def update_product(self, product_id, name, price, category, description, stock, image_url=None):
        """Update an existing product."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                if image_url:
                    cursor.execute("""
                        UPDATE products 
                        SET name = ?, price = ?, category = ?, description = ?, 
                            stock = ?, image_url = ?
                        WHERE id = ?
                    """, (name, price, category, description, stock, image_url, product_id))
                else:
                    cursor.execute("""
                        UPDATE products 
                        SET name = ?, price = ?, category = ?, description = ?, 
                            stock = ?
                        WHERE id = ?
                    """, (name, price, category, description, stock, product_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating product: {e}")
            return False

    def delete_product(self, product_id):
        """Delete a product."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                # First, check if the product is in any carts
                cursor.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))
                # Then delete the product
                cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
