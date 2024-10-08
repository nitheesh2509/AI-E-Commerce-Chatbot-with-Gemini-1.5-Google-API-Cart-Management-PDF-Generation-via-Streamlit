import streamlit as st
import pandas as pd
from fpdf import FPDF

import google.generativeai as genai  # Make sure you have the Gemini API installed and set up

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

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

# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Cart Management: using session state for cart persistence
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# App title
st.set_page_config(layout="wide")
st.title("🛒 Welcome to My E-Commerce Store")

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

# Display available products
st.subheader("Available Products:")
cols = st.columns(3)

for idx, product in enumerate(products):
    with cols[idx % 3]:
        st.image(product["image"], width=150, caption=product["name"])
        st.write(f"**Price**: ${product['price']}")
        st.write(f"**Description**: {product['description']}")
        
        if st.button(f"Add {product['name']} to Cart", key=idx):
            if product["name"] in st.session_state.cart:
                st.session_state.cart[product["name"]] += 1
            else:
                st.session_state.cart[product["name"]] = 1
            st.success(f"Added {product['name']} to your cart!")


def get_chatbot_response(user_message):
    user_message = user_message.lower().strip()

    # Greeting response
    if "hi" in user_message or "hello" in user_message:
        return "Hi there! How can I assist you with your shopping today?"

    # Check if the user is looking for a new phone or mentions a damaged mobile
    if "looking for new phone" in user_message or "my mobile is damaged" in user_message:
        gemini_response = model.generate_content(
            "I'm looking for a new phone because my current one is damaged. What should I say?",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=150,
                temperature=0.7,
            )
        )
        response = gemini_response.text

        # Show available products
        product_list = "\n".join([f"- {product['name']} for ${product['price']}" for product in products])
        return f"{response}\n\nHere are some options you might consider:\n{product_list}"

    # Add products to cart
    for product in products:
        if product["name"].lower() in user_message and "add" in user_message:
            # Extract quantity from the user message
            quantity = 1  # Default quantity
            words = user_message.split()
            for word in words:
                if word.isdigit():
                    quantity = int(word)  # Get the quantity if specified
                    break

            st.session_state.cart[product["name"]] = st.session_state.cart.get(product["name"], 0) + quantity
            return f"Added {quantity} unit(s) of {product['name']} to your cart."

    # Show cart summary
    if "show" in user_message and "cart" in user_message:
        if st.session_state.cart:
            cart_items = "\n".join([f"- {item}: {count} unit(s)" for item, count in st.session_state.cart.items()])
            total_price = sum(products[i]["price"] * count for i, (item, count) in enumerate(st.session_state.cart.items()))
            return f"Your cart contains:\n{cart_items}\n**Total Price: ${total_price:.2f}**"
        else:
            return "Your cart is empty."

    # Remove items or adjust quantity
    if "remove" in user_message:
        for product in products:
            if product["name"].lower() in user_message:
                if "quantity" in user_message:  # Adjusting quantity
                    quantity_to_remove = 1  # Default quantity
                    words = user_message.split()
                    for word in words:
                        if word.isdigit():
                            quantity_to_remove = int(word)  # Get the quantity to remove if specified
                            break

                    if product["name"] in st.session_state.cart:
                        current_quantity = st.session_state.cart[product["name"]]
                        if current_quantity > quantity_to_remove:
                            st.session_state.cart[product["name"]] -= quantity_to_remove
                            return f"Removed {quantity_to_remove} unit(s) of {product['name']} from your cart."
                        elif current_quantity == quantity_to_remove:
                            del st.session_state.cart[product["name"]]
                            return f"Removed all units of {product['name']} from your cart."
                        else:
                            return f"You only have {current_quantity} unit(s) of {product['name']} in your cart."

                if "delete" in user_message or "remove" in user_message:  # Full item deletion
                    if product["name"] in st.session_state.cart:
                        del st.session_state.cart[product["name"]]
                        return f"{product['name']} has been removed from your cart."
                    else:
                        return f"{product['name']} is not in your cart."

    # Proceed with order
    if "proceed" in user_message or "order" in user_message:
        if st.session_state.cart:
            order_summary = []
            total_price = 0
            for item, count in st.session_state.cart.items():
                price = next(p["price"] for p in products if p["name"] == item)
                total_price += price * count
                order_summary.append({"Product": item, "Quantity": count, "Price": price * count})

            order_df = pd.DataFrame(order_summary)
            pdf_filename = generate_pdf(order_df, total_price)

            st.session_state.cart.clear()  # Clear the cart after ordering
            return f"Thank you for your order! Your total is: ${total_price:.2f}. You can download your order summary below."

        else:
            return "Your cart is empty. Please add items to your cart before proceeding."

    return "I'm not sure how to respond to that. Can you ask something else?"

# Function to generate a PDF and provide download link
def generate_pdf(order_df, total_price):
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

    # Save the PDF file
    pdf_filename = "order_summary.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

# Chat history display
if st.session_state.chat_history:
    for chat in st.session_state.chat_history:
        st.write(f"**You:** {chat['user_input']}")
        st.write(f"**Chatbot:** {chat['bot_response']}")
    st.markdown("---")

# User input for chatbot
user_input = st.text_input("Ask me something:")

if user_input:
    bot_response = get_chatbot_response(user_input)
    st.session_state.chat_history.append({
        "user_input": user_input,
        "bot_response": bot_response
    })
    
    # Re-display chat history after new input
    for chat in st.session_state.chat_history:
        st.write(f"**You:** {chat['user_input']}")
        st.write(f"**Chatbot:** {chat['bot_response']}")

    # Show download button after placing an order
    if "Thank you for your order" in bot_response:
        with open("order_summary.pdf", "rb") as pdf_file:
            st.download_button(
                label="Download your Order Summary",
                data=pdf_file,
                file_name="order_summary.pdf",
                mime="application/pdf"
            )

# Display cart summary in sidebar
if st.session_state.cart:
    total_price = sum(products[i]["price"] * count for i, (item, count) in enumerate(st.session_state.cart.items()))
    st.sidebar.write("🛒 Cart Summary")
    st.sidebar.write(pd.DataFrame(list(st.session_state.cart.items()), columns=["Product", "Quantity"]))
    st.sidebar.write(f"**Total Price: ${total_price:.2f}**")
else:
    st.sidebar.write("Your cart is empty.")
