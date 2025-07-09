import streamlit as st
import random
from collections import Counter
import itertools

# Kart sınıfı
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

# Deste
class Deck:
    def __init__(self):
        ranks = list('23456789TJQKA')
        suits = list('SHDC')
        self.cards = [Card(r, s) for r in ranks for s in suits]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, count):
        return [self.cards.pop() for _ in range(count)]

# El değerlendirme

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

def evaluate_two_combinations(hand6):
    from itertools import combinations
    scores = []
    best_labels = []
    five_card_combos = list(combinations(hand6, 5))
    for combo in five_card_combos:
        label, score = evaluate_hand(list(combo))
        scores.append(score)
        best_labels.append(label)
    total_score = sum(scores)
    return max(best_labels), total_score

def simulate_options(player_hand, deck, trials=500):
    keep_score = evaluate_hand(player_hand)[1]

    # 6. kart alma (buy)
    buy_scores = []
    for _ in range(trials):
        new_deck = Deck()
        new_deck.cards = [c for c in new_deck.cards if c not in player_hand]
        sixth_card = random.choice(new_deck.cards)
        hand6 = player_hand + [sixth_card]
        _, total_score = evaluate_two_combinations(hand6)
        buy_scores.append(total_score)
    avg_buy_score = sum(buy_scores) / trials

    # Kart değiştirme
    best_change_score = keep_score
    best_change_combo = []
    combinations_to_try = [combo for r in range(1, 6) for combo in itertools.combinations(range(5), r)]
    for combo in combinations_to_try:
        change_scores = []
        for _ in range(trials // 10):
            new_deck = Deck()
            new_deck.cards = [c for c in new_deck.cards if c not in player_hand]
            new_hand = player_hand[:]
            for idx in combo:
                new_hand[idx] = random.choice(new_deck.cards)
            score = evaluate_hand(new_hand)[1]
            change_scores.append(score)
        avg_score = sum(change_scores) / len(change_scores)
        if avg_score > best_change_score:
            best_change_score = avg_score
            best_change_combo = combo

    # Karşılaştırma
    if avg_buy_score >= best_change_score and avg_buy_score > keep_score:
        return "6. Kart Al (Buy)"
    elif best_change_score > keep_score:
        indices = [i+1 for i in best_change_combo]
        return f"{len(indices)} Kart Değiştir ({', '.join(map(str, indices))})"
    else:
        return "Kart Çekmeden Oyna"

def streamlit_app():
    st.title("Rus Pokeri: El Öneri Modu")
    deck = Deck()

    st.header("Oyuncunun Kartları")
    ranks = list('23456789TJQKA')
    suits = list('SHDC')
    selected_cards = []
    cols = st.columns(5)
    for i in range(5):
        rank = cols[i].selectbox(f"Kart {i+1} Rütbe", ranks, key=f"player_rank_{i}")
        suit = cols[i].selectbox(f"Kart {i+1} Maça", suits, key=f"player_suit_{i}")
        selected_cards.append(Card(rank, suit))

    st.header("Kasanın Açık Kartı")
    dealer_rank = st.selectbox("Kasa Kartı Rütbe", ranks, key="dealer_rank")
    dealer_suit = st.selectbox("Kasa Kartı Maça", suits, key="dealer_suit")
    dealer_card = Card(dealer_rank, dealer_suit)

    if st.button("Hamle Önerisi Al"):
        deck.cards = [c for c in deck.cards if c not in selected_cards and c != dealer_card]
        suggestion = simulate_options(selected_cards, deck)
        st.subheader("Program Önerisi")
        st.write(f"👉 **{suggestion}**")

if __name__ == "__main__":
    streamlit_app()
