#!/usr/bin/env python3
"""Seed Weston municipal, school, and judicial records into the standard site data (branch only).

Writes:
  data/county_officials/weston.json (new groups)
  data/county_officials/shared/judicial-statewide.json
  data/people/people_additions.csv
  data/people/offices_held_additions.csv
  data/people/candidacies_additions.csv
  tools/local-data/{2022,2024,2026}/municipal_*.csv
  tools/local-data/{2022,2024,2026}/school_*.csv
  tools/local-data/{2022,2024,2026}/judicial_retention_*.csv
  candidate / judge Profile HTML for new (and a few enriched) people

Does not merge, push, or publish.
"""
from __future__ import annotations

import csv
import json
from copy import deepcopy
from pathlib import Path

from sources import (
    SRC_2022, SRC_2024, SRC_2026, SRC_NEWC, SRC_UPTON, SRC_SD1,
    SRC_SD7_UPTON, SRC_SD7_DIST, SRC_COURTS_SC, SRC_COURTS_CH,
    SRC_COURTS_D6, SRC_COURTS_C6, RETRIEVED,
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "county_officials"
PEOPLE = ROOT / "data" / "people"
LOCAL = ROOT / "tools" / "local-data"

# Existing IDs (name-index) reused. Minted IDs are marked minted=True below.
# Display names prefer the official website / board roster form.
# ballot_name is the name as printed on the official results.

PERSONS = [
    # reused
    dict(person_id="WY-BUTTS-JOHN", display_name="John G. Butts", first="John", middle="G.", last="Butts", aliases="John Butts", minted=False, slug="john-g-butts"),
    dict(person_id="WY-VOSS-THOMAS", display_name="Thomas Voss", first="Thomas", middle="", last="Voss", aliases="Tom Voss; THOMAS A. VOSS", minted=False, slug="thomas-voss"),
    dict(person_id="WY-JENKINS-JASON", display_name="Jason Jenkins", first="Jason", middle="", last="Jenkins", aliases="", minted=False, slug="jason-jenkins"),
    dict(person_id="WY-JOHNSON-SCOTT", display_name="Scott W. Johnson", first="Scott", middle="W.", last="Johnson", aliases="", minted=False, slug="scott-w-johnson"),
    dict(person_id="WY-RANKIN-CURTIS", display_name="Curtis Rankin", first="Curtis", middle="", last="Rankin", aliases="", minted=False, slug="curtis-rankin"),
    dict(person_id="WY-JASINSKI-STANLEY", display_name="Stanley Jasinski", first="Stanley", middle="", last="Jasinski", aliases="", minted=False, slug="stanley-jasinski"),
    dict(person_id="WY-LAMBERT-MARCIA", display_name="Marcia Lambert", first="Marcia", middle="", last="Lambert", aliases="", minted=False, slug="marcia-lambert"),
    dict(person_id="WY-SEARS-GILLIAN", display_name="Gillian Sears", first="Gillian", middle="", last="Sears", aliases="", minted=False, slug="gillian-sears"),
    # minted municipal / school / judicial
    dict(person_id="WY-OWENS-TYREL", display_name="Tyrel Owens", first="Tyrel", middle="", last="Owens", aliases="TYREL OWENS", minted=True, slug="tyrel-owens"),
    dict(person_id="WY-STEVESON-DON", display_name="Don Steveson", first="Don", middle="", last="Steveson", aliases="Donnie Steveson; DONNIE STEVESON", minted=True, slug="don-steveson"),
    dict(person_id="WY-MCCOLLEY-ANN", display_name="Ann McColley", first="Ann", middle="", last="McColley", aliases="ANN MCCOLLEY", minted=True, slug="ann-mccolley"),
    dict(person_id="WY-DOWNS-DAREN", display_name="Daren Downs", first="Daren", middle="L.", last="Downs", aliases="Darren Downs; DAREN L. DOWNS", minted=True, slug="daren-downs"),
    dict(person_id="WY-KENNEY-CHRIS", display_name="Chris Kenney", first="Chris", middle="", last="Kenney", aliases="CHRIS KENNEY", minted=True, slug="chris-kenney"),
    dict(person_id="WY-GUALTIERI-PAM", display_name="Pam Gualtieri", first="Pam", middle="", last="Gualtieri", aliases="PAM GUALTIERI", minted=True, slug="pam-gualtieri"),
    dict(person_id="WY-VOELKER-WYATT", display_name="Wyatt Voelker", first="Wyatt", middle="", last="Voelker", aliases="WYATT VOELKER", minted=True, slug="wyatt-voelker"),
    dict(person_id="WY-TRANDAHL-NICK", display_name="Nick Trandahl", first="Nick", middle="", last="Trandahl", aliases="Nicholas Trandahl; NICK TRANDAHL", minted=True, slug="nick-trandahl"),
    dict(person_id="WY-KENNEDY-TY", display_name="Ty Kennedy", first="Ty", middle="", last="Kennedy", aliases="TY KENNEDY", minted=True, slug="ty-kennedy"),
    dict(person_id="WY-NORMAN-JUSTIN", display_name="Justin Norman", first="Justin", middle="", last="Norman", aliases="JUSTIN NORMAN", minted=True, slug="justin-norman"),
    dict(person_id="WY-WATT-JOE", display_name="Joe Watt", first="Joe", middle="", last="Watt", aliases="JOE WATT", minted=True, slug="joe-watt"),
    dict(person_id="WY-MCMILLAN-TIFFANY", display_name="Tiffany McMillan", first="Tiffany", middle="", last="McMillan", aliases="TIFFANY MCMILLAN", minted=True, slug="tiffany-mcmillan"),
    dict(person_id="WY-ROTHLEUTNER-RICK", display_name="Rick Rothleutner", first="Rick", middle="", last="Rothleutner", aliases="RICK ROTHLEUTNER", minted=True, slug="rick-rothleutner"),
    dict(person_id="WY-WOZNEY-KELLY", display_name="Kelly Wozney", first="Kelly", middle="", last="Wozney", aliases="KELLY WOZNEY", minted=True, slug="kelly-wozney"),
    dict(person_id="WY-FITZWATER-BILLY", display_name="Billy Fitzwater", first="Billy", middle="", last="Fitzwater", aliases="BILLY FITZWATER", minted=True, slug="billy-fitzwater"),
    dict(person_id="WY-PRELL-JOE", display_name="Joe Prell", first="Joe", middle="", last="Prell", aliases="Richard Joe Prell; RICHARD JOE PRELL; JOE PRELL", minted=True, slug="joe-prell"),
    dict(person_id="WY-MANN-TAVEGIA-DANA", display_name="Dana Mann-Tavegia", first="Dana", middle="", last="Mann-Tavegia", aliases="DANA MANN-TAVEGIA", minted=True, slug="dana-mann-tavegia"),
    dict(person_id="WY-BAU-PAUL", display_name="Paul Bau", first="Paul", middle="", last="Bau", aliases="PAUL BAU", minted=True, slug="paul-bau"),
    dict(person_id="WY-CRABTREE-SEAN", display_name="Sean Crabtree", first="Sean", middle="", last="Crabtree", aliases="SEAN CRABTREE", minted=True, slug="sean-crabtree"),
    dict(person_id="WY-GORDON-DANA", display_name="Dana Gordon", first="Dana", middle="", last="Gordon", aliases="DANA GORDON", minted=True, slug="dana-gordon"),
    dict(person_id="WY-MILLS-TYLER", display_name="Tyler Mills", first="Tyler", middle="J.", last="Mills", aliases="Tyler J. Mills; TYLER J. MILLS; TYLER MILLS", minted=True, slug="tyler-mills"),
    dict(person_id="WY-PILLEN-SUSAN", display_name="Susan Pillen", first="Susan", middle="", last="Pillen", aliases="SUSAN PILLEN", minted=True, slug="susan-pillen"),
    dict(person_id="WY-WHITE-DIANA", display_name="Diana White", first="Diana", middle="", last="White", aliases="DIANA WHITE", minted=True, slug="diana-white"),
    dict(person_id="WY-MILLER-TY", display_name="Ty Miller", first="Ty", middle="", last="Miller", aliases="TY MILLER", minted=True, slug="ty-miller"),
    dict(person_id="WY-MITCHELL-MARK", display_name="Mark Mitchell", first="Mark", middle="", last="Mitchell", aliases="MARK MITCHELL", minted=True, slug="mark-mitchell"),
    dict(person_id="WY-MILLS-JUSTIN", display_name="Justin Mills", first="Justin", middle="D.", last="Mills", aliases="Justin D. Mills; JUSTIN D. MILLS; JUSTIN MILLS", minted=True, slug="justin-mills"),
    dict(person_id="WY-HILL-BRIDGET", display_name="Bridget Hill", first="Bridget", middle="", last="Hill", aliases="Justice Bridget Hill", minted=True, slug="bridget-hill"),
    dict(person_id="WY-JAROSH-ROBERT", display_name="Robert C. Jarosh", first="Robert", middle="C.", last="Jarosh", aliases="Justice Robert C. Jarosh", minted=True, slug="robert-c-jarosh"),
    dict(person_id="WY-MCGRADY-MICHAEL", display_name="Michael J. McGrady", first="Michael", middle="J.", last="McGrady", aliases="Judge Michael J. McGrady", minted=True, slug="michael-j-mcgrady"),
    dict(person_id="WY-BURNINGHAM-BEN", display_name="Benjamin M. Burningham", first="Benjamin", middle="M.", last="Burningham", aliases="Ben Burningham; Judge Ben Burningham", minted=True, slug="benjamin-m-burningham"),
    dict(person_id="WY-STEWARD-GREG", display_name="Greg R. Steward", first="Greg", middle="R.", last="Steward", aliases="Judge Greg R. Steward", minted=True, slug="greg-r-steward"),
    # 2022/2024 named candidates who are not current holders (results only, no Profile required unless they won a later seat)
    dict(person_id="WY-ROMINE-DONALD", display_name="Donald Romine", first="Donald", middle="", last="Romine", aliases="", minted=True, slug="donald-romine"),
    dict(person_id="WY-TACY-LEVI", display_name="Levi Tacy", first="Levi", middle="", last="Tacy", aliases="", minted=True, slug="levi-tacy"),
    dict(person_id="WY-SCHILLER-NEIL", display_name="Neil Schiller", first="Neil", middle="", last="Schiller", aliases="", minted=True, slug="neil-schiller"),
    dict(person_id="WY-HAYNES-DELANE", display_name="Delane Haynes", first="Delane", middle="", last="Haynes", aliases="", minted=True, slug="delane-haynes"),
    dict(person_id="WY-GALE-STEVEN", display_name="Steven Gale", first="Steven", middle="", last="Gale", aliases="", minted=True, slug="steven-gale"),
    dict(person_id="WY-WRIGHT-TOM", display_name="Tom Wright", first="Tom", middle="", last="Wright", aliases="", minted=True, slug="tom-wright"),
    dict(person_id="WY-COWGER-JACKIE", display_name="Jackie Cowger", first="Jackie", middle="", last="Cowger", aliases="", minted=True, slug="jackie-cowger"),
    dict(person_id="WY-HALL-JEFFREY", display_name="Jeffrey Hall", first="Jeffrey", middle="", last="Hall", aliases="", minted=True, slug="jeffrey-hall"),
    dict(person_id="WY-KRINGLIE-KEVIN", display_name="Kevin S. Kringlie", first="Kevin", middle="S.", last="Kringlie", aliases="", minted=True, slug="kevin-s-kringlie"),
    dict(person_id="WY-LACEY-KARL", display_name="Karl Lacey", first="Karl", middle="", last="Lacey", aliases="", minted=True, slug="karl-lacey"),
    dict(person_id="WY-BARBER-RYAN", display_name="Ryan Barber", first="Ryan", middle="", last="Barber", aliases="", minted=True, slug="ryan-barber"),
    dict(person_id="WY-JOHNSON-TOM-WESTON", display_name="Tom Johnson", first="Tom", middle="", last="Johnson", aliases="", minted=True, slug="tom-johnson"),
    dict(person_id="WY-BUSH-LYNDA", display_name="Lynda R. Bush", first="Lynda", middle="R.", last="Bush", aliases="Judge Lynda R Bush", minted=True, slug="lynda-r-bush"),
]

# Tom Johnson minted as WY-JOHNSON-TOM-WESTON to avoid colliding with other Tom/Johnson IDs.

P = {p["person_id"]: p for p in PERSONS}


def src(label, url=None):
    d = {"label": label}
    if url:
        d["url"] = url
    return d


def href_for(pid, year_dir):
    p = P[pid]
    return f"candidates/{year_dir}/c/{p['slug']}.html"


def judge_href(pid):
    return f"officials/judges/{P[pid]['slug']}.html"

# Election rows: one dict per named candidate or write-in totals row.
# kind: municipal | school | judicial
# Fields follow the Phase 1/2 candidate columns plus person_id, jurisdiction, office_kind.

def cand(**k):
    k.setdefault("incumbent", "")
    k.setdefault("party", "")
    k.setdefault("primary_votes", "")
    k.setdefault("primary_vote_pct", "")
    k.setdefault("primary_result", "n/a")
    k.setdefault("primary_status", "")
    k.setdefault("writein_total_primary", "")
    k.setdefault("retrieved_date", RETRIEVED)
    return k

ELECTIONS = []

# ---------- 2022 municipal / school ----------
def add(row):
    ELECTIONS.append(cand(**row))

# Newcastle council 4yr 2022 VF3
NC22_WI, NC22_TVC, NC22_OV, NC22_UV, NC22_CT = 50, 2492, 72, 565, 3129
for name, pid, votes, pct, result, winner in [
    ("ANN MCCOLLEY", "WY-MCCOLLEY-ANN", 660, "21.09%", "elected", "Y"),
    ("DONNIE STEVESON", "WY-STEVESON-DON", 487, "15.56%", "elected", "Y"),
    ("JOHN BUTTS", "WY-BUTTS-JOHN", 470, "15.02%", "elected", "Y"),
    ("THOMAS A. VOSS", "WY-VOSS-THOMAS", 349, "11.15%", "defeated", ""),
    ("DONALD ROMINE", "WY-ROMINE-DONALD", 330, "10.55%", "defeated", ""),
    ("LEVI TACY", "WY-TACY-LEVI", 146, "4.67%", "defeated", ""),
]:
    add(dict(cycle="2022", county="Weston", office="NEWCASTLE COUNCIL MEMBER AT LARGE 4YR",
             office_normalized="City Council", seat_or_term="4-yr", vote_for=3, party="",
             candidate_ballot_name=name, person_id=pid, general_votes=votes, general_vote_pct=pct,
             general_result=result, general_status="official", winner=winner,
             writein_total_general=NC22_WI, source_general_results_url=SRC_2022,
             votes_named_plus_writeins_general=2492, pdf_total_votes_cast_general=NC22_TVC,
             check_ok_general="Y", notes="", phase="local-offices", jurisdiction="Newcastle",
             office_kind="city_council"))
add(dict(cycle="2022", county="Weston", office="NEWCASTLE COUNCIL MEMBER AT LARGE 4YR",
         office_normalized="City Council", seat_or_term="4-yr", vote_for=3, party="",
         candidate_ballot_name="Write-In Totals", person_id="", general_votes=NC22_WI, general_vote_pct="1.60%",
         general_result="n/a", general_status="official", winner="",
         writein_total_general=NC22_WI, source_general_results_url=SRC_2022,
         votes_named_plus_writeins_general=2492, pdf_total_votes_cast_general=NC22_TVC,
         check_ok_general="Y", notes="", phase="local-offices", jurisdiction="Newcastle",
         office_kind="city_council"))

# Newcastle council 2yr 2022 VF1 write-in only, no named winner
add(dict(cycle="2022", county="Weston", office="NEWCASTLE COUNCIL MEMBER AT LARGE 2YR",
         office_normalized="City Council", seat_or_term="2-yr", vote_for=1, party="",
         candidate_ballot_name="Write-In Totals", person_id="", general_votes=141, general_vote_pct="13.52%",
         general_result="n/a", general_status="official", winner="",
         writein_total_general=141, source_general_results_url=SRC_2022,
         votes_named_plus_writeins_general=141, pdf_total_votes_cast_general=141,
         check_ok_general="Y",
         notes="Write-in only; no named winner was printed on the official general summary.",
         phase="local-offices", jurisdiction="Newcastle", office_kind="city_council"))

# Upton mayor 2022
for name, pid, votes, pct, result, winner in [
    ("NICK TRANDAHL", "WY-TRANDAHL-NICK", 246, "59.13%", "elected", "Y"),
    ("NEIL SCHILLER", "WY-SCHILLER-NEIL", 126, "30.29%", "defeated", ""),
]:
    add(dict(cycle="2022", county="Weston", office="UPTON MAYOR", office_normalized="Mayor",
             seat_or_term="4-yr", vote_for=1, party="", candidate_ballot_name=name, person_id=pid,
             general_votes=votes, general_vote_pct=pct, general_result=result, general_status="official",
             winner=winner, writein_total_general=25, source_general_results_url=SRC_2022,
             votes_named_plus_writeins_general=397, pdf_total_votes_cast_general=397, check_ok_general="Y",
             notes="", phase="local-offices", jurisdiction="Upton", office_kind="mayor"))
add(dict(cycle="2022", county="Weston", office="UPTON MAYOR", office_normalized="Mayor",
         seat_or_term="4-yr", vote_for=1, party="", candidate_ballot_name="Write-In Totals", person_id="",
         general_votes=25, general_vote_pct="6.01%", general_result="n/a", general_status="official",
         winner="", writein_total_general=25, source_general_results_url=SRC_2022,
         votes_named_plus_writeins_general=397, pdf_total_votes_cast_general=397, check_ok_general="Y",
         notes="", phase="local-offices", jurisdiction="Upton", office_kind="mayor"))

# Upton council 2022 VF2
for name, pid, votes, pct, result, winner in [
    ("TIFFANY MCMILLAN", "WY-MCMILLAN-TIFFANY", 279, "33.53%", "elected", "Y"),
    ("JOE WATT", "WY-WATT-JOE", 257, "30.89%", "elected", "Y"),
    ("DELANE HAYNES", "WY-HAYNES-DELANE", 173, "20.79%", "defeated", ""),
]:
    add(dict(cycle="2022", county="Weston", office="UPTON COUNCIL MEMBER", office_normalized="Town Council",
             seat_or_term="4-yr", vote_for=2, party="", candidate_ballot_name=name, person_id=pid,
             general_votes=votes, general_vote_pct=pct, general_result=result, general_status="official",
             winner=winner, writein_total_general=10, source_general_results_url=SRC_2022,
             votes_named_plus_writeins_general=719, pdf_total_votes_cast_general=719, check_ok_general="Y",
             notes="", phase="local-offices", jurisdiction="Upton", office_kind="town_council"))
add(dict(cycle="2022", county="Weston", office="UPTON COUNCIL MEMBER", office_normalized="Town Council",
         seat_or_term="4-yr", vote_for=2, party="", candidate_ballot_name="Write-In Totals", person_id="",
         general_votes=10, general_vote_pct="1.20%", general_result="n/a", general_status="official",
         winner="", writein_total_general=10, source_general_results_url=SRC_2022,
         votes_named_plus_writeins_general=719, pdf_total_votes_cast_general=719, check_ok_general="Y",
         notes="", phase="local-offices", jurisdiction="Upton", office_kind="town_council"))

# SD1 2022 VF4
SD1_22 = [
    ("SEAN CRABTREE", "WY-CRABTREE-SEAN", 1121, "12.75%", "elected", "Y"),
    ("DANA GORDON", "WY-GORDON-DANA", 1009, "11.48%", "elected", "Y"),
    ("JOE PRELL", "WY-PRELL-JOE", 941, "10.70%", "elected", "Y"),
    ("JASON JENKINS", "WY-JENKINS-JASON", 684, "7.78%", "elected", "Y"),
    ("MARCIA LAMBERT", "WY-LAMBERT-MARCIA", 682, "7.76%", "defeated", ""),
    ("TOM WRIGHT", "WY-WRIGHT-TOM", 642, "7.30%", "defeated", ""),
    ("PAUL BAU", "WY-BAU-PAUL", 611, "6.95%", "defeated", ""),
    ("GILLIAN SEARS", "WY-SEARS-GILLIAN", 480, "5.46%", "defeated", ""),
    ("TYLER MILLS", "WY-MILLS-TYLER", 478, "5.44%", "defeated", ""),
    ("STANLEY JASINSKI", "WY-JASINSKI-STANLEY", 359, "4.08%", "defeated", ""),
    ("STEVEN GALE", "WY-GALE-STEVEN", 176, "2.00%", "defeated", ""),
]
for name, pid, votes, pct, result, winner in SD1_22:
    add(dict(cycle="2022", county="Weston", office="WESTON CO SCH DIST NO. 1 AT LARGE",
             office_normalized="School Board", seat_or_term="4-yr", vote_for=4, party="",
             candidate_ballot_name=name, person_id=pid, general_votes=votes, general_vote_pct=pct,
             general_result=result, general_status="official", winner=winner, writein_total_general=15,
             source_general_results_url=SRC_2022, votes_named_plus_writeins_general=7198,
             pdf_total_votes_cast_general=7198, check_ok_general="Y", notes="",
             phase="local-offices", jurisdiction="Weston County School District #1", office_kind="school_board"))
add(dict(cycle="2022", county="Weston", office="WESTON CO SCH DIST NO. 1 AT LARGE",
         office_normalized="School Board", seat_or_term="4-yr", vote_for=4, party="",
         candidate_ballot_name="Write-In Totals", person_id="", general_votes=15, general_vote_pct="0.17%",
         general_result="n/a", general_status="official", winner="", writein_total_general=15,
         source_general_results_url=SRC_2022, votes_named_plus_writeins_general=7198,
         pdf_total_votes_cast_general=7198, check_ok_general="Y", notes="",
         phase="local-offices", jurisdiction="Weston County School District #1", office_kind="school_board"))

# SD7 2022 VF3
for name, pid, votes, pct, result, winner in [
    ("JUSTIN MILLS", "WY-MILLS-JUSTIN", 475, "24.47%", "elected", "Y"),
    ("TY MILLER", "WY-MILLER-TY", 390, "20.09%", "elected", "Y"),
    ("MARK MITCHELL", "WY-MITCHELL-MARK", 352, "18.14%", "elected", "Y"),
    ("JACKIE COWGER", "WY-COWGER-JACKIE", 296, "15.25%", "defeated", ""),
]:
    add(dict(cycle="2022", county="Weston", office="WESTON CO SCH DIST NO. 7 AT LARGE",
             office_normalized="School Board", seat_or_term="4-yr", vote_for=3, party="",
             candidate_ballot_name=name, person_id=pid, general_votes=votes, general_vote_pct=pct,
             general_result=result, general_status="official", winner=winner, writein_total_general=12,
             source_general_results_url=SRC_2022, votes_named_plus_writeins_general=1525,
             pdf_total_votes_cast_general=1525, check_ok_general="Y", notes="",
             phase="local-offices", jurisdiction="Weston County School District #7", office_kind="school_board"))
add(dict(cycle="2022", county="Weston", office="WESTON CO SCH DIST NO. 7 AT LARGE",
         office_normalized="School Board", seat_or_term="4-yr", vote_for=3, party="",
         candidate_ballot_name="Write-In Totals", person_id="", general_votes=12, general_vote_pct="0.62%",
         general_result="n/a", general_status="official", winner="", writein_total_general=12,
         source_general_results_url=SRC_2022, votes_named_plus_writeins_general=1525,
         pdf_total_votes_cast_general=1525, check_ok_general="Y", notes="",
         phase="local-offices", jurisdiction="Weston County School District #7", office_kind="school_board"))

# 2022 judicial (circuit Phillips) — results only, not treated as a current holder here
add(dict(cycle="2022", county="Weston", office="JUDGE CIRCUIT COURT SIXTH JUDICIAL DIST PHILLIPS",
         office_normalized="Circuit Judge Retention", seat_or_term="", vote_for=1, party="",
         candidate_ballot_name="PHILLIPS", person_id="", general_votes="", general_vote_pct="",
         general_result="retained", general_status="official", winner="Y",
         writein_total_general="", source_general_results_url=SRC_2022,
         notes="YES 1,825 (64.15% of contest); NO 629; Total Votes Cast 2,454; Overvotes 0; Undervotes 391; Contest Totals 2,845. Listed as historical results only; this person is not on the 2026 ballot and is not in the current officeholder file.",
         phase="local-offices", jurisdiction="6th Judicial District", office_kind="judicial_retention",
         yes_votes=1825, no_votes=629, yes_pct="64.15%", no_pct="22.11%",
         votes_named_plus_writeins_general=2454, pdf_total_votes_cast_general=2454, check_ok_general="Y"))

# ---------- 2024 ----------
# Newcastle mayor
for name, pid, votes, result, winner in [
    ("TYREL OWENS", "WY-OWENS-TYREL", 743, "elected", "Y"),
    ("PAM GUALTIERI", "WY-GUALTIERI-PAM", 574, "defeated", ""),
]:
    add(dict(cycle="2024", county="Weston", office="CITY OF NEWCASTLE MAYOR", office_normalized="Mayor",
             seat_or_term="4-yr", vote_for=1, party="", candidate_ballot_name=name, person_id=pid,
             general_votes=votes, general_vote_pct="", general_result=result, general_status="official",
             winner=winner, writein_total_general=12, source_general_results_url=SRC_2024,
             votes_named_plus_writeins_general=1329, pdf_total_votes_cast_general=1329, check_ok_general="Y",
             notes="", phase="local-offices", jurisdiction="Newcastle", office_kind="mayor"))
add(dict(cycle="2024", county="Weston", office="CITY OF NEWCASTLE MAYOR", office_normalized="Mayor",
         seat_or_term="4-yr", vote_for=1, party="", candidate_ballot_name="Write-In Totals", person_id="",
         general_votes=12, general_vote_pct="", general_result="n/a", general_status="official", winner="",
         writein_total_general=12, source_general_results_url=SRC_2024,
         votes_named_plus_writeins_general=1329, pdf_total_votes_cast_general=1329, check_ok_general="Y",
         notes="", phase="local-offices", jurisdiction="Newcastle", office_kind="mayor"))

# Newcastle council 2024 VF3
for name, pid, votes, result, winner in [
    ("DAREN L. DOWNS", "WY-DOWNS-DAREN", 681, "elected", "Y"),
    ("CHRIS KENNEY", "WY-KENNEY-CHRIS", 659, "elected", "Y"),
    ("THOMAS A. VOSS", "WY-VOSS-THOMAS", 483, "elected", "Y"),
    ("KEVIN S. KRINGLIE", "WY-KRINGLIE-KEVIN", 460, "defeated", ""),
    ("JEFFREY HALL", "WY-HALL-JEFFREY", 407, "defeated", ""),
    ("KARL LACEY", "WY-LACEY-KARL", 263, "defeated", ""),
]:
    add(dict(cycle="2024", county="Weston", office="CITY OF NEWCASTLE COUNCIL MEMBER AT-LARGE",
             office_normalized="City Council", seat_or_term="4-yr", vote_for=3, party="",
             candidate_ballot_name=name, person_id=pid, general_votes=votes, general_vote_pct="",
             general_result=result, general_status="official", winner=winner, writein_total_general=29,
             source_general_results_url=SRC_2024, votes_named_plus_writeins_general=2982,
             pdf_total_votes_cast_general=2982, check_ok_general="Y", notes="",
             phase="local-offices", jurisdiction="Newcastle", office_kind="city_council"))
add(dict(cycle="2024", county="Weston", office="CITY OF NEWCASTLE COUNCIL MEMBER AT-LARGE",
         office_normalized="City Council", seat_or_term="4-yr", vote_for=3, party="",
         candidate_ballot_name="Write-In Totals", person_id="", general_votes=29, general_vote_pct="",
         general_result="n/a", general_status="official", winner="", writein_total_general=29,
         source_general_results_url=SRC_2024, votes_named_plus_writeins_general=2982,
         pdf_total_votes_cast_general=2982, check_ok_general="Y", notes="",
         phase="local-offices", jurisdiction="Newcastle", office_kind="city_council"))

# Upton council 2024 VF2 — scan is slightly unclear on Norman's total (375 vs nearby digits);
# named+write-ins using 375+353+15=743 vs printed Total Votes Cast 745.
for name, pid, votes, result, winner in [
    ("JUSTIN NORMAN", "WY-NORMAN-JUSTIN", 375, "elected", "Y"),
    ("RICK ROTHLEUTNER", "WY-ROTHLEUTNER-RICK", 353, "elected", "Y"),
]:
    add(dict(cycle="2024", county="Weston", office="TOWN OF UPTON COUNCIL MEMBER",
             office_normalized="Town Council", seat_or_term="4-yr", vote_for=2, party="",
             candidate_ballot_name=name, person_id=pid, general_votes=votes, general_vote_pct="",
             general_result=result, general_status="official", winner=winner, writein_total_general=15,
             source_general_results_url=SRC_2024, votes_named_plus_writeins_general=743,
             pdf_total_votes_cast_general=745, check_ok_general="N",
             notes="Official summary is a scanned page. Justin Norman's total was read as 375; named candidates plus write-ins add to 743 against a printed Total Votes Cast of 745. Overvotes 0, Undervotes 253, Contest Totals 998 (745+253=998).",
             phase="local-offices", jurisdiction="Upton", office_kind="town_council"))
add(dict(cycle="2024", county="Weston", office="TOWN OF UPTON COUNCIL MEMBER",
         office_normalized="Town Council", seat_or_term="4-yr", vote_for=2, party="",
         candidate_ballot_name="Write-In Totals", person_id="", general_votes=15, general_vote_pct="",
         general_result="n/a", general_status="official", winner="", writein_total_general=15,
         source_general_results_url=SRC_2024, votes_named_plus_writeins_general=743,
         pdf_total_votes_cast_general=745, check_ok_general="N",
         notes="See named-candidate rows for the 743 vs 745 cross-check note.",
         phase="local-offices", jurisdiction="Upton", office_kind="town_council"))

# SD1 2024 VF5 — named+wi may be 8119 vs printed 8121 (scan)
for name, pid, votes, result, winner in [
    ("DANA MANN-TAVEGIA", "WY-MANN-TAVEGIA-DANA", 1514, "elected", "Y"),
    ("BILLY FITZWATER", "WY-FITZWATER-BILLY", 1487, "elected", "Y"),
    ("TYLER J. MILLS", "WY-MILLS-TYLER", 1459, "elected", "Y"),
    ("SUSAN PILLEN", "WY-PILLEN-SUSAN", 1354, "elected", "Y"),
    ("PAUL BAU", "WY-BAU-PAUL", 1343, "elected", "Y"),
    ("STEVEN GALE", "WY-GALE-STEVEN", 847, "defeated", ""),
]:
    add(dict(cycle="2024", county="Weston", office="WESTON COUNTY SCHOOL DIST NO. 1 AT LARGE",
             office_normalized="School Board", seat_or_term="4-yr", vote_for=5, party="",
             candidate_ballot_name=name, person_id=pid, general_votes=votes, general_vote_pct="",
             general_result=result, general_status="official", winner=winner, writein_total_general=117,
             source_general_results_url=SRC_2024, votes_named_plus_writeins_general=8119,
             pdf_total_votes_cast_general=8121, check_ok_general="N",
             notes="Official summary is a scanned page. Named candidates plus write-ins add to 8,119 against a printed Total Votes Cast of 8,121. Overvotes 15, Undervotes 5,634, Contest Totals 13,770.",
             phase="local-offices", jurisdiction="Weston County School District #1", office_kind="school_board"))
add(dict(cycle="2024", county="Weston", office="WESTON COUNTY SCHOOL DIST NO. 1 AT LARGE",
         office_normalized="School Board", seat_or_term="4-yr", vote_for=5, party="",
         candidate_ballot_name="Write-In Totals", person_id="", general_votes=117, general_vote_pct="",
         general_result="n/a", general_status="official", winner="", writein_total_general=117,
         source_general_results_url=SRC_2024, votes_named_plus_writeins_general=8119,
         pdf_total_votes_cast_general=8121, check_ok_general="N", notes="See named-candidate rows for the cross-check note.",
         phase="local-offices", jurisdiction="Weston County School District #1", office_kind="school_board"))

# SD7 2024 VF2
for name, pid, votes, result, winner in [
    ("DIANA WHITE", "WY-WHITE-DIANA", 591, "elected", "Y"),
    ("CURTIS RANKIN", "WY-RANKIN-CURTIS", 568, "elected", "Y"),
]:
    add(dict(cycle="2024", county="Weston", office="WESTON COUNTY SCHOOL DIST NO. 7 AT LARGE",
             office_normalized="School Board", seat_or_term="4-yr", vote_for=2, party="",
             candidate_ballot_name=name, person_id=pid, general_votes=votes, general_vote_pct="",
             general_result=result, general_status="official", winner=winner, writein_total_general=12,
             source_general_results_url=SRC_2024, votes_named_plus_writeins_general=1171,
             pdf_total_votes_cast_general=1171, check_ok_general="Y", notes="",
             phase="local-offices", jurisdiction="Weston County School District #7", office_kind="school_board"))
add(dict(cycle="2024", county="Weston", office="WESTON COUNTY SCHOOL DIST NO. 7 AT LARGE",
         office_normalized="School Board", seat_or_term="4-yr", vote_for=2, party="",
         candidate_ballot_name="Write-In Totals", person_id="", general_votes=12, general_vote_pct="",
         general_result="n/a", general_status="official", winner="", writein_total_general=12,
         source_general_results_url=SRC_2024, votes_named_plus_writeins_general=1171,
         pdf_total_votes_cast_general=1171, check_ok_general="Y", notes="",
         phase="local-offices", jurisdiction="Weston County School District #7", office_kind="school_board"))

# 2024 Judge Bush retention
add(dict(cycle="2024", county="Weston", office="RETAIN JUDGE LYNDA R BUSH",
         office_normalized="Circuit Judge Retention", seat_or_term="", vote_for=1, party="",
         candidate_ballot_name="LYNDA R BUSH", person_id="WY-BUSH-LYNDA",
         general_votes="", general_vote_pct="", general_result="retained", general_status="official",
         winner="Y", writein_total_general="", source_general_results_url=SRC_2024,
         yes_votes=2175, no_votes=797, votes_named_plus_writeins_general=2972,
         pdf_total_votes_cast_general=2972, check_ok_general="Y",
         notes="YES 2,175; NO 797; Total Votes Cast 2,972; Overvotes 0; Undervotes 561; Contest Totals 3,533. Current Weston circuit judge per wyocourts; not on the 2026 ballot.",
         phase="local-offices", jurisdiction="6th Judicial District", office_kind="judicial_retention"))

# ---------- 2026 ----------
for name, pid, votes, pct, result, winner in [
    ("WYATT VOELKER", "WY-VOELKER-WYATT", 660, "31.03%", "elected", "Y"),
    ("PAM GUALTIERI", "WY-GUALTIERI-PAM", 579, "27.22%", "elected", "Y"),
    ("DONNIE STEVESON", "WY-STEVESON-DON", 459, "21.58%", "elected", "Y"),
    ("JOHN G. BUTTS", "WY-BUTTS-JOHN", 406, "19.09%", "defeated", ""),
]:
    add(dict(cycle="2026", county="Weston", office="NEWCASTLE COUNCIL MEMBER AT-LARGE",
             office_normalized="City Council", seat_or_term="4-yr", vote_for=3, party="",
             candidate_ballot_name=name, person_id=pid, general_votes=votes, general_vote_pct=pct,
             general_result=result, general_status="official", winner=winner, writein_total_general=23,
             source_general_results_url=SRC_2026, votes_named_plus_writeins_general=2127,
             pdf_total_votes_cast_general=2127, check_ok_general="Y", notes="",
             phase="local-offices", jurisdiction="Newcastle", office_kind="city_council"))
add(dict(cycle="2026", county="Weston", office="NEWCASTLE COUNCIL MEMBER AT-LARGE",
         office_normalized="City Council", seat_or_term="4-yr", vote_for=3, party="",
         candidate_ballot_name="Write-In Totals", person_id="", general_votes=23, general_vote_pct="1.08%",
         general_result="n/a", general_status="official", winner="", writein_total_general=23,
         source_general_results_url=SRC_2026, votes_named_plus_writeins_general=2127,
         pdf_total_votes_cast_general=2127, check_ok_general="Y", notes="",
         phase="local-offices", jurisdiction="Newcastle", office_kind="city_council"))

for name, pid, votes, pct, result, winner in [
    ("TY KENNEDY", "WY-KENNEDY-TY", 200, "55.25%", "elected", "Y"),
    ("TIFFANY MCMILLAN", "WY-MCMILLAN-TIFFANY", 155, "42.82%", "defeated", ""),
]:
    add(dict(cycle="2026", county="Weston", office="UPTON MAYOR UPTON", office_normalized="Mayor",
             seat_or_term="4-yr", vote_for=1, party="", candidate_ballot_name=name, person_id=pid,
             general_votes=votes, general_vote_pct=pct, general_result=result, general_status="official",
             winner=winner, writein_total_general=7, source_general_results_url=SRC_2026,
             votes_named_plus_writeins_general=362, pdf_total_votes_cast_general=362, check_ok_general="Y",
             notes="", phase="local-offices", jurisdiction="Upton", office_kind="mayor"))
add(dict(cycle="2026", county="Weston", office="UPTON MAYOR UPTON", office_normalized="Mayor",
         seat_or_term="4-yr", vote_for=1, party="", candidate_ballot_name="Write-In Totals", person_id="",
         general_votes=7, general_vote_pct="1.93%", general_result="n/a", general_status="official",
         winner="", writein_total_general=7, source_general_results_url=SRC_2026,
         votes_named_plus_writeins_general=362, pdf_total_votes_cast_general=362, check_ok_general="Y",
         notes="", phase="local-offices", jurisdiction="Upton", office_kind="mayor"))

for name, pid, votes, pct, result, winner in [
    ("KELLY WOZNEY", "WY-WOZNEY-KELLY", 211, "31.92%", "elected", "Y"),
    ("JOE WATT", "WY-WATT-JOE", 174, "26.32%", "elected", "Y"),
    ("TOM JOHNSON", "WY-JOHNSON-TOM-WESTON", 137, "20.73%", "defeated", ""),
    ("RYAN BARBER", "WY-BARBER-RYAN", 135, "20.42%", "defeated", ""),
]:
    add(dict(cycle="2026", county="Weston", office="UPTON COUNCIL MEMBER AT-LARGE",
             office_normalized="Town Council", seat_or_term="4-yr", vote_for=2, party="",
             candidate_ballot_name=name, person_id=pid, general_votes=votes, general_vote_pct=pct,
             general_result=result, general_status="official", winner=winner, writein_total_general=4,
             source_general_results_url=SRC_2026, votes_named_plus_writeins_general=661,
             pdf_total_votes_cast_general=661, check_ok_general="Y", notes="",
             phase="local-offices", jurisdiction="Upton", office_kind="town_council"))
add(dict(cycle="2026", county="Weston", office="UPTON COUNCIL MEMBER AT-LARGE",
         office_normalized="Town Council", seat_or_term="4-yr", vote_for=2, party="",
         candidate_ballot_name="Write-In Totals", person_id="", general_votes=4, general_vote_pct="0.61%",
         general_result="n/a", general_status="official", winner="", writein_total_general=4,
         source_general_results_url=SRC_2026, votes_named_plus_writeins_general=661,
         pdf_total_votes_cast_general=661, check_ok_general="Y", notes="",
         phase="local-offices", jurisdiction="Upton", office_kind="town_council"))

for name, pid, votes, pct in [
    ("SEAN CRABTREE", "WY-CRABTREE-SEAN", 1469, "28.08%"),
    ("SCOTT W. JOHNSON", "WY-JOHNSON-SCOTT", 1281, "24.49%"),
    ("RICHARD JOE PRELL", "WY-PRELL-JOE", 1238, "23.67%"),
    ("JASON JENKINS", "WY-JENKINS-JASON", 1199, "22.92%"),
]:
    add(dict(cycle="2026", county="Weston", office="WESTON COUNTY SCH DIST NO. 1 AT-LARGE",
             office_normalized="School Board", seat_or_term="4-yr", vote_for=4, party="",
             candidate_ballot_name=name, person_id=pid, general_votes=votes, general_vote_pct=pct,
             general_result="elected", general_status="official", winner="Y", writein_total_general=44,
             source_general_results_url=SRC_2026, votes_named_plus_writeins_general=5231,
             pdf_total_votes_cast_general=5231, check_ok_general="Y", notes="",
             phase="local-offices", jurisdiction="Weston County School District #1", office_kind="school_board"))
add(dict(cycle="2026", county="Weston", office="WESTON COUNTY SCH DIST NO. 1 AT-LARGE",
         office_normalized="School Board", seat_or_term="4-yr", vote_for=4, party="",
         candidate_ballot_name="Write-In Totals", person_id="", general_votes=44, general_vote_pct="0.84%",
         general_result="n/a", general_status="official", winner="", writein_total_general=44,
         source_general_results_url=SRC_2026, votes_named_plus_writeins_general=5231,
         pdf_total_votes_cast_general=5231, check_ok_general="Y", notes="",
         phase="local-offices", jurisdiction="Weston County School District #1", office_kind="school_board"))

for name, pid, votes, pct in [
    ("JUSTIN D. MILLS", "WY-MILLS-JUSTIN", 482, "37.31%"),
    ("MARK MITCHELL", "WY-MITCHELL-MARK", 420, "32.51%"),
    ("TY MILLER", "WY-MILLER-TY", 380, "29.41%"),
]:
    add(dict(cycle="2026", county="Weston", office="WESTON COUNTY SCH DIST NO. 7 AT-LARGE",
             office_normalized="School Board", seat_or_term="4-yr", vote_for=3, party="",
             candidate_ballot_name=name, person_id=pid, general_votes=votes, general_vote_pct=pct,
             general_result="elected", general_status="official", winner="Y", writein_total_general=10,
             source_general_results_url=SRC_2026, votes_named_plus_writeins_general=1292,
             pdf_total_votes_cast_general=1292, check_ok_general="Y", notes="",
             phase="local-offices", jurisdiction="Weston County School District #7", office_kind="school_board"))
add(dict(cycle="2026", county="Weston", office="WESTON COUNTY SCH DIST NO. 7 AT-LARGE",
         office_normalized="School Board", seat_or_term="4-yr", vote_for=3, party="",
         candidate_ballot_name="Write-In Totals", person_id="", general_votes=10, general_vote_pct="0.77%",
         general_result="n/a", general_status="official", winner="", writein_total_general=10,
         source_general_results_url=SRC_2026, votes_named_plus_writeins_general=1292,
         pdf_total_votes_cast_general=1292, check_ok_general="Y", notes="",
         phase="local-offices", jurisdiction="Weston County School District #7", office_kind="school_board"))

# 2026 judicial retention
for office, pid, bname, yes, no, ypct, npct, tvc, uv in [
    ("RETAIN JUSTICE BRIDGET HILL", "WY-HILL-BRIDGET", "BRIDGET HILL", 1465, 697, "67.76%", "32.24%", 2162, 392),
    ("RETAIN JUSTICE ROBERT C. JAROSH", "WY-JAROSH-ROBERT", "ROBERT C. JAROSH", 1426, 700, "67.07%", "32.93%", 2126, 428),
    ("RETAIN JUDGE MICHAEL J. MCGRADY", "WY-MCGRADY-MICHAEL", "MICHAEL J. MCGRADY", 1478, 642, "69.72%", "30.28%", 2120, 434),
    ("RETAIN JUDGE BEN BURNINGHAM", "WY-BURNINGHAM-BEN", "BEN BURNINGHAM", 1471, 624, "70.21%", "29.79%", 2095, 459),
    ("RETAIN JUDGE GREG R. STEWARD", "WY-STEWARD-GREG", "GREG R. STEWARD", 1493, 616, "70.79%", "29.21%", 2109, 445),
]:
    norm = "Supreme Court Retention" if "JUSTICE" in office else (
        "Chancery Judge Retention" if "BURNINGHAM" in office else (
        "District Judge Retention" if "MCGRADY" in office else "Circuit Judge Retention"))
    add(dict(cycle="2026", county="Weston", office=office, office_normalized=norm, seat_or_term="",
             vote_for=1, party="", candidate_ballot_name=bname, person_id=pid,
             general_votes="", general_vote_pct="", general_result="retained", general_status="official",
             winner="Y", writein_total_general="", source_general_results_url=SRC_2026,
             yes_votes=yes, no_votes=no, yes_pct=ypct, no_pct=npct,
             votes_named_plus_writeins_general=tvc, pdf_total_votes_cast_general=tvc, check_ok_general="Y",
             notes=f"YES {yes:,} ({ypct}); NO {no:,} ({npct}); Total Votes Cast {tvc:,}; Overvotes 0; Undervotes {uv:,}; Contest Totals 2,554.",
             phase="local-offices", jurisdiction="Weston", office_kind="judicial_retention"))

def holder(pid, party="", role=None, href=None, ballot_name=None, term_end=None,
           sources=None, succeeding=None, notes=None, sort_key=None, retention=None):
    p = P[pid]
    h = {"name": p["display_name"], "person_id": pid, "sources": sources or []}
    if party:
        h["party"] = party
    if role:
        h["role"] = role
    if href:
        h["href"] = href
    if ballot_name:
        h["ballot_name"] = ballot_name
    if term_end:
        h["term_end"] = term_end
    if succeeding:
        h["succeeding"] = succeeding
    if notes:
        h["notes"] = notes
    if sort_key:
        h["sort_key"] = sort_key
    if retention:
        h["retention"] = retention
    return h


def office(title, holders, layout=None, sort_key=None, note=None):
    o = {"office": title, "layout": layout or ("heading-then-names" if len(holders) != 1 else "office-and-name"),
         "holders": holders}
    if sort_key:
        o["sort_key"] = sort_key
    if note:
        o["note"] = note
    return o


def elect(pid, party="", href=None, sources=None, ballot_name=None, term_end=None):
    p = P[pid]
    s = {"name": p["display_name"], "person_id": pid, "takes_office": "January", "sources": sources or []}
    if party:
        s["party"] = party
    if href:
        s["href"] = href
    if ballot_name:
        s["ballot_name"] = ballot_name
    if term_end:
        s["term_end"] = term_end
    return s


def municipal_group():
    # Current Newcastle council from city website, matched to official results.
    # Terms labeled (2026) on the city site end in January 2027; (2029) end January 2029.
    nc_council = [
        holder("WY-VOSS-THOMAS", role="President", href=href_for("WY-VOSS-THOMAS", "2024-local"),
               ballot_name="THOMAS A. VOSS", term_end="January 2029", sort_key="F02A",
               sources=[src("City of Newcastle Mayor & City Council (President, 2029)", SRC_NEWC),
                        src("Weston County official 2024 general results, elected", SRC_2024)]),
        holder("WY-STEVESON-DON", href=href_for("WY-STEVESON-DON", "2026-local"),
               ballot_name="DONNIE STEVESON", term_end="January 2031", sort_key="F02B",
               sources=[src("City of Newcastle Mayor & City Council (2026); re-elected 2026", SRC_NEWC),
                        src("Weston County official 2022 general results, elected", SRC_2022),
                        src("Weston County official 2026 general results, re-elected", SRC_2026)]),
        holder("WY-MCCOLLEY-ANN", href=href_for("WY-MCCOLLEY-ANN", "2022-local"),
               ballot_name="ANN MCCOLLEY", term_end="January 2027", sort_key="F02C",
               sources=[src("City of Newcastle Mayor & City Council (2026)", SRC_NEWC),
                        src("Weston County official 2022 general results, elected", SRC_2022)],
               succeeding=elect("WY-VOELKER-WYATT", href=href_for("WY-VOELKER-WYATT", "2026-local"),
                                ballot_name="WYATT VOELKER", term_end="January 2031",
                                sources=[src("Weston County official 2026 general results, elected", SRC_2026)]),
               notes="Term ends January 2027. She was not on the 2026 council ballot. Wyatt Voelker, a 2026 council winner, is listed as the incoming member along with Pam Gualtieri (succeeding John Butts). Pairing of incoming members to outgoing seats is by vacancy count, not a seat-by-seat official map."),
        holder("WY-DOWNS-DAREN", href=href_for("WY-DOWNS-DAREN", "2024-local"),
               ballot_name="DAREN L. DOWNS", term_end="January 2029", sort_key="F02D",
               sources=[src("City of Newcastle Mayor & City Council (2029); site also spells Darren in one committee list", SRC_NEWC),
                        src("Weston County official 2024 general results, elected as DAREN L. DOWNS", SRC_2024)]),
        holder("WY-KENNEY-CHRIS", href=href_for("WY-KENNEY-CHRIS", "2024-local"),
               ballot_name="CHRIS KENNEY", term_end="January 2029", sort_key="F02E",
               sources=[src("City of Newcastle Mayor & City Council (2029)", SRC_NEWC),
                        src("Weston County official 2024 general results, elected", SRC_2024)]),
        holder("WY-BUTTS-JOHN", href=href_for("WY-BUTTS-JOHN", "2022-local"),
               ballot_name="JOHN G. BUTTS", term_end="January 2027", sort_key="F02F",
               sources=[src("City of Newcastle Mayor & City Council (2026)", SRC_NEWC),
                        src("Weston County official 2022 general results, elected", SRC_2022),
                        src("Weston County official 2026 general results, not re-elected", SRC_2026)],
               succeeding=elect("WY-GUALTIERI-PAM", href=href_for("WY-GUALTIERI-PAM", "2026-local"),
                                ballot_name="PAM GUALTIERI", term_end="January 2031",
                                sources=[src("Weston County official 2026 general results, elected", SRC_2026)]),
               notes="On the 2026 council ballot and was not among the top three. Pam Gualtieri and Wyatt Voelker were elected; Don Steveson was re-elected."),
    ]
    up_council = [
        holder("WY-NORMAN-JUSTIN", role="Vice Mayor", href=href_for("WY-NORMAN-JUSTIN", "2024-local"),
               ballot_name="JUSTIN NORMAN", term_end="January 2029", sort_key="F04A",
               sources=[src("Town of Upton City Government (Vice Mayor, 2028)", SRC_UPTON),
                        src("Weston County official 2024 general results, elected", SRC_2024)],
               notes="The town site labels the term (2028); a regular 4-year term from the 2024 election ends January 2029."),
        holder("WY-WATT-JOE", href=href_for("WY-WATT-JOE", "2026-local"),
               ballot_name="JOE WATT", term_end="January 2031", sort_key="F04B",
               sources=[src("Town of Upton City Government (2026); re-elected 2026", SRC_UPTON),
                        src("Weston County official 2022 general results, elected", SRC_2022),
                        src("Weston County official 2026 general results, re-elected", SRC_2026)]),
        holder("WY-MCMILLAN-TIFFANY", href=href_for("WY-MCMILLAN-TIFFANY", "2022-local"),
               ballot_name="TIFFANY MCMILLAN", term_end="January 2027", sort_key="F04C",
               sources=[src("Town of Upton City Government (2026)", SRC_UPTON),
                        src("Weston County official 2022 general results, elected to council", SRC_2022),
                        src("Weston County official 2026 general results, ran for mayor, not elected", SRC_2026)],
               succeeding=elect("WY-WOZNEY-KELLY", href=href_for("WY-WOZNEY-KELLY", "2026-local"),
                                ballot_name="KELLY WOZNEY", term_end="January 2031",
                                sources=[src("Weston County official 2026 general results, elected to council", SRC_2026)]),
               notes="Ran for Upton mayor in 2026 and was not elected. She was not on the 2026 council ballot. Kelly Wozney was a 2026 council winner; Joe Watt was re-elected."),
        holder("WY-ROTHLEUTNER-RICK", href=href_for("WY-ROTHLEUTNER-RICK", "2024-local"),
               ballot_name="RICK ROTHLEUTNER", term_end="January 2029", sort_key="F04D",
               sources=[src("Town of Upton City Government (2028)", SRC_UPTON),
                        src("Weston County official 2024 general results, elected", SRC_2024)],
               notes="The town site labels the term (2028); a regular 4-year term from the 2024 election ends January 2029."),
    ]
    return {
        "id": "municipal",
        "title": "Municipal offices",
        "sort_key": "F",
        "offices": [
            office("Newcastle Mayor", [
                holder("WY-OWENS-TYREL", href=href_for("WY-OWENS-TYREL", "2024-local"),
                       ballot_name="TYREL OWENS", term_end="January 2029", sort_key="F01",
                       sources=[src("City of Newcastle Mayor & City Council (Mayor, 2029)", SRC_NEWC),
                                src("Weston County official 2024 general results, elected", SRC_2024)])
            ], sort_key="F01"),
            office("Newcastle City Council, at-large", nc_council, sort_key="F02",
                   note="Six members. The official city roster and the 2022 and 2024 (and 2026) general results agree on the current six. Two members leave in January 2027; two 2026 winners take office then. Pairing of each incoming member to an outgoing seat is not printed on the results."),
            office("Upton Mayor", [
                holder("WY-TRANDAHL-NICK", href=href_for("WY-TRANDAHL-NICK", "2022-local"),
                       ballot_name="NICK TRANDAHL", term_end="January 2027", sort_key="F03",
                       sources=[src("Town of Upton City Government (Mayor, 2026)", SRC_UPTON),
                                src("Weston County official 2022 general results, elected", SRC_2022)],
                       succeeding=elect("WY-KENNEDY-TY", href=href_for("WY-KENNEDY-TY", "2026-local"),
                                        ballot_name="TY KENNEDY", term_end="January 2031",
                                        sources=[src("Weston County official 2026 general results, elected", SRC_2026)]))
            ], sort_key="F03"),
            office("Upton Town Council, at-large", up_council, sort_key="F04",
                   note="Four members. The official town roster and the 2022 and 2024 general results agree on the current four. Tiffany McMillan leaves in January 2027; Kelly Wozney, a 2026 council winner, takes office then. Joe Watt was re-elected."),
        ],
    }


def schools_group():
    # Current 9 SD1 members from the official board page, matched to 2022/2024 results.
    # 2026 seats (NLJ: Jenkins, Dana Gordon, Prell, Crabtree): Crabtree, Johnson, Prell, Jenkins elected.
    # Dana Gordon leaves in January; Scott W. Johnson takes office.
    sd1 = [
        holder("WY-FITZWATER-BILLY", role="Board Chair", href=href_for("WY-FITZWATER-BILLY", "2024-local"),
               ballot_name="BILLY FITZWATER", term_end="January 2029", sort_key="G01A",
               sources=[src("WCSD #1 official board members page (Board Chair)", SRC_SD1),
                        src("Weston County official 2024 general results, elected", SRC_2024)]),
        holder("WY-JENKINS-JASON", role="Board Vice-Chair", href=href_for("WY-JENKINS-JASON", "2026-local"),
               ballot_name="JASON JENKINS", term_end="January 2031", sort_key="G01B",
               sources=[src("WCSD #1 official board members page (Board Vice-Chair)", SRC_SD1),
                        src("Weston County official 2022 general results, elected", SRC_2022),
                        src("Weston County official 2026 general results, re-elected", SRC_2026)]),
        holder("WY-PRELL-JOE", role="Board Clerk", href=href_for("WY-PRELL-JOE", "2026-local"),
               ballot_name="RICHARD JOE PRELL", term_end="January 2031", sort_key="G01C",
               sources=[src("WCSD #1 official board members page (Board Clerk, Joe Prell)", SRC_SD1),
                        src("Weston County official 2022 general results, elected as JOE PRELL", SRC_2022),
                        src("Weston County official 2026 general results, re-elected as RICHARD JOE PRELL", SRC_2026)],
               notes="The official board page lists Joe Prell. The 2026 ballot used Richard Joe Prell."),
        holder("WY-MANN-TAVEGIA-DANA", role="Board Treasurer", href=href_for("WY-MANN-TAVEGIA-DANA", "2024-local"),
               ballot_name="DANA MANN-TAVEGIA", term_end="January 2029", sort_key="G01D",
               sources=[src("WCSD #1 official board members page (Board Treasurer)", SRC_SD1),
                        src("Weston County official 2024 general results, elected", SRC_2024)],
               notes="Listed separately from Dana Gordon on the official board page; they are treated as two people."),
        holder("WY-BAU-PAUL", href=href_for("WY-BAU-PAUL", "2024-local"),
               ballot_name="PAUL BAU", term_end="January 2029", sort_key="G01E",
               sources=[src("WCSD #1 official board members page", SRC_SD1),
                        src("Weston County official 2024 general results, elected", SRC_2024)]),
        holder("WY-CRABTREE-SEAN", href=href_for("WY-CRABTREE-SEAN", "2026-local"),
               ballot_name="SEAN CRABTREE", term_end="January 2031", sort_key="G01F",
               sources=[src("WCSD #1 official board members page", SRC_SD1),
                        src("Weston County official 2022 general results, elected", SRC_2022),
                        src("Weston County official 2026 general results, re-elected", SRC_2026)]),
        holder("WY-GORDON-DANA", href=href_for("WY-GORDON-DANA", "2022-local"),
               ballot_name="DANA GORDON", term_end="January 2027", sort_key="G01G",
               sources=[src("WCSD #1 official board members page", SRC_SD1),
                        src("Weston County official 2022 general results, elected", SRC_2022)],
               succeeding=elect("WY-JOHNSON-SCOTT", href=href_for("WY-JOHNSON-SCOTT", "2026-local"),
                                ballot_name="SCOTT W. JOHNSON", term_end="January 2031",
                                sources=[src("Weston County official 2026 general results, elected", SRC_2026)]),
               notes="The News Letter Journal reported that her 2022 seat was one of the four on the 2026 ballot. She was not a 2026 candidate. Scott W. Johnson was elected to one of those four seats."),
        holder("WY-MILLS-TYLER", href=href_for("WY-MILLS-TYLER", "2024-local"),
               ballot_name="TYLER J. MILLS", term_end="January 2029", sort_key="G01H",
               sources=[src("WCSD #1 official board members page (Tyler Mills)", SRC_SD1),
                        src("Weston County official 2024 general results, elected as TYLER J. MILLS", SRC_2024)]),
        holder("WY-PILLEN-SUSAN", href=href_for("WY-PILLEN-SUSAN", "2024-local"),
               ballot_name="SUSAN PILLEN", term_end="January 2029", sort_key="G01I",
               sources=[src("WCSD #1 official board members page", SRC_SD1),
                        src("Weston County official 2024 general results, elected", SRC_2024)]),
    ]
    sd7 = [
        holder("WY-RANKIN-CURTIS", role="Chairman", href=href_for("WY-RANKIN-CURTIS", "2024-local"),
               ballot_name="CURTIS RANKIN", term_end="January 2029", sort_key="G02A",
               sources=[src("Town of Upton boards page, WCSD #7 Board-Elected (Chairman)", SRC_SD7_UPTON),
                        src("Weston County official 2024 general results, elected", SRC_2024)],
               notes="The district site at weston7.org/page/board-of-education/ did not list member names in the static HTML that was fetched."),
        holder("WY-WHITE-DIANA", href=href_for("WY-WHITE-DIANA", "2024-local"),
               ballot_name="DIANA WHITE", term_end="January 2029", sort_key="G02B",
               sources=[src("Town of Upton boards page, WCSD #7 Board-Elected", SRC_SD7_UPTON),
                        src("Weston County official 2024 general results, elected", SRC_2024)]),
        holder("WY-MILLER-TY", href=href_for("WY-MILLER-TY", "2026-local"),
               ballot_name="TY MILLER", term_end="January 2031", sort_key="G02C",
               sources=[src("Town of Upton boards page, WCSD #7 Board-Elected", SRC_SD7_UPTON),
                        src("Weston County official 2022 general results, elected", SRC_2022),
                        src("Weston County official 2026 general results, re-elected", SRC_2026)]),
        holder("WY-MITCHELL-MARK", href=href_for("WY-MITCHELL-MARK", "2026-local"),
               ballot_name="MARK MITCHELL", term_end="January 2031", sort_key="G02D",
               sources=[src("Town of Upton boards page, WCSD #7 Board-Elected", SRC_SD7_UPTON),
                        src("Weston County official 2022 general results, elected", SRC_2022),
                        src("Weston County official 2026 general results, re-elected", SRC_2026)]),
        holder("WY-MILLS-JUSTIN", href=href_for("WY-MILLS-JUSTIN", "2026-local"),
               ballot_name="JUSTIN D. MILLS", term_end="January 2031", sort_key="G02E",
               sources=[src("Town of Upton boards page, WCSD #7 Board-Elected (Justin Mills)", SRC_SD7_UPTON),
                        src("Weston County official 2022 general results, elected as JUSTIN MILLS", SRC_2022),
                        src("Weston County official 2026 general results, re-elected as JUSTIN D. MILLS", SRC_2026)]),
    ]
    return {
        "id": "schools",
        "title": "School boards",
        "sort_key": "G",
        "offices": [
            office("Weston County School District #1 Board, at-large", sd1, sort_key="G01",
                   note="Nine members. The official board page matches the 2022 and 2024 general winners. Four 2022 seats were on the 2026 ballot; Dana Gordon leaves in January 2027 and Scott W. Johnson, a 2026 winner, takes office. The other three 2026 winners were already on the board and were re-elected."),
            office("Weston County School District #7 Board, at-large", sd7, sort_key="G02",
                   note="Five members. The Upton boards page matches the 2022 and 2024 general winners. The three 2022 members were all re-elected in 2026, so the board does not change in January 2027."),
        ],
    }


def special_group():
    return {
        "id": "special-districts",
        "title": "Special districts",
        "sort_key": "H",
        "note": "No elected special-district board appeared on the official Weston County 2022, 2024, or 2026 general results. A hospital-district mill levy was on the 2024 ballot as a proposition, not a candidate race.",
        "offices": [],
    }


def judicial_county_group():
    # Judges who appeared on the Weston 2026 ballot and who sit on a district or circuit court
    # that is not statewide. Statewide justices and the chancery judge live in shared/judicial-statewide.json.
    return {
        "id": "judicial",
        "title": "Judicial retention (district and circuit)",
        "sort_key": "J3",
        "note": "These judges appeared on the Weston County 2026 general ballot. Retention figures are the official Weston totals. Supreme Court justices and the Chancery Court judge are in the shared statewide judicial file.",
        "offices": [
            office("District Judge, 6th Judicial District", [
                holder("WY-MCGRADY-MICHAEL", href=judge_href("WY-MCGRADY-MICHAEL"),
                       ballot_name="MICHAEL J. MCGRADY", sort_key="J03",
                       sources=[src("Wyoming Judicial Branch, District Court, 6th Judicial District, Weston County", SRC_COURTS_D6),
                                src("Weston County official 2026 general results, retained", SRC_2026)],
                       retention={"year": 2026, "yes": 1478, "no": 642, "yes_pct": "69.72%", "no_pct": "30.28%",
                                  "result": "retained", "source": SRC_2026},
                       notes="Appointed July 2024 (Wyoming Judicial Branch). The same judge is listed for Campbell, Crook, and Weston in the 6th Judicial District.")
            ], sort_key="J03"),
            office("Circuit Judge, 6th Judicial District", [
                holder("WY-STEWARD-GREG", href=judge_href("WY-STEWARD-GREG"),
                       ballot_name="GREG R. STEWARD", sort_key="J05",
                       sources=[src("Wyoming Judicial Branch, Circuit Court of the 6th Judicial District, Campbell County (Gillette)", SRC_COURTS_C6),
                                src("Weston County official 2026 general results, retained", SRC_2026)],
                       retention={"year": 2026, "yes": 1493, "no": 616, "yes_pct": "70.79%", "no_pct": "29.21%",
                                  "result": "retained", "source": SRC_2026},
                       notes="The Judicial Branch lists this court as Circuit Court of the 6th Judicial District, Campbell County (Gillette). He appeared on the Weston County 2026 general ballot. The Weston circuit court page lists Judge Lynda R. Bush, who was retained in 2024 and was not on the 2026 ballot.")
            ], sort_key="J05"),
        ],
    }


def judicial_statewide():
    return {
        "title": "Statewide judicial officers",
        "as_of": "2026-11-23",
        "intro": "These judicial officers serve every county. Retention figures shown with each name are the official Weston County 2026 general totals.",
        "groups": [
            {
                "id": "supreme-court",
                "title": "Wyoming Supreme Court",
                "sort_key": "J1",
                "offices": [
                    office("Justice of the Wyoming Supreme Court", [
                        holder("WY-HILL-BRIDGET", href=judge_href("WY-HILL-BRIDGET"),
                               ballot_name="BRIDGET HILL", sort_key="J01",
                               sources=[src("Wyoming Judicial Branch, Supreme Court, Justice Bridget Hill", SRC_COURTS_SC),
                                        src("Weston County official 2026 general results, retained", SRC_2026)],
                               retention={"year": 2026, "yes": 1465, "no": 697, "yes_pct": "67.76%", "no_pct": "32.24%",
                                          "result": "retained", "source": SRC_2026, "county": "Weston"},
                               notes="Appointed May 2025 (Wyoming Judicial Branch). Stood for retention in November 2026."),
                        holder("WY-JAROSH-ROBERT", href=judge_href("WY-JAROSH-ROBERT"),
                               ballot_name="ROBERT C. JAROSH", sort_key="J02",
                               sources=[src("Wyoming Judicial Branch, Supreme Court, Justice Robert C. Jarosh", SRC_COURTS_SC),
                                        src("Weston County official 2026 general results, retained", SRC_2026)],
                               retention={"year": 2026, "yes": 1426, "no": 700, "yes_pct": "67.07%", "no_pct": "32.93%",
                                          "result": "retained", "source": SRC_2026, "county": "Weston"},
                               notes="Appointed March 2024 and sworn in March 27, 2024 (Wyoming Judicial Branch). Stood for retention in November 2026."),
                    ], layout="heading-then-names", sort_key="J1"),
                ],
            },
            {
                "id": "chancery-court",
                "title": "Chancery Court",
                "sort_key": "J2",
                "offices": [
                    office("Chancery Court Judge", [
                        holder("WY-BURNINGHAM-BEN", href=judge_href("WY-BURNINGHAM-BEN"),
                               ballot_name="BEN BURNINGHAM", sort_key="J04",
                               sources=[src("Wyoming Judicial Branch, Chancery Court, Honorable Benjamin M. Burningham", SRC_COURTS_CH),
                                        src("Weston County official 2026 general results, retained as BEN BURNINGHAM", SRC_2026)],
                               retention={"year": 2026, "yes": 1471, "no": 624, "yes_pct": "70.21%", "no_pct": "29.79%",
                                          "result": "retained", "source": SRC_2026, "county": "Weston"},
                               notes="Appointed January 2025 (Wyoming Judicial Branch). The 2026 Weston ballot used Ben Burningham."),
                    ], sort_key="J2"),
                ],
            },
        ],
    }

CAND_COLS = [
    "cycle","county","office","office_normalized","seat_or_term","vote_for","party",
    "candidate_ballot_name","person_id","incumbent","primary_votes","primary_vote_pct",
    "primary_result","primary_status","general_votes","general_vote_pct","general_result",
    "general_status","winner","writein_total_primary","writein_total_general",
    "source_roster_url","source_primary_results_url","source_general_results_url",
    "retrieved_date","notes","votes_named_plus_writeins_primary","pdf_total_votes_cast_primary",
    "check_ok_primary","votes_named_plus_writeins_general","pdf_total_votes_cast_general",
    "check_ok_general","phase","jurisdiction","office_kind","yes_votes","no_votes","yes_pct","no_pct",
]

JUD_COLS = CAND_COLS  # same plus yes/no already included


def write_csv(path, rows, cols):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            out = {c: r.get(c, "") for c in cols}
            w.writerow(out)


def write_elections():
    by = {}
    for r in ELECTIONS:
        year, kind = r["cycle"], r["office_kind"]
        if kind == "judicial_retention":
            key = (year, "judicial_retention")
        elif kind == "school_board":
            key = (year, "school")
        else:
            key = (year, "municipal")
        by.setdefault(key, []).append(r)
    written = []
    for (year, kind), rows in sorted(by.items()):
        fn = {"municipal": f"municipal_{year}.csv", "school": f"school_{year}.csv",
              "judicial_retention": f"judicial_retention_{year}.csv"}[kind]
        path = LOCAL / year / fn
        write_csv(path, rows, CAND_COLS)
        written.append(path)
    return written


def write_people():
    PEOPLE.mkdir(parents=True, exist_ok=True)
    cols = ["person_id","slug","display_name","sort_name","first","middle","last","suffix",
            "aliases","name_status","sources","notes","minted"]
    rows = []
    for p in PERSONS:
        rows.append({
            "person_id": p["person_id"], "slug": p["slug"], "display_name": p["display_name"],
            "sort_name": f"{p['last']}, {p['first']}".strip(", "),
            "first": p["first"], "middle": p.get("middle",""), "last": p["last"], "suffix": "",
            "aliases": p.get("aliases",""),
            "name_status": "minted" if p.get("minted") else "existing",
            "sources": "Weston County official general results 2022-2026; official city, town, school, or court pages as recorded in offices_held_additions.csv",
            "notes": "Added for 114 County Officeholders (Weston). Existing IDs were reused when already in the name index.",
            "minted": "Y" if p.get("minted") else "N",
        })
    write_csv(PEOPLE / "people_additions.csv", rows, cols)

    oh_cols = ["person_id","office","office_level","jurisdiction","county","district","party",
               "start_date","end_date","status","source","role"]
    oh = []
    # Filled from officeholder groups after we build them, in patch_and_write_json
    write_csv(PEOPLE / "offices_held_additions.csv", [], oh_cols)  # placeholder, rewritten later
    cand_cols = ["person_id","year","election","office","office_level","county","district",
                 "district_counties","precinct","party","votes","vote_pct","result","incumbent",
                 "write_in","name_on_ballot","source"]
    cand_rows = []
    for r in ELECTIONS:
        if r["candidate_ballot_name"] == "Write-In Totals":
            continue
        if not r.get("person_id"):
            continue
        level = {"mayor":"municipal","city_council":"municipal","town_council":"municipal",
                 "school_board":"school","judicial_retention":"judicial"}.get(r["office_kind"], r["office_kind"])
        votes = r.get("general_votes") or ""
        if r["office_kind"] == "judicial_retention":
            votes = r.get("yes_votes") or ""
        cand_rows.append({
            "person_id": r["person_id"], "year": r["cycle"], "election": "general",
            "office": r["office_normalized"] or r["office"], "office_level": level,
            "county": r["county"], "district": r.get("jurisdiction",""), "district_counties": "",
            "precinct": "", "party": r.get("party",""), "votes": votes,
            "vote_pct": r.get("general_vote_pct") or r.get("yes_pct") or "",
            "result": r.get("general_result",""), "incumbent": r.get("incumbent",""),
            "write_in": "", "name_on_ballot": r["candidate_ballot_name"],
            "source": r.get("source_general_results_url",""),
        })
    write_csv(PEOPLE / "candidacies_additions.csv", cand_rows, cand_cols)
    return oh_cols


def flatten_holders(groups):
    rows = []
    for g in groups:
        for o in g.get("offices") or []:
            for h in o.get("holders") or []:
                rows.append((g, o, h))
                if h.get("succeeding"):
                    rows.append((g, o, {**h["succeeding"], "_succeeding": True}))
    return rows


def write_offices_held(oh_cols, extra_groups, shared):
    rows = []
    groups = list(extra_groups) + list((shared or {}).get("groups") or [])
    for g, o, h in flatten_holders(groups):
        pid = h.get("person_id")
        if not pid:
            continue
        level = {"municipal":"municipal","schools":"school","judicial":"judicial",
                 "supreme-court":"judicial","chancery-court":"judicial"}.get(g["id"], g["id"])
        end = h.get("term_end") or ""
        status = "elect" if h.get("_succeeding") else "current"
        rows.append({
            "person_id": pid, "office": o["office"], "office_level": level,
            "jurisdiction": o["office"], "county": "Weston", "district": "",
            "party": h.get("party",""), "start_date": "", "end_date": end,
            "status": status, "source": "; ".join(s.get("url") or s.get("label","") for s in h.get("sources") or []),
            "role": h.get("role",""),
        })
    write_csv(PEOPLE / "offices_held_additions.csv", rows, oh_cols)


def patch_weston_json(extra_groups):
    path = DATA / "weston.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    # Drop any previously seeded copies of the new groups, then append.
    keep_ids = {"state-senate", "state-house", "county", "precincts"}
    data["groups"] = [g for g in data["groups"] if g["id"] in keep_ids]
    data["groups"].extend(extra_groups)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


PROFILE_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="cand-local">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} — Profile — WyoVote</title>
    <meta name="description" content="{desc}">
    <link rel="icon" href="{root}assets/img/surveyor-icon.png" type="image/png">
    <link rel="stylesheet" href="{root}css/styles.css">
    <link rel="stylesheet" href="{root}assets/css/site.css">
    <link rel="stylesheet" href="{root}officials/profile.css">
  </head>
  <body class="pf cand-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header">
      <div class="wrap header-inner">
        <a class="brand" href="{root}index.html">
          <img src="{root}assets/img/surveyor-icon.png" alt="" width="135" height="152">
          <span class="site-name">WyoVote</span>
        </a>
        <nav class="site-nav" aria-label="Site">
          <ul>
            <li><a href="{root}index.html">Home</a></li>
            <li><a href="{root}candidates.html" aria-current="page">Candidates</a></li>
            <li><a href="{root}committees.html">Committees</a></li>
            <li><a href="{root}counties.html">Counties</a></li>
            <li><a href="{root}officials.html">Officials</a></li>
            <li><a href="{root}people/index.html">Name Index</a></li>
            <li><a href="{root}research.html">Research</a></li>
            <li><a href="{root}archive.html">Archive</a></li>
          </ul>
        </nav>
      </div>
    </header>
    <main id="main" class="profile">
      <div class="wrap">
        <p class="back-row"><a class="back-btn" href="{back_href}">← Back to Weston County</a></p>
        <section class="pf-head" aria-labelledby="h-name">
          <h1 id="h-name">{title}</h1>
          <p class="pf-sub">{subtitle}</p>
        </section>
        <p class="cand-blurb">{blurb}</p>
        {results}
        {research}
      </div>
    </main>
    <footer class="site-footer">
      <div class="wrap footer-inner">
        <nav aria-label="Footer">
          <ul class="footer-links">
            <li><a href="{root}about.html">About</a></li>
            <li><a href="{root}privacy.html">Privacy</a></li>
            <li><a href="{root}contact.html">Contact</a></li>
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
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def results_block(rows, sources):
    facts = "".join(f"<tr><th scope=\"row\">{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in rows)
    srcs = "".join(
        f'<li><a href="{esc(u)}">{esc(lab)}</a> <span class="ext">(leaves WyoVote)</span></li>'
        if u else f"<li>{esc(lab)}</li>"
        for lab, u in sources
    )
    return f'''        <section class="pf-card cand-research" aria-labelledby="h-results">
          <h2 id="h-results">Results</h2>
          <table class="cand-facts">{facts}</table>
          <div class="cand-sources-block">
            <h2 id="h-results-sources">Sources</h2>
            <ul class="cand-sources">{srcs}</ul>
          </div>
        </section>'''


def research_block(fields, sources):
    if not fields:
        return ""
    facts = "".join(
        f"<tr><th scope=\"row\">{esc(k)}</th><td>{v if v.startswith('<p>') else esc(v)}</td></tr>"
        for k, v in fields
    )
    srcs = "".join(
        f'<li><a href="{esc(u)}">{esc(lab)}</a> <span class="ext">(leaves WyoVote)</span></li>'
        if u else f"<li>{esc(lab)}</li>"
        for lab, u in sources
    )
    return f'''        <section class="pf-card cand-research" aria-labelledby="h-research">
          <h2 id="h-research">Research</h2>
          <table class="cand-facts">{facts}</table>
          <div class="cand-sources-block">
            <h2 id="h-sources">Sources</h2>
            <ul class="cand-sources">{srcs}</ul>
          </div>
        </section>'''


def profile_path_from_href(href):
    return ROOT / href


def collect_results_for(pid):
    rows, sources = [], []
    seen = set()
    for r in ELECTIONS:
        if r.get("person_id") != pid:
            continue
        if r["office_kind"] == "judicial_retention":
            label = f"{r['cycle']} general · {r['office']}"
            val = f"Retained, Yes {r['yes_votes']:,}, No {r['no_votes']:,} ({r.get('yes_pct')})"
        else:
            label = f"{r['cycle']} general · {r.get('jurisdiction') or ''} · {r['office_normalized']}"
            val = f"{r['general_result'].capitalize() if r.get('general_result') else ''}, {r.get('general_votes')} votes"
            if r.get("general_vote_pct"):
                val += f" ({r['general_vote_pct']})"
        rows.append((label.strip(" ·"), val))
        url = r.get("source_general_results_url")
        if url and url not in seen:
            seen.add(url)
            sources.append((f"Weston County official {r['cycle']} general results", url))
    return rows, sources


# People who get a new or enriched Profile page (current holders, elects, and 2026-retained judges).
PROFILE_PIDS = {
    "WY-OWENS-TYREL", "WY-VOSS-THOMAS", "WY-STEVESON-DON", "WY-MCCOLLEY-ANN",
    "WY-DOWNS-DAREN", "WY-KENNEY-CHRIS", "WY-BUTTS-JOHN", "WY-GUALTIERI-PAM", "WY-VOELKER-WYATT",
    "WY-TRANDAHL-NICK", "WY-KENNEDY-TY", "WY-NORMAN-JUSTIN", "WY-WATT-JOE", "WY-MCMILLAN-TIFFANY",
    "WY-ROTHLEUTNER-RICK", "WY-WOZNEY-KELLY",
    "WY-FITZWATER-BILLY", "WY-JENKINS-JASON", "WY-PRELL-JOE", "WY-MANN-TAVEGIA-DANA",
    "WY-BAU-PAUL", "WY-CRABTREE-SEAN", "WY-GORDON-DANA", "WY-MILLS-TYLER", "WY-PILLEN-SUSAN",
    "WY-JOHNSON-SCOTT",
    "WY-RANKIN-CURTIS", "WY-WHITE-DIANA", "WY-MILLER-TY", "WY-MITCHELL-MARK", "WY-MILLS-JUSTIN",
    "WY-HILL-BRIDGET", "WY-JAROSH-ROBERT", "WY-MCGRADY-MICHAEL", "WY-BURNINGHAM-BEN", "WY-STEWARD-GREG",
}

# Research blurbs kept to official titles and documented facts. No invented biography.
RESEARCH = {
    "WY-OWENS-TYREL": [("Residence", "Newcastle, Weston County"),
                       ("Occupation", "Mayor of Newcastle (listed on the official city government page, term labeled 2029)")],
    "WY-VOSS-THOMAS": [("Residence", "Newcastle, Weston County"),
                       ("Occupation", "Newcastle City Council president (official city government page, term labeled 2029)")],
    "WY-STEVESON-DON": [("Residence", "Newcastle, Weston County"),
                        ("Occupation", "Newcastle City Council member (official city government page); re-elected November 2026")],
    "WY-MCCOLLEY-ANN": [("Residence", "Newcastle, Weston County"),
                        ("Occupation", "Newcastle City Council member (official city government page, term labeled 2026)")],
    "WY-DOWNS-DAREN": [("Residence", "Newcastle, Weston County"),
                       ("Occupation", "Newcastle City Council member (official city government page, term labeled 2029). The city site also spells the first name Darren in one committee list; the 2024 ballot used DAREN L. DOWNS.")],
    "WY-KENNEY-CHRIS": [("Residence", "Newcastle, Weston County"),
                        ("Occupation", "Newcastle City Council member (official city government page, term labeled 2029)")],
    "WY-BUTTS-JOHN": [("Residence", "Newcastle, Weston County"),
                      ("Occupation", "Newcastle City Council member (official city government page, term labeled 2026)")],
    "WY-GUALTIERI-PAM": [("Residence", "Newcastle, Weston County"),
                         ("Background", "<p>Ran for Newcastle mayor in the November 2024 general election and was elected to the Newcastle City Council in the November 2026 general election.</p>")],
    "WY-VOELKER-WYATT": [("Residence", "Newcastle, Weston County"),
                         ("Background", "<p>Elected to the Newcastle City Council in the November 2026 general election.</p>")],
    "WY-TRANDAHL-NICK": [("Residence", "Upton, Weston County"),
                         ("Occupation", "Mayor of Upton (official town government page, term labeled 2026). October 13, 2026 town minutes list him as Mayor Nicholas Trandahl.")],
    "WY-KENNEDY-TY": [("Residence", "Upton, Weston County"),
                      ("Background", "<p>Elected Upton mayor in the November 2026 general election. October 13, 2026 town minutes list him as Assistant Fire Chief of the Upton Volunteer Fire Department, present at that meeting.</p>")],
    "WY-NORMAN-JUSTIN": [("Residence", "Upton, Weston County"),
                         ("Occupation", "Upton Town Council member and vice mayor (official town government page, term labeled 2028)")],
    "WY-WATT-JOE": [("Residence", "Upton, Weston County"),
                    ("Occupation", "Upton Town Council member, Water &amp; Sewer commissioner (official town government page); re-elected November 2026")],
    "WY-MCMILLAN-TIFFANY": [("Residence", "Upton, Weston County"),
                            ("Occupation", "Upton Town Council member (official town government page, term labeled 2026)")],
    "WY-ROTHLEUTNER-RICK": [("Residence", "Upton, Weston County"),
                            ("Occupation", "Upton Town Council member, Streets &amp; Sanitation commissioner (official town government page, term labeled 2028)")],
    "WY-WOZNEY-KELLY": [("Residence", "Upton, Weston County"),
                        ("Background", "<p>Elected to the Upton Town Council in the November 2026 general election.</p>")],
    "WY-FITZWATER-BILLY": [("Residence", "Weston County"),
                           ("Occupation", "Weston County School District #1 Board Chair (official board members page)")],
    "WY-JENKINS-JASON": [("Residence", "Weston County"),
                         ("Occupation", "Weston County School District #1 Board Vice-Chair (official board members page); also a Republican precinct committeeman for Weston precinct 5-3")],
    "WY-PRELL-JOE": [("Residence", "Weston County"),
                     ("Occupation", "Weston County School District #1 Board Clerk (official board members page)")],
    "WY-MANN-TAVEGIA-DANA": [("Residence", "Weston County"),
                             ("Occupation", "Weston County School District #1 Board Treasurer (official board members page)")],
    "WY-BAU-PAUL": [("Residence", "Weston County"),
                    ("Occupation", "Weston County School District #1 board member (official board members page)")],
    "WY-CRABTREE-SEAN": [("Residence", "Weston County"),
                         ("Occupation", "Weston County School District #1 board member (official board members page); re-elected November 2026")],
    "WY-GORDON-DANA": [("Residence", "Weston County"),
                       ("Occupation", "Weston County School District #1 board member (official board members page)")],
    "WY-MILLS-TYLER": [("Residence", "Weston County"),
                       ("Occupation", "Weston County School District #1 board member (official board members page)")],
    "WY-PILLEN-SUSAN": [("Residence", "Weston County"),
                        ("Occupation", "Weston County School District #1 board member (official board members page)")],
    "WY-JOHNSON-SCOTT": [("Residence", "Weston County"),
                         ("Occupation", "Weston County School District #1 board member, official-elect (November 2026 general); also a Republican precinct committeeman in Weston County")],
    "WY-RANKIN-CURTIS": [("Residence", "Weston County"),
                         ("Occupation", "Weston County School District #7 Board Chairman (Town of Upton boards page); also a Republican precinct committeeman for Weston precinct 3-1")],
    "WY-WHITE-DIANA": [("Residence", "Weston County"),
                       ("Occupation", "Weston County School District #7 board member (Town of Upton boards page)")],
    "WY-MILLER-TY": [("Residence", "Weston County"),
                     ("Occupation", "Weston County School District #7 board member (Town of Upton boards page); re-elected November 2026")],
    "WY-MITCHELL-MARK": [("Residence", "Weston County"),
                         ("Occupation", "Weston County School District #7 board member (Town of Upton boards page); re-elected November 2026")],
    "WY-MILLS-JUSTIN": [("Residence", "Weston County"),
                        ("Occupation", "Weston County School District #7 board member (Town of Upton boards page); re-elected November 2026")],
    "WY-HILL-BRIDGET": [("Occupation", "Justice of the Wyoming Supreme Court"),
                        ("Background", "<p>Appointed to the Wyoming Supreme Court in May 2025 by Governor Mark Gordon. The Judicial Branch biography states that she previously served as Wyoming Attorney General (2019–2025), Director of the Office of State Lands and Investments (2013–2019), and as an assistant attorney general (2005–2013), and that she served as a law clerk to Wyoming Supreme Court Justices Larry Lehman and Michael Golden. She stood for retention in November 2026 and was retained in Weston County official results.</p>")],
    "WY-JAROSH-ROBERT": [("Occupation", "Justice of the Wyoming Supreme Court"),
                         ("Background", "<p>Appointed to the Wyoming Supreme Court by Governor Mark Gordon and sworn in on March 27, 2024, according to the Judicial Branch biography. That biography states he was previously in private practice in Cheyenne and Denver and served as a law clerk to Federal Magistrate Judge William C. Beaman. He stood for retention in November 2026 and was retained in Weston County official results.</p>")],
    "WY-MCGRADY-MICHAEL": [("Occupation", "District Judge, 6th Judicial District (Campbell, Crook, and Weston counties)"),
                           ("Background", "<p>The Wyoming Judicial Branch lists him as district judge for the 6th Judicial District, including Weston County, appointed July 2024. He stood for retention in November 2026 and was retained in Weston County official results.</p>")],
    "WY-BURNINGHAM-BEN": [("Occupation", "Chancery Court Judge"),
                          ("Background", "<p>The Wyoming Judicial Branch lists Honorable Benjamin M. Burningham on the Chancery Court, appointed January 2025. The 2026 Weston ballot used the name Ben Burningham. He was retained in Weston County official results.</p>")],
    "WY-STEWARD-GREG": [("Occupation", "Circuit Judge, 6th Judicial District, Campbell County (Gillette)"),
                        ("Background", "<p>The Wyoming Judicial Branch lists him on the Circuit Court of the 6th Judicial District, Campbell County (Gillette), appointed July 2025. He appeared on the Weston County 2026 general ballot and was retained in Weston County official results.</p>")],
}

RESEARCH_SOURCES = {
    "WY-OWENS-TYREL": [("City of Newcastle Mayor & City Council", SRC_NEWC), ("Weston County official 2024 general results", SRC_2024)],
    "WY-VOSS-THOMAS": [("City of Newcastle Mayor & City Council", SRC_NEWC), ("Weston County official 2024 general results", SRC_2024)],
    "WY-STEVESON-DON": [("City of Newcastle Mayor & City Council", SRC_NEWC), ("Weston County official 2022 general results", SRC_2022), ("Weston County official 2026 general results", SRC_2026)],
    "WY-MCCOLLEY-ANN": [("City of Newcastle Mayor & City Council", SRC_NEWC), ("Weston County official 2022 general results", SRC_2022)],
    "WY-DOWNS-DAREN": [("City of Newcastle Mayor & City Council", SRC_NEWC), ("Weston County official 2024 general results", SRC_2024)],
    "WY-KENNEY-CHRIS": [("City of Newcastle Mayor & City Council", SRC_NEWC), ("Weston County official 2024 general results", SRC_2024)],
    "WY-BUTTS-JOHN": [("City of Newcastle Mayor & City Council", SRC_NEWC), ("Weston County official 2022 and 2026 general results", SRC_2026)],
    "WY-GUALTIERI-PAM": [("Weston County official 2024 general results", SRC_2024), ("Weston County official 2026 general results", SRC_2026)],
    "WY-VOELKER-WYATT": [("Weston County official 2026 general results", SRC_2026)],
    "WY-TRANDAHL-NICK": [("Town of Upton City Government", SRC_UPTON), ("Weston County official 2022 general results", SRC_2022)],
    "WY-KENNEDY-TY": [("Weston County official 2026 general results", SRC_2026), ("Town of Upton October 13, 2026 minutes", "https://townofupton.com/_pdfs/2026/MINUTES%20OF%20THE%20October%2013,%202026%20Regular%20Meeting.pdf")],
    "WY-NORMAN-JUSTIN": [("Town of Upton City Government", SRC_UPTON), ("Weston County official 2024 general results", SRC_2024)],
    "WY-WATT-JOE": [("Town of Upton City Government", SRC_UPTON), ("Weston County official 2022 and 2026 general results", SRC_2026)],
    "WY-MCMILLAN-TIFFANY": [("Town of Upton City Government", SRC_UPTON), ("Weston County official 2022 and 2026 general results", SRC_2026)],
    "WY-ROTHLEUTNER-RICK": [("Town of Upton City Government", SRC_UPTON), ("Weston County official 2024 general results", SRC_2024)],
    "WY-WOZNEY-KELLY": [("Weston County official 2026 general results", SRC_2026)],
    "WY-FITZWATER-BILLY": [("WCSD #1 official board members page", SRC_SD1), ("Weston County official 2024 general results", SRC_2024)],
    "WY-JENKINS-JASON": [("WCSD #1 official board members page", SRC_SD1), ("Weston County official 2022 and 2026 general results", SRC_2026)],
    "WY-PRELL-JOE": [("WCSD #1 official board members page", SRC_SD1), ("Weston County official 2022 and 2026 general results", SRC_2026)],
    "WY-MANN-TAVEGIA-DANA": [("WCSD #1 official board members page", SRC_SD1), ("Weston County official 2024 general results", SRC_2024)],
    "WY-BAU-PAUL": [("WCSD #1 official board members page", SRC_SD1), ("Weston County official 2024 general results", SRC_2024)],
    "WY-CRABTREE-SEAN": [("WCSD #1 official board members page", SRC_SD1), ("Weston County official 2022 and 2026 general results", SRC_2026)],
    "WY-GORDON-DANA": [("WCSD #1 official board members page", SRC_SD1), ("Weston County official 2022 general results", SRC_2022)],
    "WY-MILLS-TYLER": [("WCSD #1 official board members page", SRC_SD1), ("Weston County official 2024 general results", SRC_2024)],
    "WY-PILLEN-SUSAN": [("WCSD #1 official board members page", SRC_SD1), ("Weston County official 2024 general results", SRC_2024)],
    "WY-JOHNSON-SCOTT": [("Weston County official 2026 general results", SRC_2026)],
    "WY-RANKIN-CURTIS": [("Town of Upton boards page, WCSD #7", SRC_SD7_UPTON), ("Weston County official 2024 general results", SRC_2024)],
    "WY-WHITE-DIANA": [("Town of Upton boards page, WCSD #7", SRC_SD7_UPTON), ("Weston County official 2024 general results", SRC_2024)],
    "WY-MILLER-TY": [("Town of Upton boards page, WCSD #7", SRC_SD7_UPTON), ("Weston County official 2022 and 2026 general results", SRC_2026)],
    "WY-MITCHELL-MARK": [("Town of Upton boards page, WCSD #7", SRC_SD7_UPTON), ("Weston County official 2022 and 2026 general results", SRC_2026)],
    "WY-MILLS-JUSTIN": [("Town of Upton boards page, WCSD #7", SRC_SD7_UPTON), ("Weston County official 2022 and 2026 general results", SRC_2026)],
    "WY-HILL-BRIDGET": [("Wyoming Judicial Branch, Supreme Court", SRC_COURTS_SC), ("Weston County official 2026 general results", SRC_2026)],
    "WY-JAROSH-ROBERT": [("Wyoming Judicial Branch, Supreme Court", SRC_COURTS_SC), ("Weston County official 2026 general results", SRC_2026)],
    "WY-MCGRADY-MICHAEL": [("Wyoming Judicial Branch, 6th Judicial District, Weston County", SRC_COURTS_D6), ("Weston County official 2026 general results", SRC_2026)],
    "WY-BURNINGHAM-BEN": [("Wyoming Judicial Branch, Chancery Court", SRC_COURTS_CH), ("Weston County official 2026 general results", SRC_2026)],
    "WY-STEWARD-GREG": [("Wyoming Judicial Branch, Circuit Court, 6th JD, Campbell County", SRC_COURTS_C6), ("Weston County official 2026 general results", SRC_2026)],
}

HREF_BY_PID = {}


def register_hrefs(groups, shared):
    for g in list(groups) + list((shared or {}).get("groups") or []):
        for o in g.get("offices") or []:
            for h in o.get("holders") or []:
                if h.get("person_id") and h.get("href"):
                    HREF_BY_PID[h["person_id"]] = h["href"]
                if h.get("succeeding") and h["succeeding"].get("person_id") and h["succeeding"].get("href"):
                    HREF_BY_PID[h["succeeding"]["person_id"]] = h["succeeding"]["href"]


def write_profiles():
    written = []
    for pid in sorted(PROFILE_PIDS):
        href = HREF_BY_PID.get(pid)
        if not href:
            # judges or others
            if pid.startswith("WY-HILL") or pid.startswith("WY-JAROSH") or pid.startswith("WY-MCGRADY") or pid.startswith("WY-BURNINGHAM") or pid.startswith("WY-STEWARD"):
                href = judge_href(pid)
            else:
                continue
        path = profile_path_from_href(href)
        path.parent.mkdir(parents=True, exist_ok=True)
        p = P[pid]
        res_rows, res_src = collect_results_for(pid)
        research = RESEARCH.get(pid) or [("Residence", "Weston County"),
                                         ("Background", "<p>Public information found for this Profile is limited to official election results and the official officeholder roster.</p>")]
        rsrc = RESEARCH_SOURCES.get(pid) or res_src
        is_judge = href.startswith("officials/judges/")
        depth = 3 if href.startswith("candidates/") else 2 if is_judge else 3
        # href like candidates/2026-local/c/name.html -> ../../../
        # officials/judges/name.html -> ../../
        root = "../" * (len(Path(href).parts) - 1)
        back = f"{root}counties/weston.html"
        subtitle = "Profile · Judge" if is_judge else (
            "Profile · 2026 Local" if "2026-local" in href else
            "Profile · 2024 Local" if "2024-local" in href else
            "Profile · 2022 Local" if "2022-local" in href else "Profile")
        blurb_bits = [p["display_name"]]
        if res_rows:
            blurb_bits.append(res_rows[-1][0] + ": " + res_rows[-1][1] + ".")
        html = PROFILE_TEMPLATE.format(
            title=esc(p["display_name"]), desc=esc(" ".join(blurb_bits)[:300]),
            root=root, back_href=back, subtitle=esc(subtitle),
            blurb=esc(" ".join(blurb_bits)),
            results=results_block(res_rows, res_src) if res_rows else "",
            research=research_block(research, rsrc),
        )
        path.write_text(html, encoding="utf-8")
        written.append(path)
    return written


def write_schema_notes():
    path = DATA / "SCHEMA.md"
    text = path.read_text(encoding="utf-8")
    marker = "## Additional office types (municipal, schools, special districts, judicial)"
    block = f'''
{marker}

Added for the 114 County Officeholders report (Weston first; structure ready for all 23 counties).

Optional groups may appear in a county file after Precincts, in this order:

| Group `id` | Title | What it holds |
|---|---|---|
| `municipal` | Municipal offices | Elected city and town offices (mayor, council). Use `jurisdiction` in the election CSVs (city or town name). |
| `schools` | School boards | Elected school-district boards. |
| `special-districts` | Special districts | Elected special-district boards, when an official results source lists them. If none appear, the group may be present with `offices: []` and a `note`. Ballot questions (mill levies, taxes) are not officeholders. |
| `judicial` | Judicial retention (district and circuit) | Judges who appeared on that county's ballot and sit on a district or circuit court. |

Statewide judicial officers (Wyoming Supreme Court, Chancery Court) serve every county and live once in `shared/judicial-statewide.json`, in the same group shape as `shared/federal-statewide.json`. A county report includes that shared file plus the county `judicial` group. Retention figures may be stored on a holder as `retention` (`year`, `yes`, `no`, `yes_pct`, `no_pct`, `result`, `source`, optional `county`).

New optional holder fields, used when known: `person_id` (WY-LAST-FIRST), `sort_key` (alphanumeric 0-9A-Z), `term_end`, `retention`. Party is omitted or set to empty for nonpartisan contests (municipal, school, judicial); do not invent a party.

Election results for these offices are not added to Phase 1 `county_offices_YYYY.csv`. They live in:

| File | Role |
|---|---|
| `tools/local-data/YYYY/municipal_YYYY.csv` | City and town candidates, same core columns as Phase 2, plus `person_id` |
| `tools/local-data/YYYY/school_YYYY.csv` | School-board candidates |
| `tools/local-data/YYYY/judicial_retention_YYYY.csv` | Retention contests; uses `yes_votes` / `no_votes` |
| `data/people/people_additions.csv` | Person records (existing IDs reused; new IDs minted) |
| `data/people/offices_held_additions.csv` | Current and incoming offices |
| `data/people/candidacies_additions.csv` | General-election candidacies |

Weston is populated. Other counties can drop in the same groups when their official rosters are compiled; do not invent names. If a seat cannot be confirmed, use `Not yet collected`.

'''
    if marker in text:
        text = text.split(marker)[0].rstrip() + "\n" + block
    else:
        text = text.rstrip() + "\n" + block
    path.write_text(text, encoding="utf-8")
    readme = PEOPLE / "README.md"
    readme.write_text(
        "# Person and office additions (114 County Officeholders)\n\n"
        "These CSVs extend the standard person-ID (`WY-LAST-FIRST`), offices-held, and candidacy tables "
        "for municipal, school-board, and judicial officers compiled for Weston County. "
        "Existing name-index IDs are reused. Minted IDs are flagged in `people_additions.csv`. "
        "This folder is on the 114 work branch only; it is not merged to main in this step.\n",
        encoding="utf-8",
    )


def write_local_schema():
    path = LOCAL / "LOCAL_OFFICES.md"
    path.write_text(
        """# Municipal, school, and judicial election files

These files extend the local-election collection beyond Phase 1 county offices.
They use the same core candidate columns as `county_offices_YYYY.csv` and Phase 2 municipal files,
plus `person_id`, `jurisdiction`, `office_kind`, and, for retention contests, `yes_votes` / `no_votes`.

`office_normalized` values: `Mayor`, `City Council`, `Town Council`, `School Board`,
`Supreme Court Retention`, `District Judge Retention`, `Circuit Judge Retention`, `Chancery Judge Retention`.

`office_kind` values: `mayor`, `city_council`, `town_council`, `school_board`, `judicial_retention`.

Weston County is populated for 2022, 2024, and 2026 (plus 2022 and 2024 judicial rows as historical results).
The same filenames are ready for the other 22 counties when official results are keyed. Do not invent names.

See `data/county_officials/SCHEMA.md` for the officeholder JSON groups that these files feed.
""",
        encoding="utf-8",
    )


def main():
    extra = [municipal_group(), schools_group(), special_group(), judicial_county_group()]
    shared = judicial_statewide()
    (DATA / "shared" / "judicial-statewide.json").write_text(
        json.dumps(shared, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    patch_weston_json(extra)
    write_elections()
    oh_cols = write_people()
    write_offices_held(oh_cols, extra, shared)
    write_schema_notes()
    write_local_schema()
    register_hrefs(extra, shared)
    paths = write_profiles()
    print("seeded Weston local offices")
    print(" profiles", len(paths))
    print(" election rows", len(ELECTIONS))
    print(" persons", len(PERSONS))


if __name__ == "__main__":
    main()
