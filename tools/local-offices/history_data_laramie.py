"""Laramie County dated terms and live-roster update. Imported by build_county_history.py."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import history_lib as H

from legislative_office_notes import apply_to_groups
RETRIEVED = "2026-11-24"
FM = H.FM
ROOT = H.ROOT
ARCHIVE = "https://www.laramiecountywy.gov/County-Government/Elected-Officials/County-Clerk/Elections/Election-Results"

# Official Laramie County Clerk general results (see /workspace/wyoleg/local-results/laramie/SOURCES.md).
PG = {
    2010: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/laramie-county-official-results-summary-report.pdf",
           "Laramie County official 2010 general results (combined all-races summary)"),
    2012: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/2012-general-official-county-city-summary-report-1.pdf",
           "Laramie County official 2012 general city/county results"),
    2014: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/2014official-summary-report-county-and-city-races.pdf",
           "Laramie County official 2014 general city/county results"),
    2016: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/official-summary-county-city-races.pdf",
           "Laramie County official 2016 general city/county results"),
    2018: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/official-complete-general-election-results-county-and-city-races2018.pdf",
           "Laramie County official 2018 general city/county results"),
    2020: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/general-election-results-city-county-summary-2020.pdf",
           "Laramie County official 2020 general city/county results"),
    2022: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/general-election-results-city-county-summary-2022.pdf",
           "Laramie County official 2022 general city/county results"),
    2024: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/2024-general/official/city-and-county-election-summary.pdf",
           "Laramie County official 2024 general city/county results"),
    2026: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/2026-general/county-city-election-summary.pdf",
           "Laramie County official 2026 general city/county results"),
}
FS = {
    2012: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/2012-general-official-fed-state-summary-report.pdf",
           "Laramie County official 2012 general federal/state results"),
    2014: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/2014official-summary-report-federal-and-state-races.pdf",
           "Laramie County official 2014 general federal/state results"),
    2016: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/official-summary-report-federal-and-state-races.pdf",
           "Laramie County official 2016 general federal/state results"),
    2018: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/official-complete-general-election-results-federal-and-state-races2018.pdf",
           "Laramie County official 2018 general federal/state results"),
    2020: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/general-election-results-federal-and-state-summary-2020.pdf",
           "Laramie County official 2020 general federal/state results"),
    2022: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/general-election-results-federal-state-summary-2022.pdf",
           "Laramie County official 2022 general federal/state results"),
    2024: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/2024-general/official/federal-and-state-election-summary.pdf",
           "Laramie County official 2024 general federal/state results"),
    2026: ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/2026-general/fed-state-election-summary.pdf",
           "Laramie County official 2026 general federal/state results"),
}
SD1_2026 = ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/2026-general/lcsd1.pdf",
            "Laramie County official 2026 general LCSD #1 results")
SD2_2026 = ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/2026-general/lcsd2.pdf",
            "Laramie County official 2026 general LCSD #2 results")
SD1_2014R = ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/official-results-recount-election-summary-report.pdf",
             "Laramie County official 2014 general LCSD #1 recount summary")
SD1_2018R = ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/official-summary-report-recount-sd1.pdf",
             "Laramie County official 2018 general LCSD #1 recount summary")
PP_2026 = ("https://www.laramiecountywy.gov/files/assets/public/v/1/clerk/documents/election-results/2026-primary/county-and-city-election-summary.pdf",
           "Laramie County official 2026 primary city/county results")


def pg(year: int) -> dict:
    url, label = PG[year]
    return {"label": label, "url": url}


def fs(year: int) -> dict:
    url, label = FS[year]
    return {"label": label, "url": url}


def T(**kw):
    if not kw.get("sources"):
        if kw.get("election_year") in PG and kw.get("office_group") in {"state-senate", "state-house", "judicial"}:
            # legislature and statewide-on-county-ballot judicial retentions are on the official federal/state summary
            # when a federal/state PDF exists; 1st JD circuit retentions also appear on the city/county summary in some years.
            yr = kw["election_year"]
            if yr in FS and kw.get("office_group") in {"state-senate", "state-house"}:
                kw["sources"] = [fs(yr)]
            elif yr in FS and kw.get("office_group") == "judicial":
                kw["sources"] = [fs(yr)]
            else:
                kw["sources"] = [pg(yr)] if yr in PG else []
        elif kw.get("election_year") in PG:
            kw["sources"] = [pg(kw["election_year"])]
    kw.setdefault("confidence", "high")
    return H.term(**kw)

def register_people(P):
    reused = [
        # Legislature / county names that already exist in the name index or prior worktrees
        ("WY-NETHERCOTT-TARA", "Tara Nethercott", "Tara", "Nethercott", ""),
        ("WY-HUTCHINGS-LYNN", "Lynn Hutchings", "Lynn", "Hutchings", ""),
        ("WY-SCHOENFELD-LAUREN", "Lauren Schoenfeld", "Lauren", "Schoenfeld", ""),
        ("WY-LOVE-TAFT", "Taft Love", "Taft", "Love", "Taft C. Love"),
        ("WY-PAPPAS-STEPHAN", "Stephan Pappas", "Stephan", "Pappas", "Stephan A. Pappas"),
        ("WY-RINNE-MARK", "Mark Rinne", "Mark", "Rinne", "Mark D. Rinne"),
        ("WY-ELLIS-AFFIE", "Affie Ellis", "Affie", "Ellis", ""),
        ("WY-OLSEN-JARED", "Jared Olsen", "Jared", "Olsen", ""),
        ("WY-BRENNAN-EVIE", "Evie Brennan", "Evie", "Brennan", ""),
        ("WY-HAROLDSON-JEREMY", "Jeremy Haroldson", "Jeremy", "Haroldson", ""),
        ("WY-NICHOLAS-BOB", "Bob Nicholas", "Bob", "Nicholas", ""),
        ("WY-JOHNSON-STEVE", "Steve Johnson", "Steve", "Johnson", ""),
        ("WY-REINER-LUKE", "Luke Reiner", "Luke", "Reiner", ""),
        ("WY-BROWN-LANDON", "Landon J. Brown", "Landon", "Brown", "Landon Brown; Landon J Brown"),
        ("WY-WIGGAM-BOYD", "Boyd O. Wiggam", "Boyd", "Wiggam", "Boyd O Wiggam"),
        ("WY-EKLUND-JOHN", "John Eklund", "John", "Eklund", "John Eklund Jr"),
        ("WY-FORNSTROM-JUSTIN", "Justin Fornstrom", "Justin", "Fornstrom", ""),
        ("WY-WASSERBURGER-JACOB", "Jacob Wasserburger", "Jacob", "Wasserburger", ""),
        ("WY-TENNANT-BRITNEY", "Britney Tennant", "Britney", "Tennant", ""),
        ("WY-STYVAR-CLARENCE", "Clarence Styvar", "Clarence", "Styvar", "Clarence L. Styvar"),
        ("WY-BROWN-GARY", "Gary Brown", "Gary", "Brown", ""),
        ("WY-EDWARDS-ERIN", "Erin Edwards", "Erin", "Edwards", ""),
        ("WY-GERINGER-ROB", "Rob Geringer", "Rob", "Geringer", ""),
        ("WY-LUCAS-ANN", "Ann Lucas", "Ann", "Lucas", ""),
        ("WY-CROWDER-JESSICA", "Jessica Crowder", "Jessica", "Crowder", ""),
        ("WY-FILER-LEE", "Lee Filer", "Lee", "Filer", "Lee R. Filer"),
        ("WY-SINGH-DANIEL", "Daniel J. Singh", "Daniel", "Singh", "Daniel Singh"),
        ("WY-SERVER-ANDREW", "Andrew Server", "Andrew", "Server", ""),
        ("WY-WILSON-SUE", "Sue Wilson", "Sue", "Wilson", ""),
        ("WY-ZWONITZER-DAN", "Dan Zwonitzer", "Dan", "Zwonitzer", ""),
        ("WY-ZWONITZER-DAVE", "Dave Zwonitzer", "Dave", "Zwonitzer", "David Zwonitzer; David L. Zwonitzer; David L Zwonitzer"),
        ("WY-BURLINGAME-SARA", "Sara Burlingame", "Sara", "Burlingame", ""),
        ("WY-BYRD-JAMES", "James W. Byrd", "James", "Byrd", "James Byrd"),
        ("WY-THRONE-MARY", "Mary A. Throne", "Mary", "Throne", "Mary Throne"),
        ("WY-HENDERSON-BILL", "Bill Henderson", "Bill", "Henderson", ""),
        ("WY-BLACKBURN-JIM", "Jim Blackburn", "Jim", "Blackburn", ""),
        ("WY-BOUCHARD-ANTHONY", "Anthony Bouchard", "Anthony", "Bouchard", ""),
        ("WY-SMITH-DARIN", "Darin Smith", "Darin", "Smith", ""),
        ("WY-EMERICH-FRED", "Fred Emerich", "Fred", "Emerich", ""),
        ("WY-HORNOK-BEN", "Ben Hornok", "Ben", "Hornok", ""),
        ("WY-TRUJILLO-TAMARA", "Tamara N. Trujillo", "Tamara", "Trujillo", "Tamara Trujillo"),
        ("WY-ROMERO-MARTINEZ-JOHN", "John B. Romero-Martinez", "John", "Romero-Martinez", ""),
        ("WY-ESQUIBEL-KEN", "Ken A. Esquibel", "Ken", "Esquibel", "Ken Esquibel"),
        ("WY-ESQUIBEL-FLOYD", "Floyd A. Esquibel", "Floyd", "Esquibel", ""),
        ("WY-ROSS-TONY", "Tony Ross", "Tony", "Ross", ""),
        ("WY-MANLOVE-LEIGH-ANNE", "Leigh Anne Manlove", "Leigh Anne", "Manlove", ""),
        ("WY-HACKL-SYLVIA", "Sylvia Miller Hackl", "Sylvia", "Hackl", "Sylvia Lee Hackl; Sylvia Lee Hackl"),
        ("WY-HILL-BRIDGET", "Bridget Hill", "Bridget", "Hill", ""),  # SC only; do not reuse for others
    ]
    def add(row):
        pid, display, first, last, aka = row
        P(pid, display, first, last, aliases=aka)
    for row in reused:
        add(row)


def _register_local_people(P):
    local = [
        ("WY-THOMPSON-TROY", "Troy Thompson", "Troy", "Thompson", ""),
        ("WY-HUMPHREY-DIANE", "Diane Humphrey", "Diane", "Humphrey", ""),
        ("WY-HASENAUER-M-LEE", "M. Lee Hasenauer", "M. Lee", "Hasenauer", "M Lee Hasenauer"),
        ("WY-HOLMES-KN-BUCK", "K.N. Buck Holmes", "K.N.", "Holmes", "K.N. \"Buck\" Holmes; K.N. BUCK HOLMES; KN Buck Holmes"),
        ("WY-HEATH-LINDA", "Linda Heath", "Linda", "Heath", "Linda M Heath; Linda M. Heath"),
        ("WY-KAILEY-RON-JR", "Ron Kailey Jr", "Ron", "Kailey", "Ron Kailey Jr.; RON KAILEY JR"),
        ("WY-ASH-AMBER", "Amber Ash", "Amber", "Ash", ""),
        ("WY-MALM-GUNNAR", "Gunnar Malm", "Gunnar", "Malm", ""),
        ("WY-LOVETT-BRIAN", "Brian Lovett", "Brian", "Lovett", ""),
        ("WY-HOLLINGSHEAD-DON", "Don Hollingshead", "Don", "Hollingshead", ""),
        ("WY-ZWONITZER-TY", "Ty Zwonitzer", "Ty", "Zwonitzer", ""),
        ("WY-KETCHAM-JESS-E", "Jess E. Ketcham", "Jess", "Ketcham", "Jess E Ketcham"),
        ("WY-KETCHAM-JEFF", "Jeff Ketcham", "Jeff", "Ketcham", ""),
        ("WY-LATHROP-DEBBYE", "Debbye Lathrop", "Debbye", "Lathrop", ""),
        ("WY-LEE-DEBRA", "Debra Lee", "Debra", "Lee", ""),
        ("WY-TINNEY-MISTY", "Misty Tinney", "Misty", "Tinney", ""),
        ("WY-EISELE-TRUDY", "Trudy L. Eisele", "Trudy", "Eisele", "Trudy Eisele"),
        ("WY-DEISCH-TAMMY", "Tammy Deisch", "Tammy", "Deisch", ""),
        ("WY-WOOD-TRISTA", "Trista Wood", "Trista", "Wood", ""),
        ("WY-ARNOLD-BRENDA", "Brenda Arnold", "Brenda", "Arnold", ""),
        ("WY-GUILLE-KENNETH", "Kenneth Guille", "Kenneth", "Guille", ""),
        ("WY-ERNST-TODD-A", "Todd A. Ernst", "Todd", "Ernst", "Todd A Ernst"),
        ("WY-GLICK-DANNY", "Danny Glick", "Danny", "Glick", ""),
        ("WY-KOZAK-BRIAN", "Brian Kozak", "Brian", "Kozak", ""),
        ("WY-SANDBURG-JEREMIAH", "Jeremiah Sandburg", "Jeremiah", "Sandburg", ""),
        ("WY-HOMAR-SCOTT-A", "Scott A. Homar", "Scott", "Homar", ""),
        ("WY-LANDERS-SANDY", "Sandy Landers", "Sandy", "Landers", ""),
        ("WY-SANCHEZ-DIANE", "Diane Sanchez", "Diane", "Sanchez", "Diane K. Sanchez"),
        ("WY-LUNA-MARTY", "Marty Luna", "Marty", "Luna", ""),
        ("WY-SARGENT-RONALD-J", "Ronald J. Sargent", "Ronald", "Sargent", ""),
        ("WY-REID-REBECCA", "Rebecca Reid", "Rebecca", "Reid", ""),
        ("WY-NUTTING-LESLIE", "Leslie J. Nutting", "Leslie", "Nutting", ""),
        ("WY-JOHNSON-WAYNE", "Wayne Johnson", "Wayne", "Johnson", ""),
        ("WY-PEDERSEN-BRYAN", "Bryan Pedersen", "Bryan", "Pedersen", ""),
        ("WY-EDMONDS-AMY", "Amy Edmonds", "Amy", "Edmonds", ""),
        ("WY-EDMONDS-HARLAN", "Harlan Edmonds", "Harlan", "Edmonds", ""),
        ("WY-ILLOWAY-PETE", "Pete Illoway", "Pete", "Illoway", ""),
        ("WY-LONE-LARS", "Lars Lone", "Lars", "Lone", ""),
        ("WY-BLACKBURN-THEODORE", "Theodore Blackburn", "Theodore", "Blackburn", ""),
        ("WY-COLLINS-PATRICK", "Patrick Collins", "Patrick", "Collins", ""),
        ("WY-KAYSEN-RICHARD", "Richard L. Kaysen", "Richard", "Kaysen", ""),
        ("WY-ORR-MARIAN", "Marian Orr", "Marian", "Orr", ""),
        ("WY-LAYBOURN-PETE", "Pete Laybourn", "Pete", "Laybourn", ""),
        ("WY-WHITE-JEFF", "Jeff White", "Jeff", "White", ""),
        ("WY-ROYBAL-SCOTT", "Scott D. Roybal", "Scott", "Roybal", ""),
        ("WY-VALDEZ-JIMMY", "Jimmy R. Valdez", "Jimmy", "Valdez", ""),
        ("WY-COOK-BRYAN", "Bryan M. Cook", "Bryan", "Cook", ""),
        ("WY-SEGRAVE-TOM", "Tom Segrave", "Tom", "Segrave", ""),
        ("WY-SHANOR-DICKY", "Dicky Shanor", "Dicky", "Shanor", ""),
        ("WY-EMMONS-KATHY", "Kathy Emmons", "Kathy", "Emmons", ""),
        ("WY-ROSE-JANELLE", "Janelle Rose", "Janelle", "Rose", ""),
        ("WY-ALDRICH-MICHELLE", "Michelle Aldrich", "Michelle", "Aldrich", "Michelle D. Aldrich"),
        ("WY-MOODY-MARK-A", "Mark A. Moody", "Mark", "Moody", ""),
        ("WY-JOHNSON-RICHARD", "Richard Johnson", "Richard", "Johnson", ""),
        ("WY-BROWN-JIM", "Jim Brown", "Jim", "Brown", ""),
        ("WY-LUNA-MIKE", "Mike Luna", "Mike", "Luna", ""),
        ("WY-KALLAS-MAREN", "Maren Kallas", "Maren", "Kallas", ""),
        ("WY-ALLEN-SEAN", "Sean D. Allen", "Sean", "Allen", "Sean A. Allen"),
        ("WY-FORNSTROM-JUSTIN", "Justin Fornstrom", "Justin", "Fornstrom", ""),
        ("WY-MICHAUD-DENNIS", "Dennis Michaud", "Dennis", "Michaud", ""),
        ("WY-LEITZA-ALLIE", "Allie Leitza", "Allie", "Leitza", ""),
        ("WY-KESTNER-JANNA", "Janna Kestner", "Janna", "Kestner", ""),
        ("WY-CURRIE-AMY", "Amy Currie", "Amy", "Currie", ""),
        ("WY-CROUSE-DAVID", "David Crouse", "David", "Crouse", ""),
        ("WY-SOTO-WENDY", "Wendy J. Soto", "Wendy", "Soto", "Wendy Soto"),
        ("WY-ERICKSON-DON", "Don Erickson", "Don", "Erickson", ""),
        ("WY-SALAZAR-BOB", "Bob Salazar", "Bob", "Salazar", ""),
        ("WY-KELLY-JOE", "Joe Kelly", "Joe", "Kelly", ""),
        ("WY-LYTTLE-BRENDA", "Brenda Lyttle", "Brenda", "Lyttle", ""),
        ("WY-MERRELL-CAROL", "Carol Merrell", "Carol", "Merrell", "Carol A. Merrell"),
        ("WY-THOMPSON-JANINE", "Janine Thompson", "Janine", "Thompson", ""),
        ("WY-BARKER-BRADLEY", "Bradley S. Barker", "Bradley", "Barker", ""),
        ("WY-DUBOIS-WILLIAM", "William DuBois", "William", "DuBois", ""),
        ("WY-DAVIS-HARMON", "Harmon Davis II", "Harmon", "Davis", "Harmon (Bud) Davis II"),
        ("WY-AVERY-EDWIN", "Edwin G Avery", "Edwin", "Avery", "Edwin G. Avery"),
        ("WY-HINKLE-RENE", "Rene R. Hinkle", "Rene", "Hinkle", ""),
        ("WY-BURDEN-MARILYN", "Marilyn Burden", "Marilyn", "Burden", ""),
        ("WY-HUMPHREY-BROOKE", "Brooke Humphrey", "Brooke", "Humphrey", ""),
        ("WY-BAILEY-HENRY-HANK", "Henry \"Hank\" Bailey", "Henry", "Bailey", "Henry (Hank) Bailey; HENRY \"HANK\" BAILEY"),
        ("WY-COOK-BARBARA", "Barbara Cook", "Barbara", "Cook", ""),
        ("WY-ASHBY-BRITTANY", "Brittany Ashby", "Brittany", "Ashby", ""),
        ("WY-SMITH-ALICIA", "Alicia Smith", "Alicia", "Smith", ""),
        ("WY-EDGERTON-SUSAN", "Susan Edgerton", "Susan", "Edgerton", ""),
        ("WY-KLAASSEN-CHRISTY", "Christy Klaassen", "Christy", "Klaassen", ""),
        ("WY-BOLIN-TIM", "Tim Bolin", "Tim", "Bolin", ""),
        ("WY-BREEN-NATE", "Nate Breen", "Nate", "Breen", ""),
        ("WY-STOREY-HUYLAR-LYNN", "Lynn Storey-Huylar", "Lynn", "Storey-Huylar", "Lynn A. Storey-Huylar; LYNN A. STOREY-HUYLA; Lynn A Storey-Huylar"),
        ("WY-HERMAN-MARGUERITE", "Marguerite Herman", "Marguerite", "Herman", ""),
        ("WY-SHANOR-SANDY", "Sandy Shanor", "Sandy", "Shanor", ""),
        ("WY-KLAASSEN-MARK", "Mark Klaassen", "Mark", "Klaassen", ""),
        ("WY-LANDEN-JIM", "Jim Landen", "Jim", "Landen", ""),
        ("WY-WIEDERSPAHN-RICH", "Rich Wiederspahn", "Rich", "Wiederspahn", ""),
        ("WY-RINNE-ROSE-ANN", "Rose Ann Rinne", "Rose Ann", "Rinne", ""),
        ("WY-LERWICK-MICHAEL", "Michael Lerwick", "Michael", "Lerwick", ""),
        ("WY-ROEDER-KENDRA", "Kendra Roeder", "Kendra", "Roeder", ""),
        ("WY-JESSEN-ASHLEY", "Ashley Jessen", "Ashley", "Jessen", ""),
        ("WY-NUSBAUM-CODY", "Cody Nusbaum", "Cody", "Nusbaum", ""),
        ("WY-KIRKBRIDE-JEFF", "Jeff Kirkbride", "Jeff", "Kirkbride", ""),
        ("WY-FORNSTROM-RUSSELL", "Russell Fornstrom", "Russell", "Fornstrom", ""),
        ("WY-ROMSA-HEIDI", "Heidi Romsa", "Heidi", "Romsa", ""),
        ("WY-WILSON-BILLIE", "Billie Wilson", "Billie", "Wilson", "Billie J. Wilson"),
        ("WY-WILES-JERRID", "Jerrid G. Wiles", "Jerrid", "Wiles", ""),
        ("WY-KEITER-DAVE", "Dave Keiter", "Dave", "Keiter", ""),
        ("WY-MAY-LEE", "Lee May", "Lee", "May", ""),
        ("WY-MORGAN-STEWART", "Stewart Morgan", "Stewart", "Morgan", ""),
        ("WY-HAAS-MATT", "Matt Haas", "Matt", "Haas", ""),
        ("WY-RANDALL-JULIANNE", "Julianne Randall", "Julianne", "Randall", ""),
        ("WY-FORNSTROM-TODD", "Todd Fornstrom", "Todd", "Fornstrom", ""),
        ("WY-OLSON-MIKE", "Mike Olson", "Mike", "Olson", ""),
        ("WY-GROENEWEG-KELLY", "Kelly Groeneweg", "Kelly", "Groeneweg", ""),
        ("WY-DAVISON-ESTHER", "Esther Davison", "Esther", "Davison", ""),
        ("WY-BOMHOFF-JACK", "Jack Bomhoff", "Jack", "Bomhoff", ""),
        ("WY-EPLER-CASEY", "Casey F. Epler", "Casey", "Epler", ""),
        ("WY-CHEREK-SCOTT", "Scott J. Cherek", "Scott", "Cherek", ""),
        ("WY-WELLS-KEVIN", "Kevin Wells", "Kevin", "Wells", "Kevin M. Wells"),
        ("WY-FARRELL-TOM", "Tom Farrell", "Tom", "Farrell", ""),
        ("WY-HEMMER-DENNIS", "Dennis Hemmer", "Dennis", "Hemmer", ""),
        ("WY-BERRY-JAY", "Jay Berry", "Jay", "Berry", ""),
        ("WY-SANCHEZ-ANN", "Ann Sanchez", "Ann", "Sanchez", ""),
        ("WY-KIRKBRIDE-LINDI", "Lindi Kirkbride", "Lindi", "Kirkbride", ""),
        ("WY-HARDING-MELISSA", "Melissa Harding", "Melissa", "Harding", ""),
        ("WY-CROWDER-JASON", "Jason Crowder", "Jason", "Crowder", ""),
        ("WY-RUNDELL-FORD", "Ford Rundell", "Ford", "Rundell", ""),
        ("WY-ASH-TIM", "Tim Ash", "Tim", "Ash", ""),
        # 1st JD judges (named official retentions only)
        ("WY-COOLEY", "Cooley", "Cooley", "Cooley", "DISTRICT COURT - COOLEY"),
        ("WY-HIBBEN", "Hibben", "Hibben", "Hibben", "DISTRICT COURT - HIBBEN"),
        ("WY-CAMPBELL-JD1", "Campbell", "Campbell", "Campbell", "DISTRICT COURT CAMPBELL"),
        ("WY-ROGERS-JD1", "Rogers", "Rogers", "Rogers", "DISTRICT COURT ROGERS"),
        ("WY-SHARPE-JD1", "Sharpe", "Sharpe", "Sharpe", "DIST CT - SHARPE"),
        ("WY-FROELICHER", "Froelicher", "Froelicher", "Froelicher", "DIST CT - FROELICHER"),
        ("WY-CHAMBERS-JD1", "Chambers", "Chambers", "Chambers", "CIRCUIT COURT - CHAMBERS"),
        ("WY-FORWOOD", "Forwood", "Forwood", "Forwood", "CIRCUIT COURT - FORWOOD"),
        ("WY-WILLIAMS-JD1", "Williams", "Williams", "Williams", "CIRCUIT COURT - WILLIAMS"),
        ("WY-LEE-JD1", "Lee", "Lee", "Lee", "CIRCUIT CT - LEE"),
        ("WY-HEALY-JD1", "Healy", "Healy", "Healy", "CIRCUIT COURT HEALY"),
        ("WY-NAU-JD1", "Nau", "Nau", "Nau", "CIRCUIT COURT NAU"),
        ("WY-ARNOLD-JD1", "Arnold", "Arnold", "Arnold", "DISTRICT COURT ARNOLD"),
    ]
    def add(row):
        pid, display, first, last, aka = row
        P(pid, display, first, last, aliases=aka, minted=True)
    for row in local:
        add(row)


def county_and_legislature_terms():
    terms = []

    def sen(dist, pid, name, start, end, year, notes="", party="R"):
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-senate",
                       office=f"Senate District {dist}", jurisdiction=f"Senate District {dist}",
                       term_start=FM[start], term_end=FM[end], election_year=year, notes=notes))

    def house(dist, pid, name, start, end, year, notes="", party="R"):
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-house",
                       office=f"House District {dist}", jurisdiction=f"House District {dist}",
                       term_start=FM[start], term_end=FM[end], election_year=year, notes=notes))

    def row(pid, name, office, start, end, year, notes="", party="R"):
        terms.append(T(person_id=pid, name=name, party=party, office_group="county",
                       office=office, jurisdiction="Laramie County",
                       term_start=FM[start], term_end=FM[end], election_year=year, notes=notes))

    def comm(pid, name, start, end, year, notes="", party="R"):
        row(pid, name, "County Commissioner", start, end, year, notes, party)

    # Official 2010 general also passed a measure to increase the number of county commissioners
    # (FOR 14,749 / AGAINST 14,296). The official 2012 general has two Vote-For-1 commissioner
    # contests; from January 2015 the board is the official 2014 Vote-For-3 plus the two 2012 seats.

    # 2012 presidential-year seats (in office January 2015–2016): Hasenauer, Holmes
    comm("WY-HASENAUER-M-LEE", "M. Lee Hasenauer", 2013, 2017, 2012,
         "Official 2012 general Vote-For-1, 19,052.")
    comm("WY-HOLMES-KN-BUCK", "K.N. Buck Holmes", 2013, 2017, 2012,
         "Official 2012 general Vote-For-1, 17,561. Ballot K.N. \"BUCK\" HOLMES.")

    # 2014 midterm VF3: Thompson, Heath, Kailey (Hasenauer was on the ballot and was not among the top three)
    comm("WY-THOMPSON-TROY", "Troy Thompson", 2015, 2019, 2014, "Official 2014 general Vote-For-3, 17,518.")
    comm("WY-HEATH-LINDA", "Linda Heath", 2015, 2019, 2014, "Official 2014 general Vote-For-3, 16,267.")
    comm("WY-KAILEY-RON-JR", "Ron Kailey Jr", 2015, 2019, 2014, "Official 2014 general Vote-For-3, 12,810.")

    # 2016 VF2: Ash, Holmes
    comm("WY-ASH-AMBER", "Amber Ash", 2017, 2021, 2016, "Official 2016 general Vote-For-2, 27,596.")
    comm("WY-HOLMES-KN-BUCK", "K.N. Buck Holmes", 2017, 2021, 2016, "Official 2016 general Vote-For-2, 25,177.")

    # 2018 VF3
    comm("WY-THOMPSON-TROY", "Troy Thompson", 2019, 2023, 2018, "Official 2018 general Vote-For-3, 20,084.")
    comm("WY-HEATH-LINDA", "Linda Heath", 2019, 2023, 2018, "Official 2018 general Vote-For-3, 18,822.")
    comm("WY-MALM-GUNNAR", "Gunnar Malm", 2019, 2023, 2018, "Official 2018 general Vote-For-3, 18,580.")

    # 2020 VF2
    comm("WY-LOVETT-BRIAN", "Brian Lovett", 2021, 2025, 2020, "Official 2020 general Vote-For-2, 30,639.")
    comm("WY-HOLMES-KN-BUCK", "K.N. Buck Holmes", 2021, 2025, 2020, "Official 2020 general Vote-For-2, 27,000.")

    # 2022 VF3
    comm("WY-THOMPSON-TROY", "Troy Thompson", 2023, 2027, 2022, "Official 2022 general Vote-For-3, 21,169.")
    comm("WY-MALM-GUNNAR", "Gunnar Malm", 2023, 2027, 2022, "Official 2022 general Vote-For-3, 21,045.")
    comm("WY-HEATH-LINDA", "Linda Heath", 2023, 2027, 2022, "Official 2022 general Vote-For-3, 20,101. Ballot Linda M Heath.")

    # 2024 VF2
    comm("WY-HOLLINGSHEAD-DON", "Don Hollingshead", 2025, 2029, 2024, "Official 2024 general Vote-For-2, 33,054.")
    comm("WY-ZWONITZER-TY", "Ty Zwonitzer", 2025, 2029, 2024, "Official 2024 general Vote-For-2, 32,219.")

    # 2026 VF3 (Ketcham succeeds Heath; Thompson and Malm re-elected)
    comm("WY-KETCHAM-JESS-E", "Jess E. Ketcham", 2027, 2031, 2026, "Official 2026 general Vote-For-3, 19,481. Succeeds Linda Heath.")
    comm("WY-THOMPSON-TROY", "Troy Thompson", 2027, 2031, 2026, "Official 2026 general Vote-For-3, 19,116.")
    comm("WY-MALM-GUNNAR", "Gunnar Malm", 2027, 2031, 2026, "Official 2026 general Vote-For-3, 18,775.")

    # Clerk (midterm 4-year)
    row("WY-LATHROP-DEBBYE", "Debbye Lathrop", "County Clerk", 2011, 2015, 2010, "Official 2010 general, 20,043. Term ends January 2015.")
    row("WY-LATHROP-DEBBYE", "Debbye Lathrop", "County Clerk", 2015, 2019, 2014, "Official 2014 general, 21,827.")
    row("WY-LEE-DEBRA", "Debra Lee", "County Clerk", 2019, 2023, 2018, "Official 2018 general, 27,011.")
    row("WY-LEE-DEBRA", "Debra Lee", "County Clerk", 2023, 2027, 2022, "Official 2022 general, 26,145.")
    row("WY-TINNEY-MISTY", "Misty Tinney", "County Clerk", 2027, 2031, 2026, "Official 2026 general, 25,643.")

    # Treasurer
    row("WY-EISELE-TRUDY", "Trudy L. Eisele", "County Treasurer", 2011, 2015, 2010, "Official 2010 general, 24,650 (ballot Trudy Eisele).")
    row("WY-EISELE-TRUDY", "Trudy L. Eisele", "County Treasurer", 2015, 2019, 2014, "Official 2014 general, 21,863.")
    row("WY-EISELE-TRUDY", "Trudy L. Eisele", "County Treasurer", 2019, 2023, 2018, "Official 2018 general, 27,073.")
    row("WY-DEISCH-TAMMY", "Tammy Deisch", "County Treasurer", 2023, 2027, 2022, "Official 2022 general, 25,319.")
    row("WY-WOOD-TRISTA", "Trista Wood", "County Treasurer", 2027, 2031, 2026, "Official 2026 general, 25,880.")

    # Assessor. Usual midterm 4-year cycle (2014, 2018, 2022). Official 2024 also lists Todd A. Ernst
    # (mid-term relative to Guille's 2022 term); official 2026 is the next regular midterm contest.
    row("WY-GUILLE-KENNETH", "Kenneth Guille", "County Assessor", 2015, 2019, 2014, "Official 2014 general, 21,088.")
    row("WY-GUILLE-KENNETH", "Kenneth Guille", "County Assessor", 2019, 2023, 2018, "Official 2018 general, 26,433.")
    row("WY-GUILLE-KENNETH", "Kenneth Guille", "County Assessor", 2023, 2025, 2022, "Official 2022 general, 25,478. The usual midterm term would have run through January 2027; official 2024 general winner Todd A. Ernst is used beginning January 2025. Mid-term succession date is not stated in the official generals.")
    row("WY-ERNST-TODD-A", "Todd A. Ernst", "County Assessor", 2025, 2027, 2024,
        "Official 2024 general, 37,089. Mid-term relative to the usual midterm assessor cycle (official 2022 winner Kenneth Guille). Term encoded as the remainder through January 2027; mid-term succession date is not stated in the official generals.",
        )
    # Mark 2024 assessor term medium because remainder end is inferred from the next official regular (2026) contest.
    terms[-1]["confidence"] = "medium"
    row("WY-ERNST-TODD-A", "Todd A. Ernst", "County Assessor", 2027, 2031, 2026, "Official 2026 general, 25,813. Regular midterm 4-year term.")

    # Sheriff
    row("WY-GLICK-DANNY", "Danny Glick", "County Sheriff", 2011, 2015, 2010, "Official 2010 general, 24,219.")
    row("WY-GLICK-DANNY", "Danny Glick", "County Sheriff", 2015, 2019, 2014, "Official 2014 general, 17,983.")
    row("WY-GLICK-DANNY", "Danny Glick", "County Sheriff", 2019, 2023, 2018, "Official 2018 general, 20,296.")
    row("WY-KOZAK-BRIAN", "Brian Kozak", "County Sheriff", 2023, 2027, 2022, "Official 2022 general, 13,959.")
    row("WY-KOZAK-BRIAN", "Brian Kozak", "County Sheriff", 2027, 2031, 2026, "Official 2026 general, 19,077.")

    # District Attorney (not County Attorney)
    row("WY-SANDBURG-JEREMIAH", "Jeremiah Sandburg", "District Attorney", 2015, 2019, 2014, "Official 2014 general, 20,661.")
    row("WY-MANLOVE-LEIGH-ANNE", "Leigh Anne Manlove", "District Attorney", 2019, 2023, 2018, "Official 2018 general, 21,087.")
    row("WY-HACKL-SYLVIA", "Sylvia Miller Hackl", "District Attorney", 2023, 2027, 2022,
         "Official 2022 general, 24,999. Ballot Sylvia Miller Hackl.")
    row("WY-HACKL-SYLVIA", "Sylvia Miller Hackl", "District Attorney", 2027, 2031, 2026,
         "Official 2026 general, 25,743. Ballot Sylvia Lee Hackl.")

    # Clerk of District Court
    row("WY-LANDERS-SANDY", "Sandy Landers", "Clerk of District Court", 2011, 2015, 2010, "Official 2010 general, 17,683.")
    row("WY-SANCHEZ-DIANE", "Diane Sanchez", "Clerk of District Court", 2015, 2019, 2014, "Official 2014 general, 21,231. Ballot Diane K. Sanchez.")
    row("WY-SANCHEZ-DIANE", "Diane Sanchez", "Clerk of District Court", 2019, 2023, 2018, "Official 2018 general, 26,662. Ballot Diane K. Sanchez.")
    row("WY-SANCHEZ-DIANE", "Diane Sanchez", "Clerk of District Court", 2023, 2027, 2022, "Official 2022 general, 25,739.")
    row("WY-SANCHEZ-DIANE", "Diane Sanchez", "Clerk of District Court", 2027, 2031, 2026, "Official 2026 general, 26,256.")

    # Coroner
    row("WY-LUNA-MARTY", "Marty Luna", "County Coroner", 2011, 2015, 2010, "Official 2010 general, 25,463.")
    row("WY-SARGENT-RONALD-J", "Ronald J. Sargent", "County Coroner", 2015, 2019, 2014, "Official 2014 general, 21,274.")
    row("WY-REID-REBECCA", "Rebecca Reid", "County Coroner", 2019, 2023, 2018, "Official 2018 general, 26,445.")
    row("WY-REID-REBECCA", "Rebecca Reid", "County Coroner", 2023, 2027, 2022, "Official 2022 general, 25,917.")
    row("WY-REID-REBECCA", "Rebecca Reid", "County Coroner", 2027, 2031, 2026, "Official 2026 general, 25,830.")

    # ----- Senate -----
    # S04 presidential-year
    sen("4 (S04)", "WY-ROSS-TONY", "Tony Ross", 2013, 2017, 2012, "Official 2012 general, 7,555.")
    sen("4 (S04)", "WY-NETHERCOTT-TARA", "Tara Nethercott", 2017, 2021, 2016, "Official 2016 general, 5,867.")
    sen("4 (S04)", "WY-NETHERCOTT-TARA", "Tara Nethercott", 2021, 2025, 2020, "Official 2020 general, 9,299.")
    sen("4 (S04)", "WY-NETHERCOTT-TARA", "Tara Nethercott", 2025, 2029, 2024, "Official 2024 general, 8,255.")

    # S05 midterm
    sen("5 (S05)", "WY-EMERICH-FRED", "Fred Emerich", 2015, 2019, 2014, "Official 2014 general, 5,026.")
    sen("5 (S05)", "WY-HUTCHINGS-LYNN", "Lynn Hutchings", 2019, 2023, 2018, "Official 2018 general, 5,382.")
    sen("5 (S05)", "WY-HUTCHINGS-LYNN", "Lynn Hutchings", 2023, 2027, 2022, "Official 2022 general, 3,284.")
    sen("5 (S05)", "WY-SCHOENFELD-LAUREN", "Lauren Schoenfeld", 2027, 2031, 2026, "Official 2026 general, 3,357.")

    # S06 presidential-year, plus official 2026 contest
    sen("6 (S06)", "WY-JOHNSON-WAYNE", "Wayne Johnson", 2013, 2017, 2012, "Official 2012 general, 5,802 (74.87%).")
    sen("6 (S06)", "WY-BOUCHARD-ANTHONY", "Anthony Bouchard", 2017, 2021, 2016, "Official 2016 general, 4,492.")
    sen("6 (S06)", "WY-BOUCHARD-ANTHONY", "Anthony Bouchard", 2021, 2025, 2020, "Official 2020 general, 6,680.")
    sen("6 (S06)", "WY-SMITH-DARIN", "Darin Smith", 2025, 2029, 2024,
        "Official 2024 general, 4,486. The official 2026 general names Taft Love as the Senate District 6 winner; January 2025–2026 snapshots keep Smith as the last official general-election holder. The mid-term succession date is not stated in the official generals.")
    sen("6 (S06)", "WY-LOVE-TAFT", "Taft Love", 2027, 2029, 2026,
        "Official 2026 general, 3,199, not labeled unexpired on the official summary. Official 2024 general winner was Darin Smith. Encoded as the remainder of the 2024 term through January 2029; term length is inferred. Same person as official LCSD #2 trustee Taft C. Love.")
    terms[-1]["confidence"] = "medium"

    # S07 midterm
    sen("7 (S07)", "WY-PAPPAS-STEPHAN", "Stephan Pappas", 2015, 2019, 2014, "Official 2014 general, 2,258.")
    sen("7 (S07)", "WY-PAPPAS-STEPHAN", "Stephan Pappas", 2019, 2023, 2018, "Official 2018 general, 3,723. Ballot Stephan A. Pappas.")
    sen("7 (S07)", "WY-PAPPAS-STEPHAN", "Stephan Pappas", 2023, 2027, 2022, "Official 2022 general, 3,238.")
    sen("7 (S07)", "WY-RINNE-MARK", "Mark Rinne", 2027, 2031, 2026,
        "Official 2026 general, 3,276. Same person as Cheyenne City Council Ward 2 member Mark D. Rinne (official municipal results).")

    # S08 presidential-year
    sen("8 (S08)", "WY-ESQUIBEL-FLOYD", "Floyd A. Esquibel", 2013, 2017, 2012, "Official 2012 general, 2,963 (52.27%).", party="D")
    sen("8 (S08)", "WY-ELLIS-AFFIE", "Affie Ellis", 2017, 2021, 2016, "Official 2016 general, 3,638.")
    sen("8 (S08)", "WY-ELLIS-AFFIE", "Affie Ellis", 2021, 2025, 2020, "Official 2020 general, 4,231.")
    sen("8 (S08)", "WY-OLSEN-JARED", "Jared Olsen", 2025, 2029, 2024, "Official 2024 general, 3,444. Previously H11.")

    # S31 (created in the 2022 redistricting; first official Laramie general in 2022)
    sen("31 (S31)", "WY-BRENNAN-EVIE", "Evie Brennan", 2023, 2027, 2022, "Official 2022 general, 3,807.")
    sen("31 (S31)", "WY-BRENNAN-EVIE", "Evie Brennan", 2027, 2031, 2026, "Official 2026 general, 3,174.")

    # ----- House (2-year terms) -----
    # H04 appears on official Laramie federal/state summaries beginning 2022 (Laramie County portion of the district).
    house("4 (H04)", "WY-HAROLDSON-JEREMY", "Jeremy Haroldson", 2023, 2025, 2022, "Official 2022 SOS statewide House summary totals: Jeremy Haroldson 2,539, Dan Brecht 1,436. Official Laramie County portion: Haroldson 44, Brecht 11. Also covers Platte County.")
    house("4 (H04)", "WY-HAROLDSON-JEREMY", "Jeremy Haroldson", 2025, 2027, 2024, "Official 2024 SOS statewide House summary totals: Jeremy Haroldson 3,516, Charles Randolph 1,014. Official Laramie County portion: Haroldson 78, Randolph 7. Also covers Platte County.")
    house("4 (H04)", "WY-HAROLDSON-JEREMY", "Jeremy Haroldson", 2027, 2029, 2026, "Official 2026 SOS statewide House summary totals: Jeremy Haroldson 2,533. Official Laramie County portion: 57. Also covers Platte County.")

    house("7 (H07)", "WY-WILSON-SUE", "Sue Wilson", 2013, 2015, 2012, "Official 2012 general, 3,320.")
    house("7 (H07)", "WY-WILSON-SUE", "Sue Wilson", 2015, 2017, 2014, "Official 2014 general, 3,386.")
    house("7 (H07)", "WY-WILSON-SUE", "Sue Wilson", 2017, 2019, 2016, "Official 2016 general, 4,782.")
    house("7 (H07)", "WY-WILSON-SUE", "Sue Wilson", 2019, 2021, 2018, "Official 2018 general, 4,283.")
    house("7 (H07)", "WY-WILSON-SUE", "Sue Wilson", 2021, 2023, 2020, "Official 2020 general, 5,804.")
    house("7 (H07)", "WY-NICHOLAS-BOB", "Bob Nicholas", 2023, 2025, 2022, "Official 2022 general, 2,043. Previously H08.")
    house("7 (H07)", "WY-NICHOLAS-BOB", "Bob Nicholas", 2025, 2027, 2024, "Official 2024 general, 2,791.")
    house("7 (H07)", "WY-NICHOLAS-BOB", "Bob Nicholas", 2027, 2029, 2026, "Official 2026 general, 1,993.")

    house("8 (H08)", "WY-NICHOLAS-BOB", "Bob Nicholas", 2013, 2015, 2012, "Official 2012 general, 2,531.")
    house("8 (H08)", "WY-NICHOLAS-BOB", "Bob Nicholas", 2015, 2017, 2014, "Official 2014 general, 2,481.")
    house("8 (H08)", "WY-NICHOLAS-BOB", "Bob Nicholas", 2017, 2019, 2016, "Official 2016 general, 2,570.")
    house("8 (H08)", "WY-NICHOLAS-BOB", "Bob Nicholas", 2019, 2021, 2018, "Official 2018 general, 2,212.")
    house("8 (H08)", "WY-NICHOLAS-BOB", "Bob Nicholas", 2021, 2023, 2020, "Official 2020 general, 2,547.")
    house("8 (H08)", "WY-ZWONITZER-DAVE", "Dave Zwonitzer", 2023, 2025, 2022, "Official 2022 general, 2,717. Ballot Dave Zwonitzer. Distinct from Dan Zwonitzer (H43) and Ty Zwonitzer (commissioner).")
    house("8 (H08)", "WY-JOHNSON-STEVE", "Steve Johnson", 2025, 2027, 2024, "Official 2024 general, 4,229.")
    house("8 (H08)", "WY-REINER-LUKE", "Luke Reiner", 2027, 2029, 2026, "Official 2026 general, 3,120.")

    house("9 (H09)", "WY-ZWONITZER-DAVE", "David L. Zwonitzer", 2013, 2015, 2012, "Official 2012 general, 2,609.")
    house("9 (H09)", "WY-ZWONITZER-DAVE", "David Zwonitzer", 2015, 2017, 2014, "Official 2014 general, 1,444.")
    house("9 (H09)", "WY-BROWN-LANDON", "Landon Brown", 2017, 2019, 2016, "Official 2016 general, 2,299.")
    house("9 (H09)", "WY-BROWN-LANDON", "Landon J. Brown", 2019, 2021, 2018, "Official 2018 general, 2,594.")
    house("9 (H09)", "WY-BROWN-LANDON", "Landon J. Brown", 2021, 2023, 2020, "Official 2020 general, 3,798.")
    house("9 (H09)", "WY-BROWN-LANDON", "Landon J. Brown", 2023, 2025, 2022, "Official 2022 general, 2,014.")
    house("9 (H09)", "WY-BROWN-LANDON", "Landon J. Brown", 2025, 2027, 2024, "Official 2024 general, 3,453.")
    house("9 (H09)", "WY-WIGGAM-BOYD", "Boyd O. Wiggam", 2027, 2029, 2026, "Official 2026 general, 1,792.")

    house("10 (H10)", "WY-EKLUND-JOHN", "John Eklund", 2013, 2015, 2012, "Official 2012 general, 3,641.")
    house("10 (H10)", "WY-EKLUND-JOHN", "John Eklund", 2015, 2017, 2014, "Official 2014 general, 2,144.")
    house("10 (H10)", "WY-EKLUND-JOHN", "John Eklund", 2017, 2019, 2016, "Official 2016 general, 3,994.")
    house("10 (H10)", "WY-EKLUND-JOHN", "John Eklund", 2019, 2021, 2018, "Official 2018 general, 3,187.")
    house("10 (H10)", "WY-EKLUND-JOHN", "John Eklund", 2021, 2023, 2020, "Official 2020 general, 5,360.")
    house("10 (H10)", "WY-EKLUND-JOHN", "John Eklund", 2023, 2025, 2022, "Official 2022 general, 3,197.")
    house("10 (H10)", "WY-EKLUND-JOHN", "John Eklund", 2025, 2027, 2024, "Official 2024 general, 3,963.")
    house("10 (H10)", "WY-FORNSTROM-JUSTIN", "Justin Fornstrom", 2027, 2029, 2026, "Official 2026 general, 2,911. Same person as the official 2024 Pine Bluffs mayor.")

    house("11 (H11)", "WY-THRONE-MARY", "Mary A. Throne", 2013, 2015, 2012, "Official 2012 general, 1,727.", party="D")
    house("11 (H11)", "WY-THRONE-MARY", "Mary A. Throne", 2015, 2017, 2014, "Official 2014 general, 1,093.", party="D")
    house("11 (H11)", "WY-OLSEN-JARED", "Jared Olsen", 2017, 2019, 2016, "Official 2016 general, 1,549.")
    house("11 (H11)", "WY-OLSEN-JARED", "Jared Olsen", 2019, 2021, 2018, "Official 2018 general, 1,275.")
    house("11 (H11)", "WY-OLSEN-JARED", "Jared Olsen", 2021, 2023, 2020, "Official 2020 general, 1,807.")
    house("11 (H11)", "WY-OLSEN-JARED", "Jared Olsen", 2023, 2025, 2022, "Official 2022 general, 1,145.")
    house("11 (H11)", "WY-WASSERBURGER-JACOB", "Jacob Wasserburger", 2025, 2027, 2024, "Official 2024 general, 1,774.")
    house("11 (H11)", "WY-TENNANT-BRITNEY", "Britney Tennant", 2027, 2029, 2026, "Official 2026 general, 1,080.", party="D")

    house("12 (H12)", "WY-FILER-LEE", "Lee R. Filer", 2013, 2015, 2012, "Official 2012 general, 1,578.", party="D")
    house("12 (H12)", "WY-EDMONDS-HARLAN", "Harlan Edmonds", 2015, 2017, 2014, "Official 2014 general, 930.")
    house("12 (H12)", "WY-LONE-LARS", "Lars Lone", 2017, 2019, 2016, "Official 2016 general, 1,756.")
    house("12 (H12)", "WY-STYVAR-CLARENCE", "Clarence L. Styvar", 2019, 2021, 2018, "Official 2018 general, 1,359.")
    house("12 (H12)", "WY-STYVAR-CLARENCE", "Clarence Styvar", 2021, 2023, 2020, "Official 2020 general, 2,327.")
    house("12 (H12)", "WY-STYVAR-CLARENCE", "Clarence Styvar", 2023, 2025, 2022, "Official 2022 general, 1,377.")
    house("12 (H12)", "WY-STYVAR-CLARENCE", "Clarence Styvar", 2025, 2027, 2024, "Official 2024 general, 2,252.")
    house("12 (H12)", "WY-STYVAR-CLARENCE", "Clarence Styvar", 2027, 2029, 2026, "Official 2026 general, 1,360.")

    house("41 (H41)", "WY-ESQUIBEL-KEN", "Ken A. Esquibel", 2013, 2015, 2012, "Official 2012 general, 2,164.", party="D")
    house("41 (H41)", "WY-ESQUIBEL-KEN", "Ken A. Esquibel", 2015, 2017, 2014, "Official 2014 general, 1,479.", party="D")
    house("41 (H41)", "WY-HENDERSON-BILL", "Bill Henderson", 2017, 2019, 2016, "Official 2016 general, 1,976.")
    house("41 (H41)", "WY-HENDERSON-BILL", "Bill Henderson", 2019, 2021, 2018, "Official 2018 general, 1,552.")
    house("41 (H41)", "WY-HENDERSON-BILL", "Bill Henderson", 2021, 2023, 2020, "Official 2020 general, 2,497.")
    house("41 (H41)", "WY-HENDERSON-BILL", "Bill Henderson", 2023, 2025, 2022, "Official 2022 general, 1,384.")
    house("41 (H41)", "WY-BROWN-GARY", "Gary Brown", 2025, 2027, 2024, "Official 2024 general, 2,039. Distinct from Landon J. Brown (H09).")
    house("41 (H41)", "WY-EDWARDS-ERIN", "Erin Edwards", 2027, 2029, 2026, "Official 2026 general, 1,602.")

    house("42 (H42)", "WY-HUTCHINGS-LYNN", "Lynn Hutchings", 2013, 2015, 2012, "Official 2012 general, 2,833. Later S05.")
    house("42 (H42)", "WY-BLACKBURN-THEODORE", "Theodore Blackburn", 2015, 2017, 2014, "Official 2014 general, 1,800. Distinct ID from Jim Blackburn.")
    house("42 (H42)", "WY-BLACKBURN-JIM", "Jim Blackburn", 2017, 2019, 2016, "Official 2016 general, 2,775.")
    house("42 (H42)", "WY-BLACKBURN-JIM", "Jim Blackburn", 2019, 2021, 2018, "Official 2018 general, 2,187.")
    house("42 (H42)", "WY-BLACKBURN-JIM", "Jim Blackburn", 2021, 2023, 2020, "Official 2020 general, 3,918.")
    house("42 (H42)", "WY-HORNOK-BEN", "Ben Hornok", 2023, 2025, 2022, "Official 2022 general, 2,414.")
    house("42 (H42)", "WY-GERINGER-ROB", "Rob Geringer", 2025, 2027, 2024, "Official 2024 general, 3,270.")
    house("42 (H42)", "WY-GERINGER-ROB", "Rob Geringer", 2027, 2029, 2026, "Official 2026 general, 2,376.")

    house("43 (H43)", "WY-ZWONITZER-DAN", "Dan Zwonitzer", 2013, 2015, 2012, "Official 2012 general, 2,490.")
    house("43 (H43)", "WY-ZWONITZER-DAN", "Dan Zwonitzer", 2015, 2017, 2014, "Official 2014 general, 1,474.")
    house("43 (H43)", "WY-ZWONITZER-DAN", "Dan Zwonitzer", 2017, 2019, 2016, "Official 2016 general, 2,620.")
    house("43 (H43)", "WY-ZWONITZER-DAN", "Dan Zwonitzer", 2019, 2021, 2018, "Official 2018 general, 1,901.")
    house("43 (H43)", "WY-ZWONITZER-DAN", "Dan Zwonitzer", 2021, 2023, 2020, "Official 2020 general, 2,918.")
    house("43 (H43)", "WY-ZWONITZER-DAN", "Dan Zwonitzer", 2023, 2025, 2022, "Official 2022 general, 2,193.")
    house("43 (H43)", "WY-LUCAS-ANN", "Ann Lucas", 2025, 2027, 2024, "Official 2024 general, 3,540.")
    house("43 (H43)", "WY-CROWDER-JESSICA", "Jessica Crowder", 2027, 2029, 2026, "Official 2026 general, 2,443.")

    house("44 (H44)", "WY-BYRD-JAMES", "James W. Byrd", 2013, 2015, 2012, "Official 2012 general, 1,486.", party="D")
    house("44 (H44)", "WY-BYRD-JAMES", "James W. Byrd", 2015, 2017, 2014, "Official 2014 general, 1,113.", party="D")
    house("44 (H44)", "WY-BYRD-JAMES", "James W. Byrd", 2017, 2019, 2016, "Official 2016 general, 1,412.", party="D")
    house("44 (H44)", "WY-BURLINGAME-SARA", "Sara Burlingame", 2019, 2021, 2018, "Official 2018 general, 1,058.", party="D")
    house("44 (H44)", "WY-ROMERO-MARTINEZ-JOHN", "John B. Romero-Martinez", 2021, 2023, 2020, "Official 2020 general, 1,552.")
    house("44 (H44)", "WY-TRUJILLO-TAMARA", "Tamara N. Trujillo", 2023, 2025, 2022, "Official 2022 general, 937.")
    house("44 (H44)", "WY-FILER-LEE", "Lee Filer", 2025, 2027, 2024, "Official 2024 general, 2,265. Same person as official 2012 H12 winner Lee R. Filer.")
    house("44 (H44)", "WY-FILER-LEE", "Lee Filer", 2027, 2029, 2026, "Official 2026 general, 1,256.")

    # H61 first official Laramie general in 2022
    house("61 (H61)", "WY-SINGH-DANIEL", "Daniel J. Singh", 2023, 2025, 2022, "Official 2022 general, 1,561.")
    house("61 (H61)", "WY-SINGH-DANIEL", "Daniel J. Singh", 2025, 2027, 2024, "Official 2024 general, 2,516.")
    house("61 (H61)", "WY-SERVER-ANDREW", "Andrew Server", 2027, 2029, 2026, "Official 2026 general, 1,515.")

    return terms

def judicial_terms():
    """Named 1st Judicial District retentions on official Laramie general ballots only.
    Names are the official contest last names (the summaries do not print a given name).
    The official 2018 circuit retention has no judge’s name and is not attached."""
    terms = []

    def retain(pid, name, office, year, yes, no, start, end, notes=""):
        tot = yes + no
        src = [fs(year)] if year in FS else [pg(year)]
        terms.append(T(person_id=pid, name=name, office_group="judicial",
                       office=office, jurisdiction="1st Judicial District",
                       term_start=FM[start], term_end=FM[end], election_year=year,
                       how_took_office="retained", sources=src,
                       notes=notes or f"Official Laramie {year} general retention, YES {yes:,} / NO {no:,}.",
                       retention={"year": year, "yes": yes, "no": no,
                                  "yes_pct": f"{yes/tot*100:.2f}%", "no_pct": f"{no/tot*100:.2f}%",
                                  "result": "retained", "source": (FS.get(year) or PG[year])[0]}))

    # Official 2020 federal/state summary (named)
    retain("WY-SHARPE-JD1", "Sharpe", "District Judge, 1st Judicial District (Sharpe)",
           2020, 32599, 8762, 2021, 2027,
           "Official 2020 general “DIST CT - SHARPE,” YES 32,599 / NO 8,762. Official ballot last name only.")
    retain("WY-FROELICHER", "Froelicher", "District Judge, 1st Judicial District (Froelicher)",
           2020, 31755, 9222, 2021, 2027,
           "Official 2020 general “DIST CT - FROELICHER,” YES 31,755 / NO 9,222. Official ballot last name only.")
    retain("WY-LEE-JD1", "Lee", "Circuit Judge, 1st Judicial District (Lee)",
           2020, 32436, 8641, 2021, 2025,
           "Official 2020 general “CIRCUIT CT - LEE,” YES 32,436 / NO 8,641. Official ballot last name only.")
    retain("WY-WILLIAMS-JD1", "Williams", "Circuit Judge, 1st Judicial District (Williams)",
           2020, 31262, 9760, 2021, 2025,
           "Official 2020 general “CIRCUIT CT - WILLIAMS,” YES 31,262 / NO 9,760. Official ballot last name only.")

    # Official 2022
    retain("WY-CAMPBELL-JD1", "Campbell", "District Judge, 1st Judicial District (Campbell)",
           2022, 20557, 7643, 2023, 2029,
           "Official 2022 general “DISTRICT COURT CAMPBELL,” YES 20,557 / NO 7,643. Official ballot last name only. This is the 1st Judicial District (Laramie), not Campbell County.")
    retain("WY-ROGERS-JD1", "Rogers", "District Judge, 1st Judicial District (Rogers)",
           2022, 19868, 8133, 2023, 2029,
           "Official 2022 general “DISTRICT COURT ROGERS,” YES 19,868 / NO 8,133. Official ballot last name only.")
    retain("WY-CHAMBERS-JD1", "Chambers", "Circuit Judge, 1st Judicial District (Chambers)",
           2022, 20763, 6849, 2023, 2027,
           "Official 2022 general “CIRCUIT COURT CHAMBERS,” YES 20,763 / NO 6,849. Official ballot last name only.")

    # Official 2024
    retain("WY-WILLIAMS-JD1", "Williams", "Circuit Judge, 1st Judicial District (Williams)",
           2024, 29124, 10394, 2025, 2029,
           "Official 2024 general “CIRCUIT COURT - WILLIAMS,” YES 29,124 / NO 10,394. Official ballot last name only.")

    # Official 2026
    retain("WY-COOLEY", "Cooley", "District Judge, 1st Judicial District (Cooley)",
           2026, 20836, 7289, 2027, 2033,
           "Official 2026 general “DISTRICT COURT - COOLEY,” YES 20,836 / NO 7,289. Official ballot last name only.")
    retain("WY-HIBBEN", "Hibben", "District Judge, 1st Judicial District (Hibben)",
           2026, 20853, 7076, 2027, 2033,
           "Official 2026 general “DISTRICT COURT - HIBBEN,” YES 20,853 / NO 7,076. Official ballot last name only.")
    retain("WY-CHAMBERS-JD1", "Chambers", "Circuit Judge, 1st Judicial District (Chambers)",
           2026, 20979, 6940, 2027, 2031,
           "Official 2026 general “CIRCUIT COURT - CHAMBERS,” YES 20,979 / NO 6,940 (also on the official city/county summary). Official ballot last name only.")
    retain("WY-FORWOOD", "Forwood", "Circuit Judge, 1st Judicial District (Forwood)",
           2026, 21328, 6651, 2027, 2031,
           "Official 2026 general “CIRCUIT COURT - FORWOOD,” YES 21,328 / NO 6,651 (also on the official city/county summary). Official ballot last name only.")
    return terms


def local_terms():
    terms = []

    def muni(pid, name, office, jur, start, end, year, notes="", party=""):
        terms.append(T(person_id=pid, name=name, party=party, office_group="municipal",
                       office=office, jurisdiction=jur,
                       term_start=FM[start], term_end=FM[end], election_year=year, notes=notes))

    def sch(pid, name, office, jur, start, end, year, notes="", sources=None):
        kw = dict(person_id=pid, name=name, office_group="schools",
                  office=office, jurisdiction=jur,
                  term_start=FM[start], term_end=FM[end], election_year=year, notes=notes)
        if sources:
            kw["sources"] = sources
        terms.append(T(**kw))

    def spec(pid, name, office, jur, start, end, year, notes=""):
        terms.append(T(person_id=pid, name=name, office_group="special-districts",
                       office=office, jurisdiction=jur,
                       term_start=FM[start], term_end=FM[end], election_year=year, notes=notes))

    # Cheyenne mayor — official November generals (4-year)
    muni("WY-KAYSEN-RICHARD", "Richard L. Kaysen", "Cheyenne Mayor", "City of Cheyenne", 2013, 2017, 2012,
         "Official 2012 general, 13,609.")
    muni("WY-ORR-MARIAN", "Marian Orr", "Cheyenne Mayor", "City of Cheyenne", 2017, 2021, 2016,
         "Official 2016 general, 14,383.")
    muni("WY-COLLINS-PATRICK", "Patrick Collins", "Cheyenne Mayor", "City of Cheyenne", 2021, 2025, 2020,
         "Official 2020 general, 18,134.")
    muni("WY-COLLINS-PATRICK", "Patrick Collins", "Cheyenne Mayor", "City of Cheyenne", 2025, 2029, 2024,
         "Official 2024 general, 14,992.")

    # Cheyenne council: official midterm Vote-For-1 and presidential Vote-For-2 results
    # used for the current 3-members-per-ward board (2022 VF1 + 2024 VF2 + 2026 VF1).
    muni("WY-ROYBAL-SCOTT", "Scott D. Roybal", "Cheyenne City Council Ward 1", "City of Cheyenne", 2015, 2019, 2014,
         "Official 2014 general, 1,985.")
    muni("WY-RINNE-MARK", "Mark D. Rinne", "Cheyenne City Council Ward 2", "City of Cheyenne", 2015, 2019, 2014,
         "Official 2014 general, 5,669.")
    muni("WY-JOHNSON-RICHARD", "Richard Johnson", "Cheyenne City Council Ward 3", "City of Cheyenne", 2015, 2019, 2014,
         "Official 2014 general, 2,214.")

    muni("WY-LAYBOURN-PETE", "Pete Laybourn", "Cheyenne City Council Ward 1", "City of Cheyenne", 2017, 2021, 2016,
         "Official 2016 general Vote-For-2, 3,037.")
    muni("WY-WHITE-JEFF", "Jeff White", "Cheyenne City Council Ward 1", "City of Cheyenne", 2017, 2021, 2016,
         "Official 2016 general Vote-For-2, 2,757.")
    muni("WY-COOK-BRYAN", "Bryan M. Cook", "Cheyenne City Council Ward 2", "City of Cheyenne", 2017, 2021, 2016,
         "Official 2016 general Vote-For-2, 5,650.")
    muni("WY-SHANOR-DICKY", "Dicky Shanor", "Cheyenne City Council Ward 2", "City of Cheyenne", 2017, 2021, 2016,
         "Official 2016 general Vote-For-2, 5,368.")
    muni("WY-LUNA-MIKE", "Mike Luna", "Cheyenne City Council Ward 3", "City of Cheyenne", 2017, 2021, 2016,
         "Official 2016 general, 4,305.")

    muni("WY-ROYBAL-SCOTT", "Scott D. Roybal", "Cheyenne City Council Ward 1", "City of Cheyenne", 2019, 2023, 2018,
         "Official 2018 general, 2,691.")
    muni("WY-RINNE-MARK", "Mark D. Rinne", "Cheyenne City Council Ward 2", "City of Cheyenne", 2019, 2023, 2018,
         "Official 2018 general, 4,749.")
    muni("WY-ESQUIBEL-KEN", "Ken A. Esquibel", "Cheyenne City Council Ward 3", "City of Cheyenne", 2019, 2023, 2018,
         "Official 2018 general, 3,513.")

    muni("WY-LAYBOURN-PETE", "Pete Laybourn", "Cheyenne City Council Ward 1", "City of Cheyenne", 2021, 2025, 2020,
         "Official 2020 general Vote-For-2, 3,780.")
    muni("WY-WHITE-JEFF", "Jeff White", "Cheyenne City Council Ward 1", "City of Cheyenne", 2021, 2025, 2020,
         "Official 2020 general Vote-For-2, 3,574.")
    muni("WY-COOK-BRYAN", "Bryan M. Cook", "Cheyenne City Council Ward 2", "City of Cheyenne", 2021, 2025, 2020,
         "Official 2020 general Vote-For-2, 5,921.")
    muni("WY-SEGRAVE-TOM", "Tom Segrave", "Cheyenne City Council Ward 2", "City of Cheyenne", 2021, 2025, 2020,
         "Official 2020 general Vote-For-2, 5,265.")
    muni("WY-ALDRICH-MICHELLE", "Michelle D. Aldrich", "Cheyenne City Council Ward 3", "City of Cheyenne", 2021, 2025, 2020,
         "Official 2020 general Vote-For-2, 4,599.")
    muni("WY-JOHNSON-RICHARD", "Richard Johnson", "Cheyenne City Council Ward 3", "City of Cheyenne", 2021, 2025, 2020,
         "Official 2020 general Vote-For-2, 4,343.")

    muni("WY-ROYBAL-SCOTT", "Scott D. Roybal", "Cheyenne City Council Ward 1", "City of Cheyenne", 2023, 2027, 2022,
         "Official 2022 general Vote-For-1, 2,694.")
    muni("WY-RINNE-MARK", "Mark D. Rinne", "Cheyenne City Council Ward 2", "City of Cheyenne", 2023, 2027, 2022,
         "Official 2022 general Vote-For-1, 4,269.")
    muni("WY-ESQUIBEL-KEN", "Ken A. Esquibel", "Cheyenne City Council Ward 3", "City of Cheyenne", 2023, 2027, 2022,
         "Official 2022 general Vote-For-1, 2,765.")

    muni("WY-WHITE-JEFF", "Jeff White", "Cheyenne City Council Ward 1", "City of Cheyenne", 2025, 2029, 2024,
         "Official 2024 general Vote-For-2, 3,969.")
    muni("WY-LAYBOURN-PETE", "Pete Laybourn", "Cheyenne City Council Ward 1", "City of Cheyenne", 2025, 2029, 2024,
         "Official 2024 general Vote-For-2, 3,528.")
    muni("WY-EMMONS-KATHY", "Kathy Emmons", "Cheyenne City Council Ward 2", "City of Cheyenne", 2025, 2029, 2024,
         "Official 2024 general Vote-For-2, 5,830. Same name as LCCC trustee Kathy Emmons.")
    muni("WY-SEGRAVE-TOM", "Tom Segrave", "Cheyenne City Council Ward 2", "City of Cheyenne", 2025, 2029, 2024,
         "Official 2024 general Vote-For-2, 5,635.")
    muni("WY-ALDRICH-MICHELLE", "Michelle Aldrich", "Cheyenne City Council Ward 3", "City of Cheyenne", 2025, 2029, 2024,
         "Official 2024 general Vote-For-2, 4,904.")
    muni("WY-MOODY-MARK-A", "Mark A. Moody", "Cheyenne City Council Ward 3", "City of Cheyenne", 2025, 2029, 2024,
         "Official 2024 general Vote-For-2, 4,586.")

    muni("WY-KALLAS-MAREN", "Maren Kallas", "Cheyenne City Council Ward 1", "City of Cheyenne", 2027, 2031, 2026,
         "Official 2026 general Vote-For-1, 2,626. Succeeds Scott D. Roybal.")
    muni("WY-ROSE-JANELLE", "Janelle Rose", "Cheyenne City Council Ward 2", "City of Cheyenne", 2027, 2031, 2026,
         "Official 2026 general Vote-For-1, 4,466. Succeeds Mark D. Rinne.")
    muni("WY-ESQUIBEL-KEN", "Ken A. Esquibel", "Cheyenne City Council Ward 3", "City of Cheyenne", 2027, 2031, 2026,
         "Official 2026 general Vote-For-1, 2,699.")

    # Pine Bluffs appears on official November city/county summaries in 2024 and 2026.
    # Official 2024 and 2026 both include a mayoral contest; terms are encoded as two-year
    # (inferred from that official ballot pattern).
    muni("WY-FORNSTROM-JUSTIN", "Justin Fornstrom", "Pine Bluffs Mayor", "Town of Pine Bluffs", 2025, 2027, 2024,
         "Official 2024 general, 497. Official 2026 general also lists a Pine Bluffs mayoral contest; term encoded as two years (inferred).")
    terms[-1]["confidence"] = "medium"
    muni("WY-LEITZA-ALLIE", "Allie Leitza", "Pine Bluffs Town Council", "Town of Pine Bluffs", 2025, 2029, 2024,
         "Official 2024 general Vote-For-2, 482.")
    muni("WY-KESTNER-JANNA", "Janna Kestner", "Pine Bluffs Town Council", "Town of Pine Bluffs", 2025, 2029, 2024,
         "Official 2024 general Vote-For-2, 449.")
    muni("WY-MICHAUD-DENNIS", "Dennis Michaud", "Pine Bluffs Mayor", "Town of Pine Bluffs", 2027, 2029, 2026,
         "Official 2026 general, 263. Succeeds Justin Fornstrom.")
    terms[-1]["confidence"] = "medium"
    muni("WY-CURRIE-AMY", "Amy Currie", "Pine Bluffs Town Council", "Town of Pine Bluffs", 2027, 2031, 2026,
         "Official 2026 general Vote-For-2, 380.")
    muni("WY-CROUSE-DAVID", "David Crouse", "Pine Bluffs Town Council", "Town of Pine Bluffs", 2027, 2031, 2026,
         "Official 2026 general Vote-For-2, 376.")

    # LCCC — official November VF3 (midterm) and VF4 (presidential)
    sch("WY-LYTTLE-BRENDA", "Brenda Lyttle", "Laramie County Community College Board of Trustees", "LCCC", 2015, 2019, 2014,
        "Official 2014 general Vote-For-3, 16,540.")
    sch("WY-MERRELL-CAROL", "Carol A. Merrell", "Laramie County Community College Board of Trustees", "LCCC", 2015, 2019, 2014,
        "Official 2014 general Vote-For-3, 16,402.")
    sch("WY-BARKER-BRADLEY", "Bradley S. Barker", "Laramie County Community College Board of Trustees", "LCCC", 2015, 2019, 2014,
        "Official 2014 general Vote-For-3, 14,779.")
    sch("WY-ERICKSON-DON", "Don Erickson", "Laramie County Community College Board of Trustees", "LCCC", 2017, 2021, 2016,
        "Official 2016 general Vote-For-4, 13,874.")
    sch("WY-SOTO-WENDY", "Wendy Soto", "Laramie County Community College Board of Trustees", "LCCC", 2017, 2021, 2016,
        "Official 2016 general Vote-For-4, 12,877.")
    sch("WY-KETCHAM-JESS-E", "Jess E. Ketcham", "Laramie County Community College Board of Trustees", "LCCC", 2017, 2021, 2016,
        "Official 2016 general Vote-For-4, 12,041.")
    sch("WY-SALAZAR-BOB", "Bob Salazar", "Laramie County Community College Board of Trustees", "LCCC", 2017, 2021, 2016,
        "Official 2016 general Vote-For-4, 10,824.")
    sch("WY-LYTTLE-BRENDA", "Brenda Lyttle", "Laramie County Community College Board of Trustees", "LCCC", 2019, 2023, 2018,
        "Official 2018 general Vote-For-3, 15,005.")
    sch("WY-MERRELL-CAROL", "Carol Merrell", "Laramie County Community College Board of Trustees", "LCCC", 2019, 2023, 2018,
        "Official 2018 general Vote-For-3, 14,017.")
    sch("WY-THOMPSON-JANINE", "Janine Thompson", "Laramie County Community College Board of Trustees", "LCCC", 2019, 2023, 2018,
        "Official 2018 general Vote-For-3, 13,466.")
    sch("WY-SOTO-WENDY", "Wendy J. Soto", "Laramie County Community College Board of Trustees", "LCCC", 2021, 2025, 2020,
        "Official 2020 general Vote-For-4, 22,523.")
    sch("WY-KETCHAM-JESS-E", "Jess E. Ketcham", "Laramie County Community College Board of Trustees", "LCCC", 2021, 2025, 2020,
        "Official 2020 general Vote-For-4, 21,960.")
    sch("WY-SALAZAR-BOB", "Bob Salazar", "Laramie County Community College Board of Trustees", "LCCC", 2021, 2025, 2020,
        "Official 2020 general Vote-For-4, 19,990.")
    sch("WY-ERICKSON-DON", "Don Erickson", "Laramie County Community College Board of Trustees", "LCCC", 2021, 2025, 2020,
        "Official 2020 general Vote-For-4, 19,693.")
    sch("WY-EMMONS-KATHY", "Kathy Emmons", "Laramie County Community College Board of Trustees", "LCCC", 2023, 2027, 2022,
        "Official 2022 general Vote-For-3, 13,103.")
    sch("WY-THOMPSON-JANINE", "Janine Thompson", "Laramie County Community College Board of Trustees", "LCCC", 2023, 2027, 2022,
        "Official 2022 general Vote-For-3, 11,558.")
    sch("WY-MERRELL-CAROL", "Carol Merrell", "Laramie County Community College Board of Trustees", "LCCC", 2023, 2027, 2022,
        "Official 2022 general Vote-For-3, 10,508.")
    sch("WY-KETCHAM-JESS-E", "Jess E. Ketcham", "Laramie County Community College Board of Trustees", "LCCC", 2025, 2029, 2024,
        "Official 2024 general Vote-For-4, 24,430. Also the official 2026 county commissioner-elect (takes office January 2027).")
    sch("WY-SOTO-WENDY", "Wendy J. Soto", "Laramie County Community College Board of Trustees", "LCCC", 2025, 2029, 2024,
        "Official 2024 general Vote-For-4, 23,022.")
    sch("WY-ERICKSON-DON", "Don Erickson", "Laramie County Community College Board of Trustees", "LCCC", 2025, 2029, 2024,
        "Official 2024 general Vote-For-4, 22,027.")
    sch("WY-SALAZAR-BOB", "Bob Salazar", "Laramie County Community College Board of Trustees", "LCCC", 2025, 2029, 2024,
        "Official 2024 general Vote-For-4, 21,192.")
    sch("WY-EMMONS-KATHY", "Kathy Emmons", "Laramie County Community College Board of Trustees", "LCCC", 2027, 2031, 2026,
        "Official 2026 general Vote-For-3, 15,903.")
    sch("WY-KELLY-JOE", "Joe Kelly", "Laramie County Community College Board of Trustees", "LCCC", 2027, 2031, 2026,
        "Official 2026 general Vote-For-3, 12,300.")
    sch("WY-GUILLE-KENNETH", "Kenneth Guille", "Laramie County Community College Board of Trustees", "LCCC", 2027, 2031, 2026,
        "Official 2026 general Vote-For-3, 11,044. Former official Laramie County Assessor.")

    # LCSD #1
    r2014 = [{"label": SD1_2014R[1], "url": SD1_2014R[0]}]
    r2018 = [{"label": SD1_2018R[1], "url": SD1_2018R[0]}]
    s2026 = [{"label": SD1_2026[1], "url": SD1_2026[0]}]
    s2_2026 = [{"label": SD2_2026[1], "url": SD2_2026[0]}]

    sch("WY-HERMAN-MARGUERITE", "Marguerite Herman", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2015, 2019, 2014,
        "Official 2014 general LCSD #1 recount Vote-For-4, 9,665.", sources=r2014)
    sch("WY-SHANOR-SANDY", "Sandy Shanor", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2015, 2019, 2014,
        "Official 2014 general LCSD #1 recount Vote-For-4, 8,799.", sources=r2014)
    sch("WY-KLAASSEN-MARK", "Mark Klaassen", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2015, 2019, 2014,
        "Official 2014 general LCSD #1 recount Vote-For-4, 8,385.", sources=r2014)
    sch("WY-LANDEN-JIM", "Jim Landen", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2015, 2019, 2014,
        "Official 2014 general LCSD #1 recount Vote-For-4, 8,009 (Lee Beidleman 8,004).", sources=r2014)
    sch("WY-BOLIN-TIM", "Tim Bolin", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2017, 2021, 2016,
        "Official 2016 general Vote-For-3, 11,933.")
    sch("WY-STOREY-HUYLAR-LYNN", "Lynn Storey-Huylar", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2017, 2021, 2016,
        "Official 2016 general Vote-For-3, 11,748. Official layout truncates the last letter of STOREY-HUYLAR; the official 2012 ballot and later summaries use Storey-Huylar.")
    sch("WY-BREEN-NATE", "Nate Breen", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2017, 2021, 2016,
        "Official 2016 general Vote-For-3, 11,159.")
    sch("WY-WIEDERSPAHN-RICH", "Rich Wiederspahn", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2019, 2023, 2018,
        "Official 2018 general LCSD #1 recount Vote-For-4, 11,253.", sources=r2018)
    sch("WY-KLAASSEN-CHRISTY", "Christy Klaassen", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2019, 2023, 2018,
        "Official 2018 general LCSD #1 recount Vote-For-4, 10,046.", sources=r2018)
    sch("WY-HERMAN-MARGUERITE", "Marguerite Herman", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2019, 2023, 2018,
        "Official 2018 general LCSD #1 recount Vote-For-4, 9,816.", sources=r2018)
    sch("WY-RINNE-ROSE-ANN", "Rose Ann Rinne", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2019, 2023, 2018,
        "Official 2018 general LCSD #1 recount Vote-For-4, 9,019.", sources=r2018)
    sch("WY-BOLIN-TIM", "Tim Bolin", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2021, 2025, 2020,
        "Official 2020 general Vote-For-3, 15,580.")
    sch("WY-ASHBY-BRITTANY", "Brittany Ashby", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2021, 2025, 2020,
        "Official 2020 general Vote-For-3, 15,015.")
    sch("WY-SMITH-ALICIA", "Alicia Smith", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2021, 2025, 2020,
        "Official 2020 general Vote-For-3, 13,837.")
    sch("WY-HINKLE-RENE", "Rene R. Hinkle", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2023, 2027, 2022,
        "Official 2022 general, 8,586.")
    sch("WY-EDGERTON-SUSAN", "Susan Edgerton", "LCSD #1 Board Trustee Area 1", "LCSD #1", 2023, 2027, 2022,
        "Official 2022 general, 2,358.")
    sch("WY-HUMPHREY-BROOKE", "Brooke Humphrey", "LCSD #1 Board Trustee Area 2", "LCSD #1", 2023, 2027, 2022,
        "Official 2022 general, 3,559.")
    sch("WY-KLAASSEN-CHRISTY", "Christy Klaassen", "LCSD #1 Board Trustee Area 3", "LCSD #1", 2023, 2027, 2022,
        "Official 2022 general, 3,629.")
    sch("WY-COOK-BARBARA", "Barbara Cook", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2025, 2029, 2024,
        "Official 2024 general Vote-For-3, 16,770.")
    sch("WY-ASHBY-BRITTANY", "Brittany Ashby", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2025, 2029, 2024,
        "Official 2024 general Vote-For-3, 15,690.")
    sch("WY-SMITH-ALICIA", "Alicia Smith", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2025, 2029, 2024,
        "Official 2024 general Vote-For-3, 15,357.")
    sch("WY-HINKLE-RENE", "Rene R. Hinkle", "LCSD #1 Board Trustee At-Large", "LCSD #1", 2027, 2031, 2026,
        "Official 2026 general LCSD #1 summary, 14,804.", sources=s2026)
    sch("WY-BURDEN-MARILYN", "Marilyn Burden", "LCSD #1 Board Trustee Area 1", "LCSD #1", 2027, 2031, 2026,
        "Official 2026 general LCSD #1 summary, 5,156.", sources=s2026)
    sch("WY-HUMPHREY-BROOKE", "Brooke Humphrey", "LCSD #1 Board Trustee Area 2", "LCSD #1", 2027, 2031, 2026,
        "Official 2026 general LCSD #1 summary, 3,035.", sources=s2026)
    sch("WY-BAILEY-HENRY-HANK", "Henry \"Hank\" Bailey", "LCSD #1 Board Trustee Area 3", "LCSD #1", 2027, 2031, 2026,
        "Official 2026 general LCSD #1 summary, 4,060. Ballot HENRY \"HANK\" BAILEY.", sources=s2026)

    # LCSD #2
    sch("WY-KIRKBRIDE-JEFF", "Jeff Kirkbride", "LCSD #2 Board Trustee At-Large", "LCSD #2", 2015, 2019, 2014,
        "Official 2014 general Vote-For-3, 1,337.")
    sch("WY-FORNSTROM-RUSSELL", "Russell Fornstrom", "LCSD #2 Board Trustee At-Large", "LCSD #2", 2015, 2019, 2014,
        "Official 2014 general Vote-For-3, 1,173.")
    sch("WY-LOVE-TAFT", "Taft C. Love", "LCSD #2 Board Trustee At-Large", "LCSD #2", 2015, 2019, 2014,
        "Official 2014 general Vote-For-3, 988. Same person later elected to Senate District 6.")
    sch("WY-MORGAN-STEWART", "Stewart Morgan", "LCSD #2 Board Trustee Area D", "LCSD #2", 2015, 2019, 2014,
        "Official 2014 general, 1,364.")
    sch("WY-DAVISON-ESTHER", "Esther Davison", "LCSD #2 Board Trustee Area C", "LCSD #2", 2017, 2021, 2016,
        "Official 2016 general, 1,260.")
    sch("WY-MAY-LEE", "Lee May", "LCSD #2 Board Trustee Area D", "LCSD #2", 2017, 2021, 2016,
        "Official 2016 general, 1,112.")
    sch("WY-FORNSTROM-TODD", "Todd Fornstrom", "LCSD #2 Board Trustee Area E", "LCSD #2", 2017, 2021, 2016,
        "Official 2016 general Vote-For-2, 1,764.")
    sch("WY-RANDALL-JULIANNE", "Julianne Randall", "LCSD #2 Board Trustee Area E", "LCSD #2", 2017, 2021, 2016,
        "Official 2016 general Vote-For-2, 1,520.")
    sch("WY-OLSON-MIKE", "Mike Olson", "LCSD #2 Board Trustee Area F", "LCSD #2", 2017, 2021, 2016,
        "Official 2016 general, 1,122.")
    sch("WY-KIRKBRIDE-JEFF", "Jeff Kirkbride", "LCSD #2 Board Trustee At-Large", "LCSD #2", 2019, 2023, 2018,
        "Official 2018 general Vote-For-3, 1,580.")
    sch("WY-FORNSTROM-RUSSELL", "Russell Fornstrom", "LCSD #2 Board Trustee At-Large", "LCSD #2", 2019, 2023, 2018,
        "Official 2018 general Vote-For-3, 1,366.")
    sch("WY-LOVE-TAFT", "Taft C. Love", "LCSD #2 Board Trustee At-Large", "LCSD #2", 2019, 2023, 2018,
        "Official 2018 general Vote-For-3, 1,031.")
    sch("WY-WILSON-BILLIE", "Billie J. Wilson", "LCSD #2 Board Trustee Area D", "LCSD #2", 2019, 2023, 2018,
        "Official 2018 general, 1,545.")
    sch("WY-ROMSA-HEIDI", "Heidi Romsa", "LCSD #2 Board Trustee Area C", "LCSD #2", 2021, 2025, 2020,
        "Official 2020 general, 1,434.")
    sch("WY-KEITER-DAVE", "Dave Keiter", "LCSD #2 Board Trustee Area D", "LCSD #2", 2021, 2025, 2020,
        "Official 2020 general, 1,520.")
    sch("WY-HAAS-MATT", "Matt Haas", "LCSD #2 Board Trustee Area E", "LCSD #2", 2021, 2025, 2020,
        "Official 2020 general Vote-For-2, 2,192.")
    sch("WY-RANDALL-JULIANNE", "Julianne Randall", "LCSD #2 Board Trustee Area E", "LCSD #2", 2021, 2025, 2020,
        "Official 2020 general Vote-For-2, 2,064.")
    sch("WY-OLSON-MIKE", "Mike Olson", "LCSD #2 Board Trustee Area F", "LCSD #2", 2021, 2025, 2020,
        "Official 2020 general, 1,389.")
    sch("WY-NUSBAUM-CODY", "Cody Nusbaum", "LCSD #2 Board Trustee At-Large", "LCSD #2", 2023, 2027, 2022,
        "Official 2022 general Vote-For-3, 1,290.")
    sch("WY-LERWICK-MICHAEL", "Michael Lerwick", "LCSD #2 Board Trustee At-Large", "LCSD #2", 2023, 2027, 2022,
        "Official 2022 general Vote-For-3, 1,185.")
    sch("WY-ROEDER-KENDRA", "Kendra Roeder", "LCSD #2 Board Trustee At-Large", "LCSD #2", 2023, 2027, 2022,
        "Official 2022 general Vote-For-3, 1,102.")
    sch("WY-WILSON-BILLIE", "Billie Wilson", "LCSD #2 Board Trustee Area D", "LCSD #2", 2023, 2027, 2022,
        "Official 2022 general, 1,824.")
    sch("WY-ROMSA-HEIDI", "Heidi Romsa", "LCSD #2 Board Trustee Area C", "LCSD #2", 2025, 2029, 2024,
        "Official 2024 general, 2,782.")
    sch("WY-WILES-JERRID", "Jerrid G. Wiles", "LCSD #2 Board Trustee Area D", "LCSD #2", 2025, 2027, 2024,
        "Official 2024 general, 2,562, not labeled unexpired. Official 2022 Area D winner Billie Wilson would ordinarily have sat through January 2027; official 2026 Area D winner is again Billie Wilson. Encoded as a two-year 2024 term; mid-term circumstances are not stated in the official generals.")
    terms[-1]["confidence"] = "medium"
    sch("WY-HAAS-MATT", "Matt Haas", "LCSD #2 Board Trustee Area E", "LCSD #2", 2025, 2029, 2024,
        "Official 2024 general Vote-For-2, 2,469.")
    sch("WY-RANDALL-JULIANNE", "Julianne Randall", "LCSD #2 Board Trustee Area E", "LCSD #2", 2025, 2029, 2024,
        "Official 2024 general Vote-For-2, 2,353.")
    sch("WY-OLSON-MIKE", "Mike Olson", "LCSD #2 Board Trustee Area F", "LCSD #2", 2025, 2029, 2024,
        "Official 2024 general, 1,355.")
    sch("WY-LERWICK-MICHAEL", "Michael Lerwick", "LCSD #2 Board Trustee At-Large", "LCSD #2", 2027, 2031, 2026,
        "Official 2026 general LCSD #2 summary Vote-For-3, 1,346.", sources=s2_2026)
    sch("WY-ROEDER-KENDRA", "Kendra Roeder", "LCSD #2 Board Trustee At-Large", "LCSD #2", 2027, 2031, 2026,
        "Official 2026 general LCSD #2 summary Vote-For-3, 1,178.", sources=s2_2026)
    sch("WY-JESSEN-ASHLEY", "Ashley Jessen", "LCSD #2 Board Trustee At-Large", "LCSD #2", 2027, 2031, 2026,
        "Official 2026 general LCSD #2 summary Vote-For-3, 1,007.", sources=s2_2026)
    sch("WY-WILSON-BILLIE", "Billie Wilson", "LCSD #2 Board Trustee Area D", "LCSD #2", 2027, 2031, 2026,
        "Official 2026 general LCSD #2 summary, 1,884.", sources=s2_2026)
    sch("WY-GROENEWEG-KELLY", "Kelly Groeneweg", "LCSD #2 Board Trustee Area F", "LCSD #2", 2027, 2031, 2026,
        "Official 2026 general LCSD #2 summary, 843.", sources=s2_2026)

    # Conservation
    spec("WY-KIRKBRIDE-LINDI", "Lindi Kirkbride", "Laramie County Conservation District Supervisor", "Laramie County Conservation District", 2015, 2019, 2014,
         "Official 2014 general Vote-For-2, 16,972.")
    spec("WY-BERRY-JAY", "Jay Berry", "Laramie County Conservation District Supervisor", "Laramie County Conservation District", 2015, 2019, 2014,
         "Official 2014 general Vote-For-2, 16,750.")
    spec("WY-HEMMER-DENNIS", "Dennis Hemmer", "Laramie County Conservation District Supervisor At-Large", "Laramie County Conservation District", 2017, 2021, 2016,
         "Official 2016 general, 29,720.")
    spec("WY-FARRELL-TOM", "Tom Farrell", "Laramie County Conservation District Supervisor Urban", "Laramie County Conservation District", 2017, 2021, 2016,
         "Official 2016 general, 29,973.")
    spec("WY-WELLS-KEVIN", "Kevin M. Wells", "Laramie County Conservation District Supervisor Rural", "Laramie County Conservation District", 2017, 2021, 2016,
         "Official 2016 general, 29,374.")
    spec("WY-EPLER-CASEY", "Casey F. Epler", "Laramie County Conservation District Supervisor At-Large", "Laramie County Conservation District", 2021, 2025, 2020,
         "Official 2020 general, 14,279.")
    spec("WY-FARRELL-TOM", "Tom Farrell", "Laramie County Conservation District Supervisor Urban", "Laramie County Conservation District", 2021, 2025, 2020,
         "Official 2020 general, 19,317.")
    spec("WY-WELLS-KEVIN", "Kevin Wells", "Laramie County Conservation District Supervisor Rural", "Laramie County Conservation District", 2021, 2025, 2020,
         "Official 2020 general, 34,786.")
    spec("WY-BERRY-JAY", "Jay Berry", "Laramie County Conservation District Supervisor", "Laramie County Conservation District", 2023, 2027, 2022,
         "Official 2022 general Vote-For-2, 20,010.")
    spec("WY-SANCHEZ-ANN", "Ann Sanchez", "Laramie County Conservation District Supervisor", "Laramie County Conservation District", 2023, 2027, 2022,
         "Official 2022 general Vote-For-2, 18,594.")
    spec("WY-EPLER-CASEY", "Casey F. Epler", "Laramie County Conservation District Supervisor At-Large", "Laramie County Conservation District", 2025, 2029, 2024,
         "Official 2024 general, 35,569.")
    spec("WY-CHEREK-SCOTT", "Scott J. Cherek", "Laramie County Conservation District Supervisor Urban", "Laramie County Conservation District", 2025, 2029, 2024,
         "Official 2024 general, 17,984.")
    spec("WY-WELLS-KEVIN", "Kevin Wells", "Laramie County Conservation District Supervisor Rural", "Laramie County Conservation District", 2025, 2029, 2024,
         "Official 2024 general, 34,425.")
    spec("WY-RUNDELL-FORD", "Ford Rundell", "Laramie County Conservation District Rural Board Member (unexpired)", "Laramie County Conservation District", 2027, 2029, 2026,
         "Official 2026 general unexpired rural seat, 24,331. Term end encoded as January 2029 (remainder inferred from the rural cycle); the official summary does not state the end date.")
    terms[-1]["confidence"] = "medium"
    spec("WY-HARDING-MELISSA", "Melissa Harding", "Laramie County Conservation District Supervisor Rural", "Laramie County Conservation District", 2027, 2031, 2026,
         "Official 2026 general Vote-For-2, 11,593.")
    spec("WY-CROWDER-JASON", "Jason Crowder", "Laramie County Conservation District Supervisor Rural", "Laramie County Conservation District", 2027, 2031, 2026,
         "Official 2026 general Vote-For-2, 9,513.")

    spec("WY-ASH-TIM", "Tim Ash", "Chugwater Fire District Director", "Chugwater Fire District", 2027, 2031, 2026,
         "Official 2026 general, 29 (Laramie County portion of the district).")
    return terms

def _holder(people, pid, *, sources, term_end="", party="", notes="", succeeding=None, extra=None, confidence="high"):
    rec = people.get(pid) or {}
    h = {
        "name": rec.get("display_name") or pid,
        "person_id": pid,
        "party": party,
        "sources": sources,
        "confidence": confidence,
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
    rec = people.get(pid) or {}
    return {
        "name": rec.get("display_name") or pid,
        "person_id": pid,
        "sources": sources,
        "takes_office": takes_office,
        "term_end": term_end,
    }


def build_laramie():
    people: dict = {}
    P = H.person_factory(people)
    register_people(P)
    _register_local_people(P)

    terms = county_and_legislature_terms() + judicial_terms() + local_terms()

    weston = json.loads((H.HISTORY / "weston" / "terms.json").read_text())
    copied = 0
    for t in weston["terms"]:
        og = t.get("office_group")
        office = (t.get("office") or "")
        if og in {"federal", "statewide"}:
            terms.append(deepcopy(t)); copied += 1
        elif og == "judicial" and any(x in office for x in ("Supreme Court", "Chancery")):
            rec = deepcopy(t)
            if rec.get("election_year") in FS:
                rec["sources"] = list(rec.get("sources") or []) + [fs(rec["election_year"])]
            terms.append(rec); copied += 1
        # Do not copy 4th, 5th, or 6th Judicial District judges. Laramie is in the 1st JD.

    H.attach_people_from_terms(terms, people)

    expected = {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [
            ("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
            ("State Treasurer", 1), ("Superintendent of Public Instruction", 1),
        ],
        "state-senate": [
            ("Senate District 4 (S04)", 1),
            ("Senate District 5 (S05)", 1),
            ("Senate District 6 (S06)", 1),
            ("Senate District 7 (S07)", 1),
            ("Senate District 8 (S08)", 1),
            ("Senate District 31 (S31)", 1),
        ],
        "state-house": [
            ("House District 4 (H04)", 1),
            ("House District 7 (H07)", 1),
            ("House District 8 (H08)", 1),
            ("House District 9 (H09)", 1),
            ("House District 10 (H10)", 1),
            ("House District 11 (H11)", 1),
            ("House District 12 (H12)", 1),
            ("House District 41 (H41)", 1),
            ("House District 42 (H42)", 1),
            ("House District 43 (H43)", 1),
            ("House District 44 (H44)", 1),
            ("House District 61 (H61)", 1),
        ],
        "county": [
            ("County Commissioner", 5), ("County Clerk", 1), ("County Treasurer", 1),
            ("County Assessor", 1), ("County Sheriff", 1), ("District Attorney", 1),
            ("Clerk of District Court", 1), ("County Coroner", 1),
        ],
        "municipal": [
            ("Cheyenne Mayor", 1),
            ("Cheyenne City Council Ward 1", 3),
            ("Cheyenne City Council Ward 2", 3),
            ("Cheyenne City Council Ward 3", 3),
            ("Pine Bluffs Mayor", 1),
            ("Pine Bluffs Town Council", 4),
        ],
    }

    judicial_note = (
        "Supreme Court justices and the Chancery Court judge are the people in office this January, from official "
        "Wyoming Judicial Branch dates and official retention results (shared with other counties). Local rows are "
        "1st Judicial District judges who appeared by last name on a Laramie County official retention ballot; the "
        "official summaries do not print a given name, and no given name is invented. The official 2018 general lists "
        "a Circuit Court Judge retention (YES 18,725 / NO 11,081) with no judge’s name; that contest is not attached "
        "to a person. Official named 1st JD retentions are keyed beginning with the 2020 general; earlier January "
        "1st JD seats are marked Not yet collected rather than invented. Laramie is in the 1st Judicial District; "
        "4th, 5th, and 6th Judicial District judges are not copied here."
    )
    special_note = (
        "Municipal names are keyed from official Laramie November generals. Cheyenne council is filled from official "
        "midterm Vote-For-1 and presidential Vote-For-2 results (three members per ward on the current board). "
        "Pine Bluffs appears on the official 2024 and 2026 November city/county summaries; official 2024 and 2026 "
        "both include a mayoral contest, so those mayoral terms are encoded as two years (inferred). Burns and Albin "
        "do not appear on the official November city/county summaries archived for 2010–2026. The official Laramie "
        "County clerk election-results page, retrieved 2026-11-24, has no 2025 municipal canvass posted. Official "
        "burnswy.com could not be retrieved (TLS failure); a March 2025 Wayback capture is only the Apache default "
        "page. No official Town of Albin site was found. Those two towns remain Not yet collected rather than invented. "
        "School and conservation seats are keyed from official generals (LCSD #1 "
        "2014 and 2018 at-large from the official recount summaries; official 2026 school results from the official "
        "LCSD #1 and #2 PDFs). The official 2024 LCSD #2 Area D winner is Jerrid G. Wiles and the official 2026 "
        "Area D winner is Billie Wilson; the mid-term circumstances are not stated in the official generals. "
        "Jess E. Ketcham is an official 2024 LCCC trustee and the official 2026 commissioner-elect."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. Official Laramie primary PDFs are "
        "archived under /workspace/wyoleg/local-results/laramie/<year>/. The current (November 2026) precinct roster "
        "is in data/county_officials/laramie.json, from the official 2026 primary (named winners only; write-in-only "
        "precinct contests are not listed)."
    )

    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Laramie", county_number=2, slug="laramie", terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Laramie", slug="laramie")
    print(f"wrote {terms_path}")
    print(f"terms {len(terms)} (including {copied} shared federal/statewide/SC-chancery terms)")
    print(f"people_additions +{n_people} offices_held +{n_off} thin_profiles +{n_prof}")
    H.print_coverage(coverage_all)
    return people, terms, coverage_all


def update_laramie_json(people: dict):
    path = ROOT / "data" / "county_officials" / "laramie.json"
    data = json.loads(path.read_text())
    data["as_of"] = RETRIEVED
    data["term_switch_date"] = "2027-01-04"
    g2026 = [pg(2026)]
    g2024 = [pg(2024)]
    fs2026 = [fs(2026)]
    fs2024 = [fs(2024)]
    s2026 = [{"label": SD1_2026[1], "url": SD1_2026[0]}]
    s2_2026 = [{"label": SD2_2026[1], "url": SD2_2026[0]}]

    def HLD(pid, **kw):
        return _holder(people, pid, **kw)

    # Rebuild legislative / county / added groups; keep precincts as-is.
    new_groups = []
    precincts = None
    for g in data["groups"]:
        if g.get("id") == "precincts":
            precincts = g

    # Senate
    new_groups.append({
        "id": "state-senate", "title": "State Senate",
        "offices": [
            {"office": "Senate District 4 (S04)", "layout": "office-and-name",
             "holders": [HLD("WY-NETHERCOTT-TARA", sources=fs2024, party="R", term_end="January 2029")]},
            {"office": "Senate District 5 (S05)", "layout": "office-and-name",
             "holders": [HLD("WY-HUTCHINGS-LYNN", sources=fs2026, party="R", term_end="January 2027",
                             succeeding=_succ(people, "WY-SCHOENFELD-LAUREN", sources=fs2026, term_end="January 2031"))]},
            {"office": "Senate District 6 (S06)", "layout": "office-and-name",
             "holders": [HLD("WY-LOVE-TAFT", sources=fs2026, party="R", term_end="January 2029",
                             confidence="medium",
                             notes="Official 2024 general winner was Darin Smith; official 2026 general names Taft Love (not labeled unexpired). Mid-term succession date is not stated in the official generals.")]},
            {"office": "Senate District 7 (S07)", "layout": "office-and-name",
             "holders": [HLD("WY-PAPPAS-STEPHAN", sources=fs2026, party="R", term_end="January 2027",
                             succeeding=_succ(people, "WY-RINNE-MARK", sources=fs2026, term_end="January 2031"))]},
            {"office": "Senate District 8 (S08)", "layout": "office-and-name",
             "holders": [HLD("WY-OLSEN-JARED", sources=fs2024, party="R", term_end="January 2029")]},
            {"office": "Senate District 31 (S31)", "layout": "office-and-name",
             "holders": [HLD("WY-BRENNAN-EVIE", sources=fs2026, party="R", term_end="January 2031",
                             notes="Official 2022 term ends January 2027; official 2026 general winner, continuing.")]},
        ],
    })
    # House
    house_now = [
        ("4 (H04)", "WY-HAROLDSON-JEREMY", fs2026, "R", "January 2029", None, "Official 2026 general winner. Official SOS district-wide totals are used for this multi-county seat."),
        ("7 (H07)", "WY-NICHOLAS-BOB", fs2026, "R", "January 2029", None, ""),
        ("8 (H08)", "WY-JOHNSON-STEVE", fs2026, "R", "January 2027", "WY-REINER-LUKE", ""),
        ("9 (H09)", "WY-BROWN-LANDON", fs2026, "R", "January 2027", "WY-WIGGAM-BOYD", ""),
        ("10 (H10)", "WY-EKLUND-JOHN", fs2026, "R", "January 2027", "WY-FORNSTROM-JUSTIN", ""),
        ("11 (H11)", "WY-WASSERBURGER-JACOB", fs2026, "R", "January 2027", "WY-TENNANT-BRITNEY", ""),
        ("12 (H12)", "WY-STYVAR-CLARENCE", fs2026, "R", "January 2029", None, ""),
        ("41 (H41)", "WY-BROWN-GARY", fs2026, "R", "January 2027", "WY-EDWARDS-ERIN", ""),
        ("42 (H42)", "WY-GERINGER-ROB", fs2026, "R", "January 2029", None, ""),
        ("43 (H43)", "WY-LUCAS-ANN", fs2026, "R", "January 2027", "WY-CROWDER-JESSICA", ""),
        ("44 (H44)", "WY-FILER-LEE", fs2026, "R", "January 2029", None, ""),
        ("61 (H61)", "WY-SINGH-DANIEL", fs2026, "R", "January 2027", "WY-SERVER-ANDREW", ""),
    ]
    house_offices = []
    for dist, pid, sources, party, tend, succpid, notes in house_now:
        kw = dict(sources=sources, party=party, term_end=tend)
        if notes:
            kw["notes"] = notes
        if succpid:
            kw["succeeding"] = _succ(people, succpid, sources=fs2026, term_end="January 2029")
            # Tennant is D
            if succpid == "WY-TENNANT-BRITNEY":
                kw["succeeding"]["party"] = "D"
        rec = {"office": f"House District {dist}", "layout": "office-and-name",
               "holders": [HLD(pid, **kw)]}
        if dist == "4 (H04)":
            rec["note"] = (
                "Official 2026 SOS statewide House summary totals: Jeremy Haroldson 2,533. "
                "Official Laramie County portion: 57. Also covers Platte County. "
                "Official SOS district-wide totals are used for this multi-county seat."
            )
        house_offices.append(rec)
    new_groups.append({"id": "state-house", "title": "State House", "offices": house_offices})

    # County
    comm_holders = [
        HLD("WY-MALM-GUNNAR", sources=g2026, party="R", term_end="January 2031",
            notes="Official 2022 term ends January 2027; official 2026 general Vote-For-3 winner, continuing."),
        HLD("WY-THOMPSON-TROY", sources=g2026, party="R", term_end="January 2031",
            notes="Official 2022 term ends January 2027; official 2026 general Vote-For-3 winner, continuing."),
        HLD("WY-HEATH-LINDA", sources=g2026, party="R", term_end="January 2027",
            succeeding=_succ(people, "WY-KETCHAM-JESS-E", sources=g2026, term_end="January 2031")),
        HLD("WY-HOLLINGSHEAD-DON", sources=g2024, party="R", term_end="January 2029"),
        HLD("WY-ZWONITZER-TY", sources=g2024, party="R", term_end="January 2029"),
    ]
    new_groups.append({
        "id": "county", "title": "County Offices",
        "offices": [
            {"office": "County Commissioners", "layout": "heading-then-names", "holders": comm_holders},
            {"office": "County Clerk", "layout": "office-and-name",
             "holders": [HLD("WY-LEE-DEBRA", sources=g2026, party="R", term_end="January 2027",
                             succeeding=_succ(people, "WY-TINNEY-MISTY", sources=g2026, term_end="January 2031"))]},
            {"office": "County Treasurer", "layout": "office-and-name",
             "holders": [HLD("WY-DEISCH-TAMMY", sources=g2026, party="R", term_end="January 2027",
                             succeeding=_succ(people, "WY-WOOD-TRISTA", sources=g2026, term_end="January 2031"))]},
            {"office": "County Assessor", "layout": "office-and-name",
             "holders": [HLD("WY-ERNST-TODD-A", sources=g2026, party="R", term_end="January 2031",
                             notes="Official 2024 general winner (mid-term relative to official 2022 winner Kenneth Guille) and official 2026 general winner. Mid-term succession date is not stated in the official generals.")]},
            {"office": "County Sheriff", "layout": "office-and-name",
             "holders": [HLD("WY-KOZAK-BRIAN", sources=g2026, party="R", term_end="January 2031",
                             notes="Official 2022 term ends January 2027; official 2026 general winner, continuing.")]},
            {"office": "District Attorney", "layout": "office-and-name",
             "holders": [HLD("WY-HACKL-SYLVIA", sources=g2026, party="R", term_end="January 2031",
                             extra={"ballot_name": "Sylvia Lee Hackl"},
                             notes="Official 2022 ballot Sylvia Miller Hackl; official 2026 ballot Sylvia Lee Hackl. Official 2022 term ends January 2027; official 2026 general winner, continuing.")]},
            {"office": "Clerk of District Court", "layout": "office-and-name",
             "holders": [HLD("WY-SANCHEZ-DIANE", sources=g2026, party="R", term_end="January 2031",
                             notes="Official 2022 term ends January 2027; official 2026 general winner, continuing.")]},
            {"office": "County Coroner", "layout": "office-and-name",
             "holders": [HLD("WY-REID-REBECCA", sources=g2026, party="R", term_end="January 2031",
                             notes="Official 2022 term ends January 2027; official 2026 general winner, continuing.")]},
        ],
    })

    # Municipal
    new_groups.append({
        "id": "municipal", "title": "Municipal Offices",
        "offices": [
            {"office": "Cheyenne Mayor", "layout": "office-and-name",
             "holders": [HLD("WY-COLLINS-PATRICK", sources=g2024, term_end="January 2029")]},
            {"office": "Cheyenne City Council Ward 1", "layout": "heading-then-names",
             "holders": [
                 HLD("WY-WHITE-JEFF", sources=g2024, term_end="January 2029"),
                 HLD("WY-LAYBOURN-PETE", sources=g2024, term_end="January 2029"),
                 HLD("WY-ROYBAL-SCOTT", sources=g2026, term_end="January 2027",
                     succeeding=_succ(people, "WY-KALLAS-MAREN", sources=g2026, term_end="January 2031")),
             ]},
            {"office": "Cheyenne City Council Ward 2", "layout": "heading-then-names",
             "holders": [
                 HLD("WY-EMMONS-KATHY", sources=g2024, term_end="January 2029"),
                 HLD("WY-SEGRAVE-TOM", sources=g2024, term_end="January 2029"),
                 HLD("WY-RINNE-MARK", sources=g2026, term_end="January 2027",
                     succeeding=_succ(people, "WY-ROSE-JANELLE", sources=g2026, term_end="January 2031")),
             ]},
            {"office": "Cheyenne City Council Ward 3", "layout": "heading-then-names",
             "holders": [
                 HLD("WY-ALDRICH-MICHELLE", sources=g2024, term_end="January 2029"),
                 HLD("WY-MOODY-MARK-A", sources=g2024, term_end="January 2029"),
                 HLD("WY-ESQUIBEL-KEN", sources=g2026, term_end="January 2031",
                     notes="Official 2022 term ends January 2027; official 2026 general winner, continuing."),
             ]},
            {"office": "Pine Bluffs Mayor", "layout": "office-and-name",
             "holders": [HLD("WY-FORNSTROM-JUSTIN", sources=g2026, term_end="January 2027", confidence="medium",
                             notes="Official 2024 and 2026 November summaries both include a Pine Bluffs mayoral contest; the 2024 term is encoded as two years (inferred).",
                             succeeding=_succ(people, "WY-MICHAUD-DENNIS", sources=g2026, term_end="January 2029"))]},
            {"office": "Pine Bluffs Town Council", "layout": "heading-then-names",
             "holders": [
                 HLD("WY-LEITZA-ALLIE", sources=g2024, term_end="January 2029"),
                 HLD("WY-KESTNER-JANNA", sources=g2024, term_end="January 2029"),
                 HLD("WY-CURRIE-AMY", sources=g2026, term_end="January 2031",
                     notes="Official 2026 general Vote-For-2 winner; takes office January 2027."),
                 HLD("WY-CROUSE-DAVID", sources=g2026, term_end="January 2031",
                     notes="Official 2026 general Vote-For-2 winner; takes office January 2027."),
             ]},
            {"office": "Town of Burns", "layout": "office-and-name",
             "holders": [{"name": "Not yet collected", "notes": "Burns does not appear on the official November 2010–2026 city/county summaries. The official Laramie County clerk election-results page, retrieved 2026-11-24, has no 2025 municipal canvass posted. Official burnswy.com could not be retrieved (TLS failure); a March 2025 Wayback capture is only the Apache default page. Left Not yet collected rather than invented."}]},
            {"office": "Town of Albin", "layout": "office-and-name",
             "holders": [{"name": "Not yet collected", "notes": "Albin does not appear on the official November 2010–2026 city/county summaries. The official Laramie County clerk election-results page, retrieved 2026-11-24, has no 2025 municipal canvass posted. No official Town of Albin site was found. Left Not yet collected rather than invented."}]},
        ],
    })

    # Schools
    new_groups.append({
        "id": "schools", "title": "School and College Boards",
        "offices": [
            {"office": "Laramie County Community College Board of Trustees", "layout": "heading-then-names",
             "holders": [
                 HLD("WY-KETCHAM-JESS-E", sources=g2024, term_end="January 2029",
                     notes="Official 2024 general Vote-For-4 winner. Also the official 2026 county commissioner-elect (takes office January 2027)."),
                 HLD("WY-SOTO-WENDY", sources=g2024, term_end="January 2029"),
                 HLD("WY-ERICKSON-DON", sources=g2024, term_end="January 2029"),
                 HLD("WY-SALAZAR-BOB", sources=g2024, term_end="January 2029"),
                 HLD("WY-EMMONS-KATHY", sources=g2026, term_end="January 2031",
                     notes="Official 2022 term ends January 2027; official 2026 general Vote-For-3 winner, continuing."),
                 HLD("WY-THOMPSON-JANINE", sources=g2026, term_end="January 2027",
                     succeeding=_succ(people, "WY-KELLY-JOE", sources=g2026, term_end="January 2031")),
                 HLD("WY-MERRELL-CAROL", sources=g2026, term_end="January 2027",
                     succeeding=_succ(people, "WY-GUILLE-KENNETH", sources=g2026, term_end="January 2031")),
             ]},
            {"office": "LCSD #1 Board Trustee At-Large", "layout": "heading-then-names",
             "holders": [
                 HLD("WY-COOK-BARBARA", sources=g2024, term_end="January 2029"),
                 HLD("WY-ASHBY-BRITTANY", sources=g2024, term_end="January 2029"),
                 HLD("WY-SMITH-ALICIA", sources=g2024, term_end="January 2029"),
                 HLD("WY-HINKLE-RENE", sources=s2026, term_end="January 2031",
                     notes="Official 2022 term ends January 2027; official 2026 general LCSD #1 winner, continuing."),
             ]},
            {"office": "LCSD #1 Board Trustee Area 1", "layout": "office-and-name",
             "holders": [HLD("WY-EDGERTON-SUSAN", sources=s2026, term_end="January 2027",
                             succeeding=_succ(people, "WY-BURDEN-MARILYN", sources=s2026, term_end="January 2031"))]},
            {"office": "LCSD #1 Board Trustee Area 2", "layout": "office-and-name",
             "holders": [HLD("WY-HUMPHREY-BROOKE", sources=s2026, term_end="January 2031",
                             notes="Official 2022 term ends January 2027; official 2026 general LCSD #1 winner, continuing.")]},
            {"office": "LCSD #1 Board Trustee Area 3", "layout": "office-and-name",
             "holders": [HLD("WY-KLAASSEN-CHRISTY", sources=s2026, term_end="January 2027",
                             succeeding=_succ(people, "WY-BAILEY-HENRY-HANK", sources=s2026, term_end="January 2031"))]},
            {"office": "LCSD #2 Board Trustee At-Large", "layout": "heading-then-names",
             "holders": [
                 HLD("WY-NUSBAUM-CODY", sources=s2_2026, term_end="January 2027",
                     succeeding=_succ(people, "WY-JESSEN-ASHLEY", sources=s2_2026, term_end="January 2031")),
                 HLD("WY-LERWICK-MICHAEL", sources=s2_2026, term_end="January 2031",
                     notes="Official 2022 term ends January 2027; official 2026 general LCSD #2 Vote-For-3 winner, continuing."),
                 HLD("WY-ROEDER-KENDRA", sources=s2_2026, term_end="January 2031",
                     notes="Official 2022 term ends January 2027; official 2026 general LCSD #2 Vote-For-3 winner, continuing."),
             ]},
            {"office": "LCSD #2 Board Trustee Area C", "layout": "office-and-name",
             "holders": [HLD("WY-ROMSA-HEIDI", sources=g2024, term_end="January 2029")]},
            {"office": "LCSD #2 Board Trustee Area D", "layout": "office-and-name",
             "holders": [HLD("WY-WILES-JERRID", sources=s2_2026, term_end="January 2027", confidence="medium",
                             notes="Official 2024 general Area D winner. Official 2026 general Area D winner is Billie Wilson. Mid-term circumstances are not stated in the official generals.",
                             succeeding=_succ(people, "WY-WILSON-BILLIE", sources=s2_2026, term_end="January 2031"))]},
            {"office": "LCSD #2 Board Trustee Area E", "layout": "heading-then-names",
             "holders": [
                 HLD("WY-HAAS-MATT", sources=g2024, term_end="January 2029"),
                 HLD("WY-RANDALL-JULIANNE", sources=g2024, term_end="January 2029"),
             ]},
            {"office": "LCSD #2 Board Trustee Area F", "layout": "office-and-name",
             "holders": [HLD("WY-OLSON-MIKE", sources=s2_2026, term_end="January 2027",
                             succeeding=_succ(people, "WY-GROENEWEG-KELLY", sources=s2_2026, term_end="January 2031"))]},
        ],
    })

    # Special
    new_groups.append({
        "id": "special-districts", "title": "Special Districts",
        "offices": [
            {"office": "Laramie County Conservation District Supervisor At-Large", "layout": "office-and-name",
             "holders": [HLD("WY-EPLER-CASEY", sources=g2024, term_end="January 2029")]},
            {"office": "Laramie County Conservation District Supervisor Urban", "layout": "office-and-name",
             "holders": [HLD("WY-CHEREK-SCOTT", sources=g2024, term_end="January 2029")]},
            {"office": "Laramie County Conservation District Supervisor Rural", "layout": "heading-then-names",
             "holders": [
                 HLD("WY-WELLS-KEVIN", sources=g2024, term_end="January 2029"),
                 HLD("WY-BERRY-JAY", sources=g2026, term_end="January 2027",
                     succeeding=_succ(people, "WY-HARDING-MELISSA", sources=g2026, term_end="January 2031")),
                 HLD("WY-SANCHEZ-ANN", sources=g2026, term_end="January 2027",
                     succeeding=_succ(people, "WY-CROWDER-JASON", sources=g2026, term_end="January 2031")),
                 HLD("WY-RUNDELL-FORD", sources=g2026, term_end="January 2029", confidence="medium",
                     notes="Official 2026 general unexpired rural winner; takes office January 2027. Term end January 2029 is inferred from the rural cycle."),
             ]},
            {"office": "Chugwater Fire District Director", "layout": "office-and-name",
             "holders": [HLD("WY-ASH-TIM", sources=g2026, term_end="January 2031",
                             notes="Official 2026 general, 29 (Laramie County portion). Takes office January 2027.")]},
        ],
    })

    # Judicial (current, pre-switch: 2022 district Campbell/Rogers through Jan 2029; circuit Chambers through Jan 2027 then re-retained; Williams through Jan 2029; Forwood/Cooley/Hibben take office Jan 2027)
    new_groups.append({
        "id": "judicial", "title": "Judicial Retention",
        "note": "1st Judicial District judges named on official Laramie retention ballots (official last name only). Supreme Court and Chancery Court are in the shared statewide file.",
        "offices": [
            {"office": "District Judge, 1st Judicial District (Campbell)", "layout": "office-and-name",
             "holders": [HLD("WY-CAMPBELL-JD1", sources=fs(2022) and [fs(2022)] or [], term_end="January 2029",
                             notes="Official 2022 general retention, last name only as printed on the official summary.")]},
            {"office": "District Judge, 1st Judicial District (Rogers)", "layout": "office-and-name",
             "holders": [HLD("WY-ROGERS-JD1", sources=[fs(2022)], term_end="January 2029",
                             notes="Official 2022 general retention, last name only as printed on the official summary.")]},
            {"office": "District Judge, 1st Judicial District (Cooley)", "layout": "office-and-name",
             "holders": [HLD("WY-COOLEY", sources=fs2026, term_end="January 2033",
                             notes="Official 2026 general retention, last name only. Takes office under the January 2027 term start used for retentions.")]},
            {"office": "District Judge, 1st Judicial District (Hibben)", "layout": "office-and-name",
             "holders": [HLD("WY-HIBBEN", sources=fs2026, term_end="January 2033",
                             notes="Official 2026 general retention, last name only.")]},
            {"office": "Circuit Judge, 1st Judicial District (Chambers)", "layout": "office-and-name",
             "holders": [HLD("WY-CHAMBERS-JD1", sources=g2026, term_end="January 2031",
                             notes="Official 2022 term ends January 2027; official 2026 general retention (last name only), continuing.")]},
            {"office": "Circuit Judge, 1st Judicial District (Williams)", "layout": "office-and-name",
             "holders": [HLD("WY-WILLIAMS-JD1", sources=[fs(2024)], term_end="January 2029",
                             notes="Official 2024 general retention, last name only.")]},
            {"office": "Circuit Judge, 1st Judicial District (Forwood)", "layout": "office-and-name",
             "holders": [HLD("WY-FORWOOD", sources=g2026, term_end="January 2031",
                             notes="Official 2026 general retention, last name only.")]},
        ],
    })

    if precincts is not None:
        new_groups.append(precincts)

    data["groups"] = new_groups
    data["sources"] = {
        "general_results": PG[2026][0],
        "primary_results": PP_2026[0],
        "general_fed_state": FS[2026][0],
        "lcsd1": SD1_2026[0],
        "lcsd2": SD2_2026[0],
        "clerk_archive": ARCHIVE,
        "checked": RETRIEVED,
        "local_archive": "/workspace/wyoleg/local-results/laramie/SOURCES.md",
    }
    apply_to_groups(data["groups"], 'laramie')
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("updated", path)
    return path
