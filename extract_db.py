import pandas as pd
from werkzeug.utils import secure_filename

db = "sqlite:///chatbot.db"

users = pd.read_sql("user", db, index_col="id")
replies = pd.read_sql("reply", db, index_col="id")

# --------------------------------- Tisk konverzací v přehledném formátu

# Výstup skriptu tištěný funkcí print() lze zapsat do souboru, když na
# konec příkazu připojíte tzv. přesměrování:
#
#   >soubor.txt

for user_id, user in users.iterrows():
    if user_id > 12 and user.nick != "test":
            header = f"Konverzace s uživatelem {user.nick!r}, id: {user_id}"
            print(header)
            print("=" * len(header))

            print("Metadata:")
            for col_name, value in user.iteritems():
                print(f"  {col_name}: {value!r}")

            print("Obsah konverzace:")
            conversation_with_user = replies.query("user_id == @user_id")
            for _, reply in conversation_with_user.iterrows():
                name = (
                    user.scenario
                    # rozdíl mezi botem a člověkem se pozná podle toho, že bot
                    # nemá u reply vyplněný sloupec reaction_ms
                    if pd.isnull(reply.reaction_ms)
                    else f"{user.nick} (po {reply.reaction_ms} ms)"
                )
                print(f"  {name}: {reply.content}")

            print()

# ------------------------------------------ Export konverzací do Excelu

# Exportuje se jedna velká sloučená tabulka za každou konverzaci, kde
# jsou v každém řádku obsaženy všechny informace. Tj. mění se jen
# informace týkající se repliky, informace ohledně uživatele (nick,
# hodnocení, komentář atp.) jsou ve všech řádcích stejné, jen se
# prokopírují ke každé replice.


def explicit_author_info(reaction_ms):
    return "bot" if pd.isnull(reaction_ms) else "uživatel"


replies = replies.join(users, on="user_id").groupby("user_id")
for _, conversation in replies:
    first_row = conversation.iloc[0]
    file_name = secure_filename(
        f"{first_row.scenario}-{first_row.nick}-{first_row.user_id}.xlsx"
    )
    # když už v tom jsme, můžeme ještě doplnit sloupec, který explicitně
    # uvádí autora repliky, odvozený ze sloupce reaction_ms
    conversation["author"] = conversation["reaction_ms"].map(explicit_author_info)
    conversation.to_excel(file_name)
