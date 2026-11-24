#!/usr/bin/env python3
"""Build per-county effective-dated officeholder history and January snapshots.

Preview only. Does not merge, publish, or touch schedule-stage.

  python3 tools/local-offices/build_county_history.py --county crook

Crook is implemented in this run. Shared federal, statewide, S01, H01, and
6th Judicial District / statewide judicial terms are reused from the Weston
history (those offices are the same people). Local Crook terms come from
official Crook County Clerk results. Names are never invented.
"""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

from legislative_office_notes import apply_to_groups
sys.path.insert(0, str(Path(__file__).resolve().parent))
import history_lib as H

ROOT = H.ROOT
RETRIEVED = "2026-11-23"
FM = H.FM
JAN3 = H.JAN3

# Official Crook County Clerk general-result URLs (as archived in SOURCES.md).
CG = {
    2012: ("https://www.crookcounty.wy.gov/General Election 2012 Official Results.pdf",
           "Crook County official 2012 general results"),
    2014: ("https://www.crookcounty.wy.gov/Canvas Block Style.pdf",
           "Crook County official 2014 general results"),
    2016: ("https://www.crookcounty.wy.gov/elected_officials/clerk/Election/2016_Election/2016 canvass block style.pdf",
           "Crook County official 2016 general results"),
    2018: ("https://www.crookcounty.wy.gov/2018 General Election Official Results.pdf",
           "Crook County official 2018 general results"),
    2020: ("https://www.crookcounty.wy.gov/Official Results General 2020.pdf",
           "Crook County official 2020 general results"),
    2022: ("https://www.crookcounty.wy.gov/elected_officials/clerk/Election/General Election Summary- Official Results.pdf",
           "Crook County official 2022 general results"),
    2024: ("https://www.crookcounty.wy.gov/elected_officials/clerk/Election/2024/Crook County Election Summary.pdf",
           "Crook County official 2024 general results"),
    2026: ("https://www.crookcounty.wy.gov/elected_officials/clerk/Election/2026/COUNTY ELECTION SUMMARY.pdf",
           "Crook County official 2026 general results"),
}
CP_2026 = ("https://www.crookcounty.wy.gov/elected_officials/clerk/Election/2026/Official Election Summary.pdf",
           "Crook County official 2026 primary results")
CLERK_ROSTER = "https://www.crookcounty.wy.gov/elected_officials/index.php"
DAY_APPT = {
    "label": "Sundance Times legal notice of the December 19, 2025 Crook County Commission proceedings (Baron retired December 31, 2025; DaNece Day appointed and took office January 1, 2026)",
    "url": "",
}
HULETT_PIONEER = {
    "label": "Wyoming Pioneer, May 21, 2026, reporting the May 12, 2026 Town of Hulett municipal election (87 of 200 voters; sworn June 3, 2026)",
    "url": "",
}
HULETT_NOTICE = {
    "label": "Wyoming Pioneer subsequent official-minutes-style council notices naming holdover Hulett council members serving with the May 2026 winners",
    "url": "",
}


def cg(year: int) -> dict:
    url, label = CG[year]
    return {"label": label, "url": url}


def build_crook():
    people: dict = {}
    P = H.person_factory(people)
    terms: list = []

    def T(**kw):
        terms.append(H.term(**kw))

    # Reused IDs (name index or already minted in the 114 worktree)
    P("WY-DEVISH-FRED", "Fred Devish", "Fred", "Devish", minted=False)
    P("WY-LATHAM-BOB", "Bob Latham", "Bob", "Latham", minted=False)
    P("WY-HAIAR-KEITH", "Keith Haiar", "Keith", "Haiar", minted=False)
    P("WY-DAVIS-JOHN", "John D. Davis", "John", "Davis", middle="D.", minted=False)
    P("WY-DENNIS-KELLY", "Kelly B. Dennis", "Kelly", "Dennis", middle="B.", aliases="Kelly Dennis", minted=False)
    P("WY-WHALEN-JEANNE", "Jeanne A. Whalen", "Jeanne", "Whalen", middle="A.", aliases="Jeanne Whalen", minted=False)
    P("WY-JONES-MELISSA", "Melissa Jones", "Melissa", "Jones", minted=False)
    P("WY-JUNDT-TAMMY", "Tammy Jundt", "Tammy", "Jundt", minted=False)
    P("WY-THOMAS-DAN", "Dan Thomas", "Dan", "Thomas", minted=False)
    P("WY-HODGE-JEFF", "Jeff Hodge", "Jeff", "Hodge", minted=False)
    P("WY-DAY-DANECE", "DaNece Day", "DaNece", "Day", aliases="Danece Day", minted=False, slug="danece-day")
    P("WY-CRAWFORD-JULIE", "Julie Crawford", "Julie", "Crawford",
      aliases="Julie Altaffer; Julie Altaffer Crawford", minted=False)
    P("WY-FROLANDER-MIKE", "Mike Frolander", "Mike", "Frolander",
      aliases="R. Michael Frolander; Michael Frolander; Mike Frolander", minted=False)
    P("WY-BARON-JOSEPH", "Joseph M. Baron", "Joseph", "Baron", middle="M.", minted=False)
    P("WY-STEVENS-ERIC", "Eric Stevens", "Eric", "Stevens", minted=False)
    P("WY-MARCHANT-BRAD", "Brad Marchant", "Brad", "Marchant", minted=False)
    P("WY-BLAKEMAN-KAIDEN", "Kaiden Blakeman", "Kaiden", "Blakeman", minted=False)
    P("WY-MAHONEY-RACHEL", "Rachel Mahoney", "Rachel", "Mahoney", minted=False)
    P("WY-RISING-CLINT", "Clint Rising", "Clint", "Rising", minted=False)
    P("WY-WOOD-ANDREA", "Andrea Wood", "Andrea", "Wood", aliases="Andrea Driskill Wood", minted=False)

    # Newly minted (not in the name index under these IDs)
    P("WY-STAHLA-STEVE", "Steve J. Stahla", "Steve", "Stahla", middle="J.")
    P("WY-FRITZ-LINDA", "Linda Fritz", "Linda", "Fritz")
    P("WY-WOODHILL-MARY", "Mary Woodhill", "Mary", "Woodhill")
    P("WY-CURREN-THERESA", "Theresa L. Curren", "Theresa", "Curren", middle="L.", aliases="Theresa Curren")
    P("WY-WARD-CHRISTINA", "Christina Ward", "Christina", "Ward")
    P("WY-HILTY-CALLIE", "Callie Hilty", "Callie", "Hilty")
    P("WY-KEYWORTH-TREVOR", "Trevor Keyworth", "Trevor", "Keyworth")
    P("WY-WILSON-JOE", "Joe Wilson", "Joe", "Wilson")
    P("WY-STEVENSON-RANDY", "Randy Stevenson", "Randy", "Stevenson")
    P("WY-BROOKS-PAUL", "Paul Brooks", "Paul", "Brooks")
    P("WY-GLENN-BENJAMIN", "Benjamin P. Glenn", "Benjamin", "Glenn", middle="P.", aliases="Benjamin Glenn")
    P("WY-BLAKEMAN-HEIDI", "Heidi Blakeman", "Heidi", "Blakeman",
      aliases="Heidi Blakeman Humpal; Heidi Humpal")
    P("WY-SMITH-AUSTIN-J", "Austin J. Smith", "Austin", "Smith", middle="J.", aliases="Austin Smith")
    P("WY-STEWART-ROBERT-E", "Robert E. Stewart", "Robert", "Stewart", middle="E.", aliases="Robert E Stewart")
    P("WY-PETERSEN-DALE", "Dale Petersen", "Dale", "Petersen")
    P("WY-TRIGG-ROBERT-D", "Robert D. Trigg", "Robert", "Trigg", middle="D.")
    P("WY-GALLEGOS-PAUL", "Paul Gallegos", "Paul", "Gallegos")
    P("WY-BRANDENBURG-KARLA", "Karla Brandenburg", "Karla", "Brandenburg")
    P("WY-NORTON-ROB", "Rob Norton", "Rob", "Norton")
    P("WY-COOK-JOHN-PH", "John Cook", "John", "Cook")
    P("WY-SPEED-KRISTY", "Kristy Speed", "Kristy", "Speed")
    P("WY-EDWARDS-SUZETTE", "Suzette Edwards", "Suzette", "Edwards")
    P("WY-HEYING-DUSTIN", "Dustin Heying", "Dustin", "Heying")
    P("WY-ROBERTS-TOM", "Tom Roberts", "Tom", "Roberts")
    P("WY-MURPHY-BRIAN-P", "Brian P. Murphy", "Brian", "Murphy", middle="P.")
    P("WY-SMITH-EMILY-PH", "Emily Smith", "Emily", "Smith")
    P("WY-KENNAH-BRIAN", "Brian Kennah", "Brian", "Kennah")
    P("WY-BEARS-ANDY", "Andy Bears", "Andy", "Bears")
    P("WY-BACKEN-BOZ", "Boz Backen", "Boz", "Backen")
    P("WY-SPRACHER-KIM", "Kim Spracher", "Kim", "Spracher")
    P("WY-MAHER-WOLFENSPERGER-KELLY", "Kelly Maher-Wolfensperger", "Kelly", "Maher-Wolfensperger",
      aliases="Kelly Maher")
    P("WY-ISTA-HANNAH", "Hannah Ista", "Hannah", "Ista")
    P("WY-WILLIAMS-CHASE-C", "Chase C. Williams", "Chase", "Williams", middle="C.")
    P("WY-MOTLEY-WILLIAM", "William Motley", "William", "Motley", aliases="Bill Motley; William (Bill) Motley")
    P("WY-GRAY-THAYNE", "Thayne Gray", "Thayne", "Gray")
    P("WY-ELLSBURY-WILL", "Will Ellsbury", "Will", "Ellsbury")
    P("WY-LENZ-COLTON", "Colton Lenz", "Colton", "Lenz")
    P("WY-WOLF-SHANE", "Shane Wolf", "Shane", "Wolf")
    P("WY-JAGEMANN-DAVE", "Dave Jagemann", "Dave", "Jagemann")
    P("WY-WADDELL-HEITH", "Heith Waddell", "Heith", "Waddell")
    P("WY-EDWARDS-MARLENE", "D. Marlene Edwards", "Marlene", "Edwards", aliases="D. Marlene Edwards")
    P("WY-BLAKEMAN-STEVEN-M", "Steven M. Blakeman", "Steven", "Blakeman", middle="M.")
    P("WY-CONNALLY-TOBY", "Toby Connally", "Toby", "Connally")
    P("WY-DEWEY-TRAVIS", "Travis Dewey", "Travis", "Dewey")
    P("WY-FOWLER-BRENT", "Brent Fowler", "Brent", "Fowler")
    P("WY-NEIMAN-SANDY", "Sandy Neiman", "Sandy", "Neiman")
    P("WY-RICHEY-BOB", "Bob Richey", "Bob", "Richey")
    P("WY-HIBBARD-ROBERT", "Robert Hibbard", "Robert", "Hibbard", aliases="Robin Hibbard; Robert (Robin) Hibbard")
    P("WY-COLEMAN-SHARON-D", "Sharon D. Coleman", "Sharon", "Coleman", middle="D.")
    P("WY-ERICKSON-MARK", "Mark Erickson", "Mark", "Erickson")
    P("WY-FENLASON-JOHN-ROBERT", "John-Robert B. Fenlason", "John-Robert", "Fenlason", middle="B.")
    P("WY-LINDMIER-CONNIE", "Connie Lindmier", "Connie", "Lindmier")
    P("WY-RAY-ED", "Ed Ray", "Ed", "Ray")
    P("WY-GOODSON-AMY", "Amy Goodson", "Amy", "Goodson")
    P("WY-MOLINE-GALEN", "Galen Moline", "Galen", "Moline")
    P("WY-GARMAN-TAYLOR", "Taylor Garman", "Taylor", "Garman")
    P("WY-BARON-KANODE-MAYLEE", "Maylee Baron-Kanode", "Maylee", "Baron-Kanode")
    P("WY-HOFER-COX-KIMBERLY", "Kimberly A. Hofer-Cox", "Kimberly", "Hofer-Cox", middle="A.")
    P("WY-GRAY-NEAL", "Neal Gray", "Neal", "Gray")
    P("WY-THOMPSON-PAM", "Pam Thompson", "Pam", "Thompson")
    P("WY-WILMER-MELANIE", "Melanie Wilmer", "Melanie", "Wilmer")
    P("WY-JORDAN-MARY-JAYNE", "Mary Jayne Jordan", "Mary Jayne", "Jordan")
    P("WY-MCKIM-KAY", "Kay McKim", "Kay", "McKim")
    P("WY-BOWMAN-EDWARDS-BARBARA", "Barbara Bowman-Edwards", "Barbara", "Bowman-Edwards")
    P("WY-HOWARD-PEGGY-K", "Peggy K. Howard", "Peggy", "Howard", middle="K.")
    P("WY-WILKERSON-TERRY", "Terry Wilkerson", "Terry", "Wilkerson")
    P("WY-BANKENBUSH-LILLY", "Lilly Ann Bankenbush", "Lilly Ann", "Bankenbush", aliases="Lilly Ann Bankenbusch")
    P("WY-BEAUDOIN-BONNIE-J", "Bonnie J. Beaudoin", "Bonnie", "Beaudoin", middle="J.",
      aliases="Bonnie J. Beaudin; Bonnie J. Beaudoin")
    P("WY-HANSEN-MARCIA", "Marcia Hansen", "Marcia", "Hansen")
    P("WY-BURGET-WANDA", "Wanda Burget", "Wanda", "Burget")
    P("WY-FUNDAUN-KIM", "Kim Fundaun", "Kim", "Fundaun", aliases="Kim Fountain; Kim Foundain")
    P("WY-GARMAN-WAYNE-W", "Wayne W. Garman", "Wayne", "Garman", middle="W.", aliases="Wayne W Garman")
    P("WY-ALTAFFER-LILY", "Lily Altaffer", "Lily", "Altaffer")
    P("WY-DEVISH-CASEY", "Casey Devish", "Casey", "Devish")
    jur = "Crook County"


    # County commissioners: two midterm seats (2014/2018/2022/2026) and one presidential seat (2012/2016/2020/2024).
    T(person_id="WY-STAHLA-STEVE", name="Steve J. Stahla", party="R", office_group="county",
      office="County Commissioners", jurisdiction=jur, term_start=FM[2015], term_end=FM[2019],
      election_year=2014, sources=[cg(2014)], ballot_name="STEVE J. STAHLA")
    T(person_id="WY-WHALEN-JEANNE", name="Jeanne A. Whalen", party="R", office_group="county",
      office="County Commissioners", jurisdiction=jur, term_start=FM[2015], term_end=FM[2019],
      election_year=2014, sources=[cg(2014)], ballot_name="JEANNE WHALEN")
    T(person_id="WY-WHALEN-JEANNE", name="Jeanne A. Whalen", party="R", office_group="county",
      office="County Commissioners", jurisdiction=jur, term_start=FM[2019], term_end=FM[2023],
      election_year=2018, sources=[cg(2018)], ballot_name="JEANNE WHALEN")
    T(person_id="WY-DEVISH-FRED", name="Fred Devish", party="R", office_group="county",
      office="County Commissioners", jurisdiction=jur, term_start=FM[2019], term_end=FM[2023],
      election_year=2018, sources=[cg(2018)])
    T(person_id="WY-DEVISH-FRED", name="Fred Devish", party="R", office_group="county",
      office="County Commissioners", jurisdiction=jur, term_start=FM[2023], term_end=FM[2027],
      election_year=2022, sources=[cg(2022)])
    T(person_id="WY-DEVISH-FRED", name="Fred Devish", party="R", office_group="county",
      office="County Commissioners", jurisdiction=jur, term_start=FM[2027], term_end=FM[2031],
      election_year=2026, sources=[cg(2026)])
    T(person_id="WY-LATHAM-BOB", name="Bob Latham", party="R", office_group="county",
      office="County Commissioners", jurisdiction=jur, term_start=FM[2023], term_end=FM[2027],
      election_year=2022, sources=[cg(2022)])
    T(person_id="WY-HAIAR-KEITH", name="Keith Haiar", party="R", office_group="county",
      office="County Commissioners", jurisdiction=jur, term_start=FM[2027], term_end=FM[2031],
      election_year=2026, sources=[cg(2026)])
    T(person_id="WY-DENNIS-KELLY", name="Kelly B. Dennis", party="R", office_group="county",
      office="County Commissioners", jurisdiction=jur, term_start=FM[2013], term_end=FM[2017],
      election_year=2012, sources=[cg(2012)], ballot_name="KELLY B. DENNIS")
    T(person_id="WY-DENNIS-KELLY", name="Kelly B. Dennis", party="R", office_group="county",
      office="County Commissioners", jurisdiction=jur, term_start=FM[2017], term_end=FM[2021],
      election_year=2016, sources=[cg(2016)], ballot_name="KELLY DENNIS")
    T(person_id="WY-DENNIS-KELLY", name="Kelly B. Dennis", party="R", office_group="county",
      office="County Commissioners", jurisdiction=jur, term_start=FM[2021], term_end=FM[2025],
      election_year=2020, sources=[cg(2020)])
    T(person_id="WY-DAVIS-JOHN", name="John D. Davis", party="R", office_group="county",
      office="County Commissioners", jurisdiction=jur, term_start=FM[2025], term_end=FM[2029],
      election_year=2024, sources=[cg(2024)])

    def row_office(pid, name, office, starts_ends, party="R", notes=""):
        for year, start, end in starts_ends:
            T(person_id=pid, name=name, party=party, office_group="county", office=office,
              jurisdiction=jur, term_start=start, term_end=end, election_year=year,
              sources=[cg(year)], notes=notes)

    row_office("WY-FRITZ-LINDA", "Linda Fritz", "County Clerk",
               [(2014, FM[2015], FM[2019]), (2018, FM[2019], FM[2023])])
    row_office("WY-JONES-MELISSA", "Melissa Jones", "County Clerk",
               [(2022, FM[2023], FM[2027]), (2026, FM[2027], FM[2031])])
    row_office("WY-WOODHILL-MARY", "Mary Woodhill", "County Treasurer",
               [(2014, FM[2015], FM[2019]), (2018, FM[2019], FM[2023])],
               notes="Surname read from official 2014 and 2018 block-canvass page images (WOODHILL).")
    row_office("WY-JUNDT-TAMMY", "Tammy Jundt", "County Treasurer",
               [(2022, FM[2023], FM[2027]), (2026, FM[2027], FM[2031])])
    row_office("WY-CURREN-THERESA", "Theresa L. Curren", "County Assessor",
               [(2014, FM[2015], FM[2019]), (2018, FM[2019], FM[2023])])
    row_office("WY-THOMAS-DAN", "Dan Thomas", "County Assessor",
               [(2022, FM[2023], FM[2027]), (2026, FM[2027], FM[2031])])
    row_office("WY-HODGE-JEFF", "Jeff Hodge", "County Sheriff",
               [(2014, FM[2015], FM[2019]), (2018, FM[2019], FM[2023]),
                (2022, FM[2023], FM[2027]), (2026, FM[2027], FM[2031])])
    row_office("WY-BARON-JOSEPH", "Joseph M. Baron", "County Attorney",
               [(2014, FM[2015], FM[2019]), (2018, FM[2019], FM[2023])])
    T(person_id="WY-BARON-JOSEPH", name="Joseph M. Baron", party="D", office_group="county",
      office="County Attorney", jurisdiction=jur, term_start=FM[2023], term_end="2026-01-01",
      election_year=2022, sources=[cg(2022), DAY_APPT],
      notes="Retired December 31, 2025. DaNece Day took office January 1, 2026.")
    T(person_id="WY-DAY-DANECE", name="DaNece Day", party="R", office_group="county",
      office="County Attorney", jurisdiction=jur, term_start="2026-01-01", term_end=FM[2027],
      how_took_office="appointed", election_year=None,
      sources=[DAY_APPT, {"label": "Crook County elected officials roster", "url": CLERK_ROSTER}],
      notes="Appointed December 19, 2025 to fill Joseph M. Baron unexpired term; took office January 1, 2026.")
    T(person_id="WY-DAY-DANECE", name="DaNece Day", party="R", office_group="county",
      office="County Attorney", jurisdiction=jur, term_start=FM[2027], term_end=FM[2031],
      election_year=2026, sources=[cg(2026)])
    row_office("WY-WARD-CHRISTINA", "Christina Ward", "Clerk of District Court",
               [(2014, FM[2015], FM[2019]), (2018, FM[2019], FM[2023])])
    T(person_id="WY-CRAWFORD-JULIE", name="Julie Crawford", party="R", office_group="county",
      office="Clerk of District Court", jurisdiction=jur, term_start=FM[2023], term_end=FM[2027],
      election_year=2022, sources=[cg(2022)], ballot_name="JULIE ALTAFFER",
      notes="2022 official ballot name Julie Altaffer. Same person as Julie Crawford (2026 ballot and current official roster).")
    T(person_id="WY-CRAWFORD-JULIE", name="Julie Crawford", party="R", office_group="county",
      office="Clerk of District Court", jurisdiction=jur, term_start=FM[2027], term_end=FM[2031],
      election_year=2026, sources=[cg(2026)], ballot_name="JULIE CRAWFORD")
    row_office("WY-FROLANDER-MIKE", "Mike Frolander", "County Coroner",
               [(2014, FM[2015], FM[2019]), (2018, FM[2019], FM[2023]), (2022, FM[2023], FM[2027])])
    T(person_id="WY-STEVENS-ERIC", name="Eric Stevens", party="R", office_group="county",
      office="County Coroner", jurisdiction=jur, term_start=FM[2027], term_end=FM[2031],
      election_year=2026, sources=[cg(2026)])


    # Sundance
    T(person_id="WY-BROOKS-PAUL", name="Paul Brooks", office_group="municipal",
      office="Sundance Mayor", jurisdiction="Town of Sundance", term_start=FM[2023], term_end=FM[2027],
      election_year=2022, sources=[cg(2022)])
    T(person_id="WY-MARCHANT-BRAD", name="Brad Marchant", office_group="municipal",
      office="Sundance Mayor", jurisdiction="Town of Sundance", term_start=FM[2027], term_end=FM[2031],
      election_year=2026, sources=[cg(2026)])
    for pid, name, year, start, end in [
        ("WY-STEVENSON-RANDY", "Randy Stevenson", 2020, FM[2021], FM[2025]),
        ("WY-WILSON-JOE", "Joe Wilson", 2020, FM[2021], FM[2025]),
        ("WY-HILTY-CALLIE", "Callie Hilty", 2022, FM[2023], FM[2027]),
        ("WY-MARCHANT-BRAD", "Brad Marchant", 2022, FM[2023], FM[2027]),
        ("WY-WILSON-JOE", "Joe Wilson", 2024, FM[2025], FM[2029]),
        ("WY-STEVENSON-RANDY", "Randy Stevenson", 2024, FM[2025], FM[2029]),
        ("WY-HILTY-CALLIE", "Callie Hilty", 2026, FM[2027], FM[2031]),
        ("WY-KEYWORTH-TREVOR", "Trevor Keyworth", 2026, FM[2027], FM[2031]),
    ]:
        T(person_id=pid, name=name, office_group="municipal", office="Sundance Town Council",
          jurisdiction="Town of Sundance", term_start=start, term_end=end, election_year=year,
          sources=[cg(year)])

    # Moorcroft
    T(person_id="WY-GLENN-BENJAMIN", name="Benjamin P. Glenn", office_group="municipal",
      office="Moorcroft Mayor", jurisdiction="Town of Moorcroft", term_start=FM[2023], term_end=FM[2027],
      election_year=2022, sources=[cg(2022)])
    T(person_id="WY-BLAKEMAN-HEIDI", name="Heidi Blakeman", office_group="municipal",
      office="Moorcroft Mayor", jurisdiction="Town of Moorcroft", term_start=FM[2027], term_end=FM[2031],
      election_year=2026, sources=[cg(2026)])
    for pid, name, year, start, end, note in [
        ("WY-GALLEGOS-PAUL", "Paul Gallegos", 2020, FM[2021], FM[2025], ""),
        ("WY-GLENN-BENJAMIN", "Benjamin P. Glenn", 2020, FM[2021], FM[2025], ""),
        ("WY-SMITH-AUSTIN-J", "Austin J. Smith", 2022, FM[2023], FM[2027], ""),
        ("WY-STEWART-ROBERT-E", "Robert E. Stewart", 2022, FM[2023], FM[2027], ""),
        ("WY-BLAKEMAN-HEIDI", "Heidi Blakeman", 2022, FM[2023], FM[2025], "2-year council seat (official 2022 contest)."),
        ("WY-PETERSEN-DALE", "Dale Petersen", 2022, FM[2023], FM[2025], "2-year council seat (official 2022 contest)."),
        ("WY-BLAKEMAN-HEIDI", "Heidi Blakeman", 2024, FM[2025], FM[2029], ""),
        ("WY-PETERSEN-DALE", "Dale Petersen", 2024, FM[2025], FM[2029], ""),
        ("WY-BLAKEMAN-KAIDEN", "Kaiden Blakeman", 2026, FM[2027], FM[2031], "4-year council seat."),
        ("WY-STEWART-ROBERT-E", "Robert E. Stewart", 2026, FM[2027], FM[2031], "4-year council seat."),
        ("WY-TRIGG-ROBERT-D", "Robert D. Trigg", 2026, FM[2027], FM[2029], "2-year council seat (official 2026 contest)."),
    ]:
        T(person_id=pid, name=name, office_group="municipal", office="Moorcroft Town Council",
          jurisdiction="Town of Moorcroft", term_start=start, term_end=end, election_year=year,
          sources=[cg(year)], notes=note)

    # Pine Haven
    T(person_id="WY-COOK-JOHN-PH", name="John Cook", office_group="municipal",
      office="Pine Haven Mayor", jurisdiction="Town of Pine Haven", term_start=FM[2021], term_end=FM[2023],
      election_year=2020, sources=[cg(2020)],
      notes="A new mayor was elected in 2022, so this 2020 term is treated as ending January 2023.")
    T(person_id="WY-BRANDENBURG-KARLA", name="Karla Brandenburg", office_group="municipal",
      office="Pine Haven Mayor", jurisdiction="Town of Pine Haven", term_start=FM[2023], term_end=FM[2027],
      election_year=2022, sources=[cg(2022)])
    T(person_id="WY-NORTON-ROB", name="Rob Norton", office_group="municipal",
      office="Pine Haven Mayor", jurisdiction="Town of Pine Haven", term_start=FM[2027], term_end=FM[2031],
      election_year=2026, sources=[cg(2026)])
    for pid, name, year, start, end, note in [
        ("WY-BRANDENBURG-KARLA", "Karla Brandenburg", 2020, FM[2021], FM[2023],
         "Elected mayor in 2022; council term treated as ending January 2023."),
        ("WY-SMITH-EMILY-PH", "Emily Smith", 2020, FM[2021], FM[2025], "Ordinary 4-year term from the official 2020 general."),
        ("WY-NORTON-ROB", "Rob Norton", 2022, FM[2023], FM[2027], "4-year council seat."),
        ("WY-SPEED-KRISTY", "Kristy Speed", 2022, FM[2023], FM[2027], "4-year council seat."),
        ("WY-EDWARDS-SUZETTE", "Suzette Edwards", 2022, FM[2023], FM[2025], "2-year council seat."),
        ("WY-HEYING-DUSTIN", "Dustin Heying", 2024, FM[2025], FM[2029], "4-year council seat."),
        ("WY-EDWARDS-SUZETTE", "Suzette Edwards", 2024, FM[2025], FM[2029], "4-year council seat."),
        ("WY-ROBERTS-TOM", "Tom Roberts", 2024, FM[2025], FM[2027], "2-year council seat."),
        ("WY-ROBERTS-TOM", "Tom Roberts", 2026, FM[2027], FM[2031], ""),
        ("WY-MURPHY-BRIAN-P", "Brian P. Murphy", 2026, FM[2027], FM[2031], ""),
    ]:
        T(person_id=pid, name=name, office_group="municipal", office="Pine Haven Town Council",
          jurisdiction="Town of Pine Haven", term_start=start, term_end=end, election_year=year,
          sources=[cg(year)], notes=note)

    # Hulett (May municipal election; not on the county November ballot).
    # Sworn June 3, 2026: in the current roster, not in any January 2015-2026 snapshot.
    T(person_id="WY-KENNAH-BRIAN", name="Brian Kennah", office_group="municipal",
      office="Hulett Mayor", jurisdiction="Town of Hulett", term_start="2026-06-03", term_end=FM[2029],
      election_year=2026, how_took_office="elected", confidence="medium",
      sources=[HULETT_PIONEER],
      notes="May 12, 2026 municipal election (not on the county November ballot). Town website was stale. Medium confidence pending an official canvass. Term end not confirmed from an official canvass.")
    T(person_id="WY-BEARS-ANDY", name="Andy Bears", office_group="municipal",
      office="Hulett Town Council", jurisdiction="Town of Hulett", term_start="2026-06-03", term_end=FM[2029],
      election_year=2026, confidence="medium", sources=[HULETT_PIONEER],
      notes="Elected May 12, 2026; sworn June 3, 2026. Medium confidence pending an official canvass.")
    T(person_id="WY-BACKEN-BOZ", name="Boz Backen", office_group="municipal",
      office="Hulett Town Council", jurisdiction="Town of Hulett", term_start="2026-06-03", term_end=FM[2029],
      election_year=2026, confidence="medium", sources=[HULETT_PIONEER],
      notes="Elected May 12, 2026; sworn June 3, 2026. Medium confidence pending an official canvass.")
    T(person_id="WY-SPRACHER-KIM", name="Kim Spracher", office_group="municipal",
      office="Hulett Town Council", jurisdiction="Town of Hulett", term_start="2026-06-03", term_end=FM[2029],
      how_took_office="holdover", election_year=None, confidence="medium",
      sources=[HULETT_NOTICE],
      notes="Named as a sitting council member in later Pioneer official-minutes-style notices. Historical Hulett seats before May 2026 are not yet collected.")
    T(person_id="WY-MAHER-WOLFENSPERGER-KELLY", name="Kelly Maher-Wolfensperger", office_group="municipal",
      office="Hulett Town Council", jurisdiction="Town of Hulett", term_start="2026-06-03", term_end=FM[2029],
      how_took_office="holdover", election_year=None, confidence="medium",
      sources=[HULETT_NOTICE],
      notes="Named as a sitting council member in later Pioneer official-minutes-style notices. Historical Hulett seats before May 2026 are not yet collected.")

    # Schools (CCSD #1)
    for pid, name, year, start, end, office in [
        ("WY-WOLF-SHANE", "Shane Wolf", 2020, FM[2021], FM[2025], "CCSD #1 Trustee, Hulett"),
        ("WY-ISTA-HANNAH", "Hannah Ista", 2022, FM[2023], FM[2027], "CCSD #1 Trustee, Hulett"),
        ("WY-MOTLEY-WILLIAM", "William (Bill) Motley", 2024, FM[2025], FM[2029], "CCSD #1 Trustee, Hulett"),
        ("WY-ISTA-HANNAH", "Hannah Ista", 2026, FM[2027], FM[2031], "CCSD #1 Trustee, Hulett"),
        ("WY-GRAY-THAYNE", "Thayne Gray", 2020, FM[2021], FM[2025], "CCSD #1 Trustee, Moorcroft"),
        ("WY-WILLIAMS-CHASE-C", "Chase C. Williams", 2022, FM[2023], FM[2027], "CCSD #1 Trustee, Moorcroft"),
        ("WY-GRAY-THAYNE", "Thayne Gray", 2024, FM[2025], FM[2029], "CCSD #1 Trustee, Moorcroft"),
        ("WY-WILLIAMS-CHASE-C", "Chase C. Williams", 2026, FM[2027], FM[2031], "CCSD #1 Trustee, Moorcroft"),
        ("WY-JAGEMANN-DAVE", "Dave Jagemann", 2020, FM[2021], FM[2025], "CCSD #1 Trustee, Sundance"),
        ("WY-WADDELL-HEITH", "Heith Waddell", 2020, FM[2021], FM[2025], "CCSD #1 Trustee, Sundance"),
        ("WY-ELLSBURY-WILL", "Will Ellsbury", 2024, FM[2025], FM[2029], "CCSD #1 Trustee, Sundance"),
        ("WY-LENZ-COLTON", "Colton Lenz", 2024, FM[2025], FM[2029], "CCSD #1 Trustee, Sundance"),
        ("WY-EDWARDS-MARLENE", "D. Marlene Edwards", 2022, FM[2023], FM[2027], "CCSD #1 Trustee, at-large"),
        ("WY-BLAKEMAN-STEVEN-M", "Steven M. Blakeman", 2022, FM[2023], FM[2027], "CCSD #1 Trustee, at-large"),
        ("WY-CONNALLY-TOBY", "Toby Connally", 2022, FM[2023], FM[2027], "CCSD #1 Trustee, at-large"),
        ("WY-DEWEY-TRAVIS", "Travis Dewey", 2026, FM[2027], FM[2031], "CCSD #1 Trustee, at-large"),
        ("WY-MAHONEY-RACHEL", "Rachel Mahoney", 2026, FM[2027], FM[2031], "CCSD #1 Trustee, at-large"),
        ("WY-CONNALLY-TOBY", "Toby Connally", 2026, FM[2027], FM[2031], "CCSD #1 Trustee, at-large"),
    ]:
        T(person_id=pid, name=name, office_group="schools", office=office,
          jurisdiction="Crook County School District #1", term_start=start, term_end=end,
          election_year=year, sources=[cg(year)])


    # CCMSD
    for pid, name, year, start, end, office in [
        ("WY-ERICKSON-MARK", "Mark Erickson", 2020, FM[2021], FM[2025], "CCMSD Trustee, Sundance"),
        ("WY-LINDMIER-CONNIE", "Connie Lindmier", 2020, FM[2021], FM[2025], "CCMSD Trustee, Hulett"),
        ("WY-RAY-ED", "Ed Ray", 2020, FM[2021], FM[2025], "CCMSD Trustee, Moorcroft"),
        ("WY-FOWLER-BRENT", "Brent Fowler", 2022, FM[2023], FM[2027], "CCMSD Trustee, at-large"),
        ("WY-NEIMAN-SANDY", "Sandy Neiman", 2022, FM[2023], FM[2027], "CCMSD Trustee, at-large"),
        ("WY-RICHEY-BOB", "Bob Richey", 2022, FM[2023], FM[2027], "CCMSD Trustee, Hulett"),
        ("WY-HIBBARD-ROBERT", "Robert (Robin) Hibbard", 2024, FM[2025], FM[2029], "CCMSD Trustee, Hulett"),
        ("WY-COLEMAN-SHARON-D", "Sharon D. Coleman", 2024, FM[2025], FM[2029], "CCMSD Trustee, Moorcroft"),
        ("WY-EDWARDS-MARLENE", "D. Marlene Edwards", 2024, FM[2025], FM[2029], "CCMSD Trustee, Sundance"),
        ("WY-ERICKSON-MARK", "Mark Erickson", 2026, FM[2027], FM[2031], "CCMSD Trustee, at-large"),
        ("WY-FENLASON-JOHN-ROBERT", "John-Robert B. Fenlason", 2026, FM[2027], FM[2031], "CCMSD Trustee, at-large"),
    ]:
        T(person_id=pid, name=name, office_group="special-districts", office=office,
          jurisdiction="Crook County Medical Services District", term_start=start, term_end=end,
          election_year=year, sources=[cg(year)])

    # Museum
    for pid, name, year, start, end, note in [
        ("WY-GRAY-NEAL", "Neal Gray", 2020, FM[2021], FM[2025], ""),
        ("WY-THOMPSON-PAM", "Pam Thompson", 2020, FM[2021], FM[2025], ""),
        ("WY-WILMER-MELANIE", "Melanie Wilmer", 2020, FM[2021], FM[2025], ""),
        ("WY-WOOD-ANDREA", "Andrea Wood", 2022, FM[2023], FM[2027],
         "Official 2022 contest was Vote For 3 with two named candidates."),
        ("WY-GOODSON-AMY", "Amy Goodson", 2022, FM[2023], FM[2027],
         "Official 2022 contest was Vote For 3 with two named candidates."),
        ("WY-MOLINE-GALEN", "Galen Moline", 2024, FM[2025], FM[2029],
         "Official 2024 contest was Vote For 3 with only one named candidate (Galen Moline) plus write-in totals; no other winner is named."),
        ("WY-GARMAN-TAYLOR", "Taylor Garman", 2026, FM[2027], FM[2031], ""),
        ("WY-BARON-KANODE-MAYLEE", "Maylee Baron-Kanode", 2026, FM[2027], FM[2031], ""),
        ("WY-HOFER-COX-KIMBERLY", "Kimberly A. Hofer-Cox", 2026, FM[2027], FM[2031], ""),
    ]:
        T(person_id=pid, name=name, office_group="special-districts", office="Museum District Trustee",
          jurisdiction="Crook County Museum District", term_start=start, term_end=end,
          election_year=year, sources=[cg(year)], notes=note)

    # Senior citizens district
    for pid, name, year, start, end, conf, note in [
        ("WY-BEAUDOIN-BONNIE-J", "Bonnie J. Beaudoin", 2020, FM[2021], FM[2025], "medium",
         "Surname read from the official 2020 general page image (Beaudoin / Beaudin). Official 2020 contest was Vote For 3 with two named candidates plus a write-in total; the third winner is not named."),
        ("WY-HANSEN-MARCIA", "Marcia Hansen", 2020, FM[2021], FM[2025], "high",
         "Official 2020 contest was Vote For 3 with two named candidates plus a write-in total; the third winner is not named."),
        ("WY-WILKERSON-TERRY", "Terry Wilkerson", 2022, FM[2023], FM[2027], "high", ""),
        ("WY-BANKENBUSH-LILLY", "Lilly Ann Bankenbush", 2022, FM[2023], FM[2027], "high", ""),
        ("WY-BOWMAN-EDWARDS-BARBARA", "Barbara Bowman-Edwards", 2024, FM[2025], FM[2029], "high",
         "Official 2024 contest was Vote For 3 with two named candidates plus write-in totals."),
        ("WY-HOWARD-PEGGY-K", "Peggy K. Howard", 2024, FM[2025], FM[2029], "high",
         "Official 2024 contest was Vote For 3 with two named candidates plus write-in totals."),
        ("WY-JORDAN-MARY-JAYNE", "Mary Jayne Jordan", 2026, FM[2027], FM[2031], "high", ""),
        ("WY-MCKIM-KAY", "Kay McKim", 2026, FM[2027], FM[2031], "high", ""),
    ]:
        T(person_id=pid, name=name, office_group="special-districts", office="CCSCSD Trustee",
          jurisdiction="Crook County Senior Citizens Special District", term_start=start, term_end=end,
          election_year=year, sources=[cg(year)], confidence=conf, notes=note)

    # CCNRD
    T(person_id="WY-FUNDAUN-KIM", name="Kim Fundaun", office_group="special-districts",
      office="CCNRD Rural", jurisdiction="Crook County Natural Resource District",
      term_start=FM[2021], term_end=FM[2023], election_year=2020, sources=[cg(2020)],
      notes="Official 2020 contest was CCNRD rural 2-year. The 2020 page-image surname was uncertain; the official 2022 text spelling Fundaun is used for the same person.")
    T(person_id="WY-GARMAN-WAYNE-W", name="Wayne W. Garman", office_group="special-districts",
      office="CCNRD Rural", jurisdiction="Crook County Natural Resource District",
      term_start=FM[2021], term_end=FM[2025], election_year=2020, sources=[cg(2020)],
      notes="Official 2020 rural 4-year seat.")
    T(person_id="WY-BURGET-WANDA", name="Wanda Burget", office_group="special-districts",
      office="CCNRD Rural", jurisdiction="Crook County Natural Resource District",
      term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[cg(2022)])
    T(person_id="WY-FUNDAUN-KIM", name="Kim Fundaun", office_group="special-districts",
      office="CCNRD Rural", jurisdiction="Crook County Natural Resource District",
      term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[cg(2022)])
    T(person_id="WY-GARMAN-WAYNE-W", name="Wayne W. Garman", office_group="special-districts",
      office="CCNRD Rural", jurisdiction="Crook County Natural Resource District",
      term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[cg(2024)])
    T(person_id="WY-RISING-CLINT", name="Clint Rising", office_group="special-districts",
      office="CCNRD Rural", jurisdiction="Crook County Natural Resource District",
      term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[cg(2026)])
    T(person_id="WY-WHALEN-JEANNE", name="Jeanne A. Whalen", office_group="special-districts",
      office="CCNRD Rural", jurisdiction="Crook County Natural Resource District",
      term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[cg(2026)],
      notes="Same person as the former county commissioner.")
    T(person_id="WY-DEVISH-CASEY", name="Casey Devish", office_group="special-districts",
      office="CCNRD Urban", jurisdiction="Crook County Natural Resource District",
      term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[cg(2024)],
      notes="Official 2020 and 2022 urban contests were write-in only and no winner is named.")
    T(person_id="WY-ALTAFFER-LILY", name="Lily Altaffer", office_group="special-districts",
      office="CCNRD At-large", jurisdiction="Crook County Natural Resource District",
      term_start=FM[2021], term_end=FM[2025], election_year=2020, sources=[cg(2020)])
    T(person_id="WY-ALTAFFER-LILY", name="Lily Altaffer", office_group="special-districts",
      office="CCNRD At-large", jurisdiction="Crook County Natural Resource District",
      term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[cg(2024)])

    # Shared federal / statewide / S01 / H01 / judicial from Weston terms
    weston_path = H.HISTORY / "weston" / "terms.json"
    weston = json.loads(weston_path.read_text())
    shared_groups = {"federal", "statewide", "judicial"}
    copied = 0
    for t in weston["terms"]:
        og = t.get("office_group")
        office = t.get("office") or ""
        # Crook shares S01 and H01 with Weston; do not copy Weston-only S03 or H02.
        if og in shared_groups or (
            og == "state-senate" and "Senate District 1" in office
        ) or (
            og == "state-house" and "House District 1" in office
        ):
            rec = deepcopy(t)
            if rec["office_group"] == "judicial" and rec.get("election_year") in CG:
                rec.setdefault("sources", [])
                rec["sources"] = list(rec["sources"]) + [cg(rec["election_year"])]
            terms.append(rec)
            copied += 1

    H.attach_people_from_terms(terms, people)

    expected = {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [
            ("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
            ("State Treasurer", 1), ("Superintendent of Public Instruction", 1),
        ],
        "state-senate": [("Senate District 1 (S01)", 1)],
        "state-house": [("House District 1 (H01)", 1)],
        "county": [
            ("County Commissioners", 3), ("County Clerk", 1), ("County Treasurer", 1),
            ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
            ("Clerk of District Court", 1), ("County Coroner", 1),
        ],
        "municipal": [
            ("Sundance Mayor", 1), ("Sundance Town Council", 4),
            ("Moorcroft Mayor", 1), ("Moorcroft Town Council", 4),
            ("Pine Haven Mayor", 1), ("Pine Haven Town Council", 4),
            ("Hulett Mayor", 1), ("Hulett Town Council", 4),
        ],
        "schools": [
            ("CCSD #1 Trustee, Hulett", 2), ("CCSD #1 Trustee, Moorcroft", 2),
            ("CCSD #1 Trustee, Sundance", 2), ("CCSD #1 Trustee, at-large", 3),
        ],
        "special-districts": [
            ("CCMSD Trustee, at-large", 2), ("CCMSD Trustee, Hulett", 1),
            ("CCMSD Trustee, Moorcroft", 1), ("CCMSD Trustee, Sundance", 1),
            ("Museum District Trustee", 3),
            ("CCSCSD Trustee", 3),
            ("CCNRD Rural", 3), ("CCNRD Urban", 1), ("CCNRD At-large", 1),
        ],
    }

    judicial_note = (
        "Supreme Court justices are the five who were in office this January, using official Wyoming Judicial Branch "
        "appointment and retirement dates together with official retention results. District and circuit rows are the "
        "6th Judicial District judges (the district also includes Campbell and Weston) who appeared on a Crook County "
        "official retention ballot in an adjoining cycle; those local benches may be incomplete."
    )
    special_note = (
        "Write-in-only contests without a named winner are not filled (including the official 2026 Museum trustee 2-year "
        "seat and the official 2020 and 2022 CCNRD Urban seats). Some Vote For N contests listed fewer named candidates "
        "than N; those extra seats are marked Not yet collected and are not invented."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. Official Crook primary PDFs for "
        "2010-2026 are archived under /workspace/wyoleg/local-results/crook/<year>/. The current (November 2026) "
        "precinct roster is in data/county_officials/crook.json, from the official 2026 primary (named winners only)."
    )

    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Crook", county_number=18, slug="crook", terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Crook", slug="crook")
    print(f"wrote {terms_path}")
    print(f"terms {len(terms)} (including {copied} shared federal/statewide/legislature/judicial terms)")
    print(f"people_additions +{n_people} offices_held +{n_off} thin_profiles +{n_prof}")
    H.print_coverage(coverage_all)
    return people, terms, coverage_all


def _holder(*, name, person_id, people, party="", term_end="", sources=None, notes="",
            ballot_name="", confidence="high", succeeding=None, href=None, role=""):
    p = people.get(person_id) or {}
    slug = p.get("slug") or ""
    if href is None:
        href = f"candidates/local-history/c/{slug}.html" if slug else ""
    h = {
        "name": name,
        "person_id": person_id,
        "sources": sources or [],
        "party": party,
        "term_end": term_end,
        "confidence": confidence,
    }
    if href:
        h["href"] = href
    if notes:
        h["notes"] = notes
    if ballot_name:
        h["ballot_name"] = ballot_name
    if role:
        h["role"] = role
    if succeeding:
        h["succeeding"] = succeeding
    return h


def update_crook_json(people: dict):
    path = ROOT / "data" / "county_officials" / "crook.json"
    data = json.loads(path.read_text())
    data["as_of"] = "2026-11-23"
    data["term_switch_date"] = "2027-01-04"
    data["intro"] = (
        "Names are the people in office today. Where the latest general election chose a different person, "
        "that change is shown beside the name. Those elects take office in January."
    )
    data["intro_after_switch"] = "Names are the people in office today."

    id_map = {
        "Ogden Driskill": ("WY-DRISKILL-OGDEN", "R", "January 2027", "officials/driskill.html"),
        "Chip Neiman": ("WY-NEIMAN-CHIP", "R", "January 2027", "officials/neiman.html"),
        "Fred Devish": ("WY-DEVISH-FRED", "R", "January 2031", None),
        "Bob Latham": ("WY-LATHAM-BOB", "R", "January 2027", None),
        "John D. Davis": ("WY-DAVIS-JOHN", "R", "January 2029", None),
        "Melissa Jones": ("WY-JONES-MELISSA", "R", "January 2031", None),
        "Tammy Jundt": ("WY-JUNDT-TAMMY", "R", "January 2031", None),
        "Dan Thomas": ("WY-THOMAS-DAN", "R", "January 2031", None),
        "Jeff Hodge": ("WY-HODGE-JEFF", "R", "January 2031", None),
        "DaNece Day": ("WY-DAY-DANECE", "R", "January 2031", None),
        "Julie Crawford": ("WY-CRAWFORD-JULIE", "R", "January 2031", None),
        "Michael Frolander": ("WY-FROLANDER-MIKE", "R", "January 2027", None),
    }
    for g in data["groups"]:
        for o in g.get("offices") or []:
            for h in o.get("holders") or []:
                rec = id_map.get(h.get("name"))
                if not rec:
                    continue
                pid, party, term_end, href = rec
                h["person_id"] = pid
                h.setdefault("party", party)
                h["term_end"] = term_end
                p = people.get(pid) or {}
                if href:
                    h["href"] = href
                elif p.get("slug") and not h.get("href"):
                    h["href"] = f"candidates/local-history/c/{p['slug']}.html"
                if h.get("name") == "Julie Crawford":
                    h["notes"] = "2022 official ballot name Julie Altaffer. Same person as the 2026 ballot and current official roster."
                if h.get("name") == "DaNece Day":
                    h["notes"] = "Appointed December 19, 2025 to fill Joseph M. Baron unexpired term; took office January 1, 2026; elected November 2026."
                suc = h.get("succeeding") or {}
                suc_map = {
                    "Troy Claycomb": "WY-CLAYCOMB-TROY",
                    "Keith Haiar": "WY-HAIAR-KEITH",
                    "Eric Stevens": "WY-STEVENS-ERIC",
                }
                if suc.get("name") in suc_map:
                    suc["person_id"] = suc_map[suc["name"]]
                    suc.setdefault("takes_office", "January")
                    sp = people.get(suc["person_id"]) or {}
                    if sp.get("slug"):
                        suc["href"] = f"candidates/local-history/c/{sp['slug']}.html"
                    h["succeeding"] = suc

    def suc(name, pid, party="", sources=None, term_end="January 2031"):
        p = people.get(pid) or {}
        rec = {
            "name": name,
            "person_id": pid,
            "party": party,
            "takes_office": "January",
            "term_end": term_end,
            "sources": sources or [cg(2026)],
        }
        if p.get("slug"):
            rec["href"] = f"candidates/local-history/c/{p['slug']}.html"
        return rec


    municipal = {
        "id": "municipal",
        "title": "Municipal offices",
        "sort_key": "F",
        "note": (
            "Sundance, Moorcroft, and Pine Haven appear on the official Crook County November general ballot. "
            "Hulett runs its own May municipal election. The Town of Hulett website was stale at the time of this research; "
            "current Hulett names are from the Wyoming Pioneer report of the May 12, 2026 election and later council notices, marked medium. "
            "Historical Hulett seats before May 2026 are not yet collected."
        ),
        "offices": [
            {"office": "Sundance Mayor", "layout": "office-and-name", "sort_key": "F01", "holders": [_holder(
                name="Paul Brooks", person_id="WY-BROOKS-PAUL", people=people, term_end="January 2027",
                sources=[cg(2022)], succeeding=suc("Brad Marchant", "WY-MARCHANT-BRAD"))]},
            {"office": "Sundance Town Council", "layout": "heading-then-names", "sort_key": "F02", "holders": [
                _holder(name="Callie Hilty", person_id="WY-HILTY-CALLIE", people=people, term_end="January 2031",
                        sources=[cg(2022), cg(2026)], notes="Re-elected November 2026; continues in January."),
                _holder(name="Brad Marchant", person_id="WY-MARCHANT-BRAD", people=people, term_end="January 2027",
                        sources=[cg(2022)], notes="Leaves the council in January when he takes office as mayor.",
                        succeeding=suc("Trevor Keyworth", "WY-KEYWORTH-TREVOR")),
                _holder(name="Joe Wilson", person_id="WY-WILSON-JOE", people=people, term_end="January 2029",
                        sources=[cg(2020), cg(2024)]),
                _holder(name="Randy Stevenson", person_id="WY-STEVENSON-RANDY", people=people, term_end="January 2029",
                        sources=[cg(2020), cg(2024)]),
            ]},
            {"office": "Moorcroft Mayor", "layout": "office-and-name", "sort_key": "F03", "holders": [_holder(
                name="Benjamin P. Glenn", person_id="WY-GLENN-BENJAMIN", people=people, term_end="January 2027",
                sources=[cg(2022)], succeeding=suc("Heidi Blakeman", "WY-BLAKEMAN-HEIDI"))]},
            {"office": "Moorcroft Town Council", "layout": "heading-then-names", "sort_key": "F04", "holders": [
                _holder(name="Austin J. Smith", person_id="WY-SMITH-AUSTIN-J", people=people, term_end="January 2027",
                        sources=[cg(2022)], succeeding=suc("Kaiden Blakeman", "WY-BLAKEMAN-KAIDEN")),
                _holder(name="Robert E. Stewart", person_id="WY-STEWART-ROBERT-E", people=people, term_end="January 2031",
                        sources=[cg(2022), cg(2026)], notes="Re-elected November 2026 to a 4-year council seat; continues in January."),
                _holder(name="Heidi Blakeman", person_id="WY-BLAKEMAN-HEIDI", people=people, term_end="January 2027",
                        sources=[cg(2024)], notes="Leaves the council in January when she takes office as mayor.",
                        succeeding=suc("Robert D. Trigg", "WY-TRIGG-ROBERT-D", term_end="January 2029")),
                _holder(name="Dale Petersen", person_id="WY-PETERSEN-DALE", people=people, term_end="January 2029",
                        sources=[cg(2024)]),
            ]},
            {"office": "Pine Haven Mayor", "layout": "office-and-name", "sort_key": "F05", "holders": [_holder(
                name="Karla Brandenburg", person_id="WY-BRANDENBURG-KARLA", people=people, term_end="January 2027",
                sources=[cg(2022)], succeeding=suc("Rob Norton", "WY-NORTON-ROB"))]},
            {"office": "Pine Haven Town Council", "layout": "heading-then-names", "sort_key": "F06", "holders": [
                _holder(name="Rob Norton", person_id="WY-NORTON-ROB", people=people, term_end="January 2027",
                        sources=[cg(2022)], notes="Leaves the council in January when he takes office as mayor.",
                        succeeding=suc("Tom Roberts", "WY-ROBERTS-TOM")),
                _holder(name="Kristy Speed", person_id="WY-SPEED-KRISTY", people=people, term_end="January 2027",
                        sources=[cg(2022)], succeeding=suc("Brian P. Murphy", "WY-MURPHY-BRIAN-P")),
                _holder(name="Dustin Heying", person_id="WY-HEYING-DUSTIN", people=people, term_end="January 2029",
                        sources=[cg(2024)]),
                _holder(name="Suzette Edwards", person_id="WY-EDWARDS-SUZETTE", people=people, term_end="January 2029",
                        sources=[cg(2024)]),
                _holder(name="Tom Roberts", person_id="WY-ROBERTS-TOM", people=people, term_end="January 2027",
                        sources=[cg(2024)], notes="2024 2-year council seat; re-elected November 2026."),
            ]},
            {"office": "Hulett Mayor", "layout": "office-and-name", "sort_key": "F07", "holders": [_holder(
                name="Brian Kennah", person_id="WY-KENNAH-BRIAN", people=people, term_end="",
                sources=[HULETT_PIONEER], confidence="medium",
                notes="Elected May 12, 2026 and sworn June 3, 2026. Medium confidence pending an official canvass. The town website was stale.")]},
            {"office": "Hulett Town Council", "layout": "heading-then-names", "sort_key": "F08", "holders": [
                _holder(name="Andy Bears", person_id="WY-BEARS-ANDY", people=people, sources=[HULETT_PIONEER],
                        confidence="medium", notes="Elected May 12, 2026; sworn June 3, 2026."),
                _holder(name="Boz Backen", person_id="WY-BACKEN-BOZ", people=people, sources=[HULETT_PIONEER],
                        confidence="medium", notes="Elected May 12, 2026; sworn June 3, 2026."),
                _holder(name="Kim Spracher", person_id="WY-SPRACHER-KIM", people=people, sources=[HULETT_NOTICE],
                        confidence="medium", notes="Holdover named in later Pioneer council notices. Historical Hulett seats before May 2026 are not yet collected."),
                _holder(name="Kelly Maher-Wolfensperger", person_id="WY-MAHER-WOLFENSPERGER-KELLY", people=people,
                        sources=[HULETT_NOTICE], confidence="medium",
                        notes="Holdover named in later Pioneer council notices. Historical Hulett seats before May 2026 are not yet collected."),
            ]},
        ],
    }

    schools = {
        "id": "schools", "title": "School boards", "sort_key": "G",
        "offices": [
            {"office": "CCSD #1 Trustee, Hulett", "layout": "heading-then-names", "holders": [
                _holder(name="Hannah Ista", person_id="WY-ISTA-HANNAH", people=people, term_end="January 2031",
                        sources=[cg(2022), cg(2026)], notes="Re-elected November 2026; continues in January."),
                _holder(name="William (Bill) Motley", person_id="WY-MOTLEY-WILLIAM", people=people,
                        term_end="January 2029", sources=[cg(2024)]),
            ]},
            {"office": "CCSD #1 Trustee, Moorcroft", "layout": "heading-then-names", "holders": [
                _holder(name="Chase C. Williams", person_id="WY-WILLIAMS-CHASE-C", people=people, term_end="January 2031",
                        sources=[cg(2022), cg(2026)], notes="Re-elected November 2026; continues in January."),
                _holder(name="Thayne Gray", person_id="WY-GRAY-THAYNE", people=people, term_end="January 2029",
                        sources=[cg(2020), cg(2024)]),
            ]},
            {"office": "CCSD #1 Trustee, Sundance", "layout": "heading-then-names", "holders": [
                _holder(name="Will Ellsbury", person_id="WY-ELLSBURY-WILL", people=people, term_end="January 2029",
                        sources=[cg(2024)]),
                _holder(name="Colton Lenz", person_id="WY-LENZ-COLTON", people=people, term_end="January 2029",
                        sources=[cg(2024)]),
            ]},
            {"office": "CCSD #1 Trustee, at-large", "layout": "heading-then-names", "holders": [
                _holder(name="D. Marlene Edwards", person_id="WY-EDWARDS-MARLENE", people=people, term_end="January 2027",
                        sources=[cg(2022)], succeeding=suc("Travis Dewey", "WY-DEWEY-TRAVIS")),
                _holder(name="Steven M. Blakeman", person_id="WY-BLAKEMAN-STEVEN-M", people=people, term_end="January 2027",
                        sources=[cg(2022)], succeeding=suc("Rachel Mahoney", "WY-MAHONEY-RACHEL")),
                _holder(name="Toby Connally", person_id="WY-CONNALLY-TOBY", people=people, term_end="January 2031",
                        sources=[cg(2022), cg(2026)], notes="Re-elected November 2026; continues in January."),
            ]},
        ],
    }


    special = {
        "id": "special-districts", "title": "Special districts", "sort_key": "H",
        "note": (
            "The official 2026 Museum trustee 2-year contest was write-in only and no winner is named; that seat is not filled here. "
            "The official 2024 Museum District and Senior District contests were Vote For 3 with fewer named candidates than three; "
            "unnamed seats are not invented."
        ),
        "offices": [
            {"office": "CCMSD Trustee, at-large", "layout": "heading-then-names", "holders": [
                _holder(name="Brent Fowler", person_id="WY-FOWLER-BRENT", people=people, term_end="January 2027",
                        sources=[cg(2022)], succeeding=suc("Mark Erickson", "WY-ERICKSON-MARK")),
                _holder(name="Sandy Neiman", person_id="WY-NEIMAN-SANDY", people=people, term_end="January 2027",
                        sources=[cg(2022)], succeeding=suc("John-Robert B. Fenlason", "WY-FENLASON-JOHN-ROBERT")),
            ]},
            {"office": "CCMSD Trustee, Hulett", "layout": "heading-then-names", "holders": [
                _holder(name="Bob Richey", person_id="WY-RICHEY-BOB", people=people, term_end="January 2027",
                        sources=[cg(2022)]),
                _holder(name="Robert (Robin) Hibbard", person_id="WY-HIBBARD-ROBERT", people=people,
                        term_end="January 2029", sources=[cg(2024)]),
            ]},
            {"office": "CCMSD Trustee, Moorcroft", "layout": "office-and-name", "holders": [
                _holder(name="Sharon D. Coleman", person_id="WY-COLEMAN-SHARON-D", people=people,
                        term_end="January 2029", sources=[cg(2024)]),
            ]},
            {"office": "CCMSD Trustee, Sundance", "layout": "office-and-name", "holders": [
                _holder(name="D. Marlene Edwards", person_id="WY-EDWARDS-MARLENE", people=people,
                        term_end="January 2029", sources=[cg(2024)]),
            ]},
            {"office": "Museum District Trustee", "layout": "heading-then-names", "holders": [
                _holder(name="Andrea Wood", person_id="WY-WOOD-ANDREA", people=people, term_end="January 2027",
                        sources=[cg(2022)], notes="Official 2022 contest was Vote For 3 with two named candidates.",
                        succeeding=suc("Taylor Garman", "WY-GARMAN-TAYLOR")),
                _holder(name="Amy Goodson", person_id="WY-GOODSON-AMY", people=people, term_end="January 2027",
                        sources=[cg(2022)], succeeding=suc("Maylee Baron-Kanode", "WY-BARON-KANODE-MAYLEE")),
                _holder(name="Galen Moline", person_id="WY-MOLINE-GALEN", people=people, term_end="January 2029",
                        sources=[cg(2024)], notes="Official 2024 contest was Vote For 3 with only one named candidate.",
                        succeeding=suc("Kimberly A. Hofer-Cox", "WY-HOFER-COX-KIMBERLY")),
                {"name": "Not yet collected", "person_id": "", "party": "",
                 "notes": "Official 2026 Museum trustee 2-year contest was write-in only (243 write-in votes); the winner is not named on the official summary.",
                 "flags": ["write_in_winner_not_named"]},
            ]},
            {"office": "CCSCSD Trustee", "layout": "heading-then-names", "holders": [
                _holder(name="Terry Wilkerson", person_id="WY-WILKERSON-TERRY", people=people, term_end="January 2027",
                        sources=[cg(2022)], succeeding=suc("Mary Jayne Jordan", "WY-JORDAN-MARY-JAYNE")),
                _holder(name="Lilly Ann Bankenbush", person_id="WY-BANKENBUSH-LILLY", people=people, term_end="January 2027",
                        sources=[cg(2022)], succeeding=suc("Kay McKim", "WY-MCKIM-KAY")),
                _holder(name="Barbara Bowman-Edwards", person_id="WY-BOWMAN-EDWARDS-BARBARA", people=people,
                        term_end="January 2029", sources=[cg(2024)],
                        notes="Official 2024 contest was Vote For 3 with two named candidates."),
                _holder(name="Peggy K. Howard", person_id="WY-HOWARD-PEGGY-K", people=people, term_end="January 2029",
                        sources=[cg(2024)]),
            ]},
            {"office": "CCNRD Rural", "layout": "heading-then-names", "holders": [
                _holder(name="Wanda Burget", person_id="WY-BURGET-WANDA", people=people, term_end="January 2027",
                        sources=[cg(2022)], succeeding=suc("Clint Rising", "WY-RISING-CLINT")),
                _holder(name="Kim Fundaun", person_id="WY-FUNDAUN-KIM", people=people, term_end="January 2027",
                        sources=[cg(2022)],
                        notes="Official 2022 spelling. The 2020 2-year rural surname on the page image was uncertain.",
                        succeeding=suc("Jeanne A. Whalen", "WY-WHALEN-JEANNE")),
                _holder(name="Wayne W. Garman", person_id="WY-GARMAN-WAYNE-W", people=people, term_end="January 2029",
                        sources=[cg(2020), cg(2024)]),
            ]},
            {"office": "CCNRD Urban", "layout": "office-and-name", "holders": [
                _holder(name="Casey Devish", person_id="WY-DEVISH-CASEY", people=people, term_end="January 2029",
                        sources=[cg(2024)],
                        notes="Official 2020 and 2022 urban contests were write-in only and no winner is named."),
            ]},
            {"office": "CCNRD At-large", "layout": "office-and-name", "holders": [
                _holder(name="Lily Altaffer", person_id="WY-ALTAFFER-LILY", people=people, term_end="January 2029",
                        sources=[cg(2020), cg(2024)],
                        notes="Not the same person as Julie Altaffer / Julie Crawford."),
            ]},
        ],
    }

    judicial = {
        "id": "judicial",
        "title": "Judicial retention (district and circuit)",
        "sort_key": "J3",
        "note": (
            "These judges appeared on the Crook County 2026 general ballot. Retention figures are the official Crook totals. "
            "Supreme Court justices and the Chancery Court judge are in the shared statewide judicial file. "
            "The same 6th Judicial District judges also serve Campbell and Weston."
        ),
        "offices": [
            {"office": "District Judge, 6th Judicial District", "layout": "office-and-name", "sort_key": "J03",
             "holders": [{
                 "name": "Michael J. McGrady", "person_id": "WY-MCGRADY-MICHAEL",
                 "href": "officials/judges/michael-j-mcgrady.html", "ballot_name": "MICHAEL J. MCGRADY",
                 "sources": [
                     {"label": "Wyoming Judicial Branch, District Court, 6th Judicial District",
                      "url": "https://www.wyocourts.gov/court/district-court-6th-judicial-district-weston-county/"},
                     cg(2026),
                 ],
                 "notes": "Appointed July 2024 (Wyoming Judicial Branch). The same judge is listed for Campbell, Crook, and Weston in the 6th Judicial District.",
                 "retention": {"year": 2026, "yes": 2001, "no": 575, "yes_pct": "77.68%", "no_pct": "22.32%",
                               "result": "retained", "source": CG[2026][0]},
             }]},
            {"office": "Circuit Judge, 6th Judicial District", "layout": "office-and-name", "sort_key": "J04",
             "holders": [{
                 "name": "Greg R. Steward", "person_id": "WY-STEWARD-GREG",
                 "href": "candidates/local-history/c/greg-r-steward.html", "ballot_name": "GREG R. STEWARD",
                 "sources": [cg(2026)],
                 "notes": "The person_id is WY-STEWARD-GREG (already used in the Weston 114 file). Other Steward IDs in the name index are different people.",
                 "retention": {"year": 2026, "yes": 2010, "no": 542, "yes_pct": "78.76%", "no_pct": "21.24%",
                               "result": "retained", "source": CG[2026][0]},
             }]},
        ],
    }

    keep_ids = {"state-senate", "state-house", "county", "precincts"}
    kept = [g for g in data["groups"] if g.get("id") in keep_ids]
    sk = {"state-senate": "C", "state-house": "D", "county": "E", "precincts": "P"}
    for g in kept:
        g["sort_key"] = sk.get(g["id"], g.get("sort_key"))
    data["groups"] = kept + [municipal, schools, special, judicial]
    data["sources"] = {
        "general_results": CG[2026][0],
        "primary_results": CP_2026[0],
        "clerk_archive": "https://www.crookcounty.wy.gov/elected_officials/clerk/election/election_results.php",
        "checked": RETRIEVED,
        "local_archive": "/workspace/wyoleg/local-results/crook/SOURCES.md",
    }
    apply_to_groups(data["groups"], 'crook')
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("updated", path)
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--county", required=True, help="County slug (crook ... big-horn, or hot-springs).")
    args = ap.parse_args()
    if args.county == "crook":
        people, terms, coverage = build_crook()
        update_crook_json(people)
    elif args.county == "campbell":
        import history_data_campbell as C
        people, terms, coverage = C.build_campbell()
        C.update_campbell_json(people)
    elif args.county == "sheridan":
        import history_data_sheridan as S
        people, terms, coverage = S.build_sheridan()
        S.update_sheridan_json(people)
    elif args.county == "park":
        import history_data_park as P
        people, terms, coverage = P.build_park()
        P.update_park_json(people)
    elif args.county == "laramie":
        import history_data_laramie as L
        people, terms, coverage = L.build_laramie()
        L.update_laramie_json(people)
    elif args.county == "natrona":
        import history_data_natrona as N
        people, terms, coverage = N.build_natrona()
        N.update_natrona_json(people)
    elif args.county == "albany":
        import history_data_albany as A
        people, terms, coverage = A.build_albany()
        A.update_albany_json(people)
    elif args.county == "sweetwater":
        import history_data_sweetwater as SW
        people, terms, coverage = SW.build_sweetwater()
        SW.update_sweetwater_json(people)
    elif args.county == "teton":
        import history_data_teton as T
        people, terms, coverage = T.build_teton()
        T.update_teton_json(people)
    elif args.county == "lincoln":
        import history_data_lincoln as LN
        people, terms, coverage = LN.build_lincoln()
        LN.update_lincoln_json(people)
    elif args.county == "uinta":
        import history_data_uinta as U
        people, terms, coverage = U.build_uinta()
        U.update_uinta_json(people)
    elif args.county == "carbon":
        import history_data_carbon as C
        people, terms, coverage = C.build_carbon()
        C.update_carbon_json(people, terms)
    elif args.county == "converse":
        import history_data_converse as CV
        people, terms, coverage = CV.build_converse()
        CV.update_converse_json(people, terms)
    elif args.county == "goshen":
        import history_data_goshen as G
        people, terms, coverage = G.build_goshen()
        G.update_goshen_json(people, terms)
    elif args.county == "platte":
        import history_data_platte as G
        people, terms, coverage = G.build_platte()
        G.update_platte_json(people, terms)
    elif args.county == "sublette":
        import history_data_sublette as G
        people, terms, coverage = G.build_sublette()
        G.update_sublette_json(people, terms)
    elif args.county == "washakie":
        import history_data_washakie as G
        people, terms, coverage = G.build_washakie()
        G.update_washakie_json(people, terms)
    elif args.county == "niobrara":
        import history_data_niobrara as G
        people, terms, coverage = G.build_niobrara()
        G.update_niobrara_json(people, terms)
    elif args.county == "johnson":
        import history_data_johnson as G
        people, terms, coverage = G.build_johnson()
        G.update_johnson_json(people, terms)
    elif args.county == "fremont":
        import history_data_fremont as G
        people, terms, coverage = G.build_fremont()
        G.update_fremont_json(people, terms)
    elif args.county == "big-horn":
        import history_data_big_horn as G
        people, terms, coverage = G.build_big_horn()
        G.update_big_horn_json(people, terms)
    elif args.county == "hot-springs":
        import history_data_hot_springs as G
        people, terms, coverage = G.build_hot_springs()
        G.update_hot_springs_json(people, terms)
    else:
        raise SystemExit(
            f"This preview run implements Crook through Big Horn and Hot Springs only. {args.county!r} is not yet implemented."
        )
    print("people in memory", len(people), "terms", len(terms))


if __name__ == "__main__":
    main()
