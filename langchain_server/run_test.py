import os
import json
import time
import openai
from chatAgent import MentalHealthChatAgent  # import your existing agent class
from dotenv import load_dotenv
load_dotenv()  # this loads the .env file into os.environ



TEST_PROMPT_FOLDER = "test/prompts"
LOG_FOLDER = "test/logs"
MODEL = "gpt-4-turbo"

def load_prompt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def init_testing_agent(system_prompt):
    return [
        {"role": "system", "content": system_prompt}
    ]

def chat_with_test_agent(messages):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )
    reply = response.choices[0].message.content
    return reply

def run_test_case(prompt_path):
    scenario_id = os.path.basename(prompt_path).replace(".txt", "")
    print(f"\n[TEST] Running scenario: {scenario_id}")
    system_prompt = load_prompt(prompt_path)

    # Initialize agents
    test_agent_messages = init_testing_agent(system_prompt)
    mh_agent = MentalHealthChatAgent()

    log = []  # Save full conversation

    # Start chat
    assistant_start = mh_agent.messages[-1]["content"]
    test_agent_messages.append({"role": "user", "content": assistant_start})
    print(f"[TEST] Initial message sent to test agent: {assistant_start}")

    turn_count = 0
    max_turns = 20

    while turn_count < max_turns:
        # Get user reply from testing LLM
        user_reply = chat_with_test_agent(test_agent_messages)
        test_agent_messages.append({"role": "assistant", "content": user_reply})
        print(f"[TEST] User reply: {user_reply}")
        # Feed into MH agent
        assistant_reply = mh_agent.get_reply(user_reply)
        test_agent_messages.append({"role": "user", "content": assistant_reply})
        print(f"[TEST] Assistant reply: {assistant_reply}")

        # End if session ends
        if "<END>" in mh_agent.messages[-1]["content"] or "<EMERGENCY>" in assistant_reply:
            break

        turn_count += 1
        time.sleep(1)  # prevent rate limit
    log = mh_agent.messages[1:]

    save_log(scenario_id, log)

def save_log(scenario_id, log):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    filename = f"{LOG_FOLDER}/{scenario_id}_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"[LOG] Conversation saved to: {filename}")

def run_all_tests():
    for prompt_file in os.listdir(TEST_PROMPT_FOLDER):
        if prompt_file.endswith(".txt"):
            run_test_case(os.path.join(TEST_PROMPT_FOLDER, prompt_file))

if __name__ == "__main__":
    run_all_tests()
