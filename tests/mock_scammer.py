"""
🛡️ Mock Scammer API Simulator
Generates realistic scam messages for testing.
"""

from typing import List, Dict, Any
import random
from faker import Faker

fake = Faker('en_IN')


class MockScammer:
    """
    Simulates various scam scenarios for testing the honey-pot.
    """
    
    SCAM_TEMPLATES = [
        # Bank account scams
        {
            "category": "bank_scam",
            "messages": [
                "Your bank account has been temporarily suspended. Verify immediately: {url}",
                "URGENT: Your {bank} account will be blocked in 24 hours. Click here to update KYC: {url}",
                "Alert! Unauthorized transaction of ₹{amount} detected. Confirm OTP {otp} to block.",
                "Dear customer, your account is locked due to suspicious activity. Call {phone} immediately.",
            ]
        },
        
        # Prize/lottery scams
        {
            "category": "prize_scam",
            "messages": [
                "Congratulations! You won ₹{amount} in {company} lottery. Send ₹500 processing fee to {upi}",
                "WINNER ALERT! You got selected for iPhone 15. Pay ₹999 shipping to {upi}",
                "Badhaai ho! Aapko ₹{amount} ka inaam mila hai. Details ke liye click karein: {url}",
                "You are the lucky winner! Transfer ₹{amount} tax to {upi} to claim your prize.",
            ]
        },
        
        # OTP/verification scams
        {
            "category": "otp_scam",
            "messages": [
                "Your OTP for account verification is {otp}. Valid for 10 minutes only.",
                "Verify your number immediately. OTP: {otp}. Do not share with anyone.",
                "Security Alert: Login attempt from new device. Your OTP is {otp}",
                "Confirm transaction of ₹{amount}. OTP: {otp}. Reply YES to proceed.",
            ]
        },
        
        # Job/investment scams
        {
            "category": "job_scam",
            "messages": [
                "Work from home opportunity! Earn ₹{amount}/month. Register at {url}",
                "Urgent hiring! ₹{amount} salary. Send resume to {email}. Registration fee ₹500 to {upi}",
                "Investment opportunity! 200% returns guaranteed. Transfer to {upi} now!",
                "Part-time job available. Earn daily. Pay ₹999 registration to {upi}",
            ]
        },
        
        # Phishing URLs
        {
            "category": "phishing",
            "messages": [
                "Update your details now: {url}",
                "Click to claim your refund: {url}",
                "Important: Verify your identity at {url}",
                "Download app for cashback: {url}",
            ]
        },
    ]
    
    SUSPICIOUS_DOMAINS = [
        "secure-bank-verify.tk",
        "indian-lottery-winner.ml",
        "bank-kyc-update.ga",
        "prize-claim-india.xyz",
        "urgent-verify-now.click",
    ]
    
    UPI_IDS = [
        "scammer123@paytm",
        "fraudster@phonepe",
        "fake.account@googlepay",
        "prize.claim@ybl",
        "winner2024@paytm",
    ]
    
    BANK_NAMES = ["HDFC", "ICICI", "SBI", "Axis", "Kotak"]
    
    @staticmethod
    def generate_scam_message() -> Dict[str, Any]:
        """
        Generate a random scam message.
        
        Returns:
            Dictionary with scam details
        """
        template = random.choice(MockScammer.SCAM_TEMPLATES)
        message_template = random.choice(template["messages"])
        
        # Fill in placeholders
        message = message_template.format(
            url=f"https://{random.choice(MockScammer.SUSPICIOUS_DOMAINS)}/verify",
            upi=random.choice(MockScammer.UPI_IDS),
            phone=fake.phone_number(),
            email=fake.email(),
            otp=str(random.randint(100000, 999999)),
            amount=random.choice([5000, 10000, 25000, 50000, 100000]),
            bank=random.choice(MockScammer.BANK_NAMES),
            company=random.choice(["Amazon", "Flipkart", "Google", "Paytm"]),
        )
        
        return {
            "category": template["category"],
            "message": message,
            "sender_id": fake.phone_number() if random.random() > 0.5 else "SCAM" + str(random.randint(10, 99)),
        }
    
    @staticmethod
    def generate_conversation(num_turns: int = 5) -> List[Dict[str, Any]]:
        """
        Generate a multi-turn scam conversation.
        
        Args:
            num_turns: Number of conversation turns
            
        Returns:
            List of scam messages
        """
        # Start with initial scam
        category = random.choice(["bank_scam", "prize_scam", "otp_scam"])
        
        conversation = []
        
        for turn in range(num_turns):
            if turn == 0:
                # Initial scam message
                msg = MockScammer.generate_scam_message()
            else:
                # Follow-up messages
                follow_ups = [
                    f"Sir, did you verify? Time is running out. Only {random.randint(1, 5)} hours left!",
                    f"Please respond immediately. Your account will be permanently blocked.",
                    f"Have you sent the amount to {random.choice(MockScammer.UPI_IDS)}?",
                    f"Sir please confirm. This is urgent matter.",
                    f"Call this number immediately: {fake.phone_number()}",
                ]
                msg = {
                    "category": category,
                    "message": random.choice(follow_ups),
                    "sender_id": conversation[0]["sender_id"],  # Same sender
                }
            
            conversation.append(msg)
        
        return conversation


# Test scenarios
PREDEFINED_SCENARIOS = [
    {
        "name": "Bank Account Locked",
        "messages": [
            "URGENT: Your HDFC account has been locked due to KYC non-compliance. Update now: https://secure-hdfc-verify.tk/kyc",
            "Sir this is final warning. Account will be PERMANENTLY closed. Verify immediately.",
            "Please send your account number and OTP to verify identity.",
        ]
    },
    {
        "name": "Prize Winner Scam",
        "messages": [
            "Congratulations! You won ₹50,000 in Amazon Lucky Draw. Pay ₹500 processing fee to winner2024@paytm",
            "Sir have you sent the amount? We need to process your prize today only.",
            "Many people are waiting in queue. Please transfer ₹500 to confirm.",
        ]
    },
    {
        "name": "Job Offer Scam",
        "messages": [
            "Work from home opportunity! Earn ₹25,000/month. Registration fee ₹999. Pay to jobportal@paytm",
            "Sir this is genuine company. Thousands of people working. Just pay small registration fee.",
            "After payment, we will send you joining letter and work details.",
        ]
    },
]


if __name__ == "__main__":
    # Generate sample scam messages
    print("=== Sample Scam Messages ===\n")
    
    for i in range(5):
        scam = MockScammer.generate_scam_message()
        print(f"{i+1}. Category: {scam['category']}")
        print(f"   Sender: {scam['sender_id']}")
        print(f"   Message: {scam['message']}")
        print()
