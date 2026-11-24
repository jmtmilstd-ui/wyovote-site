"""Official 2022 clerk results and official current Uinta holders through January 2027."""
from __future__ import annotations

BASE = "https://uintacountywy.gov/DocumentCenter/View"

CLERK_2022_GEN = f"{BASE}/7940/2022-Official-General-Election-Summary"
CLERK_2022_LABEL = ("Uinta County official 2022 general election summary (DocumentCenter/View/7940; "
                    "header OFFICIAL RESULTS, Election Summary - 11/10/2022 1:19 PM)")
ELECTED = "https://www.uintacountywy.gov/1084/List-of-All-Elected-Officials"
COMM = "https://www.uintacountywy.gov/15/County-Commissioners"
ASSESSOR = "https://www.uintacountywy.gov/18/County-Assessor"
EVAN_GOV = "https://www.evanstonwy.org/171/Government"
EVAN_DIR = "https://www.evanstonwy.org/Directory.aspx?did=3"
LYMAN = "https://lymanwy.com/index.asp?SEC=1194D5D1-CF0F-4001-B916-DF6EFE95A329&Type=B_LIST"
MTV_DIR = "https://www.mtvwy.com/directory"
MTV_COUNCIL = "https://www.mtvwy.com/mayor-and-council"
BEAR_CO = "https://www.uintacountywy.gov/211/Bear-River"
UCSD1 = "https://uinta1.com/en-US/school-board-under-construction-c936cc91"
UCSD4 = "https://www.uinta4.com/information/public_notices/public_notices_archive/public_notices_archive_f_y27/260702_notice_of_budget_hearing"
UCSD6 = "https://sites.google.com/lymanschools.org/ucsd6/information/school-board-information"
CD_TEAM = "https://www.uintacountycd.com/our-team"
CD_NEWS = "https://www.uintacountycd.com/_files/ugd/3f1386_6e8a8fde5f464717adf302f5938f8bb1.pdf"
SPECIAL = "https://www.uintacountywy.gov/532/Boards-Elected-by-Special-District"
MIN_2021 = f"{BASE}/7947"
MIN_2024 = f"{BASE}/8636"

def _T(**kw):
    import history_data_uinta as U
    return U.T(**kw)

def pg(year):
    import history_data_uinta as U
    return U.pg(year)

def s2022():
    return {"label": CLERK_2022_LABEL, "url": CLERK_2022_GEN}

def s(url, label):
    return {"label": label, "url": url}

def register_extra(P):
    rows = [
        ("WY-SOUTH-ERIC", "Eric South", "Eric", "South"),
        ("WY-HATCH-BRENT", "Brent Hatch", "Brent", "Hatch"),
        ("WY-PERKINS-LORI-S", "Lori S. Perkins", "Lori", "Perkins", "S."),
        ("WY-WILLIAMS-KENT", "Kent Williams", "Kent", "Williams"),
        ("WY-SCHMIDT-HENRY", "Henry Schmidt", "Henry", "Schmidt"),
        ("WY-HEGEMAN-JENNIE", "Jennie Hegeman", "Jennie", "Hegeman", "", "Jen Hegeman"),
        ("WY-SELLERS-MIKE", "Mike Sellers", "Mike", "Sellers"),
        ("WY-PERKES-EVAN", "Evan Perkes", "Evan", "Perkes"),
        ("WY-BERG-BRONSON", "Bronson Berg", "Bronson", "Berg"),
        ("WY-MORETTI-GREGG", "Gregg Moretti", "Gregg", "Moretti"),
        ("WY-BRAMLETT-JAMES", "James Bramlett", "James", "Bramlett", "", "Jimmy Bramlett"),
        ("WY-WILBUR-DANIELLE", "Danielle Wilbur", "Danielle", "Wilbur", "", "Dani Wilbur"),
        ("WY-AYRES-BRYAN", "Bryan Ayres", "Bryan", "Ayres"),
        ("WY-BONNER-KELLY", "Kelly Bonner", "Kelly", "Bonner"),
        ("WY-FERRIN-JAMY-D", "Jamy D. Ferrin", "Jamy", "Ferrin", "D.", "Jamy Ferrin"),
        ("WY-CARTER-TORI", "Tori Carter", "Tori", "Carter"),
        ("WY-TIMS-MICHAEL", "Michael Tims", "Michael", "Tims"),
        ("WY-KOFOED-CLYDE", "Clyde Kofoed", "Clyde", "Kofoed"),
        ("WY-BENNETT-DAVID", "David Bennett", "David", "Bennett"),
        ("WY-DAVIS-JANICE", "Janice Davis", "Janice", "Davis"),
        ("WY-LIND-JESSE-TRUSTEE", "Jesse Lind", "Jesse", "Lind"),  # unused; reuse WY-LIND-JESSE
        ("WY-WEAVER-CHRISTA-BARKER", "Christa Barker Weaver", "Christa", "Weaver"),
        ("WY-ARCH-JESSICA", "Jessica Arch", "Jessica", "Arch"),
        ("WY-PETERSON-DAVID", "David Peterson", "David", "Peterson"),
        ("WY-WHEELER-DAN", "Dan Wheeler", "Dan", "Wheeler"),
        ("WY-WOODWARD-BRIAN", "Brian Woodward", "Brian", "Woodward"),
        ("WY-DUBOIS-JOHN", "John DuBois", "John", "DuBois", "", "John R. Dubois Sr.; John R. DuBois Sr."),
        ("WY-CARPENTER-KELLY-Q", "Kelly Q. Carpenter", "Kelly", "Carpenter", "Q.", "Kelly Q Carpenter"),
        ("WY-RUDY-AARON", "Aaron Rudy", "Aaron", "Rudy"),
        ("WY-TIMS-BRIAN", "Brian Tims", "Brian", "Tims"),
        ("WY-DUNN-SUE", "Sue Dunn", "Sue", "Dunn"),
        ("WY-BLUEMEL-CHRISTI", "Christi Bluemel", "Christi", "Bluemel"),
        ("WY-LAMBERTI-JASON", "Jason Lamberti", "Jason", "Lamberti"),
        ("WY-HEATON-NATHAN", "Nathan Heaton", "Nathan", "Heaton"),
        ("WY-CORNELISON-DENNIS", "Dennis Cornelison", "Dennis", "Cornelison"),
        ("WY-STONE-DANA", "Dana Stone", "Dana", "Stone"),
        ("WY-LUNSFORD-DAN", "Dan Lunsford", "Dan", "Lunsford"),
        ("WY-WELLING-CRAIG-B", "Craig B. Welling", "Craig", "Welling", "B."),
    ]
    for row in rows:
        if row[0] == "WY-LIND-JESSE-TRUSTEE":
            continue
        pid, display, first, last = row[0], row[1], row[2], row[3]
        middle = row[4] if len(row) > 4 else ""
        aliases = row[5] if len(row) > 5 else ""
        P(pid, display, first, last, middle, aliases=aliases, minted=True)

def _add(terms, pid, name, group, office, jur, a, b, ey, party="", notes="", sources=None, how="elected", conf="high"):
    terms.append(_T(
        person_id=pid, name=name, party=party,
        office_group=group, office=office, jurisdiction=jur,
        term_start=a if isinstance(a, str) else __import__("history_lib", fromlist=["FM"]).FM[a],
        term_end=b if isinstance(b, str) else __import__("history_lib", fromlist=["FM"]).FM[b],
        how_took_office=how, election_year=ey, confidence=conf,
        sources=sources, notes=notes,
    ))

def add_holder_terms(terms):
    import history_lib as H
    FM = H.FM
    n22 = (lambda tot: f"Official 2022 Uinta clerk general (OFFICIAL RESULTS, 11/10/2022 1:19 PM): {tot}. Term begins January 2023.")
    src22 = [s2022()]

    # County 2022 winners, terms Jan 2023–Jan 2027
    _add(terms, "WY-ANDERSON-D-MARK", "D. Mark Anderson", "county", "County Commissioner", "Uinta County",
         2023, 2027, 2022, "REP",
         n22("David Mark Anderson 4,536, Eric South 4,215 (Vote-For-2). Official commission page lists him as Mark Anderson, Chairman, term end January 2027. Official 2026 general winner, continues January 2027–2031."),
         sources=src22 + [s(COMM, "Uinta County official County Commissioners members table"), s(ELECTED, "Uinta County official List of All Elected Officials")])
    _add(terms, "WY-SOUTH-ERIC", "Eric South", "county", "County Commissioner", "Uinta County",
         2023, 2027, 2022, "REP",
         n22("David Mark Anderson 4,536, Eric South 4,215 (Vote-For-2). Official commission page term end January 2027."),
         sources=src22 + [s(COMM, "Uinta County official County Commissioners members table")])
    _add(terms, "WY-HUTCHINSON-AMANDA", "Amanda Hutchinson", "county", "County Clerk", "Uinta County",
         2023, 2027, 2022, "REP", n22("Amanda Hutchinson 5,848.") + " Official 2026 general winner, continues January 2027–2031.",
         sources=src22 + [s(ELECTED, "Uinta County official List of All Elected Officials")])
    _add(terms, "WY-BRIMHALL-TERRY", "Terry Brimhall", "county", "County Treasurer", "Uinta County",
         2023, 2027, 2022, "REP", n22("Terry Brimhall 5,795.") + " Official 2026 general winner, continues January 2027–2031.",
         sources=src22)
    _add(terms, "WY-PERKINS-LORI-S", "Lori S. Perkins", "county", "County Assessor", "Uinta County",
         2023, 2026, 2022, "REP",
         n22("Lori S. Perkins 5,640.") + " Official current assessor pages list Ashlee Richins (term expires 2027); this term is encoded through the January 2025 snapshot only (term_end 2026-01-05) because a mid-term change is documented on official current pages. The exact official appointment date was not in the official minutes collected here.",
         sources=src22 + [s(ASSESSOR, "Uinta County official County Assessor page"), s(ELECTED, "Uinta County official List of All Elected Officials")])
    _add(terms, "WY-RICHINS-ASHLEE", "Ashlee Richins", "county", "County Assessor", "Uinta County",
         2026, 2027, None, "REP",
         "Official Uinta County Assessor page and official List of All Elected Officials (retrieved 2026-11-24) name Ashlee Richins, term expires 2027. Mid-term successor to official 2022 winner Lori S. Perkins. Official 2026 general winner, continues January 2027–2031.",
         sources=[s(ASSESSOR, "Uinta County official County Assessor page"), s(ELECTED, "Uinta County official List of All Elected Officials"), pg(2026)],
         how="appointed", conf="medium")
    _add(terms, "WY-KOPP-ANDY", "Andy Kopp", "county", "County Sheriff", "Uinta County",
         2023, 2027, 2022, "REP", n22("Andy Kopp 3,922, Rowdy Dean 2,652.") + " Official 2026 general winner, continues January 2027–2031.",
         sources=src22)
    _add(terms, "WY-KALLAS-LORETTA-HOWIESON", "Loretta Howieson Kallas", "county", "County Attorney", "Uinta County",
         2023, 2027, 2022, "REP", n22("Loretta Howieson Kallas 5,015.") + " Official 2026 general winner, continues January 2027–2031.",
         sources=src22)
    _add(terms, "WY-WRIGHT-KERRI", "Kerri Wright", "county", "Clerk of District Court", "Uinta County",
         2023, 2027, 2022, "REP", n22("Kerri Wright 5,728.") + " Official 2026 general winner, continues January 2027–2031.",
         sources=src22)
    _add(terms, "WY-CRANDALL-GREG", "Greg Crandall", "county", "County Coroner", "Uinta County",
         2023, 2027, 2022, "REP", n22("Greg Crandall 5,925.") + " Official 2026 general winner, continues January 2027–2031.",
         sources=src22)
    # Hatch: official current term January 2029; official minutes show he already held the seat in 2021 and 2024.
    _add(terms, "WY-HATCH-BRENT", "Brent Hatch", "county", "County Commissioner", "Uinta County",
         2022, 2025, 2020, "REP",
         "Official Uinta County Commissioners proceedings December 21, 2021 and January 16, 2024 name Commissioner Brent Hatch as present. Official 2020 clerk general results were not collected here; encoded from official minutes that he held the seat, at medium confidence, through January 2025.",
         sources=[s(MIN_2021, "Uinta County official Commissioners proceedings, December 21, 2021"),
                  s(MIN_2024, "Uinta County official Commissioners proceedings, January 16, 2024")],
         conf="medium")
    _add(terms, "WY-HATCH-BRENT", "Brent Hatch", "county", "County Commissioner", "Uinta County",
         2025, 2029, 2024, "REP",
         "Official County Commissioners members table (retrieved 2026-11-24) lists Brent Hatch, term end January 2029. Official 2024 clerk general summary was not found on the current official elections page or in a Wayback capture of DocumentCenter 8642 (that ID later holds the official 2026 general). Encoded from the official current term date, at medium confidence, without official 2024 vote totals.",
         sources=[s(COMM, "Uinta County official County Commissioners members table, term end January 2029"),
                  s(ELECTED, "Uinta County official List of All Elected Officials")],
         conf="medium")

    # Municipal 2022
    _add(terms, "WY-WILLIAMS-KENT", "Kent Williams", "municipal", "Evanston Mayor", "City of Evanston",
         2023, 2027, 2022, "", n22("Kent Williams 1,711, Tim Lynch 1,449.") + " Official City of Evanston Government page lists Mayor Kent Williams as current.",
         sources=src22 + [s(EVAN_GOV, "City of Evanston official Government page")])
    _add(terms, "WY-HEGEMAN-JENNIE", "Jennie Hegeman", "municipal", "Evanston City Council Ward 1", "City of Evanston",
         2023, 2027, 2022, "", n22("Jen Hegeman 475, Mikal D Welling 452.") + " Official city directory lists Jennie Hegeman.",
         sources=src22 + [s(EVAN_DIR, "City of Evanston official Mayor & Council Members directory")])
    _add(terms, "WY-LIND-JESSE", "Jesse Lind", "municipal", "Evanston City Council Ward 2", "City of Evanston",
         2023, 2027, 2022, "", n22("Jesse Lind 699, Tib Ottley 555.") + " Official city directory lists Jesse Lind, Ward II. Official 2026 Evanston mayor elect.",
         sources=src22 + [s(EVAN_DIR, "City of Evanston official Mayor & Council Members directory")])
    _add(terms, "WY-WELLING-DAVID-DON", "David Don Welling", "municipal", "Evanston City Council Ward 3", "City of Evanston",
         2023, 2027, 2022, "", n22("David Don Welling 621.") + " Official city directory lists David Welling. Official 2026 Ward 3 winner, continues January 2027–2031.",
         sources=src22 + [s(EVAN_DIR, "City of Evanston official Mayor & Council Members directory"), pg(2026)])
    # Evanston 2024-class current members, no official 2024 canvass collected
    for pid, name, office in [
        ("WY-SCHMIDT-HENRY", "Henry Schmidt", "Evanston City Council Ward 1"),
        ("WY-SELLERS-MIKE", "Mike Sellers", "Evanston City Council Ward 2"),
        ("WY-PERKES-EVAN", "Evan Perkes", "Evanston City Council Ward 3"),
    ]:
        _add(terms, pid, name, "municipal", office, "City of Evanston",
             2025, 2029, 2024, "",
             "Named on the official City of Evanston Government page and official Mayor & Council directory (retrieved 2026-11-24). Official 2024 clerk general results were not collected; term years follow the ordinary 4-year municipal cycle for the seat not on the official 2022 ward ballot, at medium confidence.",
             sources=[s(EVAN_GOV, "City of Evanston official Government page"), s(EVAN_DIR, "City of Evanston official Mayor & Council Members directory")],
             conf="medium")

    _add(terms, "WY-HOOTON-SHANE", "Shane Hooton", "municipal", "Lyman Mayor", "Town of Lyman",
         2023, 2027, 2022, "", n22("Shane Hooton 392, Allen Wyatt 287.") + " Official Town of Lyman mayor page: term expires Dec 31, 2026.",
         sources=src22 + [s(LYMAN, "Town of Lyman official Mayor and Council page")])
    _add(terms, "WY-BERG-BRONSON", "Bronson Berg", "municipal", "Lyman Town Council", "Town of Lyman",
         2023, 2027, 2022, "", n22("Bronson Berg 376, Gregg Moretti 373, over Jimmy Bramlett 258, Bob Armstrong 194.") + " Official town page term expires Dec 31, 2026.",
         sources=src22 + [s(LYMAN, "Town of Lyman official Mayor and Council page")])
    _add(terms, "WY-MORETTI-GREGG", "Gregg Moretti", "municipal", "Lyman Town Council", "Town of Lyman",
         2023, 2027, 2022, "", n22("Bronson Berg 376, Gregg Moretti 373.") + " Official town page term expires Dec 31, 2026.",
         sources=src22 + [s(LYMAN, "Town of Lyman official Mayor and Council page")])
    _add(terms, "WY-BRAMLETT-JAMES", "James Bramlett", "municipal", "Lyman Town Council", "Town of Lyman",
         2025, 2029, 2024, "",
         "Official Town of Lyman Mayor and Council page: Councilmember James Bramlett, term expires Dec 31, 2028. Official 2024 clerk general results were not collected; term date is from the official town page.",
         sources=[s(LYMAN, "Town of Lyman official Mayor and Council page")])
    _add(terms, "WY-WILBUR-DANIELLE", "Danielle Wilbur", "municipal", "Lyman Town Council", "Town of Lyman",
         2025, 2029, 2024, "",
         "Official Town of Lyman Mayor and Council page: Councilmember Danielle Wilbur, term expires Dec 31, 2028. Official 2024 clerk general results were not collected; term date is from the official town page.",
         sources=[s(LYMAN, "Town of Lyman official Mayor and Council page")])

    _add(terms, "WY-BONNER-KELLY", "Kelly Bonner", "municipal", "Mountain View Town Council", "Town of Mountain View",
         2023, 2027, 2022, "",
         n22("Kelly Bonner 275, Jamy D. Ferrin 260, over Katie (Johnson) Taylor 221.") + " Not named on the official Mountain View staff directory retrieved 2026-11-24; live roster omits this seat’s 2022 winner for that reason.",
         sources=src22)
    _add(terms, "WY-FERRIN-JAMY-D", "Jamy D. Ferrin", "municipal", "Mountain View Town Council", "Town of Mountain View",
         2023, 2027, 2022, "",
         n22("Kelly Bonner 275, Jamy D. Ferrin 260.") + " Official Mountain View directory lists Jamy Ferrin, Council President.",
         sources=src22 + [s(MTV_DIR, "Town of Mountain View official staff directory")])
    _add(terms, "WY-AYRES-BRYAN", "Bryan Ayres", "municipal", "Mountain View Mayor", "Town of Mountain View",
         2025, 2029, 2024, "",
         "Official Town of Mountain View staff directory and official Uinta County Mountain View page list Mayor Bryan Ayres (retrieved 2026-11-24). No mayor contest was on the official 2022 or 2026 clerk generals. Official 2024 clerk results were not collected; encoded as current from official town/county pages, at medium confidence for the term start.",
         sources=[s(MTV_DIR, "Town of Mountain View official staff directory"), s("https://www.uintacountywy.gov/213/Mountain-View", "Uinta County official Mountain View page")],
         conf="medium")
    for pid, name in [("WY-BRUNSKI-DECKERT-BRITTNEY", "Brittney Brunski-Deckert"), ("WY-CARTER-TORI", "Tori Carter"), ("WY-TIMS-MICHAEL", "Michael Tims")]:
        ey, a, b, conf, extra = (2024, 2025, 2029, "medium", " Official 2026 general Vote-For-2 winner, continues January 2027–2031." if "Brunski" in name else "")
        _add(terms, pid, name, "municipal", "Mountain View Town Council", "Town of Mountain View",
             a, b, ey, "",
             "Named on the official Town of Mountain View staff directory (retrieved 2026-11-24)." + extra + " Official 2024 clerk general results were not collected; term years follow the ordinary 4-year cycle for seats not won on the official 2022 council contest, at medium confidence.",
             sources=[s(MTV_DIR, "Town of Mountain View official staff directory")] + ([pg(2026)] if "Brunski" in name else []),
             conf=conf)

    _add(terms, "WY-STOKES-BRIAN-J", "Brian J. Stokes", "municipal", "Bear River Town Council", "Town of Bear River",
         2023, 2027, 2022, "",
         n22("BJ Stokes 111, Clyde Kofoed 98, over Todd M. Jones 72, James G. Johnson 35 (Vote-For-2).") + " Official 2026 general Vote-For-2 winner, continues January 2027–2031.",
         sources=src22 + [pg(2026)])
    _add(terms, "WY-KOFOED-CLYDE", "Clyde Kofoed", "municipal", "Bear River Town Council", "Town of Bear River",
         2023, 2027, 2022, "",
         n22("BJ Stokes 111, Clyde Kofoed 98.") + " Official Uinta County Bear River page now lists Clyde Kofoed as Mayor; the date he left the council seat, if he did, is not in an official 2024 clerk general collected here.",
         sources=src22 + [s(BEAR_CO, "Uinta County official Bear River page, Mayor Clyde Kofoed")])
    _add(terms, "WY-KOFOED-CLYDE", "Clyde Kofoed", "municipal", "Bear River Mayor", "Town of Bear River",
         2025, 2029, 2024, "",
         "Official Uinta County Bear River page (retrieved 2026-11-24) lists Mayor Clyde Kofoed. No Bear River mayor contest was on the official 2022 or 2026 clerk generals. Official 2024 clerk results were not collected; encoded as current from the official county town page, at medium confidence for the term start.",
         sources=[s(BEAR_CO, "Uinta County official Bear River page, Mayor Clyde Kofoed")],
         conf="medium")

    # Schools 2022
    for pid, name, tot in [
        ("WY-WELLING-JENNY", "Jenny Welling", "Jenny Welling 2,059"),
        ("WY-BENNETT-DAVID", "David Bennett", "David Bennett 1,911"),
        ("WY-GUILD-CALEB", "Caleb Guild", "Caleb Guild 1,887"),
        ("WY-LIND-JESSE", "Jesse Lind", "Jesse Lind 1,715 (also official 2022 Evanston Ward 2 winner and official 2026 Evanston mayor elect). The official UCSD #1 School Board staff list retrieved 2026-11-24 does not include Jesse Lind; he is omitted from the live roster for that reason"),
        ("WY-DAVIS-JANICE", "Janice Davis", "Janice Davis 1,619, over Brian Woodward 1,597"),
    ]:
        _add(terms, pid, name, "schools", "UCSD #1 Trustee", "Uinta County School District #1",
             2023, 2027, 2022, "",
             n22("Vote-For-5: " + tot + "."),
             sources=src22 + [s(UCSD1, "Uinta County School District #1 official School Board page")])
    _add(terms, "WY-WEAVER-CHRISTA-BARKER", "Christa Barker Weaver", "schools", "UCSD #1 Trustee", "Uinta County School District #1",
         2023, 2025, 2022, "",
         n22("Unexpired 2-year term: Christa Barker Weaver 2,653, Tamra Mander Petersen 709."),
         sources=src22)
    # 2024-class UCSD #1 named on official current board page (not 2022 VF5 winners, not 2026-only elects)
    for pid, name, role in [
        ("WY-ARCH-JESSICA", "Jessica Arch", ""),
        ("WY-PETERSON-DAVID", "David Peterson", " Official page lists David Peterson, Chairman."),
        ("WY-WHEELER-DAN", "Dan Wheeler", ""),
        ("WY-WOODWARD-BRIAN", "Brian Woodward", ""),
        ("WY-DUBOIS-JOHN", "John DuBois", ""),
    ]:
        _add(terms, pid, name, "schools", "UCSD #1 Trustee", "Uinta County School District #1",
             2025, 2029, 2024, "",
             "Named on the official UCSD #1 School Board page staff list (retrieved 2026-11-24)." + role + " Official 2024 clerk general results were not collected; encoded from the official current board list, at medium confidence for the term start.",
             sources=[s(UCSD1, "Uinta County School District #1 official School Board page")],
             conf="medium")

    _add(terms, "WY-CARPENTER-KELLY-Q", "Kelly Q. Carpenter", "schools", "UCSD #4 Trustee", "Uinta County School District #4",
         2023, 2027, 2022, "", n22("Kelly Q Carpenter 992, Dale Madsen 904 (Vote-For-2)."),
         sources=src22)
    _add(terms, "WY-MADSEN-DALE", "Dale Madsen", "schools", "UCSD #4 Trustee", "Uinta County School District #4",
         2023, 2027, 2022, "", n22("Kelly Q Carpenter 992, Dale Madsen 904.") + " Official 2026 general Vote-For-2 winner, continues January 2027–2031.",
         sources=src22 + [pg(2026)])
    for pid, name, role in [("WY-RUDY-AARON", "Aaron Rudy", " Chairman of the Board of Trustees."), ("WY-TIMS-BRIAN", "Brian Tims", " Clerk of the Board of Trustees.")]:
        _add(terms, pid, name, "schools", "UCSD #4 Trustee", "Uinta County School District #4",
             2025, 2029, 2024, "",
             "Official UCSD #4 Notice of Public Hearing on the FY2027 budget (dated June 30, 2026) is attested by" + role + " Official 2024 clerk general results were not collected; encoded from that official district notice, at medium confidence for the term start. A fifth current trustee was not named in the official sources collected here.",
             sources=[s(UCSD4, "Uinta County School District #4 official Notice of Public Hearing, budget for fiscal year ending June 30, 2027")],
             conf="medium")

    _add(terms, "WY-EYRE-SPENCER-J", "Spencer J. Eyre", "schools", "UCSD #6 Trustee", "Uinta County School District #6",
         2023, 2027, 2022, "", n22("Spencer J. Eyre 696, Jason Lamberti 473, over Kalli H. Hill 439, Amber Taylor 325.") + " Official 2026 general Vote-For-2 winner, continues January 2027–2031.",
         sources=src22 + [s(UCSD6, "Uinta County School District #6 official School Board Information page"), pg(2026)])
    _add(terms, "WY-LAMBERTI-JASON", "Jason Lamberti", "schools", "UCSD #6 Trustee", "Uinta County School District #6",
         2023, 2027, 2022, "", n22("Spencer J. Eyre 696, Jason Lamberti 473."),
         sources=src22 + [s(UCSD6, "Uinta County School District #6 official School Board Information page")])
    for pid, name, role in [
        ("WY-DUNN-SUE", "Sue Dunn", ""),
        ("WY-BLUEMEL-CHRISTI", "Christi Bluemel", ""),
        ("WY-HEATON-NATHAN", "Nathan Heaton", " Official page lists Nathan Heaton, Chairman."),
    ]:
        _add(terms, pid, name, "schools", "UCSD #6 Trustee", "Uinta County School District #6",
             2025, 2029, 2024, "",
             "Named on the official UCSD #6 School Board Information page (retrieved 2026-11-24)." + role + " Official 2024 clerk general results were not collected; encoded from the official current board list, at medium confidence for the term start.",
             sources=[s(UCSD6, "Uinta County School District #6 official School Board Information page")],
             conf="medium")

    # Conservation / fire 2022
    _add(terms, "WY-GUILD-KELLY", "Kelly Guild", "special-districts", "Uinta Conservation District Rural Supervisor", "Uinta County",
         2023, 2027, 2022, "", n22("Kelly Guild 5,482 (Rural).") + " Official 2026 rural winner, continues. Official CD January 2026 newsletter lists Kelly Guild, Chairman.",
         sources=src22 + [s(CD_NEWS, "Uinta County Conservation District official January 2026 newsletter"), pg(2026)])
    _add(terms, "WY-LESTER-TY", "Ty Lester", "special-districts", "Uinta Conservation District Urban Supervisor", "Uinta County",
         2023, 2027, 2022, "", n22("Ty Lester 5,222 (Urban).") + " Official 2026 clerk lists Ty Lester as a Rural Vote-For-1 winner (continuing). Official CD January 2026 newsletter lists Ty Lester, Secretary/Treasurer.",
         sources=src22 + [s(CD_NEWS, "Uinta County Conservation District official January 2026 newsletter"), pg(2026)])
    _add(terms, "WY-CONDOS-KEVIN", "Kevin Condos", "special-districts", "Uinta Conservation District At-Large Supervisor", "Uinta County",
         2023, 2027, 2022, "", n22("Kevin Condos 5,167 (At Large).") + " Official 2026 at-large winner, continues.",
         sources=src22 + [s(CD_NEWS, "Uinta County Conservation District official January 2026 newsletter"), pg(2026)])
    _add(terms, "WY-CORNELISON-DENNIS", "Dennis Cornelison", "special-districts", "Uinta Conservation District Rural Supervisor", "Uinta County",
         2025, 2026, 2024, "",
         "Official Uinta County Boards Elected by Special District page lists Dennis Cornelison (rural), term expiration 2028. Official Uinta County Conservation District January 2026 newsletter states he served until his retirement in August 2025. Encoded through the January 2025 snapshot only. Official 2024 clerk results were not collected.",
         sources=[s(SPECIAL, "Uinta County official Boards Elected by Special District page"),
                  s(CD_NEWS, "Uinta County Conservation District official January 2026 newsletter, Dennis Cornelison retirement")],
         conf="medium")
    _add(terms, "WY-EYRE-SPENCER-J", "Spencer J. Eyre", "special-districts", "Uinta Conservation District Rural Supervisor", "Uinta County",
         2025, 2029, 2024, "",
         "Official CD January 2026 newsletter lists Spencer Eyre, Vice Chairman. Official county special-district boards page lists Spencer J. Eyre (rural), term expiration 2028. Official 2024 clerk results were not collected.",
         sources=[s(CD_NEWS, "Uinta County Conservation District official January 2026 newsletter"), s(SPECIAL, "Uinta County official Boards Elected by Special District page")],
         conf="medium")
    _add(terms, "WY-STODDARD-WADE", "Wade Stoddard", "special-districts", "Uinta Conservation District Urban Supervisor", "Uinta County",
         2026, 2027, None, "",
         "Official CD January 2026 newsletter lists Wade Stoddard as a Board of Supervisors member (retrieved board list in that official January 2026 publication). Official 2026 clerk urban winner, continues January 2027–2031. Official 2024 clerk results were not collected; mid-2025 seating after Dennis Cornelison’s official CD-noted August 2025 retirement is not given an official appointment date here.",
         sources=[s(CD_NEWS, "Uinta County Conservation District official January 2026 newsletter"), pg(2026)],
         how="appointed", conf="medium")
    _add(terms, "WY-STONE-DANA", "Dana Stone", "special-districts", "Uinta County Rural Fire District Director", "Uinta County",
         2023, 2027, 2022, "", n22("Dana Stone 1,721.") + " Official county special-district boards page lists Dana Stone, term expiration 2026.",
         sources=src22 + [s(SPECIAL, "Uinta County official Boards Elected by Special District page")])
    for pid, name, yr in [("WY-LUNSFORD-DAN", "Dan Lunsford", "2028"), ("WY-WELLING-CRAIG-B", "Craig B. Welling", "2028")]:
        _add(terms, pid, name, "special-districts", "Uinta County Rural Fire District Director", "Uinta County",
             2025, 2029, 2024, "",
             f"Official Uinta County Boards Elected by Special District page lists {name}, term expiration {yr} (retrieved 2026-11-24). Official 2024 clerk general results were not collected.",
             sources=[s(SPECIAL, "Uinta County official Boards Elected by Special District page")],
             conf="medium")

def expand_expected(expected):
    expected["municipal"] = [
        ("Evanston Mayor", 1), ("Evanston City Council Ward 1", 2), ("Evanston City Council Ward 2", 2),
        ("Evanston City Council Ward 3", 2), ("Lyman Mayor", 1), ("Lyman Town Council", 4),
        ("Mountain View Mayor", 1), ("Mountain View Town Council", 4),
        ("Bear River Mayor", 1), ("Bear River Town Council", 4),
    ]
    expected["schools"] = [("UCSD #1 Trustee", 9), ("UCSD #4 Trustee", 5), ("UCSD #6 Trustee", 5)]
    expected["special-districts"] = [
        ("Uinta Conservation District Rural Supervisor", 3),
        ("Uinta Conservation District Urban Supervisor", 1),
        ("Uinta Conservation District At-Large Supervisor", 1),
        ("Uinta County Rural Fire District Director", 3),
    ]
    return expected
