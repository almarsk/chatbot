from pathlib import Path
from corpy.morphodita import Tagger
from ufal.morphodita import TaggedLemmasForms

description = """
Scénář 4 obsahuje funkci generate, která dovede generovat konkrétní tvary slov na zákaldy tagu.
""".strip()

# Před použitím scénáře je potřeba stáhnout model, na základě kterého se
# značkování provede, a uložit ho ve stejném adresáři jako scénář.
# Seznam dostupných modelů pro systém MorphoDiTa je zde:
# http://ufal.mff.cuni.cz/morphodita#language_models
script_dir = Path(__file__).parent
model_path = str(script_dir / "czech-morfflex-pdt-161115" / "czech-morfflex-pdt-161115.tagger")
tagger = Tagger(model_path)

def generate(tagger: Tagger, lemma: str, tag_wildcard: str = None):
    """Vygeneruje tvary pro dané lemma na základě morfologie z taggeru.

    Výsledky lze omezit jen na některé tvary pomocí tag_wildcard, což je
    řetězec ve formátu popsaném zde:
    <http://ufal.mff.cuni.cz/morphodita/api-tutorial#tutorial_tag_wildcard>

    """
    # generování se nedělá pomocí taggeru, ale pomocí morfologického
    # slovníku, který je součástí taggeru a je tedy potřeba jej z něj
    # nejprve vytáhnout
    morpho = tagger._tagger.getMorpho()
    results = TaggedLemmasForms()
    morpho.generate(lemma, tag_wildcard, morpho.GUESSER, results)

    # výsledků může být víc (záleží na tag_wildcard)
    for lemma in results:
        for form in lemma.forms:
            # pro testovací účely prostě všechny vygenerované výsledky
            # vytiskneme (tvar, lemma i tag)...
            # print(form.form, lemma.lemma, form.tag, sep="\t")
            # ... ale v chatbotu patrně asi spíš budete chtít vrátit
            # prostě první vygenerovaný tvar? ↓
            return form.form

# tímhle dodatečně přidáme funkci generate jako metodu na třídu Tagger,
# což není nutné, ale umožní nám to ji volat jako `tagger.generate(...)`
# místo `generate(tagger, ...)`
tagger.generate = generate

def reply(user_reply, nick, cs):
    tagged = list(tagger.tag(user_reply or "", convert="strip_lemma_id"))


    if cs['row'] == 0:
        cs['row'] += 1
        return "Dobrý den, čím se v poslední době zabýváte??"

    else:

        cs['row'] += 1
        for token in tagged:

            if token.tag[0] == "V" and token.tag[7] == "1" and token.tag[10] == "A":
                print(token.tag)
                psd = [token.lemma]
                return f"Aha, a to {str(generate(tagger,lemma=psd[0], tag_wildcard='VB?P???2P?AA??-'))} bez doprovodu, nebo {str(generate(tagger,lemma=psd[0], tag_wildcard='VB?S???3P?AA??-'))} někdo s vámi?"

            else:
                return "aha"



print(reply("chodím na výlety","test", {"row":1, "col":1}))
