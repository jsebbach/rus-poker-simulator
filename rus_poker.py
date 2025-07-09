import streamlit as st
import random
from PIL import Image
import os
from collections import Counter
import itertools

CARD_IMAGES = "cards"

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def short(self):
        return f"{self.rank}{self.suit}"

    def value(self):
        order = {'2': 2, '3': 3, '4': 4, '5':  5, '6': 6, '7': 7,
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

def evaluate_hand(hand):
    values = sorted([card.value() for card in hand], reverse=True)
    suits = [card.suit for card in hand]
    counts = Counter(values)
    most_common = counts.most_common()

    is_flush = len(set(suits)) == 1
    is_straight = all(values[i] - 1 == values[i+1] for i in range(len(values)-1)) or values == [14, 5, 4, 3, 2]

    if is_flush and is_straight and values[0] == 14:
        return "royal flush", 10
    if is_flush and is_straight:
        return "straight flush", 9
    if most_common[0][1] == 4:
        return "four of a kind", 8
    if most_common[0][1] == 3 and most_common[1][1] == 2:
        return "full house", 7
    if is_flush:
        return "flush", 6
    if is_straight:
        return "straight", 5
    if most_common[0][1] == 3:
        return "three of a kind", 4
    if most_common[0][1] == 2 and most_common[1][1] == 2:
        return "two pair", 3
    if most_common[0][1] == 2:
        return "pair", 2
    return "high card", 1

def get_payout(combo):
    payouts = {
        "royal flush": 100,
        "straight flush": 50,
        "four of a kind": 20,
        "full house": 7,
        "flush": 5,
        "straight": 4,
        "three of a kind": 3,
        "two pair": 2,
        "pair": 1,
        "high card": 0
    }
    return payouts.get(combo, 0)

def is_ak_bonus(hand):
    has_a = any(card.rank == 'A' for card in hand)
    has_k = any(card.rank == 'K' for card in hand)
    combo, _ = evaluate_hand(hand)
    return has_a and has_k and combo == "high card"

def dealer_should_open(dealer_hand):
    has_a = any(card.rank == 'A' for card in dealer_hand)
    has_k = any(card.rank == 'K' for card in dealer_hand)
    combo, _ = evaluate_hand(dealer_hand)
    return combo != "high card" or (has_a and has_k)

def simulate_options(player_hand, dealer_hand, deck):
    keep_hand = player_hand.copy()
    buy_card = player_hand.copy() + deck.draw(1)
    combinations = list(itertools.combinations(range(5), r=1)) + list(itertools.combinations(range(5), r=2))

    best_change = keep_hand
    best_score = evaluate_hand(keep_hand)[1]
    for combo in combinations:
        new_hand = player_hand.copy()
        for idx in combo:
            new_hand[idx] = deck.draw(1)[0]
        score = evaluate_hand(new_hand)[1]
        if score > best_score:
            best_score = score
            best_change = new_hand

    buy_score = evaluate_hand(buy_card[:5])[1]
    change_score = evaluate_hand(best_change)[1]
    base_score = evaluate_hand(keep_hand)[1]

    if buy_score >= change_score and buy_score > base_score:
        return "Buy 6th card"
    elif change_score > base_score:
        return "Change cards"
    else:
        return "Play as is"

def play_hand(player_hand, dealer_hand, deck, buy=False, insurance=False):
    player_combo, player_strength = evaluate_hand(player_hand)
    dealer_combo, dealer_strength = evaluate_hand(dealer_hand)

    dealer_opens = dealer_should_open(dealer_hand)
    player_wins = False
    tie = False
    payout = 0
    ak_bonus = False
    insurance_payout = 0
    base_cost = 2
    total_cost = base_cost + (1 if buy else 0) + (get_payout(player_combo) if insurance else 0)

    if not dealer_opens:
        if buy:
            weakest = min(dealer_hand, key=lambda c: c.value())
            dealer_hand.remove(weakest)
            dealer_hand.append(deck.draw(1)[0])
            dealer_combo, dealer_strength = evaluate_hand(dealer_hand)
            dealer_opens = dealer_should_open(dealer_hand)

    if dealer_opens:
        if player_strength > dealer_strength:
            player_wins = True
        elif player_strength == dealer_strength:
            tie = True

    if not dealer_opens:
        if insurance:
            insurance_payout = get_payout(player_combo)
        if not buy:
            payout = 1
    elif player_wins:
        payout = get_payout(player_combo)
        if is_ak_bonus(player_hand):
            ak_bonus = True
            payout += 1
    elif tie:
        payout = 0

    net_gain = payout - total_cost + insurance_payout

    return {
        "dealer_opens": dealer_opens,
        "dealer_buy": buy,
        "player_combo": player_combo,
        "dealer_combo": dealer_combo,
        "winner": "player" if player_wins else "tie" if tie else "dealer",
        "ak_bonus": ak_bonus,
        "payout": payout,
        "cost": total_cost,
        "net_gain": net_gain,
        "dealer_hand": dealer_hand
    }

