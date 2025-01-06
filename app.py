import streamlit as st
import pandas as pd
import os
import re

class LoanChatbot:
    def __init__(self):
        self.user_data = {}
        self.loan_types = ['Personal', 'Business', 'Home', 'Car', 'Education']
        self.valid_promo_codes = ['NEWUSER2024', 'SPRING20', 'SPECIAL50']

    def extract_initial_info(self, message):
        name_match = re.search(r'i am (\w+)', message.lower())
        amount_match = re.search(r'\$(\d+(?:,\d{3})*)', message)
        loan_type_match = re.search(r'(education|business|personal|home|car).*loan', message.lower())

        if name_match:
            self.user_data['first_name'] = name_match.group(1).capitalize()
        if amount_match:
            self.user_data['loan_amount'] = amount_match.group(0)
        if loan_type_match:
            self.user_data['loan_type'] = loan_type_match.group(1).capitalize()

    def validate_promo_code(self, code):
        return code in self.valid_promo_codes

    def validate_input(self, field_type, value):
        patterns = {
            'email': r'^[\w\.-]+@[\w\.-]+\.(?:com|ac\.in)$',
            'phone': r'^\d{10}$',
            'dob': r'^\d{2}/\d{2}/\d{4}$',
            'amount': r'^\$?\d+(?:,\d{3})*(?:\.\d{2})?$',
            'account': r'^\d{12,16}$'
        }
        return bool(re.match(patterns.get(field_type, r'.+'), value))

    def save_application(self):
        df = pd.DataFrame([self.user_data])
        csv_file = "loan_applications1.csv"
        if os.path.exists(csv_file):
            df.to_csv(csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_file, mode='w', header=True, index=False)


# Streamlit app
st.title("Loan Application Chatbot")
st.subheader("Let's get started with your loan application!")

chatbot = LoanChatbot()

# Dynamic Questions
required_fields = {
    'first_name': "What is your name?",
    'loan_type': "What type of loan are you interested in?",
    'loan_amount': "What loan amount are you looking for?",
    'loan_purpose': "What is the purpose of this loan?",
    'membership_status': "Are you a member or non-member?",
    'account_number': "Enter your account number:",
    'telephone': "Enter your contact number:",
    'email': "Enter your email address:",
    'date_of_birth': "Enter your date of birth (DD/MM/YYYY):"
}

# Loop through required fields and ask for missing information
for field, prompt in required_fields.items():
    if field not in chatbot.user_data or not chatbot.user_data[field]:
        value = st.text_input(prompt)
        if value:
            chatbot.user_data[field] = value

# Promotion Code Section
if 'promotion_applied' not in chatbot.user_data:
    promo_code_section = st.expander("Do you have a promotion code?")
    with promo_code_section:
        has_promo = st.radio("Do you have a promotion code?", ["No", "Yes"], index=0)
        if has_promo == "Yes":
            promo_code = st.text_input("Enter your promotion code:")
            if promo_code:
                if chatbot.validate_promo_code(promo_code.upper()):
                    st.success("Promotion code applied successfully!")
                    chatbot.user_data['promotion_applied'] = promo_code.upper()
                else:
                    st.error("Invalid promotion code.")

# References Section
for i in range(1, 3):
    if f'reference{i}_name' not in chatbot.user_data:
        st.subheader(f"Reference {i}")
        chatbot.user_data[f'reference{i}_name'] = st.text_input(f"Reference {i} Name:")
        chatbot.user_data[f'reference{i}_relation'] = st.text_input(f"Reference {i} Relation:")
        chatbot.user_data[f'reference{i}_address'] = st.text_input(f"Reference {i} Address:")
        chatbot.user_data[f'reference{i}_contact'] = st.text_input(f"Reference {i} Contact:")
        chatbot.user_data[f'reference{i}_occupation'] = st.text_input(f"Reference {i} Occupation:")

# Document Upload Section
if 'uploaded_ids' not in chatbot.user_data:
    st.subheader("Upload Required Documents")
    uploaded_ids = st.file_uploader("Upload your ID documents", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_ids:
        chatbot.user_data['uploaded_ids'] = uploaded_ids.name
        st.success("ID documents uploaded.")

if 'uploaded_documents' not in chatbot.user_data:
    uploaded_docs = st.file_uploader("Upload supporting documents", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_docs:
        chatbot.user_data['uploaded_documents'] = uploaded_docs.name
        st.success("Supporting documents uploaded.")

# Submit Application Button
if st.button("Submit Application"):
    chatbot.save_application()
    st.success(f"Thank you {chatbot.user_data.get('first_name', 'Guest')}! Your loan application has been submitted.")
    st.info(f"We'll contact you at {chatbot.user_data.get('email', 'your provided email')} soon.")

