import streamlit as st
import random
from PIL import Image
import os
from collections import Counter

CARD_IMAGES = "cards"

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def short(self):
        return f"{self.rank}{self.suit}"

    def value(self):
        order = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                 '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return order[self.rank]

    def __repr__(self):
        return self.short()

    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))

class Deck:
    def __init__(self):
        ranks = '23456789TJQKA'
        suits = 'SHDC'
        self.cards = [Card(r, s) for r in ranks for s in suits]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, count):
        return [self.cards.pop() for _ in range(count)]

def card_image(code):
    rank_map = {
        '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7',
        '8': '8', '9': '9', 'T': '10', 'J': 'jack', 'Q': 'queen', 'K': 'king', 'A': 'ace'
    }
    suit_map = {
        'H': 'hearts', 'D': 'diamonds', 'S': 'spades', 'C': 'clubs'
    }
    rank = rank_map[code[0]]
    suit = suit_map[code[1]]
    filename = f"{rank}_of_{suit}.png"
    path = os.path.join(CARD_IMAGES, filename)
    return Image.open(path)

def classify_hand(cards):
    values = sorted([c.value() for c in cards], reverse=True)
    suits = [c.suit for c in cards]
    counter = Counter(values)
    counts = sorted(counter.values(), reverse=True)
    unique_vals = sorted(counter.keys(), reverse=True)

    is_flush = len(set(suits)) == 1
    is_straight = all(values[i] - 1 == values[i + 1] for i in range(4))

    if values == [14, 5, 4, 3, 2]:
        is_straight = True
        values = [5, 4, 3, 2, 1]

    if is_straight and is_flush and values[0] == 14:
        return (9, "Royal Flush")
    if is_straight and is_flush:
        return (8, "Straight Flush")
    if counts == [4, 1]:
        return (7, "Four of a Kind")
    if counts == [3, 2]:
        return (6, "Full House")
    if is_flush:
        return (5, "Flush")
    if is_straight:
        return (4, "Straight")
    if counts == [3, 1, 1]:
        return (3, "Three of a Kind")
    if counts == [2, 2, 1]:
        return (2, "Two Pair")
    if counts == [2, 1, 1, 1]:
        return (1, "One Pair")
    return (0, "High Card")

def play_hand(player, dealer, deck, buy=True, insurance=True):
    ante = 1
    bet = 2
    payout = 0
    cost = ante + bet

    dealer_opens = classify_hand(dealer)[0] >= 1 or ('A' in [c.rank for c in dealer] and 'K' in [c.rank for c in dealer])

    insurance_win = not dealer_opens
    insurance_payout = (bet * 3 if insurance_win else 0) if insurance else 0
    cost += (bet * 3) if insurance else 0

    dealer_buy = False
    if not dealer_opens and buy:
        dealer_buy = True
        worst = min(dealer, key=lambda c: c.value())
        dealer.remove(worst)
        dealer.append(deck.draw(1)[0])
        dealer_opens = classify_hand(dealer)[0] >= 1 or ('A' in [c.rank for c in dealer] and 'K' in [c.rank for c in dealer])
        cost += ante

    score_p, combo_p = classify_hand(player)
    score_d, combo_d = classify_hand(dealer)
    ak_bonus = False
    second_combo = None

    if not dealer_opens:
        return {
            "dealer_opens": False,
            "dealer_buy": dealer_buy,
            "winner": "no_show",
            "player_combo": combo_p,
            "dealer_combo": "",
            "ak_bonus": False,
            "second_combo": None,
            "insurance_win": insurance_payout,
            "payout": insurance_payout + ante if not buy else insurance_payout,
            "cost": cost,
            "net_gain": insurance_payout + (ante if not buy else 0) - cost
        }

    if score_p > score_d:
        multiplier = [1, 1, 2, 3, 4, 6, 9, 20, 50, 100][score_p]
        payout = bet * multiplier
        if 'A' in [c.rank for c in player] and 'K' in [c.rank for c in player] and score_p == 0:
            ak_bonus = True
            payout += 1
    elif score_p == score_d:
        payout = 0
    else:
        payout = 0

    net = payout + insurance_payout - cost
    return {
        "dealer_opens": dealer_opens,
        "dealer_buy": dealer_buy,
        "winner": "player" if score_p > score_d else "tie" if score_p == score_d else "dealer",
        "player_combo": combo_p,
        "dealer_combo": combo_d,
        "ak_bonus": ak_bonus,
        "second_combo": second_combo,
        "insurance_win": insurance_payout,
        "payout": payout + insurance_payout,
        "cost": cost,
        "net_gain": net
    }
