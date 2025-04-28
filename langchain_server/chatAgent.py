import openai

CHAT_SYSTEM_PTOMPT = """
You are a mental health intake assistant.
You always reply to user/patient gently and warmly.
You must always reply with special tags to guide the system's action:
- <START> if starting a new session
- <CONSENT> if greeting and ask for consent of asking question and the chatting data privacy policy before intake form filling.
- <FAQ> if user asks questions about services
- <EMERGENCY> if user shows signs of crisis or severe emotional distress
- <INTAKE> if strating or continuing intake form:
    - Add <BEGIN> if to start the intake filling
    - Add <NEXT> if ready to move to the next section of the intake form
    - Add <CONTINUE> if keep on the current section
    - Add <FINISH> if all intake question completed
- <END> if the the session is end
Always embed these tags at in your response.
The chatting session flow for making appointment with mental health counselling session is:
- Normal case: Greet → Consent → Intake Form Questions → Confirm → Close → Done.
- Ask each quseiton one by one in short sentance, keep each section short and concise for finishing the session in 10 mins.
- If no consent, ask again or close the session.
- If user asks questions: Reply with <FAQ> tag → Answer → Return to intake form.
- If emergency detected: Reply with <EMERGENCY> tag → Provide immediate crisis contact → End intake form politely → End the session.
"""
CHAT_INIT_MSG="<START> Hello! I'm here to support you. Before scheduling an appointment, may I ask you a few questions to better understand your situation?"

class MentalHealthChatAgent:
    def __init__(self):
        self.messages = [
            {"role": "system", "content": CHAT_SYSTEM_PTOMPT},
            {"role": "assistant", "content": CHAT_INIT_MSG}
        ]
        self.intake_question_index = 0
        self.intake_form_data = {}
        self.intake_section = [
            "<INTAKE><BEGIN> Section 1. General Information: Name and Contact.",
            "<INTAKE><NEXT> Section 2. Main issue and past history.",
            "<INTAKE><NEXT> Section 3. Symptom Check: Decreased need for sleep, Change in appetite, Anxiety attacks, etc.",
            "<INTAKE><NEXT> Section 4. Risk Assessment: suicide risk, family violance, rist of harm to others.",
            "<INTAKE><NEXT> Section 5. Medical History.",
            "<INTAKE><NEXT> Section 6. Appointment check: time, prefer phsician."
        ]

    def chat(self, messages = None):
        if not messages:
            messages=self.messages
        client= openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # or gpt-4-turbo if you want cheaper
            messages=messages
        )
        reply = response.choices[0].message.content
        return reply

    def parse_reply(self, reply):
        if "<FAQ>" in reply:
            ## use RAG to regerate answer
            self.handle_faq()
        elif "<EMERGENCY>" in reply:
            # use RAG to generate emergency handling answer
            self.handle_emergency()
        elif "<INTAKE>"in reply:
            if "<NEXT>" in reply or "<BEGIN>" in reply or "<FINISHED>" in reply:
                # inject intake section to lead the question to ask
                reply = self.ask_next_intake_question()
                # if "<FINISHED>" in reply:
                #     self.submit_intake_form()
        elif "<END>" in reply:
            self.end_session()

        return reply

    def handle_faq(self):
        print("[SYSTEM] FAQ detected. Retrieving answer...")
        # TODO: Call your RAG retriever here
        # could include contact, acaliable time table etc.
        # thinking to copy content from school web: https://www.nus.edu.sg/hwb/ucs/

    def handle_emergency(self):
        print("[SYSTEM] Emergency detected! Providing crisis lifeline...")
        print("If you are in immediate danger, please call 24/7 Lifeline: 1-800-273-TALK (8255)")
        print("A real counselor will follow up shortly. Please stay safe.")
        # TODO: Optionally halt further conversation
        # considering more solidate way to detect emergency, as it is important and can not make mistakes.

    def ask_next_intake_question(self):
        if self.intake_question_index < len(self.intake_section):
            question = self.intake_section[self.intake_question_index]
            self.intake_question_index += 1
            self.messages.append({"role": "assistant", "content":question})
            reply = self.chat()
            return reply
        else:
            return "<FINISH> All intake questions completed."


    def end_session(self):
        # save the session, generate final intake form
        # restart the chat
        print("[SYSTEM] Submitting intake form...")
        print(self.intake_form_data)  # Simulate form submission
        print("[SYSTEM] Session ended. Thank you.")
    


    def get_reply(self, user_input)-> str:
        # print("Hello! I'm here to support you. Before scheduling an appointment, may I ask you a few questions to better understand your situation?")
        # while True:
        # user_input = input("You: ")
        self.messages.append({"role": "user", "content": user_input})
        AI_reply = self.chat()
        print(f"[DEBUG] Assistant: {AI_reply}")
        reply=self.parse_reply(AI_reply)
        self.messages.append({"role": "assistant", "content": reply})
        if "<END>" in reply:
            self.end_session()
        return reply
        # print(f"Messages\n\n {self.messages[1:]}")
        
