import asyncio
import json
import subprocess
import sys
import wave
from pathlib import Path
import edge_tts
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

STUDIO_DIR = Path(r"C:\Users\samet\.gemini\antigravity\scratch\stickman-us-studio")
FFMPEG_BIN = STUDIO_DIR / "node_modules" / "@remotion" / "compositor-win32-x64-msvc" / "ffmpeg.exe"
FFMPEG = str(FFMPEG_BIN) if FFMPEG_BIN.exists() else "ffmpeg"

TMP_VO_DIR = STUDIO_DIR / "out" / "vo_chernobyl_10min_tmp"
OUT_AUDIO = STUDIO_DIR / "public" / "audio" / "chernobyl_10min_master.mp3"
OUT_TIMELINE = STUDIO_DIR / "src" / "ifnoir" / "chernobyl10MinTimeline.ts"

SR = 44100
FPS = 30

# Gripping US investigative Cold War documentary narrator
VOICE_ID = "en-US-AndrewNeural"
VOICE_RATE = "+3%"
VOICE_PITCH = "-2Hz"

CHAPTERS = [
    {"chapterId": 1, "code": "CHAPTER I", "title": "01:23:04 DESK 8: THE SURVIVING TURBINE ENGINEER"},
    {"chapterId": 2, "code": "CHAPTER II", "title": "KGB FILE DIVERSIYA: SABOTAGE & THE SPY SATELLITE"},
    {"chapterId": 3, "code": "CHAPTER III", "title": "MAY 1986: THE JERUSALEM SHORTWAVE INTERCEPT"},
    {"chapterId": 4, "code": "CHAPTER IV", "title": "CHERNOBYL-2: THE 7-BILLION-RUBLE RADAR COVER-UP"},
    {"chapterId": 5, "code": "CHAPTER V", "title": "5,000 LIQUIDATORS & THE POST-SOVIET EXODUS"},
    {"chapterId": 6, "code": "CHAPTER VI", "title": "ROBERT MAXWELL'S JET & THE MINSK STANDOFF"},
    {"chapterId": 7, "code": "CHAPTER VII", "title": "REVELATION 8:11: THE WORMWOOD PROPHECY"},
    {"chapterId": 8, "code": "CHAPTER VIII", "title": "01:23:40: THE AZ-5 SECRET KGB BURIED"},
]

SHOT_SCRIPT = [
    # ==================== CHAPTER 1 ====================
    {
        "shotId": 1,
        "chapterId": 1,
        "slug": "ch1_hook_desk8",
        "sfx": "alarm_klaxon",
        "text": (
            "Everyone thinks they know what happened inside Chernobyl at one twenty-three AM on April twenty-sixth, "
            "nineteen eighty-six. Operators ran a reckless test, pressed emergency button A-Z-five, and died of radiation. "
            "Almost nobody asks about the surviving engineer at Desk Eight—or why the KGB opened a foreign sabotage file before dawn."
        ),
        "cues": [
            "APRIL 26, 1986 · 01:23 AM\nTHE STORY EVERYONE KNOWS",
            "A RECKLESS MIDNIGHT TEST\nAND BUTTON AZ-5",
            "NOBODY ASKS ABOUT THE\nSURVIVOR AT DESK EIGHT",
            "OR WHY THE KGB OPENED\nA FOREIGN SABOTAGE FILE",
        ],
    },
    {
        "shotId": 2,
        "chapterId": 1,
        "slug": "ch1_igor_kirschenbaum_valve",
        "sfx": "switch_throw",
        "text": (
            "Meet Igor Kirschenbaum, Senior Turbine Control Engineer inside Unit Four. "
            "At exactly one twenty-three and four seconds, obeying Deputy Chief Engineer Anatoly Dyatlov's order, "
            "Kirschenbaum shut the main steam valves feeding Turbogenerator Number Eight—starting the thirty-six-second countdown to detonation."
        ),
        "cues": [
            "IGOR KIRSCHENBAUM\nSENIOR TURBINE ENGINEER",
            "EXACTLY 01:23:04 AM\nINSIDE CONTROL ROOM FOUR",
            "SHUT THE STEAM VALVES ON\nTURBOGENERATOR NO. 8",
            "36 SECONDS BEFORE\nREACTOR FOUR DETONATED",
        ],
    },
    {
        "shotId": 3,
        "chapterId": 1,
        "slug": "ch1_shielded_room_survival",
        "sfx": "geiger_burst",
        "text": (
            "Why did Kirschenbaum live while young reactor operators beside him died in Moscow Hospital Number Six? "
            "Control Room Four sat behind thick biological concrete shielding. Aleksandr Akimov and Leonid Toptunov "
            "marched out into flooded, unshielded corridors to crank emergency water valves by hand—absorbing fatal fifteen-sievert doses."
        ),
        "cues": [
            "WHY DID KIRSCHENBAUM LIVE\nWHILE COWORKERS DIED?",
            "CONTROL ROOM FOUR HAD\nHEAVY CONCRETE SHIELDING",
            "AKIMOV & TOPTUNOV ENTERED\nFLOODED PUMP CORRIDORS",
            "ABSORBING LETHAL 15-SIEVERT\nDOSES CRANKING VALVES",
        ],
    },
    {
        "shotId": 4,
        "chapterId": 1,
        "slug": "ch1_relocation_to_israel",
        "sfx": "shutter",
        "text": (
            "Years later, as the Iron Curtain cracked and KGB secrecy collapsed, Kirschenbaum quietly emigrated to Israel, "
            "spending decades operating power turbines for the Israel Electric Corporation. "
            "Now, forty years on, viral threads have turned his survival—and five bizarre Cold War connections—into a global obsession."
        ),
        "cues": [
            "AS SOVIET BORDERS CRACKED\nKIRSCHENBAUM LEFT UKRAINE",
            "RELOCATED TO ISRAEL TO RUN\nPOWER PLANT TURBINES",
            "DECADE AFTER DECADE IN\nNEAR-TOTAL PUBLIC SILENCE",
            "SPARKING THE INTERNET'S\nWILDEST COLD WAR RABBIT HOLE",
        ],
    },
    {
        "shotId": 5,
        "chapterId": 1,
        "slug": "ch1_sbu_kgb_dossiers_unsealed",
        "sfx": "stamp",
        "text": (
            "To separate internet myth from classified reality, we went straight inside the Top Secret KGB Chernobyl Dossiers "
            "unsealed by Ukraine's Security Service, alongside CIA satellite cables and forgotten nineteen eighty-six wire dispatches. "
            "What is actually documented in those files is stranger than fiction."
        ),
        "cues": [
            "UNSEALED BY UKRAINE'S SBU:\nTHE KGB CHERNOBYL DOSSIERS",
            "CROSS-CHECKED WITH CIA\nSATELLITE & WIRE ARCHIVES",
            "SEPARATING VIRAL MYTH\nFROM CLASSIFIED FACT",
            "WHAT THE FILES REVEAL IS\nSTRANGER THAN FICTION",
        ],
    },
    # ==================== CHAPTER 2 ====================
    {
        "shotId": 6,
        "chapterId": 2,
        "slug": "ch2_chebrikov_sabotage_order",
        "sfx": "stamp",
        "text": (
            "Declassified Ukrainian KGB memos confirm a stunning fact: in the first days after the blast, "
            "KGB Chairman Viktor Chebrikov ordered Counterintelligence Chief Filipp Bobkov to investigate Reactor Four "
            "as a deliberate act of foreign sabotage—codenamed Diversion."
        ),
        "cues": [
            "DECLASSIFIED SBU ARCHIVE:\nDAY ONE KGB DIRECTIVE",
            "CHAIRMAN VIKTOR CHEBRIKOV\nMOBILIZED COUNTERINTELLIGENCE",
            "TREATED REACTOR FOUR AS\nPOSSIBLE FOREIGN SABOTAGE",
            "OFFICIAL KGB CODENAME:\nOPERATION 'DIVERSION'",
        ],
    },
    {
        "shotId": 7,
        "chapterId": 2,
        "slug": "ch2_kh11_spy_satellite",
        "sfx": "radio_static",
        "text": (
            "Why did Soviet intelligence suspect Western agencies immediately? KGB orbital logs flagged an American "
            "K-H-eleven Kennan reconnaissance satellite passing directly over Pripyat—snapping thermal images of the open burning core "
            "before Soviet generals had even admitted the roof was gone."
        ),
        "cues": [
            "WHY SOVIET INTELLIGENCE\nSUSPECTED WESTERN SPIES",
            "ORBITAL LOGS FLAGGED A U.S.\nKH-11 KENNAN SATELLITE",
            "PASSING DIRECTLY OVER\nNORTHERN UKRAINE",
            "IMAGING THE BURNING CORE\nBEFORE MOSCOW ADMITTED IT",
        ],
    },
    {
        "shotId": 8,
        "chapterId": 2,
        "slug": "ch2_norinsk_seismic_shock",
        "sfx": "geiger_burst",
        "text": (
            "Then came a baffling seismic anomaly recorded sixty miles west at the Norinsk geophysical station. "
            "Sixteen seconds before the main explosion tore off the reactor lid, sensors logged a sharp tremor beneath Unit Four—"
            "fueling secret theories of a subterranean charge or foundation shear."
        ),
        "cues": [
            "60 MILES WEST AT NORINSK\nGEOPHYSICAL STATION",
            "16 SECONDS BEFORE THE\nMAIN REACTOR EXPLOSION",
            "SEISMOGRAPHS LOGGED A SHARP\nLOCALIZED TREMOR",
            "SPARKING SECRET PROBES INTO\nSUBTERRANEAN CHARGES",
        ],
    },
    {
        "shotId": 9,
        "chapterId": 2,
        "slug": "ch2_29_kgb_warnings",
        "sfx": "shutter",
        "text": (
            "KGB agents audited every foreign-made valve and sensor imported through Western suppliers, searching for planted defects. "
            "They found zero foreign bombs—instead uncovering twenty-nine buried KGB memos from nineteen seventy-three onward "
            "warning that Soviet builders had stolen cement and cracked the plant's pillars."
        ),
        "cues": [
            "KGB AUDITED EVERY IMPORTED\nWESTERN VALVE & SENSOR",
            "ZERO EVIDENCE OF FOREIGN\nEXPLOSIVES WAS FOUND",
            "INSTEAD: 29 BURIED KGB\nMEMOS SINCE 1973",
            "STOLEN CEMENT & CRACKED\nSTRUCTURAL PILLARS",
        ],
    },
    {
        "shotId": 10,
        "chapterId": 2,
        "slug": "ch2_1982_unit1_secret_meltdown",
        "sfx": "alarm_klaxon",
        "text": (
            "Even darker, those files revealed April nineteen eighty-six wasn't Chernobyl's first meltdown. "
            "In September nineteen eighty-two, Reactor Number One suffered a partial core fuel rupture venting radiation over Pripyat—"
            "and KGB chief Yuri Andropov personally buried every word of it."
        ),
        "cues": [
            "1986 WAS NOT CHERNOBYL'S\nFIRST NUCLEAR MELTDOWN",
            "SEPTEMBER 1982: UNIT ONE\nSUFFERED A PARTIAL RUPTURE",
            "RADIATION VENTED SILENTLY\nACROSS PRIPYAT",
            "BURIED PERSONALLY BY\nYURI ANDROPOV'S KGB",
        ],
    },
    # ==================== CHAPTER 3 ====================
    {
        "shotId": 11,
        "chapterId": 3,
        "slug": "ch3_kremlin_68h_blackout",
        "sfx": "radio_static",
        "text": (
            "When Unit Four blew apart, the Kremlin imposed total information lockdown. For sixty-eight hours, "
            "state television aired parades while KGB signal troops severed long-distance phone lines around Pripyat. "
            "Yet somehow, four mysterious radio transmissions pierced straight out of the zone—into Israel."
        ),
        "cues": [
            "68 HOURS OF TOTAL\nKREMLIN MEDIA BLACKOUT",
            "KGB SIGNAL TROOPS CUT\nPRIPYAT TELEPHONE LINES",
            "YET FOUR MYSTERIOUS RADIO\nCALLS PIERCED THE ZONE",
            "PICKED UP 1,300 MILES AWAY\nINSIDE ISRAEL",
        ],
    },
    {
        "shotId": 12,
        "chapterId": 3,
        "slug": "ch3_david_ben_bassat_tapes",
        "sfx": "radio_static",
        "text": (
            "In early May nineteen eighty-six, The Washington Post and NBC News reported a startling claim from Israeli "
            "amateur radio operator David Ben-Bassat. Tuning shortwave frequencies from Tel Aviv and Jerusalem, "
            "Ben-Bassat recorded four separate exchanges with a panicked Russian voice thirty miles north of Chernobyl."
        ),
        "cues": [
            "MAY 1986: WASHINGTON POST\n& NBC NEWS DISPATCHES",
            "ISRAELI HAM OPERATOR\nDAVID BEN-BASSAT",
            "RECORDED FOUR SHORTWAVE\nCONTACTS IN RUSSIAN",
            "30 MILES NORTH OF THE\nBURNING NUCLEAR PLANT",
        ],
    },
    {
        "shotId": 13,
        "chapterId": 3,
        "slug": "ch3_nobody_drinks_the_water",
        "sfx": "geiger_burst",
        "text": (
            "Through crackling twenty-meter static, the caller claimed between six hundred and seven hundred people "
            "were already hospitalized with sixty dead, pleading into the microphone: 'Nobody drinks the water. "
            "We cannot leave. We are afraid.' Western newsrooms replayed the tapes around the clock."
        ),
        "cues": [
            "OVER CRACKLING 20-METER\nSHORTWAVE STATIC",
            "'600 TO 700 CASUALTIES\nINCLUDING 60 DEAD'",
            "'NOBODY DRINKS THE WATER.\nWE ARE AFRAID.'",
            "BROADCAST GLOBALLY WHILE\nMOSCOW STAYED SILENT",
        ],
    },
    {
        "shotId": 14,
        "chapterId": 3,
        "slug": "ch3_hoax_leak_or_psyop",
        "sfx": "stamp",
        "text": (
            "Immediately, veteran radio trackers and CIA monitors raised a chilling question. "
            "Soviet KGB jamming towers triangulated illegal transmitters within minutes. How did one operator broadcast "
            "four times unjammed—was it a miracle leak, a cold-blooded hoax, or an intelligence psy-op to shatter Soviet silence?"
        ),
        "cues": [
            "RADIO EXPERTS & ANALYSTS\nRAISED A RED FLAG",
            "KGB JAMMING TOWERS TRACKED\nILLEGAL RADIOS IN MINUTES",
            "HOW DID ONE VOICE TRANSMIT\nFOUR SEPARATE TIMES?",
            "MIRACLE LEAK, RADIO HOAX,\nOR COLD WAR PSY-OP?",
        ],
    },
    {
        "shotId": 15,
        "chapterId": 3,
        "slug": "ch3_forsmark_gorbachev_tv",
        "sfx": "shutter",
        "text": (
            "Whatever was on those tapes, Moscow's blackout collapsed hours after technicians at Sweden's Forsmark reactor "
            "detected radioactive particles on their own boots eight hundred miles away—forcing Mikhail Gorbachev "
            "to face television cameras eighteen agonizing days after the blast."
        ),
        "cues": [
            "800 MILES AWAY AT SWEDEN'S\nFORSMARK NUCLEAR PLANT",
            "RADIATION ALARMS TRIGGERED\nON WORKERS' BOOTS",
            "MOSCOW'S COVER-UP COLLAPSED\nON THE WORLD STAGE",
            "18 DAYS LATE: GORBACHEV\nFINALLY ADDRESSED TV",
        ],
    },
    # ==================== CHAPTER 4 ====================
    {
        "shotId": 16,
        "chapterId": 4,
        "slug": "ch4_chernobyl2_map_erased",
        "sfx": "woodpecker_pulse",
        "text": (
            "If foreign agents didn't sabotage Unit Four, another underground theory points just nine kilometers "
            "into the pine woods behind the reactor. On public Soviet maps, the site was marked as an abandoned pioneer camp. "
            "Behind triple barbed wire sat Secret Military Garrison Chernobyl-Two."
        ),
        "cues": [
            "9 KILOMETERS THROUGH THE\nPINE FOREST FROM UNIT 4",
            "MARKED ON SOVIET MAPS AS\nA CHILDREN'S SUMMER CAMP",
            "BEHIND TRIPLE BARBED WIRE:\nGARRISON 'CHERNOBYL-2'",
            "ONE OF THE COLD WAR'S\nMOST EXPENSIVE SECRETS",
        ],
    },
    {
        "shotId": 17,
        "chapterId": 4,
        "slug": "ch4_duga1_woodpecker_array",
        "sfx": "woodpecker_pulse",
        "text": (
            "Towering five hundred feet into the sky stood Duga-One—a half-mile steel wall built to detect American "
            "intercontinental missiles seconds after launch. Its ten-hertz pulsing signal hammered global radios "
            "so relentlessly NATO dubbed it the Russian Woodpecker."
        ),
        "cues": [
            "500 FEET TALL · HALF A MILE\nOF SOLID STEEL CAGES",
            "OVER-THE-HORIZON MISSILE\nDEFENSE RADAR 'DUGA-1'",
            "10-HERTZ PULSES HIJACKED\nRADIOS WORLDWIDE",
            "NATO CODENAME:\nTHE RUSSIAN WOODPECKER",
        ],
    },
    {
        "shotId": 18,
        "chapterId": 4,
        "slug": "ch4_seven_billion_ruble_failure",
        "sfx": "ui_tick",
        "text": (
            "Here is what Moscow hid even from its own citizens: Duga-One cost an estimated seven billion rubles—"
            "roughly double the cost of the Chernobyl nuclear plant itself—and it had a fatal blind spot. "
            "Northern aurora borealis storms scrambled its beams right across the Arctic missile corridor."
        ),
        "cues": [
            "SECRET PRICE TAG:\n7 BILLION SOVIET RUBLES",
            "NEARLY TWICE THE COST OF\nCHERNOBYL POWER PLANT",
            "FATAL DESIGN FLAW:\nARCTIC AURORA INTERFERENCE",
            "BLIND TO U.S. MISSILES\nCOMING OVER THE POLE",
        ],
    },
    {
        "shotId": 19,
        "chapterId": 4,
        "slug": "ch4_audit_coverup_hypothesis",
        "sfx": "stamp",
        "text": (
            "In the award-winning investigation The Russian Woodpecker, Ukrainian researcher Fedor Alexandrovich "
            "uncovered a haunting timeline: top military officials faced a decisive Kremlin state audit of Duga-One later in nineteen eighty-six—"
            "an audit where failure meant disgrace or a firing squad."
        ),
        "cues": [
            "THE 'RUSSIAN WOODPECKER'\nCOVER-UP HYPOTHESIS",
            "LATE 1986: HIGH-LEVEL\nKREMLIN AUDIT SCHEDULED",
            "EXPOSING A 7-BILLION-RUBLE\nDEFENSE FAILURE",
            "IN SOVIET MILITARY LAW,\nFAILURE MEANT RUIN",
        ],
    },
    {
        "shotId": 20,
        "chapterId": 4,
        "slug": "ch4_duga_buried_in_zone",
        "sfx": "geiger_burst",
        "text": (
            "Whether coincidence or conspiracy, the explosion of Reactor Four instantly swallowed Chernobyl-Two "
            "inside a permanent radioactive exclusion zone. The Kremlin audit was canceled overnight, "
            "and Duga-One's classified computers were stripped and buried in lead-lined pits."
        ),
        "cues": [
            "INSTANTLY SWALLOWED INSIDE\nTHE 30-KM EXCLUSION ZONE",
            "THE KREMLIN RADAR AUDIT\nWAS CANCELED OVERNIGHT",
            "CLASSIFIED COMPUTERS\nSTRIPPED & BURIED IN PITS",
            "NOBODY WAS EVER PROSECUTED\nFOR DUGA-1'S FAILURE",
        ],
    },
    # ==================== CHAPTER 5 ====================
    {
        "shotId": 21,
        "chapterId": 5,
        "slug": "ch5_viral_liquidators_claim",
        "sfx": "shutter",
        "text": (
            "Now examine the viral claim sweeping social media today: that thousands of Chernobyl cleanup workers "
            "suddenly moved to Israel right after the explosion. What actually happened is documented down to the exact passport numbers."
        ),
        "cues": [
            "THE VIRAL CLAIM SWEEPING\nSOCIAL MEDIA TODAY:",
            "'THOUSANDS OF CLEANUP CREWS\nSUDDENLY MOVED TO ISRAEL'",
            "WHAT DO OFFICIAL PASSPORT\n& MEDICAL LOGS SHOW?",
            "THE REAL TIMELINE IS\nCOMPLETELY DOCUMENTED",
        ],
    },
    {
        "shotId": 22,
        "chapterId": 5,
        "slug": "ch5_biorobots_45_seconds",
        "sfx": "geiger_burst",
        "text": (
            "To seal the burning core, Moscow drafted six hundred thousand liquidators from every corner of the USSR. "
            "When gamma radiation fried German police robots on the roof, soldiers in hand-cut lead aprons ran out as human bio-robots—"
            "given forty-five seconds to hurl one shovel of lethal fuel."
        ),
        "cues": [
            "600,000 LIQUIDATORS DRAFTED\nACROSS THE SOVIET UNION",
            "GAMMA RAYS FRIED GERMAN\n& LUNAR ROBOTS ON THE ROOF",
            "SOLDIERS IN LEAD APRONS\nBECAME 'BIO-ROBOTS'",
            "45 SECONDS PER MAN TO\nSHOVEL GLOWING GRAPHITE",
        ],
    },
    {
        "shotId": 23,
        "chapterId": 5,
        "slug": "ch5_1990_aliyah_5000_liquidators",
        "sfx": "stamp",
        "text": (
            "None of them left in nineteen eighty-six—Soviet borders were sealed shut. "
            "Only in nineteen ninety, when Gorbachev opened emigration gates, did one million Soviet Jewish citizens depart—"
            "including nearly five thousand decorated Chernobyl liquidators fleeing Ukraine and Belarus."
        ),
        "cues": [
            "1986–1988: SOVIET EXIT\nBORDERS REMAINED SEALED",
            "1990: GORBACHEV LIFTED\nIRON CURTAIN EXIT BANS",
            "1 MILLION EMIGRATED IN\nTHE POST-SOVIET EXODUS",
            "INCLUDING ~5,000 VERIFIED\nCHERNOBYL LIQUIDATORS",
        ],
    },
    {
        "shotId": 24,
        "chapterId": 5,
        "slug": "ch5_secret_medical_gag_order",
        "sfx": "ui_tick",
        "text": (
            "Why were Chernobyl families desperate to get out first? Declassified Soviet Health Ministry orders "
            "banned doctors from writing radiation sickness on hospital charts—forcing physicians to record tumors and bone marrow failure "
            "as ordinary vascular fatigue."
        ),
        "cues": [
            "WHY CHERNOBYL FAMILIES\nRUSHED FOR THE FIRST PLANES",
            "SECRET SOVIET HEALTH\nMINISTRY GAG DIRECTIVE",
            "DOCTORS BANNED FROM LISTING\nRADIATION ON CHARTS",
            "TUMORS FALSIFIED AS\n'VASCULAR DISTONIA'",
        ],
    },
    {
        "shotId": 25,
        "chapterId": 5,
        "slug": "ch5_ben_gurion_dna_studies",
        "sfx": "shutter",
        "text": (
            "Once outside KGB jurisdiction, those five thousand liquidators broke Moscow's medical cover-up wide open. "
            "Israeli hematologists and Ben-Gurion University geneticists published landmark studies on their blood and children—"
            "reconstructing the true radiation doses Soviet officers had erased."
        ),
        "cues": [
            "OUTSIDE KGB REACH, THE\nMEDICAL COVER-UP BROKE",
            "5,000 LIQUIDATORS EXAMINED\nBY WESTERN GENETICISTS",
            "BEN-GURION UNIVERSITY\nDNA & THYROID STUDIES",
            "RECONSTRUCTED THE TRUE\nDOSES MOSCOW ERASED",
        ],
    },
    # ==================== CHAPTER 6 ====================
    {
        "shotId": 26,
        "chapterId": 6,
        "slug": "ch6_robert_maxwell_clipping",
        "sfx": "shutter",
        "text": (
            "Then online researchers dug up a jaw-dropping nineteen ninety newspaper photograph: "
            "billionaire press tycoon Robert Maxwell—father of Ghislaine Maxwell—standing inside Kfar Chabad near Tel Aviv, "
            "embracing evacuated children flown straight out of Chernobyl's fallout zone."
        ),
        "cues": [
            "UNEARTHED 1990 ARCHIVAL\nNEWSPAPER PHOTOGRAPH",
            "BRITISH BILLIONAIRE MOGUL\nROBERT MAXWELL",
            "FATHER OF GHISLAINE MAXWELL\nINSIDE KFAR CHABAD",
            "GREETING CHILDREN FLOWN\nFROM CHERNOBYL'S ZONE",
        ],
    },
    {
        "shotId": 27,
        "chapterId": 6,
        "slug": "ch6_maxwell_triple_intelligence",
        "sfx": "stamp",
        "text": (
            "Why was Robert Maxwell mixed up in Soviet nuclear evacuations? Foreign Office and intelligence dossiers "
            "describe Maxwell as the Cold War's ultimate shadow broker—simultaneously cultivating British MI6, "
            "high-ranking KGB generals in Moscow, and Israeli intelligence."
        ),
        "cues": [
            "WHO WAS ROBERT MAXWELL\nBEHIND THE HEADLINES?",
            "THE COLD WAR'S ULTIMATE\nINTELLIGENCE BROKER",
            "LINKED TO BRITISH MI6,\nMOSCOW'S KGB & MOSSAD",
            "DIRECT BACKCHANNEL ACCESS\nTO GORBACHEV'S KREMLIN",
        ],
    },
    {
        "shotId": 28,
        "chapterId": 6,
        "slug": "ch6_minsk_airport_60_hours",
        "sfx": "ui_tick",
        "text": (
            "In August nineteen ninety, Chabad's first rescue airlift of nearly two hundred radiation-exposed children "
            "collapsed into chaos. Stranded for sixty hours at Minsk Airport after the Gulf War crisis grounded their charter jet, "
            "organizers placed an emergency call to Maxwell in London."
        ),
        "cues": [
            "AUGUST 1990: OPERATION\n'CHILDREN OF CHERNOBYL'",
            "196 EVACUEE CHILDREN\nSTRANDED AT MINSK AIRPORT",
            "60 HOURS GROUNDED AS GULF\nWAR DIVERTED AIRCRAFT",
            "AN URGENT MIDNIGHT CALL\nTO MAXWELL IN LONDON",
        ],
    },
    {
        "shotId": 29,
        "chapterId": 6,
        "slug": "ch6_maxwell_jet_intervention",
        "sfx": "stamp",
        "text": (
            "Maxwell worked his Kremlin backchannels, dispatched private aviation crews and funding to break the Minsk bottleneck, "
            "and landed to a hero's welcome in Israel—ultimately helping launch an airlift that evacuated "
            "nearly three thousand Chernobyl children."
        ),
        "cues": [
            "MAXWELL WORKED HIS DIRECT\nMOSCOW BACKCHANNELS",
            "DISPATCHED FLIGHT CREWS &\nFUNDING TO MINSK",
            "BROKE THE 60-HOUR SOVIET\nAIRPORT STANDOFF",
            "LAUNCHING AN AIRLIFT OF\n2,800+ CHERNOBYL CHILDREN",
        ],
    },
    {
        "shotId": 30,
        "chapterId": 6,
        "slug": "ch6_lady_ghislaine_mystery",
        "sfx": "alarm_klaxon",
        "text": (
            "Fifteen months later, on November fifth, nineteen ninety-one, as four hundred million dollars vanished "
            "from his Mirror Group pension funds, Robert Maxwell disappeared at night off his superyacht, the Lady Ghislaine. "
            "Six intelligence chiefs attended his Jerusalem funeral—and his KGB files vanished with him."
        ),
        "cues": [
            "15 MONTHS LATER:\nNOVEMBER 5, 1991",
            "$400 MILLION MISSING FROM\nMIRROR PENSION FUNDS",
            "VANISHED AT NIGHT OFF YACHT\n'LADY GHISLAINE'",
            "SIX INTELLIGENCE CHIEFS\nATTENDED HIS FUNERAL",
        ],
    },
    # ==================== CHAPTER 7 ====================
    {
        "shotId": 31,
        "chapterId": 7,
        "slug": "ch7_chornobyl_wormwood_meaning",
        "sfx": "ui_tick",
        "text": (
            "Beyond espionage and billionaires, one ancient linguistic coincidence sent chills across Ukraine in May nineteen eighty-six. "
            "In Ukrainian, the word chornobyl literally names common wormwood—a dark, bitter wild plant blanketing the riverbanks."
        ),
        "cues": [
            "THE LINGUISTIC COINCIDENCE\nTHAT CHILLED UKRAINE",
            "UKRAINIAN WORD 'CHORNOBYL'\nTRANSLATES LITERALLY TO:",
            "BITTER COMMON WORMWOOD\n(ARTEMISIA VULGARIS)",
            "GROWING WILD ALONG THE\nPRIPYAT RIVERBANKS",
        ],
    },
    {
        "shotId": 32,
        "chapterId": 7,
        "slug": "ch7_revelation_8_11_prophecy",
        "sfx": "stamp",
        "text": (
            "In the Book of Revelation, Chapter Eight, Verse Eleven, John writes: 'A great star fell from heaven, "
            "burning like a torch, onto a third of the rivers. The name of the star is Wormwood—and many died from the water, "
            "because it was made bitter.'"
        ),
        "cues": [
            "BOOK OF REVELATION 8:10–11\nTHE FALLING TORCH STAR",
            "'THE NAME OF THE STAR\nIS CALLED WORMWOOD'",
            "'A THIRD OF THE WATERS\nBECAME WORMWOOD'",
            "'AND MANY DIED FROM THE\nBITTER POISONED WATER'",
        ],
    },
    {
        "shotId": 33,
        "chapterId": 7,
        "slug": "ch7_dnieper_water_crisis",
        "sfx": "geiger_burst",
        "text": (
            "Inside the Kremlin war room, poisoning the rivers wasn't biblical metaphor—it was an imminent nightmare. "
            "Two hundred tons of molten nuclear corium were burning downward toward flooded basement tanks "
            "and the Dnieper reservoir supplying drinking water to thirty million citizens."
        ),
        "cues": [
            "INSIDE THE KREMLIN WAR ROOM\nIT WAS NO METAPHOR",
            "200 TONS OF 2,000°C MOLTEN\nNUCLEAR CORIUM",
            "MELTING TOWARD FLOODED\nBASEMENT BUBBLER POOLS",
            "THREATENING DRINKING WATER\nFOR 30 MILLION PEOPLE",
        ],
    },
    {
        "shotId": 34,
        "chapterId": 7,
        "slug": "ch7_three_suicide_divers_lived",
        "sfx": "switch_throw",
        "text": (
            "Three volunteer engineers—Oleksiy Ananenko, Valeri Bezpalov, and Boris Baranov—plunged into pitch-black, "
            "knee-deep radioactive basement water to wrench open drain valves before a massive steam explosion could occur. "
            "And contrary to myth, all three divers survived for decades."
        ),
        "cues": [
            "ANANENKO, BEZPALOV &\nBARANOV VOLUNTEERED",
            "WADED THROUGH PITCH-BLACK\nRADIOACTIVE BASEMENT PIPES",
            "DRAINED THE BUBBLER POOLS\nBY FLASHLIGHT & TOUCH",
            "CONTRARY TO MYTH: ALL THREE\nDIVERS SURVIVED DECADES",
        ],
    },
    {
        "shotId": 35,
        "chapterId": 7,
        "slug": "ch7_elephants_foot_corridor",
        "sfx": "geiger_burst",
        "text": (
            "In December nineteen eighty-six, physicists pushing a camera on wheels beneath Corridor Two-Seventeen "
            "found what remained of that molten core: the Elephant's Foot—emitting ten thousand roentgens an hour, "
            "fatal to any human standing beside it in just five minutes."
        ),
        "cues": [
            "DECEMBER 1986: CORRIDOR\n217/2 BENEATH UNIT FOUR",
            "SOLIDIFIED NUCLEAR LAVA:\nTHE 'ELEPHANT'S FOOT'",
            "RADIATION OUTPUT:\n10,000 ROENTGENS PER HOUR",
            "FIVE MINUTES BESIDE IT\nMEANT CERTAIN DEATH",
        ],
    },
    # ==================== CHAPTER 8 ====================
    {
        "shotId": 36,
        "chapterId": 8,
        "slug": "ch8_1987_show_trial_lie",
        "sfx": "stamp",
        "text": (
            "So when we return to Control Room Four at one twenty-three AM, what was the supreme state secret "
            "Moscow lied to the entire world to protect? At the closed nineteen eighty-seven Chernobyl trial, "
            "prosecutors pinned everything on operator error—hiding a lethal trap inside button A-Z-five."
        ),
        "cues": [
            "JULY 1987: MOSCOW'S CLOSED\nCHERNOBYL SHOW TRIAL",
            "BLAMED EVERYTHING ON\nCONTROL ROOM OPERATORS",
            "TO PROTECT THE SUPREME\nSOVIET NUCLEAR SECRET:",
            "THE LETHAL TRAP BUILT\nINTO BUTTON AZ-5",
        ],
    },
    {
        "shotId": 37,
        "chapterId": 8,
        "slug": "ch8_graphite_tip_detonator",
        "sfx": "switch_throw",
        "text": (
            "Thirty-six seconds after Igor Kirschenbaum shut Turbine Eight, Akimov hit emergency shutdown A-Z-five. "
            "Because R-B-M-K control rods were tipped with graphite, dropping all two hundred rods displaced cooling water first—"
            "turning the emergency brake into a nuclear detonator."
        ),
        "cues": [
            "36 SECONDS AFTER TURBINE 8\nSHUT DOWN AT DESK 8",
            "AKIMOV PRESSED EMERGENCY\nSCRAM BUTTON AZ-5",
            "GRAPHITE-TIPPED RODS\nDISPLACED COOLING WATER",
            "THE EMERGENCY BRAKE ACTED\nLIKE A DETONATOR",
        ],
    },
    {
        "shotId": 38,
        "chapterId": 8,
        "slug": "ch8_1975_leningrad_coverup",
        "sfx": "stamp",
        "text": (
            "Declassified KGB files prove Soviet physicists already saw that exact power spike in nineteen seventy-five "
            "at Leningrad and nineteen eighty-three at Ignalina. Instead of fixing the rods, the state classified the flaw Top Secret—"
            "never warning the night crew inside Unit Four."
        ),
        "cues": [
            "PROVEN BY DECLASSIFIED\nSOVIET KGB ARCHIVES:",
            "SAME SPIKE HIT LENINGRAD\n(1975) & IGNALINA (1983)",
            "CLASSIFIED 'TOP SECRET'\nINSTEAD OF FIXING RODS",
            "NEVER TOLD THE NIGHT CREW\nINSIDE CONTROL ROOM FOUR",
        ],
    },
    {
        "shotId": 39,
        "chapterId": 8,
        "slug": "ch8_gorbachev_2006_confession",
        "sfx": "shutter",
        "text": (
            "Twenty years later, Mikhail Gorbachev delivered the ultimate verdict. "
            "Even more than Perestroika, Gorbachev wrote, Chernobyl was perhaps the real cause of the collapse of the Soviet Union—"
            "draining hundreds of billions and shattering an empire built on classified lies."
        ),
        "cues": [
            "TWENTY YEARS LATER:\nGORBACHEV'S CONFESSION",
            "'PERHAPS THE REAL CAUSE OF\nTHE SOVIET COLLAPSE'",
            "OVER $235 BILLION IN\nECONOMIC DEVASTATION",
            "SHATTERED AN EMPIRE BUILT\nON CLASSIFIED LIES",
        ],
    },
    {
        "shotId": 40,
        "chapterId": 8,
        "slug": "ch8_finale_desk8_eternity",
        "sfx": "geiger_burst",
        "text": (
            "Today, Igor Kirschenbaum lives quietly along the Mediterranean coast, Robert Maxwell's secrets sleep beneath the Atlantic, "
            "Duga-One rusts above silent radioactive pines, and inside Chernobyl's steel arch, "
            "the embers of April twenty-sixth will burn for another hundred thousand years."
        ),
        "cues": [
            "KIRSCHENBAUM LIVES QUIETLY\nBY THE MEDITERRANEAN",
            "MAXWELL'S SECRETS SLEEP\nBENEATH THE ATLANTIC",
            "DUGA-1 RUSTS ABOVE\nRADIOACTIVE PINE WOODS",
            "AND REACTOR FOUR WILL BURN\nFOR 100,000 YEARS",
        ],
    },
]


def load_audio_mono(path: Path) -> np.ndarray:
    wav_tmp = path.with_suffix(".tmp44k.wav")
    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(path),
            "-ac",
            "1",
            "-ar",
            str(SR),
            "-f",
            "wav",
            str(wav_tmp),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    with wave.open(str(wav_tmp), "rb") as wf:
        raw = wf.readframes(wf.getnframes())
    wav_tmp.unlink(missing_ok=True)
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def trim_silence(samples: np.ndarray, thresh: float = 0.007) -> tuple[np.ndarray, float]:
    idx = np.where(np.abs(samples) > thresh)[0]
    if len(idx) == 0:
        return samples, 0.0
    pad_head = int(0.03 * SR)
    pad_tail = int(0.08 * SR)
    s0 = max(0, int(idx[0]) - pad_head)
    s1 = min(len(samples), int(idx[-1]) + pad_tail)
    return samples[s0:s1], s0 / SR


async def synth_shot(shot: dict, sem: asyncio.Semaphore) -> dict:
    async with sem:
        TMP_VO_DIR.mkdir(parents=True, exist_ok=True)
        mp3_path = TMP_VO_DIR / f"shot_{shot['shotId']:02d}_{shot['slug']}.mp3"
        meta_path = TMP_VO_DIR / f"shot_{shot['shotId']:02d}_{shot['slug']}.json"

        if mp3_path.exists() and meta_path.exists() and mp3_path.stat().st_size > 2000:
            cached_meta = json.loads(meta_path.read_text(encoding="utf-8"))
            raw_samples = load_audio_mono(mp3_path)
            trimmed, _ = trim_silence(raw_samples)
            dur_sec = len(trimmed) / SR
            return {
                "shot": shot,
                "samples": trimmed,
                "durationSec": dur_sec,
                "wordsRel": cached_meta["wordsRel"],
            }

        comm = edge_tts.Communicate(
            shot["text"],
            VOICE_ID,
            rate=VOICE_RATE,
            pitch=VOICE_PITCH,
            boundary="WordBoundary",
        )
        words_raw = []
        with open(mp3_path, "wb") as out_f:
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    out_f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    w_off = chunk["offset"] / 10_000_000.0
                    w_dur = max(0.06, chunk["duration"] / 10_000_000.0)
                    words_raw.append(
                        {
                            "text": chunk["text"],
                            "offsetSec": w_off,
                            "durationSec": w_dur,
                        }
                    )

        raw_samples = load_audio_mono(mp3_path)
        trimmed, head_trim_sec = trim_silence(raw_samples)
        dur_sec = len(trimmed) / SR

        words_rel = []
        for w in words_raw:
            rel_s = max(0.0, w["offsetSec"] - head_trim_sec)
            rel_e = min(dur_sec, rel_s + w["durationSec"])
            words_rel.append({"text": w["text"], "startRel": rel_s, "endRel": max(rel_s + 0.05, rel_e)})

        meta_path.write_text(json.dumps({"durationSec": dur_sec, "wordsRel": words_rel}, indent=2), encoding="utf-8")
        print(f"  [VO] Shot {shot['shotId']:02d} ({shot['slug']}): {dur_sec:.2f}s ({len(words_rel)} words)")
        return {
            "shot": shot,
            "samples": trimmed,
            "durationSec": dur_sec,
            "wordsRel": words_rel,
        }


def align_cues_and_words(shot: dict, voice_start_sec: float, dur_sec: float, words_rel: list[dict]) -> list[dict]:
    cues_txt = shot["cues"]
    n_cues = len(cues_txt)
    out = []
    # Split voice span cleanly across the 4 punchy 2-line investigative cues
    char_weights = [max(8, len(c.replace("\n", " "))) for c in cues_txt]
    total_w = sum(char_weights)
    acc = 0.0
    for idx, c_str in enumerate(cues_txt):
        frac0 = acc / total_w
        acc += char_weights[idx]
        frac1 = acc / total_w
        c_s = voice_start_sec + frac0 * dur_sec
        c_e = voice_start_sec + frac1 * dur_sec
        s_frame = int(round(c_s * FPS))
        e_frame = max(s_frame + 18, int(round(c_e * FPS)))

        tokens = [tok for tok in c_str.replace("\n", " ").split(" ") if tok.strip()]
        n_tok = max(1, len(tokens))
        span_f = max(1, e_frame - s_frame)
        w_timings = []
        for ti, tok in enumerate(tokens):
            ws = s_frame + int(round((ti / n_tok) * span_f))
            we = s_frame + int(round(((ti + 1) / n_tok) * span_f))
            w_timings.append(
                {
                    "word": tok,
                    "startFrame": ws,
                    "endFrame": max(ws + 3, we),
                }
            )
        out.append(
            {
                "text": c_str,
                "startSec": round(s_frame / FPS, 3),
                "endSec": round(e_frame / FPS, 3),
                "startFrame": s_frame,
                "endFrame": e_frame,
                "words": w_timings,
            }
        )
    return out


def lowpass_noise(rng: np.random.Generator, length: int, taps: int = 24) -> np.ndarray:
    raw = rng.standard_normal(length + taps).astype(np.float32)
    kernel = np.hanning(taps).astype(np.float32)
    kernel /= max(1e-6, kernel.sum())
    return np.convolve(raw, kernel, mode="valid")[:length]


def build_chernobyl_sfx_kit(rng: np.random.Generator) -> dict[str, np.ndarray]:
    kit: dict[str, np.ndarray] = {}

    # 1. Chapter Boom (deep sub impact + metallic reactor resonance)
    t_b = np.linspace(0, 1.9, int(1.9 * SR), dtype=np.float32)
    freq_b = 68.0 * np.exp(-t_b * 2.1) + 28.0
    boom = np.sin(2 * np.pi * np.cumsum(freq_b) / SR) * np.exp(-t_b * 2.4) * 0.65
    metallic = np.sin(2 * np.pi * 196.0 * t_b) * np.exp(-t_b * 4.5) * 0.16
    kit["chapter_boom"] = (boom + metallic).astype(np.float32)

    # 2. Subtle Transition Whoosh
    t_w = np.linspace(0, 0.34, int(0.34 * SR), dtype=np.float32)
    env_w = np.maximum(0.0, np.sin(np.pi * (t_w / 0.34))) ** 1.8
    kit["whoosh"] = (lowpass_noise(rng, len(t_w), taps=18) * env_w * 0.22).astype(np.float32)

    # 3. Geiger Counter Radiation Crackle Burst (signature Chernobyl sound!)
    n_g = int(1.65 * SR)
    geiger = np.zeros(n_g, dtype=np.float32)
    for _ in range(46):
        pos = int(rng.integers(0, n_g - 220))
        click_t = np.linspace(0, 0.004, int(0.004 * SR), dtype=np.float32)
        click = np.sin(2 * np.pi * 2950.0 * click_t) * np.exp(-click_t * 950.0) * 0.38
        geiger[pos : pos + len(click)] += click
    kit["geiger_burst"] = geiger

    # 4. Control Room Alarm Klaxon (subtle muffled Soviet 2-tone alert)
    t_k = np.linspace(0, 1.35, int(1.35 * SR), dtype=np.float32)
    mod = np.where((t_k * 3.0) % 1.0 < 0.5, 520.0, 415.0)
    klax = np.tanh(np.sin(2 * np.pi * np.cumsum(mod) / SR) * 1.8) * np.exp(-t_k * 1.9) * 0.19
    kit["alarm_klaxon"] = klax.astype(np.float32)

    # 5. Heavy Control Room Switch / Valve Throw
    t_sw = np.linspace(0, 0.28, int(0.28 * SR), dtype=np.float32)
    clunk = (
        np.sin(2 * np.pi * 145.0 * t_sw) * np.exp(-t_sw * 28.0) * 0.52
        + lowpass_noise(rng, len(t_sw), taps=8) * np.exp(-t_sw * 42.0) * 0.34
    )
    kit["switch_throw"] = clunk.astype(np.float32)

    # 6. Duga-1 "Russian Woodpecker" 10 Hz Over-The-Horizon Radar Tapping!
    n_wp = int(1.6 * SR)
    wp = np.zeros(n_wp, dtype=np.float32)
    step_10hz = int(SR / 10.0)
    for p0 in range(0, n_wp - 600, step_10hz):
        pt = np.linspace(0, 0.012, int(0.012 * SR), dtype=np.float32)
        pulse = np.tanh(np.sin(2 * np.pi * 880.0 * pt) * 2.4) * np.exp(-pt * 210.0) * 0.25
        wp[p0 : p0 + len(pulse)] += pulse
    kit["woodpecker_pulse"] = wp

    # 7. Shortwave HF Radio Static + Morse/Heterodyne Whistle
    t_r = np.linspace(0, 1.4, int(1.4 * SR), dtype=np.float32)
    het = np.sin(2 * np.pi * (1120.0 + 90.0 * np.sin(2 * np.pi * 2.5 * t_r)) * t_r) * 0.08
    stat = lowpass_noise(rng, len(t_r), taps=10) * 0.14
    env_r = np.maximum(0.0, np.sin(np.pi * (t_r / 1.4)))
    kit["radio_static"] = ((het + stat) * env_r).astype(np.float32)

    # 8. KGB Dossier Ink Stamp Slam
    t_st = np.linspace(0, 0.24, int(0.24 * SR), dtype=np.float32)
    stamp = (
        np.sin(2 * np.pi * 92.0 * t_st) * np.exp(-t_st * 24.0) * 0.50
        + lowpass_noise(rng, len(t_st), taps=10) * np.exp(-t_st * 36.0) * 0.28
    )
    kit["stamp"] = stamp.astype(np.float32)

    # 9. Archival Recon Camera Shutter
    t_sh = np.linspace(0, 0.16, int(0.16 * SR), dtype=np.float32)
    shutter = lowpass_noise(rng, len(t_sh), taps=6) * np.exp(-t_sh * 48.0) * 0.30
    kit["shutter"] = shutter.astype(np.float32)

    # 10. Telemetry UI Tick
    t_u = np.linspace(0, 0.08, int(0.08 * SR), dtype=np.float32)
    kit["ui_tick"] = (np.sin(2 * np.pi * 1480.0 * t_u) * np.exp(-t_u * 65.0) * 0.20).astype(np.float32)

    return kit


def synthesize_chernobyl_dark_score(total_sec: float, rng: np.random.Generator) -> np.ndarray:
    """Evolving Hildur Guðnadóttir-inspired dark cello/turbine drone + dosimeter tension pulse."""
    n_total = int(np.ceil(total_sec * SR)) + SR
    bed = np.zeros((n_total, 2), dtype=np.float32)

    # 8 somber Cold War minor/Phrygian root progressions (D2 -> Bb1 -> G1 -> A1 -> C2 -> F1 -> E1 -> D1)
    chords = [
        (73.42, 110.00, 146.83),
        (58.27, 87.31, 130.81),
        (49.00, 73.42, 116.54),
        (55.00, 82.41, 123.47),
        (65.41, 98.00, 146.83),
        (43.65, 65.41, 103.83),
        (41.20, 61.74, 98.00),
        (73.42, 103.83, 146.83),
    ]

    block_len = int(14.0 * SR)
    num_blocks = int(np.ceil(n_total / block_len))

    for b in range(num_blocks):
        i0 = b * block_len
        i1 = min(n_total, (b + 1) * block_len)
        m = i1 - i0
        t = np.arange(m, dtype=np.float32) / SR
        f1, f2, f3 = chords[b % len(chords)]

        # Bowed cello-like warm analog drone
        slow_lfo = 0.72 + 0.28 * np.sin(2 * np.pi * 0.09 * t)
        left = (
            np.sin(2 * np.pi * f1 * t) * 0.085
            + np.sin(2 * np.pi * (f2 * 1.002) * t) * 0.052
            + np.sin(2 * np.pi * f3 * t) * 0.030
        ) * slow_lfo
        right = (
            np.sin(2 * np.pi * (f1 * 0.999) * t) * 0.085
            + np.sin(2 * np.pi * f2 * t) * 0.052
            + np.sin(2 * np.pi * (f3 * 1.003) * t) * 0.030
        ) * slow_lfo

        # Subtle sub-heartbeat tension pulse (66 -> 76 BPM)
        bpm = 66.0 + 10.0 * (b / max(1, num_blocks - 1))
        p_phase = (t * (bpm / 60.0)) % 1.0
        pulse = (
            np.sin(2 * np.pi * 48.0 * (p_phase / 1.15))
            * np.minimum(1.0, p_phase * 25.0)
            * np.exp(-p_phase * 9.6)
            * 0.080
        )

        air_l = lowpass_noise(rng, m, taps=32) * 0.013
        air_r = lowpass_noise(rng, m, taps=32) * 0.013

        bed[i0:i1, 0] = left + pulse + air_l
        bed[i0:i1, 1] = right + pulse + air_r

    fi_n = min(n_total, int(0.8 * SR))
    fo_n = min(n_total, int(1.8 * SR))
    bed[:fi_n, :] *= np.linspace(0.0, 1.0, fi_n, dtype=np.float32)[:, None]
    bed[-fo_n:, :] *= np.linspace(1.0, 0.0, fo_n, dtype=np.float32)[:, None]
    return bed


async def main():
    print("[Chernobyl 10Min] Synthesizing 40 investigative shots with Edge-TTS...")
    sem = asyncio.Semaphore(4)
    tasks = [synth_shot(shot, sem) for shot in SHOT_SCRIPT]
    shot_results = await asyncio.gather(*tasks)
    shot_results.sort(key=lambda r: r["shot"]["shotId"])

    raw_vo_sum = sum(r["durationSec"] for r in shot_results)
    min_target_sec = 620.0
    base_overhead = 8 * 1.45 + 40 * (0.28 + 0.42) + 1.2
    extra_per_shot = max(0.0, (min_target_sec - (raw_vo_sum + base_overhead)) / len(shot_results))

    cursor_sec = 0.0
    shots_timeline = []
    chapters_timeline = []
    all_cues = []
    seen_chapters = set()

    for idx, res in enumerate(shot_results):
        shot = res["shot"]
        ch_id = shot["chapterId"]
        is_chapter_start = ch_id not in seen_chapters
        if is_chapter_start:
            seen_chapters.add(ch_id)

        lead_pad = (1.45 if is_chapter_start else 0.28) + extra_per_shot * 0.35
        tail_pad = (1.35 if idx == len(shot_results) - 1 else 0.42) + extra_per_shot * 0.65

        shot_start_sec = cursor_sec
        start_frame = int(round(shot_start_sec * FPS))
        shot_start_sec = start_frame / FPS

        voice_start_sec = shot_start_sec + lead_pad
        shot_end_sec = voice_start_sec + res["durationSec"] + tail_pad
        end_frame = int(round(shot_end_sec * FPS))
        shot_end_sec = end_frame / FPS
        cursor_sec = shot_end_sec

        if is_chapter_start:
            ch_meta = next(c for c in CHAPTERS if c["chapterId"] == ch_id)
            chapters_timeline.append(
                {
                    "chapterId": ch_id,
                    "code": ch_meta["code"],
                    "title": ch_meta["title"],
                    "startFrame": start_frame,
                    "startSec": round(shot_start_sec, 2),
                }
            )

        cues = align_cues_and_words(shot, voice_start_sec, res["durationSec"], res["wordsRel"])
        all_cues.extend(cues)

        shots_timeline.append(
            {
                "shotId": shot["shotId"],
                "chapterId": ch_id,
                "isChapterStart": is_chapter_start,
                "slug": shot["slug"],
                "sfx": shot.get("sfx", "ui_tick"),
                "startFrame": start_frame,
                "endFrame": end_frame,
                "durationInFrames": end_frame - start_frame,
                "voiceStartSec": round(voice_start_sec, 3),
                "samples": res["samples"],
            }
        )

    for ci in range(len(chapters_timeline)):
        chapters_timeline[ci]["endFrame"] = (
            chapters_timeline[ci + 1]["startFrame"]
            if ci + 1 < len(chapters_timeline)
            else shots_timeline[-1]["endFrame"]
        )

    total_frames = shots_timeline[-1]["endFrame"]
    total_sec = total_frames / FPS
    mins = int(total_sec // 60)
    secs = total_sec - mins * 60
    print(f"[Chernobyl 10Min] Master Duration: {mins:02d}:{secs:05.2f} ({total_sec:.2f}s / {total_frames} frames @ {FPS}fps)")

    rng = np.random.default_rng(19860426)
    sfx = build_chernobyl_sfx_kit(rng)
    bed = synthesize_chernobyl_dark_score(total_sec, rng)
    n_total = bed.shape[0]

    vo_L = np.zeros(n_total, dtype=np.float32)
    vo_R = np.zeros(n_total, dtype=np.float32)
    duck = np.ones(n_total, dtype=np.float32)

    for st in shots_timeline:
        s_i = int(st["voiceStartSec"] * SR)
        samp = st["samples"]
        e_i = min(n_total, s_i + len(samp))
        if e_i > s_i:
            vo_L[s_i:e_i] += samp[: e_i - s_i]
            vo_R[s_i:e_i] += samp[: e_i - s_i]
            d0 = max(0, s_i - int(0.08 * SR))
            d1 = min(n_total, e_i + int(0.12 * SR))
            duck[d0:d1] = np.minimum(duck[d0:d1], 0.38)

    smooth_k = np.ones(int(0.05 * SR), dtype=np.float32) / int(0.05 * SR)
    duck_s = np.convolve(duck, smooth_k, mode="same")
    bed[:, 0] *= duck_s
    bed[:, 1] *= duck_s

    sfx_events: list[tuple[float, str, float]] = []
    for i, st in enumerate(shots_timeline):
        cut_s = st["startFrame"] / FPS
        if st["isChapterStart"]:
            sfx_events.append((cut_s + 0.04, "chapter_boom", 0.72))
        elif i > 0:
            sfx_events.append((max(0.0, cut_s - 3.0 / FPS), "whoosh", 0.58))

        kind = st["sfx"]
        offset = 0.85 if st["isChapterStart"] else 0.18
        if kind in sfx:
            sfx_events.append((cut_s + offset, kind, 0.62))

    for ev_sec, kind, gain in sfx_events:
        clip = sfx[kind]
        s_i = int(ev_sec * SR)
        e_i = min(n_total, s_i + len(clip))
        if e_i > s_i:
            bed[s_i:e_i, 0] += clip[: e_i - s_i] * gain
            bed[s_i:e_i, 1] += clip[: e_i - s_i] * gain * 0.96

    mix = np.zeros_like(bed)
    mix[:, 0] = bed[:, 0] * 0.76 + vo_L * 0.96
    mix[:, 1] = bed[:, 1] * 0.76 + vo_R * 0.96
    mix = np.tanh(mix * 0.95) * 0.86

    OUT_AUDIO.parent.mkdir(parents=True, exist_ok=True)
    wav_master = STUDIO_DIR / "out" / "chernobyl_10min_tmp.wav"
    pcm16 = np.clip(np.round(mix * 32767.0), -32768, 32767).astype(np.int16)
    with wave.open(str(wav_master), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

    print("[Chernobyl 10Min] Normalizing master broadcast audio (-16 LUFS)...")
    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(wav_master),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=9",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(OUT_AUDIO),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    wav_master.unlink(missing_ok=True)

    shots_export = [
        {
            "shotId": s["shotId"],
            "chapterId": s["chapterId"],
            "isChapterStart": s["isChapterStart"],
            "slug": s["slug"],
            "startFrame": s["startFrame"],
            "endFrame": s["endFrame"],
            "durationInFrames": s["durationInFrames"],
        }
        for s in shots_timeline
    ]

    print("\n=== YOUTUBE CHAPTER TIMESTAMPS ===")
    for ch in chapters_timeline:
        m = int(ch["startSec"] // 60)
        s = int(ch["startSec"] % 60)
        print(f"{m:02d}:{s:02d} {ch['code']} — {ch['title']}")

    OUT_TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    ts_content = f"""// Auto-generated by scripts/build_chernobyl_10min_audio.py
import type {{ CaptionCue }} from "./alcatrazPilotTimeline";
import type {{ Docu10MinShotTiming, DocuChapterTiming }} from "./alcatraz10MinTimeline";

export const CHERNOBYL_10MIN_FPS = {FPS};
export const CHERNOBYL_10MIN_TOTAL_FRAMES = {total_frames};
export const CHERNOBYL_10MIN_DURATION_SEC = {round(total_sec, 3)};

export const CHERNOBYL_10MIN_CHAPTERS: readonly DocuChapterTiming[] = {json.dumps(chapters_timeline, indent=2)} as const;

export const CHERNOBYL_10MIN_SHOTS: readonly Docu10MinShotTiming[] = {json.dumps(shots_export, indent=2)} as const;

export const CHERNOBYL_10MIN_CUES: readonly CaptionCue[] = {json.dumps(all_cues, indent=2)} as const;
"""
    OUT_TIMELINE.write_text(ts_content, encoding="utf-8")
    print(f"[Chernobyl 10Min] Done! Saved {OUT_AUDIO.name} & {OUT_TIMELINE.name} ({len(all_cues)} cues).")


if __name__ == "__main__":
    asyncio.run(main())
