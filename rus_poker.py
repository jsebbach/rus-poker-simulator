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

# (Sınıflar ve yardımcı fonksiyonlar değişmedi)

# --- Güncellenmiş Kasa Gösterimi ---
def streamlit_app():
    st.set_page_config(page_title="Rus Pokeri Simülasyonu", layout="centered")
    st.title("🃏 Rus Pokeri El Simülatörü")

    deck = Deck()
    all_cards = [card.short() for card in deck.cards]

    st.subheader("🎴 Oyuncu Elini Seç")
    player_hand_strs = []
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            selected = st.selectbox(f"Kart {i+1}", options=[c for c in all_cards if c not in player_hand_strs], key=f"p{i}")
            player_hand_strs.append(selected)

    player_hand = [Card(c[:-1], c[-1]) for c in player_hand_strs]
    for c in player_hand:
        deck.cards.remove(c)

    st.subheader("🎴 Kasa Elini Seç")
    dealer_hand_strs = []
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            selected = st.selectbox(f"Kasa Kart {i+1}", options=[c for c in all_cards if c not in player_hand_strs + dealer_hand_strs], key=f"d{i}")
            dealer_hand_strs.append(selected)

    dealer_hand = [Card(c[:-1], c[-1]) for c in dealer_hand_strs]
    for c in dealer_hand:
        deck.cards.remove(c)

    buy = st.checkbox("Kasa açmazsa kart çektirilsin mi?", value=True)
    insurance = st.checkbox("Sigorta yapılsın mı?", value=True)

    if st.button("🕹️ Eli Oyna"):
        result = play_hand(player_hand, dealer_hand, deck, buy=buy, insurance=insurance)

        st.subheader("🎴 Oyuncu Eliniz")
        cols = st.columns(5)
        for i, card in enumerate(player_hand):
            with cols[i]:
                st.image(card_image(card.short()), use_container_width=True)
                st.caption(card.short())

        st.subheader("🃎 Kasa Açık Kartı")
        cols = st.columns(5)
        with cols[0]:
            st.image(card_image(dealer_hand[0].short()), use_container_width=True)
            st.caption(dealer_hand[0].short())
        for i in range(1, 5):
            with cols[i]:
                st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Card_back_01.svg/200px-Card_back_01.svg.png", use_container_width=True)
                st.caption("Gizli")

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
    streamlit_app()
