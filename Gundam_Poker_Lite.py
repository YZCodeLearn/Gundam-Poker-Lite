import streamlit as st
import matplotlib.pyplot as plt
import time

# --- Page Setup ---
st.set_page_config(page_title="G Poker Lite Tallyman", layout="centered")

# === Player Name Setup ===
if "players_ready" not in st.session_state:
    st.session_state.players_ready = False
    st.session_state.player_names = {}

if not st.session_state.players_ready:
    st.title("🎮 Gundam Poker Lite")
    st.write("Enter names for 3 players:")

    p1 = st.text_input("Player 1", value="")
    p2 = st.text_input("Player 2", value="")
    p3 = st.text_input("Player 3", value="")

    if st.button("Start Game 🎲"):
        st.session_state.player_names = {1: p1, 2: p2, 3: p3}
        st.session_state.positions = {1: 2, 2: 2, 3: 2}
        st.session_state.status = {1: "", 2: "", 3: ""}
        st.session_state.history = {1: [2], 2: [2], 3: [2]}
        st.session_state.fail_flags = {
            1: {"A1": False, "A2": False},
            2: {"A1": False, "A2": False},
            3: {"A1": False, "A2": False},
        }
        st.session_state.prev_winner = None
        st.session_state.prev_king_card = None
        st.session_state.round_num = 1
        st.session_state.winner = None
        st.session_state.players_ready = True
        st.rerun()

    st.stop()

# === Config ===
players = st.session_state.player_names
target = 14

def king_card_label(pos):
    if pos >= 14:
        return "主牌→A"
    elif pos == 13:
        return "主牌→K"
    elif pos == 12:
        return "主牌→Q"
    elif pos == 11:
        return "主牌→J"
    else:
        return f"主牌→{pos}"

# === Game UI ===
st.title(f"🎯 Round {st.session_state.round_num}")
st.markdown("### Tap to rank players (1st and 2nd). Third is automatic.")
st.markdown("""
    <style>
    div[role="radiogroup"] label {
        font-size: 1.4em !important;
        padding: 0.6em 1em;
        display: flex;
        align-items: center;
        gap: 0.5em;
        margin-bottom: 0.3em;
    }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    first = st.radio("1st Place", list(players.values()), key="first_place", label_visibility="visible")
with col2:
    second = st.radio("2nd Place", [p for p in players.values() if p != first], key="second_place", label_visibility="visible")

if st.button("✅ Submit Round", use_container_width=True):
    reverse_map = {v: k for k, v in players.items()}
    first_pid = reverse_map[first]
    second_pid = reverse_map[second]
    third_pid = [pid for pid in players if pid not in [first_pid, second_pid]][0]

    status_at_start = st.session_state.status.copy()

    for pid in players:
        if st.session_state.status[pid] == "":
            if pid == first_pid:
                st.session_state.positions[pid] += 3
            elif pid == second_pid:
                st.session_state.positions[pid] += 1

    for pid in players:
        if st.session_state.positions[pid] >= target and st.session_state.status[pid] == "":
            st.session_state.status[pid] = "A1"
            st.session_state.fail_flags[pid]["A1"] = False
            st.session_state.fail_flags[pid]["A2"] = False

    for pid in players:
        if pid == first_pid:
            if st.session_state.status[pid] == "A1" and st.session_state.fail_flags[pid]["A1"]:
                st.session_state.status[pid] = "A2"
                st.session_state.fail_flags[pid]["A1"] = False
            elif st.session_state.status[pid] == "A2" and st.session_state.fail_flags[pid]["A2"]:
                st.session_state.status[pid] = "A3"
                st.session_state.fail_flags[pid]["A2"] = False
        else:
            if st.session_state.status[pid] == "A1":
                st.session_state.fail_flags[pid]["A1"] = True
            elif st.session_state.status[pid] == "A2":
                st.session_state.fail_flags[pid]["A2"] = True
            elif st.session_state.status[pid] == "A3":
                st.session_state.status[pid] = ""
                st.session_state.positions[pid] = 2
                st.session_state.fail_flags[pid]["A1"] = False
                st.session_state.fail_flags[pid]["A2"] = False
                st.session_state.history[pid].append(2)

    for pid in players:
        st.session_state.history[pid].append(st.session_state.positions[pid])

    current_king = king_card_label(st.session_state.positions[first_pid])
    st.session_state.prev_king_card = current_king

    if st.session_state.prev_winner == first_pid and status_at_start[first_pid] in ["A1", "A2", "A3"]:
        st.session_state.winner = players[first_pid]

    st.session_state.prev_winner = first_pid
    st.session_state.round_num += 1
    time.sleep(0.1)
    st.rerun()

# === Game State ===
if st.session_state.winner:
    st.success(f"🎉 Game over! {st.session_state.winner} has won the game! 🏆")
    st.balloons()

# Always show Reset Game button
if st.button("🔁 Reset Game", use_container_width=True, key="reset_game"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# === Player Status ===
st.markdown("---")
st.subheader("📊 Player Status")
for pid in players:
    tag = f" [{st.session_state.status[pid]}]" if st.session_state.status[pid] else ""
    st.markdown(f"**{players[pid]}**: Position {st.session_state.positions[pid]}{tag}")

if st.session_state.prev_king_card:
    st.markdown(f"**{st.session_state.prev_king_card}**")

# === Plot only after game ends ===
if st.session_state.winner:
    st.subheader("📈 Progress History")
    fig, ax = plt.subplots()
    rounds = list(range(len(st.session_state.history[1])))
    colors = ["black", "red", "green"]

    for i, pid in enumerate(players):
        y = st.session_state.history[pid]
        ax.plot(rounds, y, color=colors[i], marker='o', label=players[pid])

    ax.set_xticks(rounds)
    ax.set_xlabel("Round #")
    ax.set_ylabel("Position")
    ax.set_title("Player Advancement Journey")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
