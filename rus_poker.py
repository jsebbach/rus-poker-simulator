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

def simulate_options(player_hand, deck):
    keep_hand = player_hand.copy()
    buy_card = player_hand.copy() + deck.draw(1)
    combinations = list(itertools.combinations(range(5), r=1)) + list(itertools.combinations(range(5), r=2)) + list(itertools.combinations(range(5), r=3)) + list(itertools.combinations(range(5), r=4)) + [tuple(range(5))]

    best_change = keep_hand
    best_score = evaluate_hand(keep_hand)[1]
    for combo in combinations:
        new_hand = player_hand.copy()
        new_deck = Deck()
        new_deck.cards = [c for c in new_deck.cards if c not in player_hand]
        for idx in combo:
            new_hand[idx] = new_deck.draw(1)[0]
        score = evaluate_hand(new_hand)[1]
        if score > best_score:
            best_score = score
            best_change = new_hand

    buy_score = evaluate_hand(buy_card[:5])[1]
    change_score = evaluate_hand(best_change)[1]
    base_score = evaluate_hand(keep_hand)[1]

    if buy_score >= change_score and buy_score > base_score:
        return "6. Kart Al (Buy)"
    elif change_score > base_score:
        changed = [i+1 for i in range(5) if player_hand[i] != best_change[i]]
        return f"{len(changed)} Kart Değiştir ({', '.join(map(str, changed))})"
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
