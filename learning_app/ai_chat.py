import anthropic

client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5-20251001"


def ask_ai(topic_name, topic_content, chat_history, user_question):
    """
    Send a question to the AI with the topic content as context.
    chat_history: list of (role, message) tuples from the DB.
    Returns the AI's reply as a string.
    """
    system_prompt = (
        f"You are a helpful tutor. The student is studying: '{topic_name}'.\n"
        f"Use the following reference material to answer their questions clearly and simply.\n\n"
        f"--- REFERENCE MATERIAL ---\n{topic_content[:6000]}\n--- END ---\n\n"
        "If the answer is not in the material, say so and give a general explanation."
    )

    messages = []
    for role, message in chat_history:
        messages.append({"role": role, "content": message})
    messages.append({"role": "user", "content": user_question})

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text
