#!/usr/bin/env python3
"""Platte County officeholder history (preview). Official clerk, SOS, court,
and town sources only. Names are never invented.
"""
from __future__ import annotations

import json
from copy import deepcopy

import history_lib as H
from history_lib import FM, ROOT, src_dict, term

RETRIEVED = "2026-11-24"
CN = 8
SLUG = "platte"

URL_ELECTIONS = "https://www.plattecountywyoming.com/departments/elections/ResultsofElection"
URL_C26 = "https://www.plattecountywyoming.com/media/Elections/Election%20Results/2026/2026%20General%20Election/Official%20Results/Summary%20Report_Final%20Official.pdf"
URL_P26 = "https://www.plattecountywyoming.com/media/Elections/Election%20Results/2026/2026%20Primary%20Election/Official%20Results/Summary%20Report.pdf"
URL_C24 = "https://www.plattecountywyoming.com/media/Elections/Election%20Results/2024/General%20Election/Election%20Summary.pdf"
URL_C22 = "https://www.plattecountywyoming.com/media/Elections/2022/Results/Official%20Election%20Summary.pdf"
URL_C20 = "https://www.plattecountywyoming.com/media/Elections/2020%20Primary/Official%20Election%20Summary.pdf"
URL_C20P = "https://www.plattecountywyoming.com/media/Elections/2020%20Primary/Official%202020%20Primary%20Results.pdf"
URL_H25 = "https://www.plattecountywyoming.com/media/Elections/2025/9b%20-%20Election%20Results%202025.pdf"
URL_GLENDO = "https://townofglendo.com/government/"
URL_GLENDO_WB_2026 = "https://web.archive.org/web/20260708004946/https://townofglendo.com/government/"
URL_GLENDO_WB_2024 = "https://web.archive.org/web/20240221004900/https://townofglendo.com/government/"
URL_COURT_D = "https://www.wyocourts.gov/court/district-court-8th-judicial-district-converse-county/"
URL_COURT_G = "https://www.wyocourts.gov/court/circuit-court-of-the-8th-judicial-district-goshen-county-state-of-wyoming-torrington/"
URL_COURT_C = "https://www.wyocourts.gov/court/circuit-court-of-the-8th-judicial-district-converse-county-state-of-wyoming-douglas/"
URL_GOSHEN_C26 = "https://goshencounty.org/ArchiveCenter/ViewFile/Item/162"
URL_GOSHEN_C24 = "https://goshencounty.org/ArchiveCenter/ViewFile/Item/143"
URL_GOSHEN_C22 = "https://goshencounty.org/ArchiveCenter/ViewFile/Item/135"
URL_GOSHEN_C20 = "https://goshencounty.org/ArchiveCenter/ViewFile/Item/138"


def S(label, url=""):
    return src_dict(label, url)


def sos_url(year, chamber):
    ch = "Senate" if chamber == "Senate" else "House"
    return f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_Statewide_{ch}_Candidates_Summary.pdf"


def sos_src(year, chamber):
    return S(
        f"Official Wyoming SOS {year} statewide {chamber} candidates summary (district-wide Total row)",
        sos_url(year, chamber),
    )


def T(**kw):
    kw.setdefault("confidence", "high")
    kw.setdefault("how_took_office", "elected")
    if "sources" not in kw:
        kw["sources"] = []
    return term(**kw)


SRC_C26 = S("Official Platte County 2026 general election summary (header OFFICIAL RESULTS, Election Summary - 11/06/2026 01:37PM, 13 of 13 precincts). Official names and totals for this encoded canvass were read from official rendered page images because the official PDF text is font-encoded.", URL_C26)
SRC_P26 = S("Official Platte County 2026 primary election summary (header Official Results)", URL_P26)
SRC_C24 = S("Official Platte County 2024 general election summary (header OFFICIAL RESULTS)", URL_C24)
SRC_C22 = S("Official Platte County 2022 general election official results (header OFFICIAL RESULTS, Election Summary - 11/10/2022 4:27 PM)", URL_C22)
SRC_C20 = S("Official Platte County 2020 general election official results (file path is under media/Elections/2020 Primary/, but the official PDF header is OFFICIAL RESULTS, 2020 General Election, Precincts Complete 13 of 13)", URL_C20)
SRC_H25 = S("Official Town of Hartville May 6, 2025 municipal election results (official Platte County clerk PDF 9b - Election Results 2025, header Official Election Results)", URL_H25)
SRC_GLENDO = S("Official Town of Glendo government page (https://townofglendo.com/government/), retrieved from the Wayback Machine because the live official site returned 500/406 at the time of collection", URL_GLENDO)
SRC_GLENDO_2026 = S("Official Town of Glendo government page, Wayback Machine capture 2026-07-08 (https://web.archive.org/web/20260708004946/https://townofglendo.com/government/)", URL_GLENDO_WB_2026)
SRC_GLENDO_2024 = S("Official Town of Glendo government page, Wayback Machine capture 2024-02-21 (https://web.archive.org/web/20240221/https://townofglendo.com/government/)", URL_GLENDO_WB_2024)
SRC_COURT_D = S("Official Wyoming Judicial Branch, District Court of the 8th Judicial District", URL_COURT_D)
SRC_COURT_G = S("Official Wyoming Judicial Branch, Circuit Court of the 8th Judicial District, Goshen County (Torrington)", URL_COURT_G)
SRC_COURT_C = S("Official Wyoming Judicial Branch, Circuit Court of the 8th Judicial District, Converse County (Douglas)", URL_COURT_C)
SRC_G20 = S("Official Goshen County 2020 general election official results (ArchiveCenter Item 138), Platte County School District sliver", URL_GOSHEN_C20)
SRC_G22 = S("Official Goshen County 2022 general election official results (ArchiveCenter Item 135), Platte County School District sliver", URL_GOSHEN_C22)
SRC_G24 = S("Official Goshen County 2024 general election official results (ArchiveCenter Item 143), Platte County School District sliver", URL_GOSHEN_C24)
SRC_G26 = S("Official Goshen County 2026 general election official results (ArchiveCenter Item 162), Platte County School District sliver", URL_GOSHEN_C26)
SRC_SOS12S = sos_src(2012, "Senate")
SRC_SOS14H = sos_src(2014, "House")
SRC_SOS16S = sos_src(2016, "Senate")
SRC_SOS16H = sos_src(2016, "House")
SRC_SOS18H = sos_src(2018, "House")
SRC_SOS20S = sos_src(2020, "Senate")
SRC_SOS20H = sos_src(2020, "House")
SRC_SOS22H = sos_src(2022, "House")
SRC_SOS24S = sos_src(2024, "Senate")
SRC_SOS24H = sos_src(2024, "House")
SRC_SOS26S = sos_src(2026, "Senate")
SRC_SOS26H = sos_src(2026, "House")


def register_people(P):
    # Legislature (reuse existing IDs)
    P("WY-ANDERSON-JIM-SD02", "Jim Anderson", "Jim", "Anderson",
      aliases="Jim Anderson (S02)")
    P("WY-BONER-BRIAN", "Brian Boner", "Brian", "Boner")
    P("WY-SMITH-DARIN", "Darin Smith", "Darin", "Smith")
    P("WY-LOVE-TAFT", "Taft Love", "Taft", "Love")
    P("WY-KIRKBRIDE-DAN-R", "Dan R. Kirkbride", "Dan", "Kirkbride", middle="R.",
      aliases="Dan R Kirkbride|Dan Kirkbride|Kirkbride")
    P("WY-HAROLDSON-JEREMY", "Jeremy Haroldson", "Jeremy", "Haroldson")
    # County
    P("WY-SHOCKLEY-STEVE", "Steve Shockley", "Steve", "Shockley", aliases="STEVE SHOCKLEY|REP STEVE SHOCKLEY")
    P("WY-JOLOVICH-IAN", "Ian Jolovich", "Ian", "Jolovich", aliases="IAN JOLOVICH|REP IAN JOLOVICH")
    P("WY-MANTLE-KAYLA", "Kayla Mantle", "Kayla", "Mantle", aliases="KAYLA MANTLE|REP KAYLA MANTLE")
    P("WY-BAKER-JEB", "Jeb Baker", "Jeb", "Baker", aliases="JEB BAKER|REP JEB BAKER")
    P("WY-ERVIN-MALCOLM-J", "Malcolm J. Ervin", "Malcolm", "Ervin", middle="J.",
      aliases="Malcolm J Ervin|MALCOLM J. ERVIN|MALCOLM J ERVIN|REP MALCOLM J ERVIN")
    P("WY-RIETZ-KRISTI", "Kristi Rietz", "Kristi", "Rietz", aliases="KRISTI RIETZ|REP KRISTI RIETZ")
    P("WY-GLOVER-LISA", "Lisa Glover", "Lisa", "Glover", aliases="LISA GLOVER|REP LISA GLOVER")
    P("WY-EPPEL-DANETTE", "Danette Eppel", "Danette", "Eppel", aliases="DANETTE EPPEL|REP DANETTE EPPEL")
    P("WY-RUSSELL-DAVID", "David Russell", "David", "Russell", aliases="DAVID RUSSELL|REP DAVID RUSSELL")
    P("WY-KROTZ-ANTHONY", "Anthony Krotz", "Anthony", "Krotz", aliases="Tony Krotz|ANTHONY KROTZ|TONY KROTZ|REP ANTHONY KROTZ")
    P("WY-WEAVER-DOUGLAS-W", "Douglas W. Weaver", "Douglas", "Weaver", middle="W.",
      aliases="Douglas Weaver|Doug Weaver|DOUGLAS W. WEAVER|DOUGLAS WEAVER|DOUG WEAVER|REP DOUGLAS W WEAVER")
    P("WY-ROTH-MAREL-E-BUNKER", "Marel E. Bunker Roth", "Marel", "Roth", middle="E. Bunker",
      aliases="Marel E Bunker Roth|MAREL E. BUNKER ROTH|MAREL E BUNKER ROTH")
    P("WY-MCAULEY-MONA", "Mona McAuley", "Mona", "McAuley", aliases="MONA MCAULEY|REP MONA MCAULEY")
    P("WY-MARTIN-PHILIP-G", "Philip G. Martin", "Philip", "Martin", middle="G.",
      aliases="Philip G Martin|PHILIP G. MARTIN|PHILIP G MARTIN")
    P("WY-DEAN-TIFFANY-GORMAN", "Tiffany Gorman Dean", "Tiffany", "Dean", middle="Gorman",
      aliases="Tiffany Dean|TIFFANY GORMAN DEAN|TIFFANY DEAN")
    # 8th JD
    P("WY-KORELL-PATRICK-W", "Patrick W. Korell", "Patrick", "Korell", middle="W.")
    P("WY-PEASLEY-F-SCOTT", "F. Scott Peasley", "F. Scott", "Peasley")
    P("WY-BUCHANAN-EDWARD-A", "Edward A. Buchanan", "Edward", "Buchanan", middle="A.")
    P("WY-ARP-RANDAL-R", "Randal R. Arp", "Randal", "Arp", middle="R.")
    P("WY-HIBBEN-NATHANIEL-S", "Nathaniel S. Hibben", "Nathaniel", "Hibben", middle="S.",
      aliases="Nathaniel Scott Hibben|NATHANIEL SCOTT HIBBEN|JUDGE HIBBEN")
    P("WY-ALLAN-CLARK-C", "Clark C. Allan", "Clark", "Allan", middle="C.", aliases="CLARK C ALLAN|CLARK C. ALLAN")
    P("WY-BROWN-JACQUELINE-K", "Jacqueline K. Brown", "Jacqueline", "Brown", middle="K.",
      aliases="JACQUELINE K BROWN|JACQUELINE K. BROWN")
    # Municipal
    P("WY-GRAVES-BRANDON-R", "Brandon R. Graves", "Brandon", "Graves", middle="R.",
      aliases="Brandon R Graves|BRANDON R. GRAVES|BRANDON R GRAVES")
    P("WY-KAUFMAN-JOSHUA-J", "Joshua J. Kaufman", "Joshua", "Kaufman", middle="J.",
      aliases="Joshua Kaufman|JOSHUA J. KAUFMAN|JOSHUA J KAUFMAN|JOSHUA KAUFMAN")
    P("WY-ALLISON-WILLIAM-L", "William L. Allison", "William", "Allison", middle="L.",
      aliases="William L Allison|WILLIAM L. ALLISON|WILLIAM L ALLISON")
    P("WY-EVANS-JASON", "Jason Evans", "Jason", "Evans", aliases="JASON EVANS")
    P("WY-MIXSON-KELLY", "Kelly Mixson", "Kelly", "Mixson", aliases="KELLY MIXSON")
    P("WY-MILLER-DAVE", "Dave Miller", "Dave", "Miller", aliases="DAVE MILLER")
    P("WY-MONTOYA-TONY", "Tony Montoya", "Tony", "Montoya", aliases="TONY MONTOYA")
    P("WY-MADSEN-ALAN", "Alan Madsen", "Alan", "Madsen", aliases="ALAN MADSEN")
    P("WY-DELGADO-EDDIE", "Eddie Delgado", "Eddie", "Delgado",
      aliases="Edward Delgado|EDDIE DELGADO|EDWARD DELGADO")
    P("WY-REICHERT-SHAWNA", "Shawna Reichert", "Shawna", "Reichert", aliases="SHAWNA REICHERT")
    P("WY-HARRIS-DALE-R", "Dale R. Harris", "Dale", "Harris", middle="R.",
      aliases="Dale Harris|Dale R Harris|DALE R HARRIS|DALE HARRIS")
    P("WY-WELLS-PENNY", "Penny Wells", "Penny", "Wells", aliases="PENNY WELLS")
    P("WY-MICHAELS-JOE", "Joe Michaels", "Joe", "Michaels", aliases="JOE MICHAELS")
    P("WY-FIELDS-JEREMIAH", "Jeremiah Fields", "Jeremiah", "Fields", aliases="JEREMIAH FIELDS")
    P("WY-AUGUSTYN-KELLIE", "Kellie Augustyn", "Kellie", "Augustyn",
      aliases="Kellie J. Augustyn|KELLIE AUGUSTYN|KELLIE J AUGUSTYN")
    P("WY-THOMAS-JEFFERY", "Jeffery Thomas", "Jeffery", "Thomas", aliases="JEFFERY THOMAS")
    P("WY-ASH-CAROL-A", "Carol A. Ash", "Carol", "Ash", middle="A.", aliases="Carol A Ash|CAROL A. ASH|CAROL A ASH")
    P("WY-HOPKINS-JOSHUA", "Joshua Hopkins", "Joshua", "Hopkins", aliases="JOSHUA HOPKINS")
    P("WY-KELLEY-STEVEN-L", "Steven L. Kelley", "Steven", "Kelley", middle="L.",
      aliases="Steven Kelley|Steve Kelley|STEVEN L. KELLEY|STEVEN KELLEY|STEVEN L KELLEY")
    P("WY-BURNS-JOHN", "John Burns", "John", "Burns", aliases="JOHN BURNS")
    P("WY-SKIBA-STEVE", "Steve Skiba", "Steve", "Skiba", aliases="STEVE SKIBA")
    P("WY-MARLATT-ERIC-C", "Eric C. Marlatt", "Eric", "Marlatt", middle="C.", aliases="Eric C Marlatt|ERIC C. MARLATT")
    P("WY-SCHIRMER-JOSEPH-G", "Joseph G. Schirmer", "Joseph", "Schirmer", middle="G.",
      aliases="Joseph G Schirmer|JOSEPH G. SCHIRMER")
    P("WY-KLEIN-VICKI-R", "Vicki R. Klein", "Vicki", "Klein", middle="R.", aliases="Vicki R Klein|VICKI R. KLEIN")
    P("WY-HANSEN-JOSH", "Josh Hansen", "Josh", "Hansen", aliases="JOSH HANSEN")
    P("WY-TROUPE-KATHERYN", "Katheryn Troupe", "Katheryn", "Troupe", aliases="KATHERYN TROUPE")
    P("WY-YOUNG-KARI", "Kari Young", "Kari", "Young", aliases="KARI YOUNG")
    P("WY-HARMON-WILLIAM-SCOTT", "William Scott Harmon", "William Scott", "Harmon", aliases="WILLIAM SCOTT HARMON")
    P("WY-YENGER-VERN", "Vern Yenger", "Vern", "Yenger", aliases="VERN YENGER")
    P("WY-JUSCKA-SUSAN", "Susan Juscka", "Susan", "Juscka")
    P("WY-SCHOENING-HEATHER", "Heather Schoening", "Heather", "Schoening")
    P("WY-DUGDALE-DAN", "Dan Dugdale", "Dan", "Dugdale")
    P("WY-BROOKS-LACY", "Lacy Brooks", "Lacy", "Brooks")
    P("WY-JONES-KELLY-GLENDO", "Kelly Jones", "Kelly", "Jones")
    P("WY-CUNDALL-JESTON", "Jeston Cundall", "Jeston", "Cundall")
    # Schools
    P("WY-ELLER-CONNIE-TWIFORD", "Connie Twiford Eller", "Connie", "Eller", aliases="CONNIE TWIFORD ELLER")
    P("WY-KAFKA-DUSTIN-J", "Dustin J. Kafka", "Dustin", "Kafka", middle="J.", aliases="Dustin J Kafka|DUSTIN J. KAFKA")
    P("WY-HAROLDSON-DIANE", "Diane Haroldson", "Diane", "Haroldson", aliases="DIANE HAROLDSON")
    P("WY-FOX-AMANDA", "Amanda Fox", "Amanda", "Fox", aliases="AMANDA FOX")
    P("WY-LAY-GLENDA-L", "Glenda L. Lay", "Glenda", "Lay", middle="L.",
      aliases="Glenda Lu Lay|Glenda L Lay|GLENDA LU LAY|GLENDA L. LAY")
    P("WY-IRVINE-CHASE", "Chase Irvine", "Chase", "Irvine", aliases="CHASE IRVINE")
    P("WY-BECKER-CLAY", "Clay Becker", "Clay", "Becker", aliases="CLAY BECKER")
    P("WY-JONES-KRISTEN", "Kristen Jones", "Kristen", "Jones", aliases="KRISTEN JONES")
    P("WY-SEYFANG-SARAH-A", "Sarah A. Seyfang", "Sarah", "Seyfang", middle="A.",
      aliases="Sarah Seyfang|Sarah A Seyfang|SARAH SEYFANG|SARAH A SEYFANG")
    P("WY-ANDERSON-GARY-L", "Gary L. Anderson", "Gary", "Anderson", middle="L.",
      aliases="Gary L Anderson|GARY L. ANDERSON|GARY L ANDERSON")
    P("WY-COWAN-JASON", "Jason Cowan", "Jason", "Cowan", aliases="JASON COWAN")
    P("WY-GROSS-KEVIN-M", "Kevin M. Gross", "Kevin", "Gross", middle="M.",
      aliases="Kevin Gross|Kevin M Gross|KEVIN M GROSS|KEVIN GROSS")
    P("WY-AYERS-BLAINE", "Blaine Ayers", "Blaine", "Ayers", aliases="BLAINE AYERS")
    P("WY-IBARRA-ROBERT", "Robert Ibarra", "Robert", "Ibarra", aliases="ROBERT IBARRA")
    P("WY-SEYFANG-DAVID", "David Seyfang", "David", "Seyfang", aliases="DAVID SEYFANG")
    P("WY-JONES-ERIC-E", "Eric E. Jones", "Eric", "Jones", middle="E.",
      aliases="Eric E Jones|ERIC E. JONES|ERIC E JONES")
    P("WY-HOFFMAN-SHAWN", "Shawn Anne Hoffman", "Shawn", "Hoffman", middle="Anne",
      aliases="Shawn Hoffman|SHAWN ANNE HOFFMAN|SHAWN HOFFMAN")
    # Specials (plus reused municipal/school IDs where official names match)
    P("WY-GOERTZ-JASON", "Jason Goertz", "Jason", "Goertz", aliases="JASON GOERTZ")
    P("WY-REYES-BURR-JENNIFER", "Jennifer Reyes-Burr", "Jennifer", "Reyes-Burr",
      aliases="JENNIFER REYES-BURR")
    P("WY-CLARK-LEVI-D", "Levi D. Clark", "Levi", "Clark", middle="D.",
      aliases="Levi D Clark|LEVI D. CLARK|LEVI D CLARK")
    P("WY-LAUCK-TYLER", "Tyler Lauck", "Tyler", "Lauck", aliases="TYLER LAUCK")
    P("WY-BROCKMAN-BROOK", "Brook Brockman", "Brook", "Brockman", aliases="BROOK BROCKMAN")
    P("WY-HITT-MERLIN", "Merlin Hitt", "Merlin", "Hitt", aliases="MERLIN HITT")
    P("WY-MODESITT-LEE", "Lee Modesitt", "Lee", "Modesitt", aliases="LEE MODESITT")
    P("WY-NELSON-LANA", "Lana Nelson", "Lana", "Nelson", aliases="LANA NELSON")
    P("WY-GRAVES-JILL-R", "Jill R. Graves", "Jill", "Graves", middle="R.", aliases="Jill R Graves|JILL R GRAVES")
    P("WY-PASLEY-KENNETH-L", "Kenneth L. Pasley", "Kenneth", "Pasley", middle="L.",
      aliases="Kenneth L Pasley|KENNETH L PASLEY|KENNETH L. PASLEY")
    P("WY-TAYLOR-SARAH", "Sarah Taylor", "Sarah", "Taylor", aliases="SARAH TAYLOR")
    P("WY-MARTINEZ-ROSE-MARIE", "Rose Marie Martinez", "Rose Marie", "Martinez",
      aliases="ROSE MARIE MARTINEZ")
    P("WY-GENTLE-JULIE", "Julie Gentle", "Julie", "Gentle", aliases="JULIE GENTLE")
    P("WY-ORR-JERRY-G", "Jerry G. Orr", "Jerry", "Orr", middle="G.", aliases="Jerry G Orr|JERRY G. ORR")
    P("WY-BOWEN-RICK-L", "Rick L. Bowen", "Rick", "Bowen", middle="L.", aliases="Rick L Bowen|RICK L. BOWEN")
    P("WY-WILSON-BRITT", "Britt Wilson", "Britt", "Wilson", aliases="BRITT WILSON")
    P("WY-MODESITT-LORI", "Lori Modesitt", "Lori", "Modesitt", aliases="LORI MODESITT")
    P("WY-FREDERICK-CHUCK", "Chuck Frederick", "Chuck", "Frederick", aliases="CHUCK FREDERICK")
    P("WY-HELLBAUM-ROB", "Rob Hellbaum", "Rob", "Hellbaum", aliases="ROB HELLBAUM")
    P("WY-SHANAHAN-DEBRA", "Debra Shanahan", "Debra", "Shanahan", aliases="DEBRA SHANAHAN")
    P("WY-MILLIKIN-LISA", "Lisa Millikin", "Lisa", "Millikin", aliases="LISA MILLIKIN|LISA MILLIKIN")
    P("WY-BROCKMAN-JALEA", "Jalea Brockman", "Jalea", "Brockman", aliases="JALEA BROCKMAN")
    P("WY-WATSON-JOHN", "John Watson", "John", "Watson", aliases="JOHN WATSON")
    P("WY-MICKELSEN-VICKI", "Vicki Mickelsen", "Vicki", "Mickelsen", aliases="VICKI MICKELSEN")
    P("WY-VINEYARD-ROD", "Rod Vineyard", "Rod", "Vineyard", aliases="ROD VINEYARD")
    P("WY-OCKINGA-R-KEITH", "R. Keith Ockinga", "R. Keith", "Ockinga", aliases="R KEITH OCKINGA|R. KEITH OCKINGA")
    P("WY-WINDMEIER-DAVID", "David Windmeier", "David", "Windmeier", aliases="DAVID WINDMEIER")
    P("WY-DERRA-TAYLOR", "Taylor Derra", "Taylor", "Derra", aliases="TAYLOR DERRA")
    P("WY-COLLINS-JAY-B", "Jay B. Collins", "Jay", "Collins", middle="B.",
      aliases="Jay Collins|Jay B Collins|JAY B COLLINS|JAY COLLINS")
    P("WY-FOY-PAUL", "Paul Foy", "Paul", "Foy", aliases="PAUL FOY")
    P("WY-SMALL-KEN", "Ken Small", "Ken", "Small", aliases="KEN SMALL")
    P("WY-WEBER-DAVID", "David Weber", "David", "Weber", aliases="DAVID WEBER")
    P("WY-LAFFITTE-ANTHONY", "Anthony Laffitte", "Anthony", "Laffitte", aliases="ANTHONY LAFFITTE")
    P("WY-MILLER-LYNDON-J", "Lyndon J. Miller", "Lyndon", "Miller", middle="J.",
      aliases="Lyndon J Miller|LYNDON J. MILLER|LYNDON J MILLER")
    P("WY-MILLER-DENNIS-E", "Dennis E. Miller", "Dennis", "Miller", middle="E.",
      aliases="Dennis Miller|Dennis E Miller|DENNIS E MILLER|DENNIS MILLER")
    P("WY-WARNER-DAVID", "David Warner", "David", "Warner", aliases="DAVID WARNER")
    P("WY-ASH-TIM", "Tim Ash", "Tim", "Ash", aliases="TIM ASH")
    P("WY-JACKSON-KATE", "Kate Jackson", "Kate", "Jackson", aliases="KATE JACKSON")
    P("WY-VAUGHN-RUTH", "Ruth Vaughn", "Ruth", "Vaughn", aliases="RUTH VAUGHN")
    P("WY-CROWLEY-HOLLY", "Holly Crowley", "Holly", "Crowley", aliases="HOLLY CROWLEY")
    P("WY-WEBSTER-DEAN", "Dean Webster", "Dean", "Webster", aliases="DEAN WEBSTER")
    P("WY-KELLEY-MICHAEL-L", "Michael L. Kelley", "Michael", "Kelley", middle="L.",
      aliases="Michael L Kelley|MICHAEL L KELLEY")
    P("WY-BAKER-DENNIS", "Dennis Baker", "Dennis", "Baker", aliases="DENNIS BAKER")
    P("WY-VAUGHN-BLAKE", "Blake Vaughn", "Blake", "Vaughn", aliases="BLAKE VAUGHN")
    P("WY-VAUGHN-TRACY", "Tracy Vaughn", "Tracy", "Vaughn", aliases="TRACY VAUGHN")
    P("WY-TETER-DARLA", "Darla Teter", "Darla", "Teter", aliases="DARLA TETER")
    P("WY-BAUDER-PAUL", "Paul Bauder", "Paul", "Bauder", aliases="PAUL BAUDER")
    P("WY-COLLINS-KATHRYN", "Kathryn Collins", "Kathryn", "Collins", aliases="KATHRYN COLLINS")
    P("WY-ARBOGAST-JAMES-C", "James C. Arbogast", "James", "Arbogast", middle="C.",
      aliases="James C Arbogast|JAMES C. ARBOGAST")
    P("WY-HALVORSEN-JASON", "Jason Halvorsen", "Jason", "Halvorsen", aliases="JASON HALVORSEN")


def legislature_terms():
    terms = []
    # S02 (official pre-2022 map: Converse and Platte). Official 2024+ SOS S02 is Converse and Natrona only.
    terms += [
        T(person_id="WY-ANDERSON-JIM-SD02", name="Jim Anderson", party="R", office_group="state-senate",
          office="Senate District 2 (S02)", term_start=FM[2013], term_end=FM[2017],
          election_year=2012, sources=[SRC_SOS12S],
          notes="Official 2012 SOS statewide Senate summary, Senate District 2, Jim Anderson (R) Total 8,359. Official Platte share 3,857; official Converse share 4,502. Distinct from Natrona Senate District 28 Jim Anderson (WY-ANDERSON-JIM), who was in office in S28 over the same years."),
        T(person_id="WY-BONER-BRIAN", name="Brian Boner", party="R", office_group="state-senate",
          office="Senate District 2 (S02)", term_start=FM[2017], term_end=FM[2021],
          election_year=2016, sources=[SRC_SOS16S],
          notes="Official 2016 SOS statewide Senate summary, Senate District 2 (right-hand Total is Senate District 4 and is not used): Brian Boner (R) 8,187, Cullen III (D) 1,377. Official Platte share Boner 3,557, Cullen 826; official Converse share Boner 4,630, Cullen 551."),
        T(person_id="WY-BONER-BRIAN", name="Brian Boner", party="R", office_group="state-senate",
          office="Senate District 2 (S02)", term_start=FM[2021], term_end=FM[2023],
          election_year=2020, sources=[SRC_SOS20S, SRC_C20], confidence="medium",
          notes="Official 2020 SOS statewide Senate summary, Senate District 2: Brian Boner (R) Total 9,372. Official Platte share 4,298; official Converse share 5,074. Official 2020 Platte clerk STATE SENATOR DIST #2 Brian Boner 4,298. After 2022 redistricting, official SOS Platte rows for S02 are blank (official 2024 S02 Total 7,712 is Converse 5,912 and Natrona 1,800 only). This term is ended at January 2023 rather than inventing a holdover through January 2025 (medium). January 2023–2024 Platte senate coverage is therefore Not yet collected; official S06 begins after the official 2024 election."),
        T(person_id="WY-SMITH-DARIN", name="Darin Smith", party="R", office_group="state-senate",
          office="Senate District 6 (S06)", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_SOS24S, SRC_C24],
          notes="Official 2024 SOS statewide Senate summary, Senate District 6: Darin Smith (R) Total 8,484. Official Platte share 3,998; official Laramie share 4,486. Official 2024 Platte clerk S06 Darin Smith 3,998. Same person and term dates as in the Laramie history. Official 2026 general names Taft Love as the S06 winner; January 2025–2026 snapshots keep Smith as the last official general-election holder. The mid-term succession date is not stated in the official generals and is not invented."),
        T(person_id="WY-LOVE-TAFT", name="Taft Love", party="R", office_group="state-senate",
          office="Senate District 6 (S06)", term_start=FM[2027], term_end=FM[2029],
          election_year=2026, sources=[SRC_SOS26S, SRC_C26], confidence="medium",
          notes="Official 2026 SOS statewide Senate summary, Senate District 6: Taft Love (R) Total 6,142. Official Platte share 2,943; official Laramie share 3,199. Official 2026 Platte clerk S06 Taft Love 2,943. Encoded as the remainder of the official 2024 four-year S06 term through January 2029, consistent with the Laramie history (medium on length)."),
    ]
    # H04: official 2014–2020 is Platte and Converse; official 2022+ is Platte and Laramie.
    terms += [
        T(person_id="WY-KIRKBRIDE-DAN-R", name="Dan R. Kirkbride", party="R", office_group="state-house",
          office="House District 4 (H04)", term_start=FM[2015], term_end=FM[2017],
          election_year=2014, sources=[SRC_SOS14H],
          notes="Official 2014 SOS statewide House summary, House District 4: Dan R. Kirkbride (R) Total 3,326. Official Platte share 2,999; official Converse share 327."),
        T(person_id="WY-KIRKBRIDE-DAN-R", name="Dan R. Kirkbride", party="R", office_group="state-house",
          office="House District 4 (H04)", term_start=FM[2017], term_end=FM[2019],
          election_year=2016, sources=[SRC_SOS16H],
          notes="Official 2016 SOS statewide House summary, House District 4 (right column beside House District 3; the combined two-column Total is not used for HD3): Dan R. Kirkbride (R) 3,652, Joe Michaels (C) 1,185. Official Platte share Kirkbride 3,204, Michaels 1,088; official Converse share Kirkbride 448, Michaels 97."),
        T(person_id="WY-KIRKBRIDE-DAN-R", name="Dan R. Kirkbride", party="R", office_group="state-house",
          office="House District 4 (H04)", term_start=FM[2019], term_end=FM[2021],
          election_year=2018, sources=[SRC_SOS18H],
          notes="Official 2018 SOS statewide House summary, House District 4 (right column): Dan R. Kirkbride (R) Total 3,645. Official Platte share 3,259; official Converse share 386."),
        T(person_id="WY-HAROLDSON-JEREMY", name="Jeremy Haroldson", party="R", office_group="state-house",
          office="House District 4 (H04)", term_start=FM[2021], term_end=FM[2023],
          election_year=2020, sources=[SRC_SOS20H, SRC_C20],
          notes="Official 2020 SOS statewide House summary, House District 4 (right column): Jeremy Haroldson (R) Total 4,227. Official Platte share 3,687; official Converse share 540. Official 2020 Platte clerk H04 Jeremy Haroldson 3,687."),
        T(person_id="WY-HAROLDSON-JEREMY", name="Jeremy Haroldson", party="R", office_group="state-house",
          office="House District 4 (H04)", term_start=FM[2023], term_end=FM[2025],
          election_year=2022, sources=[SRC_SOS22H, SRC_C22],
          notes="Official 2022 SOS statewide House summary, House District 4 (after redistricting: Platte and Laramie): Jeremy Haroldson (R) 2,539, Dan Brecht (I) 1,436. Official Platte share Haroldson 2,495, Brecht 1,425; official Laramie share Haroldson 44, Brecht 11."),
        T(person_id="WY-HAROLDSON-JEREMY", name="Jeremy Haroldson", party="R", office_group="state-house",
          office="House District 4 (H04)", term_start=FM[2025], term_end=FM[2027],
          election_year=2024, sources=[SRC_SOS24H, SRC_C24],
          notes="Official 2024 SOS statewide House summary, House District 4: Jeremy Haroldson (R) 3,516, Charles Randolph (D) 1,014. Official Platte share Haroldson 3,438, Randolph 1,007; official Laramie share Haroldson 78, Randolph 7."),
        T(person_id="WY-HAROLDSON-JEREMY", name="Jeremy Haroldson", party="R", office_group="state-house",
          office="House District 4 (H04)", term_start=FM[2027], term_end=FM[2029],
          election_year=2026, sources=[SRC_SOS26H, SRC_C26],
          notes="Official 2026 SOS statewide House summary, House District 4: Jeremy Haroldson (R) Total 2,533. Official Platte share 2,476; official Laramie share 57."),
    ]
    return terms


def county_terms():
    terms = []
    # Official clerk 2014–2018 general canvasses were not found on the live clerk site or in Wayback captures of media/Elections/* for 2014–2019, so 2019–2022 row-officer seats and the pre-2020 commissioner seats stay Not yet collected.
    terms += [
        T(person_id="WY-MANTLE-KAYLA", name="Kayla Mantle", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, County Commissioner Vote-For-1: Kayla Mantle 4,326."),
        T(person_id="WY-SHOCKLEY-STEVE", name="Steve Shockley", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, County Commissioner Vote-For-2: Steve Shockley 3,007, Ian Jolovich 2,692."),
        T(person_id="WY-JOLOVICH-IAN", name="Ian Jolovich", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, County Commissioner Vote-For-2: Steve Shockley 3,007, Ian Jolovich 2,692."),
        T(person_id="WY-BAKER-JEB", name="Jeb Baker", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, County Commissioner Vote-For-1: Jeb Baker 4,107."),
        T(person_id="WY-SHOCKLEY-STEVE", name="Steve Shockley", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, County Commissioner Vote-For-2: Steve Shockley 2,452, Kayla Mantle 2,227."),
        T(person_id="WY-MANTLE-KAYLA", name="Kayla Mantle", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, County Commissioner Vote-For-2: Steve Shockley 2,452, Kayla Mantle 2,227."),
        T(person_id="WY-ERVIN-MALCOLM-J", name="Malcolm J. Ervin", party="R", office_group="county",
          office="County Clerk", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, County Clerk: Malcolm J. Ervin 3,659."),
        T(person_id="WY-ERVIN-MALCOLM-J", name="Malcolm J. Ervin", party="R", office_group="county",
          office="County Clerk", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, County Clerk: Malcolm J. Ervin 2,839 over Dean S. L. Baker 527."),
        T(person_id="WY-RIETZ-KRISTI", name="Kristi Rietz", party="R", office_group="county",
          office="County Treasurer", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, County Treasurer: Kristi Rietz 3,780."),
        T(person_id="WY-GLOVER-LISA", name="Lisa Glover", party="R", office_group="county",
          office="County Treasurer", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, County Treasurer: Lisa Glover 3,127."),
        T(person_id="WY-EPPEL-DANETTE", name="Danette Eppel", party="R", office_group="county",
          office="County Assessor", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, County Assessor: Danette Eppel 3,610."),
        T(person_id="WY-EPPEL-DANETTE", name="Danette Eppel", party="R", office_group="county",
          office="County Assessor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, County Assessor: Danette Eppel 3,139."),
        T(person_id="WY-RUSSELL-DAVID", name="David Russell", party="R", office_group="county",
          office="County Sheriff", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, County Sheriff: David Russell 3,551. Official 2026 elect Anthony Krotz takes office January 2027; the Phase-1 live roster that listed Tony Krotz as current through January 2027 yields to this official 2022 canvass."),
        T(person_id="WY-KROTZ-ANTHONY", name="Anthony Krotz", party="R", office_group="county",
          office="County Sheriff", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, County Sheriff: Anthony Krotz 3,034."),
        T(person_id="WY-WEAVER-DOUGLAS-W", name="Douglas W. Weaver", party="R", office_group="county",
          office="County Attorney", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, County Attorney: Douglas W. Weaver 3,247."),
        T(person_id="WY-ROTH-MAREL-E-BUNKER", name="Marel E. Bunker Roth", party="R", office_group="county",
          office="County Attorney", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, County Attorney: Marel E. Bunker Roth 2,765. Official name read from the official rendered canvass page."),
        T(person_id="WY-MCAULEY-MONA", name="Mona McAuley", party="R", office_group="county",
          office="Clerk of District Court", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Clerk of District Court: Mona McAuley 3,687."),
        T(person_id="WY-MCAULEY-MONA", name="Mona McAuley", party="R", office_group="county",
          office="Clerk of District Court", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Clerk of District Court: Mona McAuley 3,211."),
        T(person_id="WY-MARTIN-PHILIP-G", name="Philip G. Martin", party="R", office_group="county",
          office="County Coroner", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, County Coroner: Philip G. Martin 3,631. Official 2026 elect Tiffany Gorman Dean takes office January 2027; the Phase-1 live roster that listed Tiffany Dean as current through January 2027 yields to this official 2022 canvass."),
        T(person_id="WY-DEAN-TIFFANY-GORMAN", name="Tiffany Gorman Dean", party="R", office_group="county",
          office="County Coroner", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, County Coroner: Tiffany Gorman Dean 3,215."),
    ]
    return terms


def judicial_terms():
    terms = [
        T(person_id="WY-KORELL-PATRICK-W", name="Patrick W. Korell", party="", office_group="judicial",
          office="District Judge, 8th Judicial District", term_start="2015-10-01", term_end="2022-09-01",
          election_year=2016, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_D],
          notes="Official SOS Judicial Branch directory lists Eighth Judicial District Judge A Patrick W. Korell, appointed October 2015. Official current 8th JD court pages list Edward A. Buchanan, appointed September 2022, in that district; Korell's last day is taken as the first of Buchanan's official appointment month (medium). Start day is the first of the official appointment month. Official Platte clerk 2014–2018 general canvasses were not found, so a Platte retention total for Korell is not keyed here."),
        T(person_id="WY-PEASLEY-F-SCOTT", name="F. Scott Peasley", party="", office_group="judicial",
          office="District Judge, 8th Judicial District", term_start="2017-08-01", term_end=FM[2031],
          election_year=2024, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_D, SRC_C24],
          notes="Official Wyoming Judicial Branch 8th JD District Court page: Hon. F. Scott Peasley, appointed August 2017, retained November 2024, term expires January 2031. Official 2024 Platte clerk RETAIN JUDGE B F. SCOTT PEASLEY: YES 3,396, NO 784. Start day is the first of the official appointment month."),
        T(person_id="WY-BUCHANAN-EDWARD-A", name="Edward A. Buchanan", party="", office_group="judicial",
          office="District Judge, 8th Judicial District", term_start="2022-09-01", term_end=FM[2031],
          election_year=2024, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_D, SRC_C24],
          notes="Official Wyoming Judicial Branch 8th JD District Court page: Hon. Edward A. Buchanan, appointed September 2022, retained November 2024, term expires January 2031. Official 2024 Platte clerk RETAIN JUDGE A EDWARD A. BUCHANAN: YES 3,232, NO 885. Start day is the first of the official appointment month."),
        T(person_id="WY-ARP-RANDAL-R", name="Randal R. Arp", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2015], term_end=FM[2019],
          election_year=2014, sources=[],
          notes="Official 2014 SOS General Election Winners Roster lists Eighth Judicial District Circuit Court Judge Randal R. Arp (same official roster used in the Converse and Goshen history). Official SOS Judicial Branch directory: appointed January 2000. January 2015 is the start of the term following that official 2014 retention. Official Platte clerk 2014 general canvass was not found."),
        T(person_id="WY-ARP-RANDAL-R", name="Randal R. Arp", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2019], term_end=FM[2021],
          election_year=2018, confidence="medium", sources=[],
          notes="Official 2018 SOS statewide judicial summary and official 2018 General Election Winners Roster name Eighth Judicial District Circuit Court Judge Randal R. Arp (same official sources used in the Goshen history). Official 2020 Platte clerk retains Circuit Court Judge Hibben and does not name Arp. The exact official leaving date was not taken from an official court page, so this term is ended at January 2021 when the official 2020 Hibben retention is in effect (medium). Official Platte clerk 2018 general canvass was not found."),
        T(person_id="WY-HIBBEN-NATHANIEL-S", name="Nathaniel S. Hibben", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2021], term_end="2025-05-10",
          election_year=2020, sources=[SRC_C20, SRC_C24],
          notes="Official 2020 Platte clerk CIRCUIT COURT JUDGE HIBBEN: YES 3,555, NO 793. Official 2024 Platte clerk RETAIN JUDGE NATHANIEL SCOTT HIBBEN: YES 3,290, NO 812. Full name Nathaniel S. Hibben is from the official Wyoming Judicial Branch page after his later appointment. Official Judicial Nominating Commission release announced the 8th JD Goshen circuit vacancy effective May 10, 2025."),
        T(person_id="WY-ALLAN-CLARK-C", name="Clark C. Allan", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start="2021-01-01", term_end=FM[2027],
          election_year=2022, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_C, SRC_C26],
          notes="Official Wyoming Judicial Branch 8th JD Converse (Douglas) Circuit Court page: Hon. Clark C. Allan, appointed January 2021, term expires January 2027, stands for retention November 2026. Official 2026 Platte clerk RETAIN (Circuit) Judge Clark C. Allan: YES 2,377, NO 662. Official 2022 Platte clerk has a circuit-court retention line printed as 'EIGHTH JUDICIAL DIST CIRCUIT COURT JUDGE ALL' (YES 2,920, NO 643); that official heading is truncated on the official page and is not used to invent the retained judge's name. Start day is the first of the official appointment month."),
        T(person_id="WY-ALLAN-CLARK-C", name="Clark C. Allan", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_COURT_C],
          notes="Official 2026 Platte clerk, Circuit Judge Clark C. Allan retention: YES 2,377, NO 662."),
        T(person_id="WY-BROWN-JACQUELINE-K", name="Jacqueline K. Brown", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start="2025-07-01", term_end=FM[2027],
          election_year=2026, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_G, SRC_C26],
          notes="Official Wyoming Judicial Branch 8th JD Goshen (Torrington) Circuit Court page: Hon. Jacqueline K. Brown, appointed July 2025, term expires January 2027, stands for retention November 2026. Official 2026 Platte clerk, Circuit Judge Jacqueline K. Brown retention: YES 2,374, NO 680. Official Judicial Branch robing notice lists her as Circuit Court Judge of the 8th JD (Converse, Goshen, Niobrara, and Platte Counties). Start day is the first of the official appointment month."),
        T(person_id="WY-BROWN-JACQUELINE-K", name="Jacqueline K. Brown", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_COURT_G],
          notes="Official 2026 Platte clerk, Circuit Judge Jacqueline K. Brown retention: YES 2,374, NO 680."),
    ]
    return terms


def municipal_terms():
    terms = []
    # Wheatland (official November clerk; four-year terms beginning January)
    terms += [
        T(person_id="WY-GRAVES-BRANDON-R", name="Brandon R. Graves", party="", office_group="municipal",
          office="Wheatland Mayor", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Wheatland Mayor: Brandon R. Graves 1,143."),
        T(person_id="WY-GRAVES-BRANDON-R", name="Brandon R. Graves", party="", office_group="municipal",
          office="Wheatland Mayor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Wheatland Mayor: Brandon R Graves 728 over Kelly Mixson 419."),
        T(person_id="WY-MONTOYA-TONY", name="Tony Montoya", party="", office_group="municipal",
          office="Wheatland Council", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Wheatland Council Vote-For-2: Tony Montoya 1,082, Alan Madsen 933."),
        T(person_id="WY-MADSEN-ALAN", name="Alan Madsen", party="", office_group="municipal",
          office="Wheatland Council", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Wheatland Council Vote-For-2: Tony Montoya 1,082, Alan Madsen 933."),
        T(person_id="WY-KAUFMAN-JOSHUA-J", name="Joshua J. Kaufman", party="", office_group="municipal",
          office="Wheatland Council", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Wheatland Council Vote-For-2: Joshua J. Kaufman 872, William L. Allison 851."),
        T(person_id="WY-ALLISON-WILLIAM-L", name="William L. Allison", party="", office_group="municipal",
          office="Wheatland Council", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Wheatland Council Vote-For-2: Joshua J. Kaufman 872, William L. Allison 851."),
        T(person_id="WY-EVANS-JASON", name="Jason Evans", party="", office_group="municipal",
          office="Wheatland Council", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Wheatland Council Vote-For-2: Jason Evans 1,051, Kelly Mixson 651."),
        T(person_id="WY-MIXSON-KELLY", name="Kelly Mixson", party="", office_group="municipal",
          office="Wheatland Council", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Wheatland Council Vote-For-2: Jason Evans 1,051, Kelly Mixson 651."),
        T(person_id="WY-KAUFMAN-JOSHUA-J", name="Joshua J. Kaufman", party="", office_group="municipal",
          office="Wheatland Council", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Wheatland Council Vote-For-2: Joshua Kaufman 687, Dave Miller 492 (Shirley Lock Keil 412, Scott Perkins 394)."),
        T(person_id="WY-MILLER-DAVE", name="Dave Miller", party="", office_group="municipal",
          office="Wheatland Council", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Wheatland Council Vote-For-2: Joshua Kaufman 687, Dave Miller 492."),
    ]
    # Guernsey
    terms += [
        T(person_id="WY-DELGADO-EDDIE", name="Edward Delgado", party="", office_group="municipal",
          office="Guernsey Council", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Guernsey Council Vote-For-2: Edward Delgado 340, Dale Harris 307. Same person as official 2022 Guernsey Mayor Eddie Delgado."),
        T(person_id="WY-HARRIS-DALE-R", name="Dale R. Harris", party="", office_group="municipal",
          office="Guernsey Council", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Guernsey Council Vote-For-2: Edward Delgado 340, Dale Harris 307."),
        T(person_id="WY-DELGADO-EDDIE", name="Eddie Delgado", party="", office_group="municipal",
          office="Guernsey Mayor", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Guernsey Mayor: Eddie Delgado 267 over Rose M. Martinez 157."),
        T(person_id="WY-REICHERT-SHAWNA", name="Shawna Reichert", party="", office_group="municipal",
          office="Guernsey Mayor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Guernsey Mayor: Shawna Reichert 266 over Michael Fronapfel 166."),
        T(person_id="WY-WELLS-PENNY", name="Penny Wells", party="", office_group="municipal",
          office="Guernsey Council", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Guernsey Council Vote-For-2: Penny Wells 253, Joe Michaels 230."),
        T(person_id="WY-MICHAELS-JOE", name="Joe Michaels", party="", office_group="municipal",
          office="Guernsey Council", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Guernsey Council Vote-For-2: Penny Wells 253, Joe Michaels 230."),
        T(person_id="WY-HARRIS-DALE-R", name="Dale R. Harris", party="", office_group="municipal",
          office="Guernsey Council", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Guernsey Council Vote-For-2: Dale R Harris 374, Jeremiah Fields 288."),
        T(person_id="WY-FIELDS-JEREMIAH", name="Jeremiah Fields", party="", office_group="municipal",
          office="Guernsey Council", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Guernsey Council Vote-For-2: Dale R Harris 374, Jeremiah Fields 288."),
        T(person_id="WY-AUGUSTYN-KELLIE", name="Kellie Augustyn", party="", office_group="municipal",
          office="Guernsey Council", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Guernsey Council Vote-For-2: Kellie Augustyn 297, Jeffery Thomas 256 (Penny Wells 161, Susan Fronapfel 95)."),
        T(person_id="WY-THOMAS-JEFFERY", name="Jeffery Thomas", party="", office_group="municipal",
          office="Guernsey Council", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Guernsey Council Vote-For-2: Kellie Augustyn 297, Jeffery Thomas 256."),
    ]
    # Chugwater
    terms += [
        T(person_id="WY-ASH-CAROL-A", name="Carol A. Ash", party="", office_group="municipal",
          office="Chugwater Mayor", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Chugwater Mayor: Carol A. Ash 67 over Steven Kelley 28."),
        T(person_id="WY-HOPKINS-JOSHUA", name="Joshua Hopkins", party="", office_group="municipal",
          office="Chugwater Mayor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Chugwater Mayor: Joshua Hopkins 63 over Steven Kelley 31. Official 2026 Platte clerk had no Chugwater mayor contest."),
        T(person_id="WY-SKIBA-STEVE", name="Steve Skiba", party="", office_group="municipal",
          office="Chugwater Council", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Chugwater Council Vote-For-2: Steve Skiba 66, Eric C. Marlatt 62."),
        T(person_id="WY-MARLATT-ERIC-C", name="Eric C. Marlatt", party="", office_group="municipal",
          office="Chugwater Council", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Chugwater Council Vote-For-2: Steve Skiba 66, Eric C. Marlatt 62."),
        T(person_id="WY-KELLEY-STEVEN-L", name="Steven L. Kelley", party="", office_group="municipal",
          office="Chugwater Council", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Chugwater Council 4-year Vote-For-2: Steven L. Kelley 57, John Burns 31."),
        T(person_id="WY-BURNS-JOHN", name="John Burns", party="", office_group="municipal",
          office="Chugwater Council", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Chugwater Council 4-year Vote-For-2: Steven L. Kelley 57, John Burns 31."),
        T(person_id="WY-SCHIRMER-JOSEPH-G", name="Joseph G. Schirmer", party="", office_group="municipal",
          office="Chugwater Council", term_start=FM[2023], term_end=FM[2025],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Chugwater Council unexpired 2-year Vote-For-1: Joseph G. Schirmer 74."),
        T(person_id="WY-KLEIN-VICKI-R", name="Vicki R. Klein", party="", office_group="municipal",
          office="Chugwater Council", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Chugwater Council Vote-For-2: Vicki R. Klein 56, Josh Hansen 50."),
        T(person_id="WY-HANSEN-JOSH", name="Josh Hansen", party="", office_group="municipal",
          office="Chugwater Council", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Chugwater Council Vote-For-2: Vicki R. Klein 56, Josh Hansen 50."),
        T(person_id="WY-KELLEY-STEVEN-L", name="Steven L. Kelley", party="", office_group="municipal",
          office="Chugwater Council", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Chugwater Council Vote-For-2: Steven Kelley 48, John Burns 40 (Travis Jorgensen 38, Carol A. Ash 33)."),
        T(person_id="WY-BURNS-JOHN", name="John Burns", party="", office_group="municipal",
          office="Chugwater Council", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Chugwater Council Vote-For-2: Steven Kelley 48, John Burns 40."),
    ]
    # Hartville — official May 6, 2025 canvass has council only; no mayor contest on that official page. Mayor stays NYC.
    terms += [
        T(person_id="WY-TROUPE-KATHERYN", name="Katheryn Troupe", party="", office_group="municipal",
          office="Hartville Council", term_start="2025-06-03", term_end="2029-06-05",
          election_year=2025, sources=[SRC_H25], confidence="medium",
          notes="Official Town of Hartville May 6, 2025 municipal canvass, 4-year council: Katheryn Troupe 16 ACCEPTED, Kari Young 3 ACCEPTED. Start and end days are the first Tuesday in June after the official May election (medium). Official canvass has no mayor contest; the Hartville mayor is Not yet collected rather than taken from a secondary source."),
        T(person_id="WY-YOUNG-KARI", name="Kari Young", party="", office_group="municipal",
          office="Hartville Council", term_start="2025-06-03", term_end="2029-06-05",
          election_year=2025, sources=[SRC_H25], confidence="medium",
          notes="Official Town of Hartville May 6, 2025 municipal canvass, 4-year council: Katheryn Troupe 16 ACCEPTED, Kari Young 3 ACCEPTED. Start and end days medium, as above."),
        T(person_id="WY-HARMON-WILLIAM-SCOTT", name="William Scott Harmon", party="", office_group="municipal",
          office="Hartville Council", term_start="2025-06-03", term_end="2027-06-01",
          election_year=2025, sources=[SRC_H25], confidence="medium",
          notes="Official Town of Hartville May 6, 2025 municipal canvass, 2-year council: William Scott Harmon 15 ACCEPTED, Vern Yenger 6 ACCEPTED. Start and end days medium, as above."),
        T(person_id="WY-YENGER-VERN", name="Vern Yenger", party="", office_group="municipal",
          office="Hartville Council", term_start="2025-06-03", term_end="2027-06-01",
          election_year=2025, sources=[SRC_H25], confidence="medium",
          notes="Official Town of Hartville May 6, 2025 municipal canvass, 2-year council: William Scott Harmon 15 ACCEPTED, Vern Yenger 6 ACCEPTED. Start and end days medium, as above."),
    ]
    # Glendo — official town page (Wayback). Live official site returned 500/406. Official July 8, 2026 capture still lists 2026-ending officers and is not treated as a post-May 2026 current roster. Current Glendo mayor and council stay NYC. Secondary newspaper/WAM names are not encoded.
    terms += [
        T(person_id="WY-JUSCKA-SUSAN", name="Susan Juscka", party="", office_group="municipal",
          office="Glendo Mayor", term_start="2022-06-07", term_end="2026-06-02",
          election_year=2022, sources=[SRC_GLENDO_2024, SRC_GLENDO_2026], confidence="medium",
          notes="Official Town of Glendo government page (Wayback 2024-02-21 and 2026-07-08) lists Mayor Susan Juscka with term year 2026. Official page text: elections every two years the Tuesday after the first Monday in May; terms four years. Start is inferred as June after the official May 2022 cycle (medium). Term ends June 2026. The July 8, 2026 official capture is after the May 2026 election but still lists 2026-ending officers and was not treated as a post-election current roster. Live official minutes and an official 2026 Glendo canvass were not retrieved (live site 500/406). Current (November 2026) Glendo mayor is Not yet collected."),
        T(person_id="WY-SCHOENING-HEATHER", name="Heather Schoening", party="", office_group="municipal",
          office="Glendo Council", term_start="2022-06-07", term_end="2026-06-02",
          election_year=2022, sources=[SRC_GLENDO_2024, SRC_GLENDO_2026], confidence="medium",
          notes="Official Town of Glendo government page (Wayback 2024-02-21 and 2026-07-08) lists Heather Schoening, council, term year 2026. Start and end medium, same official May even-year four-year cycle as the official mayor line. Current Glendo council is Not yet collected."),
        T(person_id="WY-DUGDALE-DAN", name="Dan Dugdale", party="", office_group="municipal",
          office="Glendo Council", term_start="2022-06-07", term_end="2026-06-02",
          election_year=2022, sources=[SRC_GLENDO_2024], confidence="medium",
          notes="Official Town of Glendo government page (Wayback 2024-02-21) lists Dan Dugdale, council, term year 2026. He does not appear on the official July 8, 2026 capture. End date is the official term year 2026 June date (medium); no official vacancy date was found. Current Glendo council is Not yet collected."),
        T(person_id="WY-BROOKS-LACY", name="Lacy Brooks", party="", office_group="municipal",
          office="Glendo Council", term_start="2020-06-02", term_end="2024-06-04",
          election_year=2020, sources=[SRC_GLENDO_2024], confidence="medium",
          notes="Official Town of Glendo government page (Wayback 2024-02-21) lists Lacy Brooks, council, term year 2024. Start is inferred as June after the official May 2020 cycle (medium)."),
        T(person_id="WY-JONES-KELLY-GLENDO", name="Kelly Jones", party="", office_group="municipal",
          office="Glendo Council", term_start="2024-06-04", term_end="2026-06-02",
          election_year=2024, sources=[SRC_GLENDO_2026], confidence="medium",
          notes="Official Town of Glendo government page (Wayback 2026-07-08) lists Kelly Jones, council, term year 2026, in the place of the official 2024-ending Lacy Brooks seat. Official 2024 Glendo canvass was not found; start is inferred as June after the official May 2024 cycle (medium). Current Glendo council is Not yet collected."),
        T(person_id="WY-CUNDALL-JESTON", name="Jeston Cundall", party="", office_group="municipal",
          office="Glendo Council", term_start="2024-06-04", term_end="2026-06-02",
          election_year=2024, sources=[SRC_GLENDO_2026], confidence="medium",
          notes="Official Town of Glendo government page (Wayback 2026-07-08) lists Jeston Cundall, council, term year 2026. Official 2024 Glendo canvass was not found; start is inferred as June after the official May 2024 cycle (medium). Secondary reports that he was sworn as mayor in June 2026 are not official town or SOS sources and are not encoded. Current Glendo mayor and council are Not yet collected."),
    ]
    return terms


def school_terms():
    """Whole-district totals = official Platte clerk + official Goshen sliver. Ranking did not change in any keyed year."""
    terms = []
    # PCSD #1
    terms += [
        T(person_id="WY-ELLER-CONNIE-TWIFORD", name="Connie Twiford Eller", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20, SRC_G20],
          notes="Official 2020 Platte clerk, SD #1 Trustee Vote-For-3: Connie Twiford Eller 1,237, Dustin J. Kafka 1,052, Diane Haroldson 947. Official 2020 Goshen sliver (PC SCHOOL PLATTE Vote-For-3): Eller 4, Kafka 3, Diane Haroldson 3 (Tricia Sagner 20 in the sliver). Combined official totals: Eller 1,241, Kafka 1,055, Diane Haroldson 950 (Sagner 924 remains fourth). Ranking unchanged."),
        T(person_id="WY-KAFKA-DUSTIN-J", name="Dustin J. Kafka", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20, SRC_G20],
          notes="Combined official 2020 Platte+Goshen SD #1 totals: Connie Twiford Eller 1,241, Dustin J. Kafka 1,055, Diane Haroldson 950."),
        T(person_id="WY-HAROLDSON-DIANE", name="Diane Haroldson", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20, SRC_G20],
          notes="Combined official 2020 Platte+Goshen SD #1 totals: Connie Twiford Eller 1,241, Dustin J. Kafka 1,055, Diane Haroldson 950."),
        T(person_id="WY-HOFFMAN-SHAWN", name="Shawn Hoffman", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22, SRC_G22],
          notes="Official 2022 Platte clerk, PCSD #1 Vote-For-4: Shawn Hoffman 1,683, Amanda Fox 1,616, Glenda Lu Lay 1,520, Chase Irvine 1,351 (Travis Witt 1,333 fifth). Official 2022 Goshen sliver: Fox 17, Irvine 15, Lay 15, Hoffman 6, Witt 8. Combined: Hoffman 1,689, Fox 1,633, Lay 1,535, Irvine 1,366 (Witt 1,341 remains fifth). Ranking unchanged."),
        T(person_id="WY-FOX-AMANDA", name="Amanda Fox", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22, SRC_G22],
          notes="Combined official 2022 Platte+Goshen PCSD #1 totals: Shawn Hoffman 1,689, Amanda Fox 1,633, Glenda Lu Lay 1,535, Chase Irvine 1,366."),
        T(person_id="WY-LAY-GLENDA-L", name="Glenda L. Lay", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22, SRC_G22],
          notes="Combined official 2022 Platte+Goshen PCSD #1 totals: Shawn Hoffman 1,689, Amanda Fox 1,633, Glenda L. Lay 1,535, Chase Irvine 1,366."),
        T(person_id="WY-IRVINE-CHASE", name="Chase Irvine", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22, SRC_G22],
          notes="Combined official 2022 Platte+Goshen PCSD #1 totals: Shawn Hoffman 1,689, Amanda Fox 1,633, Glenda L. Lay 1,535, Chase Irvine 1,366."),
        T(person_id="WY-BECKER-CLAY", name="Clay Becker", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24, SRC_G24],
          notes="Official 2024 Platte clerk, PCSD #1 Vote-For-3: Clay Becker 2,265, Douglas Weaver 2,095, Diane Haroldson 1,711 (Mike Haroldson 1,381 fourth). Official 2024 Goshen sliver: Mike Haroldson 16, Becker 15, Diane Haroldson 11, Weaver 10. Combined: Becker 2,280, Weaver 2,105, Diane Haroldson 1,722 (Mike Haroldson 1,397 remains fourth). Ranking unchanged."),
        T(person_id="WY-WEAVER-DOUGLAS-W", name="Douglas W. Weaver", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24, SRC_G24],
          notes="Combined official 2024 Platte+Goshen PCSD #1 totals: Clay Becker 2,280, Douglas Weaver 2,105, Diane Haroldson 1,722. Official 2024 school ballot is Douglas Weaver; same person as official 2022 County Attorney Douglas W. Weaver."),
        T(person_id="WY-HAROLDSON-DIANE", name="Diane Haroldson", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24, SRC_G24],
          notes="Combined official 2024 Platte+Goshen PCSD #1 totals: Clay Becker 2,280, Douglas Weaver 2,105, Diane Haroldson 1,722."),
        T(person_id="WY-HOFFMAN-SHAWN", name="Shawn Anne Hoffman", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_G26],
          notes="Official 2026 Platte clerk, PCSD #1 4-year Vote-For-4 (official rendered page): Shawn Anne Hoffman 1,315, Amanda Fox 1,281, Glenda L. Lay 1,212, Eric E. Jones 1,210 (Chase Irvine 1,129 fifth). Official 2026 Goshen sliver: Hoffman 4, Fox 12, Lay 10, Eric E. Jones 4, Irvine 8. Combined: Hoffman 1,319, Fox 1,293, Lay 1,222, Eric E. Jones 1,214 (Irvine 1,137 remains fifth). Ranking unchanged."),
        T(person_id="WY-FOX-AMANDA", name="Amanda Fox", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_G26],
          notes="Combined official 2026 Platte+Goshen PCSD #1 4-year totals: Shawn Anne Hoffman 1,319, Amanda Fox 1,293, Glenda L. Lay 1,222, Eric E. Jones 1,214."),
        T(person_id="WY-LAY-GLENDA-L", name="Glenda L. Lay", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_G26],
          notes="Combined official 2026 Platte+Goshen PCSD #1 4-year totals: Shawn Anne Hoffman 1,319, Amanda Fox 1,293, Glenda L. Lay 1,222, Eric E. Jones 1,214."),
        T(person_id="WY-JONES-ERIC-E", name="Eric E. Jones", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_G26],
          notes="Combined official 2026 Platte+Goshen PCSD #1 4-year totals: Shawn Anne Hoffman 1,319, Amanda Fox 1,293, Glenda L. Lay 1,222, Eric E. Jones 1,214."),
        T(person_id="WY-MICKELSEN-VICKI", name="Vicki Mickelsen", party="", office_group="schools",
          office="Platte County School District #1 Trustee", term_start=FM[2027], term_end=FM[2029],
          election_year=2026, sources=[SRC_C26, SRC_G26],
          notes="Official 2026 Platte clerk, PCSD #1 2-year Vote-For-1: Vicki Mickelsen 2,294. Official 2026 Goshen sliver 17. Combined official total 2,311."),
    ]
    # PCSD #2
    terms += [
        T(person_id="WY-SEYFANG-SARAH-A", name="Sarah A. Seyfang", party="", office_group="schools",
          office="Platte County School District #2 Trustee", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, SD #2 Trustee Vote-For-3: Sarah Seyfang 579, Gary L. Anderson 462, Jason Cowan 417. No official 2020 Goshen sliver for PCSD #2 was found, so this is the official Platte total."),
        T(person_id="WY-ANDERSON-GARY-L", name="Gary L. Anderson", party="", office_group="schools",
          office="Platte County School District #2 Trustee", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, SD #2 Trustee Vote-For-3: Sarah Seyfang 579, Gary L. Anderson 462, Jason Cowan 417. No official 2020 Goshen sliver for PCSD #2 was found."),
        T(person_id="WY-COWAN-JASON", name="Jason Cowan", party="", office_group="schools",
          office="Platte County School District #2 Trustee", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, SD #2 Trustee Vote-For-3: Sarah Seyfang 579, Gary L. Anderson 462, Jason Cowan 417. No official 2020 Goshen sliver for PCSD #2 was found."),
        T(person_id="WY-REICHERT-SHAWNA", name="Shawna Reichert", party="", office_group="schools",
          office="Platte County School District #2 Trustee", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22, SRC_G22],
          notes="Official 2022 Platte clerk, PCSD #2 4-year Vote-For-2: Shawna Reichert 396, Blaine Ayers 360 (Luke Zapf 330 third). Official 2022 Goshen sliver: Reichert 2, Ayers 2, Zapf 1. Combined: Reichert 398, Ayers 362 (Zapf 331 remains third). Ranking unchanged."),
        T(person_id="WY-AYERS-BLAINE", name="Blaine Ayers", party="", office_group="schools",
          office="Platte County School District #2 Trustee", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22, SRC_G22],
          notes="Combined official 2022 Platte+Goshen PCSD #2 4-year totals: Shawna Reichert 398, Blaine Ayers 362."),
        T(person_id="WY-GROSS-KEVIN-M", name="Kevin M. Gross", party="", office_group="schools",
          office="Platte County School District #2 Trustee", term_start=FM[2023], term_end=FM[2025],
          election_year=2022, sources=[SRC_C22, SRC_G22],
          notes="Official 2022 Platte clerk, PCSD #2 unexpired 2-year: Kevin Gross 332. Official 2022 Goshen sliver: Kevin Gross 2. Combined official total 334."),
        T(person_id="WY-SEYFANG-SARAH-A", name="Sarah A. Seyfang", party="", office_group="schools",
          office="Platte County School District #2 Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24, SRC_G24],
          notes="Official 2024 Platte clerk, PCSD #2 Vote-For-3: Sarah A Seyfang 398, Gary L Anderson 344, Kevin M Gross 295. Official 2024 Goshen sliver: Gross 4, Anderson 2, Seyfang 0. Combined: Seyfang 398, Anderson 346, Gross 299. Ranking unchanged."),
        T(person_id="WY-ANDERSON-GARY-L", name="Gary L. Anderson", party="", office_group="schools",
          office="Platte County School District #2 Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24, SRC_G24],
          notes="Combined official 2024 Platte+Goshen PCSD #2 totals: Sarah A. Seyfang 398, Gary L. Anderson 346, Kevin M. Gross 299."),
        T(person_id="WY-GROSS-KEVIN-M", name="Kevin M. Gross", party="", office_group="schools",
          office="Platte County School District #2 Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24, SRC_G24],
          notes="Combined official 2024 Platte+Goshen PCSD #2 totals: Sarah A. Seyfang 398, Gary L. Anderson 346, Kevin M. Gross 299."),
        T(person_id="WY-AYERS-BLAINE", name="Blaine Ayers", party="", office_group="schools",
          office="Platte County School District #2 Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_G26],
          notes="Official 2026 Platte clerk, PCSD #2 4-year Vote-For-2 (official rendered page): Blaine Ayers 456, Robert Ibarra 395. Official 2026 Goshen sliver: Ibarra 5, Ayers 3. Combined: Ayers 459, Ibarra 400."),
        T(person_id="WY-IBARRA-ROBERT", name="Robert Ibarra", party="", office_group="schools",
          office="Platte County School District #2 Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_G26],
          notes="Combined official 2026 Platte+Goshen PCSD #2 4-year totals: Blaine Ayers 459, Robert Ibarra 400."),
        T(person_id="WY-SEYFANG-DAVID", name="David Seyfang", party="", office_group="schools",
          office="Platte County School District #2 Trustee", term_start=FM[2027], term_end=FM[2029],
          election_year=2026, sources=[SRC_C26, SRC_G26],
          notes="Official 2026 Platte clerk, PCSD #2 2-year Vote-For-1 (official rendered page): David Seyfang 512 (not Sarah A. Seyfang). Official 2026 Goshen sliver 4. Combined official total 516."),
    ]
    return terms


def special_terms():
    terms = []
    # Resource conservation
    terms += [
        T(person_id="WY-GOERTZ-JASON", name="Jason Goertz", party="", office_group="special-districts",
          office="Platte County Resource Conservation District Supervisor", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Conservation Dist Vote-For-2: Jason Goertz 3,525, Jennifer Reyes-Burr 3,250. Official 2020 heading does not split rural/urban/at-large."),
        T(person_id="WY-REYES-BURR-JENNIFER", name="Jennifer Reyes-Burr", party="", office_group="special-districts",
          office="Platte County Resource Conservation District Supervisor", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Conservation Dist Vote-For-2: Jason Goertz 3,525, Jennifer Reyes-Burr 3,250."),
        T(person_id="WY-CLARK-LEVI-D", name="Levi D. Clark", party="", office_group="special-districts",
          office="Platte County Resource Conservation District Rural Supervisor", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Resource Conservation Dist Rural Vote-For-1: Levi D. Clark 3,320."),
        T(person_id="WY-LAUCK-TYLER", name="Tyler Lauck", party="", office_group="special-districts",
          office="Platte County Resource Conservation District Urban Supervisor", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Resource Conservation Dist Urban Vote-For-1: Tyler Lauck 3,322."),
        T(person_id="WY-BROCKMAN-BROOK", name="Brook Brockman", party="", office_group="special-districts",
          office="Platte County Resource Conservation District At-Large Supervisor", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Resource Conservation Dist At-Large Vote-For-1: Brook Brockman 3,235."),
        T(person_id="WY-GOERTZ-JASON", name="Jason Goertz", party="", office_group="special-districts",
          office="Platte County Resource Conservation District Rural Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Resource Conserv Dist Rural Vote-For-2: Jason Goertz 3,401, Jennifer Reyes-Burr 2,949. Official 2024 urban position is write-in totals only (322) with no named certified winner and is not seated."),
        T(person_id="WY-REYES-BURR-JENNIFER", name="Jennifer Reyes-Burr", party="", office_group="special-districts",
          office="Platte County Resource Conservation District Rural Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Resource Conserv Dist Rural Vote-For-2: Jason Goertz 3,401, Jennifer Reyes-Burr 2,949."),
        T(person_id="WY-CLARK-LEVI-D", name="Levi D. Clark", party="", office_group="special-districts",
          office="Platte County Resource Conservation District Rural Supervisor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Resource Dist. Rural Vote-For-1: Levi D Clark 2,928."),
        T(person_id="WY-KAUFMAN-JOSHUA-J", name="Joshua Kaufman", party="", office_group="special-districts",
          office="Platte County Resource Conservation District Urban Supervisor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Resource Dist. Urban Vote-For-1: Joshua Kaufman 2,833. Same person as official Wheatland council member Joshua J. Kaufman."),
        T(person_id="WY-BROCKMAN-BROOK", name="Brook Brockman", party="", office_group="special-districts",
          office="Platte County Resource Conservation District At-Large Supervisor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Resource Dist. At-Large Vote-For-1: Brook Brockman 2,849."),
    ]
    # Senior citizens
    terms += [
        T(person_id="WY-HITT-MERLIN", name="Merlin Hitt", party="", office_group="special-districts",
          office="Senior Citizen Service District Trustee", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Senior Citizen Service Dist Vote-For-3: Merlin Hitt 3,273, Lee Modesitt 3,070, Lana Nelson 3,064."),
        T(person_id="WY-MODESITT-LEE", name="Lee Modesitt", party="", office_group="special-districts",
          office="Senior Citizen Service District Trustee", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Senior Citizen Service Dist Vote-For-3: Merlin Hitt 3,273, Lee Modesitt 3,070, Lana Nelson 3,064."),
        T(person_id="WY-NELSON-LANA", name="Lana Nelson", party="", office_group="special-districts",
          office="Senior Citizen Service District Trustee", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Senior Citizen Service Dist Vote-For-3: Merlin Hitt 3,273, Lee Modesitt 3,070, Lana Nelson 3,064."),
        T(person_id="WY-GRAVES-JILL-R", name="Jill R. Graves", party="", office_group="special-districts",
          office="Senior Citizen Service District Trustee", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Senior Citizen Service Dist 4-year Vote-For-2: Jill R Graves 2,275, Kenneth L Pasley 1,941 (Rose Marie Martinez 1,538 third)."),
        T(person_id="WY-PASLEY-KENNETH-L", name="Kenneth L. Pasley", party="", office_group="special-districts",
          office="Senior Citizen Service District Trustee", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Senior Citizen Service Dist 4-year Vote-For-2: Jill R Graves 2,275, Kenneth L Pasley 1,941."),
        T(person_id="WY-TAYLOR-SARAH", name="Sarah Taylor", party="", office_group="special-districts",
          office="Senior Citizen Service District Trustee", term_start=FM[2023], term_end=FM[2025],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Senior Citizen Service Dist 2-year Vote-For-1: Sarah Taylor 2,170 over Richard Carbona 758."),
        T(person_id="WY-TAYLOR-SARAH", name="Sarah Taylor", party="", office_group="special-districts",
          office="Senior Citizen Service District Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Senior Citizens Serv Dist Trustee Vote-For-3: Sarah Taylor 2,982, Rose Marie Martinez 2,740, write-in totals 190 with no named certified third winner. The third 2024 seat is not invented."),
        T(person_id="WY-MARTINEZ-ROSE-MARIE", name="Rose Marie Martinez", party="", office_group="special-districts",
          office="Senior Citizen Service District Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Senior Citizens Serv Dist Trustee Vote-For-3: Sarah Taylor 2,982, Rose Marie Martinez 2,740."),
        T(person_id="WY-PASLEY-KENNETH-L", name="Kenneth L. Pasley", party="", office_group="special-districts",
          office="Senior Citizen Service District Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Senior Citizen Dist Vote-For-2: Kenneth L. Pasley 2,447, Julie Gentle 2,412."),
        T(person_id="WY-GENTLE-JULIE", name="Julie Gentle", party="", office_group="special-districts",
          office="Senior Citizen Service District Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Senior Citizen Dist Vote-For-2: Kenneth L. Pasley 2,447, Julie Gentle 2,412."),
    ]
    # Hospital
    terms += [
        T(person_id="WY-ORR-JERRY-G", name="Jerry G. Orr", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Hospital Dist Director Vote-For-4: Jerry G. Orr 3,222, Rick L. Bowen 3,049, Britt Wilson 2,998, Lori Modesitt 2,958."),
        T(person_id="WY-BOWEN-RICK-L", name="Rick L. Bowen", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Hospital Dist Director Vote-For-4: Jerry G. Orr 3,222, Rick L. Bowen 3,049, Britt Wilson 2,998, Lori Modesitt 2,958."),
        T(person_id="WY-WILSON-BRITT", name="Britt Wilson", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Hospital Dist Director Vote-For-4: Jerry G. Orr 3,222, Rick L. Bowen 3,049, Britt Wilson 2,998, Lori Modesitt 2,958."),
        T(person_id="WY-MODESITT-LORI", name="Lori Modesitt", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Hospital Dist Director Vote-For-4: Jerry G. Orr 3,222, Rick L. Bowen 3,049, Britt Wilson 2,998, Lori Modesitt 2,958."),
        T(person_id="WY-FREDERICK-CHUCK", name="Chuck Frederick", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Hospital Dist Director Vote-For-3: Chuck Frederick 2,759, Rob Hellbaum 2,675, Debra Shanahan 2,410."),
        T(person_id="WY-HELLBAUM-ROB", name="Rob Hellbaum", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Hospital Dist Director Vote-For-3: Chuck Frederick 2,759, Rob Hellbaum 2,675, Debra Shanahan 2,410."),
        T(person_id="WY-SHANAHAN-DEBRA", name="Debra Shanahan", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Hospital Dist Director Vote-For-3: Chuck Frederick 2,759, Rob Hellbaum 2,675, Debra Shanahan 2,410."),
        T(person_id="WY-MILLIKIN-LISA", name="Lisa Millikin", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Hospital District Dir Vote-For-4: Lisa Millikin 1,823, Tiffany Dean 1,712, Jalea Brockman 1,671, John Watson 1,466."),
        T(person_id="WY-DEAN-TIFFANY-GORMAN", name="Tiffany Dean", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Hospital District Dir Vote-For-4: Lisa Millikin 1,823, Tiffany Dean 1,712, Jalea Brockman 1,671, John Watson 1,466. Same person as official 2026 coroner elect Tiffany Gorman Dean."),
        T(person_id="WY-BROCKMAN-JALEA", name="Jalea Brockman", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Hospital District Dir Vote-For-4: Lisa Millikin 1,823, Tiffany Dean 1,712, Jalea Brockman 1,671, John Watson 1,466."),
        T(person_id="WY-WATSON-JOHN", name="John Watson", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Hospital District Dir Vote-For-4: Lisa Millikin 1,823, Tiffany Dean 1,712, Jalea Brockman 1,671, John Watson 1,466."),
        T(person_id="WY-MICKELSEN-VICKI", name="Vicki Mickelsen", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Hosp. Dist. Vote-For-3: Vicki Mickelsen 2,401, Rod Vineyard 2,362, write-in totals 140 with no named certified third winner. The third 4-year 2026 seat is not invented."),
        T(person_id="WY-VINEYARD-ROD", name="Rod Vineyard", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Hosp. Dist. Vote-For-3: Vicki Mickelsen 2,401, Rod Vineyard 2,362."),
        T(person_id="WY-MODESITT-LORI", name="Lori Modesitt", party="", office_group="special-districts",
          office="Hospital District Director", term_start=FM[2027], term_end=FM[2029],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Hosp. Dist. 2-year Vote-For-1: Lori Modesitt 2,777."),
    ]
    return terms + _fire_cemetery_ems_terms()


def _fire_cemetery_ems_terms():
    terms = []
    terms += [
        T(person_id="WY-OCKINGA-R-KEITH", name="R. Keith Ockinga", party="", office_group="special-districts",
          office="Fire District 1F Director", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, 1-F Fire Dist Vote-For-2: R. Keith Ockinga 923, David Windmeier 894."),
        T(person_id="WY-WINDMEIER-DAVID", name="David Windmeier", party="", office_group="special-districts",
          office="Fire District 1F Director", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, 1-F Fire Dist Vote-For-2: R. Keith Ockinga 923, David Windmeier 894."),
        T(person_id="WY-OCKINGA-R-KEITH", name="R. Keith Ockinga", party="", office_group="special-districts",
          office="Fire District 1F Director", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Fire District 1F Dir Vote-For-2: R. Keith Ockinga 867, David Windmeier 818. Official 2022 1-F director is write-in totals only (102) with no named certified winner and is not seated."),
        T(person_id="WY-WINDMEIER-DAVID", name="David Windmeier", party="", office_group="special-districts",
          office="Fire District 1F Director", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Fire District 1F Dir Vote-For-2: R. Keith Ockinga 867, David Windmeier 818."),
        T(person_id="WY-DERRA-TAYLOR", name="Taylor Derra", party="", office_group="special-districts",
          office="Fire District 1F Director", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Fire District 1F Director Vote-For-1: Taylor Derra 429 over Curtis Walter 302."),
        T(person_id="WY-COLLINS-JAY-B", name="Jay Collins", party="", office_group="special-districts",
          office="Fire District 2F Glendo Zone Director", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, 2-F Fire Dist Vote-For-1: Jay Collins 344."),
        T(person_id="WY-COLLINS-JAY-B", name="Jay B. Collins", party="", office_group="special-districts",
          office="Fire District 2F Glendo Zone Director", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Fire District 2F Dir Glendo Zone Vote-For-1: Jay B Collins 361."),
        T(person_id="WY-FOY-PAUL", name="Paul Foy", party="", office_group="special-districts",
          office="Fire District 2F At-Large Director", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Fire Dist 2-F Dir At Large Vote-For-1: Paul Foy 302. Official 2022 Palmer zone and official 2026 2F at-large are write-in totals only with no named certified winner and are not seated."),
        T(person_id="WY-SMALL-KEN", name="Ken Small", party="", office_group="special-districts",
          office="Fire District 2F Palmer Zone Director", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, 2F Palmer Vote-For-1: Ken Small 252."),
        T(person_id="WY-WEBER-DAVID", name="David Weber", party="", office_group="special-districts",
          office="Antelope Gap Fire District Director", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Antelope Gap FD Vote-For-2: David Weber 117, Anthony Laffitte 114."),
        T(person_id="WY-LAFFITTE-ANTHONY", name="Anthony Laffitte", party="", office_group="special-districts",
          office="Antelope Gap Fire District Director", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Antelope Gap FD Vote-For-2: David Weber 117, Anthony Laffitte 114."),
        T(person_id="WY-WEBER-DAVID", name="David Weber", party="", office_group="special-districts",
          office="Antelope Gap Fire District Director", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Antelope Gap Fire Dist Director Vote-For-2: David Weber 121, Anthony Laffitte 114. Official 2022 Antelope Gap is write-in totals only (27) and is not seated."),
        T(person_id="WY-LAFFITTE-ANTHONY", name="Anthony Laffitte", party="", office_group="special-districts",
          office="Antelope Gap Fire District Director", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Antelope Gap Fire Dist Director Vote-For-2: David Weber 121, Anthony Laffitte 114."),
        T(person_id="WY-MILLER-LYNDON-J", name="Lyndon J. Miller", party="", office_group="special-districts",
          office="Antelope Gap Fire District Director", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Antelope Gap Vote-For-1: Lyndon J. Miller 98."),
        T(person_id="WY-MILLER-DENNIS-E", name="Dennis E. Miller", party="", office_group="special-districts",
          office="Guernsey Rural Fire District Director", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Guernsey Rural Fire Dist Dir Vote-For-2: Dennis E Miller 118, David Warner 108. Official 2020 and official 2024 Guernsey Rural Fire contests are write-in totals only with no named certified winner and are not seated."),
        T(person_id="WY-WARNER-DAVID", name="David Warner", party="", office_group="special-districts",
          office="Guernsey Rural Fire District Director", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Guernsey Rural Fire Dist Dir Vote-For-2: Dennis E Miller 118, David Warner 108."),
        T(person_id="WY-WARNER-DAVID", name="David Warner", party="", office_group="special-districts",
          office="Guernsey Rural Fire District Director", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Guernsey Fire Vote-For-2: David Warner 128, Dennis Miller 125."),
        T(person_id="WY-MILLER-DENNIS-E", name="Dennis Miller", party="", office_group="special-districts",
          office="Guernsey Rural Fire District Director", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Guernsey Fire Vote-For-2: David Warner 128, Dennis Miller 125."),
        T(person_id="WY-ASH-TIM", name="Tim Ash", party="", office_group="special-districts",
          office="Chugwater Fire District Director", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Chug Fire Vote-For-1: Tim Ash 182. Official Platte totals only; official Goshen sliver for this contest was not combined here."),
    ]
    # Cemetery (official Platte totals; official Goshen sliver not combined in this pass)
    terms += [
        T(person_id="WY-JACKSON-KATE", name="Kate Jackson", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Chug Cemetery Vote-For-3: Kate Jackson 145, Ruth Vaughn 138, official named write-in Holly Crowley 21."),
        T(person_id="WY-VAUGHN-RUTH", name="Ruth Vaughn", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Chug Cemetery Vote-For-3: Kate Jackson 145, Ruth Vaughn 138, official named write-in Holly Crowley 21."),
        T(person_id="WY-CROWLEY-HOLLY", name="Holly Crowley", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Chug Cemetery Vote-For-3 lists official named write-in Holly Crowley 21 as the third named person on the official canvass."),
        T(person_id="WY-BAKER-DENNIS", name="Dennis Baker", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Chugwater Cemetery Dist Dir Vote-For-3: Dennis Baker 137, Rob Hellbaum 131, write-in totals 27 with no named certified third winner. The third 2022 seat is not invented."),
        T(person_id="WY-HELLBAUM-ROB", name="Rob Hellbaum", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Platte clerk, Chugwater Cemetery Dist Dir Vote-For-3: Dennis Baker 137, Rob Hellbaum 131."),
        T(person_id="WY-VAUGHN-RUTH", name="Ruth Vaughn", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Chugwater Cemetery Dist Trustee 4-year Vote-For-3: Ruth Vaughn 145, Dean Webster 132, Holly Crowley 131. Official Platte totals only; official Goshen sliver was not combined here."),
        T(person_id="WY-WEBSTER-DEAN", name="Dean Webster", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Chugwater Cemetery Dist Trustee 4-year Vote-For-3: Ruth Vaughn 145, Dean Webster 132, Holly Crowley 131."),
        T(person_id="WY-CROWLEY-HOLLY", name="Holly Crowley", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Chugwater Cemetery Dist Trustee 4-year Vote-For-3: Ruth Vaughn 145, Dean Webster 132, Holly Crowley 131."),
        T(person_id="WY-KELLEY-MICHAEL-L", name="Michael L. Kelley", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2025], term_end=FM[2027],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Platte clerk, Chugwater Cemetery Dist Trustee 2-year Vote-For-1: Michael L Kelley 152."),
        T(person_id="WY-VAUGHN-BLAKE", name="Blake Vaughn", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Chug Cem. 4-year Vote-For-3: Blake Vaughn 91, Kate Jackson 90, Tracy Vaughn 85 (Barbara Fletcher 74 fourth). Official Platte totals only."),
        T(person_id="WY-JACKSON-KATE", name="Kate Jackson", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Chug Cem. 4-year Vote-For-3: Blake Vaughn 91, Kate Jackson 90, Tracy Vaughn 85."),
        T(person_id="WY-VAUGHN-TRACY", name="Tracy Vaughn", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Chug Cem. 4-year Vote-For-3: Blake Vaughn 91, Kate Jackson 90, Tracy Vaughn 85."),
        T(person_id="WY-TETER-DARLA", name="Darla Teter", party="", office_group="special-districts",
          office="Chugwater Cemetery District Trustee", term_start=FM[2027], term_end=FM[2029],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Chug Cem. 2-year Vote-For-1: Darla Teter 132."),
        T(person_id="WY-BAUDER-PAUL", name="Paul Bauder", party="", office_group="special-districts",
          office="Glendo EMS District Director", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Glendo EMS 4-year Vote-For-3: Paul Bauder 235, Lisa Millikin 215, write-in totals 42 with no named certified third winner. The third 4-year seat is not invented."),
        T(person_id="WY-MILLIKIN-LISA", name="Lisa Millikin", party="", office_group="special-districts",
          office="Glendo EMS District Director", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Glendo EMS 4-year Vote-For-3: Paul Bauder 235, Lisa Millikin 215."),
        T(person_id="WY-COLLINS-KATHRYN", name="Kathryn Collins", party="", office_group="special-districts",
          office="Glendo EMS District Director", term_start=FM[2027], term_end=FM[2029],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Platte clerk, Glendo EMS 2-year Vote-For-2: Kathryn Collins 241, write-in totals 25 with no named certified second winner. The second 2-year seat is not invented."),
        T(person_id="WY-ARBOGAST-JAMES-C", name="James C. Arbogast", party="", office_group="special-districts",
          office="Y-O Ranch Service and Improvement District Director", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Y-O Ranch Dist Director Vote-For-2: James C. Arbogast 55, Jason Halvorsen 36. Official 2022 Y-O Ranch is write-in totals only (15) and is not seated."),
        T(person_id="WY-HALVORSEN-JASON", name="Jason Halvorsen", party="", office_group="special-districts",
          office="Y-O Ranch Service and Improvement District Director", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 Platte clerk, Y-O Ranch Dist Director Vote-For-2: James C. Arbogast 55, Jason Halvorsen 36."),
    ]
    return terms


def expected_offices():
    return {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
                      ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
        "state-senate": [("Senate District 2 (S02)", 1), ("Senate District 6 (S06)", 1)],
        "state-house": [("House District 4 (H04)", 1)],
        "county": [("County Commissioner", 3), ("County Clerk", 1), ("County Treasurer", 1),
                   ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
                   ("Clerk of District Court", 1), ("County Coroner", 1)],
        "municipal": [("Wheatland Mayor", 1), ("Wheatland Council", 4),
                      ("Guernsey Mayor", 1), ("Guernsey Council", 4),
                      ("Chugwater Mayor", 1), ("Chugwater Council", 4),
                      ("Hartville Mayor", 1), ("Hartville Council", 4),
                      ("Glendo Mayor", 1), ("Glendo Council", 4)],
        "schools": [("Platte County School District #1 Trustee", 7),
                    ("Platte County School District #2 Trustee", 5)],
        "special-districts": [
            ("Platte County Resource Conservation District Rural Supervisor", 2),
            ("Platte County Resource Conservation District Urban Supervisor", 1),
            ("Platte County Resource Conservation District At-Large Supervisor", 1),
            ("Senior Citizen Service District Trustee", 5),
            ("Hospital District Director", 7),
            ("Fire District 1F Director", 3),
            ("Fire District 2F Glendo Zone Director", 1),
            ("Fire District 2F Palmer Zone Director", 1),
            ("Fire District 2F At-Large Director", 1),
            ("Antelope Gap Fire District Director", 2),
            ("Guernsey Rural Fire District Director", 2),
            ("Chugwater Fire District Director", 1),
            ("Chugwater Cemetery District Trustee", 5),
            ("Glendo EMS District Director", 5),
        ],
        "judicial": [
            ("District Judge, 8th Judicial District", 2),
            ("Circuit Judge, 8th Judicial District", 2),
        ],
    }


def build_platte():
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
        "Platte clerk retentions for Justice Bridget Hill (YES 2,330, NO 745), Justice Robert C. Jarosh (YES 2,211, "
        "NO 742), and Chancery Court Judge Ben Burningham (YES 2,329, NO 690) are those statewide retentions, not "
        "local 8th JD seats. Local rows are 8th Judicial District judges (Converse, Goshen, Niobrara, and Platte). "
        "Full names are taken from official Wyoming Judicial Branch 8th JD court pages and official Platte clerk "
        "retention lines, and those sources are cited. Official 2022 Platte clerk prints 'EIGHTH JUDICIAL DIST "
        "CIRCUIT COURT JUDGE ALL' (YES 2,920, NO 643); that official heading is truncated on the official page and "
        "is not used to invent the retained judge's name. Judges of other districts are not copied here."
    )
    special_note = (
        "County, municipal, school, and special-district names are keyed from official Platte clerk general summaries "
        "(2020, 2022, 2024, and 2026; official 2026 names and totals were read from official rendered page images "
        "because the official PDF text is font-encoded), the official May 6, 2025 Hartville municipal canvass, and "
        "the official Town of Glendo government page retrieved from the Wayback Machine (captures 2024-02-21 and "
        "2026-07-08) because the live official town site returned 500/406. Official 2014–2018 Platte clerk general "
        "canvasses were not found on the live clerk URL patterns, and a Wayback CDX search of media/Elections/* for "
        "2014–2019 returned no captures, so January 2015–2020 county, municipal, school, and special-district rows "
        "are largely Not yet collected rather than invented. Multi-county legislative seats use official SOS "
        "district-wide Total rows, with the official Platte share noted, for every keyed year (2012 and 2016–2020 S02; "
        "2024 and 2026 S06; 2014–2026 H04). Official SOS two-column pages were cut at the next district header. After "
        "2022 redistricting, official SOS S02 is Converse and Natrona only; official Platte S02 is ended at January "
        "2023 rather than inventing a holdover, so January 2023–2024 Platte senate coverage is Not yet collected. "
        "Official S06 begins after the official 2024 election. Official 2016–2020 SOS S06 Platte rows are blank "
        "(Laramie-only on the pre-2022 map) and are not copied as Platte terms. Official Goshen slivers for Platte "
        "County School District #1 and #2 are combined into the official whole-district result in 2020 (PCSD #1 only), "
        "2022, 2024, and 2026; ranking did not change. No official 2020 Goshen sliver for PCSD #2 was found. "
        "Write-in-only official contests with no named certified winner are not seated. The official 2025 Hartville "
        "canvass has no mayor contest, so the Hartville mayor stays Not yet collected. Official July 8, 2026 Glendo "
        "page still lists 2026-ending officers and is not treated as a post-May 2026 current roster; current Glendo "
        "mayor and council stay Not yet collected. Chugwater cemetery and fire rows use official Platte totals; "
        "official Goshen slivers for those contests were not combined here."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. The current (November 2026) precinct "
        "roster is in data/county_officials/platte.json, from the official 2026 Platte primary (named winners only; "
        "7 precincts; write-in-only contests without a named certified winner are not listed)."
    )
    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Platte", county_number=CN, slug=SLUG, terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Platte", slug=SLUG)
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

    # Live 114 shows Taft Love as the current S06 member, matching the official
    # 2026 legislature directory and the live Laramie 114, with a note that the
    # official 2024 general winner was Darin Smith and the mid-term date is not invented.
    if office == "Senate District 6 (S06)":
        love = [t for t in elects if t["person_id"] == "WY-LOVE-TAFT"] or [
            t for t in terms if t["office"] == office and t["person_id"] == "WY-LOVE-TAFT"
        ]
        if love:
            t = sorted(love, key=lambda x: x["term_start"])[-1]
            return [_holder(people, t["person_id"], t["name"], t.get("party") or "", te(t), t.get("notes") or "")]

    def term_len(t):
        try:
            return int(t["term_end"][:4]) - int(t["term_start"][:4])
        except Exception:
            return 4

    departing = [t for t in cur if t["term_end"] == elect_start and t["person_id"] not in {e["person_id"] for e in elects}]
    new_elects = [e for e in elects if e["person_id"] not in current_ids]
    departing = sorted(departing, key=lambda t: (-term_len(t), t["name"]))
    new_elects = sorted(new_elects, key=lambda t: (-term_len(t), t["name"]))
    # Pair same-length terms first (4-year with 4-year, 2-year with 2-year).
    remaining_e = list(new_elects)
    remaining_d = []
    paired = []
    used_e = set()
    for t in departing:
        match = next((e for e in remaining_e if e["person_id"] not in used_e and term_len(e) == term_len(t)), None)
        if match:
            paired.append((t, match))
            used_e.add(match["person_id"])
        else:
            remaining_d.append(t)
    # Do not pair leftover elects to a different-length departing seat.
    departing = [t for t, _ in paired]
    new_elects = [e for _, e in paired]

    # Pair each departing current holder with the next unmatched official January elect.
    succ_map = {}
    for t, e in zip(departing, new_elects):
        succ_map[t["person_id"]] = e
        seen.add(e["person_id"])

    # Reelected currents first (in both cur and elects), then remaining currents.
    for t in elects:
        if t["person_id"] in current_ids and t["person_id"] not in seen:
            out.append(_holder(people, t["person_id"], t["name"], t.get("party") or "", te(t), t.get("notes") or ""))
            seen.add(t["person_id"])
    for t in cur:
        if t["person_id"] in seen:
            continue
        h = _holder(people, t["person_id"], t["name"], t.get("party") or "", te(t), t.get("notes") or "")
        e = succ_map.get(t["person_id"])
        if e:
            h["succeeding"] = {
                "name": e["name"],
                "person_id": e["person_id"],
                "party": e.get("party") or "",
                "takes_office": "January",
            }
        out.append(h)
        seen.add(t["person_id"])
    # Do not add leftover January elects as extra current holders (that would over-count seats).
    return out


def update_platte_json(people, terms):
    path = ROOT / "data" / "county_officials" / "platte.json"
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

    senate = [
        _office("Senate District 6 (S06)", _holders_for_office(terms, people, "Senate District 6 (S06)"),
                note=office_note("Senate District 6 (S06)")),
    ]
    house = [
        _office("House District 4 (H04)", _holders_for_office(terms, people, "House District 4 (H04)"),
                note=office_note("House District 4 (H04)")),
    ]
    county_offices = [
        "County Commissioner", "County Clerk", "County Treasurer", "County Assessor",
        "County Sheriff", "County Attorney", "Clerk of District Court", "County Coroner",
    ]
    county = [_office(o, _holders_for_office(terms, people, o),
                      layout="heading-then-names" if o == "County Commissioner" else "office-and-name",
                      note=office_note(o)) for o in county_offices]
    mun_offices = [
        "Wheatland Mayor", "Wheatland Council",
        "Guernsey Mayor", "Guernsey Council",
        "Chugwater Mayor", "Chugwater Council",
        "Hartville Mayor", "Hartville Council",
        "Glendo Mayor", "Glendo Council",
    ]
    municipal = [_office(o, _holders_for_office(terms, people, o), note=office_note(o),
                         layout="heading-then-names" if "Council" in o else "office-and-name")
                 for o in mun_offices]
    schools = [
        _office("Platte County School District #1 Trustee",
                _holders_for_office(terms, people, "Platte County School District #1 Trustee"),
                note=office_note("Platte County School District #1 Trustee"),
                layout="heading-then-names"),
        _office("Platte County School District #2 Trustee",
                _holders_for_office(terms, people, "Platte County School District #2 Trustee"),
                note=office_note("Platte County School District #2 Trustee"),
                layout="heading-then-names"),
    ]
    special_offices = [
        "Platte County Resource Conservation District Rural Supervisor",
        "Platte County Resource Conservation District Urban Supervisor",
        "Platte County Resource Conservation District At-Large Supervisor",
        "Senior Citizen Service District Trustee",
        "Hospital District Director",
        "Fire District 1F Director",
        "Fire District 2F Glendo Zone Director",
        "Fire District 2F Palmer Zone Director",
        "Fire District 2F At-Large Director",
        "Antelope Gap Fire District Director",
        "Guernsey Rural Fire District Director",
        "Chugwater Fire District Director",
        "Chugwater Cemetery District Trustee",
        "Glendo EMS District Director",
    ]
    specials = [_office(o, _holders_for_office(terms, people, o), note=office_note(o),
                        layout="heading-then-names" if "Trustee" in o or "Director" in o or "Rural" in o or "Supervisor" in o else "office-and-name")
                for o in special_offices]
    judicial = [
        _office("District Judge, 8th Judicial District",
                _holders_for_office(terms, people, "District Judge, 8th Judicial District"),
                note=office_note("District Judge, 8th Judicial District"),
                layout="heading-then-names"),
        _office("Circuit Judge, 8th Judicial District",
                _holders_for_office(terms, people, "Circuit Judge, 8th Judicial District"),
                note=office_note("Circuit Judge, 8th Judicial District"),
                layout="heading-then-names"),
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
    for grp in (senate, house, county, municipal, schools, specials, judicial):
        for rec in grp:
            if not rec.get("holders"):
                rec["holders"] = [{"name": "Not yet collected", "party": "", "term_end": ""}]
    if precincts:
        groups.append(precincts)
    data["groups"] = groups
    data["sources"] = {
        "general_results": URL_C26,
        "primary_results": URL_P26,
        "clerk_archive": URL_ELECTIONS,
        "checked": RETRIEVED,
        "local_archive": "/workspace/wyoleg/local-results/platte/SOURCES.md",
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("updated", path)
    return path
