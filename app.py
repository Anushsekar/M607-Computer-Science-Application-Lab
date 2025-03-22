from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from database_manager import DatabaseManager
from werkzeug.utils import secure_filename

# Flask App Setup with enhanced security
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24).hex())
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes session timeout

# Add these constants after app setup
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Database Manager
db = DatabaseManager()

@app.before_request
def before_request():
    """Ensure database connection and session handling."""
    if 'user_id' in session and request.endpoint not in ['static', 'login', 'register']:
        session.permanent = True  # Use permanent session

@app.route('/')
def home():
    """Home page with product listing and category filtering."""
    user_id = session.get('user_id')
    category = request.args.get('category')
    products = db.get_all_products()
    
    if category:
        products = [p for p in products if p['category'].lower() == category.lower()]
    
    return render_template('index.html', 
                         products=products,
                         user_id=user_id,
                         categories=set(p['category'] for p in products))

@app.route('/cart')
def cart():
    """Shopping cart page with enhanced features."""
    if 'user_id' not in session:
        flash("Please login to view your cart.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart_items = db.get_cart_items(user_id)
    total_price = sum(item['total'] for item in cart_items)
    
    return render_template('cart.html',
                         cart_items=cart_items,
                         total_price=total_price,
                         user_id=user_id)

@app.route('/cart/update/<int:cart_id>', methods=['POST'])
def update_cart(cart_id):
    """Update cart item quantity."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})

    try:
        quantity = int(request.form.get('quantity', 1))
        if quantity < 1:
            return jsonify({'success': False, 'message': 'Invalid quantity'})

        if db.update_cart_quantity(cart_id, quantity):
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Failed to update cart'})
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid quantity value'})

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add product to cart with quantity support."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login to add items to cart.'})

    try:
        quantity = int(request.form.get('quantity', 1))
        if quantity < 1:
            return jsonify({'success': False, 'message': 'Invalid quantity.'})
            
        if db.add_to_cart(session['user_id'], product_id, quantity):
            return jsonify({'success': True, 'message': 'Item added to cart successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add item to cart.'})
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid quantity value.'})

@app.route('/profile')
def profile():
    """Enhanced user profile page."""
    if 'user_id' not in session:
        flash("Please login to view your profile.", "warning")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = db.get_user(user_id)
    if not user:
        session.pop('user_id', None)
        flash("User session expired. Please login again.", "warning")
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Enhanced login with admin support."""
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash("Please provide both username and password.", "error")
            return render_template('login.html')

        try:
            user = db.authenticate_user(username, password)
            if user:
                session['user_id'] = user['id']
                session['is_admin'] = user.get('is_admin', False)
                session.permanent = True
                flash("Welcome back!", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid username or password.", "error")
        except Exception as e:
            print(f"Login error: {e}")
            flash("An error occurred during login. Please try again.", "error")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Enhanced registration with validation."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        if not username or not password:
            flash("Please provide both username and password.", "error")
            return render_template('register.html')

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template('register.html')

        if db.register_user(username, password, email):
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        
        flash("Username already exists.", "error")
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Secure logout."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('home'))

@app.route('/checkout', methods=['POST'])
def checkout():
    """Process checkout and create order."""
    if 'user_id' not in session:
        flash("Please login to checkout.", "warning")
        return redirect(url_for('login'))

    cart_items = db.get_cart_items(session['user_id'])
    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('cart'))

    order_id = db.create_order(session['user_id'], cart_items)
    if order_id:
        flash("Order placed successfully!", "success")
        return redirect(url_for('order_confirmation', order_id=order_id))
    
    flash("Failed to process order. Please try again.", "error")
    return redirect(url_for('cart'))

@app.route('/order/confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Order confirmation page."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('order_confirmation.html', order_id=order_id)

@app.route('/cart/remove/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    """Remove item from cart."""
    if 'user_id' not in session:
        flash("Please login to modify your cart.", "warning")
        return redirect(url_for('login'))

    try:
        if db.remove_from_cart(cart_id, session['user_id']):
            flash("Item removed from cart successfully!", "success")
        else:
            flash("Failed to remove item from cart.", "error")
    except Exception as e:
        flash(f"Error removing item from cart: {str(e)}", "error")
    
    return redirect(url_for('cart'))

@app.route('/admin')
def admin():
    """Admin dashboard for product management."""
    if not is_admin():
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for('home'))
    
    products = db.get_all_products(include_out_of_stock=True)
    return render_template('admin.html', products=products)

@app.route('/admin/add', methods=['POST'])
def admin_add_product():
    """Add a new product."""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        name = request.form.get('name')
        price = float(request.form.get('price'))
        category = request.form.get('category')
        description = request.form.get('description')
        stock = int(request.form.get('stock'))
        image = request.files.get('image')

        if not all([name, price, category, description, stock, image]):
            flash("All fields are required.", "error")
            return redirect(url_for('admin'))

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            if db.add_product(name, price, category, description, stock, filename):
                flash("Product added successfully!", "success")
            else:
                flash("Failed to add product.", "error")
        else:
            flash("Invalid image format. Allowed formats: png, jpg, jpeg, gif", "error")
            
    except Exception as e:
        flash(f"Error adding product: {str(e)}", "error")
    
    return redirect(url_for('admin'))

@app.route('/admin/edit/<int:product_id>', methods=['POST'])
def admin_edit_product(product_id):
    """Edit an existing product."""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        name = request.form.get('name')
        price = float(request.form.get('price'))
        category = request.form.get('category')
        description = request.form.get('description')
        stock = int(request.form.get('stock'))
        image = request.files.get('image')

        if not all([name, price, category, description, stock]):
            flash("All fields except image are required.", "error")
            return redirect(url_for('admin'))

        image_filename = None
        if image and image.filename:
            if allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
            else:
                flash("Invalid image format. Allowed formats: png, jpg, jpeg, gif", "error")
                return redirect(url_for('admin'))

        if db.update_product(product_id, name, price, category, description, stock, image_filename):
            flash("Product updated successfully!", "success")
        else:
            flash("Failed to update product.", "error")

    except Exception as e:
        flash(f"Error updating product: {str(e)}", "error")
    
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    """Delete a product."""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        if db.delete_product(product_id):
            flash("Product deleted successfully!", "success")
        else:
            flash("Failed to delete product.", "error")
    except Exception as e:
        flash(f"Error deleting product: {str(e)}", "error")
    
    return redirect(url_for('admin'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_admin():
    return session.get('is_admin', False)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('500.html'), 500

if __name__ == '__main__':
    db.create_tables()
    db.insert_products()
    app.run(debug=True)
