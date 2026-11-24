#!/usr/bin/env python3
"""Goshen County officeholder history (preview). Official clerk, SOS, court,
and city sources only. Names are never invented.
"""
from __future__ import annotations

import json
from copy import deepcopy

import history_lib as H
from history_lib import FM, ROOT, src_dict, term

RETRIEVED = "2026-11-24"
CN = 7
SLUG = "goshen"

URL_ELECTIONS = "https://goshencounty.org/191/Election-Results"
URL_GEN_ARCH = "https://goshencounty.org/Archive.aspx?AMID=38"
URL_PRI_ARCH = "https://goshencounty.org/Archive.aspx?AMID=37"
URL_C26 = "https://goshencounty.org/ArchiveCenter/ViewFile/Item/162"
URL_P26 = "https://goshencounty.org/ArchiveCenter/ViewFile/Item/161"
URL_C24 = "https://goshencounty.org/ArchiveCenter/ViewFile/Item/143"
URL_C24R = "https://goshencounty.org/ArchiveCenter/ViewFile/Item/142"
URL_C22 = "https://goshencounty.org/ArchiveCenter/ViewFile/Item/135"
URL_C20 = "https://goshencounty.org/ArchiveCenter/ViewFile/Item/138"
URL_C18 = "https://goshencounty.org/ArchiveCenter/ViewFile/Item/75"
URL_C16 = "https://goshencounty.org/ArchiveCenter/ViewFile/Item/74"
URL_COMM = "https://goshencounty.org/262/County-Commissioners"
URL_TORR = "https://www.torringtonwy.gov/268/City-Council"
URL_TORR_ELEC = "https://www.torringtonwy.gov/366/Election-Information"
URL_LINGLE_COUNCIL = "https://www.townoflingle.com/person-category/council/"
URL_LINGLE_2026 = "https://www.townoflingle.com/unofficial-election-results/"
URL_LINGLE_MIN_2026_05 = "https://www.townoflingle.com/wp-content/uploads/2024/01/5-6-2026-Minutes.pdf"
URL_LINGLE_MIN_2026_10 = "https://www.townoflingle.com/wp-content/uploads/2024/01/10-7-2026-Minutes.pdf"
URL_LINGLE_MIN_2024_05 = "https://www.townoflingle.com/wp-content/uploads/2024/01/5-22-2024-Minutes.pdf"
URL_LINGLE_MIN_2024_06 = "https://www.townoflingle.com/wp-content/uploads/2024/01/6-5-2024-Minutes.pdf"
URL_FL_CONTACT = "https://sites.google.com/view/town-of-fort-laramie/contact-us"
URL_FL_RECORDS = "https://sites.google.com/view/town-of-fort-laramie/public-records"
URL_LAGRANGE_GOV = "https://www.lagrangewyo.gov/government/"
URL_LAGRANGE_WELCOME = "https://www.lagrangewyo.gov/wp-content/uploads/2026/01/Updated-Welcome-Book-as-of-11-26-25.pdf"
URL_LAGRANGE_MAY2026 = "https://www.lagrangewyo.gov/wp-content/uploads/2026/04/may2026.pdf"
URL_COURT_D = "https://www.wyocourts.gov/court/district-court-8th-judicial-district-converse-county/"
URL_COURT_G = "https://www.wyocourts.gov/court/circuit-court-of-the-8th-judicial-district-goshen-county-state-of-wyoming-torrington/"
URL_COURT_C = "https://www.wyocourts.gov/court/circuit-court-of-the-8th-judicial-district-converse-county-state-of-wyoming-douglas/"


def S(label, url=""):
    return src_dict(label, url)

SRC_C26 = S("Official Goshen County 2026 general election summary (ArchiveCenter Item 162; header OFFICIAL RESULTS, Election Summary - 11/05/2026 05:05PM), including the official GC school-board recount page in the same PDF (Recount Summary GC School Board - 11/05/2026 05:11PM)", URL_C26)
SRC_C24 = S("Official Goshen County 2024 general election summary (ArchiveCenter Item 143; header OFFICIAL RESULTS, GOSHEN COUNTY - GENERAL ELECTION SUMMARY - 11/08/2024 01:39PM)", URL_C24)
SRC_C24R = S("Official Goshen County 2024 general school-district recount (ArchiveCenter Item 142; header OFFICIAL RESULTS, RECOUNT SCHOOL DISTRICTS - 11/08/2024 01:45PM)", URL_C24R)
SRC_C22 = S("Official Goshen County 2022 general election official results (ArchiveCenter Item 135; header OFFICIAL RESULTS)", URL_C22)
SRC_C20 = S("Official Goshen County 2020 general election official results (ArchiveCenter Item 138; header OFFICIAL RESULTS, 11/05/2020 3:46 PM)", URL_C20)
SRC_C18 = S("Official Goshen County 2018 general election official results (ArchiveCenter Item 75; header 2018 General Election Official Results, Date:11/08/18 Time:13:26:16)", URL_C18)
SRC_C16 = S("Official Goshen County 2016 general election official results (ArchiveCenter Item 74; header Official Results General 2016, Date:11/10/16 Time:14:44:31)", URL_C16)
SRC_COMM = S("Official Goshen County Commissioners page (Michael McNamee, Chairman; Justin Burkart, Vice Chairman; Aaron P. Walsh)", URL_COMM)
SRC_TORR = S("Official City of Torrington City Council page and official Election Information page (2026 mayoral seat listed as a four-year elected office)", URL_TORR_ELEC)
SRC_LINGLE_COUNCIL = S("Official Town of Lingle Town Council page (Mayor George Siglin; council Kathy Wilhelm, Mayor Pro Tempore; Shelly Duncan; Brian Ingram; Delwin Watson)", URL_LINGLE_COUNCIL)
SRC_LINGLE_2026 = S("Official Town of Lingle official 2026 municipal election results page (header Official election results; canvassed May 6, 2026)", URL_LINGLE_2026)
SRC_LINGLE_MIN_2026_05 = S("Official Town of Lingle May 6, 2026 regular council minutes (Clerk/Treasurer report of the official May 5, 2026 municipal canvass; install date June 3, 2026)", URL_LINGLE_MIN_2026_05)
SRC_LINGLE_MIN_2026_10 = S("Official Town of Lingle October 7, 2026 regular council minutes (roll call: Mayor George Siglin; council Kathy Wilhelm, Brian Ingram, Del Watson, Shelly Duncan)", URL_LINGLE_MIN_2026_10)
SRC_LINGLE_MIN_2024_05 = S("Official Town of Lingle May 22, 2024 regular council minutes (May 14, 2024 municipal election: Jeff Jerome and Shelly Duncan collected the most votes; 64 ballots)", URL_LINGLE_MIN_2024_05)
SRC_LINGLE_MIN_2024_06 = S("Official Town of Lingle June 5, 2024 regular council minutes (Oath of Office administered to newly elected council members Jeff Jerome and Shelly Duncan)", URL_LINGLE_MIN_2024_06)
SRC_FL_CONTACT = S("Official Town of Fort Laramie Contact us page (Mayor Ryon Brown; council Jason Curtsinger, Jacob Ellis, Chris Sachanandani, Alicia Tanner)", URL_FL_CONTACT)
SRC_FL_MIN_2025_12 = S("Official Town of Fort Laramie December 10, 2025 regular meeting minutes, posted on the official Public Records page (Mayor Brown; council Curtsinger, Ellis, Sachanandani, Tanner)", URL_FL_RECORDS)
SRC_FL_MIN_2026_01 = S("Official Town of Fort Laramie January 14, 2026 regular meeting minutes, posted on the official Public Records page (Mayor Brown; council Curtsinger, Ellis, Sachanandani, Tanner present)", URL_FL_RECORDS)
SRC_FL_MIN_2026_05_13 = S("Official Town of Fort Laramie May 13, 2026 regular meeting minutes: Alicia Tanner and Jacob Ellis elected May 5, 2026 to the two term-expiring council seats; Tanner took the oath for a four-year term", URL_FL_RECORDS)
SRC_FL_MIN_2026_05_27 = S("Official Town of Fort Laramie May 27, 2026 regular meeting minutes: Jacob Ellis took the oath for a four-year term", URL_FL_RECORDS)
SRC_FL_MIN_2026_10_14 = S("Official Town of Fort Laramie October 14, 2026 regular meeting minutes (roll call: Mayor Brown; council Curtsinger, Sachanandani, Tanner; Mayor Brown appointed Cody Powell to fill the vacant seat, oath at the next meeting)", URL_FL_RECORDS)
SRC_FL_MIN_2026_10_28 = S("Official Town of Fort Laramie October 28, 2026 regular meeting minutes (roll call: Mayor Brown; council Curtsinger, Sachanandani, Tanner; newly appointed CM Powell scheduled to take the oath November 18, 2026)", URL_FL_RECORDS)
SRC_LAGRANGE_GOV = S("Official Town of LaGrange Government page (Mayor Kirk Haas, term 2029; council Michael Huseby, term 2027; Jennifer Pragnell, term 2027; Teresa “Tracy” May, term 2029; John Goold, term 2029; elections the 2nd Tuesday in May on odd years)", URL_LAGRANGE_GOV)
SRC_LAGRANGE_WELCOME = S("Official Town of LaGrange Welcome Booklet (updated as of 11/26/25): Mayor (4 years) Kirk Haas 2029; Council Member (2 years) Michael Huseby 2027; Council Member (4 years) Tracy May 2029; Council Member (4 years) John Goold 2029; Council Member (2 years) Jennifer Pragnell 2027", URL_LAGRANGE_WELCOME)
SRC_LAGRANGE_MAY2026 = S("Official Town of LaGrange May 2026 newsletter, minutes of the April 9, 2026 regular council meeting (present: Mayor Kirk Haas; council John Goold, Jenny Pragnell, Mike Huseby, Tracy May)", URL_LAGRANGE_MAY2026)
SRC_COURT_D = S("Official Wyoming Judicial Branch, District Court, 8th Judicial District page", URL_COURT_D)
SRC_COURT_G = S("Official Wyoming Judicial Branch, Circuit Court of the 8th Judicial District, Goshen County (Torrington) page", URL_COURT_G)
SRC_COURT_C = S("Official Wyoming Judicial Branch, Circuit Court of the 8th Judicial District, Converse County (Douglas) page", URL_COURT_C)
SRC_SOS18J = S("Official Wyoming SOS 2018 General Election Winners Roster and official 2018 statewide judicial summary (Eighth Judicial District Circuit Court Judge Randal R. Arp)", "")


def sos_src(year, chamber):
    return S(f"Official Wyoming SOS {year} statewide {chamber} candidates summary (district-wide Total row)", "")


def T(**kw):
    kw.setdefault("confidence", "high")
    kw.setdefault("how_took_office", "elected")
    if "sources" not in kw:
        kw["sources"] = []
    return term(**kw)


def register_people(P):
    P("WY-STEINMETZ-CHERI", "Cheri E. Steinmetz", "Cheri", "Steinmetz", middle="E.", aliases="Cheri Steinmetz|Cheri E Steinmetz|REP CHERI E STEINMETZ|REP CHERI STEINMETZ")
    P("WY-MEIER-CURT", "Curt Meier", "Curt", "Meier")
    P("WY-WILLIAMS-JD", "JD Williams", "JD", "Williams", aliases="REP JD WILLIAMS")
    P("WY-SPECKNER-JOE", "Joe Speckner", "Joe", "Speckner", aliases="REP JOE SPECKNER")
    P("WY-SMITH-SCOTT", "Scott Smith", "Scott", "Smith", aliases="REP SCOTT SMITH")
    P("WY-SLAGLE-ALLEN-EARL", "Allen Earl Slagle", "Allen Earl", "Slagle", aliases="Allen Earl Slagle|REP ALLEN EARL SLAGLE")
    P("WY-HUNT-HANS", "Hans Hunt", "Hans", "Hunt")
    P("WY-DUNCAN-SHELLY", "Shelly Duncan", "Shelly", "Duncan", aliases="SHELLY DUNCAN")
    P("WY-SIGLIN-GEORGE", "George Siglin", "George", "Siglin", aliases="George Siglin, Jr.|George Siglin Jr.|Mayor Siglin")
    P("WY-WILHELM-KATHERINE-LYNN", "Katherine Lynn Wilhelm", "Katherine", "Wilhelm", middle="Lynn", aliases="Kathy Wilhelm|Katherine Wilhelm")
    P("WY-WATSON-DELWIN", "Delwin Watson", "Delwin", "Watson", aliases="Del Watson")
    P("WY-INGRAM-BRIAN", "Brian Ingram", "Brian", "Ingram")
    P("WY-JEROME-JEFF", "Jeff Jerome", "Jeff", "Jerome")
    P("WY-BROWN-RYON", "Ryon Brown", "Ryon", "Brown", aliases="Mayor Brown")
    P("WY-CURTSINGER-JASON", "Jason Curtsinger", "Jason", "Curtsinger")
    P("WY-SACHANANDANI-CHRIS", "Chris Sachanandani", "Chris", "Sachanandani")
    P("WY-TANNER-ALICIA", "Alicia Tanner", "Alicia", "Tanner")
    P("WY-ELLIS-JACOB", "Jacob Ellis", "Jacob", "Ellis")
    P("WY-HAAS-KIRK", "Kirk Haas", "Kirk", "Haas", aliases="Kirk C Haas|Kirk C. Haas")
    P("WY-HUSEBY-MICHAEL", "Michael Huseby", "Michael", "Huseby", aliases="Mike Huseby")
    P("WY-PRAGNELL-JENNIFER", "Jennifer Pragnell", "Jennifer", "Pragnell", aliases="Jenny Pragnell")
    P("WY-MAY-TERESA-TRACY", 'Teresa "Tracy" May', "Teresa", "May", aliases="Tracy May|Teresa May")
    P("WY-GOOLD-JOHN", "John Goold", "John", "Goold")
    P("WY-EKLUND-JOHN", "John Eklund", "John", "Eklund")
    # County
    P("WY-MCNAMEE-MICHAEL", "Michael McNamee", "Michael", "McNamee", aliases="Michael Mc Namee|MICHAEL MC NAMEE|REP MICHAEL MC NAMEE")
    P("WY-WALSH-AARON-P", "Aaron P. Walsh", "Aaron", "Walsh", middle="P.", aliases="Aaron P Walsh|REP AARON P WALSH|REP AARON P. WALSH")
    P("WY-BURKART-JUSTIN-L", "Justin L. Burkart", "Justin", "Burkart", middle="L.", aliases="Justin Burkart|JUSTIN L BURKART|REP JUSTIN L BURKART|REP JUSTIN BURKART")
    P("WY-ANDERSON-BRENT-L", "Brent L. Anderson", "Brent", "Anderson", middle="L.", aliases="Brent L Anderson|REP BRENT L ANDERSON")
    P("WY-COX-CODY", "Cody Cox", "Cody", "Cox")
    P("WY-ELLIS-JOHN", "John Ellis", "John", "Ellis")
    P("WY-FEAGLER-MARY-B", "Mary B. Feagler", "Mary", "Feagler", middle="B.", aliases="Mary B Feagler|MARY B FEAGLER|REP MARY B FEAGLER|MARY B. FEAGLER")
    P("WY-KENYON-CINDY", "Cindy Kenyon", "Cindy", "Kenyon")
    P("WY-DOMINGUEZ-LETICIA", "Leticia Dominguez", "Leticia", "Dominguez")
    P("WY-SURRATT-DEBRA-A", "Debra A. Surratt", "Debra", "Surratt", middle="A.", aliases="Debbi Surratt|Debra A Surratt|DEBRA A. SURRATT")
    P("WY-WARDELL-JEREMY", "Jeremy Wardell", "Jeremy", "Wardell")
    P("WY-FLEENOR-KORY", "Kory Fleenor", "Kory", "Fleenor")
    P("WY-IRONS-HERB", "Herb Irons", "Herb", "Irons")
    P("WY-BOYER-ERIC-R", "Eric R. Boyer", "Eric", "Boyer", middle="R.", aliases="Eric R Boyer|ERIC R BOYER|ERIC R. BOYER")
    P("WY-YATES-DARIN-R", "Darin R. Yates", "Darin", "Yates", middle="R.", aliases="Darin R Yates|DARIN R YATES|DARIN R. YATES")
    P("WY-CORREA-BRANDI", "Brandi Correa", "Brandi", "Correa")
    P("WY-RICKARD-KATHI", "Kathi Rickard", "Kathi", "Rickard")
    # Municipal
    P("WY-DOBY-HERB", "Herb Doby", "Herb", "Doby")
    P("WY-ADAMS-RANDY-L", "Randy L. Adams", "Randy", "Adams", middle="L.", aliases="Randy L Adams|RANDY L. ADAMS")
    P("WY-VIKTORIN-SHANE", "Shane Viktorin", "Shane", "Viktorin")
    P("WY-DEAHL-WAYNE-G", "Wayne G. Deahl", "Wayne", "Deahl", middle="G.", aliases="Wayne G Deahl|Wayne Deahl|WAYNE G DEAHL|WAYNE G. DEAHL")
    P("WY-KELLY-DENNIS", "Dennis Kelly", "Dennis", "Kelly")
    P("WY-WARREN-RICHARD", "Richard Warren", "Richard", "Warren", aliases="Rick Warren|RICHARD WARREN")
    P("WY-KINNEY-TED", "Ted Kinney", "Ted", "Kinney")
    P("WY-HILL-DEANNA", "Deanna Hill", "Deanna", "Hill")
    P("WY-PATTERSON-RICHARD-RICK", 'Richard "Rick" Patterson', "Richard", "Patterson", aliases="Rick Patterson")
    # Schools / college / specials
    P("WY-ZIMMERMAN-STEVE", "Steve Zimmerman", "Steve", "Zimmerman")
    P("WY-CHAIRES-SARAH", "Sarah Chaires", "Sarah", "Chaires")
    P("WY-GROSZ-TRAVIS", "Travis Grosz", "Travis", "Grosz")
    P("WY-KASPERBAUER-PETER", "Peter Kasperbauer", "Peter", "Kasperbauer")
    P("WY-PHIPPS-WADE", "Wade Phipps", "Wade", "Phipps")
    P("WY-ALEXANDER-CHRIS", "Chris Alexander", "Chris", "Alexander")
    P("WY-PETERSON-BOB", "Bob Peterson", "Bob", "Peterson")
    P("WY-HURLEY-JUSTIN", "Justin Hurley", "Justin", "Hurley")
    P("WY-STEINBOCK-KATE", "Kate Steinbock", "Kate", "Steinbock")
    P("WY-STRAMPE-KELLY-MEEBOER", "Kelly Meeboer Strampe", "Kelly", "Strampe", aliases="KELLY MEEBOER STRAMPE")
    P("WY-GOULART-TONY", "Tony Goulart", "Tony", "Goulart")
    P("WY-SHARP-VALERIE-LAMB", "Valerie Lamb Sharp", "Valerie", "Sharp", aliases="VALERIE LAMB SHARP")
    P("WY-MOELLER-LENA", "Lena Moeller", "Lena", "Moeller")
    P("WY-HAGER-DYLAN", "Dylan Hager", "Dylan", "Hager")
    P("WY-VONBURG-RICK", "Rick VonBurg", "Rick", "VonBurg", aliases="RICK VONBURG")
    P("WY-VANMARK-JACKIE", "Jackie VanMark", "Jackie", "VanMark", aliases="Jackie Van Mark|JACKIE VANMARK|JACKIE VAN MARK")
    P("WY-EBERT-H-TERRY", "H. Terry Ebert", "H. Terry", "Ebert", aliases="H TERRY EBERT|H. Terry Ebert")
    P("WY-NEWMAN-JULIA-H", "Julia H. Newman", "Julia", "Newman", middle="H.", aliases="JULIA H NEWMAN")
    P("WY-BAUMGARTNER-ROBERT", "Robert Baumgartner", "Robert", "Baumgartner")
    P("WY-PATRICK-KATHERINE", "Katherine Patrick", "Katherine", "Patrick")
    P("WY-SITTNER-KURT", "Kurt Sittner", "Kurt", "Sittner")
    P("WY-MERCER-DOUGLAS-R", "Douglas R. Mercer", "Douglas", "Mercer", middle="R.", aliases="Douglas R Mercer")
    P("WY-TEETERS-MATT", "Matt Teeters", "Matt", "Teeters")
    P("WY-MCDOWELL-DONALD-A", "Donald A. McDowell", "Donald", "McDowell", middle="A.", aliases="Donald A McDowell|DONALD A MCDOWELL|DONALD A. MC DOWELL")
    P("WY-KELLER-DUANE", "Duane Keller", "Duane", "Keller")
    P("WY-BANGERTER-KASEY", "Kasey Bangerter", "Kasey", "Bangerter")
    P("WY-ROSS-SCOTT-D", "Scott D. Ross", "Scott", "Ross", middle="D.", aliases="Scott D Ross|SCOTT D ROSS")
    P("WY-JACKSON-CRAIG", "Craig Jackson", "Craig", "Jackson")
    P("WY-NICHOL-LINDA", "Linda Nichol", "Linda", "Nichol")
    P("WY-JOHNSON-DAVID", "David Johnson", "David", "Johnson")
    P("WY-MEEKS-JENNA", "Jenna Meeks", "Jenna", "Meeks")
    P("WY-MOORE-LUCAS", "Lucas Moore", "Lucas", "Moore")
    P("WY-EISENBARTH-ANDREA", "Andrea Eisenbarth", "Andrea", "Eisenbarth")
    P("WY-BAUMGARDNER-ENOCH", "Enoch Baumgardner", "Enoch", "Baumgardner")
    P("WY-BARTLETT-DAVE", "Dave Bartlett", "Dave", "Bartlett")
    P("WY-SCHEER-JENNIFER", "Jennifer Scheer", "Jennifer", "Scheer")
    P("WY-GRANDSTAFF-CURTIS-G", "Curtis G. Grandstaff", "Curtis", "Grandstaff", middle="G.", aliases="Curtis G Grandstaff|CURTIS G GRANDSTAFF")
    P("WY-RIFE-KONNE", "Konne Rife", "Konne", "Rife")
    P("WY-LOWRY-MICHAEL", "Michael Lowry", "Michael", "Lowry")
    P("WY-JOY-MARDELL", "Mardell (Mardy) Joy", "Mardell", "Joy", aliases="Mardy Joy|MARDELL (MARDY) JOY")
    P("WY-MORGHEIM-MERRIJANE", "Merrijane Morgheim", "Merrijane", "Morgheim")
    P("WY-JOHNSON-THOMAS-A", "Thomas A. Johnson", "Thomas", "Johnson", middle="A.", aliases="Thomas A Johnson|THOMAS A JOHNSON")
    P("WY-VAUGHN-BLAKE", "Blake Vaughn", "Blake", "Vaughn")
    P("WY-VAUGHN-TRACY", "Tracy Vaughn", "Tracy", "Vaughn")
    P("WY-JACKSON-KATE", "Kate Jackson", "Kate", "Jackson")
    P("WY-TETER-DARLA", "Darla Teter", "Darla", "Teter")
    P("WY-ASH-TIM", "Tim Ash", "Tim", "Ash")
    P("WY-CROWLEY-HOLLY", "Holly Crowley", "Holly", "Crowley")
    P("WY-VAUGHN-RUTH", "Ruth Vaughn", "Ruth", "Vaughn")
    P("WY-WEBSTER-DEAN", "Dean Webster", "Dean", "Webster")
    P("WY-KELLEY-MICHAEL-L", "Michael L. Kelley", "Michael", "Kelley", middle="L.")
    # Judicial
    P("WY-PEASLEY-F-SCOTT", "F. Scott Peasley", "F. Scott", "Peasley", aliases="Hon. F. Scott Peasley")
    P("WY-BUCHANAN-EDWARD-A", "Edward A. Buchanan", "Edward", "Buchanan", middle="A.", aliases="Hon. Edward A. Buchanan")
    P("WY-KORELL-PATRICK-W", "Patrick W. Korell", "Patrick", "Korell", middle="W.", aliases="A. Patrick W. Korell|A Patrick W. Korell|Judge A Patrick W. Korell")
    P("WY-ALLAN-CLARK-C", "Clark C. Allan", "Clark", "Allan", middle="C.", aliases="Hon. Clark C. Allan|CLARK C ALLAN|CLARK C. ALLAN")
    P("WY-HIBBEN-NATHANIEL-S", "Nathaniel S. Hibben", "Nathaniel", "Hibben", middle="S.", aliases="Nathaniel Hibben|HIBBEN")
    P("WY-BROWN-JACQUELINE-K", "Jacqueline K. Brown", "Jacqueline", "Brown", middle="K.", aliases="Hon. Jacqueline K. Brown|JACQUELINE K BROWN|JACQUELINE K. BROWN")
    P("WY-ARP-RANDAL-R", "Randal R. Arp", "Randal", "Arp", middle="R.", aliases="Randal Arp|JUDGE ARP")


def legislature_terms():
    terms = []
    s03 = [
        (2014, "WY-MEIER-CURT", "Curt Meier", "REP",
         "Official 2014 SOS statewide Senate summary Total: Curt Meier (R) 5,743. Official Goshen portion: 3,579. Official Niobrara share: 931. Official Weston share: 1,233.",
         [sos_src(2014, "Senate")]),
        (2018, "WY-STEINMETZ-CHERI", "Cheri E. Steinmetz", "REP",
         "Official 2018 SOS statewide Senate summary, Senate District 3 county rows (do not use the two-column Total, which also prints Senate District 1): Cheri E. Steinmetz (R) 5,721, Marci Shaver (D) 1,449. Official Goshen portion: Steinmetz 3,447, Shaver 1,086 (matches official Goshen clerk). Official Niobrara share: 1,001–129. Official Weston share: 1,273–234.",
         [sos_src(2018, "Senate"), SRC_C18]),
        (2022, "WY-STEINMETZ-CHERI", "Cheri E. Steinmetz", "REP",
         "Official 2022 SOS statewide Senate summary Total: Cheri Steinmetz (R) 6,352. Official Goshen portion: 4,017 (matches official Goshen clerk). Official Niobrara share: 973. Official Weston share: 1,362.",
         [sos_src(2022, "Senate"), SRC_C22]),
        (2026, "WY-STEINMETZ-CHERI", "Cheri E. Steinmetz", "REP",
         "Official 2026 SOS statewide Senate summary Total: Cheri E. Steinmetz (R) 5,792. Official Goshen portion: 3,777 (matches official Goshen clerk). Official Niobrara share: 808. Official Weston share: 1,207.",
         [sos_src(2026, "Senate"), SRC_C26]),
    ]
    for year, pid, name, party, note, srcs in s03:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-senate",
                       office="Senate District 3 (S03)", term_start=FM[year + 1], term_end=FM[year + 5],
                       election_year=year, sources=srcs, notes=note))

    h02 = [
        (2014, "WY-HUNT-HANS", "Hans Hunt", "REP",
         "Official 2014 SOS statewide House summary Total: Hans Hunt (R) 2,985. Official Goshen portion: 718. Official Niobrara share: 971. Official Weston share: 1,296.",
         [sos_src(2014, "House")]),
        (2016, "WY-HUNT-HANS", "Hans Hunt", "REP",
         "Official 2016 SOS statewide House summary, House District 2 county rows (do not use the two-column Total, which also prints House District 1): Hans Hunt (R) 3,863, Harold Eaton (D) 624. Official Goshen portion: Hunt 880, Eaton 262. Official Niobrara share: 1,191–104. Official Weston share: 1,792–258.",
         [sos_src(2016, "House")]),
        (2018, "WY-HUNT-HANS", "Hans Hunt", "REP",
         "Official 2018 SOS statewide House summary, House District 2 county rows (do not use the two-column Total, which also prints House District 1): Hans Hunt (R) 3,261. Official Goshen portion: 846 (matches official Goshen clerk). Official Niobrara share: 1,101. Official Weston share: 1,314.",
         [sos_src(2018, "House"), SRC_C18]),
        (2020, "WY-HUNT-HANS", "Hans Hunt", "REP",
         "Official 2020 SOS statewide House summary, House District 2 county rows (do not use the two-column Total, which also prints House District 1): Hans Hunt (R) 4,121. Official Goshen portion: 1,106. Official Niobrara share: 1,226. Official Weston share: 1,789.",
         [sos_src(2020, "House")]),
        (2022, "WY-SLAGLE-ALLEN-EARL", "Allen Earl Slagle", "REP",
         "Official 2022 SOS statewide House summary Total: Allen Earl Slagle (R) 2,927. Official Goshen portion: 932 (matches official Goshen clerk). Official Niobrara share: 670. Official Weston share: 1,325.",
         [sos_src(2022, "House"), SRC_C22]),
        (2024, "WY-WILLIAMS-JD", "JD Williams", "REP",
         "Official 2024 SOS statewide House summary Total: JD Williams (R) 3,834. Official Goshen portion: 1,125 (matches official Goshen clerk). Official Niobrara share: 1,047. Official Weston share: 1,662.",
         [sos_src(2024, "House"), SRC_C24]),
        (2026, "WY-WILLIAMS-JD", "JD Williams", "REP",
         "Official 2026 SOS statewide House summary Total: JD Williams (R) 2,850. Official Goshen portion: 839 (matches official Goshen clerk). Official Niobrara share: 803. Official Weston share: 1,208.",
         [sos_src(2026, "House"), SRC_C26]),
    ]
    for year, pid, name, party, note, srcs in h02:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-house",
                       office="House District 2 (H02)", term_start=FM[year + 1], term_end=FM[year + 3],
                       election_year=year, sources=srcs, notes=note))

    h05 = [
        (2014, "WY-STEINMETZ-CHERI", "Cheri E. Steinmetz", "REP",
         "Official 2014 SOS statewide House summary Total: Cheri Steinmetz (R) 2,776, all in Goshen (official SOS Total equals the official Goshen row).",
         [sos_src(2014, "House")]),
        (2016, "WY-STEINMETZ-CHERI", "Cheri E. Steinmetz", "REP",
         "Official 2016 SOS statewide House summary, House District 5 county rows (do not use the two-column Total, which also prints House District 6): Cheri E. Steinmetz (R) 3,798, all in Goshen.",
         [sos_src(2016, "House")]),
        (2018, "WY-DUNCAN-SHELLY", "Shelly Duncan", "REP",
         "Official 2018 SOS statewide House summary, House District 5 county rows (do not use the two-column Total, which also prints House District 6): Shelly Duncan (R) 2,760, Joan Brinkley (D) 798, all in Goshen (matches official Goshen clerk).",
         [sos_src(2018, "House"), SRC_C18]),
        (2020, "WY-DUNCAN-SHELLY", "Shelly Duncan", "REP",
         "Official 2020 SOS statewide House summary, House District 5 county rows (do not use the two-column Total, which also prints House District 6): Shelly Duncan (R) 4,122, all in Goshen.",
         [sos_src(2020, "House")]),
        (2022, "WY-SMITH-SCOTT", "Scott Smith", "REP",
         "Official 2022 SOS statewide House summary Total: Scott Smith (R) 2,195, Todd Peterson (I) 1,603, all in Goshen (official SOS Total equals the official Goshen clerk).",
         [sos_src(2022, "House"), SRC_C22]),
        (2024, "WY-SMITH-SCOTT", "Scott Smith", "REP",
         "Official 2024 SOS statewide House summary Total: Scott Smith (R) 3,893, all in Goshen (official SOS Total equals the official Goshen clerk).",
         [sos_src(2024, "House"), SRC_C24]),
        (2026, "WY-SPECKNER-JOE", "Joe Speckner", "REP",
         "Official 2026 SOS statewide House summary Total: Joe Speckner (R) 3,226, all in Goshen (official SOS Total equals the official Goshen clerk).",
         [sos_src(2026, "House"), SRC_C26]),
    ]
    for year, pid, name, party, note, srcs in h05:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-house",
                       office="House District 5 (H05)", term_start=FM[year + 1], term_end=FM[year + 3],
                       election_year=year, sources=srcs, notes=note))

    # Official SOS shows a Goshen sliver of House District 10 (with Laramie) in 2014–2020 only; official 2022+ Goshen rows are blank.
    h10 = [
        (2014, "WY-EKLUND-JOHN", "John Eklund", "REP",
         "Official 2014 SOS statewide House summary Total: John Eklund (R) 2,282, Gaylan D. Wright Sr. (D) 774. Official Goshen portion: Eklund 138, Wright 17. Official Laramie share: 2,144–757.",
         [sos_src(2014, "House")]),
        (2016, "WY-EKLUND-JOHN", "John Eklund", "REP",
         "Official 2016 SOS statewide House summary, House District 10 county rows (do not use the two-column Total, which also prints House District 9): John Eklund (R) 4,187, Matthew Porras (D) 846. Official Goshen portion: Eklund 193, Porras 13. Official Laramie share: 3,994–833.",
         [sos_src(2016, "House")]),
        (2018, "WY-EKLUND-JOHN", "John Eklund", "REP",
         "Official 2018 SOS statewide House summary, House District 10 county rows (do not use the two-column Total, which also prints House District 9): John Eklund (R) 3,332, Jenefer Pasqua (D) 825. Official Goshen portion: Eklund 145, Pasqua 11 (matches official Goshen clerk). Official Laramie share: 3,187–814.",
         [sos_src(2018, "House"), SRC_C18]),
        (2020, "WY-EKLUND-JOHN", "John Eklund", "REP",
         "Official 2020 SOS statewide House summary, House District 10 county rows (do not use the two-column Total, which also prints House District 9): John Eklund (R) 5,565. Official Goshen portion: 205. Official Laramie share: 5,360.",
         [sos_src(2020, "House")]),
    ]
    for year, pid, name, party, note, srcs in h10:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-house",
                       office="House District 10 (H10)", term_start=FM[year + 1], term_end=FM[year + 3],
                       election_year=year, sources=srcs, notes=note))
    return terms


def county_terms():
    terms = []
    # Three commissioners, staggered. Official 2018 Vote-For-2, official 2020 Vote-For-1, official 2022 Vote-For-2, official 2024 Vote-For-1, official 2026 Vote-For-2.
    terms += [
        T(person_id="WY-ELLIS-JOHN", name="John Ellis", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Goshen clerk, Commission: John Ellis 3,675, Cody Cox 3,461."),
        T(person_id="WY-COX-CODY", name="Cody Cox", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Goshen clerk, Commission: John Ellis 3,675, Cody Cox 3,461."),
        T(person_id="WY-BURKART-JUSTIN-L", name="Justin L. Burkart", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2021], term_end=FM[2025], election_year=2020,
          sources=[SRC_C20], notes="Official 2020 Goshen clerk, Commissioner Vote-For-1: Justin Burkart 5,419."),
        T(person_id="WY-MCNAMEE-MICHAEL", name="Michael McNamee", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22, SRC_COMM], notes="Official 2022 Goshen clerk, Commissioner Vote-For-2: Michael Mc Namee 4,027, Aaron P. Walsh 3,480. Official commissioners page lists Michael McNamee as Chairman."),
        T(person_id="WY-WALSH-AARON-P", name="Aaron P. Walsh", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Goshen clerk, Commissioner Vote-For-2: Michael Mc Namee 4,027, Aaron P. Walsh 3,480."),
        T(person_id="WY-BURKART-JUSTIN-L", name="Justin L. Burkart", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2025], term_end=FM[2029], election_year=2024,
          sources=[SRC_C24, SRC_COMM], notes="Official 2024 Goshen clerk, Commissioner Vote-For-1: Justin L Burkart 5,282. Official commissioners page lists Justin Burkart as Vice Chairman."),
        T(person_id="WY-WALSH-AARON-P", name="Aaron P. Walsh", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Goshen clerk, Commissioner Vote-For-2: Aaron P Walsh 3,420, Brent L Anderson 3,071."),
        T(person_id="WY-ANDERSON-BRENT-L", name="Brent L. Anderson", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Goshen clerk, Commissioner Vote-For-2: Aaron P Walsh 3,420, Brent L Anderson 3,071."),
    ]
    terms += [
        T(person_id="WY-KENYON-CINDY", name="Cindy Kenyon", party="REP", office_group="county",
          office="County Clerk", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Goshen clerk: Cindy Kenyon 4,314."),
        T(person_id="WY-FEAGLER-MARY-B", name="Mary B. Feagler", party="REP", office_group="county",
          office="County Clerk", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Goshen clerk: Mary B. Feagler 4,560."),
        T(person_id="WY-FEAGLER-MARY-B", name="Mary B. Feagler", party="REP", office_group="county",
          office="County Clerk", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Goshen clerk: Mary B Feagler 3,961."),
        T(person_id="WY-DOMINGUEZ-LETICIA", name="Leticia Dominguez", party="REP", office_group="county",
          office="County Treasurer", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Goshen clerk: Leticia Dominguez 4,293."),
        T(person_id="WY-DOMINGUEZ-LETICIA", name="Leticia Dominguez", party="REP", office_group="county",
          office="County Treasurer", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Goshen clerk: Leticia Dominguez 4,538."),
        T(person_id="WY-DOMINGUEZ-LETICIA", name="Leticia Dominguez", party="REP", office_group="county",
          office="County Treasurer", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Goshen clerk: Leticia Dominguez 4,127."),
        T(person_id="WY-SURRATT-DEBRA-A", name="Debra A. Surratt", party="REP", office_group="county",
          office="County Assessor", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Goshen clerk: Debra A. Surratt 4,414."),
        T(person_id="WY-SURRATT-DEBRA-A", name="Debra A. Surratt", party="REP", office_group="county",
          office="County Assessor", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Goshen clerk: Debra A. Surratt 4,483. Phase-1 display Debbi Surratt is treated as the same person (alias)."),
        T(person_id="WY-WARDELL-JEREMY", name="Jeremy Wardell", party="REP", office_group="county",
          office="County Assessor", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Goshen clerk: Jeremy Wardell 4,022."),
        T(person_id="WY-FLEENOR-KORY", name="Kory Fleenor", party="REP", office_group="county",
          office="County Sheriff", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Goshen clerk: Kory Fleenor 4,260."),
        T(person_id="WY-FLEENOR-KORY", name="Kory Fleenor", party="REP", office_group="county",
          office="County Sheriff", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Goshen clerk: Kory Fleenor 4,383."),
        T(person_id="WY-IRONS-HERB", name="Herb Irons", party="REP", office_group="county",
          office="County Sheriff", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Goshen clerk: Herb Irons 3,871, Diane Servantez 512."),
        T(person_id="WY-BOYER-ERIC-R", name="Eric R. Boyer", party="REP", office_group="county",
          office="County Attorney", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Goshen clerk: Eric R. Boyer 4,218."),
        T(person_id="WY-BOYER-ERIC-R", name="Eric R. Boyer", party="REP", office_group="county",
          office="County Attorney", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Goshen clerk: Eric R. Boyer 4,391."),
        T(person_id="WY-BOYER-ERIC-R", name="Eric R. Boyer", party="REP", office_group="county",
          office="County Attorney", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Goshen clerk: Eric R Boyer 3,902."),
        T(person_id="WY-YATES-DARIN-R", name="Darin R. Yates", party="REP", office_group="county",
          office="County Coroner", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Goshen clerk: Darin R. Yates 4,435."),
        T(person_id="WY-YATES-DARIN-R", name="Darin R. Yates", party="REP", office_group="county",
          office="County Coroner", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Goshen clerk: Darin R. Yates 4,600."),
        T(person_id="WY-YATES-DARIN-R", name="Darin R. Yates", party="REP", office_group="county",
          office="County Coroner", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Goshen clerk: Darin R Yates 4,161."),
        T(person_id="WY-RICKARD-KATHI", name="Kathi Rickard", party="REP", office_group="county",
          office="Clerk of District Court", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Goshen clerk, Clerk Court: Kathi Rickard 4,291."),
        T(person_id="WY-CORREA-BRANDI", name="Brandi Correa", party="REP", office_group="county",
          office="Clerk of District Court", term_start=FM[2021], term_end=FM[2023], election_year=2020,
          sources=[SRC_C20], notes="Official 2020 Goshen clerk, Clerk District Court: Brandi Correa 5,743. Official 2022 starts a new four-year term in January 2023."),
        T(person_id="WY-CORREA-BRANDI", name="Brandi Correa", party="REP", office_group="county",
          office="Clerk of District Court", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Goshen clerk: Brandi Correa 4,551."),
        T(person_id="WY-CORREA-BRANDI", name="Brandi Correa", party="REP", office_group="county",
          office="Clerk of District Court", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Goshen clerk: Brandi Correa 4,148."),
    ]
    return terms


def judicial_terms():
    terms = []
    terms += [
        T(person_id="WY-KORELL-PATRICK-W", name="Patrick W. Korell", party="", office_group="judicial",
          office="District Judge, 8th Judicial District", term_start="2015-10-01", term_end="2022-09-01",
          election_year=2016, how_took_office="appointed", confidence="medium",
          sources=[SRC_C16, SRC_COURT_D],
          notes="Official 2016 Goshen clerk has DISTRICT COURT JUDGE KORELL. Official SOS Judicial Branch directory lists Eighth Judicial District Judge A Patrick W. Korell, appointed October 2015. Official current 8th JD court pages list Edward A. Buchanan, appointed September 2022, in that district; Korell's last day is taken as the first of Buchanan's official appointment month (medium) rather than inventing a later date. Start day is the first of the official appointment month."),
        T(person_id="WY-PEASLEY-F-SCOTT", name="F. Scott Peasley", party="", office_group="judicial",
          office="District Judge, 8th Judicial District", term_start="2017-08-01", term_end=FM[2031],
          election_year=2024, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_D, SRC_C24],
          notes="Official Wyoming Judicial Branch 8th JD District Court page: Hon. F. Scott Peasley, appointed August 2017, retained November 2024, term expires January 2031. Official 2024 Goshen clerk JUDGE PEASLEY RETENTION: YES 4,451, NO 996. Official 2018 SOS winners roster lists F. Scott Peasley as Judge B of the District Court of the Eighth District. Start day is the first of the official appointment month."),
        T(person_id="WY-BUCHANAN-EDWARD-A", name="Edward A. Buchanan", party="", office_group="judicial",
          office="District Judge, 8th Judicial District", term_start="2022-09-01", term_end=FM[2031],
          election_year=2024, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_D, SRC_C24],
          notes="Official Wyoming Judicial Branch 8th JD District Court page: Hon. Edward A. Buchanan, appointed September 2022, retained November 2024, term expires January 2031. Official 2024 Goshen clerk JUDGE BUCHANAN RETENTION: YES 4,808, NO 895. Start day is the first of the official appointment month."),
        T(person_id="WY-ARP-RANDAL-R", name="Randal R. Arp", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2015], term_end=FM[2019],
          election_year=2014, sources=[SRC_SOS18J],
          notes="Official 2014 SOS General Election Winners Roster lists Eighth Judicial District Circuit Court Judge Randal R. Arp. Official SOS Judicial Branch directory: appointed January 2000. January 2015 is the start of the term following that official 2014 retention; the official appointment date before 2014 is not used to invent earlier snapshot rows here."),
        T(person_id="WY-ARP-RANDAL-R", name="Randal R. Arp", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2019], term_end=FM[2021],
          election_year=2018, sources=[SRC_C18, SRC_SOS18J], confidence="medium",
          notes="Official 2018 Goshen clerk JUDICIAL CC JUDGE ARP: YES 3,801, NO 692. Official SOS 2018 statewide judicial summary and official 2018 General Election Winners Roster name Eighth Judicial District Circuit Court Judge Randal R. Arp. Official 2020 Goshen clerk retains Nathaniel S. Hibben and does not name Arp; later official court pages do not list Arp. The exact official leaving date was not taken from an official court page, so this term is ended at January 2021 when the official 2020 Hibben retention is in effect (medium)."),
        T(person_id="WY-HIBBEN-NATHANIEL-S", name="Nathaniel S. Hibben", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2021], term_end="2025-05-10",
          election_year=2020, sources=[SRC_C20, SRC_C24],
          notes="Official 2020 Goshen clerk CIRCUIT CT JUDGE HIBBEN: YES 5,003, NO 756. Official 2024 Goshen clerk JUDGE HIBBEN RETENTION: YES 4,841, NO 773. Full name Nathaniel S. Hibben is from the official Wyoming Judicial Branch 1st JD page after his later appointment. Official Judicial Nominating Commission release announced the 8th JD Goshen circuit vacancy effective May 10, 2025."),
        T(person_id="WY-ALLAN-CLARK-C", name="Clark C. Allan", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start="2021-01-01", term_end=FM[2027],
          election_year=2022, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_C, SRC_C26],
          notes="Official Wyoming Judicial Branch 8th JD Converse (Douglas) Circuit Court page: Hon. Clark C. Allan, appointed January 2021, term expires January 2027, stands for retention November 2026. Official 2026 Goshen clerk CIRCUIT COURT JUDGE CLARK C ALLAN: YES 3,213, NO 773. Start day is the first of the official appointment month."),
        T(person_id="WY-ALLAN-CLARK-C", name="Clark C. Allan", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_COURT_C],
          notes="Official 2026 Goshen clerk CIRCUIT COURT JUDGE CLARK C ALLAN: YES 3,213, NO 773."),
        T(person_id="WY-BROWN-JACQUELINE-K", name="Jacqueline K. Brown", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start="2025-07-01", term_end=FM[2027],
          election_year=2026, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_G, SRC_C26],
          notes="Official Wyoming Judicial Branch 8th JD Goshen (Torrington) Circuit Court page: Hon. Jacqueline K. Brown, appointed July 2025, term expires January 2027, stands for retention November 2026. Official 2026 Goshen clerk CIRCUIT COURT JUDGE JACQUELINE K BROWN: YES 3,176, NO 858. Official Judicial Branch robing notice lists her as Circuit Court Judge of the 8th JD (Converse, Goshen, Niobrara, and Platte Counties). Start day is the first of the official appointment month."),
        T(person_id="WY-BROWN-JACQUELINE-K", name="Jacqueline K. Brown", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_COURT_G],
          notes="Official 2026 Goshen clerk CIRCUIT COURT JUDGE JACQUELINE K BROWN: YES 3,176, NO 858. Official 2026 Goshen clerk CHANCERY COURT JUDGE BEN BURNINGHAM is the statewide Chancery retention copied from the shared judicial terms, not a local 8th JD seat."),
    ]
    return terms


def municipal_terms():
    """Torrington mayor is elected on the official November ballot (official city Election Information page: 2026 mayoral seat, four-year term). Not council-chosen."""
    terms = []
    terms += [
        T(person_id="WY-ADAMS-RANDY-L", name="Randy L. Adams", party="", office_group="municipal",
          office="Torrington Mayor", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Goshen clerk, Mayor: Randy L. Adams 1,083, Dennis Kelly 739."),
        T(person_id="WY-DOBY-HERB", name="Herb Doby", party="", office_group="municipal",
          office="Torrington Mayor", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22, SRC_TORR], notes="Official 2022 Goshen clerk, Mayor City of Torrington: Herb Doby 1,136, Dennis A. Kelly 641. Official City of Torrington council page lists Herb Doby as Mayor."),
        T(person_id="WY-DOBY-HERB", name="Herb Doby", party="", office_group="municipal",
          office="Torrington Mayor", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26, SRC_TORR], notes="Official 2026 Goshen clerk, Mayor City of Torrington: Herb Doby 1,205, Bob Peterson 470. Official City of Torrington Election Information page lists the 2026 mayoral seat as a four-year elected office."),
        T(person_id="WY-KINNEY-TED", name="Ted Kinney", party="", office_group="municipal",
          office="Torrington Council", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Goshen clerk, Council Vote-For-2: Ted Kinney 1,135, Deanna Hill 850, Sandy Pittman 714, Douglas R. Mercer 574."),
        T(person_id="WY-HILL-DEANNA", name="Deanna Hill", party="", office_group="municipal",
          office="Torrington Council", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Goshen clerk, Council Vote-For-2: Ted Kinney 1,135, Deanna Hill 850."),
        T(person_id="WY-PATTERSON-RICHARD-RICK", name='Richard "Rick" Patterson', party="", office_group="municipal",
          office="Torrington Council", term_start=FM[2021], term_end=FM[2025], election_year=2020,
          sources=[SRC_C20], notes="Official 2020 Goshen clerk, City Council Torrington Vote-For-2: Richard \"Rick\" Patterson 1,576, Dennis Kelly 1,380, Eric Sharp 1,004."),
        T(person_id="WY-KELLY-DENNIS", name="Dennis Kelly", party="", office_group="municipal",
          office="Torrington Council", term_start=FM[2021], term_end=FM[2025], election_year=2020,
          sources=[SRC_C20], notes="Official 2020 Goshen clerk, City Council Torrington Vote-For-2: Richard \"Rick\" Patterson 1,576, Dennis Kelly 1,380."),
        T(person_id="WY-DEAHL-WAYNE-G", name="Wayne G. Deahl", party="", office_group="municipal",
          office="Torrington Council", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Goshen clerk, City Council City of Torrington Vote-For-2: Wayne G. Deahl 1,091, Shane Viktorin 1,006, Catherine \"Kate\" Steinbock 907."),
        T(person_id="WY-VIKTORIN-SHANE", name="Shane Viktorin", party="", office_group="municipal",
          office="Torrington Council", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Goshen clerk, City Council City of Torrington Vote-For-2: Wayne G. Deahl 1,091, Shane Viktorin 1,006."),
        T(person_id="WY-KELLY-DENNIS", name="Dennis Kelly", party="", office_group="municipal",
          office="Torrington Council", term_start=FM[2025], term_end=FM[2029], election_year=2024,
          sources=[SRC_C24], notes="Official 2024 Goshen clerk, City Council City of Torrington Vote-For-2: Dennis Kelly 1,796, Richard Warren 1,460."),
        T(person_id="WY-WARREN-RICHARD", name="Richard Warren", party="", office_group="municipal",
          office="Torrington Council", term_start=FM[2025], term_end=FM[2029], election_year=2024,
          sources=[SRC_C24, SRC_TORR], notes="Official 2024 Goshen clerk, City Council City of Torrington Vote-For-2: Dennis Kelly 1,796, Richard Warren 1,460. Official City of Torrington council page lists Rick Warren."),
        T(person_id="WY-VIKTORIN-SHANE", name="Shane Viktorin", party="", office_group="municipal",
          office="Torrington Council", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Goshen clerk, City Council City of Torrington Vote-For-2: Shane Viktorin 1,027, Wayne G Deahl 991, Jason Senteney 549, David Marquiss 297."),
        T(person_id="WY-DEAHL-WAYNE-G", name="Wayne G. Deahl", party="", office_group="municipal",
          office="Torrington Council", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Goshen clerk, City Council City of Torrington Vote-For-2: Shane Viktorin 1,027, Wayne G Deahl 991."),
        # Lingle (May even-year municipal election; not on the official county November canvass)
        T(person_id="WY-SIGLIN-GEORGE", name="George Siglin", party="", office_group="municipal",
          office="Lingle Mayor", term_start="2026-06-03", term_end="2030-06-03", election_year=2026,
          confidence="medium", sources=[SRC_LINGLE_2026, SRC_LINGLE_MIN_2026_05, SRC_LINGLE_COUNCIL, SRC_LINGLE_MIN_2026_10],
          notes="Official Town of Lingle official 2026 municipal results (canvassed May 6): Mayor George Siglin 41, Shelly Duncan 35, write-ins Brian Trout 2, Allen Unverzagt 1, Del Watson 1, Jenna Meeks 1. Official May 6, 2026 minutes name him George Siglin, Jr. and say the mayor will be installed June 3, 2026. Official council page and official October 7, 2026 minutes list Mayor George Siglin. Term length is not stated on those official pages; the June 3, 2026–June 3, 2030 end is a 4-year inference from the official even-year May mayoral election (medium on length only)."),
        T(person_id="WY-WILHELM-KATHERINE-LYNN", name="Katherine Lynn Wilhelm", party="", office_group="municipal",
          office="Lingle Council", term_start="2026-06-03", term_end="2030-06-03", election_year=2026,
          confidence="medium", sources=[SRC_LINGLE_2026, SRC_LINGLE_MIN_2026_05, SRC_LINGLE_COUNCIL, SRC_LINGLE_MIN_2026_10],
          notes="Official Town of Lingle official 2026 municipal results (canvassed May 6): Council Katherine Lynn Wilhelm 56, Delwin Watson 46, Bryan Kirk 45. Official May 6 minutes say Wilhelm and Watson will be installed June 3, 2026. Official council page lists Kathy Wilhelm, Council Member/Mayor Pro Tempore. Term length is not stated on the official results page; the 4-year end is inferred from the official even-year two-seat council election pattern (medium on length only)."),
        T(person_id="WY-WATSON-DELWIN", name="Delwin Watson", party="", office_group="municipal",
          office="Lingle Council", term_start="2026-06-03", term_end="2030-06-03", election_year=2026,
          confidence="medium", sources=[SRC_LINGLE_2026, SRC_LINGLE_MIN_2026_05, SRC_LINGLE_COUNCIL, SRC_LINGLE_MIN_2026_10],
          notes="Official Town of Lingle official 2026 municipal results (canvassed May 6): Delwin Watson 46. Official May 6 minutes: installed June 3, 2026. Official October 7, 2026 minutes roll call uses Del Watson. 4-year term end is inferred (medium on length only)."),
        T(person_id="WY-DUNCAN-SHELLY", name="Shelly Duncan", party="", office_group="municipal",
          office="Lingle Council", term_start="2024-06-05", term_end="2028-06-05", election_year=2024,
          confidence="medium", sources=[SRC_LINGLE_MIN_2024_05, SRC_LINGLE_MIN_2024_06, SRC_LINGLE_COUNCIL, SRC_LINGLE_MIN_2026_10],
          notes="Official Town of Lingle May 22, 2024 minutes: the May 14, 2024 municipal election had 64 ballots; Jeff Jerome and Shelly Duncan collected the most votes and were to be sworn June 5, 2024. Official June 5, 2024 minutes: oath administered to Jeff Jerome and Shelly Duncan. Official October 7, 2026 minutes and official council page still list Shelly Duncan. 4-year term end is inferred from the official even-year two-seat council pattern (medium on length only)."),
        T(person_id="WY-INGRAM-BRIAN", name="Brian Ingram", party="", office_group="municipal",
          office="Lingle Council", term_start="2026-05-06", term_end="2028-06-05", election_year=None,
          confidence="medium", how_took_office="unknown", sources=[SRC_LINGLE_MIN_2026_05, SRC_LINGLE_COUNCIL, SRC_LINGLE_MIN_2026_10],
          notes="Official Town of Lingle May 6, 2026 and October 7, 2026 minutes, and the official council page, name Brian Ingram as a sitting council member. The official 2024 winners were Jeff Jerome and Shelly Duncan; no official appointment minute for Ingram was found, so the start is the first official minutes used here that name him as council (May 6, 2026) and the end date is not confirmed (medium). He is not treated as a 2026 election winner (2 official write-in votes)."),
        T(person_id="WY-JEROME-JEFF", name="Jeff Jerome", party="", office_group="municipal",
          office="Lingle Council", term_start="2024-06-05", term_end="2026-05-06", election_year=2024,
          confidence="medium", sources=[SRC_LINGLE_MIN_2024_05, SRC_LINGLE_MIN_2024_06, SRC_LINGLE_MIN_2026_05],
          notes="Official Town of Lingle May 22 and June 5, 2024 minutes: elected May 14, 2024 and sworn June 5, 2024. He is not on the official May 6, 2026 roll call (Wilhelm, Ingram present; Lambert and Duncan absent). The exact official leaving date was not found; the term is ended at the May 6, 2026 minutes (medium) rather than invented later."),
        # Fort Laramie (May even-year municipal election; not on the official county November canvass)
        T(person_id="WY-BROWN-RYON", name="Ryon Brown", party="", office_group="municipal",
          office="Fort Laramie Mayor", term_start="2025-12-10", term_end="2028-06-01", election_year=None,
          confidence="medium", sources=[SRC_FL_MIN_2025_12, SRC_FL_MIN_2026_01, SRC_FL_MIN_2026_10_14, SRC_FL_MIN_2026_10_28, SRC_FL_CONTACT],
          notes="Official Town of Fort Laramie December 10, 2025, January 14, 2026, May 13, 2026, October 14, 2026, and October 28, 2026 regular minutes, and the official Contact us page, name Ryon Brown as Mayor. An official 2024 mayoral canvass was not found; the start is the first official minutes used here (he was already seated), and the June 1, 2028 end is inferred from the official even-year May election calendar (medium on start and length)."),
        T(person_id="WY-CURTSINGER-JASON", name="Jason Curtsinger", party="", office_group="municipal",
          office="Fort Laramie Council", term_start="2025-12-10", term_end="2028-06-01", election_year=None,
          confidence="medium", sources=[SRC_FL_MIN_2025_12, SRC_FL_MIN_2026_01, SRC_FL_MIN_2026_05_13, SRC_FL_MIN_2026_10_14, SRC_FL_CONTACT],
          notes="Official Fort Laramie December 10, 2025 through October 28, 2026 minutes roll calls, and the official Contact us page, name Jason Curtsinger as council. He was already seated before the official May 5, 2026 election for the two expiring seats. Term end June 1, 2028 is inferred from that official even-year cycle (medium on start and length)."),
        T(person_id="WY-SACHANANDANI-CHRIS", name="Chris Sachanandani", party="", office_group="municipal",
          office="Fort Laramie Council", term_start="2025-12-10", term_end="2028-06-01", election_year=None,
          confidence="medium", sources=[SRC_FL_MIN_2025_12, SRC_FL_MIN_2026_01, SRC_FL_MIN_2026_05_13, SRC_FL_MIN_2026_10_14, SRC_FL_MIN_2026_10_28, SRC_FL_CONTACT],
          notes="Official Fort Laramie December 10, 2025 through October 28, 2026 minutes roll calls, and the official Contact us page, name Chris Sachanandani as council. He was already seated before the official May 5, 2026 election for the two expiring seats. Term end June 1, 2028 is inferred (medium on start and length)."),
        T(person_id="WY-TANNER-ALICIA", name="Alicia Tanner", party="", office_group="municipal",
          office="Fort Laramie Council", term_start="2025-12-10", term_end="2026-05-13", election_year=None,
          confidence="medium", sources=[SRC_FL_MIN_2025_12, SRC_FL_MIN_2026_01, SRC_FL_MIN_2026_05_13],
          notes="Official Fort Laramie December 10, 2025 and January 14, 2026 minutes name Alicia Tanner as a sitting council member before the official May 5, 2026 election. Start is the first official minutes used here (medium)."),
        T(person_id="WY-TANNER-ALICIA", name="Alicia Tanner", party="", office_group="municipal",
          office="Fort Laramie Council", term_start="2026-05-13", term_end="2030-05-13", election_year=2026,
          confidence="high", sources=[SRC_FL_MIN_2026_05_13, SRC_FL_MIN_2026_10_14, SRC_FL_MIN_2026_10_28, SRC_FL_CONTACT],
          notes="Official Fort Laramie May 13, 2026 minutes: Alicia Tanner and Jacob Ellis were elected May 5, 2026 to the two term-expiring council seats; Tanner took the Oath of Office as a council member for a four-year term. Official October 14 and October 28, 2026 minutes still list Tanner."),
        T(person_id="WY-ELLIS-JACOB", name="Jacob Ellis", party="", office_group="municipal",
          office="Fort Laramie Council", term_start="2025-12-10", term_end="2026-05-27", election_year=None,
          confidence="medium", sources=[SRC_FL_MIN_2025_12, SRC_FL_MIN_2026_01, SRC_FL_MIN_2026_05_13],
          notes="Official Fort Laramie December 10, 2025 and January 14, 2026 minutes name Jacob Ellis as a sitting council member before the official May 5, 2026 election. Start is the first official minutes used here (medium)."),
        T(person_id="WY-ELLIS-JACOB", name="Jacob Ellis", party="", office_group="municipal",
          office="Fort Laramie Council", term_start="2026-05-27", term_end="2026-10-14", election_year=2026,
          confidence="medium", sources=[SRC_FL_MIN_2026_05_13, SRC_FL_MIN_2026_05_27, SRC_FL_MIN_2026_10_14, SRC_FL_MIN_2026_10_28],
          notes="Official Fort Laramie May 13, 2026 minutes: elected May 5, 2026 to a term-expiring seat; oath deferred. Official May 27, 2026 minutes: took the oath for a four-year term. Official October 14, 2026 minutes roll call does not include Ellis and records that Mayor Brown appointed Cody Powell to fill the vacant seat, with the oath at the next meeting. Official October 28, 2026 minutes say newly appointed CM Powell is scheduled to take the oath November 18, 2026. Powell is not seated here because that official oath had not been taken as of the last official minutes used (October 28). The exact official last day for Ellis was not stated; the term is ended at the October 14 vacancy minute (medium) rather than invented. Ellis is not a current holder."),
        # La Grange / official town spelling LaGrange (odd-year May municipal election)
        T(person_id="WY-HAAS-KIRK", name="Kirk Haas", party="", office_group="municipal",
          office="La Grange Mayor", term_start="2025-06-01", term_end="2029-06-01", election_year=2025,
          confidence="medium", sources=[SRC_LAGRANGE_GOV, SRC_LAGRANGE_WELCOME, SRC_LAGRANGE_MAY2026],
          notes="Official Town of LaGrange Government page: Mayor Kirk Haas, term 2029. Official Welcome Booklet (updated as of 11/26/25): Mayor (4 years) Kirk Haas 2029. Official May 2026 newsletter reprints the official April 9, 2026 minutes with Mayor Kirk Haas present. Official page: elections the 2nd Tuesday in May on odd years. Exact start and end days are not stated (medium on those days only); names and term years are official."),
        T(person_id="WY-HUSEBY-MICHAEL", name="Michael Huseby", party="", office_group="municipal",
          office="La Grange Council", term_start="2025-06-01", term_end="2027-06-01", election_year=2025,
          confidence="medium", sources=[SRC_LAGRANGE_GOV, SRC_LAGRANGE_WELCOME, SRC_LAGRANGE_MAY2026],
          notes="Official Town of LaGrange Government page: Michael Huseby, term 2027. Official Welcome Booklet: Council Member (2 years) Michael Huseby 2027. Official April 9, 2026 minutes: Mike Huseby present. Exact start and end days medium; name and term year official."),
        T(person_id="WY-PRAGNELL-JENNIFER", name="Jennifer Pragnell", party="", office_group="municipal",
          office="La Grange Council", term_start="2025-06-01", term_end="2027-06-01", election_year=2025,
          confidence="medium", sources=[SRC_LAGRANGE_GOV, SRC_LAGRANGE_WELCOME, SRC_LAGRANGE_MAY2026],
          notes="Official Town of LaGrange Government page: Jennifer Pragnell, term 2027. Official Welcome Booklet: Council Member (2 years) Jennifer Pragnell 2027. Official April 9, 2026 minutes: Jenny Pragnell present. Exact start and end days medium; name and term year official."),
        T(person_id="WY-MAY-TERESA-TRACY", name='Teresa "Tracy" May', party="", office_group="municipal",
          office="La Grange Council", term_start="2025-06-01", term_end="2029-06-01", election_year=2025,
          confidence="medium", sources=[SRC_LAGRANGE_GOV, SRC_LAGRANGE_WELCOME, SRC_LAGRANGE_MAY2026],
          notes="Official Town of LaGrange Government page: Teresa “Tracy” May, term 2029. Official Welcome Booklet: Council Member (4 years) Tracy May 2029. Official April 9, 2026 minutes: Tracy May present. Exact start and end days medium; name and term year official."),
        T(person_id="WY-GOOLD-JOHN", name="John Goold", party="", office_group="municipal",
          office="La Grange Council", term_start="2025-06-01", term_end="2029-06-01", election_year=2025,
          confidence="medium", sources=[SRC_LAGRANGE_GOV, SRC_LAGRANGE_WELCOME, SRC_LAGRANGE_MAY2026],
          notes="Official Town of LaGrange Government page: John Goold, term 2029. Official Welcome Booklet: Council Member (4 years) John Goold 2029. Official April 9, 2026 minutes: John Goold present. Exact start and end days medium; name and term year official."),
    ]
    return terms


def school_terms():
    terms = []
    # Official 2022 4-year and 2-year; official 2024 general and official 2024 recount; official 2026 recount page in the official general PDF.
    for pid, name, votes in (
        ("WY-PHIPPS-WADE", "Wade Phipps", "2,613"),
        ("WY-CHAIRES-SARAH", "Sarah Chaires", "2,502"),
        ("WY-ALEXANDER-CHRIS", "Chris Alexander", "2,266"),
        ("WY-PETERSON-BOB", "Bob Peterson", "2,168"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="schools",
                       office="Goshen County School District #1 Trustee", term_start=FM[2023], term_end=FM[2027],
                       election_year=2022, sources=[SRC_C22],
                       notes=f"Official 2022 Goshen clerk, GCSD #1 Trustee At-Large 4-year Vote-For-4: Wade Phipps 2,613, Sarah Chaires 2,502, Chris Alexander 2,266, Bob Peterson 2,168 (Jane Zulauf 1,654 was fifth). This row: {name} {votes}."))
    terms.append(T(person_id="WY-HURLEY-JUSTIN", name="Justin Hurley", party="", office_group="schools",
                   office="Goshen County School District #1 Trustee", term_start=FM[2023], term_end=FM[2025],
                   election_year=2022, sources=[SRC_C22],
                   notes="Official 2022 Goshen clerk, GCSD #1 Trustee At-Large 2-year Vote-For-1: Justin Hurley 3,969."))
    for pid, name, votes in (
        ("WY-STEINBOCK-KATE", "Kate Steinbock", "1,955"),
        ("WY-STRAMPE-KELLY-MEEBOER", "Kelly Meeboer Strampe", "1,893"),
        ("WY-GOULART-TONY", "Tony Goulart", "1,847"),
        ("WY-SHARP-VALERIE-LAMB", "Valerie Lamb Sharp", "1,817"),
        ("WY-MOELLER-LENA", "Lena Moeller", "1,816"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="schools",
                       office="Goshen County School District #1 Trustee", term_start=FM[2025], term_end=FM[2029],
                       election_year=2024, sources=[SRC_C24R, SRC_C24],
                       notes=f"Official 2024 Goshen school-district recount (ArchiveCenter Item 142), GCSD #1 Trustee At-Large Vote-For-5: Kate Steinbock 1,955, Kelly Meeboer Strampe 1,893, Tony Goulart 1,847, Valerie Lamb Sharp 1,817, Lena Moeller 1,816. Official general summary ranks are the same; recount totals are used. This row: {name} {votes}."))
    terms.append(T(person_id="WY-HAGER-DYLAN", name="Dylan Hager", party="", office_group="schools",
                   office="Goshen County School District #1 Trustee", term_start=FM[2025], term_end=FM[2027],
                   election_year=2024, sources=[SRC_C24], confidence="medium",
                   notes="Official 2024 Goshen clerk, GCSD #1 Trustee At-Large Vote-For-1: Dylan Hager 2,862, Jo Meininger 2,200. Official 2024 clerk did not print 2-year/4-year on this contest; 2-year term follows the official 2022 2-year GCSD pattern."))
    for pid, name, votes in (
        ("WY-ZIMMERMAN-STEVE", "Steve Zimmerman", "2,843"),
        ("WY-CHAIRES-SARAH", "Sarah Chaires", "2,281"),
        ("WY-GROSZ-TRAVIS", "Travis Grosz", "2,183"),
        ("WY-KASPERBAUER-PETER", "Peter Kasperbauer", "1,592"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="schools",
                       office="Goshen County School District #1 Trustee", term_start=FM[2027], term_end=FM[2031],
                       election_year=2026, sources=[SRC_C26],
                       notes=f"Official 2026 Goshen clerk recount page in the official general PDF, GCSD #1 Trustee At-Large Vote-For-4: Steve Zimmerman 2,843, Sarah Chaires 2,281, Travis Grosz 2,183, Peter Kasperbauer 1,592 (Jeremy Closs 1,586 was fifth). This row: {name} {votes}."))
    return terms


def special_terms():
    terms = []
    # Eastern Wyoming College
    for pid, name, votes in (
        ("WY-VONBURG-RICK", "Rick VonBurg", "3,338"),
        ("WY-VANMARK-JACKIE", "Jackie VanMark", "3,327"),
        ("WY-MERCER-DOUGLAS-R", "Douglas R. Mercer", "2,980"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="special-districts",
                       office="Eastern Wyoming College Trustee", term_start=FM[2023], term_end=FM[2027],
                       election_year=2022, sources=[SRC_C22],
                       notes=f"Official 2022 Goshen clerk, EWC Trustee At-Large 4-year Vote-For-3: Rick VonBurg 3,338, Jackie Van Mark 3,327, Douglas R. Mercer 2,980. This row: {name} {votes}."))
    terms.append(T(person_id="WY-PATRICK-KATHERINE", name="Katherine Patrick", party="", office_group="special-districts",
                   office="Eastern Wyoming College Trustee", term_start=FM[2023], term_end=FM[2025],
                   election_year=2022, sources=[SRC_C22],
                   notes="Official 2022 Goshen clerk, EWC Trustee At-Large 2-year Vote-For-1: Katherine Patrick 3,687."))
    for pid, name, votes in (
        ("WY-SITTNER-KURT", "Kurt Sittner", "3,902"),
        ("WY-BAUMGARTNER-ROBERT", "Robert Baumgartner", "3,851"),
        ("WY-ADAMS-RANDY-L", "Randy L. Adams", "3,710"),
        ("WY-PATRICK-KATHERINE", "Katherine Patrick", "3,583"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="special-districts",
                       office="Eastern Wyoming College Trustee", term_start=FM[2025], term_end=FM[2029],
                       election_year=2024, sources=[SRC_C24],
                       notes=f"Official 2024 Goshen clerk, Eastern Wyoming College Trustee Vote-For-4: Kurt Sittner 3,902, Robert Baumgartner 3,851, Randy L Adams 3,710, Katherine Patrick 3,583. This row: {name} {votes}."))
    for pid, name, votes in (
        ("WY-VONBURG-RICK", "Rick VonBurg", "3,251"),
        ("WY-VANMARK-JACKIE", "Jackie VanMark", "3,193"),
        ("WY-EBERT-H-TERRY", "H. Terry Ebert", "2,568"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="special-districts",
                       office="Eastern Wyoming College Trustee", term_start=FM[2027], term_end=FM[2031],
                       election_year=2026, sources=[SRC_C26],
                       notes=f"Official 2026 Goshen clerk, Eastern Wyoming College Trustee 4-year Vote-For-3: Rick VonBurg 3,251, Jackie VanMark 3,193, H Terry Ebert 2,568. This row: {name} {votes}."))
    terms.append(T(person_id="WY-NEWMAN-JULIA-H", name="Julia H. Newman", party="", office_group="special-districts",
                   office="Eastern Wyoming College Trustee", term_start=FM[2027], term_end=FM[2029],
                   election_year=2026, sources=[SRC_C26],
                   notes="Official 2026 Goshen clerk, Eastern Wyoming College Trustee 2-year Vote-For-1: Julia H Newman 3,759."))

    # Conservation
    terms += [
        T(person_id="WY-TEETERS-MATT", name="Matt Teeters", party="", office_group="special-districts",
          office="Lingle-Fort Laramie Conservation District Rural Supervisor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Goshen clerk, Lingle-Fort Laramie Conservation Rural Vote-For-2: Matt Teeters 567, Donald A McDowell 472."),
        T(person_id="WY-MCDOWELL-DONALD-A", name="Donald A. McDowell", party="", office_group="special-districts",
          office="Lingle-Fort Laramie Conservation District Rural Supervisor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Goshen clerk, Lingle-Fort Laramie Conservation Rural Vote-For-2: Matt Teeters 567, Donald A McDowell 472."),
        T(person_id="WY-NICHOL-LINDA", name="Linda Nichol", party="", office_group="special-districts",
          office="Lingle-Fort Laramie Conservation District At-Large Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Goshen clerk, LFLCD Supervisor At-Large: Linda Nichol 901."),
        T(person_id="WY-JOHNSON-DAVID", name="David Johnson", party="", office_group="special-districts",
          office="Lingle-Fort Laramie Conservation District Rural Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Goshen clerk, LFLCD Supervisor Rural: David Johnson 887."),
        T(person_id="WY-MEEKS-JENNA", name="Jenna Meeks", party="", office_group="special-districts",
          office="Lingle-Fort Laramie Conservation District Urban Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Goshen clerk, LFLCD Supervisor Urban: Jenna Meeks 876."),
        T(person_id="WY-KELLER-DUANE", name="Duane Keller", party="", office_group="special-districts",
          office="North Platte Valley Conservation District Rural Supervisor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Goshen clerk, North Platte Valley Conservation Rural Vote-For-2: Duane Keller 2,357, Kasey Bangerter 2,223."),
        T(person_id="WY-BANGERTER-KASEY", name="Kasey Bangerter", party="", office_group="special-districts",
          office="North Platte Valley Conservation District Rural Supervisor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Goshen clerk, North Platte Valley Conservation Rural Vote-For-2: Duane Keller 2,357, Kasey Bangerter 2,223."),
        T(person_id="WY-MOORE-LUCAS", name="Lucas Moore", party="", office_group="special-districts",
          office="North Platte Valley Conservation District At-Large Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Goshen clerk, NPVCD Supervisor At-Large: Lucas Moore 3,558."),
        T(person_id="WY-EISENBARTH-ANDREA", name="Andrea Eisenbarth", party="", office_group="special-districts",
          office="North Platte Valley Conservation District Rural Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Goshen clerk, NPVCD Supervisor Rural: Andrea Eisenbarth 3,618."),
        T(person_id="WY-BAUMGARDNER-ENOCH", name="Enoch Baumgardner", party="", office_group="special-districts",
          office="North Platte Valley Conservation District Urban Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Goshen clerk, NPVCD Supervisor Urban: Enoch Baumgardner 3,507."),
        T(person_id="WY-ROSS-SCOTT-D", name="Scott D. Ross", party="", office_group="special-districts",
          office="South Goshen Conservation District At-Large Supervisor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Goshen clerk, South Goshen Conservation District At-Large: Scott D Ross 423."),
        T(person_id="WY-JACKSON-CRAIG", name="Craig Jackson", party="", office_group="special-districts",
          office="South Goshen Conservation District Rural Supervisor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Goshen clerk, South Goshen Conservation Rural: Craig Jackson 441."),
        T(person_id="WY-SCHEER-JENNIFER", name="Jennifer Scheer", party="", office_group="special-districts",
          office="South Goshen Conservation District Rural Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Goshen clerk, SGCD Supervisor Rural Vote-For-2: Jennifer Scheer 443, Dave Bartlett 367."),
        T(person_id="WY-BARTLETT-DAVE", name="Dave Bartlett", party="", office_group="special-districts",
          office="South Goshen Conservation District Rural Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Goshen clerk, SGCD Supervisor Rural Vote-For-2: Jennifer Scheer 443, Dave Bartlett 367."),
        T(person_id="WY-GRANDSTAFF-CURTIS-G", name="Curtis G. Grandstaff", party="", office_group="special-districts",
          office="South Goshen Conservation District Urban Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Goshen clerk, SGCD Supervisor Urban: Curtis G Grandstaff 590."),
    ]
    for pid, name, votes in (
        ("WY-RIFE-KONNE", "Konne Rife", "2,759"),
        ("WY-LOWRY-MICHAEL", "Michael Lowry", "2,718"),
        ("WY-JOY-MARDELL", "Mardell (Mardy) Joy", "2,676"),
        ("WY-MORGHEIM-MERRIJANE", "Merrijane Morgheim", "2,608"),
        ("WY-JOHNSON-THOMAS-A", "Thomas A. Johnson", "2,534"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="special-districts",
                       office="Senior Citizen Service District Trustee", term_start=FM[2027], term_end=FM[2031],
                       election_year=2026, sources=[SRC_C26],
                       notes=f"Official 2026 Goshen clerk, Senior Citizen Service District Trustee Vote-For-5: Konne Rife 2,759, Michael Lowry 2,718, Mardell (Mardy) Joy 2,676, Merrijane Morgheim 2,608, Thomas A Johnson 2,534. This row: {name} {votes}."))
    for pid, name in (
        ("WY-VAUGHN-BLAKE", "Blake Vaughn"),
        ("WY-VAUGHN-TRACY", "Tracy Vaughn"),
        ("WY-JACKSON-KATE", "Kate Jackson"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="special-districts",
                       office="Chugwater Cemetery District Director", term_start=FM[2027], term_end=FM[2031],
                       election_year=2026, sources=[SRC_C26],
                       notes="Official 2026 Goshen clerk, Chugwater Cemetery District Director 4-year Vote-For-3: Blake Vaughn 15, Tracy Vaughn 15, Kate Jackson 13, Barbara Fletcher 12. These are official Goshen votes; the district also covers area outside Goshen, and official Platte whole-district totals were not combined here."))
    terms.append(T(person_id="WY-TETER-DARLA", name="Darla Teter", party="", office_group="special-districts",
                   office="Chugwater Cemetery District Director", term_start=FM[2027], term_end=FM[2029],
                   election_year=2026, sources=[SRC_C26],
                   notes="Official 2026 Goshen clerk, Chugwater Cemetery District Director 2-year: Darla Teter 20. Official Goshen votes; official Platte whole-district totals were not combined here."))
    terms.append(T(person_id="WY-ASH-TIM", name="Tim Ash", party="", office_group="special-districts",
                   office="Chugwater Fire District Director", term_start=FM[2027], term_end=FM[2031],
                   election_year=2026, sources=[SRC_C26],
                   notes="Official 2026 Goshen clerk, Chugwater Fire District Director: Tim Ash 23. Official Goshen votes; official Platte whole-district totals were not combined here."))
    for pid, name in (
        ("WY-CROWLEY-HOLLY", "Holly Crowley"),
        ("WY-VAUGHN-RUTH", "Ruth Vaughn"),
        ("WY-WEBSTER-DEAN", "Dean Webster"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="special-districts",
                       office="Chugwater Cemetery District Director", term_start=FM[2025], term_end=FM[2029],
                       election_year=2024, sources=[SRC_C24],
                       notes="Official 2024 Goshen clerk, Chugwater Cemetery Director Vote-For-3: Ruth Vaughn 23, Dean Webster 23, Holly Crowley 22. Official Goshen votes; official Platte whole-district totals were not combined here."))
    terms.append(T(person_id="WY-KELLEY-MICHAEL-L", name="Michael L. Kelley", party="", office_group="special-districts",
                   office="Chugwater Cemetery District Director", term_start=FM[2025], term_end=FM[2027],
                   election_year=2024, sources=[SRC_C24], confidence="medium",
                   notes="Official 2024 Goshen clerk, Chugwater Cemetery Director Vote-For-1: Michael L Kelley 25. Official 2024 clerk did not print 2-year/4-year; 2-year term follows the official 2026 2-year Chugwater pattern. Official Goshen votes only."))
    return terms


def expected_offices():
    return {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
                      ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
        "state-senate": [("Senate District 3 (S03)", 1)],
        "state-house": [("House District 2 (H02)", 1), ("House District 5 (H05)", 1),
                        ("House District 10 (H10)", 1)],
        "county": [("County Commissioner", 3), ("County Clerk", 1), ("County Treasurer", 1),
                   ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
                   ("Clerk of District Court", 1), ("County Coroner", 1)],
        "municipal": [("Torrington Mayor", 1), ("Torrington Council", 4),
                      ("Lingle Mayor", 1), ("Lingle Council", 4),
                      ("Fort Laramie Mayor", 1), ("Fort Laramie Council", 4),
                      ("La Grange Mayor", 1), ("La Grange Council", 4)],
        "schools": [("Goshen County School District #1 Trustee", 9)],
        "special-districts": [
            ("Eastern Wyoming College Trustee", 7),
            ("Lingle-Fort Laramie Conservation District At-Large Supervisor", 1),
            ("Lingle-Fort Laramie Conservation District Rural Supervisor", 2),
            ("Lingle-Fort Laramie Conservation District Urban Supervisor", 1),
            ("North Platte Valley Conservation District At-Large Supervisor", 1),
            ("North Platte Valley Conservation District Rural Supervisor", 2),
            ("North Platte Valley Conservation District Urban Supervisor", 1),
            ("South Goshen Conservation District At-Large Supervisor", 1),
            ("South Goshen Conservation District Rural Supervisor", 2),
            ("South Goshen Conservation District Urban Supervisor", 1),
            ("Senior Citizen Service District Trustee", 5),
            ("Chugwater Cemetery District Director", 5),
            ("Chugwater Fire District Director", 1),
        ],
        "judicial": [
            ("District Judge, 8th Judicial District", 2),
            ("Circuit Judge, 8th Judicial District", 2),
        ],
    }


def build_goshen():
    people = {}
    P = H.person_factory(people)
    register_people(P)
    terms = []
    terms.extend(legislature_terms())
    terms.extend(county_terms())
    terms.extend(judicial_terms())
    terms.extend(municipal_terms())
    terms.extend(school_terms())
    terms.extend(special_terms())
    shared_path = ROOT / "data" / "county_officials" / "history" / "shared" / "federal-statewide-terms.json"
    shared = json.loads(shared_path.read_text())
    copied = 0
    for t in shared.get("terms") or shared:
        og = t.get("office_group") or ""
        office = t.get("office") or ""
        if og in {"federal", "statewide"}:
            terms.append(deepcopy(t)); copied += 1
        elif og == "judicial" and any(x in office for x in ("Supreme Court", "Chancery")):
            terms.append(deepcopy(t)); copied += 1
    H.attach_people_from_terms(terms, people)
    expected = expected_offices()
    judicial_note = (
        "Supreme Court justices and the Chancery Court judge are the people in office this January, from official "
        "Wyoming Judicial Branch dates and official retention results (shared with other counties). Official 2026 "
        "Goshen clerk CHANCERY COURT JUDGE BEN BURNINGHAM is that statewide Chancery retention, not a local 8th JD seat. "
        "Local rows are 8th Judicial District judges (Converse, Goshen, Niobrara, and Platte). Full names are taken from "
        "official Wyoming Judicial Branch 8th JD court pages, official SOS judicial rosters, and official Goshen clerk "
        "retention lines, and those sources are cited. Judges of other districts are not copied here."
    )
    special_note = (
        "County, municipal, school, and special-district names are keyed from official Goshen clerk general summaries "
        "(2018, 2020, 2022, 2024, and 2026), the official 2024 school-district recount, and the official 2026 GC school-board "
        "recount page bound in the official 2026 general PDF. Official 2014 and 2016 general canvasses are archived; 2014 is a "
        "scan that was not fully keyed here, so January 2015–2018 local rows are largely Not yet collected rather than invented, "
        "except official 2018 county and Torrington contests. Multi-county legislative seats use official SOS district-wide Total "
        "rows, with the official Goshen share noted. Official SOS shows a House District 10 Goshen sliver in 2014–2020 (with Laramie); "
        "official 2022+ SOS Goshen rows for H10 are blank after redistricting. Senate District 3 and House District 2 are Goshen, "
        "Niobrara, and Weston; House District 5 is Goshen-only. The Torrington mayor is elected on the official November ballot "
        "(official city Election Information page, four-year term), not chosen by the council. Official mid-term judicial vacancies "
        "are not invented; appointment start days are the first of the official month where the court page gives only the month. "
        "Niobrara County School District #1 and Platte County School District #1 and #2 appear on official Goshen canvasses as "
        "slivers; official whole-district Niobrara and Platte totals were not combined here, and those boards are not seated from "
        "the Goshen portion alone. Chugwater cemetery and fire results are official Goshen votes, with that same limitation noted. "
        "Lingle, Fort Laramie, and La Grange (official town spelling LaGrange) did not appear as mayor or council contests on the "
        "official 2018–2026 Goshen November general summaries; current holders are filled from official town pages and official town "
        "minutes, with sources and confidence noted on each term. The Town of Yoder has no official town page, official minutes, "
        "Wayback capture, or official SOS municipal canvass naming a current mayor or council in the sources searched, so those "
        "offices are not invented."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. The current (November 2026) precinct roster "
        "is in data/county_officials/goshen.json, from the official 2026 Goshen primary (named winners only; 12 precincts)."
    )
    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Goshen", county_number=CN, slug=SLUG, terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Goshen", slug=SLUG)
    print(f"wrote {terms_path}")
    print(f"terms {len(terms)} (including {copied} shared federal/statewide/SC-chancery terms)")
    print(f"people_additions +{n_people} offices_held +{n_off} thin_profiles +{n_prof}")
    H.print_coverage(coverage_all)
    return people, terms, coverage_all


def _office(title, holders, *, layout="office-and-name", note=""):
    rec = {"office": title, "layout": layout, "holders": holders}
    if note:
        rec["note"] = note
    return rec


def _holder(people, pid, name, party, term_end, notes=""):
    p = people.get(pid) or {}
    h = {
        "name": name,
        "person_id": pid,
        "party": party or "",
        "term_end": term_end,
    }
    slug = p.get("slug")
    if slug:
        h["href"] = f"candidates/local-history/c/{slug}.html"
    if notes:
        h["notes"] = notes
    return h


def _holders_for_office(terms, people, office, as_of="2026-11-24", elect_start="2027-01-04"):
    cur = [t for t in terms if t["office"] == office and t["term_start"] <= as_of < t["term_end"]]
    elects = [t for t in terms if t["office"] == office and t["term_start"] == elect_start]
    seen = set()
    out = []
    current_ids = {t["person_id"] for t in cur}
    def te(t):
        return "January " + t["term_end"][:4]
    for t in elects:
        if t["person_id"] in current_ids:
            out.append(_holder(people, t["person_id"], t["name"], t.get("party") or "", te(t), t.get("notes") or ""))
            seen.add(t["person_id"])
    for t in cur:
        if t["person_id"] in seen:
            continue
        out.append(_holder(people, t["person_id"], t["name"], t.get("party") or "", te(t), t.get("notes") or ""))
        seen.add(t["person_id"])
    for t in elects:
        if t["person_id"] in seen:
            continue
        out.append(_holder(people, t["person_id"], t["name"], t.get("party") or "", te(t), t.get("notes") or ""))
        seen.add(t["person_id"])
    return out


def update_goshen_json(people, terms):
    path = ROOT / "data" / "county_officials" / "goshen.json"
    data = json.loads(path.read_text())
    data["as_of"] = RETRIEVED
    data["county_number"] = CN
    data["term_switch_date"] = "2027-01-04"
    precincts = None
    for g in data.get("groups") or []:
        if g.get("id") == "precincts":
            precincts = g
            break

    def office_note(office):
        ts = [t for t in terms if t["office"] == office and t.get("notes")]
        as_of = "2026-11-24"
        relevant = [t for t in ts if (t["term_start"] <= as_of < t["term_end"]) or t["term_start"] >= "2026-11-01"]
        pool = relevant or ts
        pool = sorted(pool, key=lambda t: (t.get("election_year") or int(t["term_start"][:4])), reverse=True)
        if not pool:
            return ""
        seen = []
        for t in pool:
            n = t["notes"]
            if n and n not in seen:
                seen.append(n)
            if len(seen) == 2:
                break
        return " ".join(seen)

    senate = [_office("Senate District 3 (S03)", _holders_for_office(terms, people, "Senate District 3 (S03)"),
                      note=office_note("Senate District 3 (S03)"))]
    house = [
        _office("House District 2 (H02)", _holders_for_office(terms, people, "House District 2 (H02)"),
                note=office_note("House District 2 (H02)")),
        _office("House District 5 (H05)", _holders_for_office(terms, people, "House District 5 (H05)"),
                note=office_note("House District 5 (H05)")),
    ]
    county_offices = [
        "County Commissioner", "County Clerk", "County Treasurer", "County Assessor",
        "County Sheriff", "County Attorney", "Clerk of District Court", "County Coroner",
    ]
    county = [_office(o, _holders_for_office(terms, people, o), note=office_note(o)) for o in county_offices]
    mun_offices = ["Torrington Mayor", "Torrington Council",
                  "Lingle Mayor", "Lingle Council",
                  "Fort Laramie Mayor", "Fort Laramie Council",
                  "La Grange Mayor", "La Grange Council"]
    municipal = [_office(o, _holders_for_office(terms, people, o), note=office_note(o),
                         layout="heading-then-names" if "Council" in o else "office-and-name")
                 for o in mun_offices]
    schools = [_office("Goshen County School District #1 Trustee",
                       _holders_for_office(terms, people, "Goshen County School District #1 Trustee"),
                       note=office_note("Goshen County School District #1 Trustee"),
                       layout="heading-then-names")]
    special_offices = [
        "Eastern Wyoming College Trustee",
        "Lingle-Fort Laramie Conservation District At-Large Supervisor",
        "Lingle-Fort Laramie Conservation District Rural Supervisor",
        "Lingle-Fort Laramie Conservation District Urban Supervisor",
        "North Platte Valley Conservation District At-Large Supervisor",
        "North Platte Valley Conservation District Rural Supervisor",
        "North Platte Valley Conservation District Urban Supervisor",
        "South Goshen Conservation District At-Large Supervisor",
        "South Goshen Conservation District Rural Supervisor",
        "South Goshen Conservation District Urban Supervisor",
        "Senior Citizen Service District Trustee",
        "Chugwater Cemetery District Director",
        "Chugwater Fire District Director",
    ]
    specials = [_office(o, _holders_for_office(terms, people, o), note=office_note(o),
                        layout="heading-then-names" if "Trustee" in o or "Rural" in o or "Director" in o or "College" in o else "office-and-name")
                for o in special_offices]
    judicial = [
        _office("District Judge, 8th Judicial District",
                _holders_for_office(terms, people, "District Judge, 8th Judicial District"),
                note=office_note("District Judge, 8th Judicial District")),
        _office("Circuit Judge, 8th Judicial District",
                _holders_for_office(terms, people, "Circuit Judge, 8th Judicial District"),
                note=office_note("Circuit Judge, 8th Judicial District")),
    ]
    groups = [
        {"id": "state-senate", "label": "Wyoming Senate", "offices": senate},
        {"id": "state-house", "label": "Wyoming House", "offices": house},
        {"id": "county", "label": "County offices", "offices": county},
        {"id": "municipal", "label": "Municipal offices", "offices": municipal},
        {"id": "schools", "label": "School boards", "offices": schools},
        {"id": "special-districts", "label": "Special districts", "offices": specials},
        {"id": "judicial", "label": "Judicial", "offices": judicial},
    ]
    if precincts:
        groups.append(precincts)
    data["groups"] = groups
    data["sources"] = {
        "general_results": URL_C26,
        "primary_results": URL_P26,
        "clerk_archive": URL_GEN_ARCH,
        "checked": RETRIEVED,
        "local_archive": "/workspace/wyoleg/local-results/goshen/SOURCES.md",
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("updated", path)
    return path
