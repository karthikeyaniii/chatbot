import re
import pandas as pd
import os
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GenerationConfig
import torch


class LoanChatbot:
    def __init__(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.generation_config = GenerationConfig(
            max_new_tokens=100,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            pad_token_id=self.tokenizer.eos_token_id,
            temperature=0.7
        )
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

    def get_greeting_response(self, name):
        greetings = [
            f"Hello {name}! I'm excited to help you with your loan application today.",
            f"Great to meet you, {name}! Let's get started with your loan application.",
            f"Welcome {name}! I'll guide you through the loan application process."
        ]
        return greetings[hash(name) % len(greetings)]

    def validate_promo_code(self, code):
        return code in self.valid_promo_codes

    def split_name(self, full_name):
        parts = full_name.strip().split()
        if len(parts) == 1:
            return parts[0], "", ""
        elif len(parts) == 2:
            return parts[0], "", parts[1]
        else:
            return parts[0], " ".join(parts[1:-1]), parts[-1]

    def validate_input(self, field_type, value):
        patterns = {
            'email': r'^[\w\.-]+@[\w\.-]+\.(?:com|ac\.in)$',
            'phone': r'^\d{10}$',
            'dob': r'^\d{2}/\d{2}/\d{4}$',
            'amount': r'^\$?\d+(?:,\d{3})*(?:\.\d{2})?$',
            'account': r'^\d{12,16}$'
        }
        if field_type == 'yn':
            return value.lower() in ['yes', 'no']
        elif field_type == 'marital':
            return value.lower() in ['married', 'single', 'divorced', 'widowed']
        elif field_type == 'membership':
            return value.lower() in ['member', 'non-member']

        return bool(re.match(patterns.get(field_type, r'.+'), value))

    def extract_amount(self, value):
        amount_match = re.search(r'\$?\d+(?:,\d{3})*(?:\.\d{2})?', value)
        if amount_match:
            return amount_match.group(0)
        return value

    def handle_document_upload(self, doc_type):
        print(f"Please upload your {doc_type} (type 'uploaded' to simulate upload):")
        while True:
            response = input("You: ").strip().lower()
            if response == 'uploaded':
                return f"{doc_type} uploaded"
            print("Invalid response. Please type 'uploaded' after completing the upload.")

    def process_application(self):
        print("Welcome! How can I assist you with your loan application today?")
        initial_input = input("You: ")
        self.extract_initial_info(initial_input)

        name = self.user_data.get('first_name', 'Guest')
        print(self.get_greeting_response(name))

        if not self.user_data.get('loan_type'):
            print("\nWhat type of loan are you interested in? (Personal/Business/Home/Car/Education)")
            self.user_data['loan_type'] = input("You: ").capitalize()

        if not self.user_data.get('loan_amount'):
            print("\nWhat loan amount are you looking for?")
            self.user_data['loan_amount'] = input("You: ")

        print("\nBefore we continue, do you have a promotion code? (yes/no)")
        has_promo = input("You: ").lower()
        if has_promo == 'yes':
            while True:
                print("Please enter your promotion code:")
                promo_code = input("You: ").upper()
                if self.validate_promo_code(promo_code):
                    print("Great! Your promotion code has been applied.")
                    self.user_data['promotion_applied'] = promo_code
                    break
                print("Invalid code. Try again? (yes/no)")
                if input("You: ").lower() != 'yes':
                    break

        fields = [
            ('loan_purpose', 'What is the purpose of this loan?', None),
            ('full_name', 'Please confirm your full name:', None),
            ('membership_status', 'Are you a member or non-member?', 'membership'),
            ('account_number', 'Please enter your account number:', 'account'),
            ('telephone', 'What is your contact number?', 'phone'),
            ('email', 'What is your email address?', 'email'),
            ('date_of_birth', 'What is your date of birth? (DD/MM/YYYY)', 'dob'),
        ]

        for field, prompt, validation_type in fields:
            if field not in self.user_data:
                while True:
                    print(f"\n{prompt}")
                    response = input("You: ")
                    if validation_type and not self.validate_input(validation_type, response):
                        print("Invalid input format. Please try again.")
                        continue
                    if field == 'full_name':
                        first, middle, last = self.split_name(response)
                        self.user_data.update({
                            'first_name': first,
                            'middle_name': middle,
                            'last_name': last
                        })
                    else:
                        self.user_data[field] = response
                    break

        print("\nNow, I'll need two references.")
        for i in range(1, 3):
            for field_type in ['name', 'relation', 'address', 'contact', 'occupation']:
                key = f'reference{i}_{field_type}'
                print(f"Please provide reference {i} {field_type}:")
                self.user_data[key] = input("You: ")

        print("\nFinally, we need your documents.")
        self.user_data['uploaded_ids'] = self.handle_document_upload("ID documents")
        self.user_data['uploaded_documents'] = self.handle_document_upload("supporting documents")

        df = pd.DataFrame([self.user_data])

        # Save the data to CSV
        csv_file = "loan_applications1.csv"
        if os.path.exists(csv_file):
            df.to_csv(csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_file, mode='w', header=True, index=False)

        print(f"\nThank you! Your {self.user_data['loan_type']} loan application has been submitted.")
        print(f"We'll contact you at {self.user_data['email']} regarding next steps.")


if __name__ == "__main__":
    chatbot = LoanChatbot()
    chatbot.process_application()
