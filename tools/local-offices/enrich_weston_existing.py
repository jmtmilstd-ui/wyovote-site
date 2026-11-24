#!/usr/bin/env python3
"""Add person_id, href, term_end, and sort_key to existing Weston (and shared
federal/statewide) officeholder records, without changing names. Branch only.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "county_officials"

# Term ends: last general + ordinary term length, or statewide_officials_2008_2026.csv
# for Governor and other statewide offices. Federal Senate 6 years, House 2 years.

LEG = {
    "Ogden Driskill": dict(person_id="WY-DRISKILL-OGDEN", href="officials/driskill.html",
                           term_end="January 2031", sort_key="C01"),
    "Cheri Steinmetz": dict(person_id="WY-STEINMETZ-CHERI", href="officials/steinmetz.html",
                            term_end="January 2031", sort_key="C03"),
    "Chip Neiman": dict(person_id="WY-NEIMAN-CHIP", href="officials/neiman.html",
                        term_end="January 2027", sort_key="D01"),
    "JD Williams": dict(person_id="WY-WILLIAMS-JD", href="officials/williams.html",
                        term_end="January 2029", sort_key="D02"),
    "Troy Claycomb": dict(person_id="WY-CLAYCOMB-TROY", href="candidates/2026-primary/c/troy-claycomb.html",
                          term_end="January 2029", sort_key="D01E"),
}

COUNTY = {
    "Nathan Todd": dict(person_id="WY-TODD-NATHAN", href="candidates/2026-local/c/nathan-todd.html",
                        term_end="January 2031", sort_key="E01A"),
    "Ed Wagoner": dict(person_id="WY-WAGONER-ED", href="candidates/2024-local/c/ed-wagoner.html",
                       term_end="January 2029", sort_key="E01B"),
    "Garrett Borton": dict(person_id="WY-BORTON-GARRETT", href="candidates/2026-local/c/garrett-borton.html",
                           term_end="January 2031", sort_key="E01C"),
    "Marty Ertman": dict(person_id="WY-ERTMAN-MARTY", href="candidates/2024-local/c/marty-ertman.html",
                         term_end="January 2029", sort_key="E01D"),
    "Vera Huber": dict(person_id="WY-HUBER-VERA", href="candidates/2026-local/c/vera-huber.html",
                       term_end="January 2031", sort_key="E01E"),
    "Amber Green": dict(person_id="WY-PRELLGREEN-AMBER", href="candidates/2026-local/c/amber-prell-green.html",
                        term_end="January 2031", sort_key="E02", ballot_name="Amber Prell-Green"),
    "Susan Overman": dict(person_id="WY-OVERMAN-SUSAN", href="candidates/2026-local/c/susan-overman.html",
                          term_end="January 2031", sort_key="E03"),
    "Kara Lenardson": dict(person_id="WY-LENARDSON-KARA", href="candidates/2026-local/c/kara-lenardson.html",
                           term_end="January 2031", sort_key="E04"),
    "Bryan Colvard": dict(person_id="WY-COLVARD-BRYAN", href="candidates/2026-local/c/bryan-e-colvard.html",
                          term_end="January 2031", sort_key="E05"),
    "Michael Stulken": dict(person_id="WY-STULKEN-MICHAEL", href="candidates/2026-local/c/michael-stulken.html",
                            term_end="January 2031", sort_key="E06"),
    "Riki Kaiser": dict(person_id="WY-KAISER-RIKI", href="candidates/2026-local/c/riki-kaiser.html",
                        term_end="January 2031", sort_key="E07"),
    "Scott E. Beachler": dict(person_id="WY-BEACHLER-SCOTT", href="candidates/2026-local/c/scott-e-beachler.html",
                              term_end="January 2031", sort_key="E08"),
}

# Prefer the richer local/county Profile when a person also holds a precinct seat.
PRECINCT_HREF = {
    "Jon Tidyman": ("WY-TIDYMAN-JON", "candidates/precinct/c/tidyman-jon.html"),
    "Rick Wehri": ("WY-WEHRI-RICK", "candidates/precinct/c/wehri-rick.html"),
    "Megan Stith": ("WY-STITH-MEGAN", "candidates/precinct/c/stith-megan.html"),
    "Marty Ertman": ("WY-ERTMAN-MARTY", "candidates/2024-local/c/marty-ertman.html"),
    "Bill Lambert": ("WY-LAMBERT-BILL", "candidates/precinct/c/lambert-bill.html"),
    "Ed Wagoner": ("WY-WAGONER-ED", "candidates/2024-local/c/ed-wagoner.html"),
    "Marcia Lambert": ("WY-LAMBERT-MARCIA", "candidates/precinct/c/lambert-marcia.html"),
    "Jill Pischke": ("WY-PISCHKE-JILL", "candidates/precinct/c/pischke-jill.html"),
    "Clay Branscom": ("WY-BRANSCOM-CLAY", "candidates/precinct/c/branscom-clay.html"),
    "Charleen Haynes": ("WY-HAYNES-CHARLEEN", "candidates/precinct/c/haynes-charleen.html"),
    "Curtis Rankin": ("WY-RANKIN-CURTIS", "candidates/2024-local/c/curtis-rankin.html"),
    "Roxie Taft": ("WY-TAFT-ROXIE", "candidates/precinct/c/taft-roxie.html"),
    "Nathan Todd": ("WY-TODD-NATHAN", "candidates/2026-local/c/nathan-todd.html"),
    "Cody Barritt": ("WY-BARRITT-CODY", "candidates/precinct/c/barritt-cody.html"),
    "Chelsie Todd": ("WY-TODD-CHELSIE", "candidates/precinct/c/todd-chelsie.html"),
    "Ragina Barritt": ("WY-BARRITT-RAGINA", "candidates/precinct/c/barritt-ragina.html"),
    "Matt Conzelman": ("WY-CONZELMAN-MATT", "candidates/precinct/c/conzelman-matt.html"),
    "Kim Conzelman": ("WY-CONZELMAN-KIM", "candidates/precinct/c/conzelman-kim.html"),
    "Teresa I. Gross": ("WY-GROSS-TERESA", "candidates/precinct/c/gross-teresa.html"),
    "Robert W. Akers": ("WY-AKERS-ROBERT", "candidates/precinct/c/akers-robert.html"),
    "Joanna L. Akers": ("WY-AKERS-JOANNA", "candidates/precinct/c/akers-joanna.html"),
    "Kolby Pisciotti": ("WY-PISCIOTTI-KOLBY", "candidates/precinct/c/pisciotti-kolby.html"),
    "Jason Jenkins": ("WY-JENKINS-JASON", "candidates/2026-local/c/jason-jenkins.html"),
    "Riki Kaiser": ("WY-KAISER-RIKI", "candidates/2026-local/c/riki-kaiser.html"),
    "Suzanne Burrough": ("WY-BURROUGH-SUZANNE", "candidates/precinct/c/burrough-suzanne.html"),
}

FED = {
    "John Barrasso": dict(person_id="WY-BARRASSO-JOHN", href="candidates/2024-primary/c/john-barrasso.html",
                          term_end="January 2031", sort_key="A01"),
    "Cynthia Lummis": dict(person_id="WY-LUMMIS-CYNTHIA", href="officials/statewide/lummis.html",
                           term_end="January 2027", sort_key="A02"),
    "Harriet Hageman": dict(person_id="WY-HAGEMAN-HARRIET", href="candidates/2026-primary/c/harriet-hageman.html",
                            term_end="January 2027", sort_key="A03"),
    "Chuck Gray": dict(person_id="WY-GRAY-CHUCK", href="officials/statewide/gray.html",
                       term_end="January 2027", sort_key="A04"),
    "Mark Gordon": dict(person_id="WY-GORDON-MARK", href="officials/statewide/gordon.html",
                        term_end="January 2027", sort_key="B01"),
    "Eric Barlow": dict(person_id="WY-BARLOW-ERIC", href="officials/statewide/barlow.html",
                        term_end="January 2031", sort_key="B01E"),
    "Robert Short": dict(person_id="WY-SHORT-ROBERT", href="officials/statewide/short.html",
                         term_end="January 2031", sort_key="B02E"),
    "Kristi Racines": dict(person_id="WY-RACINES-KRISTI", href="officials/statewide/racines.html",
                           term_end="January 2031", sort_key="B03"),
    "Curt Meier": dict(person_id="WY-MEIER-CURTIS", href="officials/statewide/meier.html",
                       term_end="January 2031", sort_key="B04"),
    "Megan Degenfelder": dict(person_id="WY-DEGENFELDER-MEGAN", href="officials/statewide/degenfelder.html",
                              term_end="January 2027", sort_key="B05"),
    "Steve Harshman": dict(person_id="WY-HARSHMAN-STEVE", href="officials/statewide/harshman.html",
                           term_end="January 2031", sort_key="B05E"),
}

# Gray as House elect uses the same person record; term of the House seat he takes is January 2029.
GRAY_HOUSE_ELECT = dict(person_id="WY-GRAY-CHUCK", href="officials/statewide/gray.html",
                        term_end="January 2029", sort_key="A04E")
HAGEMAN_SENATE_ELECT = dict(person_id="WY-HAGEMAN-HARRIET", href="candidates/2026-primary/c/harriet-hageman.html",
                            term_end="January 2033", sort_key="A02E")


def apply_fields(holder: dict, fields: dict) -> None:
    for k, v in fields.items():
        if v and not holder.get(k):
            holder[k] = v


def enrich_holder(holder: dict, table: dict, succeeding_table: dict | None = None) -> None:
    name = holder.get("name")
    if name in table:
        apply_fields(holder, table[name])
    nxt = holder.get("succeeding")
    if nxt and isinstance(nxt, dict):
        nname = nxt.get("name")
        src = (succeeding_table or table).get(nname) or table.get(nname)
        if src:
            apply_fields(nxt, src)


def main() -> None:
    path = DATA / "weston.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for g in data["groups"]:
        if g["id"] == "state-senate":
            g["sort_key"] = g.get("sort_key") or "C"
            for o in g.get("offices") or []:
                for h in o.get("holders") or []:
                    enrich_holder(h, LEG)
        elif g["id"] == "state-house":
            g["sort_key"] = g.get("sort_key") or "D"
            for o in g.get("offices") or []:
                for h in o.get("holders") or []:
                    enrich_holder(h, LEG)
        elif g["id"] == "county":
            g["sort_key"] = g.get("sort_key") or "E"
            for o in g.get("offices") or []:
                for h in o.get("holders") or []:
                    enrich_holder(h, COUNTY)
        elif g["id"] == "precincts":
            g["sort_key"] = g.get("sort_key") or "P"
            for i, prec in enumerate(g.get("precincts") or [], start=1):
                prec["sort_key"] = prec.get("sort_key") or f"P{i:02d}"
                for o in prec.get("offices") or []:
                    for h in o.get("holders") or []:
                        rec = PRECINCT_HREF.get(h.get("name"))
                        if rec:
                            apply_fields(h, {"person_id": rec[0], "href": rec[1]})
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    shared = DATA / "shared" / "federal-statewide.json"
    fs = json.loads(shared.read_text(encoding="utf-8"))
    for g in fs["groups"]:
        if g["id"] == "federal":
            g["sort_key"] = g.get("sort_key") or "A"
        elif g["id"] == "statewide":
            g["sort_key"] = g.get("sort_key") or "B"
        for o in g.get("offices") or []:
            for h in o.get("holders") or []:
                if h.get("name") == "Cynthia Lummis":
                    enrich_holder(h, FED, {"Harriet Hageman": HAGEMAN_SENATE_ELECT})
                elif h.get("name") == "Harriet Hageman":
                    enrich_holder(h, FED, {"Chuck Gray": GRAY_HOUSE_ELECT})
                elif h.get("name") == "Chuck Gray":
                    enrich_holder(h, FED)  # current SOS term ends January 2027
                    if h.get("succeeding"):
                        enrich_holder({"name": "", "succeeding": h["succeeding"]}, FED)
                else:
                    enrich_holder(h, FED)
    shared.write_text(json.dumps(fs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("enriched weston.json and federal-statewide.json")


if __name__ == "__main__":
    main()
