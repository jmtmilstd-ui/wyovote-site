"""Sheridan County dated terms and live-roster update. Imported by build_county_history.py."""
from __future__ import annotations

import json
from copy import deepcopy

import history_lib as H

from legislative_office_notes import apply_to_groups
RETRIEVED = "2026-11-24"
FM = H.FM
ROOT = H.ROOT

SG = {
    2012: ("https://www.sheridancountywy.gov/Document Center/Departments/Elected Office/Election Results/2012 Election/2012 General Election Results.pdf",
           "Sheridan County official 2012 general results"),
    2014: ("https://www.sheridancountywy.gov/Document Center/Departments/Elected Office/Election Results/2014 Election/2014 General Election Results.pdf",
           "Sheridan County official 2014 general results"),
    2016: ("https://www.sheridancountywy.gov/Document Center/Departments/Elected Office/Election Results/2016 Election/2016 General Election Results.pdf",
           "Sheridan County official 2016 general results"),
    2018: ("https://www.sheridancountywy.gov/Document Center/Departments/Elected Office/Election Results/2018 Election/2018 General Election Results.pdf",
           "Sheridan County official 2018 general results"),
    2020: ("https://www.sheridancountywy.gov/Document Center/Departments/Elected Office/Election Results/2020 General/SUMMARY.pdf",
           "Sheridan County official 2020 general results"),
    2022: ("https://www.sheridancountywy.gov/Document Center/Departments/Elected Office/Election Results/2022 General/Sheridan County Election Summary Report.pdf",
           "Sheridan County official 2022 general results"),
    2024: ("https://www.sheridancountywy.gov/Document Center/Departments/Elected Office/Election Results/2024 General_election/Summary of Elections Report.pdf",
           "Sheridan County official 2024 general results"),
    2026: ("https://www.sheridancountywy.gov/Document Center/Departments/Elected Office/2026 Election Documents/General/Reports/Election Summary Report-Official.pdf",
           "Sheridan County official 2026 general results"),
}
ROSTER = {
    "label": "Sheridan County official elected-officials roster, June 12, 2026 (terms expiring 2026 and 2028)",
    "url": "https://www.sheridancountywy.gov/Document Center/Departments/Elected Office/Elected Officials/Elected Officials Expiring Officials 2026-2028.pdf",
}

def sg(year: int) -> dict:
    url, label = SG[year]
    return {"label": label, "url": url}

def T(**kw):
    kw.setdefault("sources", [sg(kw["election_year"])] if kw.get("election_year") else [])
    kw.setdefault("confidence", "high")
    return H.term(**kw)

def register_people(P):
    reused = [
        ("WY-BITEMAN-BO", "Bo Biteman", "Bo", "Biteman"),
        ("WY-BUTCHER-MELISSA", "Melissa Butcher", "Melissa", "Butcher"),
        ("WY-CRAGO-BARRY", "Barry Crago", "Barry", "Crago"),
        ("WY-PENDERGRAFT-KEN", "Ken Pendergraft", "Ken", "Pendergraft"),
        ("WY-STURTEVANT-MYCA", "Myca Sturtevant", "Myca", "Sturtevant"),
        ("WY-KOLTISKA-JOHN", "Ryan Koltiska", "Ryan", "Koltiska"),
        ("WY-CONNOLLY-MARILYN", "Marilyn F Connolly", "Marilyn", "Connolly"),
        ("WY-BRATTEN-LAURIE", "Laurie Bratten", "Laurie", "Bratten"),
        ("WY-HASWELL-CHRISTI", "Christi Burgess Haswell", "Christi", "Haswell"),
        ("WY-SIDDLE-NICK", "Nick Siddle", "Nick", "Siddle"),
        ("WY-SCHELLINGER-JIM", "Jim Schellinger", "Jim", "Schellinger"),
        ("WY-WRIGHT-LONNIE", "Lonnie J. Wright", "Lonnie", "Wright"),
        ("WY-ARZY-MICHAEL", "Michael R. Arzy", "Michael", "Arzy"),
        ("WY-JENNINGS-HOLLY", "Holly Jennings", "Holly", "Jennings"),
        ("WY-THOMPSON-ALLEN", "Allen J. Thompson", "Allen", "Thompson"),
        ("WY-THOMPSON-EDA", "Eda Schunk Thompson", "Eda", "Thompson"),
        ("WY-FALL-PAUL", "Paul Fall", "Paul", "Fall"),
        ("WY-KNUDTSON-KOKO", "Koko Knudtson", "Koko", "Knudtson"),
        ("WY-ARAAS-KATIE", "Katie Araas", "Katie", "Araas"),
        ("WY-DOMINGUEZ-LEVI", "Levi Dominguez", "Levi", "Dominguez"),
        ("WY-BENNETT-DIANNA", "Dianna D. Bennett", "Dianna", "Bennett"),
        ("WY-BOTTEN-RENE", "Rene Botten", "Rene", "Botten"),
        ("WY-BYRD-ROBERT", "Robert Byrd", "Robert", "Byrd"),
        ("WY-KINSKEY-DAVE", "Dave Kinskey", "Dave", "Kinskey"),
        ("WY-BURNS-BRUCE", "Bruce Burns", "Bruce", "Burns"),
        ("WY-WESTERN-CYRUS", "Cyrus Western", "Cyrus", "Western"),
        ("WY-KINNER-MARK", "Mark Kinner", "Mark", "Kinner"),
        ("WY-MAIER-STEVE", "Steve Maier", "Steve", "Maier"),
        ("WY-BRIDGER-RICHARD", "Richard Bridger", "Richard", "Bridger"),
        ("WY-LUHMAN-GREG", "Greg Luhman", "Greg", "Luhman"),
        ("WY-PATCEG-ANDREW", "Andrew Patceg", "Andrew", "Patceg"),
        ("WY-WEITZEL-TERRY", "Terry Weitzel", "Terry", "Weitzel"),
        ("WY-WOOD-JACK", "Jack Wood", "Jack", "Wood"),
        ("WY-LEICHTNAM-BEV", "Bev Leichtnam", "Bev", "Leichtnam"),
        ("WY-REED-CLIFFORD", "Clifford Reed", "Clifford", "Reed"),
        ("WY-CLARK-PETER", "Peter B. Clark", "Peter", "Clark"),
        ("WY-WEAVER-JESSICA", "Jessica Weaver", "Jessica", "Weaver"),
        ("WY-ADSIT-WILLIAM", "William (Bill) Adsit", "William", "Adsit"),
    ]
    for pid, display, first, last in reused:
        aliases = ""
        if pid == "WY-HASWELL-CHRISTI":
            aliases = "Christi Haswell; Christi Burgess Haswell"
        if pid == "WY-BRIDGER-RICHARD":
            aliases = "Rich Bridger; Richard Bridger"
        if pid == "WY-CONNOLLY-MARILYN":
            aliases = "Marilyn Connolly; Marilyn F. Connolly; Marilyn Conoly"
        if pid == "WY-KINNER-MARK":
            aliases = "Mark S. Kinner"
        if pid == "WY-BENNETT-DIANNA":
            aliases = "Dianna Bennett; Diana Bennett"
        if pid == "WY-THOMPSON-EDA":
            aliases = "Eda Schunk Thompson"
        if pid == "WY-WRIGHT-LONNIE":
            aliases = "Lonnie Wright; Lonnie J Wright"
        if pid == "WY-ARZY-MICHAEL":
            aliases = "Mike Arzy; Michael Arzy"
        P(pid, display, first, last, aliases=aliases, minted=False)

    minted = [
        ("WY-NICKEL-MIKE", "Mike Nickel", "Mike", "Nickel", ""),
        ("WY-RINGLEY-TOM", "Tom Ringley", "Tom", "Ringley", ""),
        ("WY-CRAM-TERRY", "Terry Cram", "Terry", "Cram", ""),
        ("WY-ROLSTON-BOB", "Bob Rolston", "Bob", "Rolston", ""),
        ("WY-JENNINGS-MARK-H30", "Mark Jennings", "Mark", "Jennings", ""),
        ("WY-SCHOCK-CHRIS", "Chris Schock", "Chris", "Schock", ""),
        ("WY-SCHIFFER-JOHN-C", "John C. Schiffer", "John", "Schiffer", "C."),
        ("WY-PATTON-JOHN-W", "John W. Patton", "John", "Patton", "W."),
        ("WY-COLEMAN-KATHY", "Kathy Coleman", "Kathy", "Coleman", ""),
        ("WY-MADDEN-MICHAEL", "Michael Madden", "Michael", "Madden", ""),
        ("WY-BERGER-ROSIE", "Rosie Berger", "Rosie", "Berger", ""),
        ("WY-REDLE-MATTHEW-F", "Matthew F. Redle", "Matthew", "Redle", "F."),
        ("WY-HOFMEIER-DAVE-W", "Dave W. Hofmeier", "Dave", "Hofmeier", "W."),
        ("WY-CARROLL-PETER-C", "Peter C. Carroll", "Peter", "Carroll", "C."),
        ("WY-GRANDAHL-CAROL-L", "Carol L. Grandahl", "Carol", "Grandahl", "L."),
        ("WY-ARNEY-NICKIE", "Nickie Arney", "Nickie", "Arney", ""),
        ("WY-KANE-PJ", "P.J. Kane", "P.J.", "Kane", ""),
        ("WY-HORSLEY-AMBER-C", "Amber C. Horsley", "Amber", "Horsley", "C."),
        ("WY-BRANTZ-STEVEN", "Steven Brantz", "Steven", "Brantz", ""),
        ("WY-VISSER-HANLE", "Hanlé Visser", "Hanlé", "Visser", ""),
        ("WY-REES-ARIC", "Aric Rees", "Aric", "Rees", ""),
        ("WY-LOGAN-ROBERT", "Robert (Bobby) Logan", "Robert", "Logan", ""),
        ("WY-PERKINS-SANDY", "Sandy Perkins", "Sandy", "Perkins", ""),
        ("WY-ALLEY-ROBERT", "Robert Alley", "Robert", "Alley", ""),
        ("WY-GROVER-DAN", "Dan Grover", "Dan", "Grover", ""),
        ("WY-MAZE-TIM", "Tim Maze", "Tim", "Maze", ""),
        ("WY-HOFMEIER-RICHARD", "Richard Hofmeier", "Richard", "Hofmeier", ""),
        ("WY-SUNDQUIST-RANDY", "Randy Sundquist", "Randy", "Sundquist", ""),
        ("WY-MILES-SMITH-AMBER", "Amber Miles-Smith", "Amber", "Miles-Smith", ""),
        ("WY-HELFERICH-BRYAN", "Bryan Helferich", "Bryan", "Helferich", ""),
        ("WY-KRUMM-CLINT", "Clint Krumm", "Clint", "Krumm", ""),
        ("WY-WHITEHEAD-ERIC", "Eric Whitehead", "Eric", "Whitehead", ""),
        ("WY-STALICK-MORGAN", "Morgan (Barker) Stalick", "Morgan", "Stalick", ""),
        ("WY-DAVIDSON-BRIAN-SD1", "Brian Davidson", "Brian", "Davidson", ""),
        ("WY-BITEMAN-MERCEDES", "Mercedes Biteman", "Mercedes", "Biteman", ""),
        ("WY-LANSING-MICHAEL", "Michael Lansing", "Michael", "Lansing", ""),
        ("WY-PERKINS-ANN-M", "Ann M. Perkins", "Ann", "Perkins", "M."),
        ("WY-RAMBUR-SHELTA", "Shelta Rambur", "Shelta", "Rambur", ""),
        ("WY-WADDELL-ARIN", "Arin Waddell", "Arin", "Waddell", ""),
        ("WY-CHRISTENSEN-CHASE", "Chase Christensen", "Chase", "Christensen", ""),
        ("WY-HAWKINS-PETER", "Peter Hawkins", "Peter", "Hawkins", ""),
        ("WY-WYATT-DANA", "Dana Wyatt", "Dana", "Wyatt", ""),
        ("WY-FESSLER-ED", "Ed Fessler", "Ed", "Fessler", ""),
        ("WY-MOORE-DOUG-SD2", "Doug Moore", "Doug", "Moore", ""),
        ("WY-TOMLINSON-JEFF", "Jeff Tomlinson", "Jeff", "Tomlinson", ""),
        ("WY-RADER-SHANE", "Shane Rader", "Shane", "Rader", ""),
        ("WY-OLSEN-SAM", "Sam Olsen", "Sam", "Olsen", ""),
        ("WY-HACKETT-GEORGINA", "Georgina Hackett", "Georgina", "Hackett", ""),
        ("WY-MILLER-ERNIE", "Ernie Miller", "Ernie", "Miller", ""),
        ("WY-BASSETT-ASHLEA", "Ashlea A. Bassett", "Ashlea", "Bassett", "A."),
        ("WY-MALLI-KRISTINE", "Kristine Elaine Malli", "Kristine", "Malli", ""),
        ("WY-LITTLE-KELLY-SD3", "Kelly Little", "Kelly", "Little", ""),
        ("WY-GUYER-DEBORAH", "Deborah Guyer", "Deborah", "Guyer", ""),
        ("WY-HACKETT-DUSTY", "Dusty Hackett", "Dusty", "Hackett", ""),
        ("WY-COTTON-WARD", "Ward A. Cotton", "Ward", "Cotton", "A."),
        ("WY-HENRY-ELAINE-OLAFSON", "Elaine Olafson Henry", "Elaine", "Henry", ""),
        ("WY-HOLLOWAY-CHUCK", "Chuck Holloway", "Chuck", "Holloway", ""),
        ("WY-JULIAN-DON", "Don Julian", "Don", "Julian", ""),
        ("WY-SWANSON-TRACY", "Tracy Swanson", "Tracy", "Swanson", ""),
        ("WY-LEIBRICH-BOB", "Bob Leibrich", "Bob", "Leibrich", ""),
        ("WY-REYNOLDS-GARY", "Gary Reynolds", "Gary", "Reynolds", ""),
        ("WY-WESTERN-JESSICA-M", "Jessica M. Western", "Jessica", "Western", "M."),
        ("WY-HEYWARD-EDITH", "Edith Heyward", "Edith", "Heyward", ""),
        ("WY-CONNELL-ORRIN", "Orrin Connell", "Orrin", "Connell", ""),
        ("WY-MASTERS-STEPHANIE", "Stephanie Masters", "Stephanie", "Masters", ""),
        ("WY-ADDLESPERGER-ANNIE", "Annie Addlesperger", "Annie", "Addlesperger", ""),
        ("WY-SHERWOOD-KATI", "Kati Sherwood", "Kati", "Sherwood", ""),
        ("WY-LANDON-JACK-JR", "Jack Landon, Jr.", "Jack", "Landon", ""),
        ("WY-CUSTIS-LYNN", "Lynn Custis", "Lynn", "Custis", ""),
        ("WY-PHILLIPS-DARCI", "Darci A.V. Phillips", "Darci", "Phillips", ""),
        ("WY-KIRVEN-BENJAMIN", "Benjamin Kirven", "Benjamin", "Kirven", ""),
        ("WY-CUNDIFF-SHELLEY-A", "Shelley A. Cundiff", "Shelley", "Cundiff", "A."),
        ("WY-BUNTING-SHERYL-SMITH", "Sheryl Smith Bunting", "Sheryl", "Bunting", ""),
        ("WY-EDELMAN", "Edelman", "", "Edelman", ""),
    ]
    for pid, display, first, last, middle in minted:
        aliases = ""
        if pid == "WY-COTTON-WARD":
            aliases = "Ward Cotton; Ward A Cotton"
        if pid == "WY-HACKETT-GEORGINA":
            aliases = "Gina Hackett; Georgina Hackett"
        if pid == "WY-MALLI-KRISTINE":
            aliases = "Kris Malli; Kristine Malli"
        if pid == "WY-BASSETT-ASHLEA":
            aliases = "Ashlee Bassett; Ashlea Bassett"
        if pid == "WY-OLSEN-SAM":
            aliases = "Samuel R. Olsen; Sam Olsen"
        if pid == "WY-KANE-PJ":
            aliases = "P. J. Kane; P.J. Kane; PJ Kane"
        if pid == "WY-WESTERN-JESSICA-M":
            aliases = "Jessica Western; Jessica M Western"
        if pid == "WY-LOGAN-ROBERT":
            aliases = "Bobby Logan; Robert Logan"
        P(pid, display, first, last, middle=middle, aliases=aliases, minted=True)


def county_and_legislature_terms():
    terms = []
    # ----- Senate -----
    # S21 midterm: 2014 Burns, 2018/2022 Biteman, 2026 Butcher
    terms += [
        T(person_id="WY-BURNS-BRUCE", name="Bruce Burns", office_group="state-senate",
          office="Senate District 21 (S21)", jurisdiction="Senate District 21",
          term_start=FM[2015], term_end=FM[2019], election_year=2014,
          notes="Official 2014 general, 5,452."),
        T(person_id="WY-BITEMAN-BO", name="Bo Biteman", office_group="state-senate",
          office="Senate District 21 (S21)", jurisdiction="Senate District 21",
          term_start=FM[2019], term_end=FM[2023], election_year=2018,
          notes="Official 2018 general, 5,125."),
        T(person_id="WY-BITEMAN-BO", name="Bo Biteman", office_group="state-senate",
          office="Senate District 21 (S21)", jurisdiction="Senate District 21",
          term_start=FM[2023], term_end=FM[2027], election_year=2022,
          notes="Official 2022 general, 5,815."),
        T(person_id="WY-BUTCHER-MELISSA", name="Melissa Butcher", office_group="state-senate",
          office="Senate District 21 (S21)", jurisdiction="Senate District 21",
          term_start=FM[2027], term_end=FM[2031], election_year=2026,
          notes="Succeeding; official 2026 general, 6,656."),
    ]
    # S22 presidential: 2012 Schiffer, 2016/2020 Kinskey, 2024 Crago
    terms += [
        T(person_id="WY-SCHIFFER-JOHN-C", name="John C. Schiffer", office_group="state-senate",
          office="Senate District 22 (S22)", jurisdiction="Senate District 22",
          term_start=FM[2013], term_end=FM[2017], election_year=2012,
          notes="Official 2012 general, 3,975."),
        T(person_id="WY-KINSKEY-DAVE", name="Dave Kinskey", office_group="state-senate",
          office="Senate District 22 (S22)", jurisdiction="Senate District 22",
          term_start=FM[2017], term_end=FM[2021], election_year=2016,
          notes="Official 2016 general, 3,746."),
        T(person_id="WY-KINSKEY-DAVE", name="Dave Kinskey", office_group="state-senate",
          office="Senate District 22 (S22)", jurisdiction="Senate District 22",
          term_start=FM[2021], term_end=FM[2025], election_year=2020,
          notes="Official 2020 general, 4,290."),
        T(person_id="WY-CRAGO-BARRY", name="Barry Crago", office_group="state-senate",
          office="Senate District 22 (S22)", jurisdiction="Senate District 22",
          term_start=FM[2025], term_end=FM[2029], election_year=2024,
          notes="Official 2024 general, 4,464."),
    ]
    # House
    def house(dist, pid, name, start, end, year, notes=""):
        terms.append(T(person_id=pid, name=name, office_group="state-house",
                       office=f"House District {dist}", jurisdiction=f"House District {dist}",
                       term_start=FM[start], term_end=FM[end], election_year=year, notes=notes))

    # H29: Patton 2012/2014; Kinner 2016/2018/2020; Pendergraft 2022/2024; Sturtevant 2026
    house("29 (H29)", "WY-PATTON-JOHN-W", "John W. Patton", 2013, 2015, 2012, "Official 2012 general, 3,414.")
    house("29 (H29)", "WY-PATTON-JOHN-W", "John W. Patton", 2015, 2017, 2014, "Official 2014 general, 2,012.")
    house("29 (H29)", "WY-KINNER-MARK", "Mark Kinner", 2017, 2019, 2016, "Official 2016 general, 3,073. Ballot Mark S. Kinner.")
    house("29 (H29)", "WY-KINNER-MARK", "Mark Kinner", 2019, 2021, 2018, "Official 2018 general, 2,550.")
    house("29 (H29)", "WY-KINNER-MARK", "Mark Kinner", 2021, 2023, 2020, "Official 2020 general, 3,766.")
    house("29 (H29)", "WY-PENDERGRAFT-KEN", "Ken Pendergraft", 2023, 2025, 2022, "Official 2022 general, 2,102.")
    house("29 (H29)", "WY-PENDERGRAFT-KEN", "Ken Pendergraft", 2025, 2027, 2024, "Official 2024 general, 3,009.")
    house("29 (H29)", "WY-STURTEVANT-MYCA", "Myca Sturtevant", 2027, 2029, 2026, "Succeeding; official 2026 general, 2,537.")
    # H30: Coleman 2012; Jennings 2014-2022; Kelly 2024; Koltiska 2026
    house("30 (H30)", "WY-COLEMAN-KATHY", "Kathy Coleman", 2013, 2015, 2012, "Official 2012 general, 3,625.")
    house("30 (H30)", "WY-JENNINGS-MARK-H30", "Mark Jennings", 2015, 2017, 2014, "Official 2014 general, 2,068. Distinct from other Jennings IDs.")
    house("30 (H30)", "WY-JENNINGS-MARK-H30", "Mark Jennings", 2017, 2019, 2016, "Official 2016 general, 2,953.")
    house("30 (H30)", "WY-JENNINGS-MARK-H30", "Mark Jennings", 2019, 2021, 2018, "Official 2018 general, 2,870.")
    house("30 (H30)", "WY-JENNINGS-MARK-H30", "Mark Jennings", 2021, 2023, 2020, "Official 2020 general, 3,985.")
    house("30 (H30)", "WY-JENNINGS-MARK-H30", "Mark Jennings", 2023, 2025, 2022, "Official 2022 general, 2,912.")
    house("30 (H30)", "WY-BRIDGER-RICHARD", "Richard Bridger", 2025, 2027, 2024, "PLACEHOLDER")  # WAIT Tom Kelly won 2024 not Bridger!
    # Fix below - I'll remove placeholder by rewriting last two
    terms[:] = [t for t in terms if not (t["office"]=="House District 30 (H30)" and t.get("election_year")==2024)]
    house("30 (H30)", "WY-KOLTISKA-JOHN", "Ryan Koltiska", 2025, 2027, 2024, "WRONG YEAR")  # no
    terms[:] = [t for t in terms if not (t["office"]=="House District 30 (H30)" and t.get("notes") in ("PLACEHOLDER","WRONG YEAR"))]
    # correct 2024/2026 H30
    # Need Tom Kelly ID - mint if missing. I'll add person in register later if needed.
    # For now use a term with WY-KELLY-TOM - I need to register this person.
    house("30 (H30)", "WY-KELLY-TOM", "Tom Kelly", 2025, 2027, 2024, "Official 2024 general, 3,944.")
    house("30 (H30)", "WY-KOLTISKA-JOHN", "Ryan Koltiska", 2027, 2029, 2026, "Succeeding; official 2026 general, 2,963.")
    # H40: Madden 2012-2016; Schock 2018; Crago 2020/2022; Connolly 2024/2026
    house("40 (H40)", "WY-MADDEN-MICHAEL", "Michael Madden", 2013, 2015, 2012, "Official 2012 general, 197 (Sheridan portion).")
    house("40 (H40)", "WY-MADDEN-MICHAEL", "Michael Madden", 2015, 2017, 2014, "Official 2014 general, 142. Ballot Mike Madden.")
    house("40 (H40)", "WY-MADDEN-MICHAEL", "Michael Madden", 2017, 2019, 2016, "Official 2016 general, 169.")
    house("40 (H40)", "WY-SCHOCK-CHRIS", "Chris Schock", 2019, 2021, 2018, "Official 2018 general, 108 (IND).")
    house("40 (H40)", "WY-CRAGO-BARRY", "Barry Crago", 2021, 2023, 2020, "Official 2020 general, 212.")
    house("40 (H40)", "WY-CRAGO-BARRY", "Barry Crago", 2023, 2025, 2022, "Official 2022 general, 591.")
    house("40 (H40)", "WY-CONNOLLY-MARILYN", "Marilyn F Connolly", 2025, 2027, 2024, "Official 2024 general, 706.")
    house("40 (H40)", "WY-CONNOLLY-MARILYN", "Marilyn F Connolly", 2027, 2029, 2026, "Re-elected; official 2026 general, 555.")
    # H51: Berger 2012/2014; Biteman 2016; Western 2018/2020/2022; Bratten 2024/2026
    house("51 (H51)", "WY-BERGER-ROSIE", "Rosie Berger", 2013, 2015, 2012, "Official 2012 general, 4,768.")
    house("51 (H51)", "WY-BERGER-ROSIE", "Rosie Berger", 2015, 2017, 2014, "Official 2014 general, 3,233.")
    house("51 (H51)", "WY-BITEMAN-BO", "Bo Biteman", 2017, 2019, 2016, "Official 2016 general, 3,931.")
    house("51 (H51)", "WY-WESTERN-CYRUS", "Cyrus Western", 2019, 2021, 2018, "Official 2018 general, 4,140.")
    house("51 (H51)", "WY-WESTERN-CYRUS", "Cyrus Western", 2021, 2023, 2020, "Official 2020 general, 5,619.")
    house("51 (H51)", "WY-WESTERN-CYRUS", "Cyrus Western", 2023, 2025, 2022, "Official 2022 general, 3,631.")
    house("51 (H51)", "WY-BRATTEN-LAURIE", "Laurie Bratten", 2025, 2027, 2024, "Official 2024 general, 4,910.")
    house("51 (H51)", "WY-BRATTEN-LAURIE", "Laurie Bratten", 2027, 2029, 2026, "Re-elected; official 2026 general, 3,774.")

    # ----- Commissioners -----
    def comm(pid, name, start, end, year, notes="", **kw):
        terms.append(T(person_id=pid, name=name, office_group="county",
                       office="County Commissioner", jurisdiction="Sheridan County",
                       term_start=start if isinstance(start, str) and '-' in str(start) else FM[start],
                       term_end=end if isinstance(end, str) and '-' in str(end) else FM[end],
                       election_year=year, notes=notes, **kw))
    comm("WY-NICKEL-MIKE", "Mike Nickel", 2013, 2017, 2012, "Official 2012 general, 10,168 (vote for 2).")
    comm("WY-RINGLEY-TOM", "Tom Ringley", 2013, 2017, 2012, "Official 2012 general, 9,707 (vote for 2).")
    comm("WY-CRAM-TERRY", "Terry Cram", 2015, 2019, 2014, "Official 2014 general, 6,938 (vote for 3).")
    comm("WY-ROLSTON-BOB", "Bob Rolston", 2015, 2019, 2014, "Official 2014 general, 6,675 (vote for 3).")
    comm("WY-MAIER-STEVE", "Steve Maier", 2015, 2019, 2014, "Official 2014 general, 6,622 (vote for 3).")
    comm("WY-NICKEL-MIKE", "Mike Nickel", 2017, 2021, 2016, "Official 2016 general, 9,509 (vote for 2).")
    comm("WY-RINGLEY-TOM", "Tom Ringley", 2017, 2021, 2016, "Official 2016 general, 8,850 (vote for 2).")
    comm("WY-HASWELL-CHRISTI", "Christi Burgess Haswell", 2019, 2023, 2018, "Official 2018 general, 7,441 (vote for 3).")
    comm("WY-SIDDLE-NICK", "Nick Siddle", 2019, 2023, 2018, "Official 2018 general, 7,074 (vote for 3).")
    comm("WY-CRAM-TERRY", "Terry Cram", 2019, 2023, 2018, "Official 2018 general, 6,969 (vote for 3).")
    comm("WY-RINGLEY-TOM", "Tom Ringley", 2021, 2025, 2020, "Official 2020 general, 11,242 (vote for 2).")
    comm("WY-WRIGHT-LONNIE", "Lonnie J. Wright", 2021, 2025, 2020, "Official 2020 general, 10,745 (vote for 2).")
    comm("WY-HASWELL-CHRISTI", "Christi Burgess Haswell", 2023, 2027, 2022, "Official 2022 general, 8,523 (vote for 3). Re-elected 2026.")
    comm("WY-SIDDLE-NICK", "Nick Siddle", 2023, 2027, 2022, "Official 2022 general, 8,569 (vote for 3).")
    comm("WY-THOMPSON-ALLEN", "Allen J. Thompson", 2023, 2025, 2022,
         "Official 2022 general, 8,644 (vote for 3). The official 2024 general included a 2-year commissioner seat, won by Holly Jennings, covering January 2025–January 2027. The exact date Thompson left is not independently collected; this term is ended at January 2025 when the official 2-year term begins.")
    comm("WY-JENNINGS-HOLLY", "Holly Jennings", 2025, 2027, 2024,
         "Official 2024 general, 12,437 (vote for 1, 2-year seat). Re-elected 2026 to a 4-year term.")
    comm("WY-ARZY-MICHAEL", "Michael R. Arzy", 2025, 2029, 2024, "Official 2024 general, 10,149 (vote for 2, 4-year).")
    comm("WY-WRIGHT-LONNIE", "Lonnie J. Wright", 2025, 2029, 2024, "Official 2024 general, 10,003 (vote for 2, 4-year).")
    comm("WY-SCHELLINGER-JIM", "Jim Schellinger", 2027, 2031, 2026, "Succeeding Nick Siddle; official 2026 general, 8,445 (vote for 3).")
    comm("WY-HASWELL-CHRISTI", "Christi Burgess Haswell", 2027, 2031, 2026, "Re-elected; official 2026 general, 7,733 (vote for 3).")
    comm("WY-JENNINGS-HOLLY", "Holly Jennings", 2027, 2031, 2026, "Elected to a 4-year term after the 2024 2-year seat; official 2026 general, 7,447 (vote for 3).")

    # ----- Row offices -----
    def row(office, pid, name, start, end, year, notes=""):
        terms.append(T(person_id=pid, name=name, office_group="county",
                       office=office, jurisdiction="Sheridan County",
                       term_start=FM[start], term_end=FM[end], election_year=year, notes=notes))
    row("County Clerk", "WY-THOMPSON-EDA", "Eda Schunk Thompson", 2015, 2019, 2014, "Official 2014 general, 8,047.")
    row("County Clerk", "WY-THOMPSON-EDA", "Eda Schunk Thompson", 2019, 2023, 2018, "Official 2018 general, 10,016.")
    row("County Clerk", "WY-THOMPSON-EDA", "Eda Schunk Thompson", 2023, 2027, 2022, "Official 2022 general, 10,643.")
    row("County Clerk", "WY-THOMPSON-EDA", "Eda Schunk Thompson", 2027, 2031, 2026, "Re-elected; official 2026 general, 10,195.")
    row("County Treasurer", "WY-CARROLL-PETER-C", "Peter C. Carroll", 2015, 2019, 2014, "Official 2014 general, 8,159.")
    row("County Treasurer", "WY-GRANDAHL-CAROL-L", "Carol L. Grandahl", 2019, 2023, 2018, "Official 2018 general, 9,862.")
    row("County Treasurer", "WY-ARAAS-KATIE", "Katie Araas", 2023, 2027, 2022, "Official 2022 general, 10,577.")
    row("County Treasurer", "WY-ARAAS-KATIE", "Katie Araas", 2027, 2031, 2026, "Re-elected; official 2026 general, 10,540.")
    row("County Assessor", "WY-FALL-PAUL", "Paul Fall", 2015, 2019, 2014, "Official 2014 general, 8,115.")
    row("County Assessor", "WY-FALL-PAUL", "Paul Fall", 2019, 2023, 2018, "Official 2018 general, 9,871.")
    row("County Assessor", "WY-FALL-PAUL", "Paul Fall", 2023, 2027, 2022, "Official 2022 general, 10,454. Still listed as assessor on the official June 12, 2026 roster.")
    row("County Assessor", "WY-KNUDTSON-KOKO", "Koko Knudtson", 2027, 2031, 2026, "Succeeding; official 2026 general, 9,720.")
    row("County Sheriff", "WY-HOFMEIER-DAVE-W", "Dave W. Hofmeier", 2015, 2019, 2014, "Official 2014 general, 8,170.")
    row("County Sheriff", "WY-THOMPSON-ALLEN", "Allen J. Thompson", 2019, 2023, 2018, "Official 2018 general, 10,026.")
    row("County Sheriff", "WY-DOMINGUEZ-LEVI", "Levi Dominguez", 2023, 2027, 2022, "Official 2022 general, 10,619.")
    row("County Sheriff", "WY-DOMINGUEZ-LEVI", "Levi Dominguez", 2027, 2031, 2026, "Re-elected; official 2026 general, 10,275.")
    row("County Attorney", "WY-REDLE-MATTHEW-F", "Matthew F. Redle", 2015, 2019, 2014, "Official 2014 general, 7,476.")
    row("County Attorney", "WY-BENNETT-DIANNA", "Dianna D. Bennett", 2019, 2023, 2018, "Official 2018 general, 9,156.")
    row("County Attorney", "WY-BENNETT-DIANNA", "Dianna D. Bennett", 2023, 2027, 2022, "Official 2022 general, 10,033.")
    row("County Attorney", "WY-BENNETT-DIANNA", "Dianna D. Bennett", 2027, 2031, 2026, "Re-elected; official 2026 general, 9,800.")
    row("County Coroner", "WY-KANE-PJ", "P.J. Kane", 2015, 2019, 2014, "Official 2014 general, 7,940. Ballot P. J. Kane.")
    row("County Coroner", "WY-KANE-PJ", "P.J. Kane", 2019, 2023, 2018, "Official 2018 general, 8,665.")
    row("County Coroner", "WY-BYRD-ROBERT", "Robert Byrd", 2023, 2027, 2022, "Official 2022 general, 10,324.")
    row("County Coroner", "WY-BYRD-ROBERT", "Robert Byrd", 2027, 2031, 2026, "Re-elected; official 2026 general, 9,991.")
    row("Clerk of District Court", "WY-ARNEY-NICKIE", "Nickie Arney", 2015, 2019, 2014, "Official 2014 general, 7,969.")
    row("Clerk of District Court", "WY-BOTTEN-RENE", "Rene Botten", 2019, 2023, 2018, "Official 2018 general, 9,592.")
    row("Clerk of District Court", "WY-BOTTEN-RENE", "Rene Botten", 2023, 2027, 2022, "Official 2022 general, 10,172.")
    row("Clerk of District Court", "WY-BOTTEN-RENE", "Rene Botten", 2027, 2031, 2026, "Re-elected; official 2026 general, 10,210.")

    # ----- 4th JD named retentions (no unnamed 2018 circuit) -----
    # Shown as in office from the January after a named official retention through the next ordinary cycle, without inventing appointment dates.
    def retain(pid, name, office, year, yes, no, start, end, notes=""):
        tot=yes+no
        terms.append(T(person_id=pid, name=name, office_group="judicial",
                       office=office, jurisdiction="4th Judicial District",
                       term_start=FM[start], term_end=FM[end], election_year=year,
                       how_took_office="retained",
                       notes=notes or f"Official Sheridan {year} general retention, YES {yes:,} / NO {no:,}.",
                       retention={"year": year, "yes": yes, "no": no,
                                  "yes_pct": f"{yes/tot*100:.2f}%", "no_pct": f"{no/tot*100:.2f}%",
                                  "result": "retained", "source": SG[year][0]}))
    # 2020 district: Fenn (later SC; end mid-2022 is in shared SC file — keep local row only through 2022)
    retain("WY-FENN-JOHN", "John G. Fenn", "District Judge, 4th Judicial District", 2020, 12221, 2493, 2021, 2023,
           "Official 2020 general “DIST CT - FENN,” YES 12,221 / NO 2,493. Fenn later appears on the official 2024 Supreme Court retention; this local district row is not extended past January 2023.")
    retain("WY-EDELMAN", "Edelman", "District Judge, 4th Judicial District", 2020, 8058, 6257, 2021, 2025,
           "Official 2020 general “DIST CT - EDELMAN,” YES 8,058 / NO 6,257. The official summary does not give a first name. The 2024 official general names Darci A.V. Phillips and Benjamin Kirven on the district/circuit retention lines; this row is ended January 2025.")
    retain("WY-CUNDIFF-SHELLEY-A", "Shelley A. Cundiff", "Judge (2022 official Sheridan retention)", 2022, 8790, 1980, 2023, 2025,
           "Official 2022 general “RETAIN JUDGE SHELLEY A. CUNDIFF,” YES 8,790 / NO 1,980. The official title does not say district or circuit. The official June 2026 roster does not list Cundiff; this row is not extended as a current 2026 holder.")
    retain("WY-PHILLIPS-DARCI", "Darci A.V. Phillips", "District Judge, 4th Judicial District", 2024, 11859, 2305, 2025, 2031,
           "Official 2024 general “RETAIN JUDGE A DARCI A.V. PHILLIPS,” YES 11,859 / NO 2,305.")
    retain("WY-KIRVEN-BENJAMIN", "Benjamin Kirven", "District Judge, 4th Judicial District", 2024, 11490, 2300, 2025, 2031,
           "Official 2024 general “RETAIN JUDGE B BENJAMIN KIRVEN,” YES 11,490 / NO 2,300. The official title says Judge B and does not independently confirm district vs. circuit; listed here with the 2024 paired retention.")
    return terms


def local_terms():
    terms = []
    def add(office, group, juris, pid, name, start, end, year, notes=""):
        terms.append(T(person_id=pid, name=name, office_group=group, office=office,
                       jurisdiction=juris, term_start=FM[start], term_end=FM[end],
                       election_year=year, notes=notes))

    # City of Sheridan
    add("Sheridan Mayor", "municipal", "City of Sheridan",
        "WY-BRIDGER-RICHARD", "Richard Bridger", 2021, 2025, 2020,
        "Official 2020 general, 4,754. Ballot Rich Bridger.")
    add("Sheridan Mayor", "municipal", "City of Sheridan",
        "WY-BRIDGER-RICHARD", "Richard Bridger", 2025, 2029, 2024,
        "Official 2024 general, 5,495. Ballot Richard Bridger.")
    add("Sheridan City Council", "municipal", "City of Sheridan",
        "WY-BRANTZ-STEVEN", "Steven Brantz", 2021, 2025, 2020, "Official 2020 general, 3,293 (vote for 3).")
    add("Sheridan City Council", "municipal", "City of Sheridan",
        "WY-DAY-SHAWN", "Shawn Day", 2021, 2025, 2020, "Official 2020 general, 2,965 (vote for 3).")
    add("Sheridan City Council", "municipal", "City of Sheridan",
        "WY-JENNINGS-KRISTEN-CITY", "Kristen Jennings", 2021, 2025, 2020, "Official 2020 general, 4,163 (vote for 3). Distinct from Commissioner Holly Jennings.")
    add("Sheridan City Council", "municipal", "City of Sheridan",
        "WY-LUHMAN-GREG", "Greg Luhman", 2023, 2027, 2022, "Official 2022 general, 2,611 (vote for 3).")
    add("Sheridan City Council", "municipal", "City of Sheridan",
        "WY-WEITZEL-TERRY", "Terry Weitzel", 2023, 2027, 2022, "Official 2022 general, 2,533 (vote for 3).")
    add("Sheridan City Council", "municipal", "City of Sheridan",
        "WY-PATCEG-ANDREW", "Andrew Patceg", 2023, 2027, 2022, "Official 2022 general, 2,294 (vote for 3).")
    add("Sheridan City Council", "municipal", "City of Sheridan",
        "WY-WOOD-JACK", "Jack Wood", 2025, 2029, 2024, "Official 2024 general, 4,609 (vote for 3).")
    add("Sheridan City Council", "municipal", "City of Sheridan",
        "WY-BRANTZ-STEVEN", "Steven Brantz", 2025, 2029, 2024, "Official 2024 general, 4,504 (vote for 3).")
    add("Sheridan City Council", "municipal", "City of Sheridan",
        "WY-LEICHTNAM-BEV", "Bev Leichtnam", 2025, 2029, 2024, "Official 2024 general, 4,414 (vote for 3).")
    add("Sheridan City Council", "municipal", "City of Sheridan",
        "WY-LUHMAN-GREG", "Greg Luhman", 2027, 2031, 2026, "Re-elected; official 2026 general, 3,201 (vote for 3).")
    add("Sheridan City Council", "municipal", "City of Sheridan",
        "WY-WEITZEL-TERRY", "Terry Weitzel", 2027, 2031, 2026, "Re-elected; official 2026 general, 3,133 (vote for 3).")
    add("Sheridan City Council", "municipal", "City of Sheridan",
        "WY-HORSLEY-AMBER-C", "Amber C. Horsley", 2027, 2031, 2026, "Succeeding; official 2026 general, 2,477 (vote for 3).")

    # Dayton
    add("Dayton Mayor", "municipal", "Town of Dayton",
        "WY-REED-CLIFFORD", "Clifford Reed", 2023, 2027, 2022, "Official 2022 general, 255.")
    add("Dayton Mayor", "municipal", "Town of Dayton",
        "WY-VISSER-HANLE", "Hanlé Visser", 2027, 2031, 2026, "Succeeding; official 2026 general, 284.")
    add("Dayton Town Council", "municipal", "Town of Dayton",
        "WY-HANSON-LISA-DAYTON", "Lisa Hanson", 2021, 2025, 2020, "Official 2020 general, 283 (vote for 2).")
    add("Dayton Town Council", "municipal", "Town of Dayton",
        "WY-REED-CLIFFORD", "Clifford Reed", 2021, 2025, 2020, "Official 2020 general, 236 (vote for 2). Later elected mayor in 2022.")
    add("Dayton Town Council", "municipal", "Town of Dayton",
        "WY-BERNARD-CHRISTOPHER-R", "Christopher R. Bernard", 2021, 2023, 2020,
        "Official 2020 general unexpired, 282.")
    add("Dayton Town Council", "municipal", "Town of Dayton",
        "WY-PERKINS-SANDY", "Sandy Perkins", 2023, 2027, 2022, "Official 2022 general, 325 (vote for 2).")
    add("Dayton Town Council", "municipal", "Town of Dayton",
        "WY-LOGAN-ROBERT", "Robert (Bobby) Logan", 2023, 2027, 2022, "Official 2022 general, 261 (vote for 2).")
    add("Dayton Town Council", "municipal", "Town of Dayton",
        "WY-GROVER-DAN", "Dan Grover", 2025, 2029, 2024, "Official 2024 general, 317 (vote for 2).")
    add("Dayton Town Council", "municipal", "Town of Dayton",
        "WY-ALLEY-ROBERT", "Robert Alley", 2025, 2029, 2024, "Official 2024 general, 295 (vote for 2).")
    add("Dayton Town Council", "municipal", "Town of Dayton",
        "WY-REES-ARIC", "Aric Rees", 2027, 2031, 2026, "Official 2026 general, 227 (vote for 2).")
    add("Dayton Town Council", "municipal", "Town of Dayton",
        "WY-LOGAN-ROBERT", "Robert (Bobby) Logan", 2027, 2031, 2026, "Re-elected; official 2026 general, 183 (vote for 2).")

    # Ranchester
    add("Ranchester Mayor", "municipal", "Town of Ranchester",
        "WY-CLARK-PETER", "Peter B. Clark", 2023, 2027, 2022, "Official 2022 general, 172.")
    add("Ranchester Mayor", "municipal", "Town of Ranchester",
        "WY-WEAVER-JESSICA", "Jessica Weaver", 2027, 2031, 2026,
        "Succeeding; official 2026 general, 253. Weaver also held a 2022 council term ending January 2027.")
    add("Ranchester Town Council", "municipal", "Town of Ranchester",
        "WY-BARRON-JEFFREY", "Jeffrey Barron", 2021, 2025, 2020,
        "Official 2020 general, 417 (vote for 2). Only one named candidate appeared; the second seat is not invented.")
    add("Ranchester Town Council", "municipal", "Town of Ranchester",
        "WY-SUNDQUIST-RANDY", "Randy Sundquist", 2023, 2027, 2022, "Official 2022 general, 289 (vote for 2).")
    add("Ranchester Town Council", "municipal", "Town of Ranchester",
        "WY-WEAVER-JESSICA", "Jessica Weaver", 2023, 2027, 2022, "Official 2022 general, 255 (vote for 2).")
    add("Ranchester Town Council", "municipal", "Town of Ranchester",
        "WY-MILES-SMITH-AMBER", "Amber Miles-Smith", 2025, 2029, 2024, "Official 2024 general, 245 (vote for 2).")
    add("Ranchester Town Council", "municipal", "Town of Ranchester",
        "WY-HELFERICH-BRYAN", "Bryan Helferich", 2025, 2029, 2024, "Official 2024 general, 232 (vote for 2).")
    add("Ranchester Town Council", "municipal", "Town of Ranchester",
        "WY-MAZE-TIM", "Tim Maze", 2027, 2031, 2026, "Official 2026 general, 280 (vote for 2).")
    add("Ranchester Town Council", "municipal", "Town of Ranchester",
        "WY-HOFMEIER-RICHARD", "Richard Hofmeier", 2027, 2031, 2026, "Official 2026 general, 228 (vote for 2).")
    # Weaver council term would overlap mayor starting Jan 2027; end council at FM[2027]
    # already term_end 2027 for 2022 council.

    # School District 1
    add("SD1 Trustee at-large", "schools", "Sheridan County School District No. 1",
        "WY-ADSIT-WILLIAM", "William (Bill) Adsit", 2023, 2027, 2022, "Official 2022 general, 821 (vote for 2).")
    add("SD1 Trustee at-large", "schools", "Sheridan County School District No. 1",
        "WY-KRUMM-CLINT", "Clint Krumm", 2023, 2027, 2022, "Official 2022 general, 730 (vote for 2).")
    add("SD1 Trustee at-large", "schools", "Sheridan County School District No. 1",
        "WY-STALICK-MORGAN", "Morgan (Barker) Stalick", 2025, 2029, 2024, "Official 2024 general, 1,033.")
    add("SD1 Trustee Big Horn", "schools", "Sheridan County School District No. 1",
        "WY-DAVIDSON-BRIAN-SD1", "Brian Davidson", 2025, 2029, 2024, "Official 2024 general, 1,481.")
    add("SD1 Trustee Tongue River", "schools", "Sheridan County School District No. 1",
        "WY-BITEMAN-MERCEDES", "Mercedes Biteman", 2025, 2029, 2024, "Official 2024 general, 2,342.")
    add("SD1 Trustee at-large", "schools", "Sheridan County School District No. 1",
        "WY-KRUMM-CLINT", "Clint Krumm", 2027, 2031, 2026, "Re-elected; official 2026 general, 1,263 (vote for 2).")
    add("SD1 Trustee at-large", "schools", "Sheridan County School District No. 1",
        "WY-WHITEHEAD-ERIC", "Eric Whitehead", 2027, 2031, 2026, "Succeeding; official 2026 general, 1,085 (vote for 2).")
    add("SD1 Trustee Big Horn", "schools", "Sheridan County School District No. 1",
        "WY-BAKER-CHAD-SD1", "Chad Baker", 2021, 2025, 2020, "Official 2020 general, 1,602.")
    add("SD1 Trustee Dayton area", "schools", "Sheridan County School District No. 1",
        "WY-LOFGREN-ERIC-O", "Eric O. Lofgren", 2021, 2025, 2020, "Official 2020 general “DAYTON TRUSTEE,” 1,628.")
    add("SD1 Trustee Tongue River", "schools", "Sheridan County School District No. 1",
        "WY-BITEMAN-MERCEDES", "Mercedes Biteman", 2021, 2025, 2020, "Official 2020 general “RANCHESTER TRUSTEE,” 2,199.")

    # School District 2
    for pid, name, v in [
        ("WY-WYATT-DANA", "Dana Wyatt", "6,178"),
        ("WY-EVERS-MARY-BETH", "Mary Beth Evers", "6,053"),
        ("WY-FESSLER-ED", "Ed Fessler", "5,692"),
        ("WY-SCHATZ-WAYNE", "Wayne Schatz", "4,711"),
        ("WY-RADER-SHANE", "Shane Rader", "4,337"),
    ]:
        add("SD2 Trustee", "schools", "Sheridan County School District No. 2",
            pid, name, 2021, 2025, 2020, f"Official 2020 general, {v} (vote for 5).")
    for pid, name, v in [
        ("WY-WADDELL-ARIN", "Arin Waddell", "3,552"),
        ("WY-PERKINS-ANN-M", "Ann M. Perkins", "3,380"),
        ("WY-LANSING-MICHAEL", "Michael Lansing", "3,040"),
        ("WY-RAMBUR-SHELTA", "Shelta Rambur", "2,558"),
    ]:
        add("SD2 Trustee", "schools", "Sheridan County School District No. 2",
            pid, name, 2023, 2027, 2022, f"Official 2022 general, {v} (vote for 4).")
    for pid, name, v in [
        ("WY-WYATT-DANA", "Dana Wyatt", "5,790"),
        ("WY-FESSLER-ED", "Ed Fessler", "5,587"),
        ("WY-MOORE-DOUG-SD2", "Doug Moore", "5,449"),
        ("WY-TOMLINSON-JEFF", "Jeff Tomlinson", "4,981"),
        ("WY-RADER-SHANE", "Shane Rader", "4,612"),
    ]:
        add("SD2 Trustee", "schools", "Sheridan County School District No. 2",
            pid, name, 2025, 2029, 2024, f"Official 2024 general, {v} (vote for 5).")
    for pid, name, v in [
        ("WY-PERKINS-ANN-M", "Ann M. Perkins", "5,112"),
        ("WY-CHRISTENSEN-CHASE", "Chase Christensen", "4,466"),
        ("WY-LANSING-MICHAEL", "Michael Lansing", "4,166"),
        ("WY-HAWKINS-PETER", "Peter Hawkins", "4,017"),
    ]:
        add("SD2 Trustee", "schools", "Sheridan County School District No. 2",
            pid, name, 2027, 2031, 2026, f"Official 2026 general, {v} (vote for 4).")

    # School District 3
    add("SD3 Trustee", "schools", "Sheridan County School District No. 3",
        "WY-VINEYARD-AMY", "Amy Vineyard", 2021, 2025, 2020, "Official 2020 general, 162 (vote for 3). Only two named candidates; a third winner is not invented.")
    add("SD3 Trustee", "schools", "Sheridan County School District No. 3",
        "WY-SCHOCK-CHRIS", "Chris Schock", 2021, 2025, 2020, "Official 2020 general, 142 (vote for 3).")
    add("SD3 Trustee", "schools", "Sheridan County School District No. 3",
        "WY-BETZ-WADE-A", "Wade A. Betz", 2023, 2027, 2022, "Official 2022 general, 107 (vote for 2).")
    add("SD3 Trustee", "schools", "Sheridan County School District No. 3",
        "WY-PRUSAK-KARIS", "Karis Prusak", 2023, 2027, 2022, "Official 2022 general, 105 (vote for 2).")
    for pid, name, v in [
        ("WY-LITTLE-KELLY-SD3", "Kelly Little", "148"),
        ("WY-GUYER-DEBORAH", "Deborah Guyer", "93"),
        ("WY-HACKETT-DUSTY", "Dusty Hackett", "79"),
    ]:
        add("SD3 Trustee", "schools", "Sheridan County School District No. 3",
            pid, name, 2025, 2029, 2024, f"Official 2024 general, {v} (vote for 3).")
    add("SD3 Trustee", "schools", "Sheridan County School District No. 3",
        "WY-MILLER-ERNIE", "Ernie Miller", 2027, 2031, 2026, "Official 2026 general, 103 (vote for 2, 4-year).")
    add("SD3 Trustee", "schools", "Sheridan County School District No. 3",
        "WY-HACKETT-GEORGINA", "Georgina Hackett", 2027, 2031, 2026, "Official 2026 general, 100 (vote for 2, 4-year). Ballot Georgina Hackett; official June 2026 roster lists Gina Hackett.")
    add("SD3 Trustee (2-year unexpired)", "schools", "Sheridan County School District No. 3",
        "WY-OLSEN-SAM", "Sam Olsen", 2027, 2029, 2026, "Official 2026 general 2-year unexpired, 107 (vote for 3). Ballot Samuel R. Olsen.")
    add("SD3 Trustee (2-year unexpired)", "schools", "Sheridan County School District No. 3",
        "WY-MALLI-KRISTINE", "Kristine Elaine Malli", 2027, 2029, 2026, "Official 2026 general 2-year unexpired, 97 (vote for 3).")
    add("SD3 Trustee (2-year unexpired)", "schools", "Sheridan County School District No. 3",
        "WY-BASSETT-ASHLEA", "Ashlea A. Bassett", 2027, 2029, 2026, "Official 2026 general 2-year unexpired, 82 (vote for 3).")

    # College
    for pid, name, v in [
        ("WY-KOLTISKA-GARY", "Gary Koltiska", "8,330"),
        ("WY-SWANSON-TRACY", "Tracy Swanson", "7,317"),
        ("WY-WENDTLAND-DEBRA-J", "Debra J. Wendtland", "7,202"),
        ("WY-KILBRIDE-ERIN", "Erin Kilbride", "6,682"),
    ]:
        add("College Trustee", "special-districts", "Sheridan Community College District",
            pid, name, 2021, 2025, 2020, f"Official 2020 general (Northern WY College), {v} (vote for 4).")
    for pid, name, v in [
        ("WY-HOLLOWAY-CHUCK", "Chuck Holloway", "4,326"),
        ("WY-COTTON-WARD", "Ward A. Cotton", "4,000"),
        ("WY-HENRY-ELAINE-OLAFSON", "Elaine Olafson Henry", "3,951"),
    ]:
        add("College Trustee", "special-districts", "Sheridan Community College District",
            pid, name, 2023, 2027, 2022, f"Official 2022 general, {v} (vote for 3).")
    for pid, name, v in [
        ("WY-SWANSON-TRACY", "Tracy Swanson", "8,782"),
        ("WY-RINGLEY-TOM", "Tom Ringley", "8,671"),
        ("WY-LEIBRICH-BOB", "Bob Leibrich", "7,406"),
        ("WY-REYNOLDS-GARY", "Gary Reynolds", "6,611"),
    ]:
        add("College Trustee", "special-districts", "Sheridan Community College District",
            pid, name, 2025, 2029, 2024, f"Official 2024 general, {v} (vote for 4).")
    for pid, name, v in [
        ("WY-JULIAN-DON", "Don Julian", "5,832"),
        ("WY-HENRY-ELAINE-OLAFSON", "Elaine Olafson Henry", "4,973"),
        ("WY-HOLLOWAY-CHUCK", "Chuck Holloway", "4,928"),
    ]:
        add("College Trustee", "special-districts", "Sheridan Community College District",
            pid, name, 2027, 2031, 2026, f"Official 2026 general, {v} (vote for 3).")

    # Conservation
    add("Conservation Rural", "special-districts", "Sheridan County Conservation District",
        "WY-MASTERS-STEPHANIE", "Stephanie Masters", 2021, 2025, 2020, "Official 2020 general, 8,261 (vote for 2).")
    add("Conservation Rural", "special-districts", "Sheridan County Conservation District",
        "WY-SCOTT-EMERSON", "Emerson Scott", 2021, 2025, 2020, "Official 2020 general, 8,246 (vote for 2).")
    add("Conservation Rural", "special-districts", "Sheridan County Conservation District",
        "WY-CONNELL-ORRIN", "Orrin Connell", 2023, 2027, 2022, "Official 2022 general, 9,260.")
    add("Conservation Urban", "special-districts", "Sheridan County Conservation District",
        "WY-HEYWARD-EDITH", "Edith Heyward", 2023, 2027, 2022, "Official 2022 general, 8,895.")
    add("Conservation At-large", "special-districts", "Sheridan County Conservation District",
        "WY-ADDLESPERGER-ANNIE", "Annie Addlesperger", 2023, 2027, 2022, "Official 2022 general, 8,992.")
    add("Conservation Rural", "special-districts", "Sheridan County Conservation District",
        "WY-MASTERS-STEPHANIE", "Stephanie Masters", 2025, 2029, 2024, "Official 2024 general, 6,541.")
    add("Conservation At-large", "special-districts", "Sheridan County Conservation District",
        "WY-WESTERN-JESSICA-M", "Jessica M. Western", 2025, 2029, 2024,
        "Official 2024 general, 10,572. Western also won the official 2026 at-large contest and is listed on the official June 2026 roster as expiring 2026; both official results are recorded.")
    add("Conservation At-large", "special-districts", "Sheridan County Conservation District",
        "WY-WESTERN-JESSICA-M", "Jessica M. Western", 2027, 2031, 2026, "Official 2026 general, 8,559.")
    add("Conservation Urban", "special-districts", "Sheridan County Conservation District",
        "WY-HEYWARD-EDITH", "Edith Heyward", 2027, 2031, 2026, "Re-elected; official 2026 general, 8,637.")
    add("Conservation Rural", "special-districts", "Sheridan County Conservation District",
        "WY-CONNELL-ORRIN", "Orrin Connell", 2027, 2031, 2026, "Re-elected; official 2026 general, 8,607.")

    # Senior Citizens Service District — elected 2026, ordinary start January 2027
    for pid, name, v in [
        ("WY-SIDDLE-NICK", "Nick Siddle", "3,876"),
        ("WY-JULIAN-DON", "Don Julian", "3,827"),
        ("WY-SHERWOOD-KATI", "Kati Sherwood", "3,285"),
        ("WY-LANDON-JACK-JR", "Jack Landon, Jr.", "3,110"),
        ("WY-CUSTIS-LYNN", "Lynn Custis", "2,797"),
    ]:
        add("Senior Citizens District Trustee", "special-districts", "Sheridan County Senior Citizens Service District",
            pid, name, 2027, 2031, 2026, f"Official 2026 general, {v} (vote for 5). New district trustees elected on the official 2026 general.")

    SRC_CLEARMONT = {"label": "Official Town of Clearmont city-government page, retrieved 2026-11-24",
                     "url": "https://www.townofclearmont.com/city-government"}
    terms.append(T(person_id="WY-SCHOCK-CHRIS", name="Chris Schock", office_group="municipal",
        office="Clearmont Mayor", jurisdiction="Town of Clearmont",
        term_start="2026-01-09", term_end="2027-06-30", how_took_office="elected", confidence="high",
        sources=[SRC_CLEARMONT],
        notes="Official Town of Clearmont city-government page, retrieved 2026-11-24: Chris Schock, Mayor. The same official Sheridan person ID is reused (prior official H40 and SCSD #3 service). The official page does not state a term end; encoded as current through the next ordinary May municipal cycle (June 2027) pending an official canvass. Official council minutes on that page are labeled unofficial and were not used as a canvass."))
    for pid, name in [
        ("WY-HARING-KAELAN", "Kaelan Haring"),
        ("WY-MILLER-ERNIE", "Ernie Miller"),
        ("WY-ROHRER-GREG", "Greg Rohrer"),
        ("WY-HUTCHISON-MADELINE", "Madeline Hutchison"),
    ]:
        terms.append(T(person_id=pid, name=name, office_group="municipal",
            office="Clearmont Town Council", jurisdiction="Town of Clearmont",
            term_start="2026-01-09", term_end="2027-06-30", how_took_office="elected", confidence="high",
            sources=[SRC_CLEARMONT],
            notes="Official Town of Clearmont city-government page, retrieved 2026-11-24. The official page does not state a term end; encoded as current through the next ordinary May municipal cycle (June 2027) pending an official canvass. Official council minutes on that page are labeled unofficial and were not used as a canvass."))
    return terms


def _register_extra(P):
    extras = [
        ("WY-KELLY-TOM", "Tom Kelly", "Tom", "Kelly", False, "Thomas M. Kelly"),
        ("WY-FENN-JOHN", "John G. Fenn", "John", "Fenn", False, ""),
        ("WY-DAY-SHAWN", "Shawn Day", "Shawn", "Day", True, ""),
        ("WY-JENNINGS-KRISTEN-CITY", "Kristen Jennings", "Kristen", "Jennings", True, ""),
        ("WY-HANSON-LISA-DAYTON", "Lisa Hanson", "Lisa", "Hanson", True, ""),
        ("WY-BERNARD-CHRISTOPHER-R", "Christopher R. Bernard", "Christopher", "Bernard", True, "R."),
        ("WY-BARRON-JEFFREY", "Jeffrey Barron", "Jeffrey", "Barron", True, ""),
        ("WY-BAKER-CHAD-SD1", "Chad Baker", "Chad", "Baker", True, ""),
        ("WY-LOFGREN-ERIC-O", "Eric O. Lofgren", "Eric", "Lofgren", True, "O."),
        ("WY-EVERS-MARY-BETH", "Mary Beth Evers", "Mary Beth", "Evers", True, ""),
        ("WY-SCHATZ-WAYNE", "Wayne Schatz", "Wayne", "Schatz", True, ""),
        ("WY-VINEYARD-AMY", "Amy Vineyard", "Amy", "Vineyard", True, ""),
        ("WY-BETZ-WADE-A", "Wade A. Betz", "Wade", "Betz", True, "A."),
        ("WY-PRUSAK-KARIS", "Karis Prusak", "Karis", "Prusak", True, ""),
        ("WY-KOLTISKA-GARY", "Gary Koltiska", "Gary", "Koltiska", True, ""),
        ("WY-WENDTLAND-DEBRA-J", "Debra J. Wendtland", "Debra", "Wendtland", True, "J."),
        ("WY-KILBRIDE-ERIN", "Erin Kilbride", "Erin", "Kilbride", True, ""),
        ("WY-SCOTT-EMERSON", "Emerson Scott", "Emerson", "Scott", True, ""),
        ("WY-HARING-KAELAN", "Kaelan Haring", "Kaelan", "Haring", True, ""),
        ("WY-ROHRER-GREG", "Greg Rohrer", "Greg", "Rohrer", True, ""),
        ("WY-HUTCHISON-MADELINE", "Madeline Hutchison", "Madeline", "Hutchison", True, ""),
    ]
    for pid, display, first, last, minted, extra in extras:
        middle = extra if minted and len(extra)<=3 and extra.endswith('.') else ""
        aliases = extra if not middle else ""
        if pid == "WY-BERNARD-CHRISTOPHER-R":
            middle = "R."; aliases = ""
        if pid == "WY-LOFGREN-ERIC-O":
            middle = "O."; aliases = ""
        if pid == "WY-BETZ-WADE-A":
            middle = "A."; aliases = ""
        if pid == "WY-WENDTLAND-DEBRA-J":
            middle = "J."; aliases = ""
        P(pid, display, first, last, middle=middle, aliases=aliases, minted=minted)


def build_sheridan():
    people: dict = {}
    P = H.person_factory(people)
    register_people(P)
    _register_extra(P)

    terms = county_and_legislature_terms() + local_terms()

    weston = json.loads((H.HISTORY / "weston" / "terms.json").read_text())
    copied = 0
    for t in weston["terms"]:
        og = t.get("office_group")
        office = (t.get("office") or "")
        if og in {"federal", "statewide"}:
            terms.append(deepcopy(t)); copied += 1
        elif og == "judicial" and any(x in office for x in ("Supreme Court", "Chancery")):
            rec = deepcopy(t)
            if rec.get("election_year") in SG:
                rec["sources"] = list(rec.get("sources") or []) + [sg(rec["election_year"])]
            terms.append(rec); copied += 1
        # Do not copy 6th Judicial District judges.

    H.attach_people_from_terms(terms, people)

    expected = {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [
            ("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
            ("State Treasurer", 1), ("Superintendent of Public Instruction", 1),
        ],
        "state-senate": [
            ("Senate District 21 (S21)", 1),
            ("Senate District 22 (S22)", 1),
        ],
        "state-house": [
            ("House District 29 (H29)", 1),
            ("House District 30 (H30)", 1),
            ("House District 40 (H40)", 1),
            ("House District 51 (H51)", 1),
        ],
        "county": [
            ("County Commissioner", 5), ("County Clerk", 1), ("County Treasurer", 1),
            ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
            ("Clerk of District Court", 1), ("County Coroner", 1),
        ],
        "municipal": [
            ("Sheridan Mayor", 1), ("Sheridan City Council", 6),
            ("Dayton Mayor", 1), ("Dayton Town Council", 4),
            ("Ranchester Mayor", 1), ("Ranchester Town Council", 4),
            ("Clearmont Mayor", 1), ("Clearmont Town Council", 4),
        ],
        # School and special expected counts are not padded.
    }

    judicial_note = (
        "Supreme Court justices and the Chancery Court judge are the people in office this January, from official "
        "Wyoming Judicial Branch dates and official retention results (shared with other counties). Local rows are "
        "4th Judicial District judges who appeared by name on a Sheridan County official retention ballot in an adjoining "
        "cycle. The official 2018 general lists a 4th Judicial Circuit Court judge retention with no judge’s name; that "
        "retention is not attached to a person. Sheryl Smith Bunting is named as Circuit Judge on the official June 12, 2026 "
        "clerk roster but did not appear on the official 2026 general summary."
    )
    special_note = (
        "Municipal, school, and special-district names before the official 2020 general are not all keyed in this preview; "
        "those earlier January seats are marked Not yet collected rather than invented. The Town of Clearmont does not appear "
        "on the official county November generals reviewed or on the official June 2026 roster. The official 2020 Ranchester "
        "council and School District 3 trustee contests listed fewer named candidates than the vote-for number; extra seats "
        "are not invented. The official 2024 and 2026 Conservation District at-large results both name Jessica M. Western; "
        "both are recorded. Senior Citizens Service District trustees were elected on the official 2026 general and take office in January 2027."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. Official Sheridan primary PDFs are "
        "archived under /workspace/wyoleg/local-results/sheridan/<year>/. The current (November 2026) precinct roster "
        "is in data/county_officials/sheridan.json, from the official 2026 primary (named winners only)."
    )

    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Sheridan", county_number=3, slug="sheridan", terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Sheridan", slug="sheridan")
    print(f"wrote {terms_path}")
    print(f"terms {len(terms)} (including {copied} shared federal/statewide/SC-chancery terms)")
    print(f"people_additions +{n_people} offices_held +{n_off} thin_profiles +{n_prof}")
    H.print_coverage(coverage_all)
    return people, terms, coverage_all


def _holder(people, pid, *, sources, term_end="", party="", notes="", succeeding=None, extra=None, confidence="high"):
    p = people[pid]
    h = {
        "name": p["display_name"],
        "person_id": pid,
        "party": party,
        "sources": sources,
        "confidence": confidence,
        "href": f"candidates/local-history/c/{p['slug']}.html",
    }
    if term_end:
        h["term_end"] = term_end
    if notes:
        h["notes"] = notes
    if succeeding:
        h["succeeding"] = succeeding
    if extra:
        h.update(extra)
    return h


def _succ(people, pid, *, sources, term_end, takes_office="January"):
    p = people[pid]
    return {
        "name": p["display_name"],
        "person_id": pid,
        "party": "",
        "takes_office": takes_office,
        "term_end": term_end,
        "sources": sources,
        "href": f"candidates/local-history/c/{p['slug']}.html",
    }


def update_sheridan_json(people: dict):
    path = ROOT / "data" / "county_officials" / "sheridan.json"
    data = json.loads(path.read_text())
    g2026 = [sg(2026)]
    g2024 = [sg(2024)]
    g2022 = [sg(2022)]
    HLD = lambda pid, sources, term_end, party="", notes="", succeeding=None, extra=None, confidence="high": \
        _holder(people, pid, sources=sources, term_end=term_end, party=party, notes=notes,
                succeeding=succeeding, extra=extra, confidence=confidence)

    senate = {
        "id": "state-senate", "title": "State Senate", "sort_key": "C",
        "offices": [
            {"office": "Senate District 21 (S21)", "layout": "office-and-name", "sort_key": "C01",
             "holders": [HLD("WY-BITEMAN-BO", g2022, "January 2027", "R",
                             succeeding=_succ(people, "WY-BUTCHER-MELISSA", sources=g2026, term_end="January 2031"))]},
            {"office": "Senate District 22 (S22)", "layout": "office-and-name", "sort_key": "C02",
             "holders": [HLD("WY-CRAGO-BARRY", g2024, "January 2029", "R")]},
        ],
    }
    house = {
        "id": "state-house", "title": "State House", "sort_key": "D",
        "offices": [
            {"office": "House District 29 (H29)", "layout": "office-and-name", "sort_key": "D01",
             "holders": [HLD("WY-PENDERGRAFT-KEN", g2024, "January 2027", "R",
                             succeeding=_succ(people, "WY-STURTEVANT-MYCA", sources=g2026, term_end="January 2029"))]},
            {"office": "House District 30 (H30)", "layout": "office-and-name", "sort_key": "D02",
             "holders": [HLD("WY-KELLY-TOM", g2024, "January 2027", "R",
                             succeeding=_succ(people, "WY-KOLTISKA-JOHN", sources=g2026, term_end="January 2029"))]},
            {"office": "House District 40 (H40)", "layout": "office-and-name", "sort_key": "D03",
             "holders": [HLD("WY-CONNOLLY-MARILYN", [*g2024, *g2026], "January 2029", "R",
                             notes="Re-elected 2026; official 2026 general, 555.")]},
            {"office": "House District 51 (H51)", "layout": "office-and-name", "sort_key": "D04",
             "holders": [HLD("WY-BRATTEN-LAURIE", [*g2024, *g2026], "January 2029", "R",
                             notes="Re-elected 2026; official 2026 general, 3,774.")]},
        ],
    }
    county = {
        "id": "county", "title": "County Offices", "sort_key": "E",
        "note": "The official June 12, 2026 clerk roster still lists Paul Fall as County Assessor (term expiring 2026). Koko Knudtson was elected in the official 2026 general and takes office January 2027.",
        "offices": [
            {"office": "County Commissioners", "layout": "heading-then-names", "sort_key": "E01",
             "holders": [
                 HLD("WY-HASWELL-CHRISTI", [*g2022, *g2026], "January 2031", "R",
                     notes="Re-elected 2026; official 2026 general, 7,733."),
                 HLD("WY-WRIGHT-LONNIE", g2024, "January 2029", "R"),
                 HLD("WY-SIDDLE-NICK", g2022, "January 2027", "R",
                     succeeding=_succ(people, "WY-SCHELLINGER-JIM", sources=g2026, term_end="January 2031")),
                 HLD("WY-ARZY-MICHAEL", g2024, "January 2029", "R"),
                 HLD("WY-JENNINGS-HOLLY", [*g2024, *g2026], "January 2031", "R",
                     notes="Won the official 2024 2-year seat and was elected to a 4-year term in 2026; official 2026 general, 7,447."),
             ]},
            {"office": "County Clerk", "layout": "office-and-name", "sort_key": "E02",
             "holders": [HLD("WY-THOMPSON-EDA", g2026, "January 2031", "R",
                             notes="Re-elected 2026; official 2026 general, 10,195.")]},
            {"office": "County Treasurer", "layout": "office-and-name", "sort_key": "E03",
             "holders": [HLD("WY-ARAAS-KATIE", g2026, "January 2031", "R",
                             notes="Re-elected 2026; official 2026 general, 10,540.")]},
            {"office": "County Assessor", "layout": "office-and-name", "sort_key": "E04",
             "holders": [HLD("WY-FALL-PAUL", [ROSTER, *g2022], "January 2027", "R",
                             notes="Official 2022 general, 10,454. Named as assessor on the official June 12, 2026 roster.",
                             succeeding=_succ(people, "WY-KNUDTSON-KOKO", sources=g2026, term_end="January 2031"))]},
            {"office": "County Sheriff", "layout": "office-and-name", "sort_key": "E05",
             "holders": [HLD("WY-DOMINGUEZ-LEVI", g2026, "January 2031", "R",
                             notes="Re-elected 2026; official 2026 general, 10,275.")]},
            {"office": "County Attorney", "layout": "office-and-name", "sort_key": "E06",
             "holders": [HLD("WY-BENNETT-DIANNA", g2026, "January 2031", "R",
                             notes="Re-elected 2026; official 2026 general, 9,800.")]},
            {"office": "Clerk of District Court", "layout": "office-and-name", "sort_key": "E07",
             "holders": [HLD("WY-BOTTEN-RENE", g2026, "January 2031", "R",
                             notes="Re-elected 2026; official 2026 general, 10,210.")]},
            {"office": "County Coroner", "layout": "office-and-name", "sort_key": "E08",
             "holders": [HLD("WY-BYRD-ROBERT", g2026, "January 2031", "R",
                             notes="Re-elected 2026; official 2026 general, 9,991.")]},
        ],
    }
    municipal = {
        "id": "municipal", "title": "Municipal offices", "sort_key": "F",
        "note": (
            "The City of Sheridan and the Towns of Dayton and Ranchester appear on the official Sheridan County November general ballot. "
            "The Town of Clearmont does not appear on those official generals (2012–2026) or on the official June 2026 elected-officials roster. Current Clearmont holders are taken from the official Town of Clearmont city-government page, retrieved 2026-11-24."
        ),
        "offices": [
            {"office": "Sheridan Mayor", "layout": "office-and-name", "sort_key": "F01",
             "holders": [HLD("WY-BRIDGER-RICHARD", g2024, "January 2029")]},
            {"office": "Sheridan City Council", "layout": "heading-then-names", "sort_key": "F02",
             "holders": [
                 HLD("WY-LUHMAN-GREG", [*g2022, *g2026], "January 2031", notes="Re-elected 2026; official 2026 general, 3,201."),
                 HLD("WY-WEITZEL-TERRY", [*g2022, *g2026], "January 2031", notes="Re-elected 2026; official 2026 general, 3,133."),
                 HLD("WY-PATCEG-ANDREW", g2022, "January 2027",
                     succeeding=_succ(people, "WY-HORSLEY-AMBER-C", sources=g2026, term_end="January 2031")),
                 HLD("WY-WOOD-JACK", g2024, "January 2029"),
                 HLD("WY-LEICHTNAM-BEV", g2024, "January 2029"),
                 HLD("WY-BRANTZ-STEVEN", g2024, "January 2029"),
             ]},
            {"office": "Dayton Mayor", "layout": "office-and-name", "sort_key": "F03",
             "holders": [HLD("WY-REED-CLIFFORD", g2022, "January 2027",
                             succeeding=_succ(people, "WY-VISSER-HANLE", sources=g2026, term_end="January 2031"))]},
            {"office": "Dayton Town Council", "layout": "heading-then-names", "sort_key": "F04",
             "holders": [
                 HLD("WY-LOGAN-ROBERT", [*g2022, *g2026], "January 2031", notes="Re-elected 2026; official 2026 general, 183."),
                 HLD("WY-PERKINS-SANDY", g2022, "January 2027",
                     succeeding=_succ(people, "WY-REES-ARIC", sources=g2026, term_end="January 2031")),
                 HLD("WY-GROVER-DAN", g2024, "January 2029"),
                 HLD("WY-ALLEY-ROBERT", g2024, "January 2029"),
             ]},
            {"office": "Ranchester Mayor", "layout": "office-and-name", "sort_key": "F05",
             "holders": [HLD("WY-CLARK-PETER", g2022, "January 2027",
                             succeeding=_succ(people, "WY-WEAVER-JESSICA", sources=g2026, term_end="January 2031"))]},
            {"office": "Ranchester Town Council", "layout": "heading-then-names", "sort_key": "F06",
             "holders": [
                 HLD("WY-SUNDQUIST-RANDY", g2022, "January 2027",
                     succeeding=_succ(people, "WY-MAZE-TIM", sources=g2026, term_end="January 2031")),
                 HLD("WY-WEAVER-JESSICA", g2022, "January 2027",
                     notes="Elected mayor in 2026; the official 2026 council vote-for-2 names Tim Maze and Richard Hofmeier.",
                     succeeding=_succ(people, "WY-HOFMEIER-RICHARD", sources=g2026, term_end="January 2031")),
                 HLD("WY-MILES-SMITH-AMBER", g2024, "January 2029"),
                 HLD("WY-HELFERICH-BRYAN", g2024, "January 2029"),
             ]},
            {"office": "Clearmont Mayor", "layout": "office-and-name", "sort_key": "F07",
             "holders": [HLD("WY-SCHOCK-CHRIS", [{"label": "Official Town of Clearmont city-government page, retrieved 2026-11-24", "url": "https://www.townofclearmont.com/city-government"}], "",
                             notes="Official Town of Clearmont city-government page, retrieved 2026-11-24. No term end stated on the official page.")]},
            {"office": "Clearmont Town Council", "layout": "heading-then-names", "sort_key": "F08",
             "holders": [
                 HLD("WY-HARING-KAELAN", [{"label": "Official Town of Clearmont city-government page, retrieved 2026-11-24", "url": "https://www.townofclearmont.com/city-government"}], "",
                     notes="Official Town of Clearmont city-government page, retrieved 2026-11-24. No term end stated on the official page."),
                 HLD("WY-MILLER-ERNIE", [{"label": "Official Town of Clearmont city-government page, retrieved 2026-11-24", "url": "https://www.townofclearmont.com/city-government"}], "",
                     notes="Official Town of Clearmont city-government page, retrieved 2026-11-24. The official Sheridan person ID already used for SCSD #3 is reused. No term end stated on the official page."),
                 HLD("WY-ROHRER-GREG", [{"label": "Official Town of Clearmont city-government page, retrieved 2026-11-24", "url": "https://www.townofclearmont.com/city-government"}], "",
                     notes="Official Town of Clearmont city-government page, retrieved 2026-11-24. No term end stated on the official page."),
                 HLD("WY-HUTCHISON-MADELINE", [{"label": "Official Town of Clearmont city-government page, retrieved 2026-11-24", "url": "https://www.townofclearmont.com/city-government"}], "",
                     notes="Official Town of Clearmont city-government page, retrieved 2026-11-24. No term end stated on the official page."),
             ]},
        ],
    }
    schools = {
        "id": "schools", "title": "School boards", "sort_key": "G",
        "offices": [
            {"office": "Sheridan County School District No. 1", "layout": "heading-then-names", "sort_key": "G01",
             "holders": [
                 HLD("WY-KRUMM-CLINT", [*g2022, *g2026], "January 2031", notes="Re-elected 2026; official 2026 general, 1,263."),
                 HLD("WY-ADSIT-WILLIAM", g2022, "January 2027",
                     succeeding=_succ(people, "WY-WHITEHEAD-ERIC", sources=g2026, term_end="January 2031")),
                 HLD("WY-STALICK-MORGAN", g2024, "January 2029", notes="At-large, official 2024 general."),
                 HLD("WY-DAVIDSON-BRIAN-SD1", g2024, "January 2029", notes="Big Horn area, official 2024 general."),
                 HLD("WY-BITEMAN-MERCEDES", g2024, "January 2029", notes="Tongue River area, official 2024 general."),
             ]},
            {"office": "Sheridan County School District No. 2", "layout": "heading-then-names", "sort_key": "G02",
             "holders": [
                 HLD("WY-LANSING-MICHAEL", [*g2022, *g2026], "January 2031", notes="Re-elected 2026; official 2026 general, 4,166."),
                 HLD("WY-PERKINS-ANN-M", [*g2022, *g2026], "January 2031", notes="Re-elected 2026; official 2026 general, 5,112."),
                 HLD("WY-RAMBUR-SHELTA", g2022, "January 2027",
                     succeeding=_succ(people, "WY-CHRISTENSEN-CHASE", sources=g2026, term_end="January 2031")),
                 HLD("WY-WADDELL-ARIN", g2022, "January 2027",
                     succeeding=_succ(people, "WY-HAWKINS-PETER", sources=g2026, term_end="January 2031")),
                 HLD("WY-WYATT-DANA", g2024, "January 2029"),
                 HLD("WY-FESSLER-ED", g2024, "January 2029"),
                 HLD("WY-MOORE-DOUG-SD2", g2024, "January 2029"),
                 HLD("WY-TOMLINSON-JEFF", g2024, "January 2029"),
                 HLD("WY-RADER-SHANE", g2024, "January 2029"),
             ]},
            {"office": "Sheridan County School District No. 3", "layout": "heading-then-names", "sort_key": "G03",
             "note": "The official June 2026 roster lists Sam Olsen and Gina Hackett in 4-year seats expiring 2026, and Ernie Miller, Ashlea Bassett, and Kris Malli in 2-year unexpired seats. The official 2024 general also elected Kelly Little, Deborah Guyer, and Dusty Hackett to terms through January 2029. Official 2026 4-year winners are Ernie Miller and Georgina Hackett; official 2026 2-year unexpired winners are Samuel R. Olsen, Kristine Elaine Malli, and Ashlea A. Bassett.",
             "holders": [
                 HLD("WY-OLSEN-SAM", [ROSTER], "January 2027",
                     notes="Named on the official June 2026 roster in a 4-year seat expiring 2026. Official 2026 2-year unexpired elect (takes office January 2027).",
                     succeeding=_succ(people, "WY-OLSEN-SAM", sources=g2026, term_end="January 2029")),
                 HLD("WY-HACKETT-GEORGINA", [ROSTER], "January 2027",
                     notes="Official June 2026 roster lists Gina Hackett in a 4-year seat expiring 2026.",
                     succeeding=_succ(people, "WY-HACKETT-GEORGINA", sources=g2026, term_end="January 2031")),
                 HLD("WY-MILLER-ERNIE", [ROSTER], "January 2027",
                     notes="Official June 2026 roster, 2-year unexpired seat.",
                     succeeding=_succ(people, "WY-MILLER-ERNIE", sources=g2026, term_end="January 2031")),
                 HLD("WY-BASSETT-ASHLEA", [ROSTER], "January 2027",
                     notes="Official June 2026 roster, 2-year unexpired seat.",
                     succeeding=_succ(people, "WY-BASSETT-ASHLEA", sources=g2026, term_end="January 2029")),
                 HLD("WY-MALLI-KRISTINE", [ROSTER], "January 2027",
                     notes="Official June 2026 roster, 2-year unexpired seat (Kris Malli).",
                     succeeding=_succ(people, "WY-MALLI-KRISTINE", sources=g2026, term_end="January 2029")),
                 HLD("WY-LITTLE-KELLY-SD3", g2024, "January 2029"),
                 HLD("WY-GUYER-DEBORAH", g2024, "January 2029"),
                 HLD("WY-HACKETT-DUSTY", g2024, "January 2029"),
             ]},
        ],
    }
    special = {
        "id": "special-districts", "title": "Special districts", "sort_key": "H",
        "note": (
            "Sheridan Community College District appears on official generals as Sheridan Community College / Northern Wyoming Community College. "
            "Senior Citizens Service District trustees were elected on the official 2026 general and take office in January 2027."
        ),
        "offices": [
            {"office": "Sheridan Community College District", "layout": "heading-then-names", "sort_key": "H01",
             "holders": [
                 HLD("WY-HOLLOWAY-CHUCK", [*g2022, *g2026], "January 2031", notes="Re-elected 2026; official 2026 general, 4,928."),
                 HLD("WY-HENRY-ELAINE-OLAFSON", [*g2022, *g2026], "January 2031", notes="Re-elected 2026; official 2026 general, 4,973."),
                 HLD("WY-COTTON-WARD", g2022, "January 2027",
                     succeeding=_succ(people, "WY-JULIAN-DON", sources=g2026, term_end="January 2031")),
                 HLD("WY-SWANSON-TRACY", g2024, "January 2029"),
                 HLD("WY-RINGLEY-TOM", g2024, "January 2029"),
                 HLD("WY-LEIBRICH-BOB", g2024, "January 2029"),
                 HLD("WY-REYNOLDS-GARY", g2024, "January 2029"),
             ]},
            {"office": "Sheridan County Conservation District At-large", "layout": "office-and-name", "sort_key": "H02",
             "holders": [HLD("WY-ADDLESPERGER-ANNIE", g2022, "January 2027",
                             notes="Official 2022 general, 8,992. Jessica M. Western also won official 2024 and 2026 at-large contests.",
                             succeeding=_succ(people, "WY-WESTERN-JESSICA-M", sources=g2026, term_end="January 2031"))]},
            {"office": "Sheridan County Conservation District Urban", "layout": "office-and-name", "sort_key": "H03",
             "holders": [HLD("WY-HEYWARD-EDITH", [*g2022, *g2026], "January 2031",
                             notes="Re-elected 2026; official 2026 general, 8,637.")]},
            {"office": "Sheridan County Conservation District Rural", "layout": "heading-then-names", "sort_key": "H04",
             "holders": [
                 HLD("WY-CONNELL-ORRIN", [*g2022, *g2026], "January 2031", notes="Re-elected 2026; official 2026 general, 8,607."),
                 HLD("WY-MASTERS-STEPHANIE", g2024, "January 2029"),
             ]},
            {"office": "Sheridan County Senior Citizens Service District", "layout": "heading-then-names", "sort_key": "H05",
             "holders": [
                 # January 2027 elects only — no current named holders
             ],
             "note": "Trustees elected on the official 2026 general take office in January 2027. Current (November 2026) named holders are not listed on the official June 2026 roster.",
            },
        ],
    }
    # Put 2027 elects in succeeding-style via a synthetic note holders empty + elect list in note is weak.
    # Better: use holders with takes_office January and no current, by adding succeeding-only entries as holders with term not started? 
    # The 114 format uses succeeding beside a current name. For a new district, list the five as holders with term_end January 2031 and a note "Takes office January 2027".
    special["offices"][-1]["holders"] = [
        HLD(pid, g2026, "January 2031", notes="Takes office January 2027; official 2026 general (vote for 5).")
        for pid in ("WY-SIDDLE-NICK", "WY-JULIAN-DON", "WY-SHERWOOD-KATI", "WY-LANDON-JACK-JR", "WY-CUSTIS-LYNN")
    ]

    def pct(yes, no):
        tot = yes + no
        return f"{yes/tot*100:.2f}%", f"{no/tot*100:.2f}%"
    yp, np = pct(11859, 2305)
    yp2, np2 = pct(11490, 2300)
    judicial = {
        "id": "judicial", "title": "Judicial retention (district and circuit)", "sort_key": "J3",
        "note": (
            "Supreme Court justices and the Chancery Court judge are in the shared statewide judicial file. "
            "Local names are 4th Judicial District judges retained by name on official Sheridan County general ballots, "
            "plus the circuit judge named on the official June 12, 2026 clerk roster. Sheryl Smith Bunting did not appear "
            "on the official 2026 general summary. The official 2018 circuit-judge retention has no name on the summary."
        ),
        "offices": [
            {"office": "District Judge, 4th Judicial District", "layout": "office-and-name", "sort_key": "J03",
             "holders": [{
                 "name": "Darci A.V. Phillips", "person_id": "WY-PHILLIPS-DARCI",
                 "href": f"candidates/local-history/c/{people['WY-PHILLIPS-DARCI']['slug']}.html",
                 "sources": [sg(2024)],
                 "notes": "Official 2024 general “RETAIN JUDGE A DARCI A.V. PHILLIPS.”",
                 "retention": {"year": 2024, "yes": 11859, "no": 2305, "yes_pct": yp, "no_pct": np,
                               "result": "retained", "source": SG[2024][0]},
             }]},
            {"office": "Judge, 4th Judicial District (official 2024 Judge B retention)", "layout": "office-and-name", "sort_key": "J04",
             "holders": [{
                 "name": "Benjamin Kirven", "person_id": "WY-KIRVEN-BENJAMIN",
                 "href": f"candidates/local-history/c/{people['WY-KIRVEN-BENJAMIN']['slug']}.html",
                 "sources": [sg(2024)],
                 "notes": "Official 2024 general “RETAIN JUDGE B BENJAMIN KIRVEN.” The official title does not independently confirm district vs. circuit.",
                 "retention": {"year": 2024, "yes": 11490, "no": 2300, "yes_pct": yp2, "no_pct": np2,
                               "result": "retained", "source": SG[2024][0]},
             }]},
            {"office": "Circuit Judge, 4th Judicial District", "layout": "office-and-name", "sort_key": "J05",
             "holders": [HLD("WY-BUNTING-SHERYL-SMITH", [ROSTER], "",
                             notes="Named as Circuit Judge on the official June 12, 2026 elected-officials roster (term listed as expiring 2026). This judge did not appear by name on the official 2026 general summary.",
                             confidence="medium")]},
        ],
    }

    kept = [g for g in data["groups"] if g["id"] not in {
        "state-senate", "state-house", "county", "municipal", "schools", "special-districts", "judicial"
    }]
    data["groups"] = [senate, house, county] + kept + [municipal, schools, special, judicial]
    data["as_of"] = "2026-11-24"
    data["term_switch_date"] = "2027-01-04"
    data["page_version"] = "v2.0"
    data["sources"] = {
        "general_results": SG[2026][0],
        "primary_results": "https://www.sheridancountywy.gov/Document Center/Departments/Elected Office/2026 Election Documents/Primary/Official Results.pdf",
        "checked": RETRIEVED,
        "clerk_archive": "https://www.sheridancountywy.gov/departments/elections/election_results_archive.php",
        "clerk_2026": "https://www.sheridancountywy.gov/departments/elections/2026_election_results.php",
        "local_archive": "/workspace/wyoleg/local-results/sheridan/SOURCES.md",
        "roster": ROSTER["url"],
    }
    apply_to_groups(data["groups"], 'sheridan')
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"updated {path}")
