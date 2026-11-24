"""Canonical live legislative office notes for 114 county reports.

apply_to_groups() is called from each county update_*_json (and the
Weston history builder) just before the live JSON is written, so a
history rebuild reproduces the same Senate/House office notes.

Official SOS whole-district Totals and county shares for S01, H01,
S19, and H26 are taken from the official SOS statewide Senate and
House candidate summaries already archived under
/workspace/wyoleg/local-results/big-horn/<year>/ (the same official
statewide SOS PDFs). Two-column pages were cut at the next district
header so an adjacent district Total is not used.
"""

from __future__ import annotations

OFFICE_NOTES = {
    "lincoln": {
        "Senate District 14 (S14)": "Official 2024 SOS statewide Senate summary totals: Laura Taliaferro Pearson 8,025 (official ballot name). Official 2024 Lincoln clerk portion: 2,116. Also covers Sublette, Sweetwater, and Uinta. Official SOS district-wide totals are used for this multi-county seat.",
        "Senate District 16 (S16)": "Official 2024 SOS statewide Senate summary totals: Dan Dockstader 8,830. Official 2024 Lincoln clerk portion: Dockstader 7,355. Official 2024 Teton clerk portion: Dockstader 1,475. Also covers Teton County. Official SOS district-wide totals are used for this multi-county seat. Off-cycle in 2026.",
        "House District 18 (H18)": "Kenneth D. Roberts is the official 2026 general winner and takes office January 2027. Official 2026 SOS statewide House summary totals: Kenneth D. Roberts 2,691. Official 2026 Lincoln clerk portion: Roberts 1,412. Official Sweetwater portion: 879. Official Uinta portion: 400. Also covers Sweetwater and Uinta. Official SOS district-wide totals are used for this multi-county seat.",
        "House District 20 (H20)": "Albert Sommers is the official 2026 general winner and takes office January 2027. Official 2026 SOS statewide House summary totals: Albert Sommers 3,349 (official Lincoln clerk portion 154; official Sublette share 3,195). Official 2024 SOS statewide House summary totals: Mike Schmid 4,354 (official Lincoln clerk portion 279; official Sublette share 4,075). Also covers Sublette. Official SOS district-wide totals are used for this multi-county seat.",
        "House District 22 (H22)": "Official 2026 SOS statewide House summary totals: Andrew Byron 3,055. Official 2026 Lincoln clerk portion: Byron 1,656. Official 2024 SOS statewide House summary totals: Andrew Byron 4,189. Official 2024 Lincoln clerk portion: Andrew P. Byron 2,435. Also covers Teton County. Official SOS district-wide totals are used for this multi-county seat.",
    },
    "teton": {
        "Senate District 16 (S16)": "Official 2024 SOS statewide Senate summary totals: Dan Dockstader 8,830. Official 2024 Teton clerk portion: Dockstader 1,475 to 115 write-ins. Official 2024 Lincoln clerk portion: Dockstader 7,355. Also covers Lincoln County. Official SOS district-wide totals are used for this multi-county seat. Off-cycle in 2026.",
        "House District 22 (H22)": "Official 2026 SOS statewide House summary totals: Andrew Byron 3,055. Official 2026 Lincoln clerk portion: Byron 1,656. Official 2024 SOS statewide House summary totals: Andrew Byron 4,189. Official 2024 Lincoln clerk portion: Andrew P. Byron 2,435. Official 2022 SOS statewide House summary totals: Andrew Byron 2,235, Bob Strobel 1,681, with official 2022 Teton clerk portion Strobel 938, Byron 873. Also covers Lincoln County. Official SOS district-wide totals are used for this multi-county seat. Official Teton 2024 and 2026 portions were not separately keyed from the official Teton clerk in this history.",
    },
    "park": {
        "Senate District 19 (S19)": "Official 2022 SOS statewide Senate summary, Senate District 19: Dan Laursen (R) Total 5,538. Official Park share 2,901, official Big Horn share 2,637. Official 2026 SOS: R. J. Kost (R) Total 5,311. Official Park share 2,749, official Big Horn share 2,562, taking office January 2027. Also covers Big Horn. Official county shares are from official SOS and official clerk figures already used in the official Big Horn and Park histories. Official SOS district-wide totals are used for this multi-county seat.",
        "Senate District 20 (S20)": "Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Park share 834; official Washakie 3,442, Big Horn 1,475, Hot Springs 2,180, Fremont 305. Also covers Washakie, Big Horn, Hot Springs, and Fremont. Off-cycle in 2026. Official SOS district-wide totals are used for this multi-county seat.",
        "House District 26 (H26)": "Official 2026 SOS statewide House summary, House District 26: Dalton Banks (R) Total 2,557, Ralph Nieder-Westermann (D) 571. Official Park share Banks 256, Nieder-Westermann 33; official Big Horn share Banks 2,301, Nieder-Westermann 538. Re-elected. Official 2024 SOS: Dalton Banks (R) Total 3,942. Official Park share Banks 358; official Big Horn share Banks 3,584. Also covers Big Horn. Official SOS district-wide totals are used for this multi-county seat.",
        "House District 28 (H28)": "Official 2024 SOS statewide House summary, House District 28: John R. Winter (R) Total 3,986, Larry Alwin (D) 857. Official Park share 808. Official 2026 SOS: Allen Hogg (R) Total 3,309, Larry Alwin (D) 504; official Park share 692, taking office January 2027. Official SOS name John R. Winter is not combined with earlier official SOS name Nathan Winters. Also covers Big Horn, Fremont, and Hot Springs. Official SOS district-wide totals are used for this multi-county seat.",
    },
    "sheridan": {
        "Senate District 22 (S22)": "Official 2024 SOS statewide Senate summary, Senate District 22: Barry Crago (R) Total 8,599. Official Sheridan share 4,464; official Johnson share 4,135. Also covers Johnson County. Off-cycle in 2026. Official SOS district-wide totals are used for this multi-county seat.",
        "House District 40 (H40)": "Official 2026 SOS statewide House summary, House District 40: Marilyn Connolly (R) Total 3,677. Official Sheridan share 555; official Johnson share 3,122. Display name Marilyn F Connolly follows the existing official-history person. Official SOS district-wide totals are used for this multi-county seat.",
    },
    "sweetwater": {
        "Senate District 11 (S11)": "Bob Davis is the official 2026 general winner and takes office January 2027. Official 2026 SOS statewide Senate summary Total: Bob Davis (R) 3,615, Jim Wilson (D) 1,030, Don VanMatre (C) 297. Official Sweetwater share: Davis 535, Wilson 167, VanMatre 51. Official Carbon portion: Davis 3,080, Wilson 863, VanMatre 246. Official SOS district-wide totals are used for this multi-county seat.",
        "Senate District 14 (S14)": "Official 2024 SOS statewide Senate summary totals: Laura Taliaferro Pearson 8,025 (official ballot name). Official Sweetwater portion: 1,351. Also covers Lincoln, Sublette, and Uinta. Display name follows the site rule: Laura Taliaferro (formerly Pearson), person ID WY-PEARSON-LAURA.",
        "House District 15 (H15)": "Official 2026 SOS statewide House summary totals: Pamela Thayer 1,499, Cheryl Hulme 398. Official Sweetwater portion: Thayer 28, Hulme 6. Also covers Carbon County. Official SOS district-wide totals are used for this multi-county seat.",
        "House District 17 (H17)": "Elizabeth Bingham is the official 2026 general winner and takes office January 2027.",
        "House District 18 (H18)": "Kenneth D. Roberts is the official 2026 general winner and takes office January 2027. Official 2026 SOS statewide House summary totals: Roberts 2,691. Official Sweetwater portion: 879. Also covers Lincoln and Uinta. Official SOS district-wide totals are used for this multi-county seat.",
        "House District 47 (H47)": "Eamon O'Toole is the official 2026 general winner and takes office January 2027. Official 2026 SOS statewide House summary Total: Eamon O'Toole (R) 2,523. Official Sweetwater share: 603. Official Carbon portion: 1,920. Official 2024 SOS statewide House summary Total: Bob Davis (R) 3,488, James A. Wilson (D) 666. Official Sweetwater share: 918–205. Official Carbon portion: Davis 2,570, Wilson 461. Official SOS district-wide totals are used for this multi-county seat.",
        "House District 48 (H48)": "James Wamsley is the official 2026 general winner and takes office January 2027.",
        "House District 60 (H60)": "Tony Niemiec is the official 2026 general winner and takes office January 2027.",
    },
    "natrona": {
        "Senate District 2 (S02)": "Official 2024 SOS statewide Senate summary Total: Brian Boner (R) 7,712. Official Natrona share: 1,800. Official Converse portion: 5,912. After 2022 redistricting the official SOS county rows are Converse and Natrona (Platte is no longer in S02). Official SOS district-wide totals are used for this multi-county seat. Off-cycle in 2026.",
        "Senate District 27 (S27)": "Kevin Helling is the official 2026 general winner and takes office January 2027.",
        "Senate District 29 (S29)": "Lisa Engebretsen is the official 2026 general winner and takes office January 2027.",
        "House District 62 (H62)": "Official 2026 SOS statewide House summary Total: Kevin J. Campbell (R) 2,297. Official Natrona share: 1,122. Official Converse portion: 1,175. Official 2024 SOS statewide House summary Total: Kevin Campbell (R) 3,496. Official Natrona share: 1,764. Official Converse portion: 1,732. Also covers Converse County. Official SOS district-wide totals are used for this multi-county seat.",
    },
    "laramie": {
        "Senate District 6 (S06)": "Official 2026 SOS statewide Senate summary, Senate District 6: Taft Love (R) Total 6,142. Official Laramie share 3,199; official Platte share 2,943. Official 2024 SOS statewide Senate summary, Senate District 6: Darin Smith (R) Total 8,484. Official Laramie share 4,486; official Platte share 3,998. Official 2026 general names Taft Love as the S06 winner; January 2025–2026 snapshots keep Smith as the last official general-election holder, consistent with the official Platte history. Official SOS district-wide totals are used for this multi-county seat.",
        "House District 4 (H04)": "Official 2026 SOS statewide House summary totals: Jeremy Haroldson 2,533. Official Laramie County portion: 57. Also covers Platte County. Official SOS district-wide totals are used for this multi-county seat.",
    },
    "big-horn": {
        "Senate District 19 (S19)": "Official 2022 SOS statewide Senate summary, Senate District 19: Dan Laursen (R) Total 5,538. Official Big Horn share 2,637, official Park share 2,901. Official 2026 SOS: R. J. Kost (R) Total 5,311. Official Big Horn share 2,562 (official clerk abstract same), official Park share 2,749, taking office January 2027. Official SOS district-wide totals are used for this multi-county seat.",
        "Senate District 20 (S20)": "Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Big Horn share 1,475 (official 2024 clerk canvass same 1,475); official Washakie 3,442, Hot Springs 2,180, Park 834, Fremont 305. Covers Big Horn, Hot Springs, Fremont, Park, and Washakie. Off-cycle in 2026.",
        "House District 26 (H26)": "Official 2026 SOS statewide House summary, House District 26: Dalton Banks (R) Total 2,557, Ralph Nieder-Westermann (D) 571. Official Big Horn share Banks 2,301, Nieder-Westermann 538 (official clerk abstract same); official Park Banks 256, Nieder-Westermann 33. Re-elected. Official 2024 SOS: Dalton Banks (R) Total 3,942. Official Big Horn share Banks 3,584; official Park share 358. Official SOS district-wide totals are used for this multi-county seat.",
        "House District 27 (H27)": "Official 2026 SOS statewide House summary, House District 27: Martha Lawley (R) Total 2,700, Theresa Livingston (D) 490. Official Big Horn share Lawley 418, Livingston 60 (official clerk abstract same); official Washakie Lawley 2,282, Livingston 430. Also covers Washakie. Re-elected.",
        "House District 28 (H28)": "Official 2024 SOS statewide House summary, House District 28: John R. Winter (R) Total 3,986, Larry Alwin (D) 857. Official Big Horn share Winter 920, Alwin 85. Official 2026 SOS: Allen Hogg (R) Total 3,309, Larry Alwin (D) 504; official Big Horn share Hogg 655, Alwin 66, taking office January 2027. Official SOS name John R. Winter is not combined with earlier official SOS name Nathan Winters.",
    },
    "washakie": {
        "Senate District 20 (S20)": "Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Washakie share 3,442. Also covers Big Horn, Hot Springs, Fremont, and Park. Off-cycle in 2026.",
        "House District 27 (H27)": "Official 2026 SOS statewide House summary, House District 27: Martha Lawley (R) Total 2,700, Theresa Livingston (D) 490. Official Washakie share Lawley 2,282, Livingston 430. Also covers Big Horn.",
    },
    "campbell": {
        "Senate District 1 (S01)": "Official 2026 SOS statewide Senate summary, Senate District 1: Ogden Driskill (R) Total 5,107. Official Campbell share 1,858; official Crook share 2,313; official Weston share 936. Official 2022 SOS: Ogden Driskill (R) Total 4,785. Official Campbell share 1,937; official Crook share 2,029; official Weston share 819. Also covers Crook and Weston. Official SOS district-wide totals are used for this multi-county seat. Re-elected 2026; new term begins January 2027.",
    },
    "crook": {
        "Senate District 1 (S01)": "Official 2026 SOS statewide Senate summary, Senate District 1: Ogden Driskill (R) Total 5,107. Official Crook share 2,313; official Campbell share 1,858; official Weston share 936. Official 2022 SOS: Ogden Driskill (R) Total 4,785. Official Crook share 2,029; official Campbell share 1,937; official Weston share 819. Also covers Campbell and Weston. Official SOS district-wide totals are used for this multi-county seat. Re-elected 2026; new term begins January 2027.",
        "House District 1 (H01)": "Official 2026 SOS statewide House summary, House District 1: Troy Claycomb (R) Total 3,688. Official Crook share 2,701; official Weston share 987, taking office January 2027. Official 2024 SOS: Chip Neiman (R) Total 5,096. Official Crook share 3,828; official Weston share 1,268. Also covers Weston. Official SOS district-wide totals are used for this multi-county seat.",
    },
    "weston": {
        "Senate District 1 (S01)": "Official 2026 SOS statewide Senate summary, Senate District 1: Ogden Driskill (R) Total 5,107. Official Weston share 936; official Crook share 2,313; official Campbell share 1,858. Official 2022 SOS: Ogden Driskill (R) Total 4,785. Official Weston share 819; official Crook share 2,029; official Campbell share 1,937. Also covers Campbell and Crook. Official SOS district-wide totals are used for this multi-county seat. Re-elected 2026; new term begins January 2027.",
        "Senate District 3 (S03)": "Official 2026 SOS statewide Senate summary, Senate District 3: Cheri E. Steinmetz (R) Total 5,792. Official Weston share 1,207; official Goshen share 3,777; official Niobrara share 808. Official 2022 SOS: Cheri Steinmetz (R) Total 6,352. Official Weston share 1,362; official Goshen share 4,017; official Niobrara share 973. Also covers Goshen and Niobrara. Official SOS district-wide totals are used for this multi-county seat. Re-elected 2026; new term begins January 2027.",
        "House District 1 (H01)": "Official 2026 SOS statewide House summary, House District 1: Troy Claycomb (R) Total 3,688. Official Weston share 987; official Crook share 2,701, taking office January 2027. Official 2024 SOS: Chip Neiman (R) Total 5,096. Official Weston share 1,268; official Crook share 3,828. Also covers Crook. Official SOS district-wide totals are used for this multi-county seat.",
        "House District 2 (H02)": "Official 2026 SOS statewide House summary, House District 2: JD Williams (R) Total 2,850. Official Weston share 1,208; official Goshen share 839; official Niobrara share 803. Official 2024 SOS: JD Williams (R) Total 3,834. Official Weston share 1,662; official Goshen share 1,125; official Niobrara share 1,047. Official 2022 SOS: Allen Slagle (R) Total 2,927, not JD Williams. Official Weston share 1,325; official Goshen share 932; official Niobrara share 670. Also covers Goshen and Niobrara. Official SOS district-wide totals are used for this multi-county seat.",
    },
}

HOLDER_NOTES = {  # (office, holder name) -> notes; only overrides listed holders
    "lincoln": {
        ("Senate District 14 (S14)", "Laura Taliaferro (formerly Pearson)"): "Official 2024 winner. Also covers Sublette, Sweetwater, and Uinta. Official SOS district-wide totals are used for this multi-county seat.",
        ("Senate District 16 (S16)", "Dan Dockstader"): "Official 2024 winner; not on the 2026 ballot. Also covers Teton County. Official SOS district-wide totals are used for this multi-county seat.",
        ("House District 18 (H18)", "Kenneth D. Roberts"): "Takes office January 2027. Official 2026 general winner. Official SOS district-wide totals: Roberts 2,691. Official 2026 Lincoln clerk portion: 1,412. Also covers Sweetwater and Uinta.",
        ("House District 20 (H20)", "Albert Sommers"): "Takes office January 2027. Official 2026 general winner. Official SOS district-wide totals: Sommers 3,349. Official 2026 Lincoln clerk portion: 154. Also covers Sublette.",
        ("House District 21 (H21)", "McKay L. Erickson"): "Official 2024 winner, continuing; official 2026 general winner, term begins January 2027.",
        ("House District 22 (H22)", "Andrew Byron"): "Official 2024 winner, continuing; official 2026 general winner, term begins January 2027. Also covers Teton County. Official SOS district-wide totals are used for this multi-county seat.",
    },
    "teton": {
        ("Senate District 16 (S16)", "Dan Dockstader"): "Official 2024 winner; not on the 2026 ballot. Also covers Lincoln County.",
        ("Senate District 17 (S17)", "Mike Gierau"): "Official 2022 winner, continuing; official 2026 general winner, term begins January 2027.",
        ("House District 16 (H16)", "Mike Yin"): "Official 2024 winner, continuing; official 2026 general winner, term begins January 2027.",
        ("House District 22 (H22)", "Andrew Byron"): "Official 2024 winner, continuing; official 2026 general winner, term begins January 2027. Also covers Lincoln County. Official SOS district-wide totals are used for this multi-county seat.",
        ("House District 23 (H23)", "Liz Storer"): "Official 2024 winner, continuing; official 2026 general winner, term begins January 2027.",
    },
    "park": {
        ("House District 26 (H26)", "Dalton Banks"): "Re-elected 2026; official 2026 general, 256 (Park portion).",
        ("House District 50 (H50)", "Rachel Rodriguez-Williams"): "Official ballot spelling is Rachel Rodriguez-Williams.",
    },
    "sheridan": {
        ("House District 40 (H40)", "Marilyn F Connolly"): "Re-elected 2026; official 2026 general, 555.",
        ("House District 51 (H51)", "Laurie Bratten"): "Re-elected 2026; official 2026 general, 3,774.",
    },
    "sweetwater": {
        ("Senate District 11 (S11)", "Bob Davis"): "Takes office January 2027. Official 2026 general winner.",
        ("Senate District 13 (S13)", "Stacy Jones"): "Official 2022 winner, continuing; official 2026 general winner, term begins January 2027.",
        ("House District 15 (H15)", "Pamela Thayer"): "Official 2024 winner, continuing; official 2026 general winner, term begins January 2027.",
        ("House District 17 (H17)", "Elizabeth Bingham"): "Takes office January 2027. Official 2026 general winner.",
        ("House District 18 (H18)", "Kenneth D. Roberts"): "Takes office January 2027. Official 2026 general winner. Official 2026 SOS district-wide totals: Roberts 2,691. Official Sweetwater portion: 879.",
        ("House District 39 (H39)", "Cody Wylie"): "Official 2024 winner, continuing; official 2026 general winner, term begins January 2027.",
        ("House District 47 (H47)", "Eamon O'Toole"): "Takes office January 2027. Official 2026 general winner.",
        ("House District 48 (H48)", "James Wamsley"): "Takes office January 2027. Official 2026 general winner.",
        ("House District 60 (H60)", "Tony Niemiec"): "Takes office January 2027. Official 2026 general winner.",
    },
    "natrona": {
        ("Senate District 27 (S27)", "Kevin Helling"): "Takes office January 2027. Official 2026 general winner.",
        ("Senate District 29 (S29)", "Lisa Engebretsen"): "Takes office January 2027. Official 2026 general winner.",
        ("House District 35 (H35)", "Christopher Dresang"): "Takes office January 2027. Official 2026 general winner.",
        ("House District 36 (H36)", "Art Washut"): "Official 2024 and 2026 general winner, continuing; official 2026 term begins January 2027.",
        ("House District 37 (H37)", "Brian Costello"): "Takes office January 2027. Official 2026 general winner.",
        ("House District 38 (H38)", "Robert L. Hendry"): "Takes office January 2027. Official 2026 general winner.",
        ("House District 56 (H56)", "Elissa Campbell"): "Official 2024 and 2026 general winner, continuing; official 2026 term begins January 2027.",
        ("House District 57 (H57)", "Julie Jarvis"): "Official 2024 and 2026 general winner, continuing; official 2026 term begins January 2027.",
        ("House District 58 (H58)", "Bill Allemand"): "Official 2024 and 2026 general winner, continuing; official 2026 term begins January 2027.",
        ("House District 59 (H59)", "J.R. Riggins"): "Official 2024 and 2026 general winner, continuing; official 2026 term begins January 2027.",
        ("House District 62 (H62)", "Kevin J. Campbell"): "Official 2024 and 2026 general winner, continuing; official 2026 term begins January 2027.",
    },
    "laramie": {
        ("Senate District 6 (S06)", "Taft Love"): "Official 2024 general winner was Darin Smith; official 2026 general names Taft Love (not labeled unexpired). Mid-term succession date is not stated in the official generals.",
        ("Senate District 31 (S31)", "Evie Brennan"): "Official 2022 term ends January 2027; official 2026 general winner, continuing.",
        ("House District 4 (H04)", "Jeremy Haroldson"): "Official 2026 general winner. Official SOS district-wide totals are used for this multi-county seat.",
    },
    "big-horn": {
        ("Senate District 19 (S19)", "Dan Laursen"): "Official 2022 SOS statewide Senate summary, Senate District 19: Dan Laursen (R). Official Big Horn share 2,637; official Park share 2,901.",
        ("Senate District 20 (S20)", "Ed Cooper"): "Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Big Horn share 1,475 (official 2024 clerk canvass same 1,475); official Washakie 3,442, Hot Springs 2,180, Park 834, Fremont 305. Off-cycle in 2026.",
        ("House District 26 (H26)", "Dalton Banks"): "Official 2026 SOS statewide House summary, House District 26: Dalton Banks (R), Ralph Nieder-Westermann (D). Official Big Horn share Banks 2,301, Nieder-Westermann 538 (official clerk abstract same); official Park Banks 256, Nieder-Westermann 33. Re-elected.",
        ("House District 27 (H27)", "Martha Lawley"): "Official 2026 SOS statewide House summary, House District 27: Martha Lawley (R) 2,700, Theresa Livingston (D) 490. Official Big Horn share Lawley 418, Livingston 60 (official clerk abstract same); official Washakie Lawley 2,282, Livingston 430. Re-elected.",
        ("House District 28 (H28)", "John R. Winter"): "Official 2024 SOS statewide House summary, House District 28: John R. Winter (R) Total 3,986, Larry Alwin (D) 857. Official Big Horn share Winter 920, Alwin 85.",
    },
    "washakie": {
        ("Senate District 20 (S20)", "Ed Cooper"): "Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Washakie share 3,442 (sum of official 2024 clerk precinct rows, 5 of 5 precincts); official Big Horn 1,475; official Hot Springs 2,180; official Park 834; official Fremont 305 (1,475+2,180+834+305+3,442=8,236). S20 is off-cycle in 2026.",
        ("House District 27 (H27)", "Martha Lawley"): "Official 2026 SOS statewide House summary, House District 27: Martha Lawley (R) 2,700, Theresa Livingston (D) 490. Official Washakie share Lawley 2,282, Livingston 430, write-ins 18 (official 2026 clerk same Washakie figures); official Big Horn 418-60.",
    },
    "campbell": {
        ("Senate District 1 (S01)", "Ogden Driskill"): "Re-elected 2026; official SOS Total 5,107; official Campbell share 1,858. New term begins January 2027.",
        ("House District 32 (H32)", "Ken Clouston"): "Re-elected 2026; official Campbell 2026 general, TOTAL 2,124.",
        ("House District 53 (H53)", "Christopher Knapp"): "Re-elected 2026; official Campbell 2026 general, TOTAL 1,407.",
    },
}


def apply_to_groups(groups, slug: str) -> int:
    """Set canonical legislative office (and selected holder) notes on a groups list.
    Returns the number of office/holder notes applied. Unknown offices are left alone.
    An empty string in OFFICE_NOTES removes the office note.
    """
    n = 0
    office_map = OFFICE_NOTES.get(slug) or {}
    holder_map = HOLDER_NOTES.get(slug) or {}
    for g in groups or []:
        for o in g.get("offices") or []:
            off = o.get("office")
            if off in office_map:
                val = office_map[off]
                if val:
                    o["note"] = val
                else:
                    o.pop("note", None)
                n += 1
            for h in o.get("holders") or []:
                key = (off, h.get("name"))
                if key in holder_map:
                    val = holder_map[key]
                    if val:
                        h["notes"] = val
                    else:
                        h.pop("notes", None)
                    n += 1
    return n

