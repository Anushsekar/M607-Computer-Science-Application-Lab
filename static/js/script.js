// Function to show toast notifications
function showToast(message, success = true) {
    const toast = document.createElement('div');
    toast.className = `toast ${success ? 'success' : 'error'}`;
    toast.innerText = message;
    document.body.appendChild(toast);

    // Remove the toast after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Add event listeners when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add to cart button click handlers
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            addToCart(productId);
        });
    });

    // Login button validation
    let loginButton = document.querySelector(".login-btn");
    let usernameInput = document.querySelector("input[name='username']");
    let passwordInput = document.querySelector("input[name='password']");

    if (loginButton && usernameInput && passwordInput) {
        function checkInputs() {
            if (usernameInput.value.trim() !== "" && passwordInput.value.trim() !== "") {
                loginButton.disabled = false;
            } else {
                loginButton.disabled = true;
            }
        }

        usernameInput.addEventListener("input", checkInputs);
        passwordInput.addEventListener("input", checkInputs);
    }

    // Image preview handlers
    const imageInputs = document.querySelectorAll('input[type="file"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                const preview = document.createElement('img');
                preview.className = 'image-preview';
                preview.style.maxWidth = '200px';
                preview.style.marginTop = '10px';
                
                reader.onload = function(e) {
                    preview.src = e.target.result;
                }
                
                reader.readAsDataURL(this.files[0]);
                
                // Remove existing preview if any
                const existingPreview = this.parentElement.querySelector('.image-preview');
                if (existingPreview) {
                    existingPreview.remove();
                }
                
                this.parentElement.appendChild(preview);
            }
        });
    });
});

function addToCart(productId) {
    const quantitySelect = document.querySelector(`#quantity-${productId}`);
    if (!quantitySelect) {
        showToast("❌ Error: Could not find quantity selector", false);
        return;
    }

    const quantity = quantitySelect.value;
    if (!quantity || quantity < 1) {
        showToast("❌ Please select a valid quantity", false);
        return;
    }

    fetch(`/cart/add/${parseInt(productId)}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast("✅ " + data.message);
        } else {
            showToast("❌ " + data.message, false);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast("❌ Error adding item to cart", false);
    });
}

// Search Function
document.querySelector(".search-bar button").addEventListener("click", function() {
    let query = document.querySelector(".search-bar input").value.toLowerCase();
    let products = document.querySelectorAll(".product");

    products.forEach(product => {
        let title = product.querySelector("h3").textContent.toLowerCase();
        product.style.display = title.includes(query) ? "block" : "none";
    });
});

// Function to update cart quantity
function updateQuantity(itemId, change) {
    fetch(`/cart/update/${itemId}/${change}`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload(); // Refresh cart to show updated quantity
        } else {
            alert("Error updating quantity!");
        }
    })
    .catch(error => console.error('Error:', error));
}

// Mobile Menu Toggle
function toggleMobileMenu() {
    const navRight = document.querySelector('.nav-right');
    navRight.classList.toggle('active');
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const navRight = document.querySelector('.nav-right');
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    
    if (!event.target.closest('.nav-right') && 
        !event.target.closest('.mobile-menu-toggle') && 
        navRight.classList.contains('active')) {
        navRight.classList.remove('active');
    }
});

// Admin Dashboard Functions
function showEditForm(productId) {
    document.getElementById(`edit-form-${productId}`).style.display = 'table-row';
}

function hideEditForm(productId) {
    document.getElementById(`edit-form-${productId}`).style.display = 'none';
}
