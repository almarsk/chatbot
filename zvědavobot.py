from pathlib import Path
from corpy.morphodita import Tagger
from ufal.morphodita import TaggedLemmasForms

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
    <http://ufal.mff.cuni.cz/morphodita/api-tutorial#tutorial_tag_wildcard
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

            # ... ale v chatbotu patrně asi spíš budete chtít vrátit
            # prostě první vygenerovaný tvar? ↓
            return form.form
# tímhle dodatečně přidáme funkci generate jako metodu na třídu Tagger,
# což není nutné, ale umožní nám to ji volat jako `tagger.generate(...)`
# místo `generate(tagger, ...)`
Tagger.generate = generate

co_rika_bot = [

    ["no nic, to nevadí",
     "no vážně",
     "umím jen klást otázky a odpovídat na ně",
     "neznám, co to je?",
     "aha, o tom jsem nikdy neslyšel",
     "jen do toho",
     "jen tak",
     "ups, pardón",
     "já si rád povídám s lidmi, i když mi to zatím moc nejde"],

    ["dobrý den"],

    ["jmenuji se Zvědavobot"],

    ["těší mě"],

    ["mám se dobře, a vy?",
     "jak se máte?",
     "mě také, jak se máte?"],

    ["tak to rád slyším, čemu se v poslední době věnujete?",
     "a čemu se v poslední době věnujete?",
     "tak to mě mrzí, a čemu se v poslední době věnujete?"],

    ["to je náhoda"],

    ["ano, ani trochu", "v tom se vůbec nevyznám", "já nedělám nic", "já taky nic nedělám"],

    ["jak taky",
     "jakpak bych taky uměl",
     "no jakpak bych taky uměl",
     "jakpak bych taky dělal",
     "no jakpak bych taky dělal",
     "jakpak bych se taky vyznal",
     "no jak pak bych se taky vyznal"],

    ["a co dalšího ještě třeba děláte?"],

    ["a to vás baví?", "aha, jaké to bylo?"],

    ["tak to je skvělé",
     "víte vy co"],

    ["víte, já už nic dalšího říkat neumím, tak vám děkuji za tohle povídání a třeba zase někdy příště, nashledanou",
     "asi to tak má být"]

]

description = f"Zvědavobot se učí zdvořile rozprávět.\n Hovořte s ním prosím jako s člověkem."
bg_color = "#F6FD8E"
heading_color = "#FFE18D"
reply_bg = heading_color
reply_outline = heading_color

otagovano = []
replies = []
vysvetlovani = True

def scen(user_reply, nick, cs):
    low_up = str(user_reply).lower()
    tagged = list(tagger.tag(text=low_up or "", convert="strip_lemma_id"))
    otagovano.append(tagged)
    cs.setdefault("row", 0)
    cs.setdefault("col", 0)
    replies.append(user_reply)
    situace_prisudek = ""
    situace_predmet = ""
    situace_predlozka = ""
    index_prisudku = 100
    index_predmetu = 100
    index_predlozky = 100
    index_genitivu = 100
    lemma_prisudek = None
    lemma_predmet = None
    lemma_prepozice = None
    lemma_genitiv = None
    tag_predmetu = ""
    tag_genitivu = ""
    print(cs['row'])

    if cs['row'] != 5 and cs['row'] != 6:

        if "promiň" in low_up or ("nechci" in low_up and "mluvit" in low_up):
            return co_rika_bot[0][0]

        if "fakt?" in low_up or "vážně?" in low_up:
            return co_rika_bot[0][1]

        if "děláš" in low_up or "umíš" in low_up or "věnuješ" in low_up:
            return co_rika_bot[0][2]

        if ("víš" in low_up and "co je" in low_up) or "znáš" in low_up:
            return co_rika_bot[0][3]

        if cs['row'] != 0:
            if ("víš" in replies[len(replies)-1] and "co je" in replies[len(replies)-1]) \
                    or "znáš" in replies[len(replies)-1] and "to je" in low_up:
                return co_rika_bot[0][4]

        if "můžu" in low_up or ("kdyby" in low_up and "nevadilo" in low_up) and "?" in low_up:
            return co_rika_bot[0][5]

        if "proč se ptá" in low_up:
            return co_rika_bot[0][6]

        if "jsi" in low_up and ("drz" in low_up or "zvědav" in low_up):
            return co_rika_bot[0][7]

        if "baví" in low_up and "co" in low_up and "?" in low_up:
            return co_rika_bot[0][8]

        for imperativ in otagovano[len(otagovano)-1]:
            if imperativ.tag[1] == "i":
                    return "tohle zatím neumím, omlouvám se"

    if cs['row'] in (0, 1):
        cs['row'] += 1
        return co_rika_bot[cs["row"]][cs["col"]]

    if cs['row'] == 2:
        cs['row'] = 3
        if "těší" in low_up:
            cs['col'] = 2
            cs['row'] = 4
            return co_rika_bot[cs["row"]][cs["col"]]
        else:
            return co_rika_bot[cs["row"]][cs["col"]]

    if cs['row'] == 3:
        cs['col'] = 0
        cs['row'] = 4

        if "jak se" in low_up:
            return co_rika_bot[cs["row"]][cs["col"]]
        else:
            cs['col'] = 1
            return co_rika_bot[cs["row"]][cs["col"]]

    if cs['row'] == 4:
        cs['row'] = 5
        cs['col'] = 0

        if "dobře" in low_up or "fajn" in low_up or "skvěle" in low_up or "prima" in low_up \
                or "docela" in low_up or "jde to" in low_up:
            return co_rika_bot[cs["row"]][cs["col"]]

        if "nic" in low_up or "moc" in low_up or "špatně" in low_up or "líp" in low_up or "lépe" in low_up:
            cs['col'] = 2
            return co_rika_bot[cs["row"]][cs["col"]]

        else:
            cs['col'] = 1
            return co_rika_bot[cs["row"]][cs["col"]]

    if cs['row'] == 5:
        cs['row'] = 6
        cs['col'] = 0
        return co_rika_bot[cs["row"]][cs["col"]]

    if cs['row'] == 6:
        cs['row'] = 7

        if "spoust" in replies[len(replies)-2] or "různ" in replies[len(replies)-2] \
                or "od každého" in replies[len(replies)-2] or "všelijak" in replies[len(replies)-2] \
                or "všechno možné" in replies[len(replies)-2]:
            if "třeba" in replies[len(replies)-2] or "například" in replies[len(replies)-2]:
                situace_prisudek = ""

            else:
                situace_prisudek = "ruzne_veci"

        for prisudek in otagovano[len(otagovano)-2]:

            if prisudek.tag[0] == "V" and prisudek.tag[7] == "1":
                situace_prisudek = "prvni_osoba"
                index_prisudku = otagovano[len(otagovano)-2].index(prisudek)
                lemma_prisudek = prisudek.lemma

            if prisudek.lemma in ("zabývat", "věnovat", "přemýšlet", "myslet"):
                situace_prisudek = "zabyvat_venovat"
                index_prisudku = otagovano[len(otagovano)-2].index(prisudek)
                lemma_prisudek = prisudek.lemma

            if prisudek.tag[1] == "f":
                situace_prisudek = "infinitiv"
                lemma_prisudek = prisudek.lemma

            if prisudek.lemma == "chodit":
                situace_prisudek = "infinitiv"
                lemma_prisudek = prisudek.lemma

            if prisudek.lemma == "nic" or " nic" in replies[len(replies)-1]:
                situace_prisudek = "nic_moc"
                break

        for sloveso in otagovano[len(otagovano)-1]:
            if sloveso.tag[0] == "V" and sloveso.tag[7] == "2" and sloveso.tag[10] == "N":
                situace_prisudek = "2os"

        for predmet in otagovano[len(otagovano)-2]:

            if predmet.tag[0] == "N" and predmet.tag[4] != "2" and predmet.lemma != "spousta" and predmet.lemma != "doba":
                index_predmetu = otagovano[len(otagovano)-2].index(predmet)
                if index_predmetu >= index_prisudku or index_prisudku == 100:
                    situace_predmet = "předmět"
                    lemma_predmet = predmet.lemma
                    tag_predmetu = predmet.tag
            if situace_prisudek == "zabyvat_venovat":
                if predmet.tag[0] == "N" and predmet.tag[4] == "3":
                    index_predmetu = otagovano[len(otagovano) - 2].index(predmet)
                    if index_predmetu >= index_prisudku or index_prisudku == 100:
                        situace_predmet = "předmět"
                        lemma_predmet = predmet.lemma
                        tag_predmetu = predmet.tag

            if predmet.lemma == "práce":
                index_predmetu = otagovano[len(otagovano)-2].index(predmet)
                if index_predmetu == len(otagovano[len(otagovano)-2])-1:
                    situace_predmet = "práce"

        for genitiv in otagovano[len(otagovano)-2]:
            if situace_prisudek == "zabyvat_venovat":
                if genitiv.tag[0] == "N" and genitiv.tag[4] == "2" or "6":
                    index_genitivu = otagovano[len(otagovano)-2].index(genitiv)
                    if index_genitivu > index_predmetu:
                        situace_predmet = "předmět_s_genitivem"
                        lemma_genitiv = genitiv.lemma
                        tag_genitivu = genitiv.tag

        for predlozka in otagovano[len(otagovano)-2]:

            if predlozka.tag[0] == "R":
                index_predlozky = otagovano[len(otagovano)-2].index(predlozka)
                if index_predlozky + 1 == index_predmetu or index_predlozky + 2 == index_predmetu:
                    situace_predlozka = "prepozice"
                    lemma_prepozice = predlozka.lemma
                if index_predlozky + 1 == index_genitivu:
                    situace_predlozka = "prepozice_genitivu"
                    lemma_prepozice = predlozka.lemma

        '''print("situace prisudek:    " + situace_prisudek)
        print("situace predlozka:   " + situace_predlozka)
        print("situace predmet:     " + situace_predmet)
        print("")
        print("index prisudku:      " + str(index_prisudku))
        print("index predlozky:     " + str(index_predlozky))
        print("index predmetu:      " + str(index_predmetu))
        print("")
        print("lemma prisudku:      " + str(lemma_prisudek))
        print("predlozka:           " + str(lemma_prepozice))
        print("lemma predmetu:      " + str(lemma_predmet))
        print(otagovano[len(otagovano)-2])'''

        if situace_prisudek == "infinitiv":
            cs['col'] = 1
            if situace_predmet == "předmět":
                if situace_predlozka == "prepozice":
                    return f"{generate(tagger, lemma=lemma_predmet, tag_wildcard=str(tag_predmetu))} vůbec neumím"
                else:
                    return f"{generate(tagger, lemma=lemma_prisudek, tag_wildcard='Vf')} " \
                           f"{generate(tagger, lemma=lemma_predmet, tag_wildcard=str(tag_predmetu))} vůbec neumím"
            else:
                return f"{lemma_prisudek} vůbec neumím"

        if situace_prisudek == "prvni_osoba":
            cs['col'] = 2
            if situace_predmet == "předmět":
                if situace_predlozka == "prepozice":
                    return f"{generate(tagger, lemma=lemma_prisudek, tag_wildcard='Vf????????A')} " \
                           f"{generate(tagger, lemma=lemma_prepozice)} " \
                           f"{generate(tagger, lemma=lemma_predmet, tag_wildcard=str(tag_predmetu))} vůbec neumím"
                else:
                    return f"{generate(tagger, lemma=lemma_prisudek, tag_wildcard='Vf????????A')} " \
                           f"{generate(tagger, lemma=lemma_predmet, tag_wildcard=str(tag_predmetu))} vůbec neumím"
            else:
                return f"{generate(tagger, lemma=lemma_prisudek, tag_wildcard='Vf????????A')} vůbec neumím"

        if situace_prisudek == "zabyvat_venovat":
            if situace_predmet == "předmět_s_genitivem":
                if situace_predlozka == "prepozice_genitivu":
                    cs['col'] = 0
                    return f" {generate(tagger, lemma=lemma_predmet, tag_wildcard='????1')} " \
                           f"{generate(tagger, lemma=lemma_prepozice)} " \
                           f"{generate(tagger, lemma=lemma_genitiv, tag_wildcard=tag_genitivu)} " \
                           f"musí být pěkně složitá záležitost, nemám s tím vůbec žádné zkušenosti"
                else:
                    cs['col'] = 0
                    return f"s tím nemám vůbec žádné zkušenosti, " \
                           f"{generate(tagger, lemma=lemma_predmet, tag_wildcard='????1')}" \
                           f" {generate(tagger, lemma=lemma_genitiv, tag_wildcard=tag_genitivu)} " \
                           f"musí být pěkně složitá záležitost"
            else:
                cs['col'] = 4
                return f"v {generate(tagger, lemma=lemma_predmet, tag_wildcard='????6?????A')} se vůbec nevyznám"

        if situace_prisudek == "ruzne_veci":
            cs['col'] = 2
            return co_rika_bot[cs["row"]][cs["col"]]

        if situace_prisudek == "nic_moc":
            cs['col'] = 3
            return co_rika_bot[cs["row"]][cs["col"]]

        if situace_predmet == "předmět":
            cs['col'] = 4
            return f"v {generate(tagger, lemma=lemma_predmet, tag_wildcard='????6')} se vůbec nevyznám"

        if situace_predmet == "práce":
            cs['col'] = 0
            return f"s prací nemám vůbec žádné zkušenosti"

        if situace_prisudek == "2os":
            cs['col'] = 0
            return co_rika_bot[cs['row']][cs['col']]

        else:
            cs['col'] = 4
            return "v tom se vůbec nevyznám"

    if cs['row'] == 7:
        cs['row'] = 8

        if cs['col'] == 0: # <--- jak taky
            return co_rika_bot[cs["row"]][cs["col"]]

        if cs['col'] == 1: # <--- jak bych  taky uměl
            if "proč" in low_up or "jak to" in low_up:
                cs['col'] = 2
                return co_rika_bot[cs["row"]][cs["col"]]
            else:
                cs['col'] = 1
                return co_rika_bot[cs["row"]][cs["col"]]

        if cs['col'] in (2, 3): # <--- jak bych taky dělal
            if "proč" in low_up or "jak to" in low_up:
                cs['col'] = 4
                return co_rika_bot[cs["row"]][cs["col"]]

            else:
                cs['col'] = 3
                return co_rika_bot[cs["row"]][cs["col"]]

        if cs['col'] == 4: # <--- jak bych se taky vyznal
            if "proč" in low_up or "jak to" in low_up:
                cs['col'] = 6
                return co_rika_bot[cs["row"]][cs["col"]]

            else:
                cs['col'] = 5
                return co_rika_bot[cs["row"]][cs["col"]]

        else:
            cs['col'] = 0
            return co_rika_bot[cs["row"]][cs["col"]]

    if cs['row'] == 8:
        cs['row'] = 9
        cs['col'] = 0
        return co_rika_bot[cs["row"]][cs["col"]]

    if cs['row'] == 9:
        cs['row'] = 10

        for pricesti in otagovano[len(otagovano)-1]:
            if pricesti.tag[8] == "R":
                cs['col'] = 1
                return co_rika_bot[cs["row"]][cs["col"]]

        cs['col'] = 0
        return co_rika_bot[cs["row"]][cs["col"]]

    if cs['row'] == 10:
        cs['row'] = 11
        for lemma in otagovano[len(otagovano)-1]:
            if lemma.lemma == "ne" or lemma.lemma == "už" or lemma.lemma == "celek" or lemma.lemma == "začínat":
                cs['col'] = 1
                return co_rika_bot[cs["row"]][cs["col"]]

        if "ano" in low_up or " baví" in low_up \
                or "jo" in low_up or "ujde" in low_up or "zvládám" in low_up or "moc" in low_up or\
                "samozřejmě" in low_up or "jakpak by ne" in low_up or "jak pak by ne" in low_up:
            cs['col'] = 0
            return co_rika_bot[cs["row"]][cs["col"]]

        else:
            cs['col'] = 1
            return co_rika_bot[cs["row"]][cs["col"]]

    if cs['row'] == 11:
        if cs['col'] == 0:
            cs['row'] = 12
            cs['col'] = 0
            return co_rika_bot[cs["row"]][cs["col"]]

        if cs['col'] == 1:
            cs['row'] = 12
            cs['col'] = 1
            return co_rika_bot[cs["row"]][cs["col"]]

    if cs['row'] == 12:
        if cs['col'] == 0:
            return None
        else:
            cs['col'] = 0
            return co_rika_bot[cs["row"]][cs["col"]]


def gen(user_reply, nick, cs):
    tagged = list(tagger.tag(text=user_reply or "", convert="strip_lemma_id"))
    low_up = str(user_reply).lower()

    if cs['row'] == 5:
        if "ty?" in low_up or "jak?" in low_up:
            return "já taky, "

    if cs['row'] == 6:
        return ""

    if "jak to" in low_up and "?" in low_up:
        return "jsem přece jen nemyslící jazykový mechanismus, "

    if "vždyť" in low_up or "no tak" in low_up:
        return "pravda, "

    for verbum in otagovano[len(otagovano) - 1]:
        if "?" in low_up:
                if verbum.lemma == "být" and verbum.tag[7] == "2":
                    return "kdepak, jsem jen nemyslící jazykový mechanismus, "

                if verbum.lemma == "moci" and verbum.tag[7] == "2":
                    return "tak jo, "

                if verbum.lemma == "chtít" and verbum.tag[7] == "2":
                    return "ano, to by se mi líbilo"

    if "chtěl bys" in low_up:
        return "ano, to by se mi líbilo"

    if "jméno" in low_up and ("pěkn" in low_up or "hezk" in low_up or "super" in low_up or "skvěl" in low_up or "krásn" in low_up):
        return "děkuji, "

    if "nevadí" in low_up:
        return "tak to jsem rád, "

    else:
        return ""


def reply(user_reply, nick, cs):
    bzunda = scen(user_reply, nick, cs)

    if bzunda is None:
        return None
    else:
        return gen(user_reply, nick, cs) + bzunda


'''print("usr: " + reply("", "", {'row': 0, 'col': 0}))
print("usr: dobrý den")
print('bot: ' + reply("dobrý den", "", {'row': 1, 'col': 0}))
print("usr: Hezké jméno")
print('bot: ' + reply("Hezké jméno", "", {'row': 2, 'col': 0}))

print("usr: mě taky")'''

'''
print('bot: ' + reply("mě taky", "", {'row': 3, 'col': 0}))
print("usr: mám se dobře a ty?")
print('bot: ' + reply("mám se dobře a ty?", "", {'row': 4, 'col': 0}))
print("usr: jídlu docela")
print('bot: ' + reply("jídlu docela", "", {'row': 5, 'col': 0}))

print("usr: co je náhoda?")
print('bot: ' + reply("co je náhoda?", "", {'row': 6, 'col': 0}))'''
'''print("usr: jak to")
print('bot: ' + reply("jak to", "", {'row': 7, 'col': 0}))
print("usr: jak to?")
print('bot: ' + reply("jak to?", "", {'row': 8, 'col': 0}))
print("usr: tak se ptej")
print('bot: ' + reply("tak se ptej", "", {'row': 9, 'col': 0}))
print("usr: to nevadí, tak jindy")
print('bot: ' + reply("to nevadí, tak jindy", "", {'row': 10, 'col': 0}))'''












