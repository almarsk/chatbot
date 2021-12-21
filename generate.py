from pathlib import Path
from corpy.morphodita import Tagger
from ufal.morphodita import TaggedLemmasForms

description = """
Soubor generate obsahuje funkci generate, která dovede generovat konkrétní tvary slov na základě tagu.
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
            print(form.form, lemma.lemma, form.tag, sep="\t")

            # ... ale v chatbotu patrně asi spíš budete chtít vrátit
            # prostě první vygenerovaný tvar? ↓

# tímhle dodatečně přidáme funkci generate jako metodu na třídu Tagger,
# což není nutné, ale umožní nám to ji volat jako `tagger.generate(...)`
# místo `generate(tagger, ...)`
tagger.generate = generate

print(generate(tagger, lemma="letět", tag_wildcard="V?????????A"))