description = "Scénář 2 není určen k simulaci interakce s člověkem uvězněným v počítači, nýbrž pouze k testování."


def reply(user_reply, nick, conversation_state):
    conversation_state.setdefault("y", 0)
    conversation_state["y"] += 1
    return f"Nazdar! Jsem bot ze scénáře 2. Mluvím s uživatelem {nick!r}. Konverzace je ve stavu {conversation_state}. Poslední replika uživatele byla: {user_reply!r}."
