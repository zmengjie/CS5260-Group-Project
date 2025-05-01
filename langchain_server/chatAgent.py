import openai
import json
import os
import time
from rag_retriever import RAGRetriever
from riskDetectionAgent import RiskDetectionAgent
import re

CHAT_SYSTEM_PTOMPT = """
You are a mental health intake assistant.
You always reply to user/patient gently and warmly.
You must always reply with special tags to guide the system's action:
- <START> if starting a new session
- <CONSENT> if greeting and ask for consent of asking question and the chatting data privacy policy before intake form filling.
- <FAQ> if user asks any questions about services
- <EMERGENCY> if user shows signs of crisis or severe emotional distress
- If strating or continuing intake form:
    - Add <BEGIN> if to start the intake filling
    - Add <NEXT> if ready to move to the next section of the intake form
    - Add <CONTINUE> if keep on the current intake section
    - Add <FINISH> if all intake question completed
- <END> if the the session is end
Always embed these tags at in your response. Add one and only one tag in each reponse. 
DO NOT ask consent and intake question together or mixed any intake section questions.
The chatting session flow for making appointment with mental health counselling session is:
- Normal case: Greet → Consent → Intake Form Questions → Confirm → Close → Done.
- Ask each quseiton one by one, keep you question simple. If needed, ask for follow up detail gently.
- Before moving on to next intake section, ask patient if anything to add on.
- If no consent, ask again or close the session.
- If user asks any questions: Reply with <FAQ> tag → Answer → Return to intake form.
- If emergency detected: Reply with <EMERGENCY> tag → Provide immediate crisis contact → End intake form politely → End the session.

The intake form contain 6 sections to fill in, please ask question based on each section, always come with tags.
<BEGIN> Presenting Concerns: Ask why the client is seeking counseling. Ask for the duration.
<NEXT> Mental Health History: If applicable, ask about past services (type, duration, outcome).
<NEXT> Current Symptoms: Ask relevant symptoms based on concerns (e.g., depression, anxiety, sleep).
<NEXT> Risk Assessment: Ask about self-harm, suicide, harm to others, or family violence. Probe if yes.
<NEXT> Medical History: Ask about current conditions and medications if any.
<NEXT> Appointment Preferences: Check available times and any therapist preference.
"""
CHAT_INIT_MSG="<START> Hello! I'm here to support you. Before scheduling an appointment, may I ask you a few questions to better understand your situation?"

FORM_SYSTEM_PROMPT = """
You are a professional mental health intake assistant. Your job is to read the chatting history between clinic and the user, and generate a JSON format intake form based on the conversation.
Each section content should be clear and concise for later triage and counseling.
The JSON format should be:
{
    "intake_form": {
        "Presenting Concerns": "...",
        "Mental Health History": "...",
        "Current Symptoms": "...",
        "Risk Assessment": "...",
        "Medical History": "...",
        "Appointment Preferences": "..."
}
"""

INTAKE_FORM =[
    "<BEGIN> Let's start with section 1: Presenting Concerns.",
    "<NEXT> Next is section 2: Mental Health Hisotry.",
    "<NEXT> Section 3: Current Symptoms.",
    "<NEXT> Section 4: Risk Assessment.",
    "<NEXT> Section 5: Medical History.",
    "<NEXT> Last, section 6: Appointment check."
]

REACT_SYSTEM_PROMPT = """
You are a helpful assistant answering questions about the mental health center.
Use the provided information to answer the user's question.
If the question is not in the knowledge base, please reply special tag <NULL> and do not make up any information.
If answer is found, reply with tag <ANSWER> with the answer.
"""

class MentalHealthChatAgent:
    def __init__(self):
        self.retriever = RAGRetriever()
        self.messages = [
            {"role": "system", "content": CHAT_SYSTEM_PTOMPT},
            {"role": "assistant", "content": CHAT_INIT_MSG}
        ]
        self.intake_question_index = 0
        self.intake_form_data = {}
        self.intake_section = INTAKE_FORM
        self.risk_detection_agent = RiskDetectionAgent()

    def chat(self, messages = None)-> str:
        if not messages:
            messages=self.messages
        client= openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4-turbo", 
            messages=messages
        )
        reply = response.choices[0].message.content
        return reply

    def parse_reply(self, reply):
        if "<FAQ>" in reply:
            ## use RAG to regerate answer
            answer= self.handle_faq()
            if answer:
                reply= answer
        elif "<EMERGENCY>" in reply:
            # use RAG to generate emergency handling answer
            self.handle_emergency()
        elif "<NEXT>" in reply or "<BEGIN>" in reply or "<FINISHED>" in reply:
                # inject intake section to lead the question to ask
                reply = self.ask_next_intake_question()
                # if "<FINISHED>" in reply:
                #     self.submit_intake_form()
        elif "<END>" in reply:
            self.end_session()

        return reply

    def handle_faq(self) -> str:
        print("[SYSTEM] FAQ detected. Retrieving info from knowledge base...")
        user_query = self.messages[-1]["content"]
        retrieved = self.retriever.retrieve(user_query)
        answer=""
        if retrieved:
            print("[SYSTEM] Retrieved information:", retrieved)
            # Now re-ask LLM to generate an answer with the retrieved context
            messages=[
                {"role": "system", "content": REACT_SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is the information {retrieved}"},
                {"role": "user", "content": f"Here is the question:{user_query}"}
            ]
            answer = self.chat(messages)
            if "<NULL>" in answer:
                print("[SYSTEM] No relevant information found.")
                answer=""
            elif "<ANSWER>" in answer:
                # remove answer tag                
                answer = answer.replace("<ANSWER>", "").strip()
            else:
                print("[SYSTEM] Missing tag from answer generation.")
                answer = ""

        return answer


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
        # Prepare messages to generate final intake form
        messages = [
            {"role": "system", "content": FORM_SYSTEM_PROMPT},
            {"role": "user", "content": "Here is the conversation history. Please help me fill the intake form in JSON format based on it:\n\n" + self._format_conversation()},
        ]

        # Call OpenAI to generate the intake form
        reply = self.chat(messages)
        print(f"[DEBUG] Intake form generated: {reply}")
        print("[SYSTEM] Submitting intake form...")

        # Save the reply to local folder
        self._save_form(reply)

        print("[SYSTEM] Session ended. Thank you.")

    def _format_conversation(self):
        """
        Format conversation messages for feeding into form generation.
        """
        formatted = ""
        for msg in self.messages:
            if msg["role"] == "user":
                formatted += f"Patient: {msg['content']}\n"
            elif msg["role"] == "assistant":
                formatted += f"Assistant: {msg['content']}\n"
        return formatted

    def _save_form(self, form_text):
        """
        Save the generated form to a local file.
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        if not os.path.exists("Database/saved_forms"):
            os.makedirs("Database/saved_forms")

        filename = f"Database/saved_forms/intake_form_{timestamp}.json"
        try:
            parsed_json = json.loads(form_text)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(parsed_json, f, indent=2, ensure_ascii=False)
            print(f"[SYSTEM] Form saved at {filename}")
        except Exception as e:
            print(f"[SYSTEM] Failed to save form as JSON. Raw text will be saved instead. Error: {e}")
            with open(filename.replace(".json", ".txt"), "w", encoding="utf-8") as f:
                f.write(form_text)
            print(f"[SYSTEM] Raw form saved at {filename.replace('.json', '.txt')}")

    def get_reply(self, user_input)-> str:

        self.messages.append({"role": "user", "content": user_input})
        AI_reply = self.chat()
        print(f"[DEBUG] Assistant: {AI_reply}")
        reply=self.parse_reply(AI_reply)

        # Assess User
        assessment = self.risk_detection_agent.assess(reply)
        if assessment:
            self.handle_emergency()
        self.messages.append({"role": "assistant", "content": reply})
        reply = re.sub(r'<[^>]+>', '', reply).strip()
        return reply
        
