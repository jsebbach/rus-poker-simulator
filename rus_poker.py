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
        order = {'2': 2, '3': 3, '4': '4', '5':  5, '6': 6, '7': 7,
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

# ... diğer tüm fonksiyonlar aynı kalır ...

# STREAMLIT APP

def streamlit_app():
    st.title("Rus Poker Simülatörü")

    suits = ['S', 'H', 'D', 'C']
    ranks = list('23456789TJQKA')
    all_cards = [r + s for r in ranks for s in suits]

    st.subheader("Oyuncu Kartları")
    player_cards_input = []
    for i in range(5):
        card = st.selectbox(f"Oyuncu Kartı {i+1}", all_cards, key=f"p{i}")
        player_cards_input.append(Card(card[0], card[1]))

    st.subheader("Kasa Açık Kartı")
    dealer_upcard = st.selectbox("Kasanın Açık Kartı", all_cards, key="dealer")
    dealer_hand = [Card(dealer_upcard[0], dealer_upcard[1])]

    st.subheader("Oyun Seçenekleri")
    buy = st.checkbox("Kasa kart çeksin mi (Buy)?", value=True)
    insurance = st.checkbox("Sigorta yapıldı mı?", value=True)

    if st.button("🟩 Eli Oyna"):
        deck = Deck()
        # Seçilen kartları desteden çıkar
        used_cards = player_cards_input + dealer_hand
        for c in used_cards:
            if c in deck.cards:
                deck.cards.remove(c)

        # Kasaya rastgele 4 kart daha ver
        dealer_hand += deck.draw(4)

        result = play_hand(player_cards_input, dealer_hand, deck, buy=buy, insurance=insurance)

        st.subheader("Sonuçlar")
        st.write(f"Kasa açtı mı: {'Evet' if result['dealer_opens'] else 'Hayır'}")
        st.write(f"Kasa kart aldı mı: {'Evet' if result['dealer_buy'] else 'Hayır'}")
        st.write(f"Oyuncu Kombosu: {result['player_combo']}")
        if result['dealer_opens']:
            st.write(f"Kasa Kombosu: {result['dealer_combo']}")
        st.write(f"Kazanan: {result['winner']}")
        if result['ak_bonus']:
            st.write("💥 A-K Bonusu Alındı")
        st.write(f"Kazanç: {result['payout']} (Maliyet: {result['cost']}, Net: {result['net_gain']})")
        st.write("---")
        st.write("Kasa Eli:")
        st.image([card_image(c.short()) for c in result['dealer_hand']], width=100)

if __name__ == "__main__":
    streamlit_app()
