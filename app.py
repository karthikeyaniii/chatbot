import streamlit as st
from model import LoanChatbot  # Assuming the chatbot class is in model.py

# Initialize the chatbot
chatbot = LoanChatbot()

# Initialize session state variables only once
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

if 'current_question' not in st.session_state:
    st.session_state.current_question = "greeting"  # Start with the greeting

if 'initialized' not in st.session_state:
    # Initialize chatbot only once
    chatbot = LoanChatbot()
    st.session_state.initialized = True

# Display chat history
def display_chat():
    """ Display the chat history efficiently """
    for message in st.session_state.chat_history:
        st.write(message)

# Function to handle user response and chatbot's next question
def process_response(response):
    """ Process the user response and get the next question """
    chatbot.user_data.update(st.session_state.user_data)  # Update chatbot's user_data
    next_question = None

    # Handle greeting and initial information extraction
    if st.session_state.current_question == "greeting":
        chatbot.extract_initial_info(response)  # Extract user name, loan type, and amount
        name = chatbot.user_data.get('first_name', 'Guest')
        if 'loan_type' in chatbot.user_data and 'loan_amount' in chatbot.user_data:
            next_question = "Do you have a promotion code? (yes/no)"
        else:
            next_question = "What type of loan are you interested in? (Personal/Business/Home/Car/Education)"
    elif st.session_state.current_question == "loan_type":
        chatbot.user_data['loan_type'] = response.capitalize()
        next_question = "What loan amount are you looking for?"
    elif st.session_state.current_question == "loan_amount":
        chatbot.user_data['loan_amount'] = chatbot.extract_amount(response)
        next_question = "Do you have a promotion code? (yes/no)"
    elif st.session_state.current_question == "promo_code":
        if response.lower() == 'yes':
            next_question = "Please enter your promotion code:"
        else:
            next_question = "What is the purpose of this loan?"
    elif st.session_state.current_question == "promotion_code_input":
        if chatbot.validate_promo_code(response.upper()):
            chatbot.user_data['promotion_applied'] = response.upper()
            st.session_state.chat_history.append("Promotion code applied successfully!")
        else:
            st.session_state.chat_history.append("Invalid promotion code.")
        next_question = "What is the purpose of this loan?"
    elif st.session_state.current_question == "loan_purpose":
        chatbot.user_data['loan_purpose'] = response
        next_question = "Are you a member or non-member?"
    elif st.session_state.current_question == "membership_status":
        chatbot.user_data['membership_status'] = response.lower()
        next_question = "Please enter your account number:"
    elif st.session_state.current_question == "account_number":
        chatbot.user_data['account_number'] = response
        next_question = "What is your contact number?"
    elif st.session_state.current_question == "telephone":
        chatbot.user_data['telephone'] = response
        next_question = "What is your email address?"
    elif st.session_state.current_question == "email":
        chatbot.user_data['email'] = response
        next_question = "What is your date of birth? (DD/MM/YYYY)"
    elif st.session_state.current_question == "date_of_birth":
        chatbot.user_data['date_of_birth'] = response
        next_question = "Now, let's collect references. Please provide the first reference's name."
    elif "reference" in st.session_state.current_question:
        ref_num = int(st.session_state.current_question.split('_')[1])
        field = st.session_state.current_question.split('_')[2]
        chatbot.user_data[f'reference{ref_num}_{field}'] = response
        if field == 'occupation' and ref_num == 1:
            next_question = "Please provide the second reference's name."
        elif field == 'occupation' and ref_num == 2:
            next_question = "Finally, upload your ID documents."
        else:
            fields = ['relation', 'address', 'contact', 'occupation']
            next_field = fields[fields.index(field) + 1]
            next_question = f"Please provide reference {ref_num}'s {next_field}:"
    elif st.session_state.current_question == "id_documents":
        chatbot.user_data['uploaded_ids'] = response
        next_question = "Upload your supporting documents."
    elif st.session_state.current_question == "supporting_documents":
        chatbot.user_data['uploaded_documents'] = response
        chatbot.save_application()
        st.success(f"Thank you {chatbot.user_data.get('first_name', 'Guest')}! Your loan application has been submitted.")
        st.info(f"We'll contact you at {chatbot.user_data.get('email', 'your provided email')} soon.")
        next_question = None

    st.session_state.user_data = chatbot.user_data
    return next_question

# Display initial greeting
if st.session_state.current_question == "greeting":
    greeting = chatbot.get_greeting_response("Guest")  # You can update "Guest" to the user's name if available
    st.session_state.chat_history.append(greeting)
    st.session_state.current_question = "loan_type"

# Display user inputs and chatbot responses
display_chat()

# Dynamically display the input box for the next question
if st.session_state.current_question:
    question_to_display = st.session_state.current_question
    if question_to_display:
        user_input = st.text_input(f"Chatbot: {question_to_display}", "")
        if user_input:
            st.session_state.chat_history.append(f"You: {user_input}")
            next_question = process_response(user_input)

            # Update session state for next question
            if next_question:
                st.session_state.current_question = next_question
                st.session_state.chat_history.append(f"Chatbot: {next_question}")
                display_chat()
