import streamlit as st
import random
from PIL import Image
import os
from collections import Counter

CARD_IMAGES = "cards"  # klasör içinde 52 kart görseli olmalı, örnek: AH.png, 2S.png vb.

# --- Kart Sınıfı ---
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

# --- Deste Sınıfı ---
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

# --- Kombinasyon Sınıflandırma ---
def classify_hand(cards):
    values = sorted([c.value() for c in cards], reverse=True)
    suits = [c.suit for c in cards]
    counter = Counter(values)
    counts = sorted(counter.values(), reverse=True)
    unique_vals = sorted(counter.keys(), reverse=True)

    is_flush = len(set(suits)) == 1
    is_straight = all(values[i] - 1 == values[i + 1] for i in range(4))

    if values == [14, 5, 4, 3, 2]:  # Wheel straight (A-2-3-4-5)
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

# --- El Oynama Fonksiyonu ---
def play_hand(player, dealer, deck, buy=True, insurance=True):
    ante = 1
    bet = 2
    payout = 0
    cost = ante + bet

    dealer_opens = classify_hand(dealer)[0] >= 1 or ('A' in [c.rank for c in dealer] and 'K' in [c.rank for c in dealer])

    # Sigorta ödemesi durumu
    insurance_win = not dealer_opens
    insurance_payout = (bet * 3 if insurance_win else 0) if insurance else 0
    cost += (bet * 3) if insurance else 0

    # Kasa açmazsa buy
    dealer_buy = False
    if not dealer_opens and buy:
        dealer_buy = True
        worst = min(dealer, key=lambda c: c.value())
        dealer.remove(worst)
        dealer.append(deck.draw(1)[0])
        dealer_opens = classify_hand(dealer)[0] >= 1 or ('A' in [c.rank for c in dealer] and 'K' in [c.rank for c in dealer])
        cost += ante

    # Kombinasyonlar
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

# Kart görselini getir (örnek: AH, 9D)
def card_image(code):
    path = os.path.join(CARD_IMAGES, f"{code}.png")
    return Image.open(path)

# GUI uygulaması

def streamlit_app():
    st.set_page_config(page_title="Rus Pokeri Simülasyonu", layout="centered")
    st.title("🃏 Rus Pokeri El Simülatörü")

    deck = Deck()
    player_hand = deck.draw(5)

    st.subheader("🎴 Oyuncu Eliniz")
    cols = st.columns(5)
    for i, card in enumerate(player_hand):
        with cols[i]:
            st.image(card_image(card.short()), use_column_width=True)
            st.caption(card.short())

    buy = st.checkbox("Kasa açmazsa kart çektirilsin mi?", value=True)
    insurance = st.checkbox("Sigorta yapılsın mı?", value=True)

    if st.button("🕹️ Eli Oyna"):
        dealer_hand = deck.draw(5)
        result = play_hand(player_hand, dealer_hand, deck, buy=buy, insurance=insurance)

        st.subheader("🧮 El Sonucu")
        st.write("**Kasa Elini Açtı:**", result["dealer_opens"])
        st.write("**Kasa Kart Çekti:**", result["dealer_buy"])
        st.write("**Kazanma Durumu:**", result["winner"].upper())
        st.write("**Oyuncu Kombinasyonu:**", result["player_combo"])
        if result["second_combo"]:
            st.write("**İkinci Kombinasyon:**", result["second_combo"])
        st.write("**Kasa Kombinasyonu:**", result["dealer_combo"])
        st.write("**A–K Bonusu Var mı:**", result["ak_bonus"])
        st.write("**Sigorta Kazancı:**", result["insurance_win"])
        st.metric("💰 Toplam Kazanç", f"{result['payout']:.2f} ante")
        st.metric("💸 Toplam Maliyet", f"{result['cost']:.2f} ante")
        st.metric("📈 Net Kar/Zarar", f"{result['net_gain']:.2f} ante")

    st.markdown("---")
    st.subheader("📈 Simülasyon")
    sim_count = st.number_input("Simülasyon Adedi", min_value=1000, max_value=100000, value=10000, step=1000)

    if st.button("▶️ Simülasyonu Başlat"):
        from collections import defaultdict
        outcomes = defaultdict(int)
        total_gain = 0
        total_payout = 0
        total_cost = 0

        for _ in range(sim_count):
            sim_deck = Deck()
            sim_deck.cards = [c for c in sim_deck.cards if c not in player_hand]
            sim_deck.shuffle()
            dealer_hand = sim_deck.draw(5)
            result = play_hand(player_hand, dealer_hand, sim_deck, buy=buy, insurance=insurance)
            total_gain += result["net_gain"]
            total_payout += result["payout"]
            total_cost += result["cost"]
            outcomes[result["winner"]] += 1
            if result["insurance_win"]:
                outcomes["insurance_win"] += 1

        st.success("✅ Simülasyon Tamamlandı")
        st.write(f"🟢 **Kazanma Oranı:** {outcomes['player'] / sim_count:.2%}")
        st.write(f"⚫ **Beraberlik Oranı:** {outcomes['tie'] / sim_count:.2%}")
        st.write(f"🔴 **Kasa Kazanma Oranı:** {outcomes['dealer'] / sim_count:.2%}")
        st.write(f"🕳️ **Kasa Açmadı Oranı:** {outcomes['no_show'] / sim_count:.2%}")
        st.write(f"🛡️ **Sigorta Kazanma Oranı:** {outcomes['insurance_win'] / sim_count:.2%}")
        st.metric("📈 Ortalama Net Kar", f"{total_gain / sim_count:.4f} ante")
        st.metric("💰 Ortalama Ödeme", f"{total_payout / sim_count:.4f} ante")
        st.metric("💸 Ortalama Maliyet", f"{total_cost / sim_count:.4f} ante")
