import streamlit as st
import time
import matplotlib.pyplot as plt

# === CONFIGURATION ===
players = {1: "Mom", 2: "Yehan", 3: "Nannan"}
target = 14

# === INIT STATE ===
if "positions" not in st.session_state:
    st.session_state.positions = {pid: 2 for pid in players}
    st.session_state.status = {pid: "" for pid in players}
    st.session_state.history = {pid: [2] for pid in players}
    st.session_state.fail_flags = {pid: {"A1": False, "A2": False} for pid in players}
    st.session_state.prev_winner = None
    st.session_state.prev_king_card = None
    st.session_state.round_num = 1
    st.session_state.winner = None

def king_card_label(pos):
    if pos >= 14:
        return "\u4e3b\u724c\u2192A"
    elif pos == 13:
        return "\u4e3b\u724c\u2192K"
    elif pos == 12:
        return "\u4e3b\u724c\u2192Q"
    elif pos == 11:
        return "\u4e3b\u724c\u2192J"
    else:
        return f"\u4e3b\u724c\u2192{pos}"

st.title(f"\u25b6\ufe0f Round {st.session_state.round_num}")
st.write("Select the players who got 1st and 2nd place. The 3rd will be auto-assigned.")

first = st.radio("1st Place", options=list(players.values()), key="first")
second = st.radio("2nd Place", options=[p for p in players.values() if p != first], key="second")

if st.button("Submit Round"):
    # Map names back to IDs
    reverse_map = {v: k for k, v in players.items()}
    first_pid = reverse_map[first]
    second_pid = reverse_map[second]
    third_pid = [pid for pid in players if pid not in [first_pid, second_pid]][0]

    status_at_start = st.session_state.status.copy()

    # === Position advancement ===
    for pid in players:
        if st.session_state.status[pid] == "":
            if pid == first_pid:
                st.session_state.positions[pid] += 3
            elif pid == second_pid:
                st.session_state.positions[pid] += 1

    # === Promote to A ===
    for pid in players:
        if st.session_state.positions[pid] >= target and st.session_state.status[pid] == "":
            st.session_state.status[pid] = "A"
            st.session_state.fail_flags[pid]["A1"] = False
            st.session_state.fail_flags[pid]["A2"] = False

    # === Handle A-level transitions ===
    for pid in players:
        if pid == first_pid:
            if st.session_state.status[pid] == "A1" and st.session_state.fail_flags[pid]["A1"]:
                st.session_state.status[pid] = "A2"
                st.session_state.fail_flags[pid]["A1"] = False
            elif st.session_state.status[pid] == "A2" and st.session_state.fail_flags[pid]["A2"]:
                st.session_state.status[pid] = "A3"
                st.session_state.fail_flags[pid]["A2"] = False
        else:
            if st.session_state.status[pid] == "A":
                st.session_state.status[pid] = "A1"
            elif st.session_state.status[pid] == "A1":
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

    # === Win Check ===
    if st.session_state.prev_winner == first_pid and status_at_start[first_pid] in ["A", "A1", "A2", "A3"]:
        st.session_state.winner = players[first_pid]

    st.session_state.prev_winner = first_pid
    st.session_state.round_num += 1
    st.rerun()

# === Show Status ===
if st.session_state.winner:
    st.success(f"\U0001F389 Game over! {st.session_state.winner} has won the game! \U0001F3C6")
    st.balloons()
else:
    st.subheader("Player Status")
    for pid in players:
        tag = f" [{st.session_state.status[pid]}]" if st.session_state.status[pid] else ""
        st.write(f"{players[pid]}: Position {st.session_state.positions[pid]}{tag}")

    if st.session_state.prev_king_card:
        st.write(f"**{st.session_state.prev_king_card}**")

    # Plot advancement
    st.subheader("Advancement History")
    chart_data = {players[pid]: st.session_state.history[pid] for pid in players}
    st.line_chart(chart_data)

    # Restart
    if st.button("Reset Game"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
