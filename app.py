import streamlit as st
from model import LoanChatbot  # Import LoanChatbot from model.py

# Initialize the chatbot
chatbot = LoanChatbot()

# Title and Intro
st.title("Loan Application Chatbot")
st.write("Welcome! Let's get started with your loan application.")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# Function to handle user responses and progress the chat
def process_response(response):
    chatbot.user_data.update(st.session_state.user_data)  # Update chatbot's user_data
    next_question = None

    if st.session_state.current_question == "greeting":
        chatbot.extract_initial_info(response)
        name = chatbot.user_data.get('first_name', 'Guest')
        next_question = chatbot.get_greeting_response(name)
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

# Chat Interface
if st.session_state.current_question is None:
    st.session_state.current_question = "greeting"
    st.session_state.chat_history.append("Welcome! How can I assist you with your loan application today?")

for chat in st.session_state.chat_history:
    st.write(chat)

if st.session_state.current_question:
    user_input = st.text_input("You:", key="user_input")
    if st.button("Send"):
        st.session_state.chat_history.append(f"You: {user_input}")
        next_q = process_response(user_input)
        if next_q:
            st.session_state.chat_history.append(next_q)
            st.session_state.current_question = next_q
        else:
            st.session_state.current_question = None

