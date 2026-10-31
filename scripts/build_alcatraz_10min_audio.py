import asyncio
import inspect
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

TMP_VO_DIR = STUDIO_DIR / "out" / "vo_alcatraz_10min_tmp"
OUT_AUDIO = STUDIO_DIR / "public" / "audio" / "alcatraz_10min_master.mp3"
OUT_TIMELINE = STUDIO_DIR / "src" / "ifnoir" / "alcatraz10MinTimeline.ts"

SR = 44100
FPS = 30

# Investigative, gripping US cold-case documentary narrator
VOICE_ID = "en-US-AndrewNeural"
VOICE_RATE = "+3%"
VOICE_PITCH = "-2Hz"

CHAPTERS = [
    {"chapterId": 1, "code": "CHAPTER I", "title": "FILE 70-26455: THE OFFICIAL LIE"},
    {"chapterId": 2, "code": "CHAPTER II", "title": "THE 6 PM VACUUM DRILL & ROOFTOP FACTORY"},
    {"chapterId": 3, "code": "CHAPTER III", "title": "CELL B-136: THE FOURTH MAN'S DOUBLE GAME"},
    {"chapterId": 4, "code": "CHAPTER IV", "title": "THE 45-MINUTE TIDE & THE 1 AM MYSTERY BOAT"},
    {"chapterId": 5, "code": "CHAPTER V", "title": "PLATE KPB-076 & THE GHOST SHIP NOREFJELL"},
    {"chapterId": 6, "code": "CHAPTER VI", "title": "FUNERAL DISGUISES & THE 1975 BRAZIL PHOTO"},
    {"chapterId": 7, "code": "CHAPTER VII", "title": "THE CLASSIFIED 2013 CONFESSION LETTER"},
    {"chapterId": 8, "code": "CHAPTER VIII", "title": "283 DAYS LATER: WASHINGTON'S COVER-UP"},
]

# 40 investigative shots (~15.5s average = ~10m 25s total) packed with declassified FBI evidence & untold facts
SHOT_SCRIPT = [
    # ==================== CHAPTER 1 ====================
    {
        "shotId": 1,
        "chapterId": 1,
        "slug": "ch1_hook_myth",
        "sfx": "foghorn",
        "text": (
            "Everyone thinks they know what happened on June eleventh, nineteen sixty-two. "
            "Three bank robbers scraped their walls with spoons, tucked fake heads into bed, "
            "and drowned in freezing San Francisco Bay. That is the story J. Edgar Hoover ordered America to believe."
        ),
        "cues": [
            "JUNE 11, 1962\nTHE STORY EVERYONE KNOWS",
            "THREE BANK ROBBERS\nARMED WITH SPOONS",
            "FAKE HEADS IN BED\nDROWNED IN THE BAY",
            "THE STORY J. EDGAR HOOVER\nORDERED AMERICA TO BELIEVE",
        ],
    },
    {
        "shotId": 2,
        "chapterId": 1,
        "slug": "ch1_fbi_vault_teletype",
        "sfx": "stamp",
        "text": (
            "Inside FBI Case File seventy, twenty-six four-fifty-five—spanning seventeen volumes "
            "of declassified teletypes, buried police logs, and a secret twenty-thirteen confession letter—"
            "a radically different truth emerges. And almost none of it ever made your history books."
        ),
        "cues": [
            "FBI CASE FILE 70-26455\n17 DECLASSIFIED VOLUMES",
            "BURIED POLICE LOGS &\nSUPPRESSED TELETYPES",
            "A SECRET 2013\nCONFESSION LETTER",
            "NONE OF IT MADE\nYOUR HISTORY BOOKS",
        ],
    },
    {
        "shotId": 3,
        "chapterId": 1,
        "slug": "ch1_saltwater_rot",
        "sfx": "iron_clang",
        "text": (
            "Start with Alcatraz's darkest engineering secret. Built to cage Al Capone, "
            "the prison pumped raw salt water straight from the bay into every cell toilet. "
            "Over twenty-eight years, leaking brine dissolved the mortar behind Cellblock B into wet chalk."
        ),
        "cues": [
            "ALCATRAZ'S DARKEST\nENGINEERING SECRET",
            "RAW BAY SALTWATER PUMPED\nINTO EVERY CELL TOILET",
            "28 YEARS OF LEAKING BRINE\nBEHIND CELLBLOCK B",
            "SOLID CONCRETE ROTTED\nINTO WET CHALK",
        ],
    },
    {
        "shotId": 4,
        "chapterId": 1,
        "slug": "ch1_budget_cuts_bblock",
        "sfx": "shutter",
        "text": (
            "By nineteen sixty-one, federal engineers warned Washington the cellhouse was rotting from the inside, "
            "while budget cuts left the north gun gallery unguarded at night. "
            "Into adjacent cells walked Frank Morris—IQ one thirty-three—beside brothers John and Clarence Anglin."
        ),
        "cues": [
            "1961: ENGINEERS WARNED\nTHE WALLS WERE ROTTING",
            "NIGHT GUN GALLERY LEFT\nUNGUARDED TO SAVE PAYROLL",
            "FRANK MORRIS: IQ 133\nTOP TWO PERCENT GENIUS",
            "BESIDE BANK ROBBERS\nJOHN & CLARENCE ANGLIN",
        ],
    },
    {
        "shotId": 5,
        "chapterId": 1,
        "slug": "ch1_heated_showers_irony",
        "sfx": "ui_tick",
        "text": (
            "Even the warden's cleverest trap backfired. Alcatraz heated every inmate shower to ninety degrees "
            "so prisoners could never acclimate their bodies to fifty-two-degree bay water. "
            "Morris realized immediately: they couldn't swim across—they had to engineer a boat."
        ),
        "cues": [
            "THE WARDEN'S CLEVEREST\nSECURITY TRAP BACKFIRED",
            "90°F HEATED SHOWERS TO\nPREVENT COLD ACCLIMATION",
            "52°F BAY WATER MEANT\nSWIMMING WAS SUICIDE",
            "MORRIS REALIZED: WE HAVE\nTO ENGINEER A BOAT",
        ],
    },
    # ==================== CHAPTER 2 ====================
    {
        "shotId": 6,
        "chapterId": 2,
        "slug": "ch2_spoon_silver_brazing",
        "sfx": "spoon_scrape",
        "text": (
            "Legend says they dug through concrete with plain dining spoons. Declassified FBI lab reports "
            "reveal metallurgical brilliance. They stole silver dimes, melted coin silver with matchbooks, "
            "and brazed hardened steel cutting edges onto heavy cafeteria spoon handles."
        ),
        "cues": [
            "MYTH: PLAIN DINING SPOONS\nFACT: FBI METALLURGY REPORT",
            "STOLEN SILVER DIMES\nMELTED OVER MATCHBOOKS",
            "BRAZED HARDENED STEEL\nCUTTING BLADES",
            "ONTO HEAVY CAFETERIA\nSPOON HANDLES",
        ],
    },
    {
        "shotId": 7,
        "chapterId": 2,
        "slug": "ch2_vacuum_motor_music_hour",
        "sfx": "drill_whir",
        "text": (
            "Even wilder, they smuggled a burned-out electric motor from a prison vacuum cleaner "
            "and rewound it into a homemade power drill. Every evening at six PM during mandatory Music Hour, "
            "Morris played his accordion loudly to drown out the electric motor."
        ),
        "cues": [
            "STOLEN ELECTRIC MOTOR\nFROM A PRISON VACUUM",
            "REWOUND INTO A HOMEMADE\nPOWER CONCRETE DRILL",
            "EVERY EVENING AT 6:00 PM\nDURING MUSIC HOUR",
            "MORRIS PLAYED HIS ACCORDION\nTO MASK THE DRILL NOISE",
        ],
    },
    {
        "shotId": 8,
        "chapterId": 2,
        "slug": "ch2_periscope_camouflage",
        "sfx": "shutter",
        "text": (
            "While one man drilled, a lookout watched the corridor guard's boots through a cardboard-and-mirror periscope. "
            "Before lights-out, they sealed the eight-by-eleven-inch hole behind fake cardboard grilles "
            "tinted with green prison soap to match the cell wall."
        ),
        "cues": [
            "CARDBOARD & MIRROR PERISCOPE\nTRACKED THE GUARD'S BOOTS",
            "8.5 × 11 INCH TUNNEL\nSEALED BEFORE LOCKDOWN",
            "FAKE CARDBOARD GRILLES\nTINTED WITH GREEN SOAP",
            "INVISIBLE EVEN THREE FEET\nFROM THE CELL BARS",
        ],
    },
    {
        "shotId": 9,
        "chapterId": 2,
        "slug": "ch2_rooftop_workshop",
        "sfx": "iron_clang",
        "text": (
            "Behind those vents lay a dark, three-story utility corridor nobody patrolled. "
            "Night after night, the men climbed thirty feet of vertical plumbing pipes to the top of Cellblock B, "
            "hanging prison blankets to hide a secret rooftop workshop directly over the guards."
        ),
        "cues": [
            "BEHIND THE CELLS LAY AN\nUNGUARDED UTILITY SHAFT",
            "CLIMBED 30 FEET UP\nVERTICAL PLUMBING PIPES",
            "HUNG PRISON BLANKETS\nATOP CELLBLOCK B",
            "A SECRET WORKSHOP RIGHT\nABOVE THE GUARDS' HEADS",
        ],
    },
    {
        "shotId": 10,
        "chapterId": 2,
        "slug": "ch2_steam_pipe_vulcanization",
        "sfx": "stamp",
        "text": (
            "Guided by a March nineteen sixty-two issue of Popular Mechanics found in Morris's cell, "
            "they stitched fifty stolen rubber raincoats into a fourteen-foot raft, vulcanized the seams "
            "against live steam pipes, and rebuilt a concertina instrument into an air pump."
        ),
        "cues": [
            "MARCH 1962 BLUEPRINT:\nPOPULAR MECHANICS MAGAZINE",
            "50 STOLEN RAINCOATS\nSTITCHED INTO A 14-FT RAFT",
            "SEAMS VULCANIZED AGAINST\n212°F PRISON STEAM PIPES",
            "MUSICAL CONCERTINA REBUILT\nINTO AN AIR BELLOWS",
        ],
    },
    # ==================== CHAPTER 3 ====================
    {
        "shotId": 11,
        "chapterId": 3,
        "slug": "ch3_allen_west_reveal",
        "sfx": "stamp",
        "text": (
            "Now comes the first twist Hollywood barely mentions: there weren't three conspirators—there were four. "
            "Cell B-one-thirty-six held career car thief Allen Clayton West, the very inmate who first spotted "
            "the unsealed roof ventilator while sweeping the cellhouse."
        ),
        "cues": [
            "THE TWIST RARELY TOLD:\nTHERE WERE FOUR MEN",
            "CELL B-136: CAR THIEF\nALLEN CLAYTON WEST",
            "THE MAN WHO FIRST FOUND\nTHE ROOF VENTILATOR",
            "WHY WAS THE ARCHITECT\nLEFT BEHIND AT MIDNIGHT?",
        ],
    },
    {
        "shotId": 12,
        "chapterId": 3,
        "slug": "ch3_portland_cement_mistake",
        "sfx": "spoon_scrape",
        "text": (
            "Days before the breakout, West's crumbling vent opening grew so loose his fake cover nearly fell onto the floor. "
            "To patch the rim, West mixed real Portland cement taken from a maintenance bag. "
            "When the cement cured, it locked his own escape hatch solid."
        ),
        "cues": [
            "WEST'S CRUMBLING VENT\nGREW TOO WIDE TO HOLD",
            "HE PATCHED THE EDGES WITH\nREAL PORTLAND CEMENT",
            "WHEN THE CEMENT CURED\nIT TURNED TO SOLID STONE",
            "ALLEN WEST ACCIDENTALLY\nSEALED HIMSELF INSIDE",
        ],
    },
    {
        "shotId": 13,
        "chapterId": 3,
        "slug": "ch3_145am_empty_roof",
        "sfx": "iron_clang",
        "text": (
            "At nine-thirty PM on June eleventh, Morris and the Anglins crawled into the corridor "
            "while West bled his knuckles chipping at hardened cement. When West finally broke onto the roof "
            "at one-forty-five AM, his partners—and the only raft—were already gone."
        ),
        "cues": [
            "9:30 PM: MORRIS & ANGLINS\nENTER THE SHAFT",
            "WEST FRANTICALLY CHIPS\nAT HIS CEMENTED GRILLE",
            "1:45 AM: WEST FINALLY\nREACHES THE PRISON ROOF",
            "HIS PARTNERS AND THE RAFT\nARE ALREADY GONE",
        ],
    },
    {
        "shotId": 14,
        "chapterId": 3,
        "slug": "ch3_dummy_head_morning_shock",
        "sfx": "shutter",
        "text": (
            "Down on the tier, three dummy heads molded from toilet paper, soap, paint, and real human hair "
            "from the prison barbershop fooled six midnight flashlight checks. "
            "At seven-fifteen AM, an officer nudged Morris's pillow—and screamed as a human head hit the floor."
        ),
        "cues": [
            "SOAP, TOILET PAPER &\nREAL BARBERSHOP HAIR",
            "FOOLED SIX CONSECUTIVE\nNIGHT FLASHLIGHT CHECKS",
            "7:15 AM SIREN: GUARD\nPOKES MORRIS'S PILLOW",
            "THE LIFELIKE DUMMY HEAD\nROLLS ONTO THE CONCRETE",
        ],
    },
    {
        "shotId": 15,
        "chapterId": 3,
        "slug": "ch3_angel_island_deception",
        "sfx": "stamp",
        "text": (
            "In exchange for zero prosecution, Allen West handed FBI agents every detail of the plot. "
            "He swore their target was Angel Island, two miles north. "
            "Decades later, cold-case investigators asked a chilling question: did West feed the FBI a decoy destination?"
        ),
        "cues": [
            "WEST STRUCK AN IMMUNITY\nDEAL WITH THE FBI",
            "SWORE THEIR TARGET WAS\nANGEL ISLAND TO THE NORTH",
            "HUNDREDS OF AGENTS SWARMED\nTHE NORTHERN SHORELINE",
            "OR DID WEST DELIBERATELY\nSEND THE FBI THE WRONG WAY?",
        ],
    },
    # ==================== CHAPTER 4 ====================
    {
        "shotId": 16,
        "chapterId": 4,
        "slug": "ch4_angel_island_floating_props",
        "sfx": "foghorn",
        "text": (
            "Search vessels soon pulled a wooden paddle and a rubber-wrapped packet of Anglin family addresses "
            "out of the water near Angel Island. Hoover's press office declared the raft had sunk. "
            "Yet Clarence Anglin never let go of those family photos—unless he wanted them found."
        ),
        "cues": [
            "FOUND NEAR ANGEL ISLAND:\nONE PADDLE & PHOTO POUCH",
            "HOOVER'S PRESS OFFICE\nDECLARED THEM DROWNED",
            "WHY SEAL FAMILY PHOTOS\nIN WATERPROOF RUBBER...",
            "AND TOSS THEM INTO\nTHE NORTHBOUND CURRENT?",
        ],
    },
    {
        "shotId": 17,
        "chapterId": 4,
        "slug": "ch4_delft_supercomputer_model",
        "sfx": "ui_tick",
        "text": (
            "In twenty-fourteen, hydraulic engineers at Delft University fed the exact Coast Guard tide tables "
            "from June eleventh, nineteen sixty-two into a military-grade bay simulation. "
            "Launching before eleven-thirty PM meant certain death—swept straight out past the Golden Gate."
        ),
        "cues": [
            "2014: DELFT UNIVERSITY\nHYDRODYNAMIC SUPERCOMPUTER",
            "REBUILT EXACT JUNE 11, 1962\nCOAST GUARD TIDE LOGS",
            "LAUNCH BEFORE 11:30 PM:\nSWEPT INTO PACIFIC TO DIE",
            "LAUNCH AFTER 12:30 AM:\nPULLED DEEP INTO SOUTH BAY",
        ],
    },
    {
        "shotId": 18,
        "chapterId": 4,
        "slug": "ch4_horseshoe_bay_bullseye",
        "sfx": "whoosh",
        "text": (
            "But between eleven-thirty PM and midnight—the exact minute the powerhouse chimney hid them on the roof—"
            "a forty-five-minute slack-tide corridor curved straight into Horseshoe Bay beneath the Golden Gate's north tower. "
            "Survival odds suddenly jumped from zero to real."
        ),
        "cues": [
            "11:30 PM TO MIDNIGHT:\nTHE 45-MINUTE SLACK TIDE",
            "MATCHES THEIR EXACT\nROOFTOP DEPARTURE WINDOW",
            "CURRENT CURVES STRAIGHT\nINTO HORSESHOE BAY",
            "RIGHT BENEATH THE GOLDEN\nGATE'S NORTH TOWER",
        ],
    },
    {
        "shotId": 19,
        "chapterId": 4,
        "slug": "ch4_officer_checchi_witness",
        "sfx": "foghorn",
        "text": (
            "Then came the eyewitness the FBI refused to put on television. "
            "At one AM on June twelfth, San Francisco Police Officer Robert Checchi was patrolling Saint Francis Yacht Harbor "
            "when he spotted an unauthorized white boat idling in pitch darkness near Alcatraz."
        ),
        "cues": [
            "SWORN EYEWITNESS: SFPD\nOFFICER ROBERT CHECCHI",
            "1:00 AM, JUNE 12 AT\nST. FRANCIS YACHT HARBOR",
            "ILLEGAL WHITE CRUISER\nIDLING NEAR ALCATRAZ",
            "EVERY NAVIGATION LIGHT\nSWITCHED COMPLETELY OFF",
        ],
    },
    {
        "shotId": 20,
        "chapterId": 4,
        "slug": "ch4_checchi_buried_by_fbi",
        "sfx": "stamp",
        "text": (
            "Checchi watched for twenty minutes, assuming it was Coast Guard—until a flashlight flickered "
            "at the waterline, twin engines roared, and the cruiser raced west under the Golden Gate Bridge. "
            "FBI agents took Checchi's statement, filed it away, and never followed up."
        ),
        "cues": [
            "20 MINUTES IN DARKNESS\nTHEN A WATERLINE FLASHLIGHT",
            "ENGINES ROAR FULL THROTTLE\nUNDER GOLDEN GATE BRIDGE",
            "CHECCHI FILED AN OFFICIAL\nPOLICE REPORT THAT MORNING",
            "FBI AGENTS LOCKED HIS\nSTATEMENT IN THE VAULT",
        ],
    },
    # ==================== CHAPTER 5 ====================
    {
        "shotId": 21,
        "chapterId": 5,
        "slug": "ch5_stolen_1955_chevy",
        "sfx": "shutter",
        "text": (
            "Look at what happened on land just hours later. Across the Golden Gate in Marin County, "
            "police logged a stolen nineteen fifty-five blue Chevrolet sedan—California license plate "
            "K-P-B, zero-seven-six—taken within walking distance of the Marin headlands."
        ),
        "cues": [
            "HOURS LATER ACROSS THE\nBRIDGE IN MARIN COUNTY",
            "STOLEN VEHICLE REPORT:\n1955 BLUE CHEVROLET SEDAN",
            "CALIFORNIA LICENSE PLATE:\nKPB-076",
            "MINUTES FROM THE HORSESHOE\nBAY LANDING ZONE",
        ],
    },
    {
        "shotId": 22,
        "chapterId": 5,
        "slug": "ch5_stockton_highway_ambush",
        "sfx": "stamp",
        "text": (
            "That afternoon, eighty miles east in Stockton, California, a shaken driver reported being forced "
            "off the highway by three desperate men inside a speeding blue nineteen fifty-five Chevrolet. "
            "Declassified teletypes confirm the FBI tracked plate K-P-B zero-seven-six—while telling reporters nothing."
        ),
        "cues": [
            "80 MILES EAST IN\nSTOCKTON, CALIFORNIA",
            "MOTORIST RUN OFF THE ROAD\nBY THREE FRANTIC MEN",
            "DRIVING A MATCHING BLUE\n1955 CHEVROLET SEDAN",
            "FBI LOGGED PLATE KPB-076\nWHILE TELLING PRESS NOTHING",
        ],
    },
    {
        "shotId": 23,
        "chapterId": 5,
        "slug": "ch5_ss_norefjell_discovery",
        "sfx": "foghorn",
        "text": (
            "Yet five weeks later, the Pacific delivered a macabre twist. On July seventeenth, nineteen sixty-two, "
            "sailors aboard the Norwegian freighter S-S Norefjell, seventeen miles outside the Golden Gate, "
            "watched a human corpse drift past their hull face-down."
        ),
        "cues": [
            "JULY 17, 1962: 36 DAYS\nAFTER THE BREAKOUT",
            "NORWEGIAN FREIGHTER\nSS NOREFJELL AT SEA",
            "17 MILES WEST OF THE\nGOLDEN GATE BRIDGE",
            "A FACE-DOWN HUMAN CORPSE\nDRIFTS PAST THE HULL",
        ],
    },
    {
        "shotId": 24,
        "chapterId": 5,
        "slug": "ch5_blue_denim_controversy",
        "sfx": "ui_tick",
        "text": (
            "Deckhands swore the body wore heavy blue denim trousers identical to Alcatraz issue. "
            "Lacking cold storage, the freighter didn't stop and only notified officials in October. "
            "Was it bridge suicide Cecil Cornish—or did Frank Morris perish while the brothers survived?"
        ),
        "cues": [
            "CREW SWORE THE BODY WORE\nALCATRAZ BLUE DENIM PANTS",
            "SHIP NEVER RECOVERED IT;\nREPORTED MONTHS LATER",
            "CORONER THEORY: BRIDGE\nJUMPER CECIL CORNISH",
            "DARKER THEORY: MORRIS DIED\nWHILE THE ANGLINS MADE IT",
        ],
    },
    {
        "shotId": 25,
        "chapterId": 5,
        "slug": "ch5_raft_remnants_cronkhite",
        "sfx": "shutter",
        "text": (
            "Back on Marin's Cronkhite Beach, military searchers recovered a homemade raincoat life vest "
            "with deep human teeth marks bitten into the air valve—proof someone fought desperately in the surf, "
            "walked onto the sand, or slipped beneath the swell."
        ),
        "cues": [
            "CRONKHITE BEACH, MARIN:\nHOMEMADE LIFE PRESERVER",
            "DEEP HUMAN TEETH MARKS\nCLAMPED ON THE AIR VALVE",
            "PROOF SOMEONE FOUGHT THE\nFREEZING SURF TO SHORE",
            "YET ZERO BODIES EVER\nWASHED ONTO ANY BEACH",
        ],
    },
    # ==================== CHAPTER 6 ====================
    {
        "shotId": 26,
        "chapterId": 6,
        "slug": "ch6_underground_contacts",
        "sfx": "ui_tick",
        "text": (
            "If the Anglin brothers reached dry land, they had help waiting. "
            "Grown up in Ruskin, Florida, John and Clarence knew childhood friend Fred Brizzi—a daring bush pilot "
            "flying contraband across the Caribbean straight into Brazil, beyond easy U.S. extradition."
        ),
        "cues": [
            "HOW DO MOST-WANTED MEN\nVANISH WITHOUT A TRACE?",
            "RUSKIN, FLORIDA CONNECTION:\nPILOT FRED BRIZZI",
            "SMUGGLING ROUTES STRAIGHT\nINTO SOUTH AMERICA",
            "BRAZIL: OUTSIDE ROUTINE\n1960s U.S. EXTRADITION",
        ],
    },
    {
        "shotId": 27,
        "chapterId": 6,
        "slug": "ch6_mothers_day_flowers",
        "sfx": "shutter",
        "text": (
            "For over a decade, FBI wiretaps surrounded the Anglin homestead in Florida. "
            "Yet every single Mother's Day from nineteen sixty-three onward, anonymous florists delivered fresh roses "
            "to Marie Anglin—accompanied by unsigned cards family members recognized instantly."
        ),
        "cues": [
            "FBI WIRETAPS SURROUNDED\nTHE ANGLIN FLORIDA HOME",
            "EVERY MOTHER'S DAY\nFROM 1963 TO 1973",
            "ANONYMOUS BOUQUETS OF\nROSES ARRIVED AT THE DOOR",
            "UNSIGNED CARDS MATCHING\nHER MISSING SONS",
        ],
    },
    {
        "shotId": 28,
        "chapterId": 6,
        "slug": "ch6_1973_funeral_disguise",
        "sfx": "foghorn",
        "text": (
            "When Marie Anglin passed away in nineteen seventy-three, armed FBI agents staked out her Florida funeral. "
            "Relatives later confessed that two six-foot-tall women in heavy makeup, dresses, and wigs "
            "wept silently over her coffin—then drove off right past federal surveillance."
        ),
        "cues": [
            "1973: ARMED FBI AGENTS\nSTAKE OUT MARIE'S FUNERAL",
            "TWO SIX-FOOT-TALL 'WOMEN'\nIN WIGS & HEAVY MAKEUP",
            "STOOD WEEPING SILENTLY\nBESIDE HER OPEN COFFIN",
            "SLIPPED PAST FEDERAL\nAGENTS WITHOUT AN ARREST",
        ],
    },
    {
        "shotId": 29,
        "chapterId": 6,
        "slug": "ch6_1975_brazil_kodachrome",
        "sfx": "shutter",
        "text": (
            "Then in nineteen seventy-five, pilot Fred Brizzi delivered startling physical proof to the Anglin family: "
            "a Kodachrome color photograph snapped on a ranch near Rio de Janeiro, Brazil, "
            "showing two tanned Americans standing beside a towering tropical termite mound."
        ),
        "cues": [
            "1975: PILOT FRED BRIZZI\nRETURNS FROM BRAZIL",
            "HANDS THE FAMILY A COLOR\nKODACHROME SNAPSHOT",
            "RANCH OUTSIDE RIO DE JANEIRO\nBESIDE A TERMITE MOUND",
            "TWO LEAN AMERICANS HIDING\nBEHIND DARK SUNGLASSES",
        ],
    },
    {
        "shotId": 30,
        "chapterId": 6,
        "slug": "ch6_michael_streed_biometrics",
        "sfx": "stamp",
        "text": (
            "Decades later, veteran forensic facial-identification expert Michael Streed overlaid the nineteen seventy-five "
            "Brazil photo onto nineteen sixty-two Alcatraz mugshots. Measuring ear-tragus cartilage, brow ridges, "
            "and chin ratios, Streed concluded it was 'more likely than not' John and Clarence Anglin."
        ),
        "cues": [
            "FORENSIC BIOMETRIC ANALYST\nMICHAEL STREED TESTED IT",
            "MEASURED EAR CARTILAGE,\nJAWLINES & BROW RIDGES",
            "OVERLAID DIRECTLY ONTO\n1962 ALCATRAZ MUGSHOTS",
            "VERDICT: 'MORE LIKELY THAN\nNOT' JOHN & CLARENCE ANGLIN",
        ],
    },
    # ==================== CHAPTER 7 ====================
    {
        "shotId": 31,
        "chapterId": 7,
        "slug": "ch7_2013_sfpd_letter_arrival",
        "sfx": "stamp",
        "text": (
            "Just when skeptics thought the trail had gone cold forever, an envelope arrived in twenty-thirteen "
            "at the San Francisco Police Department's Richmond Station. What was written inside shook federal investigators "
            "so deeply they classified the letter for five years."
        ),
        "cues": [
            "2013: AN ENVELOPE ARRIVES\nAT SFPD RICHMOND STATION",
            "RUSHED DIRECTLY TO FEDERAL\nCOLD-CASE INVESTIGATORS",
            "KEPT COMPLETELY SECRET\nFROM THE PUBLIC UNTIL 2018",
            "WHAT WAS WRITTEN INSIDE\nSTUNNED QUANTICO",
        ],
    },
    {
        "shotId": 32,
        "chapterId": 7,
        "slug": "ch7_letter_verbatim_quote",
        "sfx": "shutter",
        "text": (
            "Leaked to reporters in January twenty-eighteen, the shaky handwriting read verbatim: "
            "'My name is John Anglin. I escaped from Alcatraz in June nineteen sixty-two with my brother Clarence "
            "and Frank Morris. I am eighty-three years old and in bad shape. Yes, we all made it that night—but barely.'"
        ),
        "cues": [
            "'MY NAME IS JOHN ANGLIN.\nI ESCAPED IN JUNE 1962'",
            "'I AM 83 YEARS OLD\nAND IN BAD SHAPE'",
            "'YES, WE ALL MADE IT\nTHAT NIGHT — BUT BARELY!'",
            "UNSEALED FOR THE FIRST\nTIME IN JANUARY 2018",
        ],
    },
    {
        "shotId": 33,
        "chapterId": 7,
        "slug": "ch7_cancer_bargain_2008_2011",
        "sfx": "ui_tick",
        "text": (
            "The author claimed he lived quietly in Seattle for years, moved to North Dakota, "
            "and was now battling cancer in Southern California. According to the letter, "
            "Frank Morris died in October two thousand eight in an unmarked grave, and Clarence passed away in twenty-eleven."
        ),
        "cues": [
            "CLAIMED DECADES HIDING IN\nSEATTLE & NORTH DAKOTA",
            "NOW DYING OF CANCER IN\nSOUTHERN CALIFORNIA",
            "FRANK MORRIS DIED IN\nOCTOBER 2008 UNDER AN ALIAS",
            "BROTHER CLARENCE ANGLIN\nPASSED AWAY IN 2011",
        ],
    },
    {
        "shotId": 34,
        "chapterId": 7,
        "slug": "ch7_tv_code_offer",
        "sfx": "ui_tick",
        "text": (
            "Then came the deal: 'If you announce on TV that I will be promised to first go to jail for no more than a year "
            "and get medical attention, I will write back to let you know exactly where I am.' "
            "The FBI laboratory swept every millimeter for DNA, fingerprints, and ink."
        ),
        "cues": [
            "'PROMISE ON TV: ONE YEAR\nIN JAIL & CANCER CARE'",
            "'I WILL WRITE BACK WITH\nMY EXACT LOCATION'",
            "FBI QUANTICO LAB TESTED\nEVERY MILLIMETER OF PAPER",
            "SWEPT FOR DNA PROFILES,\nPRINTS & HANDWRITING",
        ],
    },
    {
        "shotId": 35,
        "chapterId": 7,
        "slug": "ch7_inconclusive_verdict",
        "sfx": "stamp",
        "text": (
            "After comparing the shaky eighty-three-year-old penmanship against nineteen sixty-two prison forms, "
            "Quantico stamped the forensic report 'Inconclusive.' Half a century of aging prevented certainty—yet "
            "the world's top crime lab could not rule John Anglin out."
        ),
        "cues": [
            "51 YEARS OF AGING ALTERS\nHUMAN PENMANSHIP",
            "OFFICIAL QUANTICO VERDICT:\nFORENSICALLY INCONCLUSIVE",
            "CRUCIALLY: THE FBI COULD\nNOT PROVE IT WAS A HOAX",
            "U.S. MARSHALS KEPT THE\nCOLD CASE WIDE OPEN",
        ],
    },
    # ==================== CHAPTER 8 ====================
    {
        "shotId": 36,
        "chapterId": 8,
        "slug": "ch8_hoover_ego_coverup",
        "sfx": "iron_clang",
        "text": (
            "Step back and look at every buried clue together: Officer Checchi's one AM boat, "
            "the stolen blue fifty-five Chevy, the forty-five-minute Horseshoe Bay tide, the Brazil ranch photo, "
            "and the twenty-thirteen letter. Why did Washington insist they drowned? Institutional pride."
        ),
        "cues": [
            "THE 1 AM BOAT · PLATE KPB-076\nTHE 45-MINUTE SLACK TIDE",
            "THE 1975 BRAZIL PHOTO &\nTHE 2013 CANCER LETTER",
            "WHY INSIST THEY DROWNED\nWITH ZERO BODIES?",
            "INSTITUTIONAL PRIDE OF\nJ. EDGAR HOOVER'S EMPIRE",
        ],
    },
    {
        "shotId": 37,
        "chapterId": 8,
        "slug": "ch8_march_1963_shutdown_newsreel",
        "sfx": "iron_clang",
        "text": (
            "Alcatraz existed as a psychological weapon—proof no man could beat federal justice. "
            "Yet just two hundred eighty-three days after Morris and the Anglins vanished, on March twenty-first, "
            "nineteen sixty-three, Attorney General Robert Kennedy chained the final prisoners and shut Alcatraz forever."
        ),
        "cues": [
            "ALCATRAZ WAS AMERICA'S\nPSYCHOLOGICAL SYMBOL",
            "JUST 283 DAYS AFTER\nTHE SPOON ESCAPE...",
            "MARCH 21, 1963: ROBERT\nKENNEDY SHUTS ALCATRAZ",
            "BLAMING THE EXACT SALT\nDECAY MORRIS CHIPPED THROUGH",
        ],
    },
    {
        "shotId": 38,
        "chapterId": 8,
        "slug": "ch8_1979_fbi_vs_marshals",
        "sfx": "stamp",
        "text": (
            "On December thirty-first, nineteen seventy-nine, after seventeen years and zero human remains, "
            "the FBI officially closed File seventy, twenty-six four-fifty-five. "
            "But the United States Marshals Service disagreed—updating age-progressed wanted posters into their nineties."
        ),
        "cues": [
            "DEC 31, 1979: FBI CLOSES\nTHE 17-YEAR INVESTIGATION",
            "OFFICIAL CLAIM: DROWNED\nBODIES RECOVERED: ZERO",
            "U.S. MARSHALS SERVICE\nREFUSED TO CLOSE THE FILE",
            "ACTIVE ARREST WARRANTS\nEXTENDED TO AGE 99",
        ],
    },
    {
        "shotId": 39,
        "chapterId": 8,
        "slug": "ch8_three_possibilities",
        "sfx": "foghorn",
        "text": (
            "Maybe the freezing Pacific claimed Frank Morris while two brothers climbed aboard a dark cabin cruiser. "
            "Or maybe all three bank robbers stood on the Marin cliffs before dawn, watching searchlights sweep "
            "an island they had broken with dimes, raincoats, and spoons."
        ),
        "cues": [
            "DID THE FREEZING BAY\nCLAIM ONE OR ALL THREE?",
            "OR DID THREE MEN STAND\nON THE MARIN HEADLANDS...",
            "WATCHING SEARCHLIGHTS\nSWEEP THE ROCK AT DAWN?",
            "OUTSMARTED WITH DIMES,\nRAINCOATS & SPOONS",
        ],
    },
    {
        "shotId": 40,
        "chapterId": 8,
        "slug": "ch8_final_verdict_outro",
        "sfx": "stamp",
        "text": (
            "Sixty-four years later, the waters of San Francisco Bay keep their secret, "
            "and three federal warrants remain unserved. What do you believe happened after midnight on June eleventh, "
            "nineteen sixty-two? Drop your theory in the comments below."
        ),
        "cues": [
            "64 YEARS LATER: THREE\nWARRANTS REMAIN UNSERVED",
            "ZERO BODIES · ZERO GRAVES\nCASE STILL ACTIVE",
            "DID THEY DROWN IN THE BAY\nOR PULL OFF THE IMPOSSIBLE?",
            "DROP YOUR VERDICT IN\nTHE COMMENTS BELOW",
        ],
    },
]


def clean_token(w: str) -> str:
    return "".join(ch for ch in w.upper() if ch.isalnum() or ch == "'")


def find_trim_bounds(samples: np.ndarray, thresh: float = 0.013, pad_ms: int = 30) -> tuple[int, int]:
    if len(samples) == 0:
        return 0, 0
    idx = np.where(np.abs(samples) > thresh)[0]
    if len(idx) == 0:
        return 0, min(len(samples), int(0.1 * SR))
    pad = int((pad_ms / 1000.0) * SR)
    start = max(0, int(idx[0]) - pad)
    end = min(len(samples), int(idx[-1]) + pad)
    return start, end


async def synth_shot(shot: dict, sem: asyncio.Semaphore) -> dict:
    async with sem:
        TMP_VO_DIR.mkdir(parents=True, exist_ok=True)
        sid = shot["shotId"]
        mp3_path = TMP_VO_DIR / f"shot_{sid:02d}.mp3"
        meta_path = TMP_VO_DIR / f"shot_{sid:02d}_words.json"

        sig = inspect.signature(edge_tts.Communicate.__init__)
        kwargs = {"voice": VOICE_ID, "rate": VOICE_RATE, "pitch": VOICE_PITCH}
        if "boundary" in sig.parameters:
            kwargs["boundary"] = "WordBoundary"

        word_events = []
        audio_bytes = bytearray()

        for attempt in range(5):
            try:
                word_events.clear()
                audio_bytes.clear()
                comm = edge_tts.Communicate(shot["text"], **kwargs)
                async for chunk in comm.stream():
                    ctype = chunk.get("type")
                    if ctype == "audio":
                        audio_bytes.extend(chunk["data"])
                    elif ctype == "WordBoundary":
                        offset_s = float(chunk["offset"]) / 1e7
                        dur_s = max(0.06, float(chunk["duration"]) / 1e7)
                        word_events.append(
                            {
                                "word": str(chunk["text"]),
                                "startRel": offset_s,
                                "endRel": offset_s + dur_s,
                            }
                        )
                if len(audio_bytes) > 800:
                    mp3_path.write_bytes(bytes(audio_bytes))
                    meta_path.write_text(json.dumps(word_events, indent=2), encoding="utf-8")
                    break
            except Exception as exc:
                if attempt == 4:
                    raise exc
                await asyncio.sleep(1.2 * (attempt + 1))

        wav_tmp = TMP_VO_DIR / f"shot_{sid:02d}_dec.wav"
        subprocess.run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(mp3_path),
                "-acodec",
                "pcm_s16le",
                "-ac",
                "1",
                "-ar",
                str(SR),
                str(wav_tmp),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        with wave.open(str(wav_tmp), "rb") as wf:
            pcm_bytes = wf.readframes(wf.getnframes())
        wav_tmp.unlink(missing_ok=True)
        full_samples = (np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0).copy()
        s0, s1 = find_trim_bounds(full_samples, thresh=0.013, pad_ms=28)
        trim_offset_s = s0 / SR
        samples = full_samples[s0:s1]
        clip_dur_s = len(samples) / SR

        mx = float(np.max(np.abs(samples))) if len(samples) else 0.0
        if mx > 1e-4:
            samples = samples / mx
        samples = (np.tanh(samples * 1.24) * 0.88).astype(np.float32)

        adjusted_words = []
        for we in word_events:
            ws = max(0.0, we["startRel"] - trim_offset_s)
            we_end = min(clip_dur_s, max(ws + 0.05, we["endRel"] - trim_offset_s))
            adjusted_words.append({"word": we["word"], "startRel": ws, "endRel": we_end})

        print(f"  [VO] Shot {sid:02d}/40 ({shot['slug']}): {clip_dur_s:.2f}s")
        return {
            "shot": shot,
            "samples": samples,
            "durationSec": clip_dur_s,
            "wordsRel": adjusted_words,
        }


def align_cues_and_words(shot: dict, shot_voice_start: float, clip_dur_s: float, words_rel: list[dict]):
    """
    Distribute shot cues cleanly across spoken duration and highlight each token progressively
    in sync with the spoken cadence.
    """
    cue_specs = []
    all_cue_tokens = []
    for cue_idx, cue_text in enumerate(shot["cues"]):
        lines = cue_text.split("\n")
        tokens = []
        for ln in lines:
            for tok in ln.strip().split():
                if tok:
                    tokens.append(tok)
                    all_cue_tokens.append((cue_idx, tok))
        cue_specs.append({"cueIdx": cue_idx, "text": cue_text, "tokens": tokens})

    # Smooth character-weighted cadence mapped onto exact voice start..end window
    weights = [max(2.2, len(t[1]) * 0.9 + (2.0 if t[1].endswith((":", ".", ",", "?", "!")) else 0.0)) for t in all_cue_tokens]
    tot_w = sum(weights) or 1.0

    # Anchor start & end to actual WordBoundary span when available
    span_start = shot_voice_start + (words_rel[0]["startRel"] if words_rel else 0.0)
    span_end = shot_voice_start + (words_rel[-1]["endRel"] if words_rel else clip_dur_s)
    usable_dur = max(1.0, span_end - span_start)

    cur = span_start
    mapped_words = []
    for (cue_idx, disp_tok), w in zip(all_cue_tokens, weights):
        dt = usable_dur * (w / tot_w)
        ws = cur
        we = cur + dt
        cur = we
        mapped_words.append(
            {
                "cueIndex": cue_idx,
                "word": disp_tok,
                "startSec": round(ws, 3),
                "endSec": round(we, 3),
                "startFrame": int(round(ws * FPS)),
                "endFrame": max(int(round(ws * FPS)) + 2, int(round(we * FPS))),
            }
        )

    cues_out = []
    for cs in cue_specs:
        c_idx = cs["cueIdx"]
        cw = [mw for mw in mapped_words if mw["cueIndex"] == c_idx]
        if not cw:
            continue
        cs_sec = cw[0]["startSec"]
        ce_sec = cw[-1]["endSec"] + 0.18
        cues_out.append(
            {
                "text": cs["text"],
                "startSec": round(cs_sec, 3),
                "endSec": round(ce_sec, 3),
                "startFrame": int(round(cs_sec * FPS)),
                "endFrame": int(round(ce_sec * FPS)),
                "words": [
                    {
                        "word": w["word"],
                        "startFrame": w["startFrame"],
                        "endFrame": w["endFrame"],
                    }
                    for w in cw
                ],
            }
        )

    for i in range(len(cues_out) - 1):
        if cues_out[i]["endFrame"] > cues_out[i + 1]["startFrame"]:
            cues_out[i]["endFrame"] = cues_out[i + 1]["startFrame"]
            cues_out[i]["endSec"] = round(cues_out[i]["endFrame"] / FPS, 3)

    return cues_out


def lowpass_noise(rng: np.random.Generator, n: int, taps: int = 14) -> np.ndarray:
    raw = rng.standard_normal(n).astype(np.float32)
    kernel = np.hanning(taps + 2)[1:-1].astype(np.float32)
    kernel /= np.sum(kernel)
    return np.convolve(raw, kernel, mode="same")


def build_docu_sfx_kit(rng: np.random.Generator) -> dict[str, np.ndarray]:
    kit: dict[str, np.ndarray] = {}

    # 1. Soft transition whoosh
    n = int(0.36 * SR)
    t = np.linspace(0, 0.36, n, endpoint=False, dtype=np.float32)
    env = np.sin(np.pi * (t / 0.36) ** 0.78) ** 2
    kit["whoosh"] = (lowpass_noise(rng, n, taps=22) * env * 0.45).astype(np.float32)

    # 2. Deep chapter boom impact
    n = int(1.65 * SR)
    t = np.linspace(0, 1.65, n, endpoint=False, dtype=np.float32)
    boom = (
        np.sin(2 * np.pi * (62 * np.exp(-t * 4.2) + 34) * t) * np.exp(-t * 2.4) * 0.72
        + np.sin(2 * np.pi * 110 * t) * np.exp(-t * 3.8) * 0.25
        + lowpass_noise(rng, n, taps=18) * np.exp(-t * 8.5) * 0.35
    )
    kit["chapter_boom"] = (np.tanh(boom * 1.35) * 0.62).astype(np.float32)

    # 3. Alcatraz iron cell door clang
    n = int(1.15 * SR)
    t = np.linspace(0, 1.15, n, endpoint=False, dtype=np.float32)
    clang = (
        np.sin(2 * np.pi * 218 * t) * np.exp(-t * 4.5) * 0.55
        + np.sin(2 * np.pi * 467 * t) * np.exp(-t * 6.8) * 0.38
        + np.sin(2 * np.pi * 912 * t) * np.exp(-t * 11.0) * 0.22
        + lowpass_noise(rng, n, taps=6) * np.exp(-t * 36.0) * 0.65
    )
    kit["iron_clang"] = (np.tanh(clang * 1.3) * 0.48).astype(np.float32)

    # 4. Metallic spoon scraping concrete
    n = int(0.22 * SR)
    t = np.linspace(0, 0.22, n, endpoint=False, dtype=np.float32)
    grit = np.diff(lowpass_noise(rng, n, taps=5), prepend=0.0)
    ring = np.sin(2 * np.pi * (1420 + 280 * t) * t) * np.exp(-t * 28.0) * 0.22
    scrape_env = np.sin(np.pi * (t / 0.22)) ** 1.3
    kit["spoon_scrape"] = (np.tanh((grit * 1.4 + ring) * 1.4) * scrape_env * 0.44).astype(np.float32)

    # 5. Vacuum-motor drill whir + muffled accordion undertone
    n = int(1.35 * SR)
    t = np.linspace(0, 1.35, n, endpoint=False, dtype=np.float32)
    d_env = np.minimum(1.0, t / 0.18) * np.minimum(1.0, (1.35 - t) / 0.28)
    whir = (
        np.sin(2 * np.pi * (380 + 35 * np.sin(2 * np.pi * 9 * t)) * t) * 0.28
        + lowpass_noise(rng, n, taps=7) * 0.36
    )
    kit["drill_whir"] = (np.tanh(whir * 1.2) * d_env * 0.34).astype(np.float32)

    # 6. Camera shutter + dossier slide
    n = int(0.18 * SR)
    t = np.linspace(0, 0.18, n, endpoint=False, dtype=np.float32)
    click1 = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 95.0) * 0.75
    click2 = rng.standard_normal(n).astype(np.float32) * np.exp(-np.maximum(0, t - 0.045) * 110.0) * (t >= 0.045) * 0.55
    kit["shutter"] = (np.clip(click1 + click2, -0.9, 0.9) * 0.46).astype(np.float32)

    # 7. Telemetry UI tick
    n = int(0.045 * SR)
    t = np.linspace(0, 0.045, n, endpoint=False, dtype=np.float32)
    kit["ui_tick"] = (np.sin(2 * np.pi * 1650 * t) * np.exp(-t * 65.0) * 0.24).astype(np.float32)

    # 8. Heavy FBI declassified stamp
    n = int(0.38 * SR)
    t = np.linspace(0, 0.38, n, endpoint=False, dtype=np.float32)
    sub = np.sin(2 * np.pi * (76 * np.exp(-t * 12.0) + 32) * t) * np.exp(-t * 8.5)
    paper = lowpass_noise(rng, n, taps=8) * np.exp(-t * 32.0) * 0.65
    kit["stamp"] = (np.tanh((sub + paper) * 1.4) * 0.54).astype(np.float32)

    # 9. San Francisco Bay nocturnal foghorn
    n = int(2.4 * SR)
    t = np.linspace(0, 2.4, n, endpoint=False, dtype=np.float32)
    f_env = np.minimum(1.0, t / 0.35) * np.minimum(1.0, (2.4 - t) / 0.75)
    horn = (
        np.sin(2 * np.pi * 65.41 * t) * 0.65
        + np.sin(2 * np.pi * 130.81 * t) * 0.38
        + np.sin(2 * np.pi * 196.00 * t) * 0.18
    )
    kit["foghorn"] = (np.tanh(horn * 1.35) * f_env * 0.32).astype(np.float32)

    return kit


def synthesize_10min_investigative_score(total_sec: float, rng: np.random.Generator) -> np.ndarray:
    """
    Synthesize a 10+ minute evolving dark investigative cinema underscore in 20-second blocks
    (memory-efficient, dark D-minor / C-minor cello & analog synth tension + subtle bay wind + pulse).
    """
    n_total = int(total_sec * SR)
    bed = np.zeros((n_total, 2), dtype=np.float32)

    chords = [
        (73.42, 110.00, 174.61, 220.00),  # Dm
        (58.27, 116.54, 174.61, 261.63),  # Bbmaj7
        (49.00, 98.00, 146.83, 233.08),   # Gm
        (55.00, 110.00, 164.81, 207.65),  # A7sus/C#
        (65.41, 98.00, 155.56, 196.00),   # Cm (darker modulation)
        (51.91, 103.83, 155.56, 233.08),  # Abmaj7
        (55.00, 110.00, 164.81, 220.00),  # Asus4
        (73.42, 110.00, 146.83, 233.08),  # Dm(b6) mystery
    ]

    block_sec = 16.0
    block_n = int(block_sec * SR)
    num_blocks = int(np.ceil(n_total / block_n))

    for b in range(num_blocks):
        i0 = b * block_n
        i1 = min(n_total, (b + 1) * block_n)
        m = i1 - i0
        t = (np.arange(i0, i1, dtype=np.float32) / SR)
        freqs = chords[b % len(chords)]
        next_freqs = chords[(b + 1) % len(chords)]

        local_u = (t - (b * block_sec)) / block_sec
        xfade = np.clip((local_u - 0.82) / 0.18, 0.0, 1.0)

        left = np.zeros(m, dtype=np.float32)
        right = np.zeros(m, dtype=np.float32)
        for fi in range(4):
            amp = 0.056 if fi == 0 else 0.030
            s1_l = np.sin(2 * np.pi * freqs[fi] * t)
            s2_l = np.sin(2 * np.pi * next_freqs[fi] * t)
            s1_r = np.sin(2 * np.pi * (freqs[fi] * 1.0015) * t)
            s2_r = np.sin(2 * np.pi * (next_freqs[fi] * 1.0015) * t)
            left += ((1.0 - xfade) * s1_l + xfade * s2_l) * amp
            right += ((1.0 - xfade) * s1_r + xfade * s2_r) * amp

        # Subtle investigative heartbeat pulse (70 -> 78 BPM across chapters)
        bpm = 70.0 + 8.0 * (b / max(1, num_blocks - 1))
        p_phase = (t * (bpm / 60.0)) % 1.0
        pulse = (
            np.sin(2 * np.pi * 50.0 * (p_phase / 1.15))
            * np.minimum(1.0, p_phase * 26.0)
            * np.exp(-p_phase * 9.8)
            * 0.085
        )

        wind_l = lowpass_noise(rng, m, taps=30) * 0.015
        wind_r = lowpass_noise(rng, m, taps=30) * 0.015

        bed[i0:i1, 0] = left + pulse + wind_l
        bed[i0:i1, 1] = right + pulse + wind_r

    # Master fade-in / fade-out
    fi_n = min(n_total, int(0.8 * SR))
    fo_n = min(n_total, int(1.8 * SR))
    bed[:fi_n, :] *= np.linspace(0.0, 1.0, fi_n, dtype=np.float32)[:, None]
    bed[-fo_n:, :] *= np.linspace(1.0, 0.0, fo_n, dtype=np.float32)[:, None]
    return bed


async def main():
    print("[Alcatraz 10Min] Synthesizing 40 investigative shots with Edge-TTS...")
    sem = asyncio.Semaphore(4)
    tasks = [synth_shot(shot, sem) for shot in SHOT_SCRIPT]
    shot_results = await asyncio.gather(*tasks)
    shot_results.sort(key=lambda r: r["shot"]["shotId"])

    raw_vo_sum = sum(r["durationSec"] for r in shot_results)
    # Ensure final total duration is cleanly >= 615 seconds (10m 15s+) for YouTube 10-min documentary & mid-roll standard
    min_target_sec = 618.0
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

        # Chapter opening shots get a crisp 1.45s atmospheric chapter card reveal before narration begins
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

    # Finalize chapter endFrames
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
    print(f"[Alcatraz 10Min] Master Duration: {mins:02d}:{secs:05.2f} ({total_sec:.2f}s / {total_frames} frames @ {FPS}fps)")

    rng = np.random.default_rng(19620612)
    sfx = build_docu_sfx_kit(rng)
    bed = synthesize_10min_investigative_score(total_sec, rng)
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
            duck[d0:d1] = np.minimum(duck[d0:d1], 0.40)

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
            sfx_events.append((max(0.0, cut_s - 3.0 / FPS), "whoosh", 0.62))

        kind = st["sfx"]
        offset = 0.85 if st["isChapterStart"] else 0.18
        if kind == "spoon_scrape":
            t_sp = cut_s + offset + 0.35
            while t_sp < (st["endFrame"] / FPS) - 0.5:
                sfx_events.append((round(t_sp, 3), "spoon_scrape", 0.52))
                t_sp += 0.80
        elif kind == "drill_whir":
            sfx_events.append((cut_s + offset + 0.4, "drill_whir", 0.58))
            sfx_events.append((cut_s + offset + 3.2, "drill_whir", 0.50))
        elif kind in sfx:
            sfx_events.append((cut_s + offset, kind, 0.66))

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
    wav_master = STUDIO_DIR / "out" / "alcatraz_10min_tmp.wav"
    pcm16 = np.clip(np.round(mix * 32767.0), -32768, 32767).astype(np.int16)
    with wave.open(str(wav_master), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

    print("[Alcatraz 10Min] Normalizing master broadcast audio (-16 LUFS)...")
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
    ts_content = f"""// Auto-generated by scripts/build_alcatraz_10min_audio.py
import type {{ CaptionCue }} from "./alcatrazPilotTimeline";

export interface DocuChapterTiming {{
  readonly chapterId: number;
  readonly code: string;
  readonly title: string;
  readonly startFrame: number;
  readonly endFrame: number;
  readonly startSec: number;
}}

export interface Docu10MinShotTiming {{
  readonly shotId: number;
  readonly chapterId: number;
  readonly isChapterStart: boolean;
  readonly slug: string;
  readonly startFrame: number;
  readonly endFrame: number;
  readonly durationInFrames: number;
}}

export const DOCU_10MIN_FPS = {FPS};
export const DOCU_10MIN_TOTAL_FRAMES = {total_frames};
export const DOCU_10MIN_DURATION_SEC = {round(total_sec, 3)};

export const DOCU_10MIN_CHAPTERS: readonly DocuChapterTiming[] = {json.dumps(chapters_timeline, indent=2)} as const;

export const DOCU_10MIN_SHOTS: readonly Docu10MinShotTiming[] = {json.dumps(shots_export, indent=2)} as const;

export const DOCU_10MIN_CUES: readonly CaptionCue[] = {json.dumps(all_cues, indent=2)} as const;
"""
    OUT_TIMELINE.write_text(ts_content, encoding="utf-8")
    print(f"[Alcatraz 10Min] Done! Saved {OUT_AUDIO.name} & {OUT_TIMELINE.name} ({len(all_cues)} cues).")


if __name__ == "__main__":
    asyncio.run(main())
