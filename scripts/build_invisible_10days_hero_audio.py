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

TMP_VO_DIR = STUDIO_DIR / "out" / "vo_invisible_hero_tmp"
OUT_AUDIO = STUDIO_DIR / "public" / "audio" / "invisible_10days_hero_master.mp3"
OUT_TIMELINE = STUDIO_DIR / "src" / "invisible" / "invisible10DaysHeroTimeline.ts"

SR = 44100
FPS = 30

# Crisp, fearless, cinematic US female first-person narrator (Superhero Edition)
VOICE_ID = "en-US-AvaNeural"
VOICE_RATE = "+3%"
VOICE_PITCH = "-1Hz"

CHAPTERS = [
    {"chapterId": 1, "code": "DAY 01", "title": "07:04 AM: EMPTY MIRROR & THE STEALTH SUIT RULE"},
    {"chapterId": 2, "code": "DAY 02", "title": "EXPRESS TRAIN RESCUE: 0.8 SECONDS TO IMPACT"},
    {"chapterId": 3, "code": "DAY 03", "title": "WALL STREET HOSTAGE VAULT: SILENT TAKEDOWN"},
    {"chapterId": 4, "code": "DAY 04", "title": "ZERO KEVLAR: REAL PHYSICS OF FIGHTING UNSEEN"},
    {"chapterId": 5, "code": "DAY 05", "title": "RED HOOK DOCKS: TRACKING CONTAINER #719"},
    {"chapterId": 6, "code": "DAY 06", "title": "ONE PHANTOM VS. TWELVE ARMED SYNDICATE GUARDS"},
    {"chapterId": 7, "code": "DAY 07", "title": "38TH-FLOOR INFERNO: THE ASH & SMOKE BETRAYAL"},
    {"chapterId": 8, "code": "DAY 08", "title": "98.6°F HUNTED: THERMAL DRONES ON THE ROOFTOP"},
    {"chapterId": 9, "code": "DAY 09", "title": "GRAND CENTRAL MIDNIGHT PLOT & EARLY GLITCHING"},
    {"chapterId": 10, "code": "DAY 10", "title": "FINAL 60 SECONDS & THE GUARDIAN MIRROR TWIST"},
]

SHOT_SCRIPT = [
    # ==================== DAY 01 ====================
    {
        "shotId": 1,
        "chapterId": 1,
        "slug": "h1_mirror_awakening",
        "sfx": "glass_shimmer",
        "text": (
            "I woke up at seven-oh-four AM in my Manhattan apartment, stepped into the bathroom, "
            "and wiped the morning mist off the mirror. Nobody stared back at me. "
            "My face, my hands, my hair—completely gone, replaced by a glowing blue countdown on the glass: "
            "two hundred forty hours. Ten days."
        ),
        "cues": [
            "07:04 AM · MANHATTAN\nI WIPED THE BATHROOM MIRROR",
            "NO FACE · NO HANDS · NO EYES\nSTARING BACK FROM THE GLASS",
            "ONLY A GLOWING BLUE TIMER:\n240:00:00 REMAINING",
            "TEN DAYS COMPLETELY UNSEEN\nAND ONE CHOICE TO MAKE",
        ],
    },
    {
        "shotId": 2,
        "chapterId": 1,
        "slug": "h1_four_millimeter_suit_rule",
        "sfx": "suit_powerup",
        "text": (
            "After ten minutes of hyperventilating, my engineering brain kicked in and started testing the boundary. "
            "Anything looser than four millimeters off my skin—like a coat or backpack—stayed completely visible. "
            "But an ultra-thin second-skin runner's compression suit, socks, and nitrile gloves sat tight inside my bio-refractive field "
            "and vanished right along with me!"
        ),
        "cues": [
            "MY ENGINEERING BRAIN TESTED\nTHE LIGHT-BENDING BOUNDARY",
            "LOOSE COATS & BACKPACKS\nSTAYED 100% VISIBLE IN AIR",
            "BUT A 2MM COMPRESSION SUIT\nSAT INSIDE MY SKIN'S FIELD",
            "VANISHING COMPLETELY WITH ME:\nMY IMPROVISED STEALTH SUIT!",
        ],
    },
    {
        "shotId": 3,
        "chapterId": 1,
        "slug": "h1_moral_crossroads_data",
        "sfx": "sonar_ping",
        "text": (
            "Most people admit that if nobody could see them, they'd rob banks or spy on enemies. "
            "I almost did too—until I looked down from my fire escape and remembered how helpless my sister felt "
            "the night she was mugged on Ninth Avenue. For ten days, predators in this city wouldn't own the dark. I would."
        ),
        "cues": [
            "MOST PEOPLE WOULD ROB BANKS\nOR SNOOP BEHIND CLOSED DOORS",
            "THEN I LOOKED DOWN AT 9TH AVE\nWHERE MY SISTER WAS MUGGED",
            "FOR 240 HOURS THE PREDATORS\nWOULDN'T OWN THE DARK",
            "THIS TIME THE GHOST IN THE\nALLEY WAS HUNTING THEM",
        ],
    },
    {
        "shotId": 4,
        "chapterId": 1,
        "slug": "h1_alley_mugging_first_save",
        "sfx": "impact_thud",
        "text": (
            "At eleven-twenty PM in Hell's Kitchen, I heard a nurse's voice shaking as two men cornered her behind a dumpster with a switchblade. "
            "I walked silently right between them, swept the gunman's ankle onto the wet concrete, "
            "wrenched the blade into a storm drain, and watched both thugs sprint away screaming at an empty alley!"
        ),
        "cues": [
            "11:20 PM · HELL'S KITCHEN\nA NURSE CORNERED IN AN ALLEY",
            "I STEPPED SILENTLY BETWEEN\nHER AND THE SWITCHBLADE",
            "SWEPT HIS ANKLE TO CONCRETE\nKICKED THE BLADE DOWN A DRAIN",
            "BOTH MUGGERS RAN SCREAMING\nFROM AN EMPTY SHADOW!",
        ],
    },

    # ==================== DAY 02 ====================
    {
        "shotId": 5,
        "chapterId": 2,
        "slug": "h2_subway_platform_patrol",
        "sfx": "sonar_ping",
        "text": (
            "Day Two: two hundred sixteen hours left. Saving one stranger felt better than a million stolen dollars ever could. "
            "I started patrolling the city's deadliest choke points—late-night parking garages, dimly lit overpasses, "
            "and packed rush-hour subway platforms at Herald Square."
        ),
        "cues": [
            "DAY TWO · 216 HOURS LEFT\nADRENALINE SHARPER THAN GREED",
            "PATROLLING MANHATTAN'S MOST\nDANGEROUS BLIND SPOTS",
            "PARKING DECKS · OVERPASSES\nAND 34TH ST SUBWAY PLATFORMS",
            "LISTENING FOR TROUBLE BEFORE\nIT COULD STRIKE",
        ],
    },
    {
        "shotId": 6,
        "chapterId": 2,
        "slug": "h2_express_train_rescue",
        "sfx": "train_horn",
        "text": (
            "At five-eighteen PM, chaos erupted. A distracted commuter bumped an unbraked stroller—and a four-year-old boy "
            "toppled straight onto the tracks just as a Queens-bound express train roared into the tunnel at forty-five miles an hour! "
            "Nobody on the platform could reach him in time. Except me."
        ),
        "cues": [
            "05:18 PM · HERALD SQUARE\nA STROLLER ROLLED OFF THE EDGE!",
            "FOUR-YEAR-OLD BOY ON THE RAILS\nEXPRESS TRAIN AT 45 MPH!",
            "NOBODY ON THE PLATFORM WAS\nCLOSE ENOUGH TO REACH HIM",
            "I VAULTED ONTO THE GRAVEL\nFOUR SECONDS BEFORE IMPACT!",
        ],
    },
    {
        "shotId": 7,
        "chapterId": 2,
        "slug": "h2_zero_point_eight_seconds",
        "sfx": "heartbeat_lubdub",
        "text": (
            "Vaulting over the yellow line, I dodged the six-hundred-volt third rail, scooped the boy against my chest, "
            "and rolled both of us into the concrete safety trough beneath the platform overhang—point-eight seconds before "
            "forty tons of steel screamed past inches above my hair!"
        ),
        "cues": [
            "DODGED THE 600-VOLT THIRD RAIL\nSCOOPED HIM AGAINST MY CHEST",
            "ROLLED INTO THE CONCRETE\nUNDER-PLATFORM SAFETY TROUGH",
            "0.8 SECONDS BEFORE 40 TONS\nOF STEEL ROARED OVERHEAD!",
            "THE CROWD WATCHED HIM RISE\nLIFTED BY INVISIBLE ARMS",
        ],
    },
    {
        "shotId": 8,
        "chapterId": 2,
        "slug": "h2_guardian_ghost_news",
        "sfx": "camera_alert",
        "text": (
            "Fifty phone cameras caught the boy floating safely back onto his mother's knees as if lifted by an angel. "
            "By midnight, every news network in America was replaying that blurry subway clip twenty million times, "
            "calling me 'The Guardian Phantom of New York.'"
        ),
        "cues": [
            "50 SMARTPHONES FILMED HIM\nFLOATING BACK TO HIS MOTHER",
            "20 MILLION VIEWS BY MIDNIGHT\nACROSS EVERY US NEWS DESK",
            "HEADLINES DUBBED ME:\n'NEW YORK'S GUARDIAN PHANTOM'",
            "AND CRIMINALS ACROSS THE CITY\nSUDDENLY STARTED LOOKING TWICE",
        ],
    },

    # ==================== DAY 03 ====================
    {
        "shotId": 9,
        "chapterId": 3,
        "slug": "h3_bank_hostage_alert",
        "sfx": "camera_alert",
        "text": (
            "Day Three pushed my luck into real tactical danger. At two-ten PM on Broad Street, "
            "four masked mercenaries with automatic rifles stormed a private depository bank, took fourteen civilians hostage, "
            "and wired laser detonators across every glass entrance while SWAT cruisers surrounded the block."
        ),
        "cues": [
            "DAY THREE · 02:10 PM\nBROAD STREET BANK SIEGE",
            "FOUR ARMED MERCENARIES WITH\n14 TERRIFIED HOSTAGES INSIDE",
            "LASER TRIPWIRES RIGGED ACROSS\nEVERY GLASS LOBBY DOOR",
            "NYPD SWAT PINNED OUTSIDE—\nUNABLE TO BREACH SAFELY",
        ],
    },
    {
        "shotId": 10,
        "chapterId": 3,
        "slug": "h3_slipping_past_swat_perimeter",
        "sfx": "door_click",
        "text": (
            "SWAT snipers couldn't breach without triggering the tripwires—because infrared laser beams break if a solid body crosses them. "
            "Wait: visible red lasers bent smoothly around my refractive suit without breaking the beam! "
            "I crawled silently through a shattered upper vent and dropped onto the marble mezzanine right behind the lead gunman."
        ),
        "cues": [
            "SWAT COULDN'T CROSS THE DOOR\nWITHOUT BREAKING THE LASERS",
            "BUT RED OPTICAL BEAMS BENT\nCLEANLY AROUND MY SUIT!",
            "SLIPPED THROUGH AN UPPER VENT\nONTO THE MARBLE MEZZANINE",
            "STANDING 12 INCHES BEHIND\nTHE MERCENARY LEADER!",
        ],
    },
    {
        "shotId": 11,
        "chapterId": 3,
        "slug": "h3_six_second_vault_takedown",
        "sfx": "impact_thud",
        "text": (
            "Reading his tablet over his shoulder, I saw the dead-man switch code, plucked the radio detonator straight out of his vest pocket, "
            "and snapped its antenna! Before his crew could turn, I popped two smoke canisters from their own tactical belts, "
            "zip-tied two gunmen's ankles together, and kicked the lobby release switch for SWAT!"
        ),
        "cues": [
            "PLUCKED THE RADIO DETONATOR\nRIGHT OUT OF HIS TACTICAL VEST",
            "POPPED THEIR OWN SMOKE CANS\nTO COVER THE 14 HOSTAGES",
            "ZIP-TIED TWO GUNMEN'S BOOTS\nTOGETHER IN SIX SECONDS FLAT",
            "HIT THE LOBBY RELEASE SWITCH\nAS SWAT STORMED IN!",
        ],
    },
    {
        "shotId": 12,
        "chapterId": 3,
        "slug": "h3_stray_bullet_reality_check",
        "sfx": "heartbeat_lubdub",
        "text": (
            "As the last gunman panicked and fired blind into the ceiling, a ricochet sliced a burning shallow graze across my forearm! "
            "I clamped my gloved palm over it and slipped out the side door—shaking with a terrifying realization: "
            "being invisible doesn't make you bulletproof."
        ),
        "cues": [
            "A BLIND RICOCHET SLICED ACROSS\nMY LEFT FOREARM IN THE CHAOS",
            "CLAMPED MY GLOVED HAND TIGHT\nSO NOT A DROP HIT THE FLOOR",
            "SLIPPED OUT SHAKING WITH ONE\nTERRIFYING REALITY CHECK:",
            "INVISIBILITY HIDES YOUR BODY—\nIT NEVER STOPS A BULLET",
        ],
    },

    # ==================== DAY 04 ====================
    {
        "shotId": 13,
        "chapterId": 4,
        "slug": "h4_bathroom_stitching_physics",
        "sfx": "glass_shimmer",
        "text": (
            "Day Four: patched up in my bathroom at dawn, staring at floating gauze turning red the instant blood left my skin. "
            "Here's the brutal superhero catch comic books never explain: I couldn't wear Kevlar body armor or carry steel weapons, "
            "because anything thicker than four millimeters floated in mid-air like a neon target!"
        ),
        "cues": [
            "DAY FOUR · DAWN TRIAGE\nPATCHING MY GRAZED FOREARM",
            "BLOOD TURNED SOLID CRIMSON\nTHE SECOND IT LEFT MY SKIN!",
            "KEVLAR VESTS & BATONS WERE\nTOO THICK TO TURN INVISIBLE",
            "ZERO ARMOR · ZERO WEAPONS\nPURE BRAINS AND LEVERAGE",
        ],
    },
    {
        "shotId": 14,
        "chapterId": 4,
        "slug": "h4_four_superhero_rules",
        "sfx": "suit_powerup",
        "text": (
            "To survive six more days fighting armed criminals without superpowers of steel, I wrote four iron rules on my apartment wall: "
            "never stand in a crossfire cone, use criminals' own weight and panic against them, carry micro-zip-ties taped flat to my ribs, "
            "and win every fight before anyone knows a fight started."
        ),
        "cues": [
            "FOUR IRON SURVIVAL RULES FOR\nAN UNARMORED STEALTH HERO:",
            "RULE 1: NEVER STAND INSIDE A\nBLIND SPRAY-FIRE CONE",
            "RULE 2: FLAT CARBON ZIP-TIES\nTAPED INSIDE MY 4MM FIELD",
            "RULE 3: END EVERY STANDOFF\nBEFORE THEY KNOW YOU EXIST",
        ],
    },
    {
        "shotId": 15,
        "chapterId": 4,
        "slug": "h4_police_precinct_intel_wall",
        "sfx": "door_click",
        "text": (
            "Instead of wandering random alleys waiting for muggers, I decided to aim higher. "
            "That afternoon, I walked unseen into the NYPD Major Case task-force room on One Police Plaza "
            "and studied their biggest unsolved wall: fourteen young women vanished near Red Hook shipping terminals."
        ),
        "cues": [
            "STOPPED CHASING STREET THUGS—\nDECIDED TO AIM MUCH HIGHER",
            "WALKED UNSEEN INTO NYPD'S\nMAJOR CASE TASK-FORCE ROOM",
            "STUDIED THEIR COLDEST CASE:\n14 MISSING WOMEN IN BROOKLYN",
            "LAST TRACKED NEAR PRIVATE\nRED HOOK SHIPPING PIERS",
        ],
    },
    {
        "shotId": 16,
        "chapterId": 4,
        "slug": "h4_warrant_loophole_detective",
        "sfx": "sonar_ping",
        "text": (
            "Detectives knew a shell company owned by billionaire Viktor Kovács was moving contraband containers out of Pier Twelve—"
            "but corrupt lawyers blocked every search warrant. Police needed probable cause to cross that fence. "
            "An invisible woman just needed an open gate."
        ),
        "cues": [
            "BILLIONAIRE SHELL COMPANY\nPROTECTED BY HIGH-PAID LAWYERS",
            "EVERY NYPD SEARCH WARRANT\nBLOCKED IN FEDERAL COURT",
            "DETECTIVES WERE TIED DOWN\nBY RED TAPE AND CAMERAS",
            "AN INVISIBLE HERO ONLY NEEDED\nONE OPEN GATE AT PIER 12",
        ],
    },

    # ==================== DAY 05 ====================
    {
        "shotId": 17,
        "chapterId": 5,
        "slug": "h5_red_hook_office_infiltration",
        "sfx": "door_click",
        "text": (
            "Day Five: halfway mark, a hundred twenty hours left. Under heavy evening fog in Brooklyn's Red Hook shipyard, "
            "I slipped behind an armed dock supervisor into Kovács Logistics' glass control office "
            "and watched him unlock an encrypted manifest terminal."
        ),
        "cues": [
            "DAY FIVE · 120 HOURS LEFT\nRED HOOK SHIPYARD AT DUSK",
            "SLIPPED PAST RAZOR WIRE BEHIND\nTHE DOCKYARD SUPERVISOR",
            "INSIDE THE GLASS CONTROL ROOM\nWATCHING HIS ENCRYPTED SCREEN",
            "SEARCHING MANIFESTS FOR ONE\nOFF-THE-BOOKS CONTAINER",
        ],
    },
    {
        "shotId": 18,
        "chapterId": 5,
        "slug": "h5_container_719_discovery",
        "sfx": "camera_alert",
        "text": (
            "Line forty-two made my stomach drop: Container Seven-Nineteen, listed as 'industrial textiles,' "
            "yet drawing live ventilation power on Berth Four—scheduled to load onto an outbound freighter at two AM tonight! "
            "Even worse: patrol K9 German shepherds were circling the yard below."
        ),
        "cues": [
            "LINE 42 ON THE TERMINAL:\nCONTAINER #719 · BERTH FOUR",
            "LISTED AS 'TEXTILES'—YET DRAWING\nLIVE AIR VENTILATION POWER!",
            "SCHEDULED TO DEPART NYC AT\n02:00 AM ON A FREIGHTER!",
            "HAZARD BELOW: GUARD DOGS\nPATROLLING THE CONTAINER YARD",
        ],
    },
    {
        "shotId": 19,
        "chapterId": 5,
        "slug": "h5_diesel_truck_scent_mask",
        "sfx": "steam_hiss",
        "text": (
            "Guard dogs don't use their eyes—they hunt by scent! Remembering my survival physics, I rubbed diesel grease "
            "and sea salt across my ankles to mask my human scent, clung silently to the side ladder of a moving yard forklift, "
            "and rode straight past two barking German shepherds to Berth Four!"
        ),
        "cues": [
            "GUARD DOGS DON'T NEED EYES—\nTHEY TRACK HUMAN SCENT!",
            "MASKED MY ANKLES WITH DIESEL\nEXHAUST AND HARBOR SALT",
            "RODE SILENTLY ON THE SIDE OF\nA MOVING YARD FORKLIFT",
            "SLIPPING RIGHT PAST TWO K9\nPATROLS TO BERTH FOUR!",
        ],
    },
    {
        "shotId": 20,
        "chapterId": 5,
        "slug": "h5_anonymous_911_gps_ping",
        "sfx": "sonar_ping",
        "text": (
            "Pressing my ear against Container Seven-Nineteen's cold corrugated steel, I heard muffled crying inside. "
            "Twelve armed syndicate guards stood between that container and the gate—and the freighter crane was already warming up. "
            "Calling NYPD from a payphone wasn't enough; if police sirens approached early, the guards would push the container into the bay!"
        ),
        "cues": [
            "PRESSED MY EAR TO STEEL:\nMUFFLED VOICES INSIDE #719!",
            "TWELVE ARMED SYNDICATE MEN\nGUARDING THE LOADING CRANE",
            "IF SIRENS PULLED UP EARLY\nTHEY'D DUMP EVIDENCE AT SEA",
            "I HAD TO CLEAR THAT PIER MYSELF\nBEFORE CALLING HARBOR SWAT!",
        ],
    },

    # ==================== DAY 06 ====================
    {
        "shotId": 21,
        "chapterId": 6,
        "slug": "h6_cutting_pier_floodlights",
        "sfx": "suit_powerup",
        "text": (
            "Day Six struck at midnight—ninety-six hours left, and my biggest test yet. "
            "First rule of asymmetric stealth: blind the enemy so your invisibility becomes absolute terror. "
            "I climbed the crane transformer box and pulled the main breaker—plunging all of Berth Four into pitch-black harbor fog!"
        ),
        "cues": [
            "DAY SIX · MIDNIGHT STRIKE\nONE PHANTOM VS. TWELVE GUNMEN",
            "CLIMBED THE CRANE TRANSFORMER\nAND PULLED THE MAIN BREAKER",
            "EVERY FLOODLIGHT ON PIER 12\nSNAPPED PITCH-BLACK AT ONCE!",
            "THICK HARBOR FOG TURNED THEIR\nNUMBERS AGAINST THEM",
        ],
    },
    {
        "shotId": 22,
        "chapterId": 6,
        "slug": "h6_phantom_dockyard_takedowns",
        "sfx": "impact_thud",
        "text": (
            "Moving barefoot across steel catwalks in total silence, I picked off the perimeter lookouts one by one—ejecting rifle magazines "
            "into the black water, locking cargo chains around the guardhouse door with six men trapped inside, "
            "and using the crane horn to lure the last four away from Container Seven-Nineteen!"
        ),
        "cues": [
            "EJECTED RIFLE MAGAZINES RIGHT\nOUT OF THEIR HANDS IN THE FOG",
            "PADLOCKED SIX GUARDS INSIDE\nTHEIR OWN STEEL BREAK ROOM",
            "TRIGGERED THE CRANE HORN TO\nLURE THE LAST FOUR AWAY",
            "PSYCHOLOGICAL WARFARE: THEY\nTHOUGHT A WHOLE TEAM HIT THEM!",
        ],
    },
    {
        "shotId": 23,
        "chapterId": 6,
        "slug": "h6_opening_container_719",
        "sfx": "door_click",
        "text": (
            "With bolt cutters lifted from the tool shed, I snapped the heavy padlock on Container Seven-Nineteen and swung the steel doors wide! "
            "Fourteen exhausted women blinked into the moonlight, whispering in shock as an unseen female voice gently said: "
            "'Follow the blue flares to the gate. Police boats are two minutes out. You're safe.'"
        ),
        "cues": [
            "SNAPPED THE HEAVY PADLOCK ON\nCONTAINER #719 WITH CUTTERS",
            "FOURTEEN CAPTIVE WOMEN STEPPED\nOUT INTO THE MOONLIGHT",
            "I WHISPERED FROM EMPTY AIR:\n'FOLLOW THE FLARES—YOU'RE SAFE'",
            "LIT THREE MARINE SIGNAL FLARES\nAS NYPD HARBOR BOATS ARRIVED!",
        ],
    },
    {
        "shotId": 24,
        "chapterId": 6,
        "slug": "h6_kovacs_ledger_delivered",
        "sfx": "camera_alert",
        "text": (
            "When FBI and NYPD units stormed Pier Twelve three minutes later, they didn't just rescue all fourteen victims unharmed—"
            "they found the dock boss zip-tied to the crane lever with Kovács's decrypted trafficking laptop taped straight to his chest! "
            "For the first time in my life, I cried happy tears nobody could see."
        ),
        "cues": [
            "ALL 14 WOMEN RESCUED UNHARMED\nBY NYPD HARBOR UNITS",
            "SYNDICATE BOSS FOUND ZIP-TIED\nWITH DECRYPTED LAPTOP EVIDENCE",
            "FEDERAL ARREST WARRANTS ISSUED\nFOR VIKTOR KOVÁCS BY DAWN!",
            "TEARS ON MY INVISIBLE CHEEKS—\nWORTH EVERY SINGLE BRUISE",
        ],
    },

    # ==================== DAY 07 ====================
    {
        "shotId": 25,
        "chapterId": 7,
        "slug": "h7_highrise_fire_38th_floor",
        "sfx": "camera_alert",
        "text": (
            "Day Seven: seventy-two hours left, running on three hours of sleep because transparent eyelids still let morning light blaze in! "
            "Then sirens wailed three blocks east: a five-alarm electrical fire raging on the thirty-eighth floor of a residential tower, "
            "with smoke trapping a mother and her seven-year-old daughter behind a buckled steel door!"
        ),
        "cues": [
            "DAY SEVEN · 72 HOURS LEFT\nFIVE-ALARM HIGH-RISE FIRE!",
            "38TH FLOOR ENGULFED IN BLACK\nSMOKE ABOVE FDNY LADDERS",
            "A MOTHER & HER LITTLE GIRL\nTRAPPED BEHIND A BUCKLED DOOR",
            "STAIRWELL COLLAPSING—MINUTES\nBEFORE FLASHOVER!",
        ],
    },
    {
        "shotId": 26,
        "chapterId": 7,
        "slug": "h7_ash_and_soot_visibility_curse",
        "sfx": "steam_hiss",
        "text": (
            "Racing up the emergency service shaft ahead of the hose crews, I slammed into nature's cruelest visibility trap: "
            "billowing black soot, falling white ash, and sprinkler spray coated every inch of my stealth suit—"
            "instantly outlining a ghostly gray female silhouette walking straight through the flames!"
        ),
        "cues": [
            "SPRINKLER WATER & FALLING ASH\nCLUNG TO MY STEALTH SUIT!",
            "COATING EVERY CURVE IN GRAY\nSOOT AMID ORANGE FLAMES!",
            "MY INVISIBILITY VANISHED UNDER\nSMOKE AND PARTICULATE DUST",
            "YET TURNING BACK WAS NEVER\nAN OPTION ON FLOOR 38",
        ],
    },
    {
        "shotId": 27,
        "chapterId": 7,
        "slug": "h7_crowbar_breach_and_carry",
        "sfx": "impact_thud",
        "text": (
            "Using a firefighter's halligan bar wedged in the frame, I pried the warped apartment door open two feet, "
            "wrapped wet towels over both their faces, lifted the coughing little girl into my soot-streaked arms, "
            "and guided them down to the thirty-fifth-floor rescue team before slipping under a hallway standpipe to wash clean!"
        ),
        "cues": [
            "PRIED THE WARPED STEEL DOOR\nOPEN WITH A HALLIGAN BAR",
            "WRAPPED WET TOWELS OVER THEIR\nLUNGS AND LIFTED THE GIRL",
            "GUIDED BOTH OF THEM SAFELY TO\nFDNY CREWS ON FLOOR 35!",
            "RINSED THE ASH OFF UNDER A\nPIPE AND VANISHED AGAIN",
        ],
    },
    {
        "shotId": 28,
        "chapterId": 7,
        "slug": "h7_exhaustion_and_bounty",
        "sfx": "heartbeat_lubdub",
        "text": (
            "That night, the little girl drew a crayon picture on live TV of a 'sparkling gray angel' carrying her through smoke. "
            "Meanwhile, out on bail with an ankle monitor, billionaire Viktor Kovács put a five-million-dollar underground bounty "
            "on capturing New York's invisible vigilante—dead or alive."
        ),
        "cues": [
            "ON LIVE TV THE GIRL DREW A\n'SHIMMERING ANGEL IN THE SMOKE'",
            "THE WHOLE CITY CHEERED FOR\nTHEIR UNSEEN PROTECTOR",
            "WHILE BILLIONAIRE KOVÁCS PUT A\n$5,000,000 BOUNTY ON MY HEAD",
            "HIRING EX-MILITARY HUNTERS\nWHO KNEW HOW TO SEE ME",
        ],
    },

    # ==================== DAY 08 ====================
    {
        "shotId": 29,
        "chapterId": 8,
        "slug": "h8_rooftop_ambush_trap",
        "sfx": "camera_alert",
        "text": (
            "Day Eight: forty-eight hours left—and I walked straight into Kovács's trap. "
            "Following a fake distress tip to a Hell's Kitchen rooftop helipad, three black quadcopter drones rose silently from behind the water tower—"
            "equipped with military FLIR thermal infrared cameras!"
        ),
        "cues": [
            "DAY EIGHT · 48 HOURS LEFT\nBAITED TO A ROOFTOP HELIPAD!",
            "THREE TACTICAL QUADCOPTERS\nROSE FROM THE SHADOWS",
            "EQUIPPED WITH LONG-WAVE FLIR\nTHERMAL INFRARED OPTICS!",
            "TO THERMAL LENSES MY 98.6°F\nBODY GLOWED LIKE A FLARE!",
        ],
    },
    {
        "shotId": 30,
        "chapterId": 8,
        "slug": "h8_thermal_paintball_hunt",
        "sfx": "impact_thud",
        "text": (
            "On their thermal tablets, my ninety-eight-point-six-degree body blazed bright orange against the cold night sky! "
            "Four mercenaries opened fire with UV-dye paintballs and electric net launchers—one dye splash away from marking me permanently visible! "
            "I dove behind a roaring HVAC exhaust stack!"
        ),
        "cues": [
            "98.6°F BODY HEAT BLAZING\nBRIGHT ORANGE ON THEIR SCREENS!",
            "MERCENARIES FIRED UV-DYE ROUNDS\nAND ELECTRIC NET LAUNCHERS!",
            "ONE SPLASH OF FLUORESCENT DYE\nAND I'D BE EXPOSED FOREVER",
            "DOVE BEHIND A ROARING 110°F\nROOFTOP HVAC EXHAUST VENT!",
        ],
    },
    {
        "shotId": 31,
        "chapterId": 8,
        "slug": "h8_chiller_steam_drone_crash",
        "sfx": "steam_hiss",
        "text": (
            "Thermodynamics saved my life: standing directly inside the building's hundred-ten-degree boiler steam plume "
            "masked my silhouette completely on infrared! As Drone One hovered close to scan the steam, "
            "I whipped a steel maintenance cable into its rotors—crashing it into Drone Two and knocking out their operator's tablet!"
        ),
        "cues": [
            "BLENDED MY BODY HEAT INSIDE\nTHE 110°F BOILER STEAM PLUME!",
            "ON THERMAL SCREENS MY OUTLINE\nDISAPPEARED INTO THE HEAT CLOUD",
            "WHIPPED A STEEL CABLE STRAIGHT\nINTO DRONE ONE'S ROTORS!",
            "SMASHED THEIR THERMAL EYES\nAND DISARMED THE HUNTERS!",
        ],
    },
    {
        "shotId": 32,
        "chapterId": 8,
        "slug": "h8_dropped_encrypted_phone_intel",
        "sfx": "sonar_ping",
        "text": (
            "Leaving Kovács's mercenaries handcuffed to the rooftop railing for NYPD, I picked up their team leader's unlocked satellite phone—"
            "and froze cold. Kovács wasn't fleeing the country. Before his federal trial Monday, "
            "he planned a midnight sabotage blackout at Grand Central Terminal to assassinate the three key witnesses!"
        ),
        "cues": [
            "LEFT THE BOUNTY HUNTERS CUFFED\nFOR NYPD ON THE HELIPAD",
            "CHECKED THEIR UNLOCKED SAT-PHONE\nAND MY BLOOD RAN COLD:",
            "KOVÁCS PLANNED A MIDNIGHT\nGRAND CENTRAL SABOTAGE ATTACK",
            "TARGETING THE WITNESS CONVOY\nBENEATH TRACK FORTY-TWO!",
        ],
    },

    # ==================== DAY 09 ====================
    {
        "shotId": 33,
        "chapterId": 9,
        "slug": "h9_final_24_hours_choice",
        "sfx": "heartbeat_lubdub",
        "text": (
            "Day Nine: final twenty-four hours. Bruised ribs, taped knuckles, aching feet—every muscle begged me to stay home, "
            "email an anonymous tip, and let the clock run out safely. "
            "Except Kovács had jammed the tunnel's radio repeaters and planted an inside man on the security detail. Only a ghost could reach Track Forty-Two."
        ),
        "cues": [
            "DAY NINE · FINAL 24 HOURS\nBRUISED RIBS & TAPED KNUCKLES",
            "EVERY MUSCLE BEGGED ME TO STAY\nHOME AND WAIT OUT THE CLOCK",
            "BUT RADIO REPEATERS WERE JAMMED\nWITH AN INSIDE MOLE ON SITE",
            "ONLY AN INVISIBLE GUARDIAN\nCOULD STOP TRACK 42 IN TIME",
        ],
    },
    {
        "shotId": 34,
        "chapterId": 9,
        "slug": "h9_suit_flicker_warning",
        "sfx": "camera_alert",
        "text": (
            "At eleven-forty PM, descending into Grand Central's cavernous marble concourse, disaster struck early! "
            "Just as I passed beneath the golden constellation ceiling—zap! My right hand and shoulder flickered solid "
            "for half a second like a failing hologram! My ten-day field was destabilizing hours ahead of schedule!"
        ),
        "cues": [
            "11:40 PM · GRAND CENTRAL HALL\nDESCENDING TOWARD LOWER TRACKS",
            "ZAP! MY RIGHT HAND FLASHED\nSOLID UNDER THE CHANDELIERS!",
            "FLICKERING LIKE A FAILING\nHOLOGRAM EVERY THIRTY SECONDS",
            "MY 10-DAY FIELD WAS COLLAPSING\nHOURS AHEAD OF SCHEDULE!",
        ],
    },
    {
        "shotId": 35,
        "chapterId": 9,
        "slug": "h9_track_42_sabotage_device",
        "sfx": "countdown_tick",
        "text": (
            "Timing my sprints strictly between shadow pillars whenever my skin shimmered, I dropped onto sub-level Track Forty-Two "
            "and spotted Kovács's two saboteurs clamping a magnetic derailment charge onto the junction rail—"
            "with the federal witness train approaching three minutes up the tunnel!"
        ),
        "cues": [
            "DARTED BETWEEN SHADOW PILLARS\nTIMING EVERY GLITCH FLASH",
            "DROPPED ONTO SUB-LEVEL TRACK 42\nIN THE HUMID DARK",
            "TWO SABOTEURS CLAMPING A CHARGE\nONTO THE JUNCTION SWITCH!",
            "WITNESS EXPRESS APPROACHING\nTHREE MINUTES UP THE TUNNEL!",
        ],
    },
    {
        "shotId": 36,
        "chapterId": 9,
        "slug": "h9_tunnel_fight_half_visible",
        "sfx": "impact_thud",
        "text": (
            "Halfway through disarming the first lookout, my stealth field strobed bright blue—exposing me face-to-face in the tunnel beam! "
            "He lunged for his suppressed pistol; I ducked under his swing, slammed the heavy steel switch lever across his wrist, "
            "and dove for the magnetic rail charge with forty-five seconds to impact!"
        ),
        "cues": [
            "MID-TAKEDOWN MY FIELD STROBED—\nEXPOSING ME FACE TO FACE!",
            "DUCKED UNDER HIS PISTOL SWING\nIN THE TUNNEL HEADLIGHT",
            "PINNED BOTH SABOTEURS WITH\nMY LAST CARBON ZIP-TIES",
            "45 SECONDS LEFT TO WRENCH THE\nCHARGE OFF THE LIVE RAIL!",
        ],
    },

    # ==================== DAY 10 ====================
    {
        "shotId": 37,
        "chapterId": 10,
        "slug": "h10_disarm_and_escape_sprint",
        "sfx": "train_horn",
        "text": (
            "Day Ten—final minutes! My fingers burned as I twisted the manual release pin, ripped the magnetic charge off the steel rail, "
            "and hurled it into the flooded drainage sump five seconds before the witness train glided safely past! "
            "Now my own countdown was flashing red: six minutes before I turned permanently human in a locked federal tunnel!"
        ),
        "cues": [
            "TWISTED THE RELEASE PIN AND\nRIPPED THE CHARGE OFF THE RAIL!",
            "WITNESS TRAIN GLIDED SAFELY\nPAST FIVE SECONDS LATER!",
            "NOW MY OWN TIMER FLASHED RED:\n00:06:00 LEFT ON DAY TEN!",
            "STROBING VISIBLE EVERY THREE\nSTEPS THROUGH DAWN STREETS!",
        ],
    },
    {
        "shotId": 38,
        "chapterId": 10,
        "slug": "h10_dawn_rooftop_homecoming",
        "sfx": "countdown_tick",
        "text": (
            "Pulling an abandoned hoodie out of a gym bin as my invisibility shattered into sparks of blue static, "
            "I sprinted up my fire escape, tumbled through my bathroom window at seven-oh-three AM, "
            "and gripped the marble sink watching the last glowing digits fade: three... two... one... zero."
        ),
        "cues": [
            "PULLED ON AN OVERSIZED HOODIE\nAS MY FIELD SHATTERED IN SPARKS",
            "UP MY FIRE ESCAPE AT 07:03 AM\nLUNGS BURNING IN DAWN AIR",
            "GRIPPED MY BATHROOM SINK AS\nTHE GLASS HIT 03... 02... 01...",
            "00:00:00 — THE REFRACTIVE HUM\nVANISHED FROM MY BONES",
        ],
    },
    {
        "shotId": 39,
        "chapterId": 10,
        "slug": "h10_hero_reflection_restored",
        "sfx": "glass_shimmer",
        "text": (
            "I looked up into the mirror—and there she was. Dark circles under hazel eyes, a small white bandage on my forearm, "
            "zero stolen millions in my bank account... yet standing taller than I had ever stood in my life. "
            "On my kitchen TV, breaking news scrolled: 'Kovács Arrested—Phantom Hero Saves Dozens, Then Vanishes Forever.'"
        ),
        "cues": [
            "MY OWN EYES STARED BACK—\nTIRED, BRUISED, AND UNBROKEN",
            "ZERO STOLEN MILLIONS IN CASH\nYET RICHER THAN ANY BILLIONAIRE",
            "BREAKING NEWS ON MY TV:\n'GUARDIAN PHANTOM SAVES DOZENS'",
            "SIXTEEN FAMILIES WHOLE TODAY\nBECAUSE NOBODY SAW ME COMING",
        ],
    },
    {
        "shotId": 40,
        "chapterId": 10,
        "slug": "h10_final_choice_question",
        "sfx": "suit_powerup",
        "text": (
            "Plato asked two thousand years ago: who are you when nobody is watching? "
            "Some people use darkness to take whatever they want; a rare few become the light inside it. "
            "If you watched both versions—tell me honestly in the comments: if you woke up invisible for ten days tomorrow, "
            "would you choose the Dark Temptation... or the Hero?"
        ),
        "cues": [
            "PLATO'S ULTIMATE QUESTION:\nWHO ARE YOU WHEN NOBODY SEES?",
            "SOME USE THE DARK TO TAKE—\nOTHERS BECOME THE SHIELD IN IT",
            "DARK TEMPTATION VS. SUPERHERO:\nYOU JUST SAW BOTH WORLDS",
            "COMMENT HONESTLY BELOW:\nWHICH 10 DAYS WOULD YOU CHOOSE?",
        ],
    },
]


def load_audio_mono(mp3_path: Path) -> np.ndarray:
    wav_tmp = mp3_path.with_suffix(".tmp.wav")
    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(mp3_path),
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


def align_cues_and_words(shot: dict, voice_start_sec: float, dur_sec: float) -> list[dict]:
    cues_txt = shot["cues"]
    out = []
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


def build_hero_sfx_kit(rng: np.random.Generator) -> dict[str, np.ndarray]:
    kit: dict[str, np.ndarray] = {}

    # 1. Heroic Orchestral-Synth Sub Boom + Brass Fifth
    t_b = np.linspace(0, 1.8, int(1.8 * SR), dtype=np.float32)
    freq_b = 82.0 * np.exp(-t_b * 2.1) + 36.0
    boom = np.sin(2 * np.pi * np.cumsum(freq_b) / SR) * np.exp(-t_b * 2.3) * 0.64
    fifth = (np.sin(2 * np.pi * 440.0 * t_b) + np.sin(2 * np.pi * 659.25 * t_b) * 0.7) * np.exp(-t_b * 3.4) * 0.09
    kit["chapter_boom"] = (boom + fifth).astype(np.float32)

    # 2. Tactical Stealth Whoosh
    t_w = np.linspace(0, 0.30, int(0.30 * SR), dtype=np.float32)
    env_w = np.maximum(0.0, np.sin(np.pi * (t_w / 0.30))) ** 1.8
    kit["whoosh"] = (lowpass_noise(rng, len(t_w), taps=16) * env_w * 0.21).astype(np.float32)

    # 3. Crystalline Refractive Shimmer
    t_s = np.linspace(0, 1.3, int(1.3 * SR), dtype=np.float32)
    shimmer = (
        np.sin(2 * np.pi * 1318.5 * t_s) * 0.14
        + np.sin(2 * np.pi * 1760.0 * t_s) * 0.10
        + np.sin(2 * np.pi * 2637.0 * t_s) * 0.07
    ) * np.exp(-t_s * 3.0)
    kit["glass_shimmer"] = shimmer.astype(np.float32)

    # 4. Stealth Suit Rising Harmonic Power-Up Sweep
    t_p = np.linspace(0, 1.1, int(1.1 * SR), dtype=np.float32)
    f_sweep = 220.0 + 660.0 * (t_p / 1.1) ** 1.5
    pup = np.sin(2 * np.pi * np.cumsum(f_sweep) / SR) * np.sin(np.pi * (t_p / 1.1)) * 0.20
    kit["suit_powerup"] = pup.astype(np.float32)

    # 5. Tactical Sonar Ping
    t_sp = np.linspace(0, 0.95, int(0.95 * SR), dtype=np.float32)
    ping = np.sin(2 * np.pi * 1046.5 * t_sp) * np.exp(-t_sp * 5.2) * 0.22
    kit["sonar_ping"] = ping.astype(np.float32)

    # 6. Kinetic Martial Takedown Impact Thud
    t_im = np.linspace(0, 0.38, int(0.38 * SR), dtype=np.float32)
    thud = (
        np.sin(2 * np.pi * (120.0 * np.exp(-t_im * 14.0) + 42.0) * t_im) * np.exp(-t_im * 11.0) * 0.55
        + lowpass_noise(rng, len(t_im), taps=8) * np.exp(-t_im * 26.0) * 0.26
    )
    kit["impact_thud"] = thud.astype(np.float32)

    # 7. NYC Express Subway Horn Blast (Distant Doppler Chord)
    t_tr = np.linspace(0, 1.35, int(1.35 * SR), dtype=np.float32)
    env_tr = np.minimum(1.0, t_tr * 8.0) * np.exp(-np.maximum(0.0, t_tr - 0.5) * 3.5)
    horn = (
        np.tanh((np.sin(2 * np.pi * 311.13 * t_tr) + np.sin(2 * np.pi * 392.0 * t_tr) * 0.85) * 1.4)
        * env_tr
        * 0.19
    )
    kit["train_horn"] = horn.astype(np.float32)

    # 8. Heartbeat Adrenaline Lub-Dub
    n_hb = int(1.25 * SR)
    hb = np.zeros(n_hb, dtype=np.float32)
    for off_s, amp in [(0.02, 0.52), (0.23, 0.38), (0.64, 0.50), (0.85, 0.36)]:
        p0 = int(off_s * SR)
        th = np.linspace(0, 0.16, int(0.16 * SR), dtype=np.float32)
        thump = np.sin(2 * np.pi * (58.0 * np.exp(-th * 8.0) + 34.0) * th) * np.exp(-th * 18.0) * amp
        hb[p0 : p0 + len(thump)] += thump
    kit["heartbeat_lubdub"] = hb

    # 9. Steam / Fire Hose / Boiler Plume Hiss
    t_st = np.linspace(0, 1.4, int(1.4 * SR), dtype=np.float32)
    env_st = np.maximum(0.0, np.sin(np.pi * (t_st / 1.4))) ** 1.3
    kit["steam_hiss"] = (lowpass_noise(rng, len(t_st), taps=8) * env_st * 0.22).astype(np.float32)

    # 10. Steel Lock / Door Click
    t_dc = np.linspace(0, 0.22, int(0.22 * SR), dtype=np.float32)
    click = (
        np.sin(2 * np.pi * 240.0 * t_dc) * np.exp(-t_dc * 34.0) * 0.42
        + lowpass_noise(rng, len(t_dc), taps=6) * np.exp(-t_dc * 55.0) * 0.28
    )
    kit["door_click"] = click.astype(np.float32)

    # 11. Tactical FLIR / Emergency Alert Beep
    n_al = int(0.75 * SR)
    al = np.zeros(n_al, dtype=np.float32)
    for b_off in [0.02, 0.22]:
        p0 = int(b_off * SR)
        tb = np.linspace(0, 0.12, int(0.12 * SR), dtype=np.float32)
        beep = np.tanh(np.sin(2 * np.pi * 1396.9 * tb) * 1.5) * np.exp(-tb * 14.0) * 0.23
        al[p0 : p0 + len(beep)] += beep
    kit["camera_alert"] = al

    # 12. Precision Countdown Tick
    n_tk = int(1.1 * SR)
    tk = np.zeros(n_tk, dtype=np.float32)
    for k_off in [0.02, 0.42, 0.82]:
        p0 = int(k_off * SR)
        tt = np.linspace(0, 0.05, int(0.05 * SR), dtype=np.float32)
        tick = np.sin(2 * np.pi * 1760.0 * tt) * np.exp(-tt * 85.0) * 0.22
        tk[p0 : p0 + len(tick)] += tick
    kit["countdown_tick"] = tk

    return kit


def synthesize_heroic_stealth_score(total_sec: float, rng: np.random.Generator) -> np.ndarray:
    """Hans Zimmer Dark-Knight / Tron-Legacy Heroic Stealth Pulse Score (84 -> 108 BPM)."""
    n_total = int(np.ceil(total_sec * SR)) + SR
    bed = np.zeros((n_total, 2), dtype=np.float32)

    # Soaring heroic minor-to-major progression (Dm -> Bbmaj7 -> F -> Csus4 -> Gm7 -> Bb -> F -> Asus4)
    chords = [
        (73.42, 110.00, 146.83, 220.00),   # Dm
        (58.27, 116.54, 146.83, 220.00),   # Bbmaj9
        (87.31, 130.81, 174.61, 261.63),   # Fmaj
        (65.41, 130.81, 174.61, 196.00),   # Csus4
        (98.00, 146.83, 174.61, 233.08),   # Gm7
        (58.27, 116.54, 174.61, 233.08),   # Bb
        (87.31, 130.81, 174.61, 220.00),   # F6
        (55.00, 110.00, 146.83, 164.81),   # Asus4 -> A
    ]

    block_len = int(11.0 * SR)
    num_blocks = int(np.ceil(n_total / block_len))

    for b in range(num_blocks):
        i0 = b * block_len
        i1 = min(n_total, (b + 1) * block_len)
        m = i1 - i0
        t = np.arange(m, dtype=np.float32) / SR
        f1, f2, f3, f4 = chords[b % len(chords)]

        lfo_l = 0.76 + 0.24 * np.sin(2 * np.pi * 0.14 * t)
        lfo_r = 0.76 + 0.24 * np.cos(2 * np.pi * 0.14 * t)

        left = (
            np.sin(2 * np.pi * f1 * t) * 0.080
            + np.sin(2 * np.pi * (f2 * 1.002) * t) * 0.050
            + np.sin(2 * np.pi * f3 * t) * 0.034
            + np.sin(2 * np.pi * (f4 * 0.998) * t) * 0.022
        ) * lfo_l
        right = (
            np.sin(2 * np.pi * (f1 * 0.999) * t) * 0.080
            + np.sin(2 * np.pi * f2 * t) * 0.050
            + np.sin(2 * np.pi * (f3 * 1.003) * t) * 0.034
            + np.sin(2 * np.pi * f4 * t) * 0.022
        ) * lfo_r

        # Driving Dark-Knight sixteenth/eighth ostinato sub-pulse (84 -> 108 BPM)
        bpm = 84.0 + 24.0 * (b / max(1, num_blocks - 1))
        p_phase = (t * (bpm / 30.0)) % 1.0
        pulse = (
            np.sin(2 * np.pi * f1 * 0.75 * p_phase)
            * np.minimum(1.0, p_phase * 30.0)
            * np.exp(-p_phase * 8.5)
            * 0.072
        )

        air_l = lowpass_noise(rng, m, taps=28) * 0.010
        air_r = lowpass_noise(rng, m, taps=28) * 0.010

        bed[i0:i1, 0] = left + pulse + air_l
        bed[i0:i1, 1] = right + pulse + air_r

    fi_n = min(n_total, int(0.8 * SR))
    fo_n = min(n_total, int(1.8 * SR))
    bed[:fi_n, :] *= np.linspace(0.0, 1.0, fi_n, dtype=np.float32)[:, None]
    bed[-fo_n:, :] *= np.linspace(1.0, 0.0, fo_n, dtype=np.float32)[:, None]
    return bed


async def main():
    print("[Invisible 10Days HERO] Synthesizing 40 female-POV superhero shots with Edge-TTS (en-US-AvaNeural)...")
    sem = asyncio.Semaphore(4)
    tasks = [synth_shot(shot, sem) for shot in SHOT_SCRIPT]
    shot_results = await asyncio.gather(*tasks)
    shot_results.sort(key=lambda r: r["shot"]["shotId"])

    raw_vo_sum = sum(r["durationSec"] for r in shot_results)
    min_target_sec = 625.0
    base_overhead = 10 * 1.40 + 40 * (0.28 + 0.42) + 1.2
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

        lead_pad = (1.40 if is_chapter_start else 0.28) + extra_per_shot * 0.35
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

        cues = align_cues_and_words(shot, voice_start_sec, res["durationSec"])
        all_cues.extend(cues)

        shots_timeline.append(
            {
                "shotId": shot["shotId"],
                "chapterId": ch_id,
                "isChapterStart": is_chapter_start,
                "slug": shot["slug"],
                "sfx": shot.get("sfx", "glass_shimmer"),
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
    print(f"[Invisible 10Days HERO] Master Duration: {mins:02d}:{secs:05.2f} ({total_sec:.2f}s / {total_frames} frames @ {FPS}fps)")

    rng = np.random.default_rng(20262020)
    sfx = build_hero_sfx_kit(rng)
    bed = synthesize_heroic_stealth_score(total_sec, rng)
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
            duck[d0:d1] = np.minimum(duck[d0:d1], 0.35)

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
            sfx_events.append((max(0.0, cut_s - 3.0 / FPS), "whoosh", 0.56))

        kind = st["sfx"]
        offset = 0.80 if st["isChapterStart"] else 0.18
        if kind in sfx:
            sfx_events.append((cut_s + offset, kind, 0.60))

    for ev_sec, kind, gain in sfx_events:
        clip = sfx[kind]
        s_i = int(ev_sec * SR)
        e_i = min(n_total, s_i + len(clip))
        if e_i > s_i:
            bed[s_i:e_i, 0] += clip[: e_i - s_i] * gain
            bed[s_i:e_i, 1] += clip[: e_i - s_i] * gain * 0.96

    mix = np.zeros_like(bed)
    mix[:, 0] = bed[:, 0] * 0.75 + vo_L * 0.96
    mix[:, 1] = bed[:, 1] * 0.75 + vo_R * 0.96
    mix = np.tanh(mix * 0.95) * 0.86

    OUT_AUDIO.parent.mkdir(parents=True, exist_ok=True)
    wav_master = STUDIO_DIR / "out" / "invisible_hero_tmp.wav"
    pcm16 = np.clip(np.round(mix * 32767.0), -32768, 32767).astype(np.int16)
    with wave.open(str(wav_master), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

    print("[Invisible 10Days HERO] Normalizing master broadcast audio (-16 LUFS)...")
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

    print("\n=== YOUTUBE CHAPTER TIMESTAMPS (HERO EDITION) ===")
    for ch in chapters_timeline:
        m = int(ch["startSec"] // 60)
        s = int(ch["startSec"] % 60)
        print(f"{m:02d}:{s:02d} {ch['code']} — {ch['title']}")

    OUT_TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    ts_content = f"""// Auto-generated by scripts/build_invisible_10days_hero_audio.py
import type {{ CaptionCue }} from "../ifnoir/alcatrazPilotTimeline";
import type {{ Docu10MinShotTiming, DocuChapterTiming }} from "../ifnoir/alcatraz10MinTimeline";

export const INVISIBLE_HERO_FPS = {FPS};
export const INVISIBLE_HERO_TOTAL_FRAMES = {total_frames};
export const INVISIBLE_HERO_DURATION_SEC = {round(total_sec, 3)};

export const INVISIBLE_HERO_CHAPTERS: readonly DocuChapterTiming[] = {json.dumps(chapters_timeline, indent=2)} as const;

export const INVISIBLE_HERO_SHOTS: readonly Docu10MinShotTiming[] = {json.dumps(shots_export, indent=2)} as const;

export const INVISIBLE_HERO_CUES: readonly CaptionCue[] = {json.dumps(all_cues, indent=2)} as const;
"""
    OUT_TIMELINE.write_text(ts_content, encoding="utf-8")
    print(f"[Invisible 10Days HERO] Done! Saved {OUT_AUDIO.name} & {OUT_TIMELINE.name} ({len(all_cues)} cues).")


if __name__ == "__main__":
    asyncio.run(main())
