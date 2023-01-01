"""Chapter 10 - Build your own story generator, Story Machines,
Sharples and Perez.
14 pot story
"""

import re
from textwrap import fill

import openai
from numpy import random

openai.api_key = open("secret-key.txt").read().rstrip()

grammar = {
    "STORY": ("INITIAL EVENT RESOLUTION CONSEQUENCES",),
    "INITIAL": (
        "SALUTATION in SETTING there lived NAME, OCCUPATION who was DESCRIPTION.",
    ),
    "SALUTATION": (
        "When it all began",
        "Before the war",
        "Of course you've heard of the time",
    ),
    "EVENT": ("COMPLICATION PLAN ACTION1",),
    "COMPLICATION": (
        "A visionary dream drove NAME to find a OBJECT.",
        "Consumed by greed, NAME set off to find a OBJECT.",
        "NAME was gripped with a compulsion to obtain a OBJECT.",
        "The boredom of life in a SETTING was too much for NAME who one day decided to find a OBJECT.",
    ),
    "PLAN": (
        "'If only I could have a OBJECT,' thought NAME.",
        "An idea formed in NAME's mind about how to get a OBJECT.",
        "NAME thought long and hard about ways to get a OBJECT.",
    ),
    "ACTION1": (
        "Filled with determination, NAME strode off, but soon his spirits began to flag. ACTION2",
        "With hope in his heart and a bounce in his step, NAME set off to find a OBJECT. ACTION2",
        "NAME wandered the roads and pathways getting further away from his SETTING looking for a OBJECT but saw no sight of one. ACTION2",
    ),
    "ACTION2": (
        "NAME was befriended by a PERSON who told him where he might find a OBJECT.",
        "As his last hope began to fade, NAME met with a PERSON who suggested where a OBJECT might be found.",
        "Suddenly, there ahead of him, was a PERSON who suggested where a OBJECT might be found.",
        "Through a haze of exhaustion, NAME saw the vague form of a OBJECT.",
    ),
    "RESOLUTION": (
        "Filled with longing, NAME rushed up to the OBJECT and grabbed it, only to find it was a mirage.",
        "NAME made a grab for the OBJECT but tripped and fell. The last thing NAME saw was the OBJECT flying through the air.",
    ),
    "CONSEQUENCES": (
        "NAME was devastated. Overcome with emotion, they took to the hills, proclaiming they would never seek a OBJECT again.",
        "NAME had achieved bliss. The OBJECT was different than expected, but this pleased NAME greatly.",
    ),
    "SETTING": (
        "central square",
        "research laboratory",
        "burger restaurant",
        "newspaper room",
    ),
    "NAME": ("Gwen", "Zhou", "Paul", "Carlos", "Vlad"),
    "OCCUPATION": (
        "iron-worker",
        "barrister",
        "financial adviser",
        "cook",
        "professor",
        "carpenter",
    ),
    "DESCRIPTION": (
        "tall and gangly",
        "rude",
        "charismatic",
    ),
    "PERSON": (
        "android",
        "tourist",
        "leader",
    ),
    "OBJECT": (
        "lustrous silver mirror",
        "fat wad of cash",
        "bag of turnips",
        "perfect song",
    ),
}


def elaborate(x):
    """Which prompts to elaborate upon"""
    return x in (
        "SALUTATION",
        "NAME",
        "DESCRIPTION",
        "PERSON",
        "OCCUPATION",
        "OBJECT",
    )


def parse(response):
    new = response["choices"][0]["text"].strip()
    new = re.sub("['\.]+$", "", new)

    return new


style = "very descriptive"

# regular expression for substitution variable tokens. strings of all
# caps / digits
re_token = r"([A-Z0-9]{2,})"

# initial story string
string = "STORY"
# find the first token or substitution variable
m = re.search(re_token, string)
cache = {}  # cache for stateful variables -- eg, NAME

print("Generating story and first-round embellishments...", end="")
# while there is still a parsed substitution variable token
while m:
    # parse the substitution variable
    match = m.groups()[0]

    if match in cache:
        new = cache[match]

    else:
        # choose a random option
        all_new = grammar[match]
        ix_new = random.randint(len(all_new))
        new_template = all_new[ix_new]

        new = new_template

        # if re.search(re_token, new_template) not elaborate(match):
        if not elaborate(match):
            new = new_template

        else:
            print(f"...", end="")
            prompt = f"'{new_template}' can be rewritten with similar words in a {style} style as '"
            response = openai.Completion.create(
                # model="text-curie-001",
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.8,
                max_tokens=64,
            )
            new = parse(response)

        cache[match] = new

    string = re.sub(match, new, string)
    m = re.search(re_token, string)

print("Done.\n\n")
print(fill(string, 60))
print("\n\n\n")

prompt = f"The passage '{string}' can be rewritten with improved grammar and better style, and like a potboiler detective novel, as '"
response = openai.Completion.create(
    # model="text-curie-001",
    model="text-davinci-003",
    prompt=prompt,
    temperature=0.7,
    max_tokens=256,
)
new_string = parse(response)
print(fill(new_string, 60))
