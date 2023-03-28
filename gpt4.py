import textwrap

import openai

openai.api_key = open("secret-key.txt").read().rstrip()

messages = []
system_init = None
while True:
    if system_init is None:
        system_init = input("Init> ")
        messages.append({"role": "system", "content": system_init})

    content = input("> ")
    if content.lower() in ["exit", "q", "quit"]:
        break

    messages.append({"role": "user", "content": content})

    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.8,
    )

    message = res["choices"][0]["message"]
    paras = message["content"].split("\n\n")

    print()
    for para in paras:
        print(textwrap.fill(para))
        print("")

    messages.append({"role": "assistant", "content": message["content"]})
