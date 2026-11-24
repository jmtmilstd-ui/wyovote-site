#!/usr/bin/env python3
"""Carbon County officeholder history (preview). Official clerk, SOS, Sweetwater share,
city, court, and directory sources only. Names are never invented.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import history_lib as H
from history_lib import FM, ROOT, src_dict, term

RETRIEVED = "2026-11-24"
CN = 6
SLUG = "carbon"

# Official Carbon clerk election-results index and DocumentCenter canvasses.
URL_CLERK = "https://www.carboncountywy.gov/997/Election-Results"
URL_C26 = "https://www.carboncountywy.gov/DocumentCenter/View/8663"
URL_C24 = "https://www.carboncountywy.gov/DocumentCenter/View/8170"
URL_C22 = "https://www.carboncountywy.gov/DocumentCenter/View/6386"
URL_C22WI = "https://www.carboncountywy.gov/DocumentCenter/View/6388"
URL_C20 = "https://www.carboncountywy.gov/DocumentCenter/View/5671"
URL_DIR = "https://www.carboncountywy.gov/DocumentCenter/View/8405"
URL_COMM = "https://www.carboncountywy.gov/319/Commissioners"
URL_RAWLINS = "https://www.rawlinswy.gov/178/City-Council"
URL_SW_INDEX = "https://www.sweetwatercountywy.gov/departments/county_clerk/election_returns/index.php"
URL_COURT_2JD = "https://www.wyocourts.gov/court/district-court-2nd-judicial-district-albany-county/"

def S(label, url=""):
    return src_dict(label, url)

SRC_C26 = S("Official Carbon County 2026 general election summary (DocumentCenter 8663; header OFFICIAL RESULTS, 11/05/2026 02:54PM)", URL_C26)
SRC_C24 = S("Official Carbon County 2024 general election summary (DocumentCenter 8170; header OFFICIAL RESULTS, 11/07/2024 02:04PM)", URL_C24)
SRC_C22 = S("Official Carbon County 2022 general election summary (DocumentCenter 6386; header OFFICIAL RESULTS, 11/10/2022 3:48 PM)", URL_C22)
SRC_C22WI = S("Official Carbon County 2022 general certified write-ins (DocumentCenter 6388; canvassed November 10, 2022)", URL_C22WI)
SRC_C18 = S("Official Carbon County 2018 general election summary (header OFFICIAL RESULTS, 11/08/18 10:51:47)", "")
SRC_C20 = S("Official Carbon County 2020 general election summary (PDF header OFFICIAL RESULTS; DocumentCenter slug still says unofficial)", URL_C20)
SRC_DIR = S("Official Carbon County 2026 County Directory (DocumentCenter 8405, revised January 2026)", URL_DIR)
SRC_COMM = S("Official Carbon County Commissioners page", URL_COMM)
SRC_RAWLINS = S("Official City of Rawlins City Council page (Mayor Jacquelin R Wells, At Large, January 2025 through January 2027) and Rawlins Municipal Code 2.04.030", URL_RAWLINS)
SRC_COURT = S("Official Wyoming Judicial Branch, District Court, 2nd Judicial District page", URL_COURT_2JD)
SRC_SW22 = S("Official Sweetwater County 2022 general election summary (official election-returns page)", URL_SW_INDEX)
SRC_SW24 = S("Official Sweetwater County 2024 general election summary (official election-returns page)", URL_SW_INDEX)
SRC_SW26 = S("Official Sweetwater County 2026 general election summary (official election-returns page)", URL_SW_INDEX)

def sos_src(year, chamber):
    return S(
        f"Official Wyoming SOS {year} statewide {chamber} candidates summary (district-wide Total row)",
        "",
    )

def T(**kw):
    kw.setdefault("confidence", "high")
    kw.setdefault("how_took_office", "elected")
    if "sources" not in kw:
        kw["sources"] = []
    return term(**kw)


def register_people(P):
    """Reuse name-index / already-minted IDs; mint only new Carbon-local people."""
    # Legislature (name-index / existing)
    P("WY-HICKS-LARRY", "Larry Hicks", "Larry", "Hicks")
    P("WY-FLEMING-LINDA", "Linda Fleming", "Linda", "Fleming")
    P("WY-STEPHENSON-LEE-ANN", "Lee Ann Stephenson", "Lee Ann", "Stephenson")
    P("WY-WILLIAMS-MICHAEL-RAY", "Michael Ray Williams", "Michael Ray", "Williams")
    P("WY-DAVIS-BOB", "Bob Davis", "Bob", "Davis", aliases='Robert "Bob" Davis|Robert Bob Davis|REP BOB DAVIS')
    P("WY-WILSON-JAMES-A", "James A. Wilson", "James", "Wilson", middle="A.", aliases="Jim Wilson|James A Wilson")
    P("WY-VANMATRE-DON", "Don VanMatre", "Don", "VanMatre")
    P("WY-BURKHART-DONALD", "Donald Burkhart", "Donald", "Burkhart", aliases="Donald Burkhart, Jr|Donald E. Burkhart Jr.")
    P("WY-MARTINEZ-DEBARI-T", "DeBari T. Martinez", "DeBari", "Martinez", middle="T.", aliases="DeBari T Martinez|DEBART T MARTINEZ")
    P("WY-WELLS-JACQUELIN", "Jacquelin R. Wells", "Jacquelin", "Wells", middle="R.", aliases="Jacquelin R Wells|Jacquelin Wells")
    P("WY-THAYER-PAMELA", "Pamela Thayer", "Pamela", "Thayer", aliases="Pam Thayer")
    P("WY-HULME-CHERYL", "Cheryl Hulme", "Cheryl", "Hulme")
    P("WY-GONZALES-PATRICK", "Patrick Gonzales", "Patrick", "Gonzales")
    P("WY-PAXTON-JERRY", "Jerry Paxton", "Jerry", "Paxton")
    P("WY-KONECNY-LELA", "Lela Konecny", "Lela", "Konecny")
    P("WY-OTOOLE-PATRICK", "Eamon O'Toole", "Eamon", "O'Toole", aliases="Patrick Eamon O'Toole")

    # County
    P("WY-MOORE-R-TRAVIS", "R. Travis Moore", "Travis", "Moore", middle="R.", aliases="R Travis Moore|Travis Moore")
    P("WY-JOHNSON-WILLING", 'Willing "John" Johnson', "Willing", "Johnson", aliases="Willing John Johnson|W. John Johnson|John Johnson")
    P("WY-BARTLETT-GWYNN", "Gwynn G. Bartlett", "Gwynn", "Bartlett", middle="G.", aliases="Gwynn Bartlett")
    P("WY-ESPY-JOHN", "John Espy", "John", "Espy")
    P("WY-JONES-SUE", "Sue Jones", "Sue", "Jones")
    P("WY-BARKHURST-BYRON-R", "Byron R. Barkhurst", "Byron", "Barkhurst", middle="R.")
    P("WY-CUIN-DON", "Don Cuin", "Don", "Cuin")
    P("WY-SMITH-LISA-M", "Lisa M. Smith", "Lisa", "Smith", middle="M.", aliases="Lisa Smith")
    P("WY-BENTSEN-PATTY-A", "Patty A. Bentsen", "Patty", "Bentsen", middle="A.")
    P("WY-WEST-LINDSEY", "Lindsey West", "Lindsey", "West")
    P("WY-SNIDER-RENEE", "Renee Snider", "Renee", "Snider")
    P("WY-ZAMORA-PAUL", "Paul Zamora", "Paul", "Zamora")
    P("WY-NYMAN-BRITTANY", "Brittany Nyman", "Brittany", "Nyman")
    P("WY-CASADA-SHAYNA", "Shayna Casada", "Shayna", "Casada")
    P("WY-DAVIS-ASHLEY", "Ashley Davis", "Ashley", "Davis")
    P("WY-HARKINS-SARAH", "Sarah Chavez Harkins", "Sarah", "Harkins", middle="Chavez")
    P("WY-HAGAN-WALTER", "Walter Hagan", "Walter", "Hagan")
    P("WY-ROYBAL-ARCHIE-C", "Archie C. Roybal", "Archie", "Roybal", middle="C.")
    P("WY-BAKKEN-ALEX-S", "Alex S. Bakken", "Alex", "Bakken", middle="S.")
    P("WY-MORRIS-MIKE", "Mike Morris", "Mike", "Morris")
    P("WY-SANGER-MARA-M", "Mara M. Sanger", "Mara", "Sanger", middle="M.")

    # Judicial (reuse Albany / people_additions IDs; full official court names on terms)
    P("WY-DONNELL-JEFFREY", "Jeffrey Donnell", "Jeffrey", "Donnell")
    P("WY-WALDRIP-WADE-E", "Wade E. Waldrip", "Wade", "Waldrip", middle="E.")
    P("WY-SNYDER-DAWNESSA", "Dawnessa A. Snyder", "Dawnessa", "Snyder", middle="A.", aliases="Dawnessa Snyder")
    P("WY-WESTBY-MISHA", "Misha E. Westby", "Misha", "Westby", middle="E.", aliases="Misha Westby")
    P("WY-CASTOR-ROBERT-A", "Robert A. Castor", "Robert", "Castor", middle="A.")
    P("WY-EAKIN-JANE", "Jane Eakin", "Jane", "Eakin")
    P("WY-STIPE-SUSAN-K", "Susan K. Stipe", "Susan", "Stipe", middle="K.")
    P("WY-SANFORD-ROBERT-J", "Robert J. Sanford", "Robert", "Sanford", middle="J.")

    # Municipal — mayors and councils used in 2022–2026 official canvasses
    P("WY-HOWELL-MATT-L", "Matt L. Howell", "Matt", "Howell", middle="L.", aliases="Matthew Lee Howell")
    P("WY-ALLISON-SCOTT", "Scott Allison", "Scott", "Allison")
    P("WY-FERGUSON-SHAN-D", "Shan D. Ferguson", "Shan", "Ferguson", middle="D.", aliases="Shan D Ferguson")
    P("WY-MAYER-GAIL", "Gail Mayer", "Gail", "Mayer")
    P("WY-MCALLISTER-MICHAEL-A", "Michael A. McAllister", "Michael", "McAllister", middle="A.")
    P("WY-MALONEY-MARK", "Mark Maloney", "Mark", "Maloney")
    P("WY-COZZENS-BEN", "Ben Cozzens", "Ben", "Cozzens")
    P("WY-KISNER-DONNY", "Donny Kisner", "Donny", "Kisner")
    P("WY-EVANS-BECKA-T", "Becka T. Evans", "Becka", "Evans", middle="T.", aliases="Becka T Evans")
    P("WY-SEILAFF-MELODIE", "Melodie Seilaff", "Melodie", "Seilaff")
    P("WY-FELDMANN-MATT", "Matt Feldmann", "Matt", "Feldmann")
    P("WY-HAUGER-RAYMOND", "Raymond Hauger", "Raymond", "Hauger")
    P("WY-HEROLD-LORELL", "Lorell Herold", "Lorell", "Herold")
    P("WY-OWENS-CALEB", "Caleb Owens", "Caleb", "Owens")
    P("WY-MIKESELL-RYANNE", "Ryanne Mikesell", "Ryanne", "Mikesell")
    P("WY-IRENE-MORGAN-J", "Morgan J. Irene", "Morgan", "Irene", middle="J.")
    P("WY-MUSTARD-CRAIG", "Craig Mustard", "Craig", "Mustard")
    P("WY-NELSON-WADE", "Wade Nelson", "Wade", "Nelson")
    P("WY-NEEL-JOSEPH-G", "Joseph G. Neel", "Joseph", "Neel", middle="G.", aliases="Joseph Neel")
    P("WY-HOBBS-ANGIE", "Angie Hobbs", "Angie", "Hobbs")
    P("WY-DAVIES-JONES-MEGAN", "Megan Davies-Jones", "Megan", "Davies-Jones")
    P("WY-CRANE-LINDA", "Linda Crane", "Linda", "Crane")
    P("WY-FAGAN-SHANNON", "Shannon Fagan", "Shannon", "Fagan")
    P("WY-MCKINNEY-JIM", "Jim McKinney", "Jim", "McKinney")
    P("WY-MCKINNEY-ASHLEY", "Ashley McKinney", "Ashley", "McKinney")
    P("WY-REICHERT-STEVE", "Steve Reichert", "Steve", "Reichert")
    P("WY-MUNSON-SUSAN", "Susan Munson", "Susan", "Munson")
    P("WY-BANACH-STAS", "Stas Banach", "Stas", "Banach")
    P("WY-WARD-SCOTT", "Scott Ward", "Scott", "Ward")
    P("WY-STULL-GARY", "Gary Stull", "Gary", "Stull")
    P("WY-OSTLING-JON", "Jon Ostling", "Jon", "Ostling")
    P("WY-GEORGE-CHARLIE-T", "Charlie T. George", "Charlie", "George", middle="T.", aliases="Charlie George")
    P("WY-HAWKS-ROGER", "Roger Hawks", "Roger", "Hawks")
    P("WY-SIKES-SAMMY", "Sammy Sikes", "Sammy", "Sikes")
    P("WY-CRUZ-PAUL", "Paul Cruz", "Paul", "Cruz")
    P("WY-WORKS-FREEMAN-ELLEN", "Ellen Works-Freeman", "Ellen", "Works-Freeman")
    P("WY-FELIX-DAVID-G", "David G. Felix", "David", "Felix", middle="G.", aliases="David G Felix")
    P("WY-BEALS-MARCIA", "Marcia Beals", "Marcia", "Beals")
    P("WY-BAILEY-WILLIAM", "William Bailey", "William", "Bailey")
    P("WY-GEORGE-JUSTIN-D", "Justin D. George", "Justin", "George", middle="D.", aliases="Justin George")
    P("WY-SCHOFIELD-LUCINDA-L", "Lucinda L. Schofield", "Lucinda", "Schofield", middle="L.")
    P("WY-FEDERER-CASEY", "Casey Federer", "Casey", "Federer")
    P("WY-COOK-LEE", "Lee Cook", "Lee", "Cook")
    P("WY-WICKIZER-KRISTI", "Kristi Wickizer", "Kristi", "Wickizer")
    P("WY-STRAUCH-TREVOR", "Trevor Strauch", "Trevor", "Strauch")
    P("WY-MAYFIELD-CRYSTAL", "Crystal Mayfield", "Crystal", "Mayfield")
    P("WY-SEILAFF-BRUCE", "Bruce Seilaff", "Bruce", "Seilaff", aliases="Bruce Sielaff")
    P("WY-LEWMAN-TONYA", "Tonya Lewman", "Tonya", "Lewman")
    P("WY-SANGER-STEVE", "Steve Sanger", "Steve", "Sanger")
    P("WY-ELLIOTT-DEREK", "Derek Elliott", "Derek", "Elliott")
    P("WY-GARNER-DARRIL", "Darril Garner", "Darril", "Garner")
    P("WY-PATTERSON-TERRY-B", "Terry B. Patterson", "Terry", "Patterson", middle="B.", aliases="Terry B Patterson")
    P("WY-CRAGUN-MEGAN", "Megan Cragun", "Megan", "Cragun")
    P("WY-MAGAGNA-CRISTY", "Cristy Magagna", "Cristy", "Magagna")
    P("WY-ARCHULETA-EDDIE", "Eddie Archuleta", "Eddie", "Archuleta")
    P("WY-STEPHENSON-LEROY", "Leroy Stephenson", "Leroy", "Stephenson")
    P("WY-LORENZ-FRED", "Fred Lorenz", "Fred", "Lorenz")
    P("WY-GOLDEN-ED", "Ed Golden", "Ed", "Golden")
    P("WY-BROWN-LINDA", "Linda Brown", "Linda", "Brown")
    P("WY-HELWICK-MARK", "Mark Helwick", "Mark", "Helwick")
    P("WY-LORENZ-LISA", "Lisa Lorenz", "Lisa", "Lorenz")
    P("WY-HELWICK-BILLIE", "Billie Helwick", "Billie", "Helwick")
    P("WY-DAVIS-CHUCK", "Chuck Davis", "Chuck", "Davis")
    P("WY-FLUTY-JERRY-J", "Jerry J. Fluty", "Jerry", "Fluty", middle="J.")
    P("WY-FLUTY-JACOB", "Jacob Fluty", "Jacob", "Fluty")
    P("WY-COOLEY-MICHAEL-E", "Michael E. Cooley", "Michael", "Cooley", middle="E.", aliases="Michael Cooley")
    P("WY-OXFORD-CORY", "Cory Oxford", "Cory", "Oxford")
    P("WY-BARKHURST-BUB", "Bub Barkhurst", "Bub", "Barkhurst")
    P("WY-MEEKS-CULLEN", "Cullen Meeks", "Cullen", "Meeks")
    P("WY-GOETZ-EUGENE-J-JR", "Eugene J. Goetz Jr.", "Eugene", "Goetz", middle="J.", aliases="Eugene J Goetz Jr.")
    P("WY-ORTIZ-FOREST-J", "Forest J. Ortiz", "Forest", "Ortiz", middle="J.", aliases="Forest J Ortiz")
    P("WY-ROBINSON-DAVID", "David Robinson", "David", "Robinson")
    P("WY-DUNLAP-BRENNAN-J", "Brennan J. Dunlap", "Brennan", "Dunlap", middle="J.", aliases="Brennan Dunlap")
    P("WY-SERRES-MICHELLE", "Michelle Serres", "Michelle", "Serres")
    P("WY-SANDERS-NANCY-E", "Nancy E. Sanders", "Nancy", "Sanders", middle="E.", aliases="Nancy Sanders")
    P("WY-HALDORSON-STEPHANIE-R", "Stephanie R. Haldorson", "Stephanie", "Haldorson", middle="R.")

    # Schools
    P("WY-EVANS-TANYA-S", "Tanya S. Evans", "Tanya", "Evans", middle="S.", aliases="Tanya Evans")
    P("WY-TAYLOR-BRANDON", "Brandon Taylor", "Brandon", "Taylor")
    P("WY-MANN-MICHAEL-R", "Michael R. Mann", "Michael", "Mann", middle="R.", aliases="Michael R Mann|Michael Mann")
    P("WY-ENGSTROM-CHERYL", "Cheryl Engstrom", "Cheryl", "Engstrom")
    P("WY-GREENE-RICK", "Rick Greene", "Rick", "Greene")
    P("WY-GARCIA-JANETH", "Janeth Garcia", "Janeth", "Garcia")
    P("WY-FLAMIG-RANDY", "Randy Flamig", "Randy", "Flamig")
    P("WY-MASCARENAS-HARLEE", "Harlee Mascarenas", "Harlee", "Mascarenas")
    P("WY-CARRICO-JUSTIN", "Justin Carrico", "Justin", "Carrico")
    P("WY-CONDICT-KAREN-D", "Karen D. Condict", "Karen", "Condict", middle="D.", aliases="Karen Condict")
    P("WY-WESTRING-KASSEY", "Kassey Westring", "Kassey", "Westring")
    P("WY-ZAHN-JANET", "Janet Zahn", "Janet", "Zahn")
    P("WY-JOHNSON-MARIA-L", "Maria L. Johnson", "Maria", "Johnson", middle="L.")
    P("WY-CLARK-PAUL", "Paul Clark", "Paul", "Clark")
    P("WY-MILLER-GEORGIA", "Georgia Miller", "Georgia", "Miller")
    P("WY-GASPARI-JOE", "Joe Gaspari", "Joe", "Gaspari")
    P("WY-WAMSLEY-NICHOLAS", "Nicholas Wamsley", "Nicholas", "Wamsley")
    P("WY-REDDISH-JALEN", "Jalen Reddish", "Jalen", "Reddish")
    P("WY-ANDERSON-MATT", "Matt Anderson", "Matt", "Anderson")

    # Conservation / specials (official named winners)
    P("WY-COBB-JOHN-JACK", 'John (Jack) Cobb', "John", "Cobb", aliases="John R (Jack) Cobb|John R. (Jack) Cobb|JOHN (JACK) COBB")
    P("WY-CHANT-THOMAS", "Thomas Chant", "Thomas", "Chant", aliases="Tom Chant")
    P("WY-LALLY-MEGHAN", "Meghan Lally", "Meghan", "Lally")
    P("WY-ARNELL-TRENT", "Trent Arnell", "Trent", "Arnell")
    P("WY-LARSON-JENNA", "Jenna Larson", "Jenna", "Larson")
    P("WY-PALM-QUADE", "Quade Palm", "Quade", "Palm")
    P("WY-WILLIAMS-OWEN", "Owen Williams", "Owen", "Williams")
    P("WY-BROKAW-RALPH-D", "Ralph D. Brokaw", "Ralph", "Brokaw", middle="D.")
    P("WY-SCHROCK-KAY", "Kay Schrock", "Kay", "Schrock")
    P("WY-HEWARD-TIMOTHY", "Timothy Heward", "Timothy", "Heward")
    P("WY-KERBS-SCOTT", "Scott Kerbs", "Scott", "Kerbs")
    P("WY-STRASSER-ARLA", "Arla Strasser", "Arla", "Strasser")
    P("WY-WILLIAMS-CHRIS", "Chris Williams", "Chris", "Williams")
    P("WY-ARNOLD-RANDY", "Randy Arnold", "Randy", "Arnold")
    P("WY-CORSON-JEFF-D", "Jeff D. Corson", "Jeff", "Corson", middle="D.")
    P("WY-WEBER-CLINT-A", "Clint A. Weber", "Clint", "Weber", middle="A.")
    P("WY-EVANS-GEORGE-JASON", "George Jason Evans", "George Jason", "Evans")
    P("WY-WILLE-DALE", "Dale Wille", "Dale", "Wille")
    P("WY-LEE-VIRGINIA-SUE", "Virginia Sue Lee", "Virginia Sue", "Lee")
    P("WY-ORCHARD-BILL", "Bill Orchard", "Bill", "Orchard")
    P("WY-DUNCAN-WILLIAM", "William Duncan", "William", "Duncan")
    P("WY-MOSS-BARBARA-J", "Barbara J. Moss", "Barbara", "Moss", middle="J.", aliases="Barbara J Moss")
    P("WY-COBB-CYNTHIA-L", "Cynthia L. Cobb", "Cynthia", "Cobb", middle="L.")
    P("WY-STOCKS-KODY", "Kody Stocks", "Kody", "Stocks")
    P("WY-MAXSON-NIKKOLE", "Nikkole Maxson", "Nikkole", "Maxson")
    P("WY-MARTINEZ-TIMMY", "Timmy Martinez", "Timmy", "Martinez")
    P("WY-CAMPBELL-JAMIE", "Jamie Campbell", "Jamie", "Campbell")
    P("WY-WIANT-JAMES", "James Wiant", "James", "Wiant")
    P("WY-ERGER-WANDA", "Wanda Erger", "Wanda", "Erger")
    P("WY-COX-SUZIE", "Suzie Cox", "Suzie", "Cox")
    P("WY-HOWE-SUSAN", "Susan Howe", "Susan", "Howe")
    P("WY-MCVEY-CHARLES", "Charles McVey", "Charles", "McVey")
    P("WY-MCBRIDE-SHAUN", "Shaun McBride", "Shaun", "McBride")
    P("WY-HOWE-EDMUND", "Edmund Howe", "Edmund", "Howe")
    P("WY-DUNCAN-KEITH", "Keith Duncan", "Keith", "Duncan")
    P("WY-WEBER-SHERRY", "Sherry Weber", "Sherry", "Weber")
    P("WY-HICKS-ROX", "Rox Hicks", "Rox", "Hicks")
    P("WY-LEONHARDT-SUSAN-E", "Susan E. Leonhardt", "Susan", "Leonhardt", middle="E.", aliases="Susan E LEONHARDT")
    P("WY-JUSSILA-JOE", "Joe Jussila", "Joe", "Jussila")
    P("WY-ROBERTS-JAMES-N", "James N. Roberts", "James", "Roberts", middle="N.", aliases="James N ROBERTS")
    P("WY-WILLE-ANN", "Ann Wille", "Ann", "Wille")
    P("WY-HEROLD-GWENDALYNN", "Gwendalynn Herold", "Gwendalynn", "Herold")
    P("WY-ERICKSON-DAWNA", "Dawna Erickson", "Dawna", "Erickson")
    P("WY-PERUE-R-RICHARD", "R. Richard Perue", "Richard", "Perue", middle="R.")
    P("WY-MACKAY-SHERRY", "Sherry Mackay", "Sherry", "Mackay")
    P("WY-PATTERSON-CONNIE", "Connie Patterson", "Connie", "Patterson")
    P("WY-BEACH-CAROL-ANN", "Carol Ann Beach", "Carol Ann", "Beach")
    P("WY-SNELL-ROGER", "Roger Snell", "Roger", "Snell")
    P("WY-RYAN-GREGORY", "Gregory Ryan", "Gregory", "Ryan")
    P("WY-ROBINSON-LOGAN", "Logan Robinson", "Logan", "Robinson")
    P("WY-VALDEZ-SCHWARTZ-NANETTE", "Nanette Valdez-Schwartz", "Nanette", "Valdez-Schwartz")
    P("WY-OTOOLE-MEGAN-STOCKLIN", "Megan Stocklin O'Toole", "Megan", "O'Toole", middle="Stocklin")
    P("WY-HARVEY-JACQUELYN", "Jacquelyn Harvey", "Jacquelyn", "Harvey")
    P("WY-MIKESELL-RYAN", "Ryan Mikesell", "Ryan", "Mikesell")
    P("WY-LALLY-BRIAN-J", "Brian J. Lally", "Brian", "Lally", middle="J.", aliases="Brian J Lally|Brian Lally")
    P("WY-KAISLER-DARCY", "Darcy Kaisler", "Darcy", "Kaisler")
    P("WY-TAYLOR-JOSHUA-RYAN", "Joshua Ryan Taylor", "Joshua Ryan", "Taylor")
    P("WY-EMBREE-KAY", "Kay Embree", "Kay", "Embree")
    P("WY-HEWARD-KENDRA", "Kendra Heward", "Kendra", "Heward")
    P("WY-STRAUCH-KENZIE", "Kenzie Strauch", "Kenzie", "Strauch")
    P("WY-COWDIN-SUE", "Sue Cowdin", "Sue", "Cowdin")
    P("WY-COOK-VERNA", "Verna Cook", "Verna", "Cook")
    P("WY-CULVER-CYNTHIA", "Cynthia Culver", "Cynthia", "Culver")
    P("WY-PEREZ-MARIE", "Marie Perez", "Marie", "Perez")
    P("WY-REEVES-JENNIFER", "Jennifer Reeves", "Jennifer", "Reeves")
    P("WY-NEY-COURTNEY", "Courtney Ney", "Courtney", "Ney")
    P("WY-BEACH-HOMER", "Homer Beach", "Homer", "Beach")
    P("WY-PICHE-JAMES-R", 'James R. "Jim" Piche', "James", "Piche", middle="R.", aliases="Jim Piche")
    P("WY-WALISER-PAT", "Pat Waliser", "Pat", "Waliser")
    P("WY-NUHN-CORY-M", "Cory M. Nuhn", "Cory", "Nuhn", middle="M.")
    P("WY-DALEY-JAIMIE", "Jaimie Daley", "Jaimie", "Daley")


def _casner_first_or_skip():
    """2016 official SOS H47 opponent is printed 'Casner (D)'. Do not invent a first name."""
    return None
# 2016 official SOS House District 47 Democratic opponent is printed only as "Casner (D)".
# The official winner (Jerry Paxton) is encoded; no first name is invented for the opponent.


def legislature_terms():
    """Whole-district official SOS totals, with the official Carbon share in the note."""
    terms = []
    # Senate District 11 — 4-year seats, even years 2014/2018/2022/2026. District includes Carbon + Sweetwater, and an Albany sliver in 2014 and 2018.
    s11 = [
        (2014, "WY-HICKS-LARRY", "Larry Hicks", "REP",
         "Official 2014 SOS statewide Senate summary Total: Larry Hicks (R) 3,167, Linda Fleming (D) 1,873. Official Carbon portion: Hicks 2,677, Fleming 1,781. Also covers Sweetwater (429–76) and an Albany sliver (61–16).",
         [sos_src(2014, "Senate")]),
        (2018, "WY-HICKS-LARRY", "Larry Hicks", "REP",
         "Official 2018 SOS statewide Senate summary Total: Larry Hicks (R) 3,757, Lee Ann Stephenson (D) 1,939. Official Carbon portion: Hicks 3,167, Stephenson 1,865. Also covers Sweetwater (495–55) and an Albany sliver (95–19).",
         [sos_src(2018, "Senate")]),
        (2022, "WY-HICKS-LARRY", "Larry Hicks", "REP",
         "Official 2022 SOS statewide Senate summary Total: Larry Hicks (R) 4,153, Michael Ray Williams (C) 1,104. Official Carbon portion: Hicks 3,455, Williams 974. Also covers Sweetwater (698–130). Official Carbon clerk matches the Carbon portion.",
         [sos_src(2022, "Senate"), SRC_C22]),
        (2026, "WY-DAVIS-BOB", "Bob Davis", "REP",
         "Official 2026 SOS statewide Senate summary Total: Bob Davis (R) 3,615, Jim Wilson (D) 1,030, Don VanMatre (C) 297. Official Carbon portion: Davis 3,080, Wilson 863, VanMatre 246. Also covers Sweetwater (535–167–51). Official Carbon clerk matches the Carbon portion.",
         [sos_src(2026, "Senate"), SRC_C26]),
    ]
    for year, pid, name, party, note, srcs in s11:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-senate",
                       office="Senate District 11 (S11)", term_start=FM[year + 1], term_end=FM[year + 5],
                       election_year=year, sources=srcs, notes=note))

    # House District 15 — 2-year. Carbon plus a Sweetwater sliver beginning 2022 (2014–2020 official SOS shows Carbon only).
    h15 = [
        (2014, "WY-BURKHART-DONALD", "Donald Burkhart", "REP",
         "Official 2014 SOS statewide House summary Total: Donald Burkhart (R) 1,700 (Carbon 1,700; no Sweetwater or Albany votes on the official Total row).",
         [sos_src(2014, "House")]),
        (2016, "WY-BURKHART-DONALD", "Donald Burkhart", "REP",
         "Official 2016 SOS statewide House summary, House District 15 county rows (do not use the two-column Total, which also prints House District 16): Donald Burkhart (R) 2,086, DeBari T. Martinez (D) 1,030, all in Carbon.",
         [sos_src(2016, "House")]),
        (2018, "WY-BURKHART-DONALD", "Donald Burkhart", "REP",
         "Official 2018 SOS statewide House summary Total: Donald Burkhart (R) 1,997 (Carbon 1,997; no Sweetwater votes on the official Total row).",
         [sos_src(2018, "House")]),
        (2020, "WY-BURKHART-DONALD", "Donald Burkhart", "REP",
         "Official 2020 SOS statewide House summary, House District 15 county rows (do not use the two-column Total, which also prints House District 16): Donald Burkhart (R) 2,052, Jacquelin Wells (D) 1,144, all in Carbon.",
         [sos_src(2020, "House")]),
        (2022, "WY-BURKHART-DONALD", "Donald Burkhart", "REP",
         "Official 2022 SOS statewide House summary Total: Donald Burkhart (R) 1,552, Patrick Gonzales (L) 602. Official Carbon portion: Burkhart 1,515, Gonzales 600. Official Sweetwater share: 37–2.",
         [sos_src(2022, "House"), SRC_C22]),
        (2024, "WY-THAYER-PAMELA", "Pamela Thayer", "REP",
         "Official 2024 SOS statewide House summary Total: Pamela Thayer (R) 2,790. Official Carbon portion: 2,744. Official Sweetwater share: 46.",
         [sos_src(2024, "House"), SRC_C24]),
        (2026, "WY-THAYER-PAMELA", "Pamela Thayer", "REP",
         "Official 2026 SOS statewide House summary Total: Pamela Thayer (R) 1,499, Cheryl Hulme (C) 398. Official Carbon portion: Thayer 1,471, Hulme 392. Official Sweetwater share: 28–6. Official Carbon clerk matches the Carbon portion.",
         [sos_src(2026, "House"), SRC_C26]),
    ]
    for year, pid, name, party, note, srcs in h15:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-house",
                       office="House District 15 (H15)", term_start=FM[year + 1], term_end=FM[year + 3],
                       election_year=year, sources=srcs, notes=note))

    # House District 47 — 2-year. Official SOS Totals include Carbon plus Sweetwater and, in 2014–2020, an Albany sliver. 2022–2026 official Totals are Carbon + Sweetwater (Albany row is blank).
    h47 = [
        (2014, "WY-PAXTON-JERRY", "Jerry Paxton", "REP",
         "Official 2014 SOS statewide House summary Total: Jerry Paxton (R) 2,480. Official Carbon portion: 1,945. Also covers Sweetwater (464) and an Albany sliver (71).",
         [sos_src(2014, "House")]),
        (2016, "WY-PAXTON-JERRY", "Jerry Paxton", "REP",
         "Official 2016 SOS statewide House summary Total: Jerry Paxton (R) 3,309, Casner (D) 612 (official SOS prints the Democratic opponent by last name only; no first name is added here). Official Carbon portion: Paxton 2,543, Casner 536. Also covers Sweetwater (646–58) and an Albany sliver (120–18).",
         [sos_src(2016, "House")]),
        (2018, "WY-PAXTON-JERRY", "Jerry Paxton", "REP",
         "Official 2018 SOS statewide House summary Total: Jerry Paxton (R) 2,912. Official Carbon portion: 2,269. Also covers Sweetwater (541) and an Albany sliver (102).",
         [sos_src(2018, "House")]),
        (2020, "WY-PAXTON-JERRY", "Jerry Paxton", "REP",
         "Official 2020 SOS statewide House summary Total: Jerry Paxton (R) 3,282, Lela Konecny (L) 886. Official Carbon portion: Paxton 2,505, Konecny 767. Also covers Sweetwater (658–94) and an Albany sliver (119–25).",
         [sos_src(2020, "House")]),
        (2022, "WY-DAVIS-BOB", "Bob Davis", "REP",
         'Official 2022 SOS statewide House summary Total: Robert "Bob" Davis (R) 2,636, Lee Ann Stephenson (D) 656. Official Carbon portion: Davis 1,949, Stephenson 525. Official Sweetwater share: 687–131. Official Carbon clerk matches the Carbon portion.',
         [sos_src(2022, "House"), SRC_C22]),
        (2024, "WY-DAVIS-BOB", "Bob Davis", "REP",
         "Official 2024 SOS statewide House summary Total: Bob Davis (R) 3,488, James A. Wilson (D) 666. Official Carbon portion: Davis 2,570, Wilson 461. Official Sweetwater share: 918–205. Official Carbon clerk matches the Carbon portion.",
         [sos_src(2024, "House"), SRC_C24]),
        (2026, "WY-OTOOLE-PATRICK", "Eamon O'Toole", "REP",
         "Official 2026 SOS statewide House summary Total: Eamon O'Toole (R) 2,523. Official Carbon portion: 1,920. Official Sweetwater share: 603. Official Carbon clerk matches the Carbon portion.",
         [sos_src(2026, "House"), SRC_C26]),
    ]
    for year, pid, name, party, note, srcs in h47:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-house",
                       office="House District 47 (H47)", term_start=FM[year + 1], term_end=FM[year + 3],
                       election_year=year, sources=srcs, notes=note))
    return terms


def county_terms():
    terms = []
    # 2018 official clerk — take office January 2019.
    terms += [
        T(person_id="WY-MOORE-R-TRAVIS", name="R. Travis Moore", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Carbon clerk, commissioner Vote-For-2: R. Travis Moore 3,494, W. John Johnson 3,002."),
        T(person_id="WY-JOHNSON-WILLING", name='Willing "John" Johnson', party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Carbon clerk ballot name W. John Johnson, 3,002."),
        T(person_id="WY-BARKHURST-BYRON-R", name="Byron R. Barkhurst", party="REP", office_group="county",
          office="County Commissioner", role="2-year unexpired", term_start=FM[2019], term_end=FM[2021],
          election_year=2018, sources=[SRC_C18],
          notes="Official 2018 Carbon clerk, commissioner 2-year: Byron R. Barkhurst 3,711, Don Cuin 1,200."),
        T(person_id="WY-BARTLETT-GWYNN", name="Gwynn G. Bartlett", party="REP", office_group="county",
          office="County Clerk", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=[SRC_C18],
          notes="Official 2018 Carbon clerk: Gwynn Bartlett 4,529."),
        T(person_id="WY-BENTSEN-PATTY-A", name="Patty A. Bentsen", party="DEM", office_group="county",
          office="County Treasurer", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=[SRC_C18],
          notes="Official 2018 Carbon clerk: Patty A. Bentsen 4,002."),
        T(person_id="WY-SNIDER-RENEE", name="Renee Snider", party="REP", office_group="county",
          office="County Assessor", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=[SRC_C18],
          notes="Official 2018 Carbon clerk: Renee Snider 3,112, Lindsey West 1,907."),
        T(person_id="WY-ZAMORA-PAUL", name="Paul Zamora", party="REP", office_group="county",
          office="County Coroner", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=[SRC_C18],
          notes="Official 2018 Carbon clerk: Paul Zamora 4,615."),
        T(person_id="WY-DAVIS-ASHLEY", name="Ashley Davis", party="REP", office_group="county",
          office="County Attorney", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=[SRC_C18],
          notes="Official 2018 Carbon clerk: Ashley Davis 4,367."),
        T(person_id="WY-ROYBAL-ARCHIE-C", name="Archie C. Roybal", party="DEM", office_group="county",
          office="County Sheriff", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=[SRC_C18],
          notes="Official 2018 Carbon clerk: Archie C. Roybal 3,356, Walter Hagan 1,756."),
        T(person_id="WY-SANGER-MARA-M", name="Mara M. Sanger", party="REP", office_group="county",
          office="Clerk of District Court", term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=[SRC_C18],
          notes="Official 2018 Carbon clerk: Mara M. Sanger 4,515."),
    ]
    # 2020 official clerk — commissioner Vote-For-3, January 2021–2025.
    for pid, name, votes in (
        ("WY-ESPY-JOHN", "John Espy", "4,515"),
        ("WY-BARKHURST-BYRON-R", "Byron R. Barkhurst", "4,012"),
        ("WY-JONES-SUE", "Sue Jones", "3,778"),
    ):
        terms.append(T(person_id=pid, name=name, party="REP", office_group="county", office="County Commissioner",
                       term_start=FM[2021], term_end=FM[2025], election_year=2020, sources=[SRC_C20],
                       notes=f"Official 2020 Carbon clerk, commissioner Vote-For-3 (PDF header OFFICIAL RESULTS): {name} {votes}."))
    # 2022 official clerk — commissioners VF2 and row officers, January 2023–2027.
    terms += [
        T(person_id="WY-MOORE-R-TRAVIS", name="R. Travis Moore", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Carbon clerk, commissioner Vote-For-2: R. Travis Moore 3,410, Willing \"John\" Johnson 2,889. Official 2026 County Directory and official commissioners page: Chairman, term ends January 2027; official 2026 winner, continues."),
        T(person_id="WY-JOHNSON-WILLING", name='Willing "John" Johnson', party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Carbon clerk ballot name Willing \"John\" Johnson, 2,889. Official 2026 directory lists John Johnson, term ends January 2027; official 2026 winner, continues."),
        T(person_id="WY-BARTLETT-GWYNN", name="Gwynn G. Bartlett", party="REP", office_group="county",
          office="County Clerk", term_start=FM[2023], term_end=FM[2025], election_year=2022, sources=[SRC_C22, SRC_DIR],
          notes="Official 2022 Carbon clerk: Gwynn G. Bartlett 4,291. Official 2024 general had no clerk contest. Official 2026 County Directory lists Lisa M. Smith as clerk 01/2025–12/2026 after Bartlett was elected commissioner in 2024. Term_end is January 2025 (medium as to the exact mid-term day; first Monday used)."),
        T(person_id="WY-NYMAN-BRITTANY", name="Brittany Nyman", party="REP", office_group="county",
          office="County Coroner", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Carbon clerk: Brittany Nyman 4,170."),
        T(person_id="WY-HARKINS-SARAH", name="Sarah Chavez Harkins", party="REP", office_group="county",
          office="County Attorney", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Carbon clerk: Sarah Chavez Harkins 4,070."),
        T(person_id="WY-BAKKEN-ALEX-S", name="Alex S. Bakken", party="REP", office_group="county",
          office="County Sheriff", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Carbon clerk: Alex S. Bakken 3,340, Mike Morris 1,293."),
        T(person_id="WY-WEST-LINDSEY", name="Lindsey West", party="REP", office_group="county",
          office="County Treasurer", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Carbon clerk: Lindsey West 4,072."),
        T(person_id="WY-SNIDER-RENEE", name="Renee Snider", party="REP", office_group="county",
          office="County Assessor", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Carbon clerk: Renee Snider 3,884."),
        T(person_id="WY-SANGER-MARA-M", name="Mara M. Sanger", party="REP", office_group="county",
          office="Clerk of District Court", term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Carbon clerk: Mara M. Sanger 4,263."),
    ]
    # Lisa M. Smith mid-term clerk, official directory 01/2025–12/2026, then official 2026 winner.
    terms.append(T(person_id="WY-SMITH-LISA-M", name="Lisa M. Smith", party="REP", office_group="county",
                   office="County Clerk", term_start=FM[2025], term_end=FM[2027], election_year=None,
                   how_took_office="appointed", confidence="medium", sources=[SRC_DIR],
                   notes="Official 2026 Carbon County Directory (revised January 2026): Clerk Lisa M. Smith (01/2025–12/2026). Official 2024 general has no clerk contest. Official appointment minutes were not collected; start date uses the January 2025 first Monday (medium)."))
    # 2024 official clerk — commissioner Vote-For-3, January 2025–2029.
    for pid, name, votes in (
        ("WY-BARTLETT-GWYNN", "Gwynn G. Bartlett", "4,222"),
        ("WY-ESPY-JOHN", "John Espy", "4,189"),
        ("WY-JONES-SUE", "Sue Jones", "3,483"),
    ):
        terms.append(T(person_id=pid, name=name, party="REP", office_group="county", office="County Commissioner",
                       term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24, SRC_COMM, SRC_DIR],
                       notes=f"Official 2024 Carbon clerk, commissioner Vote-For-3: {name} {votes}. Official commissioners page and 2026 directory: term ends January 2029."))
    # 2026 official clerk — January 2027–2031 (continuing officers).
    cont_2026 = [
        ("WY-MOORE-R-TRAVIS", "R. Travis Moore", "County Commissioner", "3,031"),
        ("WY-JOHNSON-WILLING", 'Willing "John" Johnson', "County Commissioner", "2,553"),
        ("WY-CASADA-SHAYNA", "Shayna Casada", "County Coroner", "3,752"),
        ("WY-HARKINS-SARAH", "Sarah Chavez Harkins", "County Attorney", "3,678"),
        ("WY-BAKKEN-ALEX-S", "Alex S. Bakken", "County Sheriff", "3,849"),
        ("WY-SMITH-LISA-M", "Lisa M. Smith", "County Clerk", "3,714"),
        ("WY-WEST-LINDSEY", "Lindsey West", "County Treasurer", "3,801"),
        ("WY-SNIDER-RENEE", "Renee Snider", "County Assessor", "3,752"),
        ("WY-SANGER-MARA-M", "Mara M. Sanger", "Clerk of District Court", "3,797"),
    ]
    for pid, name, office, votes in cont_2026:
        party = "REP"
        terms.append(T(person_id=pid, name=name, party=party, office_group="county", office=office,
                       term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
                       notes=f"Official 2026 Carbon clerk: {name} {votes}."))
    return terms


def judicial_terms():
    """2nd Judicial District (Carbon and Albany). Full names from official Judicial Branch pages; Carbon clerk retentions cited where named."""
    terms = []
    jsrc = [SRC_COURT]
    # District judges — copy official Albany-aligned dates; add Snyder appointment from official court (July 2017).
    terms += [
        T(person_id="WY-DONNELL-JEFFREY", name="Jeffrey Donnell", office_group="judicial",
          office="District Judge, 2nd Judicial District", term_start="2011-01-03", term_end="2017-01-02",
          how_took_office="retained", sources=jsrc,
          notes="Official 2nd JD district judge (Carbon and Albany). Official 2010 retention dates as used on the official Albany 2nd JD history, from official clerk/SOS retention lines."),
        T(person_id="WY-WALDRIP-WADE-E", name="Wade E. Waldrip", office_group="judicial",
          office="District Judge, 2nd Judicial District", term_start="2013-01-07", term_end="2019-01-07",
          how_took_office="retained", sources=jsrc,
          notes="Official 2nd JD district judge (Carbon and Albany). Full name from official SOS/Judicial Branch usage on the official 2nd JD history."),
        T(person_id="WY-SNYDER-DAWNESSA", name="Dawnessa A. Snyder", office_group="judicial",
          office="District Judge, 2nd Judicial District", term_start="2017-07-01", term_end="2025-01-06",
          how_took_office="appointed", confidence="medium", sources=[SRC_COURT],
          notes="Official Wyoming Judicial Branch 2nd JD page: Dawnessa A. Snyder, appointed July 2017 (day unstated; term_start 2017-07-01, medium), later retained. Official 2018 Carbon clerk has DISTRICT COURT JUDGE A, YES 3,915, without a last name on that line."),
        T(person_id="WY-SNYDER-DAWNESSA", name="Dawnessa A. Snyder", office_group="judicial",
          office="District Judge, 2nd Judicial District", term_start="2025-01-06", term_end="2031-01-06",
          how_took_office="retained", sources=[SRC_C24, SRC_COURT],
          notes="Official 2024 Carbon clerk: DISTRICT COURT - SNYDER, YES 4,506, NO 1,108. Official Judicial Branch: Dawnessa A. Snyder, retained November 2024, term expires January 2031."),
        T(person_id="WY-WESTBY-MISHA", name="Misha E. Westby", office_group="judicial",
          office="District Judge, 2nd Judicial District", term_start="2022-08-01", term_end="2025-01-06",
          how_took_office="appointed", confidence="medium", sources=[SRC_COURT],
          notes="Official Wyoming Judicial Branch 2nd JD page: Misha E. Westby, appointed August 2022 (day unstated; term_start 2022-08-01, medium)."),
        T(person_id="WY-WESTBY-MISHA", name="Misha E. Westby", office_group="judicial",
          office="District Judge, 2nd Judicial District", term_start="2025-01-06", term_end="2031-01-06",
          how_took_office="retained", sources=[SRC_C24, SRC_COURT],
          notes="Official 2024 Carbon clerk: DISTRICT COURT - WESTBY, YES 4,424, NO 1,000. Official Judicial Branch full name Misha E. Westby; term expires January 2031."),
    ]
    terms += [
        T(person_id="WY-CASTOR-ROBERT-A", name="Robert A. Castor", office_group="judicial",
          office="Circuit Judge, 2nd Judicial District", term_start="2011-01-03", term_end="2015-01-05",
          how_took_office="retained", sources=jsrc,
          notes="Official 2nd JD circuit judge (Carbon and Albany). Full name from official SOS Albany general precinct-by-precinct lines."),
        T(person_id="WY-EAKIN-JANE", name="Jane Eakin", office_group="judicial",
          office="Circuit Judge, 2nd Judicial District", term_start="2011-01-03", term_end="2015-01-05",
          how_took_office="retained", sources=jsrc, notes="Official 2nd JD circuit judge (Carbon and Albany)."),
        T(person_id="WY-CASTOR-ROBERT-A", name="Robert A. Castor", office_group="judicial",
          office="Circuit Judge, 2nd Judicial District", term_start="2015-01-05", term_end="2019-01-07",
          how_took_office="retained", sources=jsrc, notes="Official 2014 SOS Albany general precinct-by-precinct: Circuit Court Judge Robert A. Castor, YES."),
        T(person_id="WY-EAKIN-JANE", name="Jane Eakin", office_group="judicial",
          office="Circuit Judge, 2nd Judicial District", term_start="2015-01-05", term_end="2019-01-07",
          how_took_office="retained", sources=jsrc, notes="Official 2014 SOS Albany general precinct-by-precinct: Circuit Court Judge Jane Eakin, YES."),
        T(person_id="WY-STIPE-SUSAN-K", name="Susan K. Stipe", office_group="judicial",
          office="Circuit Judge, 2nd Judicial District", term_start="2021-01-04", term_end="2025-01-06",
          how_took_office="retained", sources=[SRC_COURT],
          notes="Official Judicial Branch full name Susan K. Stipe. Official 2020 retention as used on the official 2nd JD history."),
        T(person_id="WY-STIPE-SUSAN-K", name="Susan K. Stipe", office_group="judicial",
          office="Circuit Judge, 2nd Judicial District", term_start="2025-01-06", term_end="2029-01-01",
          how_took_office="retained", sources=[SRC_C24, SRC_COURT],
          notes="Official 2024 Carbon clerk: CIRCUIT COURT - STIPE, YES 4,427, NO 996. Official Judicial Branch full name Susan K. Stipe."),
        T(person_id="WY-SANFORD-ROBERT-J", name="Robert J. Sanford", office_group="judicial",
          office="Circuit Judge, 2nd Judicial District", term_start="2020-07-01", term_end="2023-01-02",
          how_took_office="appointed", confidence="medium", sources=[SRC_COURT],
          notes="Official Wyoming Judicial Branch 2nd JD circuit page: Robert J. Sanford, appointed July 2020 (day unstated; term_start 2020-07-01, medium)."),
        T(person_id="WY-SANFORD-ROBERT-J", name="Robert J. Sanford", office_group="judicial",
          office="Circuit Judge, 2nd Judicial District", term_start="2023-01-02", term_end="2027-01-04",
          how_took_office="retained", sources=[SRC_C22, SRC_COURT],
          notes="Official 2022 Carbon clerk: CIRCUIT JUDGE - SANFORD, YES 3,568, NO 664. Official Judicial Branch full name Robert J. Sanford."),
        T(person_id="WY-SANFORD-ROBERT-J", name="Robert J. Sanford", office_group="judicial",
          office="Circuit Judge, 2nd Judicial District", term_start="2027-01-04", term_end="2031-01-06",
          how_took_office="retained", sources=[SRC_C26, SRC_COURT],
          notes="Official 2026 Carbon clerk: CIRCUIT JUDGE - SANFORD, YES 3,010, NO 676. Official Judicial Branch full name Robert J. Sanford."),
    ]
    return terms
def _m(pid, name, office, start, end, year, sources, notes, **kw):
    return T(person_id=pid, name=name, office_group="municipal", office=office,
             term_start=start, term_end=end, election_year=year, sources=sources, notes=notes, **kw)


def municipal_terms():
    terms = []
    # ----- 2022 official clerk (January 2023–2027; unexpired 2023–2025) -----
    c22, c22wi = [SRC_C22], [SRC_C22, SRC_C22WI]
    terms += [
        _m("WY-HOWELL-MATT-L", "Matt L. Howell", "Baggs Mayor", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Matt L. Howell 76, Annamarie Waldron 68."),
        _m("WY-FERGUSON-SHAN-D", "Shan D. Ferguson", "Baggs Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Shan D Ferguson 104. Katie Gibson is listed as withdrawn and is not seated."),
        _m("WY-MAYER-GAIL", "Gail Mayer", "Baggs Council", FM[2023], FM[2027], 2022, c22wi,
           "Official 2022 Carbon certified write-ins (canvassed November 10, 2022): Gail Mayer, Baggs Councilperson 4 Year."),
        _m("WY-SEILAFF-MELODIE", "Melodie Seilaff", "Dixon Mayor", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Melodie Seilaff 26."),
        _m("WY-HAUGER-RAYMOND", "Raymond Hauger", "Dixon Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk, council Vote-For-2: Raymond Hauger 28, Lorell Herold 26."),
        _m("WY-HEROLD-LORELL", "Lorell Herold", "Dixon Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Lorell Herold 26."),
        _m("WY-IRENE-MORGAN-J", "Morgan J. Irene", "Elk Mountain Mayor", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Morgan J. Irene 63, Bonni Bruce 32."),
        _m("WY-MUSTARD-CRAIG", "Craig Mustard", "Elk Mountain Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk, council Vote-For-2: Craig Mustard 53, Wade Nelson 52."),
        _m("WY-NELSON-WADE", "Wade Nelson", "Elk Mountain Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Wade Nelson 52."),
        _m("WY-NEEL-JOSEPH-G", "Joseph G. Neel", "Elk Mountain Council", FM[2023], FM[2025], 2022, c22,
           "Official 2022 Carbon clerk, council unexpired: Joseph G. Neel 87."),
        _m("WY-FAGAN-SHANNON", "Shannon Fagan", "Encampment Mayor", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Shannon Fagan 127, Greg A. Salisbury 88."),
        _m("WY-MCKINNEY-ASHLEY", "Ashley McKinney", "Encampment Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk, council Vote-For-2: Ashley McKinney 169, Steve Reichert 99."),
        _m("WY-REICHERT-STEVE", "Steve Reichert", "Encampment Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Steve Reichert 99."),
        _m("WY-OSTLING-JON", "Jon Ostling", "Hanna Mayor", FM[2023], FM[2025], 2022, c22,
           "Official 2022 Carbon clerk: Jon Ostling 126, O.D. \"Oats\" Briggs 110. Official 2024 Hanna mayor 2-year contest seated Charlie T. George in January 2025; this 2022 term is ended at January 2025."),
        _m("WY-HAWKS-ROGER", "Roger Hawks", "Hanna Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk, council Vote-For-2: Roger Hawks 128, Sammy Sikes 96."),
        _m("WY-SIKES-SAMMY", "Sammy Sikes", "Hanna Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Sammy Sikes 96."),
        _m("WY-BAILEY-WILLIAM", "William Bailey", "Medicine Bow Mayor", FM[2023], FM[2025], 2022, c22,
           "Official 2022 Carbon clerk: William Bailey 54, Sharon Biamon 41. Official 2024 Medicine Bow mayor contest seated Justin George in January 2025; this 2022 mayoral term is ended at January 2025."),
        _m("WY-SCHOFIELD-LUCINDA-L", "Lucinda L. Schofield", "Medicine Bow Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk, council Vote-For-2: Lucinda L. Schofield 67, Casey Federer 58."),
        _m("WY-FEDERER-CASEY", "Casey Federer", "Medicine Bow Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Casey Federer 58."),
        _m("WY-SEILAFF-BRUCE", "Bruce Seilaff", "Rawlins City Council Ward 1", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Bruce Seilaff 212, DeBari T Martinez 129. Official City of Rawlins council page spelling is Bruce Seilaff."),
        _m("WY-LEWMAN-TONYA", "Tonya Lewman", "Rawlins City Council Ward 2", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Tonya Lewman 392, Linda Ann Smith 290."),
        _m("WY-SANGER-STEVE", "Steve Sanger", "Rawlins City Council Ward 3", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Steve Sanger 484, Cheryl Hulme 249."),
        _m("WY-STEPHENSON-LEROY", "Leroy Stephenson", "Riverside Mayor", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Leroy Stephenson 29."),
        _m("WY-LORENZ-FRED", "Fred Lorenz", "Riverside Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk, council Vote-For-2: Fred Lorenz 35, Ed Golden 31."),
        _m("WY-GOLDEN-ED", "Ed Golden", "Riverside Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Ed Golden 31."),
        # Riverside 2022 unexpired: official certified write-ins say no candidate received a sufficient amount. Not seated.
        _m("WY-DAVIS-CHUCK", "Chuck Davis", "Saratoga Mayor", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Chuck Davis 448, D'Ron Campbell 240."),
        _m("WY-FLUTY-JERRY-J", "Jerry J. Fluty", "Saratoga Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk, council Vote-For-2: Jerry J. Fluty 537, Jacob Fluty 474."),
        _m("WY-FLUTY-JACOB", "Jacob Fluty", "Saratoga Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Jacob Fluty 474."),
        _m("WY-COOLEY-MICHAEL-E", "Michael E. Cooley", "Saratoga Council", FM[2023], FM[2025], 2022, c22,
           "Official 2022 Carbon clerk, council unexpired: Michael Cooley 574."),
        _m("WY-MEEKS-CULLEN", "Cullen Meeks", "Sinclair Mayor", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: Cullen Meeks 77, Phyllis McWhorter 47."),
        _m("WY-ORTIZ-FOREST-J", "Forest J. Ortiz", "Sinclair Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk, council Vote-For-2: Forest J Ortiz 64."),
        _m("WY-ROBINSON-DAVID", "David Robinson", "Sinclair Council", FM[2023], FM[2027], 2022, c22,
           "Official 2022 Carbon clerk: David Robinson 54, listed as WINNER OF TIE BREAKER over Ellie Bennett 54. Official canvass seated Robinson."),
        _m("WY-DUNLAP-BRENNAN-J", "Brennan J. Dunlap", "Sinclair Council", FM[2023], FM[2025], 2022, c22,
           "Official 2022 Carbon clerk, council unexpired: Brennan J. Dunlap 73, Vicki L. Gabelson 44."),
    ]
    # Hanna 2022 mayor ended early because official 2024 2-year mayor contest was held — adjust Ostling term_end already set 2025.
    # Medicine Bow 2022 mayor ended 2025 because official 2024 mayor contest was held.

    # ----- 2024 official clerk -----
    c24 = [SRC_C24]
    terms += [
        _m("WY-MCALLISTER-MICHAEL-A", "Michael A. McAllister", "Baggs Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk, council Vote-For-2: Michael A. McAllister 138."),
        _m("WY-MALONEY-MARK", "Mark Maloney", "Baggs Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk: write-in totals 17, and the official summary names Mark Maloney as elected with write-in votes."),
        _m("WY-COZZENS-BEN", "Ben Cozzens", "Baggs Council", FM[2025], FM[2027], 2024, c24,
           "Official 2024 Carbon clerk, council 2-year: official summary names Ben Cozzens as elected with write-in votes (18)."),
        _m("WY-OWENS-CALEB", "Caleb Owens", "Dixon Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk, council Vote-For-2: Caleb Owens 36, Ryanne Mikesell 35."),
        _m("WY-MIKESELL-RYANNE", "Ryanne Mikesell", "Dixon Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk: Ryanne Mikesell 35."),
        _m("WY-NEEL-JOSEPH-G", "Joseph G. Neel", "Elk Mountain Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk, council Vote-For-2: Joseph Neel 75, Angie Hobbs 73."),
        _m("WY-HOBBS-ANGIE", "Angie Hobbs", "Elk Mountain Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk: Angie Hobbs 73."),
        _m("WY-MUNSON-SUSAN", "Susan Munson", "Encampment Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk, council Vote-For-2: Susan Munson 150, Stas Banach 135."),
        _m("WY-BANACH-STAS", "Stas Banach", "Encampment Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk: Stas Banach 135."),
        _m("WY-GEORGE-CHARLIE-T", "Charlie T. George", "Hanna Mayor", FM[2025], FM[2027], 2024, c24,
           "Official 2024 Carbon clerk, Hanna mayor 2-year: Charlie T. George 200, Orville 'Oats' Briggs 85."),
        _m("WY-CRUZ-PAUL", "Paul Cruz", "Hanna Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk, council Vote-For-2: Paul Cruz 202, Ellen Works-Freeman 124."),
        _m("WY-WORKS-FREEMAN-ELLEN", "Ellen Works-Freeman", "Hanna Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk: Ellen Works-Freeman 124."),
        _m("WY-GEORGE-JUSTIN-D", "Justin D. George", "Medicine Bow Mayor", FM[2025], FM[2027], 2024, c24,
           "Official 2024 Carbon clerk: Justin George 71, Troy W. Maddox Sr. 40. Official 2026 ballot is Justin D. George."),
        _m("WY-COOK-LEE", "Lee Cook", "Medicine Bow Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk, council Vote-For-2: Lee Cook 67, Kristi Wickizer 62."),
        _m("WY-WICKIZER-KRISTI", "Kristi Wickizer", "Medicine Bow Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk: Kristi Wickizer 62."),
        _m("WY-STRAUCH-TREVOR", "Trevor Strauch", "Medicine Bow Council", FM[2025], FM[2027], 2024, c24,
           "Official 2024 Carbon clerk, council 2-year Vote-For-2: Trevor Strauch 96, Crystal Mayfield 73."),
        _m("WY-MAYFIELD-CRYSTAL", "Crystal Mayfield", "Medicine Bow Council", FM[2025], FM[2027], 2024, c24,
           "Official 2024 Carbon clerk, council 2-year: Crystal Mayfield 73."),
        _m("WY-ELLIOTT-DEREK", "Derek Elliott", "Rawlins City Council Ward 1", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk: Derek Elliott 303, De Shann B. Schinkel 272. Official City of Rawlins council page: Ward 1, January 2025–January 2029."),
        _m("WY-GARNER-DARRIL", "Darril Garner", "Rawlins City Council Ward 2", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk: Darril Garner 713, Stanley Bugg 344. Official City of Rawlins council page: Vice Mayor, Ward 2, January 2025–January 2027 is the vice-mayor designation; the elected council term on that page is January 2025 through January 2027 for the vice-mayor line and the official 2024 4-year win is used here through January 2029."),
        _m("WY-PATTERSON-TERRY-B", "Terry B. Patterson", "Rawlins City Council Ward 3", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk: Terry B Patterson 624, Patrick Gonzales 384. Official City of Rawlins council page: Ward 3, January 2025–January 2029."),
        _m("WY-WELLS-JACQUELIN", "Jacquelin R. Wells", "Rawlins Mayor", FM[2025], FM[2027], 2024, [SRC_RAWLINS],
           "The Rawlins mayor is chosen by the city council from its members, not on the November ballot (official Rawlins Municipal Code 2.04.030). Official City of Rawlins City Council page: Mayor Jacquelin R Wells, At Large, January 2025 through January 2027. The January 2027 mayor is not named; the council elects in January 2027.",
           how_took_office="selected by council"),
        _m("WY-WELLS-JACQUELIN", "Jacquelin R. Wells", "Rawlins City Council At-Large", FM[2025], FM[2027], 2024, [SRC_RAWLINS],
           "Official City of Rawlins City Council page: Jacquelin R Wells, At Large, January 2025 through January 2027 (also serving as mayor). How she first won the at-large seat is not re-keyed from a 2024 clerk mayor/at-large contest (none appeared); the official current council page is the source.",
           how_took_office="selected by council", confidence="medium"),
        _m("WY-BROWN-LINDA", "Linda Brown", "Riverside Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk, council Vote-For-2: Linda Brown 43, Mark Helwick 29."),
        _m("WY-HELWICK-MARK", "Mark Helwick", "Riverside Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk: Mark Helwick 29."),
        _m("WY-LORENZ-LISA", "Lisa Lorenz", "Riverside Council", FM[2025], FM[2027], 2024, c24,
           "Official 2024 Carbon clerk, council 2-year: Lisa Lorenz 49."),
        _m("WY-COOLEY-MICHAEL-E", "Michael E. Cooley", "Saratoga Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk, council Vote-For-2: Michael E. Cooley 590, Cory Oxford 586."),
        _m("WY-OXFORD-CORY", "Cory Oxford", "Saratoga Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk: Cory Oxford 586."),
        _m("WY-BARKHURST-BUB", "Bub Barkhurst", "Saratoga Council", FM[2025], FM[2027], 2024, c24,
           "Official 2024 Carbon clerk, council 2-year: Bub Barkhurst 557, Sophia Borg 275."),
        _m("WY-SERRES-MICHELLE", "Michelle Serres", "Sinclair Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk, council Vote-For-2: Michelle Serres 110, Brennan Dunlap 109."),
        _m("WY-DUNLAP-BRENNAN-J", "Brennan J. Dunlap", "Sinclair Council", FM[2025], FM[2029], 2024, c24,
           "Official 2024 Carbon clerk: Brennan Dunlap 109."),
        _m("WY-SANDERS-NANCY-E", "Nancy E. Sanders", "Sinclair Council", FM[2025], FM[2027], 2024, c24,
           "Official 2024 Carbon clerk, council 2-year: Nancy Sanders 128."),
    ]

    # ----- 2026 official clerk (January 2027–2031; 2-year unexpired 2027–2029) -----
    c26 = [SRC_C26]
    terms += [
        _m("WY-ALLISON-SCOTT", "Scott Allison", "Baggs Mayor", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Scott Allison 92, Matthew Lee Howell 31."),
        _m("WY-FERGUSON-SHAN-D", "Shan D. Ferguson", "Baggs Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk, council Vote-For-2: Shan D Ferguson 76, Donny Kisner 62."),
        _m("WY-KISNER-DONNY", "Donny Kisner", "Baggs Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Donny Kisner 62."),
        _m("WY-EVANS-BECKA-T", "Becka T. Evans", "Baggs Council", FM[2027], FM[2029], 2026, c26,
           "Official 2026 Carbon clerk, council 2-year unexpired: Becka T Evans 95."),
        _m("WY-FELDMANN-MATT", "Matt Feldmann", "Dixon Mayor", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Matt Feldmann 27."),
        _m("WY-HAUGER-RAYMOND", "Raymond Hauger", "Dixon Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk, council Vote-For-2: Raymond Hauger 26. No second named winner is printed; write-in totals 6 are not certified to a named candidate on the official summary. A second January 2027 seat is left unfilled rather than invented."),
        _m("WY-IRENE-MORGAN-J", "Morgan J. Irene", "Elk Mountain Mayor", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Morgan J. Irene 72."),
        _m("WY-DAVIES-JONES-MEGAN", "Megan Davies-Jones", "Elk Mountain Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk, council Vote-For-2: Megan Davies-Jones 57, Linda Crane 51."),
        _m("WY-CRANE-LINDA", "Linda Crane", "Elk Mountain Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Linda Crane 51."),
        _m("WY-MCKINNEY-JIM", "Jim McKinney", "Encampment Mayor", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Jim McKinney 153, Greg A. Salisbury 45."),
        _m("WY-WARD-SCOTT", "Scott Ward", "Encampment Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk, council Vote-For-2: Scott Ward 130, Gary Stull 90."),
        _m("WY-STULL-GARY", "Gary Stull", "Encampment Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Gary Stull 90."),
        _m("WY-GEORGE-CHARLIE-T", "Charlie T. George", "Hanna Mayor", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Charlie T. George 145, Anthony \"Tony\" Poulos 74."),
        _m("WY-FELIX-DAVID-G", "David G. Felix", "Hanna Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk, council Vote-For-2: David G Felix 122, Marcia Beals 107."),
        _m("WY-BEALS-MARCIA", "Marcia Beals", "Hanna Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Marcia Beals 107."),
        _m("WY-GEORGE-JUSTIN-D", "Justin D. George", "Medicine Bow Mayor", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Justin D. George 58, Aaron Kovar 26."),
        _m("WY-STRAUCH-TREVOR", "Trevor Strauch", "Medicine Bow Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk, council Vote-For-2: Trevor Strauch 79, Crystal Mayfield 66."),
        _m("WY-MAYFIELD-CRYSTAL", "Crystal Mayfield", "Medicine Bow Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Crystal Mayfield 66."),
        _m("WY-CRAGUN-MEGAN", "Megan Cragun", "Rawlins City Council Ward 1", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Megan Cragun 196, Bruce Seilaff 153."),
        _m("WY-MAGAGNA-CRISTY", "Cristy Magagna", "Rawlins City Council Ward 2", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Cristy Magagna 570."),
        _m("WY-SANGER-STEVE", "Steve Sanger", "Rawlins City Council Ward 3", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Steve Sanger 377, Cody Bluth 247. Continues from the official 2022 term."),
        _m("WY-ARCHULETA-EDDIE", "Eddie Archuleta", "Rawlins City Council At-Large", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk, at-large: Eddie Archuleta 910. The January 2027 Rawlins mayor is not on this ballot; the council chooses the mayor under official code 2.04.030, and that January 2027 choice is not invented."),
        _m("WY-STEPHENSON-LEROY", "Leroy Stephenson", "Riverside Mayor", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Leroy Stephenson 29."),
        _m("WY-LORENZ-LISA", "Lisa Lorenz", "Riverside Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk, council Vote-For-2: Lisa Lorenz 37, Billie Helwick 28."),
        _m("WY-HELWICK-BILLIE", "Billie Helwick", "Riverside Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Billie Helwick 28."),
        _m("WY-DAVIS-CHUCK", "Chuck Davis", "Saratoga Mayor", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Chuck Davis 521."),
        _m("WY-BARKHURST-BUB", "Bub Barkhurst", "Saratoga Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk, council Vote-For-2: Bub Barkhurst 380, Jerry J. Fluty 375."),
        _m("WY-FLUTY-JERRY-J", "Jerry J. Fluty", "Saratoga Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Jerry J. Fluty 375."),
        _m("WY-GOETZ-EUGENE-J-JR", "Eugene J. Goetz Jr.", "Sinclair Mayor", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Eugene J Goetz Jr. 54, Cullen Meeks 51."),
        _m("WY-SANDERS-NANCY-E", "Nancy E. Sanders", "Sinclair Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk, council Vote-For-2: Nancy E. Sanders 66, Stephanie R. Haldorson 62."),
        _m("WY-HALDORSON-STEPHANIE-R", "Stephanie R. Haldorson", "Sinclair Council", FM[2027], FM[2031], 2026, c26,
           "Official 2026 Carbon clerk: Stephanie R. Haldorson 62."),
    ]
    return terms
def _s(pid, name, office, start, end, year, sources, notes, **kw):
    return T(person_id=pid, name=name, office_group="schools", office=office,
             term_start=start, term_end=end, election_year=year, sources=sources, notes=notes, **kw)


def _d(pid, name, office, start, end, year, sources, notes, **kw):
    return T(person_id=pid, name=name, office_group="special-districts", office=office,
             term_start=start, term_end=end, election_year=year, sources=sources, notes=notes, **kw)


def school_terms():
    terms = []
    # 2022 CCSD #1 VF3 — official Carbon plus official Sweetwater share (official Carbon page requires the combination).
    note_22_sd1 = (
        "Official 2022 Carbon clerk, School District 1 Vote-For-3: Tanya S. Evans 1,379, Brandon Taylor 1,314, "
        "Michael R. Mann 1,213, Michael Young 1,126. Official Sweetwater 2022 general (SD#1 Carbon Vote-For-3): "
        "Taylor 21, Evans 19, Young 15, Mann 11. Combined official totals: Evans 1,398, Taylor 1,335, Mann 1,224, Young 1,141. "
        "The official Carbon election-results page states that Sweetwater results must be added for School District #1."
    )
    src_22_sd1 = [SRC_C22, SRC_SW22]
    for pid, name in (
        ("WY-EVANS-TANYA-S", "Tanya S. Evans"),
        ("WY-TAYLOR-BRANDON", "Brandon Taylor"),
        ("WY-MANN-MICHAEL-R", "Michael R. Mann"),
    ):
        terms.append(_s(pid, name, "Carbon County School District #1 Trustee", FM[2023], FM[2027], 2022, src_22_sd1, note_22_sd1))
    # 2022 CCSD #2
    terms += [
        _s("WY-GEORGE-CHARLIE-T", "Charlie T. George", "Carbon County School District #2 Area 1 Trustee",
           FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 Carbon clerk, School Dist 2 Area 1 was write-in only (184). Official 2022 certified write-ins: Charlie George, Carbon County School District 2, Area 1."),
        _s("WY-CONDICT-KAREN-D", "Karen D. Condict", "Carbon County School District #2 Area 2 Trustee",
           FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, School Dist 2 Area 2: Karen Condict 1,735."),
        _s("WY-WESTRING-KASSEY", "Kassey Westring", "Carbon County School District #2 Area 3 Trustee",
           FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, School Dist 2 Area 3: Kassey Westring 1,281, Janet Zahn 406."),
        _s("WY-JOHNSON-MARIA-L", "Maria L. Johnson", "Carbon County School District #2 Area 4 Trustee",
           FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, School Dist 2 Area 4 Vote-For-2: Maria L. Johnson 1,608."),
        _s("WY-ZAHN-JANET", "Janet Zahn", "Carbon County School District #2 Area 4 Trustee",
           FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 Carbon certified write-ins: Janet Zahn, Carbon County School District 2, Area 4 (At-Large). Official 2022 clerk write-in totals 80."),
    ]
    # 2024 CCSD #1 VF4 + 2yr, plus official Sweetwater shares. Official Carbon page requires the combination. 2yr Flamig official SW also listed (36); Carbon page note on the 4-year contest.
    note_24_sd1 = (
        "Official 2024 Carbon clerk, School District 1 Vote-For-4: Cheryl Engstrom 2,365, Rick Greene 2,144, Matt Feldmann 1,810, "
        "write-in totals 198 (official summary: Janeth Garcia was elected with write-in votes). "
        "Official Sweetwater 2024 general, District #1 Carbon County Trustee Vote-For-4: Engstrom 33, Feldmann 18, Greene 16, write-in 1. "
        "Combined official totals: Engstrom 2,398, Greene 2,160, Feldmann 1,828, plus official Carbon-certified write-in winner Janeth Garcia. "
        "The official Carbon summary states that results for this race must be combined with Sweetwater County."
    )
    src_24_sd1 = [SRC_C24, SRC_SW24]
    for pid, name in (
        ("WY-ENGSTROM-CHERYL", "Cheryl Engstrom"),
        ("WY-GREENE-RICK", "Rick Greene"),
        ("WY-FELDMANN-MATT", "Matt Feldmann"),
        ("WY-GARCIA-JANETH", "Janeth Garcia"),
    ):
        terms.append(_s(pid, name, "Carbon County School District #1 Trustee", FM[2025], FM[2029], 2024, src_24_sd1, note_24_sd1))
    terms.append(_s("WY-FLAMIG-RANDY", "Randy Flamig", "Carbon County School District #1 Trustee",
                    FM[2025], FM[2027], 2024, [SRC_C24, SRC_SW24],
                    "Official 2024 Carbon clerk, School District 1 2-year: Randy Flamig 2,825. Official Sweetwater 2024 general, School District #1 Carbon Trustee Vote-For-1: Randy Flamig 36. Combined official total: 2,861."))
    terms += [
        _s("WY-CLARK-PAUL", "Paul Clark", "Carbon County School District #2 Area 1 Trustee",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, School District 2-Area 1: Paul Clark 1,196, Aubrey Maughan 834."),
        _s("WY-MILLER-GEORGIA", "Georgia Miller", "Carbon County School District #2 Area 2 Trustee",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, School District 2-Area 2: Georgia Miller 2,174."),
        _s("WY-GASPARI-JOE", "Joe Gaspari", "Carbon County School District #2 Area 3 Trustee",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, School District 2-Area 3: Joe Gaspari 2,146."),
        _s("WY-WAMSLEY-NICHOLAS", "Nicholas Wamsley", "Carbon County School District #2 Area 4 Trustee",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, School District 2-Area 4: Nicholas Wamsley 2,015."),
    ]
    # 2026 CCSD #1 VF3 + 2yr unexpired + official Sweetwater shares.
    note_26_sd1 = (
        "Official 2026 Carbon clerk, Carbon County School District 1 Vote-For-3: Tanya S. Evans 1,400, Michael R. Mann 1,354, "
        "write-in totals 645 (official summary: Harlee Mascarenas was elected with write-in votes). "
        "Official Sweetwater 2026 general, Carbon County 4YR: Michael R Mann 14, Tanya Evans 13, write-in totals 0 "
        "(official Sweetwater contest is printed Vote-For-1; official shares are added as printed). "
        "Combined official named totals: Evans 1,413, Mann 1,368, plus official Carbon-certified write-in winner Harlee Mascarenas. "
        "The official Carbon summary states that results for this race must be combined with Sweetwater County."
    )
    src_26_sd1 = [SRC_C26, SRC_SW26]
    for pid, name in (
        ("WY-EVANS-TANYA-S", "Tanya S. Evans"),
        ("WY-MANN-MICHAEL-R", "Michael R. Mann"),
        ("WY-MASCARENAS-HARLEE", "Harlee Mascarenas"),
    ):
        terms.append(_s(pid, name, "Carbon County School District #1 Trustee", FM[2027], FM[2031], 2026, src_26_sd1, note_26_sd1))
    terms.append(_s("WY-CARRICO-JUSTIN", "Justin Carrico", "Carbon County School District #1 Trustee",
                    FM[2027], FM[2029], 2026, [SRC_C26, SRC_SW26],
                    "Official 2026 Carbon clerk, School District 1 2-year unexpired: write-in totals 498 (official summary: Justin Carrico was elected with write-in votes). Official Sweetwater 2026 general, Carbon County 2YR: write-in totals 2 (no named candidate on the official Sweetwater line). Combined official write-in totals 500; official Carbon canvass names Justin Carrico. The official Carbon summary states that results must be combined with Sweetwater County."))
    terms += [
        _s("WY-REDDISH-JALEN", "Jalen Reddish", "Carbon County School District #2 Area 1 Trustee",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, School District 2 Area 1: Jalen Reddish 1,477."),
        _s("WY-CONDICT-KAREN-D", "Karen D. Condict", "Carbon County School District #2 Area 2 Trustee",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, School District 2 Area 2: Karen D Condict 1,605."),
        _s("WY-JOHNSON-MARIA-L", "Maria L. Johnson", "Carbon County School District #2 Area 3 Trustee",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, School District 2 Area 3: Maria L. Johnson 1,550."),
        _s("WY-WESTRING-KASSEY", "Kassey Westring", "Carbon County School District #2 Area 4 Trustee",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, School District 2 Area 4 Vote-For-2: Kassey Westring 1,426, Matt Anderson 1,240."),
        _s("WY-ANDERSON-MATT", "Matt Anderson", "Carbon County School District #2 Area 4 Trustee",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Matt Anderson 1,240."),
    ]
    return terms


def special_terms():
    terms = []
    # 2022 LSR — official Carbon Cobb 325 + write-in Tom Chant certified; official Sweetwater Cobb 1.
    note_22_lsr = (
        "Official 2022 Carbon clerk, LSR Conservation Vote-For-2: John R (Jack) Cobb 325, write-in totals 54. "
        "Official 2022 Carbon certified write-ins: Tom Chant, Little Snake River Conservation District. "
        "Official Sweetwater 2022 general, LSR Conservation Vote-For-2: John R. (Jack) Cobb 1. "
        "Combined official Cobb total: 326, plus official Carbon-certified write-in winner Tom Chant (Thomas Chant). "
        "The official Carbon election-results page states that Sweetwater results must be added for LSR Conservation."
    )
    terms += [
        _d("WY-COBB-JOHN-JACK", "John (Jack) Cobb", "Little Snake River Conservation District Rural Supervisor",
           FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI, SRC_SW22], note_22_lsr),
        _d("WY-CHANT-THOMAS", "Thomas Chant", "Little Snake River Conservation District Rural Supervisor",
           FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI, SRC_SW22], note_22_lsr),
        _d("WY-PALM-QUADE", "Quade Palm", "Medicine Bow Conservation District Rural Supervisor",
           FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, Med Bow Conserv Rural Vote-For-2: Quade Palm 413, Owen Williams 378."),
        _d("WY-WILLIAMS-OWEN", "Owen Williams", "Medicine Bow Conservation District Rural Supervisor",
           FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk: Owen Williams 378."),
        _d("WY-BAILEY-WILLIAM", "William Bailey", "Medicine Bow Conservation District Urban Supervisor",
           FM[2023], FM[2025], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 Carbon clerk, Med Bow Conserv Urban unexpired was write-in only (51). Official 2022 certified write-ins: William Bailey, Medicine Bow Conservation District – Urban."),
        _d("WY-KERBS-SCOTT", "Scott Kerbs", "Saratoga-Encampment-Rawlins Conservation District Rural Supervisor",
           FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, SER Conservation Vote-For-2: Scott Kerbs 2,481, Arla Strasser 1,992."),
        _d("WY-STRASSER-ARLA", "Arla Strasser", "Saratoga-Encampment-Rawlins Conservation District Rural Supervisor",
           FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk: Arla Strasser 1,992."),
    ]
    # 2022 cemeteries, museums, health, fire
    terms += [
        _d("WY-CORSON-JEFF-D", "Jeff D. Corson", "Baggs Cemetery District Trustee", FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 Carbon clerk, Baggs Cemetery was write-in only (178). Official 2022 certified write-ins: Jeff D. Corson, Clint Weber, and George Jason Evans."),
        _d("WY-WEBER-CLINT-A", "Clint A. Weber", "Baggs Cemetery District Trustee", FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 certified write-ins: Clint Weber, Baggs Cemetery District."),
        _d("WY-EVANS-GEORGE-JASON", "George Jason Evans", "Baggs Cemetery District Trustee", FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 certified write-ins: George Jason Evans, Baggs Cemetery District."),
        _d("WY-COBB-CYNTHIA-L", "Cynthia L. Cobb", "Reader Cemetery District Trustee", FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, Reader Cemetery Vote-For-3: Cynthia L. Cobb 79, William Duncan 76, Barbara J. Moss 73."),
        _d("WY-DUNCAN-WILLIAM", "William Duncan", "Reader Cemetery District Trustee", FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk: William Duncan 76."),
        _d("WY-MOSS-BARBARA-J", "Barbara J. Moss", "Reader Cemetery District Trustee", FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk: Barbara J. Moss 73."),
        _d("WY-CAMPBELL-JAMIE", "Jamie Campbell", "Saratoga Cemetery District Trustee", FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, Saratoga Cemetery Vote-For-3: Jamie Campbell 793, James Wiant 644, Wanda Erger 605."),
        _d("WY-WIANT-JAMES", "James Wiant", "Saratoga Cemetery District Trustee", FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk: James Wiant 644."),
        _d("WY-ERGER-WANDA", "Wanda Erger", "Saratoga Cemetery District Trustee", FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk: Wanda Erger 605."),
        _d("WY-DUNCAN-KEITH", "Keith Duncan", "Little Snake River Museum District Trustee", FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, LSR Museum Vote-For-3: Keith Duncan 301, Sherry Weber 277, Rox Hicks 257."),
        _d("WY-WEBER-SHERRY", "Sherry Weber", "Little Snake River Museum District Trustee", FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk: Sherry Weber 277."),
        _d("WY-HICKS-ROX", "Rox Hicks", "Little Snake River Museum District Trustee", FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk: Rox Hicks 257."),
        _d("WY-ERICKSON-DAWNA", "Dawna Erickson", "Saratoga-Ryan Park Museum District Trustee", FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 Carbon clerk, Saratoga-Ryan Park Museum was write-in only (145). Official 2022 certified write-ins: Dawna Erickson, R. Richard Perue, and Sherry Mackay."),
        _d("WY-PERUE-R-RICHARD", "R. Richard Perue", "Saratoga-Ryan Park Museum District Trustee", FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 certified write-ins: R. Richard Perue, Saratoga-Ryan Park Museum District."),
        _d("WY-MACKAY-SHERRY", "Sherry Mackay", "Saratoga-Ryan Park Museum District Trustee", FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 certified write-ins: Sherry Mackay, Saratoga-Ryan Park Museum District."),
        _d("WY-OTOOLE-MEGAN-STOCKLIN", "Megan Stocklin O'Toole", "Little Snake River Rural Health Care District Trustee",
           FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, LSR Health Vote-For-3: Megan Stocklin O'Toole 287, Jacquelyn Harvey 260."),
        _d("WY-HARVEY-JACQUELYN", "Jacquelyn Harvey", "Little Snake River Rural Health Care District Trustee",
           FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk: Jacquelyn Harvey 260."),
        _d("WY-MIKESELL-RYAN", "Ryan Mikesell", "Little Snake River Rural Health Care District Trustee",
           FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 certified write-ins: Ryan Mikesell, Little Snake River Rural Health Care District. Official 2022 clerk write-in totals 74."),
        _d("WY-LALLY-BRIAN-J", "Brian J. Lally", "Little Snake River Rural Health Care District Trustee",
           FM[2023], FM[2025], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, LSR Health unexpired: Brian J Lally 273."),
        _d("WY-EMBREE-KAY", "Kay Embree", "Medicine Bow Rural Health Care District Trustee",
           FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 Carbon clerk, Med Bow Health Vote-For-3: Kay Embree 94, write-in totals 32. Official 2022 certified write-ins also name Kendra Heward and Kenzie Strauch."),
        _d("WY-HEWARD-KENDRA", "Kendra Heward", "Medicine Bow Rural Health Care District Trustee",
           FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 certified write-ins: Kendra Heward, Medicine Bow Rural Health Care District."),
        _d("WY-STRAUCH-KENZIE", "Kenzie Strauch", "Medicine Bow Rural Health Care District Trustee",
           FM[2023], FM[2027], 2022, [SRC_C22, SRC_C22WI],
           "Official 2022 certified write-ins: Kenzie Strauch, Medicine Bow Rural Health Care District."),
        _d("WY-COWDIN-SUE", "Sue Cowdin", "Medicine Bow Rural Health Care District Trustee",
           FM[2023], FM[2025], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, Med Bow Health unexpired: Sue Cowdin 105."),
        _d("WY-NEY-COURTNEY", "Courtney Ney", "Carbon County Fire Protection District Director",
           FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, Carbon County Rural Fire District Vote-For-3: Courtney Ney 609, Homer Beach 559, James R. \"Jim\" Piche 491. Encoded on the official successor/current district title used on the official 2024 and 2026 canvasses (Carbon County Fire Protection District). Official 2022 formation question: For 674, Against 311."),
        _d("WY-BEACH-HOMER", "Homer Beach", "Carbon County Fire Protection District Director",
           FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk: Homer Beach 559."),
        _d("WY-PICHE-JAMES-R", 'James R. "Jim" Piche', "Carbon County Fire Protection District Director",
           FM[2023], FM[2027], 2022, [SRC_C22],
           "Official 2022 Carbon clerk: James R. \"Jim\" Piche 491."),
        _d("WY-WALISER-PAT", "Pat Waliser", "Carbon County Fire Protection District Director",
           FM[2023], FM[2025], 2022, [SRC_C22],
           "Official 2022 Carbon clerk, Fire Protection District 2-year Vote-For-2: Pat Waliser 401, Cory M. Nuhn 346."),
        _d("WY-NUHN-CORY-M", "Cory M. Nuhn", "Carbon County Fire Protection District Director",
           FM[2023], FM[2025], 2022, [SRC_C22],
           "Official 2022 Carbon clerk: Cory M. Nuhn 346."),
    ]
    # 2024 conservation, cemetery, museum, health, fire. LSR rural must add official Sweetwater share (Lally 3).
    note_24_lsr = (
        "Official 2024 Carbon clerk, LSR Conservation Rural: Meghan Lally 383. Official Sweetwater 2024 general lists Meghan Lally 3. "
        "Combined official total: 386. The official Carbon summary states that results for this race must be combined with Sweetwater County."
    )
    terms += [
        _d("WY-LALLY-MEGHAN", "Meghan Lally", "Little Snake River Conservation District Rural Supervisor",
           FM[2025], FM[2029], 2024, [SRC_C24, SRC_SW24], note_24_lsr),
        _d("WY-ARNELL-TRENT", "Trent Arnell", "Little Snake River Conservation District Urban Supervisor",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, LSR Conservation Urban: Trent Arnell 390."),
        _d("WY-LARSON-JENNA", "Jenna Larson", "Little Snake River Conservation District At-Large Supervisor",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, LSR Conservation At-Large: Jenna Larson 425."),
        _d("WY-BROKAW-RALPH-D", "Ralph D. Brokaw", "Medicine Bow Conservation District Rural Supervisor",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, Med Bow Conservation Rural: Ralph D. Brokaw 601."),
        _d("WY-SCHROCK-KAY", "Kay Schrock", "Medicine Bow Conservation District Urban Supervisor",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, Med Bow Conservation Urban: Kay Schrock 592."),
        _d("WY-HEWARD-TIMOTHY", "Timothy Heward", "Medicine Bow Conservation District At-Large Supervisor",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, Med Bow Conservation At-Large: Timothy Heward 618."),
        _d("WY-WILLIAMS-CHRIS", "Chris Williams", "Saratoga-Encampment-Rawlins Conservation District Rural Supervisor",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, SER Conservation Rural: Chris Williams 4,045."),
        _d("WY-FAGAN-SHANNON", "Shannon Fagan", "Saratoga-Encampment-Rawlins Conservation District Urban Supervisor",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, SER Conservation Urban: Shannon Fagan 2,295, Jenita Calton 1,713."),
        _d("WY-ARNOLD-RANDY", "Randy Arnold", "Saratoga-Encampment-Rawlins Conservation District At-Large Supervisor",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, SER Conservation At-Large: Randy Arnold 4,070."),
        _d("WY-WILLE-DALE", "Dale Wille", "Baggs Cemetery District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, Baggs Cemetery Vote-For-3: Dale Wille 280, Virginia Sue Lee 243, Bill Orchard 226."),
        _d("WY-LEE-VIRGINIA-SUE", "Virginia Sue Lee", "Baggs Cemetery District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: Virginia Sue Lee 243."),
        _d("WY-ORCHARD-BILL", "Bill Orchard", "Baggs Cemetery District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: Bill Orchard 226."),
        _d("WY-STOCKS-KODY", "Kody Stocks", "Reader Cemetery District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, Reader Cemetery was write-in only (48). Official summary: Kody Stocks, Nikkole Maxson and Timmy Martinez were elected with write-in votes."),
        _d("WY-MAXSON-NIKKOLE", "Nikkole Maxson", "Reader Cemetery District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: Nikkole Maxson elected with write-in votes, Reader Cemetery."),
        _d("WY-MARTINEZ-TIMMY", "Timmy Martinez", "Reader Cemetery District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: Timmy Martinez elected with write-in votes, Reader Cemetery."),
        _d("WY-COX-SUZIE", "Suzie Cox", "Saratoga Cemetery District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, Saratoga Cemetery Vote-For-3: Suzie Cox 831, Susan Howe 819, Charles McVey 752."),
        _d("WY-HOWE-SUSAN", "Susan Howe", "Saratoga Cemetery District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: Susan Howe 819."),
        _d("WY-MCVEY-CHARLES", "Charles McVey", "Saratoga Cemetery District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: Charles McVey 752."),
        _d("WY-LEONHARDT-SUSAN-E", "Susan E. Leonhardt", "Little Snake River Museum District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, LSR Museum Vote-For-3: Susan E Leonhardt 366, Joe Jussila 364, James N Roberts 276."),
        _d("WY-JUSSILA-JOE", "Joe Jussila", "Little Snake River Museum District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: Joe Jussila 364."),
        _d("WY-ROBERTS-JAMES-N", "James N. Roberts", "Little Snake River Museum District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: James N Roberts 276."),
        _d("WY-PATTERSON-CONNIE", "Connie Patterson", "Saratoga-Ryan Park Museum District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, Saratoga-Ryan Park Museum Vote-For-3: Connie Patterson 971, Carol Ann Beach 803, Roger Snell 777."),
        _d("WY-BEACH-CAROL-ANN", "Carol Ann Beach", "Saratoga-Ryan Park Museum District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: Carol Ann Beach 803."),
        _d("WY-SNELL-ROGER", "Roger Snell", "Saratoga-Ryan Park Museum District Trustee", FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: Roger Snell 777."),
        _d("WY-KAISLER-DARCY", "Darcy Kaisler", "Little Snake River Rural Health Care District Trustee",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, LSR Health Care Vote-For-2: Darcy Kaisler 407, Brian Lally 324."),
        _d("WY-LALLY-BRIAN-J", "Brian J. Lally", "Little Snake River Rural Health Care District Trustee",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: Brian Lally 324."),
        _d("WY-COOK-VERNA", "Verna Cook", "Medicine Bow Rural Health Care District Trustee",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, Med Bow Health Care Vote-For-2: Verna Cook 78, Cynthia Culver 78."),
        _d("WY-CULVER-CYNTHIA", "Cynthia Culver", "Medicine Bow Rural Health Care District Trustee",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: Cynthia Culver 78."),
        _d("WY-WALISER-PAT", "Pat Waliser", "Carbon County Fire Protection District Director",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk, Fire Protection Vote-For-2: Pat Waliser 927, Cory M. Nuhn 920."),
        _d("WY-NUHN-CORY-M", "Cory M. Nuhn", "Carbon County Fire Protection District Director",
           FM[2025], FM[2029], 2024, [SRC_C24],
           "Official 2024 Carbon clerk: Cory M. Nuhn 920."),
    ]
    # Official 2024 hospital-board contests are omitted: the official 2024 special hospital district formation failed (Against 1,759, For 1,670). Those names are not seated here.

    # 2026 conservation, cemetery, museum, health, fire. LSR rural official Sweetwater shares.
    note_26_lsr = (
        "Official 2026 Carbon clerk, Little Snake River Conservation District Rural Vote-For-2: John (Jack) Cobb 251, Thomas Chant 222. "
        "Official Sweetwater 2026 general, LSR Cons. District Rural Vote-For-2: John (Jack) Cobb 2, Thomas Chant 1. "
        "Combined official totals: Cobb 253, Chant 223. The official Carbon summary states that results must be combined with Sweetwater County."
    )
    terms += [
        _d("WY-COBB-JOHN-JACK", "John (Jack) Cobb", "Little Snake River Conservation District Rural Supervisor",
           FM[2027], FM[2031], 2026, [SRC_C26, SRC_SW26], note_26_lsr),
        _d("WY-CHANT-THOMAS", "Thomas Chant", "Little Snake River Conservation District Rural Supervisor",
           FM[2027], FM[2031], 2026, [SRC_C26, SRC_SW26], note_26_lsr),
        _d("WY-PALM-QUADE", "Quade Palm", "Medicine Bow Conservation District Rural Supervisor",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, Medicine Bow Conservation Rural Vote-For-2: Quade Palm 396, Owen Williams 367."),
        _d("WY-WILLIAMS-OWEN", "Owen Williams", "Medicine Bow Conservation District Rural Supervisor",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Owen Williams 367."),
        _d("WY-KERBS-SCOTT", "Scott Kerbs", "Saratoga-Encampment-Rawlins Conservation District Rural Supervisor",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, SER Conservation Rural Vote-For-2: Scott Kerbs 2,264, Arla Strasser 1,968."),
        _d("WY-STRASSER-ARLA", "Arla Strasser", "Saratoga-Encampment-Rawlins Conservation District Rural Supervisor",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Arla Strasser 1,968."),
        _d("WY-CORSON-JEFF-D", "Jeff D. Corson", "Baggs Cemetery District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, Baggs Cemetery Vote-For-3: Jeff D. Corson 201, Clint A. Weber 196, write-in totals 53 (official summary: George Jason Evans was elected with write-in votes)."),
        _d("WY-WEBER-CLINT-A", "Clint A. Weber", "Baggs Cemetery District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Clint A. Weber 196."),
        _d("WY-EVANS-GEORGE-JASON", "George Jason Evans", "Baggs Cemetery District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: George Jason Evans elected with write-in votes, Baggs Cemetery."),
        _d("WY-DUNCAN-WILLIAM", "William Duncan", "Reader Cemetery District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, Reader Cemetery Vote-For-3: William Duncan 83, Barbara J Moss 81, Cynthia L. Cobb 80."),
        _d("WY-MOSS-BARBARA-J", "Barbara J. Moss", "Reader Cemetery District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Barbara J Moss 81."),
        _d("WY-COBB-CYNTHIA-L", "Cynthia L. Cobb", "Reader Cemetery District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Cynthia L. Cobb 80."),
        _d("WY-MCBRIDE-SHAUN", "Shaun McBride", "Saratoga Cemetery District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, Saratoga Cemetery was write-in only (474). Official summary: Shaun McBride, Jamie Campbell and Edmund Howe were elected with write-in votes."),
        _d("WY-CAMPBELL-JAMIE", "Jamie Campbell", "Saratoga Cemetery District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Jamie Campbell elected with write-in votes, Saratoga Cemetery."),
        _d("WY-HOWE-EDMUND", "Edmund Howe", "Saratoga Cemetery District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Edmund Howe elected with write-in votes, Saratoga Cemetery."),
        _d("WY-WILLE-ANN", "Ann Wille", "Little Snake River Museum District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, LSR Museum Vote-For-3: Ann Wille 270, Keith Duncan 267, write-in totals 33 (official summary: Gwendalynn Herold was elected with write-in votes)."),
        _d("WY-DUNCAN-KEITH", "Keith Duncan", "Little Snake River Museum District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Keith Duncan 267."),
        _d("WY-HEROLD-GWENDALYNN", "Gwendalynn Herold", "Little Snake River Museum District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Gwendalynn Herold elected with write-in votes, LSR Museum."),
        _d("WY-RYAN-GREGORY", "Gregory Ryan", "Saratoga-Ryan Park Museum District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, Saratoga-Ryan Park Museum was write-in only (267). Official summary: Gregory Ryan, Logan Robinson and Nanette Valdez-Schwartz were elected with write-in votes."),
        _d("WY-ROBINSON-LOGAN", "Logan Robinson", "Saratoga-Ryan Park Museum District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Logan Robinson elected with write-in votes, Saratoga-Ryan Park Museum."),
        _d("WY-VALDEZ-SCHWARTZ-NANETTE", "Nanette Valdez-Schwartz", "Saratoga-Ryan Park Museum District Trustee", FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Nanette Valdez-Schwartz elected with write-in votes, Saratoga-Ryan Park Museum."),
        _d("WY-OTOOLE-MEGAN-STOCKLIN", "Megan Stocklin O'Toole", "Little Snake River Rural Health Care District Trustee",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, LSR Rural Health Vote-For-3: Megan Stocklin O'Toole 263, Jacquelyn Harvey 232, write-in totals 137 (official summary: Joshua Ryan Taylor was elected with write-in votes)."),
        _d("WY-HARVEY-JACQUELYN", "Jacquelyn Harvey", "Little Snake River Rural Health Care District Trustee",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Jacquelyn Harvey 232."),
        _d("WY-TAYLOR-JOSHUA-RYAN", "Joshua Ryan Taylor", "Little Snake River Rural Health Care District Trustee",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Joshua Ryan Taylor elected with write-in votes, LSR Rural Health."),
        _d("WY-PEREZ-MARIE", "Marie Perez", "Medicine Bow Rural Health Care District Trustee",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, Medicine Bow Rural Health Vote-For-3: Marie Perez 68, Jennifer Reeves 66, Lucinda L. Schofield 60."),
        _d("WY-REEVES-JENNIFER", "Jennifer Reeves", "Medicine Bow Rural Health Care District Trustee",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Jennifer Reeves 66."),
        _d("WY-SCHOFIELD-LUCINDA-L", "Lucinda L. Schofield", "Medicine Bow Rural Health Care District Trustee",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Lucinda L. Schofield 60 (4-year). Official 2026 2-year unexpired write-in also names Lucinda L. Schofield; that 2-year seat is encoded separately."),
        _d("WY-SCHOFIELD-LUCINDA-L", "Lucinda L. Schofield", "Medicine Bow Rural Health Care District Trustee",
           FM[2027], FM[2029], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, Medicine Bow Rural Health 2-year unexpired: write-in totals 17 (official summary: Lucinda L. Schofield was elected with write-in votes)."),
        _d("WY-DALEY-JAIMIE", "Jaimie Daley", "Carbon County Fire Protection District Director",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk, Fire Protection Vote-For-3: Jaimie Daley 474, Homer Beach 442, James R. \"Jim\" Piche 407."),
        _d("WY-BEACH-HOMER", "Homer Beach", "Carbon County Fire Protection District Director",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: Homer Beach 442."),
        _d("WY-PICHE-JAMES-R", 'James R. "Jim" Piche', "Carbon County Fire Protection District Director",
           FM[2027], FM[2031], 2026, [SRC_C26],
           "Official 2026 Carbon clerk: James R. \"Jim\" Piche 407."),
    ]
    return terms


def expected_offices():
    mayors_councils = [
        ("Baggs Mayor", 1), ("Baggs Council", 4),
        ("Dixon Mayor", 1), ("Dixon Council", 4),
        ("Elk Mountain Mayor", 1), ("Elk Mountain Council", 4),
        ("Encampment Mayor", 1), ("Encampment Council", 4),
        ("Hanna Mayor", 1), ("Hanna Council", 4),
        ("Medicine Bow Mayor", 1), ("Medicine Bow Council", 4),
        ("Rawlins Mayor", 1),
        ("Rawlins City Council Ward 1", 2),
        ("Rawlins City Council Ward 2", 2),
        ("Rawlins City Council Ward 3", 2),
        ("Rawlins City Council At-Large", 1),
        ("Riverside Mayor", 1), ("Riverside Council", 4),
        ("Saratoga Mayor", 1), ("Saratoga Council", 4),
        ("Sinclair Mayor", 1), ("Sinclair Council", 4),
    ]
    return {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
                      ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
        "state-senate": [("Senate District 11 (S11)", 1)],
        "state-house": [("House District 15 (H15)", 1), ("House District 47 (H47)", 1)],
        "county": [("County Commissioner", 5), ("County Clerk", 1), ("County Treasurer", 1),
                   ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
                   ("Clerk of District Court", 1), ("County Coroner", 1)],
        "municipal": mayors_councils,
        "schools": [
            ("Carbon County School District #1 Trustee", 7),
            ("Carbon County School District #2 Area 1 Trustee", 1),
            ("Carbon County School District #2 Area 2 Trustee", 1),
            ("Carbon County School District #2 Area 3 Trustee", 1),
            ("Carbon County School District #2 Area 4 Trustee", 2),
        ],
        "special-districts": [
            ("Little Snake River Conservation District Rural Supervisor", 2),
            ("Little Snake River Conservation District Urban Supervisor", 1),
            ("Little Snake River Conservation District At-Large Supervisor", 1),
            ("Medicine Bow Conservation District Rural Supervisor", 2),
            ("Medicine Bow Conservation District Urban Supervisor", 1),
            ("Medicine Bow Conservation District At-Large Supervisor", 1),
            ("Saratoga-Encampment-Rawlins Conservation District Rural Supervisor", 2),
            ("Saratoga-Encampment-Rawlins Conservation District Urban Supervisor", 1),
            ("Saratoga-Encampment-Rawlins Conservation District At-Large Supervisor", 1),
            ("Baggs Cemetery District Trustee", 3),
            ("Reader Cemetery District Trustee", 3),
            ("Saratoga Cemetery District Trustee", 3),
            ("Little Snake River Museum District Trustee", 3),
            ("Saratoga-Ryan Park Museum District Trustee", 3),
            ("Little Snake River Rural Health Care District Trustee", 3),
            ("Medicine Bow Rural Health Care District Trustee", 3),
            ("Carbon County Fire Protection District Director", 5),
        ],
        "judicial": [
            ("District Judge, 2nd Judicial District", 2),
            ("Circuit Judge, 2nd Judicial District", 2),
        ],
    }


def build_carbon():
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
        "Wyoming Judicial Branch dates and official retention results (shared with other counties). Local rows are "
        "2nd Judicial District judges (Carbon and Albany). Full names are taken from official Wyoming Judicial Branch "
        "2nd JD pages and official Carbon clerk retention lines, and those sources are cited. Judges of other districts "
        "are not copied here."
    )
    special_note = (
        "County, municipal, school, and special-district names are keyed from official Carbon clerk general summaries "
        "(2018, 2020, 2022, 2024, and 2026) and official 2022 certified write-ins. The official 2020 DocumentCenter slug "
        "still says unofficial; the PDF header is OFFICIAL RESULTS. Official 2014 and 2016 Carbon clerk canvasses are "
        "archived but were not fully keyed here, so January 2015–2018 local rows are largely Not yet collected rather than invented. "
        "Multi-county legislative seats use official SOS district-wide Total rows, with the official Carbon share noted. "
        "Official Carbon election-results pages state that Sweetwater results must be added for School District #1 and "
        "LSR Conservation; official Sweetwater clerk general totals are included and cited. The Rawlins mayor is chosen "
        "by the city council (official Rawlins Municipal Code 2.04.030); the current mayor is from the official City of "
        "Rawlins council page, and the January 2027 mayor is not invented. Official mid-term vacancies are not invented. "
        "Official 2024 hospital-board contests are omitted because the official 2024 special hospital district formation failed."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. The current (November 2026) precinct roster "
        "is in data/county_officials/carbon.json, from the official 2026 Carbon primary (named winners only; 8 precincts / 13 holders)."
    )
    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Carbon", county_number=CN, slug=SLUG, terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Carbon", slug=SLUG)
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
    """Current holders plus January 2027 elects, official terms only."""
    cur = [t for t in terms if t["office"] == office and t["term_start"] <= as_of < t["term_end"]]
    elects = [t for t in terms if t["office"] == office and t["term_start"] == elect_start]
    # Prefer a single continuing row when the same person is both current and the 2026 winner.
    seen = set()
    out = []
    # Elects first for people who continue: use the later term_end on one row, then current-only, then new elects.
    current_ids = {t["person_id"] for t in cur}
    elect_ids = {t["person_id"] for t in elects}
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


def update_carbon_json(people, terms):
    path = ROOT / "data" / "county_officials" / "carbon.json"
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
        # If current and January 2027 elect have different official notes, join the latest two.
        seen = []
        for t in pool:
            n = t["notes"]
            if n and n not in seen:
                seen.append(n)
            if len(seen) == 2:
                break
        return " ".join(seen)

    senate = [_office("Senate District 11 (S11)", _holders_for_office(terms, people, "Senate District 11 (S11)"),
                      note=office_note("Senate District 11 (S11)"))]
    house = [
        _office("House District 15 (H15)", _holders_for_office(terms, people, "House District 15 (H15)"),
                note=office_note("House District 15 (H15)")),
        _office("House District 47 (H47)", _holders_for_office(terms, people, "House District 47 (H47)"),
                note=office_note("House District 47 (H47)")),
    ]
    county_offices = [
        "County Commissioner", "County Clerk", "County Treasurer", "County Assessor",
        "County Sheriff", "County Attorney", "Clerk of District Court", "County Coroner",
    ]
    county = [_office(o, _holders_for_office(terms, people, o), note=office_note(o)) for o in county_offices]

    mun_offices = [
        "Baggs Mayor", "Baggs Council", "Dixon Mayor", "Dixon Council",
        "Elk Mountain Mayor", "Elk Mountain Council", "Encampment Mayor", "Encampment Council",
        "Hanna Mayor", "Hanna Council", "Medicine Bow Mayor", "Medicine Bow Council",
        "Rawlins Mayor", "Rawlins City Council Ward 1", "Rawlins City Council Ward 2",
        "Rawlins City Council Ward 3", "Rawlins City Council At-Large",
        "Riverside Mayor", "Riverside Council", "Saratoga Mayor", "Saratoga Council",
        "Sinclair Mayor", "Sinclair Council",
    ]
    municipal = [_office(o, _holders_for_office(terms, people, o), note=office_note(o)) for o in mun_offices]

    school_offices = [
        "Carbon County School District #1 Trustee",
        "Carbon County School District #2 Area 1 Trustee",
        "Carbon County School District #2 Area 2 Trustee",
        "Carbon County School District #2 Area 3 Trustee",
        "Carbon County School District #2 Area 4 Trustee",
    ]
    schools = [_office(o, _holders_for_office(terms, people, o), layout="heading-then-names", note=office_note(o))
               for o in school_offices]

    special_offices = [
        "Little Snake River Conservation District Rural Supervisor",
        "Little Snake River Conservation District Urban Supervisor",
        "Little Snake River Conservation District At-Large Supervisor",
        "Medicine Bow Conservation District Rural Supervisor",
        "Medicine Bow Conservation District Urban Supervisor",
        "Medicine Bow Conservation District At-Large Supervisor",
        "Saratoga-Encampment-Rawlins Conservation District Rural Supervisor",
        "Saratoga-Encampment-Rawlins Conservation District Urban Supervisor",
        "Saratoga-Encampment-Rawlins Conservation District At-Large Supervisor",
        "Baggs Cemetery District Trustee",
        "Reader Cemetery District Trustee",
        "Saratoga Cemetery District Trustee",
        "Little Snake River Museum District Trustee",
        "Saratoga-Ryan Park Museum District Trustee",
        "Little Snake River Rural Health Care District Trustee",
        "Medicine Bow Rural Health Care District Trustee",
        "Carbon County Fire Protection District Director",
    ]
    specials = [_office(o, _holders_for_office(terms, people, o), layout="heading-then-names", note=office_note(o))
                for o in special_offices]

    judicial = [
        _office("District Judge, 2nd Judicial District",
                _holders_for_office(terms, people, "District Judge, 2nd Judicial District"),
                note="Official 2nd Judicial District (Carbon and Albany). Full names from the official Wyoming Judicial Branch 2nd JD page. Official 2024 Carbon clerk: DISTRICT COURT - SNYDER YES 4,506; DISTRICT COURT - WESTBY YES 4,424."),
        _office("Circuit Judge, 2nd Judicial District",
                _holders_for_office(terms, people, "Circuit Judge, 2nd Judicial District"),
                note="Official 2nd Judicial District circuit judges. Full names from the official Wyoming Judicial Branch 2nd JD page. Official 2024 Carbon clerk: CIRCUIT COURT - STIPE YES 4,427. Official 2026 Carbon clerk: CIRCUIT JUDGE - SANFORD YES 3,010."),
    ]

    groups = [
        {"id": "state-senate", "title": "State Senate", "layout": "office-and-name", "sort_key": "C", "offices": senate},
        {"id": "state-house", "title": "State House", "layout": "office-and-name", "sort_key": "D", "offices": house},
        {"id": "county", "title": "County Offices", "layout": "office-and-name", "sort_key": "E", "offices": county},
        {"id": "municipal", "title": "Municipal offices", "layout": "office-and-name", "sort_key": "F", "offices": municipal},
        {"id": "schools", "title": "School boards", "layout": "heading-then-names", "sort_key": "G", "offices": schools},
        {"id": "special-districts", "title": "Special districts", "layout": "heading-then-names", "sort_key": "H", "offices": specials},
        {"id": "judicial", "title": "Judicial retention", "layout": "office-and-name", "sort_key": "J3", "offices": judicial},
    ]
    if precincts:
        precincts["sort_key"] = "P"
        groups.append(precincts)
    data["groups"] = groups
    data["sources"] = [
        {"label": "Official Carbon County Election Results page", "url": URL_CLERK},
        {"label": "Official Carbon County 2026 general election summary (DocumentCenter 8663)", "url": URL_C26},
        {"label": "Official Carbon County 2024 general election summary (DocumentCenter 8170)", "url": URL_C24},
        {"label": "Official Carbon County 2022 general election summary (DocumentCenter 6386)", "url": URL_C22},
        {"label": "Official Carbon County 2022 general certified write-ins (DocumentCenter 6388)", "url": URL_C22WI},
        {"label": "Official Carbon County 2026 County Directory (DocumentCenter 8405)", "url": URL_DIR},
        {"label": "Official Carbon County Commissioners page", "url": URL_COMM},
        {"label": "Official City of Rawlins City Council page", "url": URL_RAWLINS},
        {"label": "Official Wyoming Judicial Branch, District Court, 2nd Judicial District", "url": URL_COURT_2JD},
        {"label": "Official Sweetwater County election returns (SD#1 and LSR Conservation shares)", "url": URL_SW_INDEX},
        {"label": "Official Wyoming SOS statewide Senate and House candidate summaries (S11, H15, H47 district-wide totals)", "url": ""},
    ]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"updated {path}")
