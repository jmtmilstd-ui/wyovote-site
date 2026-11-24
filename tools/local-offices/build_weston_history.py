#!/usr/bin/env python3
"""Build Weston effective-dated officeholder history and January snapshots, 2015-2026.

Preview only: writes data under the 114 worktree and local-results. Does not merge or publish.
"""
from __future__ import annotations

import csv
import html
import json
import re
from collections import defaultdict
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from legislative_office_notes import apply_to_groups

ROOT = Path(__file__).resolve().parents[2]
HISTORY = ROOT / "data" / "county_officials" / "history"
WESTON_H = HISTORY / "weston"
SHARED_H = HISTORY / "shared"
PEOPLE_DIR = ROOT / "data" / "people"
LOCAL = ROOT / "tools" / "local-data"
PROFILE_DIR = ROOT / "candidates" / "local-history" / "c"
NAME_INDEX_PEOPLE = Path("/workspace/name-index/data/people.csv")
SOURCES_PAGE = "https://www.westongov.com/county-clerk/elections/election-results/"
RETRIEVED = "2026-11-23"

# First Monday in January (America/Denver calendar date).
def first_monday(year: int) -> str:
    d = date(year, 1, 1)
    d = d + timedelta(days=(7 - d.weekday()) % 7)
    return d.isoformat()

FM = {y: first_monday(y) for y in range(2008, 2040)}
JAN3 = {y: f"{y}-01-03" for y in range(2008, 2040)}

# Official Weston County Clerk general (EL45 / official summary) URLs
WG = {
    2012: ("https://www.westongov.com/wp-content/uploads/2019/05/EL45-Cumulative-OFFICIAL-2012-General.pdf",
           "Weston County official 2012 general results"),
    2014: ("https://www.westongov.com/wp-content/uploads/2019/05/2014-General-EL45-Cumulative.pdf",
           "Weston County official 2014 general results"),
    2016: ("https://www.westongov.com/wp-content/uploads/2019/05/WestonCounty_EL45_10Nov2016_OFFICIAL_RESULTS.pdf",
           "Weston County official 2016 general results"),
    2018: ("https://www.westongov.com/wp-content/uploads/2021/01/Weston-County-OFFICIAL-RESULTS_11.9.2018-EL45.pdf",
           "Weston County official 2018 general results"),
    2020: ("https://www.westongov.com/wp-content/uploads/2020/11/Official-General-Election-2020.pdf",
           "Weston County official 2020 general results"),
    2022: ("https://www.westongov.com/wp-content/uploads/2022/11/Weston-County-Official-Results-General-2022.pdf",
           "Weston County official 2022 general results"),
    2024: ("https://www.westongov.com/wp-content/uploads/2024/11/Official-Weston-County-2024-General-Election-Summary.pdf",
           "Weston County official 2024 general results"),
    2026: ("https://www.westongov.com/wp-content/uploads/2026/11/official-local-gen-sum.pdf",
           "Weston County official 2026 general results"),
}
WP = {  # official primaries (precinct committee)
    2012: ("https://www.westongov.com/wp-content/uploads/2019/05/OFFICIAL-EL45-2012-Primary.pdf",
           "Weston County official 2012 primary results"),
    2014: ("https://www.westongov.com/wp-content/uploads/2019/05/Official-EL45_2014-Primary_consolidated.pdf",
           "Weston County official 2014 primary results"),
    2016: ("https://www.westongov.com/wp-content/uploads/2019/05/2016-Primary_OfficialResults_EL45_20Aug2016.pdf",
           "Weston County official 2016 primary results"),
    2018: ("https://www.westongov.com/wp-content/uploads/2021/01/Weston-County-Primary-EL45-OFFICIAL-Results-8.23.2018.pdf",
           "Weston County official 2018 primary results"),
    2020: ("https://www.westongov.com/wp-content/uploads/2020/08/Election-Summary-Offical-Results.pdf",
           "Weston County official 2020 primary results"),
    2022: ("https://www.westongov.com/wp-content/uploads/2022/08/Official-2022-Primary-Election.pdf",
           "Weston County official 2022 primary results"),
    2024: ("https://www.westongov.com/wp-content/uploads/2024/08/Weston-County-Primary-Election-Summary-2024-Official-Results.pdf",
           "Weston County official 2024 primary results"),
    2026: ("https://www.westongov.com/wp-content/uploads/2026/08/2026-Primary-Official-Results.pdf",
           "Weston County official 2026 primary results"),
}
SRC113 = "WyoVote 113 County Report for Weston (legislators serving that session)"
SRC_SW = "/workspace/wyoleg/statewide/statewide_officials_2008_2026.csv"
SRC_SOS = "https://sos.wyo.gov/Elections/ElectionResults.aspx"
SRC_HOSP = ("https://www.westongov.com/wp-content/uploads/2019/05/18HospitalDistrictElectionResults.pdf",
            "Weston County Hospital District official May 8, 2018 trustee canvass")
SRC_MUS = ("https://www.westongov.com/wp-content/uploads/2019/05/18ElectionResults.pdf",
           "Weston County Museum District official May 8, 2018 trustee canvass")

def src(year, kind="general"):
    url, label = (WG if kind == "general" else WP)[year]
    return {"label": label, "url": url}

def srcs(*items):
    out = []
    for it in items:
        if isinstance(it, dict):
            out.append(it)
        elif isinstance(it, tuple):
            out.append({"label": it[1], "url": it[0]})
        elif it == "113":
            out.append({"label": SRC113, "url": ""})
        elif it == "sw":
            out.append({"label": "WyoVote statewide officials file (official SOS rosters and results)", "url": SRC_SOS})
        elif it == "sos":
            out.append({"label": "Wyoming SOS official election results", "url": SRC_SOS})
        else:
            out.append({"label": str(it), "url": ""})
    return out

# person registry: person_id -> record
PEOPLE: dict[str, dict] = {}

def person(pid, display, first, last, middle="", aliases="", minted=True, slug=""):
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "-", display.lower()).strip("-")
    rec = dict(person_id=pid, slug=slug, display_name=display, sort_name=f"{last}, {first}",
               first=first, middle=middle, last=last, suffix="", aliases=aliases,
               minted="Y" if minted else "N")
    PEOPLE[pid] = rec
    return pid

# Reused IDs (minted=N)
person("WY-BARRASSO-JOHN", "John Barrasso", "John", "Barrasso", minted=False)
person("WY-CHENEY-ELIZABETH", "Liz Cheney", "Liz", "Cheney", aliases="Elizabeth Cheney", minted=False)
person("WY-HAGEMAN-HARRIET", "Harriet Hageman", "Harriet", "Hageman", minted=False)
person("WY-GRAY-CHUCK", "Chuck Gray", "Chuck", "Gray", minted=False)
person("WY-GORDON-MARK", "Mark Gordon", "Mark", "Gordon", minted=False)
person("WY-BARLOW-ERIC", "Eric Barlow", "Eric", "Barlow", minted=False)
person("WY-MEAD-MATT", "Matt Mead", "Matt", "Mead", minted=True)  # in statewide CSV, may be missing from name-index
person("WY-MURRAY-EDWARD", "Edward F. Murray, III", "Edward", "Murray", middle="F.", aliases="Ed Murray", minted=True)
person("WY-WHEELER-KAREN", "Karen L. Wheeler", "Karen", "Wheeler", middle="L.", minted=True)
person("WY-BUCHANAN-EDWARD", "Edward A. Buchanan", "Edward", "Buchanan", middle="A.", aliases="Ed Buchanan", minted=False)
person("WY-ALLRED-KARL", "Karl Allred", "Karl", "Allred", minted=False)
person("WY-SHORT-ROBERT", "Robert Short", "Robert", "Short", minted=False)
person("WY-CLOUD-CYNTHIA", "Cynthia Cloud", "Cynthia", "Cloud", aliases="Cynthia I. Cloud", minted=True)
person("WY-RACINES-KRISTI", "Kristi Racines", "Kristi", "Racines", minted=False)
person("WY-MEIER-CURTIS", "Curt Meier", "Curt", "Meier", aliases="Curtis E Meier JR; WY-MEIER-CURT", minted=False)
person("WY-BALOW-JILLIAN", "Jillian Balow", "Jillian", "Balow", minted=False)
person("WY-HILL-CINDY", "Cindy Hill", "Cindy", "Hill", minted=False)
person("WY-SCHROEDER-BRIAN", "Brian Schroeder", "Brian", "Schroeder", minted=False)
person("WY-DEGENFELDER-MEGAN", "Megan Degenfelder", "Megan", "Degenfelder", minted=False)
person("WY-HARSHMAN-STEVE", "Steve Harshman", "Steve", "Harshman", minted=False)
person("WY-DRISKILL-OGDEN", "Ogden Driskill", "Ogden", "Driskill", minted=False)
person("WY-STEINMETZ-CHERI", "Cheri Steinmetz", "Cheri", "Steinmetz", aliases="Cheri E. Steinmetz", minted=False)
person("WY-LINDHOLM-TYLER", "Tyler Lindholm", "Tyler", "Lindholm", minted=False)
person("WY-HUNT-HANS", "Hans Hunt", "Hans", "Hunt", minted=False)
person("WY-NEIMAN-CHIP", "Chip Neiman", "Chip", "Neiman", minted=False)
person("WY-WILLIAMS-JD", "JD Williams", "JD", "Williams", minted=False)
person("WY-SLAGLE-ALLEN", "Allen Slagle", "Allen", "Slagle", aliases="Allen E. Slagle; Allen Earl Slagle", minted=False)
person("WY-CLAYCOMB-TROY", "Troy Claycomb", "Troy", "Claycomb", minted=False)
person("WY-TODD-NATHAN", "Nathan Todd", "Nathan", "Todd", minted=False)
person("WY-ERTMAN-MARTY", "Marty Ertman", "Marty", "Ertman", minted=False)
person("WY-WAGONER-ED", "Ed Wagoner", "Ed", "Wagoner", minted=False)
person("WY-BORTON-GARRETT", "Garrett Borton", "Garrett", "Borton", minted=False)
person("WY-HUBER-VERA", "Vera Huber", "Vera", "Huber", minted=False)
person("WY-LAMBERT-BILL", "Bill Lambert", "Bill", "Lambert", minted=False)
person("WY-TAYLOR-DON", "Don Taylor", "Don", "Taylor", minted=False)
person("WY-COLVARD-BRYAN", "Bryan E. Colvard", "Bryan", "Colvard", middle="E.", aliases="Bryan Colvard", minted=False)
person("WY-OVERMAN-SUSAN", "Susan Overman", "Susan", "Overman", minted=False)
person("WY-HADLOCK-BECKY", "Becky Hadlock", "Becky", "Hadlock", minted=False)
person("WY-TOOMAN-MIKE", "Mike Tooman", "Mike", "Tooman", aliases="James Michael Tooman; Michael Tooman", minted=False, slug="mike-tooman")
person("WY-PRELLGREEN-AMBER", "Amber Prell-Green", "Amber", "Prell-Green", aliases="Amber Green", minted=False, slug="amber-green")
person("WY-LENARDSON-KARA", "Kara Lenardson", "Kara", "Lenardson", minted=False)
person("WY-STULKEN-MICHAEL", "Michael Stulken", "Michael", "Stulken", aliases="Michael W. Stulken", minted=False)
person("WY-BEACHLER-SCOTT", "Scott E. Beachler", "Scott", "Beachler", middle="E.", minted=False)
person("WY-COTE-TINA", "Tina Cote", "Tina", "Cote", minted=False)
person("WY-KAISER-RIKI", "Riki Kaiser", "Riki", "Kaiser", minted=False)
person("WY-OWENS-TYREL", "Tyrel Owens", "Tyrel", "Owens", minted=False)
person("WY-GUALTIERI-PAM", "Pam Gualtieri", "Pam", "Gualtieri", minted=False)
person("WY-STEVESON-DON", "Don Steveson", "Don", "Steveson", aliases="Donald Steveson; Donnie Steveson; DONALD R. STEVESON; DONNIE STEVESON", minted=False)
person("WY-MCCOLLEY-ANN", "Ann McColley", "Ann", "McColley", minted=False)
person("WY-DOWNS-DAREN", "Daren Downs", "Daren", "Downs", middle="L.", aliases="Daren L. Downs", minted=False)
person("WY-KENNEY-CHRIS", "Chris Kenney", "Chris", "Kenney", minted=False)
person("WY-VOSS-THOMAS", "Thomas Voss", "Thomas", "Voss", aliases="Thomas A. Voss; Tom Voss", minted=False)
person("WY-BUTTS-JOHN", "John G. Butts", "John", "Butts", middle="G.", minted=False)
person("WY-LACEY-KARL", "Karl Lacey", "Karl", "Lacey", minted=False)
person("WY-TRANDAHL-NICK", "Nick Trandahl", "Nick", "Trandahl", aliases="Nicholas Trandahl", minted=False)
person("WY-NORMAN-JUSTIN", "Justin Norman", "Justin", "Norman", minted=False)
person("WY-WATT-JOE", "Joe Watt", "Joe", "Watt", minted=False)
person("WY-MCMILLAN-TIFFANY", "Tiffany McMillan", "Tiffany", "McMillan", minted=False)
person("WY-ROTHLEUTNER-RICK", "Rick Rothleutner", "Rick", "Rothleutner", minted=False)
person("WY-KENNEDY-TY", "Ty Kennedy", "Ty", "Kennedy", minted=False)
person("WY-VOELKER-WYATT", "Wyatt Voelker", "Wyatt", "Voelker", minted=False)
person("WY-WOZNEY-KELLY", "Kelly Wozney", "Kelly", "Wozney", minted=False)
person("WY-SCHILLER-NEIL", "Neil Schiller", "Neil", "Schiller", minted=False)
person("WY-GORDON-DANA", "Dana Gordon", "Dana", "Gordon", minted=False)
person("WY-JENKINS-JASON", "Jason Jenkins", "Jason", "Jenkins", minted=False)
person("WY-LAMBERT-MARCIA", "Marcia Lambert", "Marcia", "Lambert", minted=False)
person("WY-MANN-TAVEGIA-DANA", "Dana Mann-Tavegia", "Dana", "Mann-Tavegia", minted=False)
person("WY-FITZWATER-BILLY", "Billy Fitzwater", "Billy", "Fitzwater", minted=False)
person("WY-MILLS-TYLER", "Tyler Mills", "Tyler", "Mills", aliases="Tyler J. Mills", minted=False)
person("WY-PILLEN-SUSAN", "Susan Pillen", "Susan", "Pillen", minted=False)
person("WY-BAU-PAUL", "Paul Bau", "Paul", "Bau", minted=False)
person("WY-CRABTREE-SEAN", "Sean Crabtree", "Sean", "Crabtree", minted=False)
person("WY-PRELL-JOE", "Joe Prell", "Joe", "Prell", aliases="Richard Joe Prell", minted=False)
person("WY-JOHNSON-SCOTT", "Scott W. Johnson", "Scott", "Johnson", middle="W.", minted=False)
person("WY-RANKIN-CURTIS", "Curtis Rankin", "Curtis", "Rankin", minted=False)
person("WY-WHITE-DIANA", "Diana White", "Diana", "White", minted=False)
person("WY-MILLER-TY", "Ty Miller", "Ty", "Miller", minted=False)
person("WY-MITCHELL-MARK", "Mark Mitchell", "Mark", "Mitchell", minted=False)
person("WY-MILLS-JUSTIN", "Justin Mills", "Justin", "Mills", aliases="Justin D. Mills", minted=False)
person("WY-HILL-BRIDGET", "Bridget Hill", "Bridget", "Hill", minted=False)
person("WY-JAROSH-ROBERT", "Robert C. Jarosh", "Robert", "Jarosh", middle="C.", minted=False)
person("WY-BURNINGHAM-BEN", "Benjamin M. Burningham", "Benjamin", "Burningham", middle="M.", aliases="Ben Burningham", minted=False)
person("WY-MCGRADY-MICHAEL", "Michael J. McGrady", "Michael", "McGrady", middle="J.", minted=False)
person("WY-STEWARD-GREG", "Greg R. Steward", "Greg", "Steward", middle="R.", minted=False)
person("WY-BUSH-LYNDA", "Lynda R. Bush", "Lynda", "Bush", middle="R.", minted=False)
person("WY-KRINGLIE-KEVIN", "Kevin S. Kringlie", "Kevin", "Kringlie", middle="S.", minted=True)  # may already be in additions
person("WY-GALE-STEVEN", "Steven Gale", "Steven", "Gale", minted=True)
person("WY-COWGER-JACKIE", "Jackie Cowger", "Jackie", "Cowger", minted=True)
person("WY-HALL-JEFFREY", "Jeffrey Hall", "Jeffrey", "Hall", minted=True)
person("WY-JOHNSON-TOM-WESTON", "Tom Johnson", "Tom", "Johnson", minted=True)
person("WY-BARBER-RYAN", "Ryan Barber", "Ryan", "Barber", minted=True)

# Minted historical people
person("WY-LUMMIS-CYNTHIA", "Cynthia Lummis", "Cynthia", "Lummis", aliases="Cynthia M. Lummis", minted=True)
person("WY-ENZI-MIKE", "Mike Enzi", "Mike", "Enzi", minted=True)
person("WY-SEMLEK-MARK", "Mark A. Semlek", "Mark", "Semlek", middle="A.", minted=True)
person("WY-HUNT-TRACY", "Tracy Hunt", "Tracy", "Hunt", minted=True)
person("WY-ROSSMAN-RANDY", "Randy Rossman", "Randy", "Rossman", minted=True)
person("WY-BARTON-TONY", "Tony Barton", "Tony", "Barton", aliases="Anthony Barton (ballot: TONY BARTON). Not Washakie County Attorney Anthony Barton (WY-BARTON-ANTHONY).", minted=True)
person("WY-CRABTREE-CYNTHIA", "Cynthia Crabtree", "Cynthia", "Crabtree", minted=True)
person("WY-CURLEY-WILLIAM", "William Curley", "William", "Curley", minted=True)
person("WY-BERGER-ALEX", "Alex Berger", "Alex", "Berger", minted=True)
person("WY-KREGEL-CHERYL", "Cheryl Ann Kregel", "Cheryl", "Kregel", middle="Ann", minted=True)
person("WY-KRANK-MAMIE", "Mamie C. Krank", "Mamie", "Krank", middle="C.", minted=True)
person("WY-CONKLIN-TINA", "Tina E. Conklin", "Tina", "Conklin", middle="E.", aliases="Tina Conklin", minted=True)
person("WY-MACKE-GIDGET", "Gidget Macke", "Gidget", "Macke", minted=True)
person("WY-JAMES-GREGORY", "Gregory H. James", "Gregory", "James", middle="H.", minted=True)
person("WY-SCHLUP-ELIJAH", "Elijah L. Schlup", "Elijah", "Schlup", middle="L.", minted=True)
person("WY-CARTER-IVA-LEA", "Iva Lea Carter", "Iva Lea", "Carter", minted=True, slug="iva-lea-carter")
person("WY-HESPE-ROGER", "Roger K. Hespe", "Roger", "Hespe", middle="K.", minted=True)
person("WY-QUIGLEY-TODD", "Todd Quigley", "Todd", "Quigley", aliases="Jodd Quigley (2012 OCR of first name was JODD; 2016 official ballot is TODD QUIGLEY)", minted=True)
person("WY-MCCOLLEY-PIANA-DEBRA", "Debra McColley-Piana", "Debra", "McColley-Piana", minted=True, slug="debra-mccolley-piana")
person("WY-ALEXANDER-MICHAEL", "Michael Alexander", "Michael", "Alexander", minted=True)
person("WY-MOLLER-LYNN", "Lynn Moller", "Lynn", "Moller", minted=True)
person("WY-WATSON-LEANNE", "Leanne Watson", "Leanne", "Watson", minted=True)
person("WY-SWEET-KARA", "Kara Sweet", "Kara", "Sweet", minted=True)
person("WY-QUALHEIM-LYRA", "Lyra Qualheim", "Lyra", "Qualheim", minted=True)
person("WY-HUNT-LINDA", "Linda Hunt", "Linda", "Hunt", minted=True)
person("WY-LADWIG-STEVEN", "Steven R. Ladwig", "Steven", "Ladwig", middle="R.", minted=True)
person("WY-MURRAY-SCOTTIE", "Scottie L. Murray", "Scottie", "Murray", middle="L.", aliases="Scottie Murray", minted=True)
person("WY-UPTON-DUSTIN", "Dustin Upton", "Dustin", "Upton", minted=True)
person("WY-KOSOLA-RON", "Ron Kosola", "Ron", "Kosola", minted=True)
person("WY-BECK-TRAVIS", "Travis Beck", "Travis", "Beck", minted=True)
person("WY-STIRMEL-DENNIS", "Dennis Stirmel", "Dennis", "Stirmel", minted=True)
person("WY-WATT-DAVID", "David Watt", "David", "Watt", minted=True)
person("WY-HICKS-JENIFER", "Jenifer Hicks", "Jenifer", "Hicks", minted=True)
person("WY-GRAY-RUSSELL", "Russell Gray", "Russell", "Gray", minted=True)
person("WY-CLAYCOMB-DICK", "Dick Claycomb", "Dick", "Claycomb", minted=True)
person("WY-HARGRAVE-JEFFREY", "Jeffrey Hargrave", "Jeffrey", "Hargrave", minted=True)
person("WY-WILLIS-ROBERT", "Robert Willis", "Robert", "Willis", minted=True)
person("WY-HAYNES-DELANE", "Delane Haynes", "Delane", "Haynes", minted=True)
person("WY-ROMINE-DONALD", "Donald Romine", "Donald", "Romine", minted=True)
person("WY-TACY-LEVI", "Levi Tacy", "Levi", "Tacy", minted=True)
person("WY-CHICK-TINA", "Tina Chick", "Tina", "Chick", minted=True)
person("WY-MILLS-RONALD", "Ronald L. Mills", "Ronald", "Mills", middle="L.", aliases="Ron Mills", minted=True)
person("WY-RIESLAND-JOHN", "John Riesland", "John", "Riesland", minted=True)
person("WY-WRIGHT-TOM", "Tom Wright", "Tom", "Wright", minted=True)
person("WY-BONNAR-BOB", "Bob Bonnar", "Bob", "Bonnar", minted=True)
person("WY-LEWIS-JIMMY", "James \"Jimmy\" Lewis", "James", "Lewis", aliases="Jimmy Lewis", minted=True, slug="jimmy-lewis")
person("WY-JOHNSON-DEAN", "Robert \"Dean\" Johnson", "Robert", "Johnson", aliases="Dean Johnson", minted=True, slug="dean-johnson")
person("WY-CORLEY-JOE", "Joe Corley", "Joe", "Corley", minted=True)
person("WY-STALDER-MELISSA", "Melissa Stalder", "Melissa", "Stalder", minted=True)
person("WY-HELWIG-DEBRA", "Debra Helwig", "Debra", "Helwig", minted=True)
person("WY-UPTON-BRENDA", "Brenda Upton", "Brenda", "Upton", minted=True)
person("WY-GAUGHENBAUGH-WOODROW", "Woodrow Gaughenbaugh", "Woodrow", "Gaughenbaugh", aliases="Woody Gaughenbaugh", minted=True)
person("WY-OLSON-LORI", "Lori Olson", "Lori", "Olson", minted=True)
person("WY-KNAPP-GENE", "Gene H. Knapp", "Gene", "Knapp", middle="H.", minted=True)
person("WY-HAMPTON-RILEY", "Riley Hampton", "Riley", "Hampton", minted=True)
person("WY-KENNEDY-DONNA", "Donna Kennedy", "Donna", "Kennedy", minted=True)
person("WY-BLUMENTHAL-RACHEL", "Rachel Blumenthal", "Rachel", "Blumenthal", minted=True)
person("WY-DOWDING-SHARLA", "Sharla Dowding", "Sharla", "Dowding", minted=True)
person("WY-KEELER-KASEY", "Kasey Keeler", "Kasey", "Keeler", minted=True)
person("WY-PISCHKE-BRIAN", "Brian Pischke", "Brian", "Pischke", minted=True)
person("WY-GORMAN-MATTHEW", "Matthew Gorman", "Matthew", "Gorman", minted=True)
person("WY-HAGGE-REGG", "Regg Hagge", "Regg", "Hagge", minted=True)
person("WY-MATERI-GEORGENNA", "Georgenna Materi", "Georgenna", "Materi", minted=True)
person("WY-VIRCHOW-JEFF", "Jeff Virchow", "Jeff", "Virchow", minted=True)
person("WY-RHOADES-CINDY", "Cindy A. Rhoades", "Cindy", "Rhoades", middle="A.", minted=True)
person("WY-MILLS-MICHAEL-M", "Michael M. Mills", "Michael", "Mills", middle="M.", minted=True, slug="michael-m-mills")
person("WY-MORRIS-BILL", "Bill A. Morris", "Bill", "Morris", middle="A.", minted=True)
# Judicial (do not reuse colliding IDs)
person("WY-PERRY-JOHN-R", "John R. Perry", "John", "Perry", middle="R.", aliases="John Perry. Distinct from Natrona precinct committeeman WY-PERRY-JOHN.", minted=True, slug="john-r-perry")
person("WY-RUMPKE-THOMAS", "Thomas W. Rumpke", "Thomas", "Rumpke", middle="W.", minted=True)
person("WY-DEEGAN-NICK", "Michael N. \"Nick\" Deegan", "Michael", "Deegan", middle="N.", aliases="Nick Deegan; Michael N. Deegan", minted=True, slug="nick-deegan")
person("WY-PHILLIPS-PAUL", "Paul S. Phillips", "Paul", "Phillips", middle="S.", minted=True)
person("WY-BARTLETT-WENDY", "Wendy M. Bartlett", "Wendy", "Bartlett", middle="M.", minted=True)
person("WY-CASTANO-MATTHEW", "Matthew F.G. Castano", "Matthew", "Castano", middle="F.G.", minted=True)
person("WY-SHEEHAN-STANLEY", "Stanley S. Sheehan", "Stanley", "Sheehan", middle="S.", minted=True)
person("WY-HEALY-JOHN", "John C. Healy III", "John", "Healy", middle="C.", aliases="Healy III", minted=True)
person("WY-FOX-CATHERINE", "Catherine M. Fox", "Catherine", "Fox", middle="M.", aliases="Kate M. Fox", minted=True)
person("WY-FENN-JOHN", "John G. Fenn", "John", "Fenn", middle="G.", minted=True)
person("WY-CAUSEY-JAMES-M", "James Michael Causey", "James", "Causey", middle="Michael", aliases="James Michael Causey. Distinct from Park County WY-CAUSEY-JAMES (James L. Causey).", minted=True, slug="james-michael-causey")
person("WY-HILL-WILLIAM", "William U. Hill", "William", "Hill", middle="U.", minted=True)
person("WY-KAUTZ-KEITH", "Keith G. Kautz", "Keith", "Kautz", middle="G.", minted=True)
person("WY-BURKE-JAMES", "E. James Burke", "E. James", "Burke", minted=True, slug="e-james-burke")
person("WY-DAVIS-MICHAEL-K", "Michael K. Davis", "Michael", "Davis", middle="K.", aliases="Distinct from WY-DAVIS-MICHAEL (Michael B. Davis).", minted=True, slug="michael-k-davis")
person("WY-BOOMGAARDEN-LYNNE", "Lynne Boomgaarden", "Lynne", "Boomgaarden", minted=True)
person("WY-GRAY-KARI", "Kari Jo Gray", "Kari Jo", "Gray", minted=True, slug="kari-jo-gray")
# Last-name-only on the 2012 official summary; first names not taken from that source
person("WY-DOLLISON", "Judge Dollison", "Judge", "Dollison", aliases="Circuit Court Judge Dollison. First name not printed on the Weston official 2012 general summary.", minted=True, slug="judge-dollison")
person("WY-THARP", "Judge Tharp", "Judge", "Tharp", aliases="Circuit Court Judge Tharp. First name not printed on the Weston official 2012 general summary.", minted=True, slug="judge-tharp")

TERMS: list[dict] = []

def term(**kw):
    start = kw["term_start"]
    end = kw["term_end"]
    sy = int(start[:4])
    # If term starts after first Monday of start year, first snapshot is next January
    # (e.g. May 2018 special-district elects still appear in January 2019).
    fm_start = FM.get(sy, start)
    first_snap = sy if start <= f"{sy}-01-31" or start <= fm_start else sy + 1
    ey = int(end[:4])
    fm_end = FM.get(ey, end)
    # last snapshot year is ey if still in office on first Monday of ey
    last_snap = ey if end > fm_end else ey - 1
    if last_snap < first_snap:
        # very short mid-year stint that does not include a first Monday in January
        first_snap, last_snap = None, None
    rec = {
        "person_id": kw["person_id"],
        "name": PEOPLE[kw["person_id"]]["display_name"] if kw["person_id"] in PEOPLE else kw.get("name", ""),
        "ballot_name": kw.get("ballot_name", ""),
        "party": kw.get("party", ""),
        "office_group": kw["office_group"],
        "office": kw["office"],
        "jurisdiction": kw.get("jurisdiction", "Weston County"),
        "role": kw.get("role", ""),
        "term_start": start,
        "term_end": end,
        "start_year": first_snap,
        "end_year": last_snap,
        "how_took_office": kw.get("how_took_office", "elected"),
        "election_year": kw.get("election_year"),
        "confidence": kw.get("confidence", "high"),
        "sources": kw.get("sources") or [],
        "notes": kw.get("notes", ""),
        "flags": kw.get("flags") or [],
        "href": kw.get("href", ""),
        "retention": kw.get("retention"),
    }
    TERMS.append(rec)
    return rec

print("helpers and people loaded", len(PEOPLE))

# ---------- Federal ----------
# U.S. Senate: Barrasso continuous (2012, 2018, 2024); Enzi through Jan 3, 2021; Lummis from Jan 3, 2021 (Hageman elect Jan 2027 is on the live file, not a 2015-2026 snapshot holder except as succeeding — omit from snapshots before 2027)
term(person_id="WY-BARRASSO-JOHN", office_group="federal", office="U.S. Senator",
     jurisdiction="Wyoming", party="R", term_start=JAN3[2013], term_end=JAN3[2019],
     election_year=2012, sources=srcs("sos"), href="officials/barrasso.html")
term(person_id="WY-BARRASSO-JOHN", office_group="federal", office="U.S. Senator",
     jurisdiction="Wyoming", party="R", term_start=JAN3[2019], term_end=JAN3[2025],
     election_year=2018, sources=srcs("sos"), href="officials/barrasso.html")
term(person_id="WY-BARRASSO-JOHN", office_group="federal", office="U.S. Senator",
     jurisdiction="Wyoming", party="R", term_start=JAN3[2025], term_end=JAN3[2031],
     election_year=2024, sources=srcs("sos"), href="officials/barrasso.html")
term(person_id="WY-ENZI-MIKE", office_group="federal", office="U.S. Senator",
     jurisdiction="Wyoming", party="R", term_start=JAN3[2015], term_end=JAN3[2021],
     election_year=2014, sources=srcs("sos"), notes="Did not run in 2020. Cynthia Lummis took office January 3, 2021.")
term(person_id="WY-LUMMIS-CYNTHIA", office_group="federal", office="U.S. Senator",
     jurisdiction="Wyoming", party="R", term_start=JAN3[2021], term_end=JAN3[2027],
     election_year=2020, sources=srcs("sos"), href="officials/lummis.html")

# U.S. House
term(person_id="WY-LUMMIS-CYNTHIA", office_group="federal", office="U.S. Representative",
     jurisdiction="Wyoming", party="R", term_start=JAN3[2013], term_end=JAN3[2015],
     election_year=2012, sources=srcs("sos"))
term(person_id="WY-LUMMIS-CYNTHIA", office_group="federal", office="U.S. Representative",
     jurisdiction="Wyoming", party="R", term_start=JAN3[2015], term_end=JAN3[2017],
     election_year=2014, sources=srcs("sos"), notes="Did not run in 2016.")
term(person_id="WY-CHENEY-ELIZABETH", office_group="federal", office="U.S. Representative",
     jurisdiction="Wyoming", party="R", term_start=JAN3[2017], term_end=JAN3[2019],
     election_year=2016, sources=srcs("sos"))
term(person_id="WY-CHENEY-ELIZABETH", office_group="federal", office="U.S. Representative",
     jurisdiction="Wyoming", party="R", term_start=JAN3[2019], term_end=JAN3[2021],
     election_year=2018, sources=srcs("sos"))
term(person_id="WY-CHENEY-ELIZABETH", office_group="federal", office="U.S. Representative",
     jurisdiction="Wyoming", party="R", term_start=JAN3[2021], term_end=JAN3[2023],
     election_year=2020, sources=srcs("sos"))
term(person_id="WY-HAGEMAN-HARRIET", office_group="federal", office="U.S. Representative",
     jurisdiction="Wyoming", party="R", term_start=JAN3[2023], term_end=JAN3[2025],
     election_year=2022, sources=srcs("sos"), href="officials/hageman.html")
term(person_id="WY-HAGEMAN-HARRIET", office_group="federal", office="U.S. Representative",
     jurisdiction="Wyoming", party="R", term_start=JAN3[2025], term_end=JAN3[2027],
     election_year=2024, sources=srcs("sos"), href="officials/hageman.html")

# ---------- Statewide (from official SOS rosters in the WyoVote statewide file) ----------
term(person_id="WY-MEAD-MATT", office_group="statewide", office="Governor", jurisdiction="Wyoming", party="R",
     term_start="2011-01-03", term_end="2015-01-05", election_year=2010, sources=srcs("sw"))
term(person_id="WY-MEAD-MATT", office_group="statewide", office="Governor", jurisdiction="Wyoming", party="R",
     term_start="2015-01-05", term_end="2019-01-07", election_year=2014, sources=srcs("sw"))
term(person_id="WY-GORDON-MARK", office_group="statewide", office="Governor", jurisdiction="Wyoming", party="R",
     term_start="2019-01-07", term_end="2023-01-02", election_year=2018, sources=srcs("sw"), href="officials/gordon.html")
term(person_id="WY-GORDON-MARK", office_group="statewide", office="Governor", jurisdiction="Wyoming", party="R",
     term_start="2023-01-02", term_end="2027-01-04", election_year=2022, sources=srcs("sw"), href="officials/gordon.html")

term(person_id="WY-MURRAY-EDWARD", office_group="statewide", office="Secretary of State", jurisdiction="Wyoming", party="R",
     term_start="2015-01-05", term_end="2018-02-09", election_year=2014, sources=srcs("sw"),
     notes="Resigned February 9, 2018 (official State Officers Roster).")
term(person_id="WY-WHEELER-KAREN", office_group="statewide", office="Secretary of State", jurisdiction="Wyoming", party="R",
     term_start="2018-02-10", term_end="2018-03-05", how_took_office="acting", sources=srcs("sw"),
     notes="Acting Secretary of State. Does not appear in a January snapshot.")
term(person_id="WY-BUCHANAN-EDWARD", office_group="statewide", office="Secretary of State", jurisdiction="Wyoming", party="R",
     term_start="2018-03-05", term_end="2019-01-07", how_took_office="appointed", sources=srcs("sw"),
     notes="Appointed March 5, 2018. Then elected to a full term.")
term(person_id="WY-BUCHANAN-EDWARD", office_group="statewide", office="Secretary of State", jurisdiction="Wyoming", party="R",
     term_start="2019-01-07", term_end="2022-09-15", election_year=2018, sources=srcs("sw"),
     notes="Resigned September 15, 2022 (official State Officers Roster).")
term(person_id="WY-ALLRED-KARL", office_group="statewide", office="Secretary of State", jurisdiction="Wyoming", party="R",
     term_start="2022-10-03", term_end="2023-01-02", how_took_office="appointed", sources=srcs("sw"))
term(person_id="WY-GRAY-CHUCK", office_group="statewide", office="Secretary of State", jurisdiction="Wyoming", party="R",
     term_start="2023-01-02", term_end="2027-01-04", election_year=2022, sources=srcs("sw"), href="officials/gray.html")

# Need Maxfield for January 2015 (term ends Jan 5, 2015, so last snapshot is 2014). January 2015 is Murray.
person("WY-MAXFIELD-MAX", "Max Maxfield", "Max", "Maxfield", minted=True)
term(person_id="WY-MAXFIELD-MAX", office_group="statewide", office="Secretary of State", jurisdiction="Wyoming", party="R",
     term_start="2011-01-03", term_end="2015-01-05", election_year=2010, sources=srcs("sw"))

term(person_id="WY-CLOUD-CYNTHIA", office_group="statewide", office="State Auditor", jurisdiction="Wyoming", party="R",
     term_start="2011-01-03", term_end="2015-01-05", election_year=2010, sources=srcs("sw"))
term(person_id="WY-CLOUD-CYNTHIA", office_group="statewide", office="State Auditor", jurisdiction="Wyoming", party="R",
     term_start="2015-01-05", term_end="2019-01-07", election_year=2014, sources=srcs("sw"))
term(person_id="WY-RACINES-KRISTI", office_group="statewide", office="State Auditor", jurisdiction="Wyoming", party="R",
     term_start="2019-01-07", term_end="2023-01-02", election_year=2018, sources=srcs("sw"), href="officials/racines.html")
term(person_id="WY-RACINES-KRISTI", office_group="statewide", office="State Auditor", jurisdiction="Wyoming", party="R",
     term_start="2023-01-02", term_end="2027-01-04", election_year=2022, sources=srcs("sw"), href="officials/racines.html")

# Treasurer: Gordon held the office into January 2015 (appointed 2012, elected 2014)
term(person_id="WY-GORDON-MARK", office_group="statewide", office="State Treasurer", jurisdiction="Wyoming", party="R",
     term_start="2012-11-01", term_end="2015-01-05", how_took_office="appointed", sources=srcs("sw"),
     notes="Appointed after Joseph Meyer died. Elected 2014 to a full term.")
term(person_id="WY-GORDON-MARK", office_group="statewide", office="State Treasurer", jurisdiction="Wyoming", party="R",
     term_start="2015-01-05", term_end="2019-01-07", election_year=2014, sources=srcs("sw"))
term(person_id="WY-MEIER-CURTIS", office_group="statewide", office="State Treasurer", jurisdiction="Wyoming", party="R",
     term_start="2019-01-07", term_end="2023-01-02", election_year=2018, sources=srcs("sw"), href="officials/meier.html")
term(person_id="WY-MEIER-CURTIS", office_group="statewide", office="State Treasurer", jurisdiction="Wyoming", party="R",
     term_start="2023-01-02", term_end="2027-01-04", election_year=2022, sources=srcs("sw"), href="officials/meier.html")

term(person_id="WY-HILL-CINDY", office_group="statewide", office="Superintendent of Public Instruction", jurisdiction="Wyoming", party="R",
     term_start="2011-01-03", term_end="2015-01-05", election_year=2010, sources=srcs("sw"))
term(person_id="WY-BALOW-JILLIAN", office_group="statewide", office="Superintendent of Public Instruction", jurisdiction="Wyoming", party="R",
     term_start="2015-01-05", term_end="2019-01-07", election_year=2014, sources=srcs("sw"))
term(person_id="WY-BALOW-JILLIAN", office_group="statewide", office="Superintendent of Public Instruction", jurisdiction="Wyoming", party="R",
     term_start="2019-01-07", term_end="2022-01-16", election_year=2018, sources=srcs("sw"),
     notes="Resigned January 16, 2022.")
term(person_id="WY-SCHROEDER-BRIAN", office_group="statewide", office="Superintendent of Public Instruction", jurisdiction="Wyoming", party="R",
     term_start="2022-01-22", term_end="2023-01-02", how_took_office="appointed", sources=srcs("sw"))
term(person_id="WY-DEGENFELDER-MEGAN", office_group="statewide", office="Superintendent of Public Instruction", jurisdiction="Wyoming", party="R",
     term_start="2023-01-02", term_end="2027-01-04", election_year=2022, sources=srcs("sw"), href="officials/degenfelder.html")

# ---------- Legislature (Weston districts) ----------
# S01 Ogden Driskill throughout 2015-2026 (re-elected 2014, 2018, 2022, 2026)
term(person_id="WY-DRISKILL-OGDEN", office_group="state-senate", office="Senate District 1 (S01)",
     jurisdiction="Senate District 1 (also Campbell and Crook)", party="R",
     term_start=FM[2013], term_end=FM[2017], election_year=2012, sources=srcs(src(2012), "113", "sos"), href="officials/driskill.html")
term(person_id="WY-DRISKILL-OGDEN", office_group="state-senate", office="Senate District 1 (S01)",
     jurisdiction="Senate District 1 (also Campbell and Crook)", party="R",
     term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014), "113", "sos"), href="officials/driskill.html",
     notes="Official 2014 SOS statewide Senate summary, Senate District 1: Ogden Driskill (R) Total 4,611. Official Weston share 839; official Crook share 2,035; official Campbell share 1,737.")
term(person_id="WY-DRISKILL-OGDEN", office_group="state-senate", office="Senate District 1 (S01)",
     jurisdiction="Senate District 1 (also Campbell and Crook)", party="R",
     term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018), "113", "sos"), href="officials/driskill.html",
     notes="Official 2018 SOS statewide Senate summary, Senate District 1 (left column beside Senate District 3; that district's Total is not used): Ogden Driskill (R) Total 5,557. Official Weston share 919; official Crook share 2,498; official Campbell share 2,140.")
term(person_id="WY-DRISKILL-OGDEN", office_group="state-senate", office="Senate District 1 (S01)",
     jurisdiction="Senate District 1 (also Campbell and Crook)", party="R",
     term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022), "113", "sos"), href="officials/driskill.html",
     notes="Official 2022 SOS statewide Senate summary, Senate District 1: Ogden Driskill (R) Total 4,785. Official Weston share 819; official Crook share 2,029; official Campbell share 1,937.")
term(person_id="WY-DRISKILL-OGDEN", office_group="state-senate", office="Senate District 1 (S01)",
     jurisdiction="Senate District 1 (also Campbell and Crook)", party="R",
     term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=srcs(src(2026), "113", "sos"), href="officials/driskill.html",
     notes="Official 2026 SOS statewide Senate summary, Senate District 1: Ogden Driskill (R) Total 5,107. Official Weston share 936; official Crook share 2,313; official Campbell share 1,858. Re-elected; takes office January 2027.")
# Wait: Senate is 4-year. 2012 general would be S01 if it was up in 2012. From 113 reports Driskill is in 2014-2026 continuously.
# 2014 general had State Senator SD1 Ogden Driskill - so 2014 was an S01 election year. Terms: Jan 2015-Jan 2019, Jan 2019-Jan 2023, Jan 2023-Jan 2027, Jan 2027-Jan 2031 (2026 re-elect, after our snapshot window).
# The 2012-2017 term I added may be wrong. If S01 was elected in 2014, the prior term started Jan 2011 (2010 election). January 2015 is the start of the 2014 term.
# Remove the erroneous 2013-2017 term by not including 2012 S01 if 2012 general didn't have S01.
# Checking 2012 general OCR: I don't think I saw Senate in the 2012 extract - only HD1 and HD2. Correct: no S01 in 2012.
# I'll leave the 2013-2017 term OUT - I already added it. I'll delete by not using it... I need to pop it.
# I'll fix after: filter later or mark. Easier to pop the first Driskill term if election_year==2012.

# S03: Curt Meier through 2018 session, Cheri Steinmetz from Jan 2019 (elected 2018). 2014 general had Curt Meier SD3.
term(person_id="WY-MEIER-CURTIS", office_group="state-senate", office="Senate District 3 (S03)",
     jurisdiction="Senate District 3 (also Goshen and Niobrara)", party="R",
     term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014), "113", "sos"),
     notes="Official 2014 SOS statewide Senate summary, Senate District 3: Curt Meier (R) Total 5,743. Official Weston share 1,233; official Goshen share 3,579; official Niobrara share 931. Left the Senate when sworn as State Treasurer on January 7, 2019.")
term(person_id="WY-STEINMETZ-CHERI", office_group="state-senate", office="Senate District 3 (S03)",
     jurisdiction="Senate District 3 (also Goshen and Niobrara)", party="R",
     term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018), "113", "sos"), href="officials/steinmetz.html",
     notes="Official 2018 SOS statewide Senate summary, Senate District 3 (right column beside Senate District 1; that district's Total is not used): Cheri E. Steinmetz (R) 5,721, Marci Shaver (D) 1,449. Official Weston share Steinmetz 1,273, Shaver 234; official Goshen Steinmetz 3,447, Shaver 1,086; official Niobrara Steinmetz 1,001, Shaver 129.")
term(person_id="WY-STEINMETZ-CHERI", office_group="state-senate", office="Senate District 3 (S03)",
     jurisdiction="Senate District 3 (also Goshen and Niobrara)", party="R",
     term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022), "113", "sos"), href="officials/steinmetz.html",
     notes="Official 2022 SOS statewide Senate summary, Senate District 3: Cheri Steinmetz (R) Total 6,352. Official Weston share 1,362; official Goshen share 4,017; official Niobrara share 973.")
term(person_id="WY-STEINMETZ-CHERI", office_group="state-senate", office="Senate District 3 (S03)",
     jurisdiction="Senate District 3 (also Goshen and Niobrara)", party="R",
     term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=srcs(src(2026), "113", "sos"), href="officials/steinmetz.html",
     notes="Official 2026 SOS statewide Senate summary, Senate District 3: Cheri E. Steinmetz (R) Total 5,792. Official Weston share 1,207; official Goshen share 3,777; official Niobrara share 808. Re-elected; takes office January 2027.")

# H01: Semlek in 2014 session (113 2014); Lindholm elected 2014, served 2015-2020; Neiman defeated Lindholm in 2020 primary, served 2021-2026 (Claycomb elect Jan 2027)
term(person_id="WY-SEMLEK-MARK", office_group="state-house", office="House District 1 (H01)",
     jurisdiction="House District 1 (also Crook)", party="R",
     term_start=FM[2013], term_end=FM[2015], election_year=2012, sources=srcs(src(2012), "113", "sos"),
     notes="Official 2012 SOS statewide House summary, House District 1: Mark A. Semlek (R) Total 4,455. Official Weston share 1,183; official Crook share 3,272.")
term(person_id="WY-LINDHOLM-TYLER", office_group="state-house", office="House District 1 (H01)",
     jurisdiction="House District 1 (also Crook)", party="R",
     term_start=FM[2015], term_end=FM[2017], election_year=2014, sources=srcs(src(2014), "113", "sos"), href="officials/lindholm.html",
     notes="Official 2014 SOS statewide House summary, House District 1: Tyler Lindholm (R) Total 3,173. Official Weston share 888; official Crook share 2,285.")
term(person_id="WY-LINDHOLM-TYLER", office_group="state-house", office="House District 1 (H01)",
     jurisdiction="House District 1 (also Crook)", party="R",
     term_start=FM[2017], term_end=FM[2019], election_year=2016, sources=srcs(src(2016), "113", "sos"), href="officials/lindholm.html",
     notes="Official 2016 SOS statewide House summary, House District 1 (left column beside House District 2; that district's Total is not used): Tyler Lindholm (R) Total 4,606, Randy Leinen (D) 510. Official Weston share Lindholm 1,260, Leinen 125; official Crook share Lindholm 3,346, Leinen 385.")
term(person_id="WY-LINDHOLM-TYLER", office_group="state-house", office="House District 1 (H01)",
     jurisdiction="House District 1 (also Crook)", party="R",
     term_start=FM[2019], term_end=FM[2021], election_year=2018, sources=srcs(src(2018), "113", "sos"), href="officials/lindholm.html",
     notes="Official 2018 SOS statewide House summary, House District 1 (left column beside House District 2; that district's Total is not used): Tyler Lindholm (R) Total 3,688. Official Weston share 1,014; official Crook share 2,674.")
term(person_id="WY-NEIMAN-CHIP", office_group="state-house", office="House District 1 (H01)",
     jurisdiction="House District 1 (also Crook)", party="R",
     term_start=FM[2021], term_end=FM[2023], election_year=2020, sources=srcs(src(2020), "113", "sos"), href="officials/neiman.html",
     notes="Official 2020 SOS statewide House summary, House District 1 (left column beside House District 2; that district's Total is not used): Chip Neiman (R) Total 4,706. Official Weston share 1,300; official Crook share 3,406.")
term(person_id="WY-NEIMAN-CHIP", office_group="state-house", office="House District 1 (H01)",
     jurisdiction="House District 1 (also Crook)", party="R",
     term_start=FM[2023], term_end=FM[2025], election_year=2022, sources=srcs(src(2022), "113", "sos"), href="officials/neiman.html",
     notes="Official 2022 SOS statewide House summary, House District 1: Chip Neiman (R) Total 3,876. Official Weston share 1,074; official Crook share 2,802.")
term(person_id="WY-NEIMAN-CHIP", office_group="state-house", office="House District 1 (H01)",
     jurisdiction="House District 1 (also Crook)", party="R",
     term_start=FM[2025], term_end=FM[2027], election_year=2024, sources=srcs(src(2024), "113", "sos"), href="officials/neiman.html",
     notes="Official 2024 SOS statewide House summary, House District 1: Chip Neiman (R) Total 5,096. Official Weston share 1,268; official Crook share 3,828.")
term(person_id="WY-CLAYCOMB-TROY", office_group="state-house", office="House District 1 (H01)",
     jurisdiction="House District 1 (also Crook)", party="R",
     term_start=FM[2027], term_end=FM[2029], election_year=2026, sources=srcs(src(2026), "113", "sos"),
     notes="Official 2026 SOS statewide House summary, House District 1: Troy Claycomb (R) Total 3,688. Official Weston share 987; official Crook share 2,701. Takes office January 2027.")

# H02: Hunt 2013-2021; Williams late 2021 through 2022 session; Slagle Jan 2023-Jan 2025; Williams Jan 2025-
term(person_id="WY-HUNT-HANS", office_group="state-house", office="House District 2 (H02)",
     jurisdiction="House District 2 (also Goshen and Niobrara)", party="R",
     term_start=FM[2013], term_end=FM[2015], election_year=2012, sources=srcs(src(2012), "113", "sos"), href="officials/hunt.html",
     notes="Official 2012 SOS statewide House summary, House District 2: Hans Hunt (R) Total 3,966. Official Weston share 1,839; official Goshen share 940; official Niobrara share 1,187.")
term(person_id="WY-HUNT-HANS", office_group="state-house", office="House District 2 (H02)",
     jurisdiction="House District 2 (also Goshen and Niobrara)", party="R",
     term_start=FM[2015], term_end=FM[2017], election_year=2014, sources=srcs(src(2014), "113", "sos"), href="officials/hunt.html",
     notes="Official 2014 SOS statewide House summary, House District 2: Hans Hunt (R) Total 2,985. Official Weston share 1,296; official Goshen share 718; official Niobrara share 971.")
term(person_id="WY-HUNT-HANS", office_group="state-house", office="House District 2 (H02)",
     jurisdiction="House District 2 (also Goshen and Niobrara)", party="R",
     term_start=FM[2017], term_end=FM[2019], election_year=2016, sources=srcs(src(2016), "113", "sos"), href="officials/hunt.html",
     notes="Official 2016 SOS statewide House summary, House District 2 (right column beside House District 1; that district's Total is not used): Hans Hunt (R) 3,863, Harold Eaton (D) 624. Official Weston share Hunt 1,792, Eaton 258; official Goshen Hunt 880, Eaton 262; official Niobrara Hunt 1,191, Eaton 104.")
term(person_id="WY-HUNT-HANS", office_group="state-house", office="House District 2 (H02)",
     jurisdiction="House District 2 (also Goshen and Niobrara)", party="R",
     term_start=FM[2019], term_end=FM[2021], election_year=2018, sources=srcs(src(2018), "113", "sos"), href="officials/hunt.html",
     notes="Official 2018 SOS statewide House summary, House District 2 (right column beside House District 1; that district's Total is not used): Hans Hunt (R) Total 3,261. Official Weston share 1,314; official Goshen share 846; official Niobrara share 1,101.")
term(person_id="WY-HUNT-HANS", office_group="state-house", office="House District 2 (H02)",
     jurisdiction="House District 2 (also Goshen and Niobrara)", party="R",
     term_start=FM[2021], term_end="2021-12-31", election_year=2020, sources=srcs(src(2020), "113", "sos"),
     href="officials/hunt.html", confidence="medium",
     notes="Official 2020 SOS statewide House summary, House District 2 (right column beside House District 1; that district's Total is not used): Hans Hunt (R) Total 4,121. Official Weston share 1,789; official Goshen share 1,106; official Niobrara share 1,226. Hunt is the January 2021 holder (elected 2020). The 2021 legislator vote file records 399 counted votes for Hunt and 6 for JD Williams; the 2021 113 report lists both, and the 2022 report lists only Williams. Exact resignation or appointment date is not yet collected. term_end 2021-12-31 is a placeholder so January 2022 shows Williams; it is flagged medium.")
term(person_id="WY-WILLIAMS-JD", office_group="state-house", office="House District 2 (H02)",
     jurisdiction="House District 2 (also Goshen and Niobrara)", party="R",
     term_start="2021-12-31", term_end=FM[2023], how_took_office="appointed", sources=srcs("113", "sos"),
     href="officials/williams.html", confidence="medium",
     notes="Appointed to finish Hunt's 2021-2022 term. Exact appointment date is not yet collected. See the Hunt 2021 term note.")
term(person_id="WY-SLAGLE-ALLEN", office_group="state-house", office="House District 2 (H02)",
     jurisdiction="House District 2 (also Goshen and Niobrara)", party="R",
     term_start=FM[2023], term_end=FM[2025], election_year=2022, sources=srcs(src(2022), "113", "sos"), href="officials/slagle.html",
     notes="Official 2022 SOS statewide House summary, House District 2: Allen Slagle (R) Total 2,927. Official Weston share 1,325; official Goshen share 932; official Niobrara share 670.")
term(person_id="WY-WILLIAMS-JD", office_group="state-house", office="House District 2 (H02)",
     jurisdiction="House District 2 (also Goshen and Niobrara)", party="R",
     term_start=FM[2025], term_end=FM[2027], election_year=2024, sources=srcs(src(2024), "113", "sos"), href="officials/williams.html",
     notes="Official 2024 SOS statewide House summary, House District 2: JD Williams (R) Total 3,834. Official Weston share 1,662; official Goshen share 1,125; official Niobrara share 1,047.")
term(person_id="WY-WILLIAMS-JD", office_group="state-house", office="House District 2 (H02)",
     jurisdiction="House District 2 (also Goshen and Niobrara)", party="R",
     term_start=FM[2027], term_end=FM[2029], election_year=2026, sources=srcs(src(2026), "113", "sos"), href="officials/williams.html",
     notes="Official 2026 SOS statewide House summary, House District 2: JD Williams (R) Total 2,850. Official Weston share 1,208; official Goshen share 839; official Niobrara share 803. Re-elected; takes office January 2027.")

print("terms after federal/statewide/leg", len(TERMS))

# Drop the 2012 S01 term (S01 was not on the 2012 Weston general ballot; 2014 was the election year).
TERMS[:] = [t for t in TERMS if not (t["person_id"]=="WY-DRISKILL-OGDEN" and t.get("election_year")==2012)]

# Need Driskill in January 2015 from the 2010/2014 cycle. The 2014 term starts FM[2015], so January 2015 is covered.
# But January 2015 first Monday is 2015-01-05, and term_start is FM[2015]='2015-01-05', so he is included. Good.
# If he was already serving in early January 2015 before swearing... first Monday IS the swearing. Good.

# ---------- County offices ----------
# Commissioners: 3 midterm (2014, 2018, 2022, 2026), 2 presidential (2012, 2016, 2020, 2024)
# 2012 VF2: Rossman 2371, Tracy Hunt 2213 → Jan 2013-Jan 2017
term(person_id="WY-ROSSMAN-RANDY", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2013], term_end=FM[2017], election_year=2012, sources=srcs(src(2012)),
     notes="2012 official general, Vote For 2: Randy Rossman 2,371; Tracy Hunt 2,213.")
term(person_id="WY-HUNT-TRACY", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2013], term_end=FM[2017], election_year=2012, sources=srcs(src(2012)))
# 2014 VF3: Lambert 1754, Ertman 1731, Barton 1658 → Jan 2015-Jan 2019
term(person_id="WY-LAMBERT-BILL", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)),
     notes="2014 official general, Vote For 3: Bill Lambert 1,754; Marty Ertman 1,731; Tony Barton 1,658.")
term(person_id="WY-ERTMAN-MARTY", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)))
term(person_id="WY-BARTON-TONY", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)),
     ballot_name="TONY BARTON")
# 2016 VF2: Wagoner 2322, Tracy Hunt 2136 → Jan 2017-Jan 2021
term(person_id="WY-WAGONER-ED", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2017], term_end=FM[2021], election_year=2016, sources=srcs(src(2016)),
     notes="2016 official general, Vote For 2: Ed Wagoner 2,322; Tracy Hunt 2,136.")
term(person_id="WY-HUNT-TRACY", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2017], term_end=FM[2021], election_year=2016, sources=srcs(src(2016)))
# 2018 VF3: Todd 1908, Ertman 1856, Barton 1705 → Jan 2019-Jan 2023
term(person_id="WY-TODD-NATHAN", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)),
     notes="2018 official general, Vote For 3: Nathan Todd 1,908; Marty Ertman 1,856; Tony Barton 1,705.")
term(person_id="WY-ERTMAN-MARTY", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)))
term(person_id="WY-BARTON-TONY", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)), ballot_name="TONY BARTON")
# 2020 VF2: Taylor 2267, Wagoner 2260 → Jan 2021-Jan 2025
term(person_id="WY-TAYLOR-DON", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2021], term_end=FM[2025], election_year=2020, sources=srcs(src(2020)),
     notes="2020 official general, Vote For 2: Don Taylor 2,267; Ed Wagoner 2,260.")
term(person_id="WY-WAGONER-ED", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2021], term_end=FM[2025], election_year=2020, sources=srcs(src(2020)))
# 2022 VF3: Borton 1982, Todd 1950, Huber 1849 → Jan 2023-Jan 2027
term(person_id="WY-BORTON-GARRETT", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)))
term(person_id="WY-TODD-NATHAN", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)), role="Chairman")
term(person_id="WY-HUBER-VERA", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)))
# 2024 VF2: Wagoner 2367, Ertman 2223 → Jan 2025-Jan 2029
term(person_id="WY-WAGONER-ED", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=srcs(src(2024)), role="Vice Chairman")
term(person_id="WY-ERTMAN-MARTY", office_group="county", office="County Commissioner", party="R",
     term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=srcs(src(2024)))
# 2026 VF3 re-elects Borton, Todd, Huber take office Jan 2027 (after snapshot window)

# Row offices: 2014, 2018, 2022, 2026 cycle (4 years)
# Clerk: Kregel 2015-2019; Hadlock 2019-Apr 9 2026 (resigned); Green acting Apr 14-Jun 8; Tooman (court appt) Jun 8-Jul 28; Green acting Jul 28-Jan 2027; Prell-Green elected Jan 2027
term(person_id="WY-KREGEL-CHERYL", office_group="county", office="County Clerk", party="I",
     term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)),
     notes="2014 official general: Cheryl Ann Kregel (IND) 1,362, Mamie C. Krank (REP) 932.")
term(person_id="WY-HADLOCK-BECKY", office_group="county", office="County Clerk", party="R",
     term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)))
WGU26 = "https://www.westongov.com/wp-content/uploads/2026"
M0414 = {"label": "Weston County official special minutes, April 14, 2026 (Hadlock resignation accepted; Deputy Clerk Amber Green appointed Acting County Clerk; Resolution 2026-12)", "url": WGU26 + "/04/April-14-2026-Special-Meeting-Minutes.pdf"}
M0729 = {"label": "Weston County official special minutes, July 29, 2026 (Tooman resignation effective July 28, 2026 at noon; Amber Green appointed Acting County Clerk; Resolution 2026-22)", "url": WGU26 + "/08/July-29-2026-Minutes.pdf"}
WYF0420 = {"label": "WyoFile, April 20, 2026, Judge dismisses case to remove Weston County clerk (resignation effective April 9, 2026; vacancy declared April 14, 2026)", "url": "https://wyofile.com/judge-dismisses-case-to-remove-weston-county-clerk-following-her-resignation/"}
WYF0608 = {"label": "WyoFile / News Letter Journal, June 8, 2026, Judge fills Weston County clerk vacancy", "url": "https://wyofile.com/judge-fills-weston-county-clerk-vacancy/"}
term(person_id="WY-HADLOCK-BECKY", office_group="county", office="County Clerk", party="R",
     term_start=FM[2023], term_end="2026-04-09", election_year=2022,
     sources=srcs(src(2022), WYF0420, M0414),
     notes="Resigned effective April 9, 2026 (stipulated dismissal filing reported by WyoFile; resignation letter dated April 9). Commissioners accepted it and declared the office vacant April 14, 2026.")
term(person_id="WY-PRELLGREEN-AMBER", office_group="county", office="County Clerk", party="R",
     how_took_office="acting", term_start="2026-04-14", term_end="2026-06-08",
     sources=srcs(M0414, WYF0608),
     notes="Acting County Clerk, appointed by the commissioners April 14, 2026 (official minutes). Commissioners failed to fill the vacancy May 5; served until Judge Castano's appointee took office June 8. April 9-13 the office was vacant (deputy clerk staff).")
term(person_id="WY-TOOMAN-MIKE", office_group="county", office="County Clerk", party="R",
     how_took_office="appointed", term_start="2026-06-08", term_end="2026-07-28",
     sources=srcs(WYF0608, M0729), href="candidates/2026-local/c/mike-tooman.html",
     notes="Appointed by District Court Judge Matthew F.G. Castano after the commissioners failed to fill the vacancy (order after the June 4 hearing; took office June 8, 2026). Resigned effective July 28, 2026 at noon (official July 29 minutes).")
term(person_id="WY-PRELLGREEN-AMBER", office_group="county", office="County Clerk", party="R",
     how_took_office="acting", term_start="2026-07-28", term_end=FM[2027],
     sources=srcs(M0729), href="candidates/2026-local/c/amber-prell-green.html",
     notes="Acting County Clerk from Tooman's resignation (July 28, 2026, noon). The commissioners formally appointed her at the July 29, 2026 special meeting (official minutes).")
term(person_id="WY-PRELLGREEN-AMBER", office_group="county", office="County Clerk", party="R",
     term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=srcs(src(2026)),
     ballot_name="Amber Prell-Green", href="candidates/2026-local/c/amber-prell-green.html",
     notes="Elected November 2026 (official general summary: Amber Prell-Green 1,965, 79.62%). Term begins January 2027, after the snapshot window.")

# Treasurer: Overman 2015-present (re-elected 2014, 2018, 2022, 2026)
term(person_id="WY-OVERMAN-SUSAN", office_group="county", office="County Treasurer", party="R",
     term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)))
term(person_id="WY-OVERMAN-SUSAN", office_group="county", office="County Treasurer", party="R",
     term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)))
term(person_id="WY-OVERMAN-SUSAN", office_group="county", office="County Treasurer", party="R",
     term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)))

# Assessor: Conklin 2015-2023; Lenardson 2023-2027
term(person_id="WY-CONKLIN-TINA", office_group="county", office="County Assessor", party="R",
     term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)))
term(person_id="WY-CONKLIN-TINA", office_group="county", office="County Assessor", party="R",
     term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)))
term(person_id="WY-LENARDSON-KARA", office_group="county", office="County Assessor", party="R",
     term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)))

# Sheriff: Colvard 2015-present
term(person_id="WY-COLVARD-BRYAN", office_group="county", office="County Sheriff", party="R",
     term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)))
term(person_id="WY-COLVARD-BRYAN", office_group="county", office="County Sheriff", party="R",
     term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)))
term(person_id="WY-COLVARD-BRYAN", office_group="county", office="County Sheriff", party="R",
     term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)))

# Attorney: Curley 2015-2019; Berger 2019-2023; Stulken 2023-2027
term(person_id="WY-CURLEY-WILLIAM", office_group="county", office="County Attorney", party="R",
     term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)))
term(person_id="WY-BERGER-ALEX", office_group="county", office="County Attorney", party="R",
     term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)))
term(person_id="WY-STULKEN-MICHAEL", office_group="county", office="County Attorney", party="R",
     term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)))

# Coroner: Crabtree 2015-2023; Beachler 2023-2027
term(person_id="WY-CRABTREE-CYNTHIA", office_group="county", office="County Coroner", party="R",
     term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)))
term(person_id="WY-CRABTREE-CYNTHIA", office_group="county", office="County Coroner", party="R",
     term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)))
term(person_id="WY-BEACHLER-SCOTT", office_group="county", office="County Coroner", party="R",
     term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)))

# Clerk of District Court: Macke 2015-2021 (2014 and 2018 elect); Cote unexpired 2021-2023 then 2023-2027
term(person_id="WY-MACKE-GIDGET", office_group="county", office="Clerk of District Court", party="R",
     term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)))
term(person_id="WY-MACKE-GIDGET", office_group="county", office="Clerk of District Court", party="R",
     term_start=FM[2019], term_end=FM[2021], election_year=2018, sources=srcs(src(2018), src(2020)),
     confidence="medium",
     notes="Elected 2018 to a term that would ordinarily run to January 2023. Tina Cote won a 2020 (presidential-year) contest for this midterm-cycle office, so this record ends when Cote’s 2020 term is treated as beginning, first Monday in January 2021. The official 2020 summary does not state the reason for the vacancy.")
term(person_id="WY-COTE-TINA", office_group="county", office="Clerk of District Court", party="R",
     term_start=FM[2021], term_end=FM[2023], election_year=2020, sources=srcs(src(2020)),
     confidence="medium",
     notes="2020 official general: Tina Cote 3,251. Treated as an unexpired term ending January 2023. See the Macke 2018 term note.")
term(person_id="WY-COTE-TINA", office_group="county", office="Clerk of District Court", party="R",
     term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)))

print("terms after county", len(TERMS))

# ---------- Municipal ----------
# Newcastle Mayor: 4-year, presidential cycle (2012, 2016, 2020, 2024)
term(person_id="WY-JAMES-GREGORY", office_group="municipal", office="Newcastle Mayor",
     jurisdiction="Newcastle", term_start=FM[2013], term_end=FM[2017], election_year=2012,
     sources=srcs(src(2012)), notes="2012 official general: Gregory H. James 854, Elijah L. Schlup 477.")
term(person_id="WY-MCCOLLEY-PIANA-DEBRA", office_group="municipal", office="Newcastle Mayor",
     jurisdiction="Newcastle", term_start=FM[2017], term_end=FM[2021], election_year=2016,
     sources=srcs(src(2016)), notes="2016 official general: Debra McColley-Piana 725, Donald Steveson 677.")
term(person_id="WY-GUALTIERI-PAM", office_group="municipal", office="Newcastle Mayor",
     jurisdiction="Newcastle", term_start=FM[2021], term_end=FM[2025], election_year=2020,
     sources=srcs(src(2020)), notes="2020 official general: Pam Gualtieri 823, Donald R. Steveson 550.")
term(person_id="WY-OWENS-TYREL", office_group="municipal", office="Newcastle Mayor",
     jurisdiction="Newcastle", term_start=FM[2025], term_end=FM[2029], election_year=2024,
     sources=srcs(src(2024)), href="candidates/2024-local/c/tyrel-owens.html")

# Newcastle council: typically 3 seats every 2 years, 4-year terms (6 members). Plus occasional 2-year unexpired seats.
# 2012 VF3: Quigley 752, Hespe 696, Carter 638 → Jan 2013-Jan 2017
term(person_id="WY-QUIGLEY-TODD", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2013], term_end=FM[2017], election_year=2012, sources=srcs(src(2012)),
     notes="2012 official general, Vote For 3. 2012 OCR of the first name was JODD; the 2016 official ballot is TODD QUIGLEY.")
term(person_id="WY-HESPE-ROGER", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2013], term_end=FM[2017], election_year=2012, sources=srcs(src(2012)))
term(person_id="WY-CARTER-IVA-LEA", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2013], term_end=FM[2017], election_year=2012, sources=srcs(src(2012)))
# 2014 VF3: Steveson 691, Linda Hunt 624, Ladwig 391 → Jan 2015-Jan 2019
term(person_id="WY-STEVESON-DON", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)))
term(person_id="WY-HUNT-LINDA", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)))
term(person_id="WY-LADWIG-STEVEN", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)))
# 2016 VF3: Quigley 689, Alexander 638, Hespe 611 → Jan 2017-Jan 2021
term(person_id="WY-QUIGLEY-TODD", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2017], term_end=FM[2021], election_year=2016, sources=srcs(src(2016)))
term(person_id="WY-ALEXANDER-MICHAEL", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2017], term_end=FM[2021], election_year=2016, sources=srcs(src(2016)))
term(person_id="WY-HESPE-ROGER", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2017], term_end=FM[2021], election_year=2016, sources=srcs(src(2016)))
# 2016 2-year: Kara Sweet 902 → Jan 2017-Jan 2019
term(person_id="WY-SWEET-KARA", office_group="municipal", office="Newcastle City Council, at-large (2-year)",
     jurisdiction="Newcastle", term_start=FM[2017], term_end=FM[2019], election_year=2016, sources=srcs(src(2016)),
     notes="2016 official general, 2-year seat: Kara Sweet 902, Lyra Qualheim 427.")
# 2018 VF3: McColley 581, Gualtieri 544, Steveson 502 → Jan 2019-Jan 2023
term(person_id="WY-MCCOLLEY-ANN", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)))
term(person_id="WY-GUALTIERI-PAM", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)))
term(person_id="WY-STEVESON-DON", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)))
# 2020 VF3: Downs 764, Alexander 613, Owens 609 → Jan 2021-Jan 2025
term(person_id="WY-DOWNS-DAREN", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2021], term_end=FM[2025], election_year=2020, sources=srcs(src(2020)))
term(person_id="WY-ALEXANDER-MICHAEL", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2021], term_end=FM[2025], election_year=2020, sources=srcs(src(2020)))
term(person_id="WY-OWENS-TYREL", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2021], term_end=FM[2025], election_year=2020, sources=srcs(src(2020)))
# 2022 4yr VF3: McColley 660, Steveson 487, Butts 470 → Jan 2023-Jan 2027
term(person_id="WY-MCCOLLEY-ANN", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)),
     href="candidates/2022-local/c/ann-mccolley.html")
term(person_id="WY-STEVESON-DON", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)),
     href="candidates/2026-local/c/don-steveson.html")
term(person_id="WY-BUTTS-JOHN", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)),
     href="candidates/2022-local/c/john-g-butts.html")
# 2022 2yr: write-in only, winner not named on the official summary
# 2024 VF3: Downs 681, Kenney 659, Voss 483 → Jan 2025-Jan 2029
term(person_id="WY-DOWNS-DAREN", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=srcs(src(2024)),
     href="candidates/2024-local/c/daren-downs.html")
term(person_id="WY-KENNEY-CHRIS", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=srcs(src(2024)),
     href="candidates/2024-local/c/chris-kenney.html")
term(person_id="WY-VOSS-THOMAS", office_group="municipal", office="Newcastle City Council, at-large",
     jurisdiction="Newcastle", term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=srcs(src(2024)),
     href="candidates/2024-local/c/thomas-voss.html", role="President")

# Upton Mayor: 2014, 2018, 2022, 2026 cycle
term(person_id="WY-UPTON-DUSTIN", office_group="municipal", office="Upton Mayor",
     jurisdiction="Upton", term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)),
     notes="2014 official general: Dustin Upton 190, Ron Kosola 173.")
term(person_id="WY-BECK-TRAVIS", office_group="municipal", office="Upton Mayor",
     jurisdiction="Upton", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)),
     notes="2018 official general: Travis Beck 319, Jenifer Hicks 69.")
term(person_id="WY-TRANDAHL-NICK", office_group="municipal", office="Upton Mayor",
     jurisdiction="Upton", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)),
     href="candidates/2022-local/c/nick-trandahl.html")
# Upton 2012 mayor was not on the 2012 general summary. January 2015 starts with the 2014 elect. 2013-2014 mayor is Not yet collected.

# Upton council: 2 seats every 2 years, 4-year terms (4 members)
# 2012 VF2: Mark Mitchell 259, David Watt 218 → Jan 2013-Jan 2017
term(person_id="WY-MITCHELL-MARK", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2013], term_end=FM[2017], election_year=2012, sources=srcs(src(2012)),
     notes="Mark Mitchell later served on School District #7. Same name; treated as the same person pending a contradicting official source.")
term(person_id="WY-WATT-DAVID", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2013], term_end=FM[2017], election_year=2012, sources=srcs(src(2012)))
# 2014 VF2: Travis Beck 286, Nathan Todd 249 → Jan 2015-Jan 2019
term(person_id="WY-BECK-TRAVIS", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)))
term(person_id="WY-TODD-NATHAN", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2015], term_end=FM[2019], election_year=2014, sources=srcs(src(2014)),
     notes="Nathan Todd later served as a Weston County Commissioner. Same name; treated as the same person pending a contradicting official source.")
# 2016 VF2: David Watt 284, Justin Norman 250 → Jan 2017-Jan 2021
term(person_id="WY-WATT-DAVID", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2017], term_end=FM[2021], election_year=2016, sources=srcs(src(2016)))
term(person_id="WY-NORMAN-JUSTIN", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2017], term_end=FM[2021], election_year=2016, sources=srcs(src(2016)))
# 2018 VF2: Stirmel 221, Joe Watt 221 (tie) → Jan 2019-Jan 2023
term(person_id="WY-STIRMEL-DENNIS", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)),
     notes="2018 official general, Vote For 2: Dennis Stirmel 221 and Joe Watt 221 (tie).")
term(person_id="WY-WATT-JOE", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=srcs(src(2018)))
# 2020 VF2: Norman 249, Trandahl 201 → Jan 2021-Jan 2025
term(person_id="WY-NORMAN-JUSTIN", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2021], term_end=FM[2025], election_year=2020, sources=srcs(src(2020)))
term(person_id="WY-TRANDAHL-NICK", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2021], term_end=FM[2023], election_year=2020, sources=srcs(src(2020), src(2022)),
     confidence="medium",
     notes="Elected to the town council in 2020 (term would run to January 2025) and elected Upton Mayor in 2022, taking office January 2023. Council term is ended at the mayoral swearing-in.")
# 2022 VF2: McMillan 279, Joe Watt 257 → Jan 2023-Jan 2027
term(person_id="WY-MCMILLAN-TIFFANY", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)),
     href="candidates/2022-local/c/tiffany-mcmillan.html")
term(person_id="WY-WATT-JOE", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=srcs(src(2022)),
     href="candidates/2026-local/c/joe-watt.html")
# 2024 VF2: Norman 375, Rothleutner 353 → Jan 2025-Jan 2029
term(person_id="WY-NORMAN-JUSTIN", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=srcs(src(2024)),
     href="candidates/2024-local/c/justin-norman.html",
     flags=["results_do_not_tie"],
     notes="Official 2024 summary is a scanned page. Named candidates plus write-ins were read as 743 against a printed Total Votes Cast of 745. The 2-vote difference is flagged, not forced.")
term(person_id="WY-ROTHLEUTNER-RICK", office_group="municipal", office="Upton Town Council, at-large",
     jurisdiction="Upton", term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=srcs(src(2024)),
     href="candidates/2024-local/c/rick-rothleutner.html", flags=["results_do_not_tie"])

print("terms after municipal", len(TERMS))

# ---------- Schools ----------
# SD #1: 9 seats, 5 in presidential years, 4 in midterm years, 4-year terms. Take office December after the election; included in the next January snapshot. term_start uses first Monday in January for consistency with other local offices, with a note.
# 2012 VF5: Mills 1819, Riesland 1735, Chick 1686, Bonnar 1416, Wright 1380 → Jan 2013-Jan 2017
for pid, bn in [
    ("WY-MILLS-RONALD", "RONALD L. MILLS"),
    ("WY-RIESLAND-JOHN", "JOHN RIESLAND"),
    ("WY-CHICK-TINA", "TINA CHICK"),
    ("WY-BONNAR-BOB", "BOB BONNAR"),
    ("WY-WRIGHT-TOM", "TOM WRIGHT"),
]:
    term(person_id=pid, office_group="schools", office="Weston County School District #1 Board, at-large",
         jurisdiction="Weston County School District #1", term_start=FM[2013], term_end=FM[2017],
         election_year=2012, sources=srcs(src(2012)), ballot_name=bn)
# 2014 VF4: Gordon 1339, Dean Johnson 1298, Corley 1136, Stalder 943 → Jan 2015-Jan 2019
for pid, bn in [
    ("WY-GORDON-DANA", "DANA GORDON"),
    ("WY-JOHNSON-DEAN", "ROBERT \"DEAN\" JOHNSON"),
    ("WY-CORLEY-JOE", "JOE CORLEY"),
    ("WY-STALDER-MELISSA", "MELISSA STALDER"),
]:
    term(person_id=pid, office_group="schools", office="Weston County School District #1 Board, at-large",
         jurisdiction="Weston County School District #1", term_start=FM[2015], term_end=FM[2019],
         election_year=2014, sources=srcs(src(2014)), ballot_name=bn)
# 2016 VF5: Mills 1853, Riesland 1721, Chick 1645, Wright 1448, Mann-Tavegia 1417 → Jan 2017-Jan 2021
for pid, bn in [
    ("WY-MILLS-RONALD", "RONALD L. MILLS"),
    ("WY-RIESLAND-JOHN", "JOHN RIESLAND"),
    ("WY-CHICK-TINA", "TINA CHICK"),
    ("WY-WRIGHT-TOM", "TOM WRIGHT"),
    ("WY-MANN-TAVEGIA-DANA", "DANA MANN-TAVEGIA"),
]:
    term(person_id=pid, office_group="schools", office="Weston County School District #1 Board, at-large",
         jurisdiction="Weston County School District #1", term_start=FM[2017], term_end=FM[2021],
         election_year=2016, sources=srcs(src(2016)), ballot_name=bn)
# 2016 VF1 Marcia Lambert: treated as an unexpired term ending January 2019 (she then won a full 2018 term)
term(person_id="WY-LAMBERT-MARCIA", office_group="schools", office="Weston County School District #1 Board, at-large (unexpired)",
     jurisdiction="Weston County School District #1", term_start=FM[2017], term_end=FM[2019],
     election_year=2016, sources=srcs(src(2016)), confidence="medium",
     notes="2016 official general had a separate Vote For 1 contest (Marcia Lambert 2,214). Treated as an unexpired term ending January 2019 because she then won a regular 4-year seat in 2018. The official summary does not label the seat.")
# 2018 VF4: Gordon 1149, Dean Johnson 1107, Lambert 903, Jenkins 687 → Jan 2019-Jan 2023
for pid, bn in [
    ("WY-GORDON-DANA", "DANA GORDON"),
    ("WY-JOHNSON-DEAN", "ROBERT \"DEAN\" JOHNSON"),
    ("WY-LAMBERT-MARCIA", "MARCIA LAMBERT"),
    ("WY-JENKINS-JASON", "JASON JENKINS"),
]:
    term(person_id=pid, office_group="schools", office="Weston County School District #1 Board, at-large",
         jurisdiction="Weston County School District #1", term_start=FM[2019], term_end=FM[2023],
         election_year=2018, sources=srcs(src(2018)), ballot_name=bn)
# 2020 VF5: Chick 1458, Mills 1415, Riesland 1300, Fitzwater 1294, Mann-Tavegia 1251 → Jan 2021-Jan 2025
for pid, bn in [
    ("WY-CHICK-TINA", "TINA CHICK"),
    ("WY-MILLS-RONALD", "RON MILLS"),
    ("WY-RIESLAND-JOHN", "JOHN RIESLAND"),
    ("WY-FITZWATER-BILLY", "BILLY FITZWATER"),
    ("WY-MANN-TAVEGIA-DANA", "DANA MANN-TAVEGIA"),
]:
    term(person_id=pid, office_group="schools", office="Weston County School District #1 Board, at-large",
         jurisdiction="Weston County School District #1", term_start=FM[2021], term_end=FM[2025],
         election_year=2020, sources=srcs(src(2020)), ballot_name=bn)
# 2022 VF4: Crabtree 1121, Gordon 1009, Prell 941, Jenkins 684 → Jan 2023-Jan 2027
for pid, bn in [
    ("WY-CRABTREE-SEAN", "SEAN CRABTREE"),
    ("WY-GORDON-DANA", "DANA GORDON"),
    ("WY-PRELL-JOE", "JOE PRELL"),
    ("WY-JENKINS-JASON", "JASON JENKINS"),
]:
    term(person_id=pid, office_group="schools", office="Weston County School District #1 Board, at-large",
         jurisdiction="Weston County School District #1", term_start=FM[2023], term_end=FM[2027],
         election_year=2022, sources=srcs(src(2022)), ballot_name=bn)
# 2024 VF5: Mann-Tavegia 1514, Fitzwater 1487, Tyler Mills 1459, Pillen 1354, Bau 1343 → Jan 2025-Jan 2029
for pid, bn in [
    ("WY-MANN-TAVEGIA-DANA", "DANA MANN-TAVEGIA"),
    ("WY-FITZWATER-BILLY", "BILLY FITZWATER"),
    ("WY-MILLS-TYLER", "TYLER J. MILLS"),
    ("WY-PILLEN-SUSAN", "SUSAN PILLEN"),
    ("WY-BAU-PAUL", "PAUL BAU"),
]:
    term(person_id=pid, office_group="schools", office="Weston County School District #1 Board, at-large",
         jurisdiction="Weston County School District #1", term_start=FM[2025], term_end=FM[2029],
         election_year=2024, sources=srcs(src(2024)), ballot_name=bn)

# SD #7: 5 seats, 2 presidential / 3 midterm
# 2012 VF2: Helwig 545, Brenda Upton 511 → Jan 2013-Jan 2017
term(person_id="WY-HELWIG-DEBRA", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2013], term_end=FM[2017],
     election_year=2012, sources=srcs(src(2012)))
term(person_id="WY-UPTON-BRENDA", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2013], term_end=FM[2017],
     election_year=2012, sources=srcs(src(2012)))
# 2014 VF3: Gaughenbaugh 412, Lori Olson 350, Knapp 342 → Jan 2015-Jan 2019
term(person_id="WY-GAUGHENBAUGH-WOODROW", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2015], term_end=FM[2019],
     election_year=2014, sources=srcs(src(2014)))
term(person_id="WY-OLSON-LORI", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2015], term_end=FM[2019],
     election_year=2014, sources=srcs(src(2014)))
term(person_id="WY-KNAPP-GENE", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2015], term_end=FM[2019],
     election_year=2014, sources=srcs(src(2014)))
# 2016 VF2: Rankin 450, White 365 → Jan 2017-Jan 2021
term(person_id="WY-RANKIN-CURTIS", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2017], term_end=FM[2021],
     election_year=2016, sources=srcs(src(2016)))
term(person_id="WY-WHITE-DIANA", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2017], term_end=FM[2021],
     election_year=2016, sources=srcs(src(2016)))
# 2018 VF3: Mitchell 216, Ty Miller 209, Gaughenbaugh 200 → Jan 2019-Jan 2023
term(person_id="WY-MITCHELL-MARK", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2019], term_end=FM[2023],
     election_year=2018, sources=srcs(src(2018)))
term(person_id="WY-MILLER-TY", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2019], term_end=FM[2023],
     election_year=2018, sources=srcs(src(2018)))
term(person_id="WY-GAUGHENBAUGH-WOODROW", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2019], term_end=FM[2023],
     election_year=2018, sources=srcs(src(2018)))
# 2020 VF2: White 559, Rankin 529 → Jan 2021-Jan 2025
term(person_id="WY-WHITE-DIANA", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2021], term_end=FM[2025],
     election_year=2020, sources=srcs(src(2020)))
term(person_id="WY-RANKIN-CURTIS", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2021], term_end=FM[2025],
     election_year=2020, sources=srcs(src(2020)))
# 2022 VF3: Justin Mills 475, Ty Miller 390, Mitchell 352 → Jan 2023-Jan 2027
term(person_id="WY-MILLS-JUSTIN", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2023], term_end=FM[2027],
     election_year=2022, sources=srcs(src(2022)))
term(person_id="WY-MILLER-TY", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2023], term_end=FM[2027],
     election_year=2022, sources=srcs(src(2022)))
term(person_id="WY-MITCHELL-MARK", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2023], term_end=FM[2027],
     election_year=2022, sources=srcs(src(2022)))
# 2024 VF2: White 591, Rankin 568 → Jan 2025-Jan 2029
term(person_id="WY-WHITE-DIANA", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2025], term_end=FM[2029],
     election_year=2024, sources=srcs(src(2024)))
term(person_id="WY-RANKIN-CURTIS", office_group="schools", office="Weston County School District #7 Board, at-large",
     jurisdiction="Weston County School District #7", term_start=FM[2025], term_end=FM[2029],
     election_year=2024, sources=srcs(src(2024)))

# ---------- Special districts (May 8, 2018 official canvasses only; other years not yet collected) ----------
# 4-year terms from the May 2018 canvass. Included in January 2019–January 2022 snapshots. Next election not on the November results page.
term(person_id="WY-MATERI-GEORGENNA", office_group="special-districts", office="Weston County Hospital District Trustee",
     jurisdiction="Weston County Hospital District", term_start="2018-05-09", term_end="2022-05-09",
     election_year=2018, sources=srcs(SRC_HOSP),
     notes="Official canvass minutes, May 9, 2018: Georgenna Materi and Jeff Virchow elected to 4-year terms. Vote totals on the abstract are handwritten and were not all clearly readable; winners are taken from the signed minutes.")
term(person_id="WY-VIRCHOW-JEFF", office_group="special-districts", office="Weston County Hospital District Trustee",
     jurisdiction="Weston County Hospital District", term_start="2018-05-09", term_end="2022-05-09",
     election_year=2018, sources=srcs(SRC_HOSP))
term(person_id="WY-RHOADES-CINDY", office_group="special-districts", office="Weston County Museum District Trustee",
     jurisdiction="Weston County Museum District", term_start="2018-05-10", term_end="2022-05-10",
     election_year=2018, sources=srcs(SRC_MUS),
     notes="Official canvass, May 10, 2018: Cindy A. Rhoades 168, Michael M. Mills 162, Bill A. Morris 157, each for a 4-year term.")
term(person_id="WY-MILLS-MICHAEL-M", office_group="special-districts", office="Weston County Museum District Trustee",
     jurisdiction="Weston County Museum District", term_start="2018-05-10", term_end="2022-05-10",
     election_year=2018, sources=srcs(SRC_MUS))
term(person_id="WY-MORRIS-BILL", office_group="special-districts", office="Weston County Museum District Trustee",
     jurisdiction="Weston County Museum District", term_start="2018-05-10", term_end="2022-05-10",
     election_year=2018, sources=srcs(SRC_MUS))

print("terms after schools/special", len(TERMS))

# ---------- Judicial (Weston ballot retentions; not a complete statewide bench) ----------
# Circuit judges generally appear every 4 years; district every 6 years, consistent with the Weston ballots.

def ret(year, yes=None, no=None, result="retained"):
    return {"year": year, "yes": yes, "no": no, "result": result, "source": WG[year][0]}

# Wendy Bartlett, circuit: 2012, 2016, 2020, 2024
term(person_id="WY-BARTLETT-WENDY", office_group="judicial", office="Circuit Judge, 6th Judicial District",
     jurisdiction="6th Judicial District", how_took_office="retained",
     term_start=FM[2013], term_end=FM[2029], election_year=2012,
     sources=srcs(src(2012), src(2016), src(2020), src(2024)),
     notes="Retained on the Weston official general ballot in 2012, 2016, 2020, and 2024 (4-year cycle). 2012: yes 2,317 / no 676; 2016: yes 2,295 / no 832; 2020: yes 2,512 / no 574; 2024 yes 2,282 (NO not clearly readable on the scanned official summary).",
     retention=ret(2020, 2512, 574))
# Matthew Castano, circuit: 2016, 2020, 2024
term(person_id="WY-CASTANO-MATTHEW", office_group="judicial", office="Circuit Judge, 6th Judicial District",
     jurisdiction="6th Judicial District", how_took_office="retained",
     term_start=FM[2017], term_end=FM[2029], election_year=2016,
     sources=srcs(src(2016), src(2020), src(2024)),
     notes="Retained in 2016, 2020, and 2024. 2016: yes 2,199 / no 923; 2020: yes 2,372 / no 693; 2024 yes 2,279 (NO not clearly readable).",
     retention=ret(2020, 2372, 693))
# Paul Phillips, circuit: 2018, 2022
term(person_id="WY-PHILLIPS-PAUL", office_group="judicial", office="Circuit Judge, 6th Judicial District",
     jurisdiction="6th Judicial District", how_took_office="retained",
     term_start=FM[2019], term_end=FM[2027], election_year=2018,
     sources=srcs(src(2018), src(2022)),
     notes="Retained in 2018 (yes 1,804 / no 530) and 2022 (yes 1,825 / no 629).",
     retention=ret(2022, 1825, 629))
# Lynda Bush, circuit: 2024 (Weston court page lists her as the Weston circuit judge)
term(person_id="WY-BUSH-LYNDA", office_group="judicial", office="Circuit Judge, 6th Judicial District",
     jurisdiction="Circuit Court of the 6th Judicial District, Weston County (Newcastle)",
     how_took_office="retained", term_start=FM[2025], term_end=FM[2029], election_year=2024,
     sources=srcs(src(2024), {"label": "Wyoming Judicial Branch, Weston circuit court", "url": "https://www.wyocourts.gov/court/circuit-court-of-the-6th-judicial-district-weston-county-state-of-wyoming-newcastle/"}),
     notes="Retained 2024: yes 2,175 / no 797.",
     retention=ret(2024, 2175, 797), href="officials/judges/lynda-r-bush.html")
# Greg Steward (Campbell circuit) retained 2026, on the Weston 2026 ballot
term(person_id="WY-STEWARD-GREG", office_group="judicial", office="Circuit Judge, 6th Judicial District",
     jurisdiction="Circuit Court of the 6th Judicial District, Campbell County (Gillette)",
     how_took_office="retained", term_start=FM[2027], term_end=FM[2031], election_year=2026,
     sources=srcs(src(2026)),
     notes="Retained on the Weston 2026 ballot (yes 1,493 / no 616). Term begins January 2027, after the 2015-2026 snapshot window. Listed so the record is complete.",
     retention=ret(2026, 1493, 616), href="officials/judges/greg-r-steward.html")
# Dollison and Tharp: retained 2012 only; first names not on the official summary. Include through Jan 2016 only (not on the 2016 ballot).
term(person_id="WY-DOLLISON", office_group="judicial", office="Circuit Judge, 6th Judicial District",
     jurisdiction="6th Judicial District", how_took_office="retained",
     term_start=FM[2013], term_end=FM[2017], election_year=2012, sources=srcs(src(2012)),
     confidence="medium",
     notes="Retained 2012 (yes 2,383 / no 701). First name is not printed on the official Weston 2012 general summary. Not on the 2016 Weston ballot.")
term(person_id="WY-THARP", office_group="judicial", office="Circuit Judge, 6th Judicial District",
     jurisdiction="6th Judicial District", how_took_office="retained",
     term_start=FM[2013], term_end=FM[2017], election_year=2012, sources=srcs(src(2012)),
     confidence="medium",
     notes="Retained 2012 (yes 2,211 / no 744). First name is not printed on the official Weston 2012 general summary. Not on the 2016 Weston ballot.")
# Magistrate Sheehan 2012, 2016
term(person_id="WY-SHEEHAN-STANLEY", office_group="judicial", office="Magistrate, 6th Judicial District",
     jurisdiction="6th Judicial District", how_took_office="retained",
     term_start=FM[2013], term_end=FM[2021], election_year=2012, sources=srcs(src(2012), src(2016)),
     notes="Retained 2012 (yes 2,429 / no 665) and 2016 (yes 2,445 / no 803). Not on later Weston general summaries reviewed.")
# Causey retained 2024
term(person_id="WY-CAUSEY-JAMES-M", office_group="judicial", office="Circuit Judge, 6th Judicial District",
     jurisdiction="6th Judicial District", how_took_office="retained",
     term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=srcs(src(2024)),
     notes="Retained 2024, yes 2,232 (NO not clearly readable on the scanned official summary). Distinct from Park County WY-CAUSEY-JAMES.",
     retention=ret(2024, 2232, None))

# District judges
# Deegan 2012, 2018
term(person_id="WY-DEEGAN-NICK", office_group="judicial", office="District Judge, 6th Judicial District",
     jurisdiction="6th Judicial District", how_took_office="retained",
     term_start=FM[2013], term_end=FM[2025], election_year=2012, sources=srcs(src(2012), src(2018)),
     notes="Retained 2012 (yes 2,258 / no 749) and 2018 (yes 1,823 / no 553). 6-year cycle. Not on the 2024 Weston general summary reviewed.",
     retention=ret(2018, 1823, 553))
# Rumpke 2014, 2020
term(person_id="WY-RUMPKE-THOMAS", office_group="judicial", office="District Judge, 6th Judicial District",
     jurisdiction="6th Judicial District", how_took_office="retained",
     term_start=FM[2015], term_end=FM[2027], election_year=2014, sources=srcs(src(2014), src(2020)),
     notes="Retained 2014 and 2020 (2020: yes 2,379 / no 767).",
     retention=ret(2020, 2379, 767))
# Perry 2014, 2020
term(person_id="WY-PERRY-JOHN-R", office_group="judicial", office="District Judge, 6th Judicial District",
     jurisdiction="6th Judicial District", how_took_office="retained",
     term_start=FM[2015], term_end=FM[2027], election_year=2014, sources=srcs(src(2014), src(2020)),
     notes="Retained 2014 and 2020 (2020: yes 2,423 / no 682). Distinct from Natrona precinct committeeman WY-PERRY-JOHN.",
     retention=ret(2020, 2423, 682))
# Healy III 2022
term(person_id="WY-HEALY-JOHN", office_group="judicial", office="District Judge, 6th Judicial District",
     jurisdiction="6th Judicial District", how_took_office="retained",
     term_start=FM[2023], term_end=FM[2029], election_year=2022, sources=srcs(src(2022)),
     notes="Retained 2022: yes 1,845 / no 634.",
     retention=ret(2022, 1845, 634))
# McGrady 2026 (term from Jan 2027)
term(person_id="WY-MCGRADY-MICHAEL", office_group="judicial", office="District Judge, 6th Judicial District",
     jurisdiction="6th Judicial District", how_took_office="retained",
     term_start=FM[2027], term_end=FM[2033], election_year=2026, sources=srcs(src(2026)),
     notes="Retained 2026: yes 1,478 / no 642. Term begins January 2027, after the snapshot window.",
     retention=ret(2026, 1478, 642), href="officials/judges/michael-j-mcgrady.html")

# Supreme Court: Weston retention results plus official Wyoming Judicial Branch
# appointment and retirement dates (so mid-term vacancies are not left as if the justice still served).
WYOCOURTS = "https://www.wyocourts.gov"
def wyc(label, path):
    return {"label": label, "url": WYOCOURTS + path}

term(person_id="WY-BURKE-JAMES", office_group="judicial", office="Justice of the Wyoming Supreme Court",
     jurisdiction="Wyoming", how_took_office="retained",
     term_start=FM[2015], term_end="2018-10-08", election_year=2014,
     sources=srcs(src(2014), wyc("Wyoming Judicial Branch, Justice E. James Burke retiring October 8, 2018",
                                 "/news/justice-e-james-burke-retiring-october-8-2018/")),
     notes="Retained on the Weston 2014 ballot (yes 1,582 / no 622). Official Judicial Branch announcement: retired October 8, 2018.",
     confidence="high", retention=ret(2014, 1582, 622))
term(person_id="WY-DAVIS-MICHAEL-K", office_group="judicial", office="Justice of the Wyoming Supreme Court",
     jurisdiction="Wyoming", how_took_office="retained",
     term_start=FM[2015], term_end="2022-01-16", election_year=2014,
     sources=srcs(src(2014), wyc("Wyoming Judicial Branch, Judicial Nominating Commission announces Supreme Court vacancy (Davis retirement January 16, 2022)",
                                 "/app/uploads/2025/05/News-Release-Announcing-Vacancy-Wyoming-Supreme-Court.pdf")),
     confidence="high", retention=ret(2014, 1573, 613),
     notes="Retained on the Weston 2014 ballot (yes 1,573 / no 613). Official JNC release: retired January 16, 2022. Distinct from WY-DAVIS-MICHAEL.")
term(person_id="WY-FOX-CATHERINE", office_group="judicial", office="Justice of the Wyoming Supreme Court",
     jurisdiction="Wyoming", how_took_office="retained",
     term_start=FM[2015], term_end="2025-05-27", election_year=2016,
     sources=srcs(src(2016), src(2024),
                  wyc("Wyoming Judicial Branch, Supreme Court justices", "/supreme-court/")),
     notes="Already serving at the start of the 2015 window (retained 2016 and 2024 on the Weston ballot). Official name Kate M. Fox. Official Judicial Branch: retired May 27, 2025.",
     retention=ret(2024, 2272, 733))
term(person_id="WY-HILL-WILLIAM", office_group="judicial", office="Justice of the Wyoming Supreme Court",
     jurisdiction="Wyoming", how_took_office="retained",
     term_start=FM[2015], term_end="2018-02-16", election_year=2016,
     sources=srcs(src(2016), wyc("Wyoming Judicial Branch, Justice William U. Hill retiring February 16, 2018",
                                 "/news/justice-william-u-hill-retiring-february-16-2018/")),
     notes="Already serving at the start of the 2015 window; retained 2016 (yes 2,138 / no 990). Official Judicial Branch announcement: retired February 16, 2018.")
term(person_id="WY-KAUTZ-KEITH", office_group="judicial", office="Justice of the Wyoming Supreme Court",
     jurisdiction="Wyoming", how_took_office="retained",
     term_start=FM[2017], term_end="2024-03-26", election_year=2016,
     sources=srcs(src(2016), wyc("Wyoming Judicial Branch, Supreme Court justices", "/supreme-court/")),
     notes="Retained 2016 (yes 2,116 / no 988). Official Judicial Branch: retired March 26, 2024 (successor Robert C. Jarosh sworn March 27, 2024).")
term(person_id="WY-BOOMGAARDEN-LYNNE", office_group="judicial", office="Justice of the Wyoming Supreme Court",
     jurisdiction="Wyoming", how_took_office="appointed",
     term_start="2018-02-20", term_end=FM[2029], election_year=2020,
     sources=srcs(src(2020), wyc("Wyoming Judicial Branch, Welcome Justice Lynne Boomgaarden, February 20, 2018",
                                 "/news/welcome-justice-lynne-boomgaarden/"),
                  wyc("Wyoming Judicial Branch, Supreme Court, Chief Justice Lynne Boomgaarden", "/supreme-court/")),
     notes="Official Judicial Branch: tenure began February 20, 2018, appointed by Gov. Mead to succeed William U. Hill. Retained 2020: yes 2,498 / no 654. Official term expires January 2029.",
     retention=ret(2020, 2498, 654))
term(person_id="WY-GRAY-KARI", office_group="judicial", office="Justice of the Wyoming Supreme Court",
     jurisdiction="Wyoming", how_took_office="appointed",
     term_start="2018-10-09", term_end=FM[2029], election_year=2020,
     sources=srcs(src(2020), wyc("Wyoming Judicial Branch, Welcome Justice Kari Jo Gray (tenure began October 9, 2018)",
                                 "/news/welcome-justice-kari-jo-gray/"),
                  wyc("Wyoming Judicial Branch, Supreme Court, Justice Kari Gray", "/supreme-court/")),
     notes="Official Judicial Branch: tenure began October 9, 2018, appointed by Gov. Mead to succeed E. James Burke. Retained 2020: yes 2,468 / no 649. Official term expires January 2029.",
     retention=ret(2020, 2468, 649))
term(person_id="WY-FENN-JOHN", office_group="judicial", office="Justice of the Wyoming Supreme Court",
     jurisdiction="Wyoming", how_took_office="appointed",
     term_start="2022-01-17", term_end=FM[2033], election_year=2024,
     sources=srcs(src(2024),
                  wyc("Wyoming Judicial Branch, Judicial Nominating Commission, Davis retirement January 16, 2022",
                      "/app/uploads/2025/05/News-Release-Announcing-Vacancy-Wyoming-Supreme-Court.pdf"),
                  wyc("Wyoming Judicial Branch, Justice John G. Fenn sworn in",
                      "/news/robing-ceremony-for-wyoming-supreme-court-justice-john-g-fenn/")),
     notes="Appointed by Gov. Gordon after Justice Davis retired January 16, 2022 (official JNC release). Term treated as starting January 17, 2022, the next day; the official robing announcement does not print the first day on the bench. Retained 2024, yes 2,187 (NO not clearly readable on the scanned official summary).",
     confidence="medium", retention=ret(2024, 2187, None))
term(person_id="WY-JAROSH-ROBERT", office_group="judicial", office="Justice of the Wyoming Supreme Court",
     jurisdiction="Wyoming", how_took_office="appointed",
     term_start="2024-03-27", term_end=FM[2035], election_year=2026,
     sources=srcs(src(2026), wyc("Wyoming Judicial Branch, Supreme Court, Justice Robert C. Jarosh", "/supreme-court/")),
     notes="Official Judicial Branch: sworn in March 27, 2024, succeeding Keith G. Kautz (retired March 26, 2024). Retained 2026.",
     href="officials/judges/robert-c-jarosh.html")
term(person_id="WY-HILL-BRIDGET", office_group="judicial", office="Justice of the Wyoming Supreme Court",
     jurisdiction="Wyoming", how_took_office="appointed",
     term_start="2025-05-28", term_end=FM[2035], election_year=2026,
     sources=srcs(src(2026), wyc("Wyoming Judicial Branch, Supreme Court, Justice Bridget Hill", "/supreme-court/")),
     notes="Official Judicial Branch: sworn in May 28, 2025, succeeding Kate M. Fox (retired May 27, 2025). Retained 2026.",
     href="officials/judges/bridget-hill.html")
term(person_id="WY-BURNINGHAM-BEN", office_group="judicial", office="Chancery Court Judge",
     jurisdiction="Wyoming", how_took_office="retained",
     term_start=FM[2027], term_end=FM[2033], election_year=2026, sources=srcs(src(2026)),
     notes="Retained 2026. Term begins January 2027, after the snapshot window.",
     href="officials/judges/ben-burningham.html")

print("terms after judicial", len(TERMS))

# ---------- Precinct committee, 2020-2026 primaries (named winners only) ----------
def add_precinct_from_parsed():
    import json as _json
    parsed = {
        2020: Path("/tmp/weston-parsed/2020P.json"),
        2022: Path("/tmp/weston-parsed/2022P.json"),
        2024: Path("/tmp/weston-parsed/2024P.json"),
    }
    # person_id lookup by normalized name
    by_name = {}
    for pid, p in PEOPLE.items():
        by_name[re.sub(r"[^A-Z0-9]", "", p["display_name"].upper())] = pid
        if p.get("aliases"):
            for a in p["aliases"].split(";"):
                by_name[re.sub(r"[^A-Z0-9]", "", a.upper())] = pid

    def pid_for(name):
        key = re.sub(r"[^A-Z0-9]", "", name.upper())
        if key in by_name:
            return by_name[key]
        # mint
        parts = name.replace(",", " ").split()
        if len(parts) < 2:
            return None
        first, last = parts[0].title(), parts[-1].title()
        pid = f"WY-{last.upper()}-{first.upper()}"
        # avoid collisions with a different person already in PEOPLE
        if pid in PEOPLE:
            # if last+first match, reuse; else skip (don't invent a variant blindly)
            if PEOPLE[pid]["last"].upper() == last.upper() and PEOPLE[pid]["first"].upper().startswith(first[0].upper()):
                return pid
            return None
        person(pid, name.title(), first, last, minted=True,
               slug=re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"))
        by_name[key] = pid
        return pid

    for year, path in parsed.items():
        if not path.is_file():
            continue
        contests = _json.loads(path.read_text())
        for c in contests:
            title = c["title"]
            m = re.search(r"(REP|DEM)\s+PCT\s+COMMITTEE(MAN|WOMAN)\s+(\d-\d)", title, re.I)
            if not m:
                m = re.search(r"(REP|DEM).*PRECINCT COMMITTEE(MAN|WOMAN)\s+(\d-\d)", title, re.I)
            if not m:
                continue
            party = "R" if m.group(1).upper().startswith("R") else "D"
            kind = "Committeeman" if m.group(2).upper().endswith("MAN") and not m.group(2).upper().endswith("WOMAN") else "Committeewoman"
            if "WOMAN" in title.upper():
                kind = "Committeewoman"
            elif "MAN" in title.upper():
                kind = "Committeeman"
            prec = m.group(3)
            vf = c.get("vote_for") or 1
            named = [x for x in c["candidates"] if not x.get("writein") and x["name"].upper() not in ("WRITE-IN TOTALS", "WRITE-IN")]
            named = sorted(named, key=lambda x: -x["votes"])
            winners = named[:vf] if named else []
            for w in winners:
                if w["votes"] <= 0:
                    continue
                pid = pid_for(w["name"])
                if not pid:
                    continue
                term(person_id=pid, office_group="precincts",
                     office=f"Precinct {prec} {kind}",
                     jurisdiction=f"Weston precinct {prec}",
                     party=party, term_start=f"{year}-09-01", term_end=f"{year+2}-09-01",
                     election_year=year, how_took_office="elected",
                     sources=srcs(src(year, "primary")),
                     notes=f"{year} official primary, {title}: {w['name']} {w['votes']} votes.")

add_precinct_from_parsed()
print("terms after precincts", len(TERMS))


# ---------- Snapshot + outputs ----------
EXPECTED = {
    "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
    "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
                  ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
    "state-senate": [("Senate District 1 (S01)", 1), ("Senate District 3 (S03)", 1)],
    "state-house": [("House District 1 (H01)", 1), ("House District 2 (H02)", 1)],
    "county": [("County Commissioner", 5), ("County Clerk", 1), ("County Treasurer", 1),
               ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
               ("Clerk of District Court", 1), ("County Coroner", 1)],
    "municipal": [("Newcastle Mayor", 1), ("Newcastle City Council, at-large", 6),
                  ("Upton Mayor", 1), ("Upton Town Council, at-large", 4)],
    "schools": [("Weston County School District #1 Board, at-large", 9),
                ("Weston County School District #7 Board, at-large", 5)],
}

GROUP_META = [
    ("federal", "Federal", "office-and-name"),
    ("statewide", "Statewide", "office-and-name"),
    ("state-senate", "State Senate", "office-and-name"),
    ("state-house", "State House", "office-and-name"),
    ("county", "County Offices", "heading-then-names"),
    ("municipal", "Municipal offices", "heading-then-names"),
    ("schools", "School boards", "heading-then-names"),
    ("special-districts", "Special districts", "heading-then-names"),
    ("judicial", "Judicial (district, circuit, and statewide justices on file)", "heading-then-names"),
    ("precincts", "Precincts", "heading-then-names"),
]

def in_snapshot(t, year):
    """True if the person was in office on January 8 of year (after the first Monday and after congressional swearing-in)."""
    as_of = f"{year}-01-08"
    return t["term_start"] <= as_of < t["term_end"]

def holder_from_term(t):
    p = PEOPLE.get(t["person_id"], {})
    href = t.get("href") or ""
    if not href and p.get("slug"):
        # prefer existing local profile years if present, else historical
        href = f"candidates/local-history/c/{p['slug']}.html"
    h = {
        "name": t["name"],
        "person_id": t["person_id"],
        "party": t.get("party") or "",
        "term_end": "January " + t["term_end"][:4] if t.get("term_end") else "",
        "sources": t.get("sources") or [],
        "confidence": t.get("confidence"),
        "notes": t.get("notes") or "",
    }
    if href:
        h["href"] = href
    if t.get("ballot_name"):
        h["ballot_name"] = t["ballot_name"]
    if t.get("role"):
        h["role"] = t["role"]
    if t.get("retention"):
        h["retention"] = t["retention"]
    if t.get("flags"):
        h["flags"] = t["flags"]
    return h

def office_base(title):
    return re.sub(r"\s*\((2-year|unexpired)\)\s*$", "", title, flags=re.I).strip()

def build_snapshot(year):
    as_of = f"{year}-01-08"
    groups = []
    coverage = []
    active = [t for t in TERMS if in_snapshot(t, year)]
    for gid, title, default_layout in GROUP_META:
        gterms = [t for t in active if t["office_group"] == gid]
        # group by office (collapse 2-year / unexpired into the main office for seat counts)
        by_off = defaultdict(list)
        for t in gterms:
            by_off[office_base(t["office"])].append(t)
        offices = []
        if gid == "precincts":
            precincts = []
            for off, ts in sorted(by_off.items()):
                holders = [holder_from_term(t) for t in ts]
                precincts.append({"office": off, "layout": "heading-then-names", "holders": holders})
            note = ("Precinct committee people are from official primary results for 2020, 2022, and 2024 "
                    "(named winners only). Official 2012–2018 primary PDFs are archived under "
                    "/workspace/wyoleg/local-results/weston/<year>/ but the two-column scanned EL45 reports "
                    "were not fully keyed; those years are marked Not yet collected.")
            if year <= 2020:
                # 2020 primary elects appear in Jan 2021-2022. Jan 2015-2020 are not yet collected.
                if year <= 2020:
                    note = "Precinct committee rosters for this January are not yet collected. Official primary PDFs for 2012–2020 are archived."
                    precincts = []
            groups.append({"id": gid, "title": title, "note": note, "precincts": precincts, "sort_key": "P"})
            have = sum(len(p["holders"]) for p in precincts)
            coverage.append({"year": year, "group": gid, "have": have,
                             "not_collected": "yes" if not precincts else "partial" if have else "yes"})
            continue

        expected = EXPECTED.get(gid, [])
        expected_map = {o: n for o, n in expected}
        all_offices = list(by_off.keys())
        for o, _n in expected:
            if o not in all_offices:
                all_offices.append(o)
        have_n = 0
        missing_n = 0
        for off in all_offices:
            ts = by_off.get(off, [])
            holders = [holder_from_term(t) for t in ts]
            need = expected_map.get(off)
            if need is not None and len(holders) < need:
                for _ in range(need - len(holders)):
                    holders.append({"name": "Not yet collected", "person_id": "", "party": "", "notes": "No official name collected for this seat in this January."})
                    missing_n += 1
            have_n += sum(1 for h in holders if h.get("person_id"))
            layout = "heading-then-names" if len(holders) != 1 or (need and need > 1) else "office-and-name"
            offices.append({"office": off, "layout": layout, "holders": holders})
        note = ""
        if gid == "judicial":
            note = ("Supreme Court justices are the five who were in office this January, using official Wyoming Judicial Branch appointment and retirement dates together with Weston County retention results. Circuit, district, and magistrate rows are limited to judges who appeared on a Weston County official retention ballot in an adjoining cycle, plus the Weston circuit-court listing for Judge Bush when that listing applies; those local benches may be incomplete.")
        if gid == "special-districts":
            if not offices or not any(o["holders"] for o in offices):
                note = ("Elected special-district trustees were found only in the official May 8, 2018 Hospital "
                        "District and Museum District canvasses (serving into 2022). Other years are Not yet collected. "
                        "November ballot questions (mill levies, taxes) are not officeholders.")
                offices = []
        SORT = {"federal":"A","statewide":"B","state-senate":"C","state-house":"D",
                "county":"E","municipal":"F","schools":"G","special-districts":"H",
                "judicial":"J3"}
        groups.append({"id": gid, "title": title, "offices": offices, "note": note, "sort_key": SORT.get(gid, gid[:3].upper())})
        coverage.append({"year": year, "group": gid, "have": have_n, "not_collected": missing_n})

    snap = {
        "county": "Weston",
        "county_number": 21,
        "snapshot_year": year,
        "as_of": as_of,
        "as_of_label": f"January {year} (as of {as_of}, after the first Monday in January and after January 3 congressional terms, America/Denver)",
        "intro": f"Names are the people in office in January {year} (as of January 8).",
        "groups": groups,
        "generated_from": "data/county_officials/history/weston/terms.json",
        "retrieved": RETRIEVED,
    }
    return snap, coverage


PROFILE_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="cand-local">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} — Profile — WyoVote</title>
    <meta name="description" content="{desc}">
    <link rel="icon" href="../../../assets/img/surveyor-icon.png" type="image/png">
    <link rel="stylesheet" href="../../../css/styles.css">
    <link rel="stylesheet" href="../../../assets/css/site.css">
    <link rel="stylesheet" href="../../../officials/profile.css">
  </head>
  <body class="pf cand-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header">
      <div class="wrap header-inner">
        <a class="brand" href="../../../index.html">
          <img src="../../../assets/img/surveyor-icon.png" alt="" width="135" height="152">
          <span class="site-name">WyoVote</span>
        </a>
        <nav class="site-nav" aria-label="Site">
          <ul>
            <li><a href="../../../index.html">Home</a></li>
            <li><a href="../../../candidates.html" aria-current="page">Candidates</a></li>
            <li><a href="../../../committees.html">Committees</a></li>
            <li><a href="../../../counties.html">Counties</a></li>
            <li><a href="../../../officials.html">Officials</a></li>
            <li><a href="../../../people/index.html">Name Index</a></li>
            <li><a href="../../../research.html">Research</a></li>
            <li><a href="../../../archive.html">Archive</a></li>
          </ul>
        </nav>
      </div>
    </header>
    <main id="main" class="profile">
      <div class="wrap">
        <p class="back-row"><a class="back-btn" href="../../../counties/weston.html">← Back to Weston County</a></p>
        <section class="pf-head" aria-labelledby="h-name">
          <h1 id="h-name">{title}</h1>
          <p class="pf-sub">Profile</p>
        </section>
        <p class="cand-blurb">{blurb}</p>
        <section class="pf-card cand-research" aria-labelledby="h-results">
          <h2 id="h-results">Results</h2>
          <table class="cand-facts">{rows}</table>
          <div class="cand-sources-block">
            <h2 id="h-results-sources">Sources</h2>
            <ul class="cand-sources">{sources}</ul>
          </div>
        </section>
        <section class="pf-card cand-research" aria-labelledby="h-research">
          <h2 id="h-research">Research</h2>
          <table class="cand-facts"><tr><th scope="row">Residence</th><td>Weston County</td></tr>
          <tr><th scope="row">Background</th><td>Public information found for this Profile is limited to official election results and the officeholder history compiled from those results.</td></tr></table>
        </section>
      </div>
    </main>
    <footer class="site-footer">
      <div class="wrap footer-inner">
        <nav aria-label="Footer">
          <ul class="footer-links">
            <li><a href="../../../about.html">About</a></li>
            <li><a href="../../../privacy.html">Privacy</a></li>
            <li><a href="../../../contact.html">Contact</a></li>
            <li class="footer-guide"><a href="/guide/WyoVote-Users-Guide-v2.0.pdf">User's Guide</a></li>
          </ul>
        </nav>
        <p>&copy; 2026 WyoVote. All rights reserved.</p>
      </div>
    </footer>
  </body>
</html>
"""

def esc(s):
    return html.escape(str(s or ""), quote=True)

def existing_people_ids():
    ids = set()
    for path in (NAME_INDEX_PEOPLE, PEOPLE_DIR / "people_additions.csv"):
        if path.is_file():
            with path.open() as f:
                for r in csv.DictReader(f):
                    ids.add(r["person_id"])
    return ids

def write_people_additions():
    existing = existing_people_ids()
    path = PEOPLE_DIR / "people_additions.csv"
    # keep prior rows, append new minted historical people not already present
    fields = ["person_id","slug","display_name","sort_name","first","middle","last","suffix","aliases","name_status","sources","notes","minted"]
    have = set()
    rows = []
    if path.is_file():
        with path.open() as f:
            for r in csv.DictReader(f):
                rows.append(r)
                have.add(r["person_id"])
    added = 0
    for pid, p in PEOPLE.items():
        if pid in have:
            continue
        # only add people who appear in TERMS (or minted historical)
        if not any(t["person_id"]==pid for t in TERMS):
            continue
        src_label = "Weston County official election results 2012-2024, as recorded in officeholder history terms."
        rows.append({
            "person_id": pid, "slug": p["slug"], "display_name": p["display_name"],
            "sort_name": p["sort_name"], "first": p["first"], "middle": p.get("middle",""),
            "last": p["last"], "suffix": p.get("suffix",""), "aliases": p.get("aliases",""),
            "name_status": "historical",
            "sources": src_label,
            "notes": "Added for 114 County Officeholders history (Weston, 2015-2026).",
            "minted": "N" if pid in existing and p.get("minted")!="Y" else p.get("minted","Y"),
        })
        have.add(pid)
        added += 1
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    return added, len(rows)

def write_offices_held():
    path = PEOPLE_DIR / "offices_held_additions.csv"
    fields = ["person_id","office","office_level","jurisdiction","county","district","party","start_date","end_date","status","source","role"]
    have = set()
    rows = []
    if path.is_file():
        with path.open() as f:
            for r in csv.DictReader(f):
                rows.append(r)
                have.add((r["person_id"], r["office"], r["start_date"], r["end_date"]))
    added = 0
    for t in TERMS:
        key = (t["person_id"], t["office"], t["term_start"], t["term_end"])
        if key in have:
            continue
        srcs_url = " | ".join(s.get("url") or s.get("label","") for s in t.get("sources") or [])
        rows.append({
            "person_id": t["person_id"], "office": t["office"], "office_level": t["office_group"],
            "jurisdiction": t.get("jurisdiction",""), "county": "Weston",
            "district": "", "party": {"R":"Republican","D":"Democratic","I":"Independent"}.get(t.get("party"), t.get("party") or ""),
            "start_date": t["term_start"], "end_date": t["term_end"],
            "status": "historical", "source": srcs_url, "role": t.get("role") or "",
        })
        have.add(key)
        added += 1
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    return added

def write_profiles():
    existing_slugs = set()
    # don't overwrite 2022-2026 local profiles
    for d in (ROOT / "candidates").glob("*/c/*.html"):
        existing_slugs.add(d.stem)
    written = 0
    by_pid = defaultdict(list)
    for t in TERMS:
        by_pid[t["person_id"]].append(t)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    for pid, ts in by_pid.items():
        p = PEOPLE.get(pid)
        if not p:
            continue
        slug = p["slug"]
        # skip if a current local/officials profile already exists
        if slug in existing_slugs:
            continue
        # only write for minted historical people (or reused people with no page)
        rows_html = []
        src_html = []
        seen_src = set()
        for t in ts:
            label = f"{t.get('election_year') or t['term_start'][:4]} · {t['office']}"
            val = f"In office {t['term_start']} to {t['term_end']}"
            if t.get("how_took_office"):
                val += f" ({t['how_took_office']})"
            rows_html.append(f"<tr><th scope=\"row\">{esc(label)}</th><td>{esc(val)}</td></tr>")
            for s in t.get("sources") or []:
                url = s.get("url") or ""
                lab = s.get("label") or url
                if url and url not in seen_src:
                    src_html.append(f'<li><a href="{esc(url)}">{esc(lab)}</a> <span class="ext">(leaves WyoVote)</span></li>')
                    seen_src.add(url)
        if not rows_html:
            continue
        blurb = f"{p['display_name']} · Weston County officeholder history, 2015–2026."
        html_out = PROFILE_TEMPLATE.format(
            title=esc(p["display_name"]), desc=esc(blurb), blurb=esc(blurb),
            rows="".join(rows_html), sources="".join(src_html) or "<li>Official Weston County election results (see officeholder history sources).</li>",
        )
        path = PROFILE_DIR / f"{slug}.html"
        path.write_text(html_out)
        written += 1
    return written

def write_terms_and_snapshots():
    WESTON_H.mkdir(parents=True, exist_ok=True)
    SHARED_H.mkdir(parents=True, exist_ok=True)
    terms_path = WESTON_H / "terms.json"
    payload = {
        "county": "Weston",
        "county_number": 21,
        "schema": "effective-dated officeholder terms; January snapshots are generated from these records",
        "retrieved": RETRIEVED,
        "terms": TERMS,
    }
    terms_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    # shared extract
    shared_terms = [t for t in TERMS if t["office_group"] in {"federal", "statewide"}]
    (SHARED_H / "federal-statewide-terms.json").write_text(
        json.dumps({"schema": "shared federal and statewide dated terms (also stored on each county snapshot)",
                    "retrieved": RETRIEVED, "terms": shared_terms}, indent=2, ensure_ascii=False) + "\n")
    coverage_all = []
    for year in range(2015, 2027):
        snap, cov = build_snapshot(year)
        (WESTON_H / f"{year}.json").write_text(json.dumps(snap, indent=2, ensure_ascii=False) + "\n")
        coverage_all.extend(cov)
    cov_path = WESTON_H / "coverage.csv"
    with cov_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["year","group","have","not_collected"])
        w.writeheader(); w.writerows(coverage_all)
    return terms_path, cov_path, coverage_all

def print_coverage(coverage_all):
    groups = [g for g, _, _ in GROUP_META]
    print("\nCOVERAGE year x group (have / not_collected)")
    header = f"{'year':>6} " + " ".join(f"{g[:10]:>10}" for g in groups)
    print(header)
    by = defaultdict(dict)
    for r in coverage_all:
        by[r["year"]][r["group"]] = r
    for year in range(2015, 2027):
        bits = [f"{year:>6}"]
        for g in groups:
            r = by[year].get(g, {})
            bits.append(f"{str(r.get('have','-'))}/{str(r.get('not_collected','-')):>4}")
        print(" ".join(f"{b:>10}" for b in bits))


def update_weston_json():
    """Persist live legislative office notes on data/county_officials/weston.json."""
    path = ROOT / "data" / "county_officials" / "weston.json"
    data = json.loads(path.read_text())
    n = apply_to_groups(data.get("groups") or [], "weston")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"updated {path} legislative notes applied={n}")

def main():
    terms_path, cov_path, coverage_all = write_terms_and_snapshots()
    update_weston_json()
    n_people, n_people_total = write_people_additions()
    n_off = write_offices_held()
    n_prof = write_profiles()
    print("wrote", terms_path, "terms", len(TERMS))
    print("snapshots 2015-2026 in", WESTON_H)
    print("people added", n_people, "people_additions rows", n_people_total)
    print("offices_held added", n_off)
    print("thin historical profiles written", n_prof, "in", PROFILE_DIR)
    print_coverage(coverage_all)

if __name__ == "__main__":
    main()
