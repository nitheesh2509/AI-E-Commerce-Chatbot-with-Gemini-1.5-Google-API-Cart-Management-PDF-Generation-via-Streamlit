import streamlit as st
import pandas as pd
from fpdf import FPDF

# Sample product data
products = [
    {"name": "Apple iPhone 14", "price": 999, "description": "6.1-inch display, 128GB, 12MP dual camera", 
     "image": "https://rukminim2.flixcart.com/image/832/832/xif0q/mobile/m/o/b/-original-imaghx9qkugtbfrn.jpeg?q=70&crop=false"},
     
    {"name": "Samsung Galaxy S21", "price": 799, "description": "6.2-inch display, 128GB, 12MP camera", 
     "image": "https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/z/j/v/galaxy-s21-fe-5g-sm-g990blv4ins-samsung-original-imah3nhk5c4dncfm.jpeg?q=70"},
     
    {"name": "Sony WH-1000XM4", "price": 349, "description": "Noise-cancelling wireless headphones", 
     "image": "https://m.media-amazon.com/images/I/71o8Q5XJS5L._SL1500_.jpg"},
     
    {"name": "Apple MacBook Pro", "price": 1299, "description": "13-inch, M1 chip, 256GB SSD", 
     "image": "https://rukminim2.flixcart.com/image/312/312/kuyf8nk0/computer/g/z/q/mk1e3hn-a-laptop-apple-original-imag7yzmv57cvg3f.jpeg?q=70"},
     
    {"name": "Amazon Echo Dot", "price": 49, "description": "Smart speaker with Alexa", 
     "image": "https://m.media-amazon.com/images/I/61KIy6gX-CL._AC_SL1000_.jpg"},
     
    {"name": "Canon EOS M50", "price": 699, "description": "Mirrorless camera with 4K video", 
     "image": "https://m.media-amazon.com/images/I/914hFeTU2-L._AC_SL1500_.jpg"}
]

# App title
st.set_page_config(layout="wide")
st.title("🛒 Welcome to My E-Commerce Store")

# Cart Management: using session state for cart persistence
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# Fullscreen mode
st.markdown(
    """
    <style>
        .streamlit-expander {
            max-width: 800px;
        }
        .main {
            max-width: 100%;
            width: 100%;
            height: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Custom CSS for product display
st.markdown("""<style>
.product-container {
    padding: 20px;
    margin-bottom: 30px;
    margin-right: 15px; 
    border: 1px solid #e1e1e1;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
}
.product-container:hover {
    transform: scale(1.02);
}
.product-image {
    width: 100%;
    margin-bottom: 10px;
    border-radius: 8px;
}
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #f1f1f1;
    color: black;
    text-align: center;
    padding: 10px;
}
</style>""", unsafe_allow_html=True)

# Display products by default
st.subheader("Available Products:")
cols = st.columns(3)  # Display in 3 columns for better alignment

for idx, product in enumerate(products):
    with cols[idx % 3]:  # Ensure products are aligned in columns
        st.markdown(f"<div class='product-container'>", unsafe_allow_html=True)
        st.image(product["image"], width=150, caption=product["name"])
        st.write(f"**Price**: ${product['price']}")
        st.write(f"**Description**: {product['description']}")
        
        # Add to Cart button
        if st.button(f"Add {product['name']} to Cart", key=idx):
            if product["name"] in st.session_state.cart:
                st.session_state.cart[product["name"]] += 1
            else:
                st.session_state.cart[product["name"]] = 1
            st.success(f"Added {product['name']} to your cart!")
        st.markdown("</div>", unsafe_allow_html=True)

# Function to send messages to the chatbot
def get_chatbot_response(user_message):
    user_message = user_message.lower().strip()

    # Greeting response
    if "hi" in user_message or "hello" in user_message:
        return "Hello! I'm here to help you with your shopping. You can ask me about our available products or request recommendations."

    # Adding products to cart
    for product in products:
        if product["name"].lower() in user_message:
            quantity = st.number_input(f"How many units of {product['name']} do you want to buy?", min_value=1, max_value=100, value=1)
            st.session_state.cart[product["name"]] = st.session_state.cart.get(product["name"], 0) + quantity
            total_price = st.session_state.cart[product["name"]] * product['price']
            return f"Added {quantity} unit(s) of {product['name']} to your cart. Total price for {product['name']}: ${total_price}. Are you looking for something else or do you want to proceed with your order?"

    # Available products
    if "recommend" in user_message or "products" in user_message:
        product_list = "\n".join([f"- {product['name']}: ${product['price']}" for product in products])
        return f"Here are some available products:\n{product_list}"

    # Displaying current cart items
    if "show" in user_message and "cart" in user_message:
        if st.session_state.cart:
            cart_items = "\n".join([f"- {item}: {count} unit(s)" for item, count in st.session_state.cart.items()])
            total_price = sum(products[i]["price"] * count for i, (item, count) in enumerate(st.session_state.cart.items()))
            return f"Your cart contains:\n{cart_items}\n**Total Price: ${total_price}**"
        else:
            return "Your cart is empty."

    # Removing items from cart
    if "remove" in user_message:
        for product in products:
            if product["name"].lower() in user_message:
                if product["name"] in st.session_state.cart:
                    del st.session_state.cart[product["name"]]
                    return f"{product['name']} has been removed from your cart."
                else:
                    return f"{product['name']} is not in your cart."

    # Proceeding with the order
    if "proceed" in user_message or "order" in user_message:
        if st.session_state.cart:
            order_summary = []
            total_price = 0
            for item, count in st.session_state.cart.items():
                price = next(p["price"] for p in products if p["name"] == item)
                total_price += price * count
                order_summary.append({"Product": item, "Quantity": count, "Price": price * count})

            order_df = pd.DataFrame(order_summary)
            st.session_state.cart.clear()

            pdf_filename = "order_summary.pdf"
            generate_pdf(order_df, total_price, pdf_filename)

            return f"Thank you for your order! Your total is: ${total_price}. You can download your order summary [here](./{pdf_filename})."
        else:
            return "Your cart is empty. Please add items to your cart before proceeding."

    return "I'm not sure how to respond to that. Can you please ask something else or refer to the available products?"

# Function to generate a PDF from the order summary
def generate_pdf(order_df, total_price, filename):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Order Summary", ln=True, align='C')

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Product", 1)
    pdf.cell(30, 10, "Quantity", 1)
    pdf.cell(40, 10, "Price", 1)
    pdf.cell(0, 10, "", 0)
    pdf.ln()

    pdf.set_font("Arial", '', 12)
    for index, row in order_df.iterrows():
        pdf.cell(60, 10, row["Product"], 1)
        pdf.cell(30, 10, str(row["Quantity"]), 1)
        pdf.cell(40, 10, f"${row['Price']:.2f}", 1)
        pdf.cell(0, 10, "", 0)
        pdf.ln()

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Total", 1)
    pdf.cell(30, 10, "", 1)
    pdf.cell(40, 10, f"${total_price:.2f}", 1)
    pdf.cell(0, 10, "", 0)
    pdf.ln()

    # Save the PDF
    pdf.output(filename)

# User input for chatbot
user_input = st.text_input("Ask me something:", "")

if user_input:
    bot_response = get_chatbot_response(user_input)
    st.write(f"**Chatbot:** {bot_response}")

# Displaying the cart summary
if st.session_state.cart:
    total_price = sum(products[i]["price"] * count for i, (item, count) in enumerate(st.session_state.cart.items()))
    st.sidebar.write("🛒 Cart Summary")
    st.sidebar.write(pd.DataFrame(list(st.session_state.cart.items()), columns=["Product", "Quantity"]))
    st.sidebar.write(f"**Total Price: ${total_price}**")
else:
    st.sidebar.write("Your cart is empty.")

# Footer
st.markdown('<div class="footer">Thank you for visiting our e-commerce store!</div>', unsafe_allow_html=True)
