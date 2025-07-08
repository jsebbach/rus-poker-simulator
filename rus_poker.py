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

def streamlit_app():
    st.set_page_config(page_title="Rus Pokeri Simülasyonu", layout="centered")
    st.title("🃏 Rus Pokeri El Simülatörü")

    all_ranks = '23456789TJQKA'
    all_suits = 'SHDC'
    all_cards = [f"{r}{s}" for r in all_ranks for s in all_suits]

    st.subheader("🎴 Oyuncu Elini Seç")
    player_hand_strs = []
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            selected = st.selectbox(
                f"Kart {i+1}",
                options=[c for c in all_cards if c not in player_hand_strs],
                key=f"player_{i}"
            )
            player_hand_strs.append(selected)
    player_hand = [Card(c[:-1], c[-1]) for c in player_hand_strs]

    st.subheader("🂠 Kasa Açık Kartını Seç")
    dealer_open_card_str = st.selectbox(
        "Kasa Açık Kartı",
        options=[c for c in all_cards if c not in player_hand_strs],
        key="dealer_open"
    )
    dealer_open_card = Card(dealer_open_card_str[:-1], dealer_open_card_str[-1])

    used_cards = player_hand + [dealer_open_card]
    deck = Deck()
    deck.cards = [c for c in deck.cards if c.short() not in [card.short() for card in used_cards]]
    dealer_hand = [dealer_open_card] + deck.draw(4)

    buy = st.checkbox("Kasa açmazsa kart çektirilsin mi?", value=True)
    insurance = st.checkbox("Sigorta yapılsın mı?", value=True)

    if st.button("🕹️ Eli Oyna"):
        from copy import deepcopy
        result = play_hand(deepcopy(player_hand), deepcopy(dealer_hand), deck, buy=buy, insurance=insurance)

        st.subheader("🎴 Oyuncu Eliniz")
        cols = st.columns(5)
        for i, card in enumerate(player_hand):
            with cols[i]:
                st.image(card_image(card.short()), use_container_width=True)
                st.caption(card.short())

        st.subheader("🃎 Kasa Eli")
        cols = st.columns(5)
        for i, card in enumerate(result["dealer_hand"]):
            with cols[i]:
                st.image(card_image(card.short()), use_container_width=True)
                st.caption(card.short())

        st.subheader("🧮 El Sonucu")
        st.write("**Kasa Elini Açtı:**", result["dealer_opens"])
        st.write("**Kasa Kart Çekti:**", result["dealer_buy"])
        st.write("**Kazanma Durumu:**", result["winner"].upper())
        st.write("**Oyuncu Kombinasyonu:**", result["player_combo"])
        if result["second_combo"]:
            st.write("**İkinci Kombinasyon:**", result["second_combo"])
        st.write("**Kasa Kombinasyonu:**", result["dealer_combo"])
        st.write("**A–K Bonusu Var mı:**", result["ak_bonus"])
        st.write("**Sigorta Kazanacı:**", result["insurance_win"])
        st.metric("💰 Toplam Kazanç", f"{result['payout']:.2f} ante")
        st.metric("💸 Toplam Maliyet", f"{result['cost']:.2f} ante")
        st.metric("📈 Net Kar/Zarar", f"{result['net_gain']:.2f} ante")

if __name__ == "__main__":
    from rus_poker import play_hand
    streamlit_app()
