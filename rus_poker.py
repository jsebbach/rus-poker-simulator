import streamlit as st
import random
from collections import Counter
import itertools

# Ödeme çarpanları
PAYOUT_MULTIPLIERS = {
    "royal flush": 100,
    "straight flush": 50,
    "four of a kind": 20,
    "full house": 14,
    "flush": 7,
    "straight": 4,
    "three of a kind": 3,
    "two pair": 2,
    "pair": 1,
    "high card": 0
}

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
        return "royal flush", PAYOUT_MULTIPLIERS["royal flush"]
    if is_flush and is_straight:
        return "straight flush", PAYOUT_MULTIPLIERS["straight flush"]
    if most_common[0][1] == 4:
        return "four of a kind", PAYOUT_MULTIPLIERS["four of a kind"]
    if most_common[0][1] == 3 and most_common[1][1] == 2:
        return "full house", PAYOUT_MULTIPLIERS["full house"]
    if is_flush:
        return "flush", PAYOUT_MULTIPLIERS["flush"]
    if is_straight:
        return "straight", PAYOUT_MULTIPLIERS["straight"]
    if most_common[0][1] == 3:
        return "three of a kind", PAYOUT_MULTIPLIERS["three of a kind"]
    if most_common[0][1] == 2 and most_common[1][1] == 2:
        return "two pair", PAYOUT_MULTIPLIERS["two pair"]
    if most_common[0][1] == 2:
        return "pair", PAYOUT_MULTIPLIERS["pair"]
    return "high card", PAYOUT_MULTIPLIERS["high card"]

def evaluate_two_combinations(hand6):
    from itertools import combinations
    five_card_combos = list(combinations(hand6, 5))
    combo_scores = [(evaluate_hand(list(combo))[1]) for combo in five_card_combos]
    combo_scores.sort(reverse=True)
    if len(combo_scores) >= 2:
        top = combo_scores[0]
        second = combo_scores[1] if combo_scores[1] >= PAYOUT_MULTIPLIERS["three of a kind"] else 0
        return "", top + second
    elif len(combo_scores) == 1:
        return "", combo_scores[0]
    return "", 0

def simulate_options(player_hand, full_deck, dealer_card=None, trials=500):
    keep_score = evaluate_hand(player_hand)[1]
    keep_ev = keep_score  # ante ve bet push, ödeme alınırsa bet kadar kazanılır

    # 6. kart alma (buy)
    buy_gains = []
    for _ in range(trials):
        available_cards = [c for c in full_deck.cards if c not in player_hand and c != dealer_card]
        sixth_card = random.choice(available_cards)
        hand6 = player_hand + [sixth_card]
        _, total_score = evaluate_two_combinations(hand6)
        gain = total_score - 1  # ante kadar ödeme yapılır
        buy_gains.append(gain)
    avg_buy_ev = sum(buy_gains) / trials

    # Kart değiştirme
    best_draw_ev = keep_ev
    best_combo = []
    combinations_to_try = [combo for r in range(1, 6) for combo in itertools.combinations(range(5), r)]
    for combo in combinations_to_try:
        draw_gains = []
        for _ in range(trials // 10):
            available_cards = [c for c in full_deck.cards if c not in player_hand and c != dealer_card]
            new_hand = player_hand[:]
            for idx in combo:
                new_hand[idx] = random.choice(available_cards)
            new_score = evaluate_hand(new_hand)[1]
            gain = new_score - 1  # ante kadar ödeme yapılır
            draw_gains.append(gain)
        avg_ev = sum(draw_gains) / len(draw_gains)
        if avg_ev > best_draw_ev:
            best_draw_ev = avg_ev
            best_combo = combo

    explanation = f"\n- Mevcut elin kazanç beklentisi (EV): {keep_ev:.2f}" \
                  f"\n- 6. kart alırsan ortalama EV: {avg_buy_ev:.2f}" \
                  f"\n- En iyi kart değişim ortalama EV: {best_draw_ev:.2f}"

    if avg_buy_ev >= best_draw_ev and avg_buy_ev > keep_ev:
        return "6. Kart Al (Buy)", explanation
    elif best_draw_ev > keep_ev:
        indices = [i+1 for i in best_combo]
        return f"{len(indices)} Kart Değiştir ({', '.join(map(str, indices))})", explanation
    else:
        return "Kart Çekmeden Oyna", explanation

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
        suggestion, explanation = simulate_options(selected_cards, deck, dealer_card=dealer_card)
        st.subheader("Program Önerisi")
        st.write(f"👉 **{suggestion}**")
        st.text(explanation)

if __name__ == "__main__":
    streamlit_app()
