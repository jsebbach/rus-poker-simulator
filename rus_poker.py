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

def play_hand(player_hand, dealer_hand, deck, buy=False, insurance=False):
    return {
        "dealer_opens": True,
        "dealer_buy": buy,
        "player_combo": "pair",
        "dealer_combo": "high card",
        "winner": "player",
        "ak_bonus": False,
        "payout": 3,
        "cost": 3,
        "net_gain": 0,
        "dealer_hand": dealer_hand
    }

def simulate_ev(player_hand, dealer_upcard, base_deck, simulations=500, six_card=False):
    total_gain = 0
    for _ in range(simulations):
        deck = Deck()
        deck.cards = base_deck.cards.copy()
        dealer_hand = [dealer_upcard] + deck.draw(4)
        if six_card:
            player_sixth = deck.draw(1)[0]
            full_hand = player_hand + [player_sixth]
            all_combos = list(itertools.combinations(full_hand, 5))
            best_result = max((play_hand(list(combo), dealer_hand.copy(), deck)["net_gain"] for combo in all_combos), default=0)
            total_gain += best_result
        else:
            result = play_hand(player_hand, dealer_hand.copy(), deck)
            total_gain += result["net_gain"]
    return total_gain / simulations

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
    st.image([card_image(c.short()) for c in player_cards_input], width=100)

    st.subheader("Kasa Açık Kartı")
    dealer_upcard = st.selectbox("Kasanın Açık Kartı", all_cards, key="dealer")
    dealer_hand = [Card(dealer_upcard[0], dealer_upcard[1])]

    st.subheader("Oyun Seçenekleri")
    buy = st.checkbox("Kasa kart çeksin mi (Buy)?", value=True)
    insurance = st.checkbox("Sigorta yapıldı mı?", value=True)

    st.subheader("Oyuncu Aksiyonu")
    action = st.radio("Oyuncu ne yapsın?", ["Hiçbir şey yapma", "6. kartı al", "Kart değiştir"])

    if st.button("🟩 Eli Oyna"):
        deck = Deck()
        used_cards = player_cards_input + dealer_hand
        for c in used_cards:
            if c in deck.cards:
                deck.cards.remove(c)

        dealer_hand += deck.draw(4)

        if action == "6. kartı al":
            st.write("Simülasyon yapılıyor, lütfen bekleyin...")
            ev_normal = simulate_ev(player_cards_input, dealer_hand[0], deck, six_card=False)
            ev_six = simulate_ev(player_cards_input, dealer_hand[0], deck, six_card=True)
            st.write(f"5 kartla beklenen kazanç: {ev_normal:.2f}")
            st.write(f"6 kartla beklenen kazanç: {ev_six:.2f}")
            if ev_six > ev_normal:
                st.success("✅ 6. kart alınmalı (beklenen kazanç daha yüksek)")
            else:
                st.warning("🚫 6. kart alınmamalı (beklenen kazanç düşük)")

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
