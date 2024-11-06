import random

male_adj = ["эпичный", "дерзкий", "чокнутый", "зашкварный", "улётный"]
femail_adj = ["эпичная", "дерзкая", "чокнутая", "зашкварная", "улётная"]

male_noun = ["тролль", "панда", "шизик", "фрик", "гуру"]
femail_noun = ["тролльша", "пандочка", "шизочка", "фрика", "гуруша"]

all_lists = [[male_adj, male_noun], [femail_adj, femail_noun]]


def generate_nick():
    adj, noun = map(random.choice, random.choice(all_lists))
    return f"{adj} {noun}"


VISIBILITY = {"private": False, "public": True}

VISIBILITY_LABELS = {True: "ОТКРЫТАЯ", False: "ЗАКРЫТАЯ"}
