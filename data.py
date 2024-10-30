import random

male_adj = ["эпичный", "дерзкий", "чокнутый", "зашкварный", "улётный"]
femail_adj = ["эпичная", "дерзкая", "чокнутая", "зашкварная", "улётная"]

male_noun = ["тролль", "панда", "шизик", "фрик", "гуру"]
femail_noun = ["тролльша", "пандочка", "шизочка", "фрика", "гуруша"]

all_lists = [[male_adj,  male_noun], [femail_noun, femail_adj]]
# def generate_nick():
#     adj, noun = random.choice(all_lists)
#     nick = f"{random.choice(adj)} {random.choice(noun)}"
#     return nick

def generate_nick():
    adj, noun = map(random.choice, random.choice(all_lists))
    return f"{adj} {noun}"

nick = generate_nick()
print(nick)
