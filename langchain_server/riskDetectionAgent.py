import openai

SYSTEN_PROMPT = """
                You are a risk detection agent assessing the mental health of the user.
                You are given the chat history of the user from a chatbot.
                If the user is in an emotional crisis and requires emergency, reply with "CRISIS"
                If not, reply with "NO CRISIS"
                Do not guess.
                Your reponse must only be "CRISIS" or "NO CRISIS".
                """
class RiskDetectionAgent:
    def __init__(self):
        self.llm = openai.OpenAI(
            api_key=openai.api_key, # input your api key here
            # api_key = "xxx",
            # base_url="https://api.deepinfra.com/v1/openai", # remove if using gpt model

        )
        self.chat_history = []
        self.SYSTEM_PROMPT = SYSTEN_PROMPT
        self.messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

    def assess(self, message):
        """
        One message from user only
        """
        if not message:
            return
        self.messages.append({"role": "user", "content": message})
        response = self.llm.chat.completions.create(
            # model="Qwen/Qwen2.5-Coder-32B-Instruct",
            model="gpt-4-turbo", 
            messages=self.messages
        )
        return response.choices[0].message.content
    

