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

TMP_VO_DIR = STUDIO_DIR / "out" / "vo_invisible_nsfw_tmp"
OUT_AUDIO = STUDIO_DIR / "public" / "audio" / "invisible_10days_nsfw_master.mp3"
OUT_TIMELINE = STUDIO_DIR / "src" / "invisible" / "invisible10DaysNsfwTimeline.ts"

SR = 44100
FPS = 30

# Expressive, intimate, razor-sharp US female first-person narrator
VOICE_ID = "en-US-AvaNeural"
VOICE_RATE = "+2%"
VOICE_PITCH = "-2Hz"

CHAPTERS = [
    {"chapterId": 1, "code": "DAY 01", "title": "07:04 AM: NO REFLECTION & THE NAKED CATCH"},
    {"chapterId": 2, "code": "DAY 02", "title": "LOCKER ROOMS, SAUNAS & UNFILTERED SECRETS"},
    {"chapterId": 3, "code": "DAY 03", "title": "10:15 PM: CATCHING MY EX RED-HANDED"},
    {"chapterId": 4, "code": "DAY 04", "title": "VELVET ROPES & BILLIONAIRE VIP SUITES"},
    {"chapterId": 5, "code": "DAY 05", "title": "PRESIDENTIAL SUITES & FORBIDDEN VOYEURISM"},
    {"chapterId": 6, "code": "DAY 06", "title": "DIRTY MILLIONS: THE LAUNDRY CART HEIST"},
    {"chapterId": 7, "code": "DAY 07", "title": "3:00 AM INSOMNIA: THE TRANSPARENT EYELID CURSE"},
    {"chapterId": 8, "code": "DAY 08", "title": "98.6°F EXPOSED: CAUGHT ON THERMAL CAMERA"},
    {"chapterId": 9, "code": "DAY 09", "title": "GOD COMPLEX, SISTER'S SECRET & THE GLITCH"},
    {"chapterId": 10, "code": "DAY 10", "title": "FINAL 60 SECONDS & THE MIRROR TWIST"},
]

SHOT_SCRIPT = [
    # ==================== DAY 01 ====================
    {
        "shotId": 1,
        "chapterId": 1,
        "slug": "d1_mirror_shock",
        "sfx": "glass_shimmer",
        "text": (
            "I woke up at seven-oh-four AM on a Tuesday, dragged myself into my Manhattan bathroom, "
            "and wiped a streak of steam off the mirror. Nobody looked back at me. "
            "Just my crimson silk robe hanging in empty air—and a glowing countdown etched into the fogged glass: "
            "two hundred forty hours. Ten days."
        ),
        "cues": [
            "TUESDAY · 07:04 AM\nI WIPED THE FOGGED MIRROR",
            "NOBODY STARE BACK AT ME\nNO FACE · NO SKIN · NOTHING",
            "JUST MY CRIMSON SILK ROBE\nFLOATING IN EMPTY AIR",
            "240 HOURS ON THE GLASS:\nTEN DAYS COMPLETELY INVISIBLE",
        ],
    },
    {
        "shotId": 2,
        "chapterId": 1,
        "slug": "d1_lipstick_and_shower",
        "sfx": "steam_hiss",
        "text": (
            "At first I thought I was hallucinating. I pinched my bare arm—I felt the sting, heard my own gasp, "
            "and watched a tube of red lipstick float upward in my invisible fingers and kiss the mirror. "
            "When I stepped under the hot shower, cascading water traced every curve of my body in shimmering steam, then vanished."
        ),
        "cues": [
            "I PINCHED MY OWN ARM\nFELT EVERY SINGLE NERVE",
            "WATCHED MY RED LIPSTICK\nFLOAT UP AND KISS THE GLASS",
            "UNDER THE HOT SHOWER SPRAY\nSTEAM TRACED EVERY CURVE",
            "A LIVING GHOST MADE OF\nFLESH, HEAT, AND BREATH",
        ],
    },
    {
        "shotId": 3,
        "chapterId": 1,
        "slug": "d1_clothes_stay_visible",
        "sfx": "heartbeat_lubdub",
        "text": (
            "Then came the awkward, spicy catch Hollywood conveniently leaves out. "
            "Only my living tissue was bending light. My lace underwear, my oversized hoodie, my sneakers, even a hair tie—"
            "all of them stayed one hundred percent visible. If I wanted to walk outside unseen, I couldn't wear a single thread."
        ),
        "cues": [
            "THEN CAME THE AWKWARD CATCH\nHOLLYWOOD NEVER MENTIONS",
            "ONLY MY LIVING SKIN BENT LIGHT\nEVERY THREAD STAYED VISIBLE",
            "LACE, HOODIES, HEELS, RINGS—\nFLOATING IN BROAD DAYLIGHT",
            "TO WALK OUTSIDE UNSEEN\nI HAD TO STRIP COMPLETELY BARE",
        ],
    },
    {
        "shotId": 4,
        "chapterId": 1,
        "slug": "d1_hallway_barefoot_step",
        "sfx": "door_click",
        "text": (
            "Heart hammering at a hundred forty beats a minute, cold hallway air raising goosebumps across every inch of me, "
            "I let my silk robe pool at my ankles and cracked open my apartment door. "
            "My attractive neighbor Liam walked past six inches from my bare shoulder, scrolling his phone—and looked right through me."
        ),
        "cues": [
            "HEART HAMMERING AT 140 BPM\nCOLD AIR ON BARE SKIN",
            "I LET MY SILK ROBE DROP\nAND OPENED THE FRONT DOOR",
            "MY NEIGHBOR WALKED PAST\nSIX INCHES FROM MY FACE",
            "STARING STRAIGHT THROUGH ME\nLIKE I WAS EMPTY AIR",
        ],
    },

    # ==================== DAY 02 ====================
    {
        "shotId": 2 + 3,
        "chapterId": 2,
        "slug": "d2_office_and_cafe_truths",
        "sfx": "champagne_clink",
        "text": (
            "By Day Two, embarrassment turned into the most intoxicating rush of my life. "
            "Wait for a stranger to push open a café door, slip through behind their coat, and suddenly the whole city drops its mask. "
            "Within an hour at my own agency, I heard what my boss and coworkers really said about me behind my back."
        ),
        "cues": [
            "BY DAY TWO, SHAME TURNED\nINTO PURE ADRENALINE",
            "SLIP THROUGH ANY GLASS DOOR\nRIGHT BEHIND A STRANGER",
            "SUDDENLY THE ENTIRE CITY\nDROPS ITS POLITE MASK",
            "I HEARD EVERY WORD PEOPLE\nSAID BEHIND MY BACK",
        ],
    },
    {
        "shotId": 6,
        "chapterId": 2,
        "slug": "d2_luxury_sauna_sneak",
        "sfx": "steam_hiss",
        "text": (
            "Curiosity is a dangerous drug when no door can stop you. That afternoon I slipped into Soho's most exclusive health club—"
            "past the front desk, through the women's lounge, and straight through the cedar door of the men's steam sauna. "
            "Let's just say men talk very differently when they swear no woman is within fifty feet—though dodging flying towels took reflexes."
        ),
        "cues": [
            "CURIOSITY TURNS RECKLESS\nWHEN NO DOOR CAN STOP YOU",
            "SLIPPED PAST RECEPTION INTO\nAN EXCLUSIVE SOHO CLUB",
            "STRAIGHT INSIDE THE STEAM\nSAUNA & LOCKER LOUNGE",
            "DODGING TOWELS WHILE HEARING\nEVERY UNFILTERED CONFESSION",
        ],
    },
    {
        "shotId": 7,
        "chapterId": 2,
        "slug": "d2_psychology_of_voyeurism",
        "sfx": "countdown_tick",
        "text": (
            "Psychologists have actually tested this exact question for decades. When promised total anonymity, "
            "over ninety percent of adults admit their very first day invisible wouldn't be saving the world—"
            "it would be crossing private boundaries, reading locked phones over shoulders, and watching forbidden rooms unseen."
        ),
        "cues": [
            "PSYCHOLOGISTS TESTED THIS\nQUESTION UNDER ANONYMITY",
            "OVER 90% ADMIT THEIR FIRST\nMOVE WOULDN'T BE HEROIC",
            "IT WOULD BE SNOOPING PHONES\nAND CROSSING CLOSED DOORS",
            "BECAUSE MORALS CHANGE FAST\nWHEN NOBODY CAN SEE YOU",
        ],
    },
    {
        "shotId": 8,
        "chapterId": 2,
        "slug": "d2_rain_silhouette_scare",
        "sfx": "glass_shimmer",
        "text": (
            "Walking back at dusk taught me my second survival lesson. A sudden spring drizzle swept across Broadway—"
            "and raindrops began splashing off my invisible hair and shoulders, carving a shimmering woman-shaped shell in mid-air! "
            "I bolted under a theater awning just before a taxi driver stared twice at the empty sidewalk."
        ),
        "cues": [
            "DUSK BROUGHT MY FIRST\nTERRIFYING NEAR-MISS",
            "RAIN BEGAN SPLASHING OFF\nMY INVISIBLE SHOULDERS",
            "CARVING A WOMAN-SHAPED SHELL\nIN THE NEON DRIZZLE",
            "DUCKED UNDER AN AWNING BEFORE\nSTRANGERS SAW A GHOST",
        ],
    },

    # ==================== DAY 03 ====================
    {
        "shotId": 9,
        "chapterId": 3,
        "slug": "d3_ex_loft_infiltration",
        "sfx": "door_click",
        "text": (
            "Day Three got personal. Two weeks earlier, my ex Ryan looked me dead in the eyes and swore he wasn't seeing anyone—"
            "he just needed 'mental space to focus on his career.' At ten-fifteen PM, I rode the Tribeca elevator up behind a sushi delivery guy "
            "and walked barefoot straight into Ryan's loft."
        ),
        "cues": [
            "DAY THREE GOT PERSONAL:\nMY EX-BOYFRIEND RYAN",
            "SWORE TWO WEEKS AGO HE JUST\nNEEDED 'MENTAL SPACE'",
            "10:15 PM: I RODE HIS ELEVATOR\nBEHIND A DELIVERY DRIVER",
            "AND STEPPED BAREFOOT INTO\nHIS CANDLELIT TRIBECA LOFT",
        ],
    },
    {
        "shotId": 10,
        "chapterId": 3,
        "slug": "d3_best_friend_betrayal",
        "sfx": "heartbeat_lubdub",
        "text": (
            "Two crystal wine glasses sat on the kitchen island. A familiar emerald dress was draped over the armchair. "
            "And curled up on his leather sofa laughing at an inside joke was Chloe—my supposed best friend who brought me ice cream "
            "and told me I was 'overthinking things.' I stood three feet away in dead silence, watching every shameless lie."
        ),
        "cues": [
            "TWO CRYSTAL WINE GLASSES\nAN EMERALD SILK DRESS",
            "LAUGHING ON HIS SOFA WAS\nMY 'BEST FRIEND' CHLOE",
            "THE SAME FRIEND WHO TOLD ME\nI WAS JUST OVERTHINKING",
            "I STOOD THREE FEET AWAY\nWATCHING EVERY SINGLE LIE",
        ],
    },
    {
        "shotId": 11,
        "chapterId": 3,
        "slug": "d3_poltergeist_revenge",
        "sfx": "champagne_clink",
        "text": (
            "Old me would have cried. Invisible me smiled. While they stepped onto the balcony, I unlocked Ryan's phone with his birthday code, "
            "airdropped his secret chat thread straight to Chloe's fiancé, tipped a six-hundred-dollar Cabernet across his white rug, "
            "and wrote 'SPACE LOOKS CROWDED' in crimson lipstick across his mirror."
        ),
        "cues": [
            "OLD ME WOULD HAVE CRIED—\nINVISIBLE ME JUST SMILED",
            "UNLOCKED HIS PHONE AND SENT\nRECEIPTS TO CHLOE'S FIANCÉ",
            "POURED HIS $600 CABERNET\nACROSS HIS DESIGNER RUG",
            "WROTE 'SPACE LOOKS CROWDED'\nIN LIPSTICK ON THE GLASS",
        ],
    },
    {
        "shotId": 12,
        "chapterId": 3,
        "slug": "d3_dopamine_god_complex",
        "sfx": "glass_shimmer",
        "text": (
            "Watching two liars panic as letters appeared out of thin air triggered a terrifying realization. "
            "When every social consequence evaporates, your brain floods with raw dopamine. "
            "By midnight of Day Three, I wasn't scared of being invisible anymore—I was starting to feel untouchable."
        ),
        "cues": [
            "WATCHING TWO LIARS PANIC\nFLIPPED A SWITCH INSIDE ME",
            "ZERO CONSEQUENCES FLOODS\nTHE BRAIN WITH DOPAMINE",
            "BY MIDNIGHT OF DAY THREE\nTHE FEAR WAS COMPLETELY GONE",
            "I WAS STARTING TO FEEL\nLIKE AN UNTOUCHABLE GOD",
        ],
    },

    # ==================== DAY 04 ====================
    {
        "shotId": 13,
        "chapterId": 4,
        "slug": "d4_velvet_rope_penthouse",
        "sfx": "champagne_clink",
        "text": (
            "Day Four: why waste ten days on exes when Manhattan's highest velvet ropes mean nothing? "
            "At midnight I glided past two armed bouncers into an invitation-only billionaire penthouse party above Central Park—"
            "lifting chilled vintage champagne off silver trays while bartenders stared at the missing glass."
        ),
        "cues": [
            "DAY FOUR: EVERY VELVET ROPE\nIN MANHATTAN DISAPPEARED",
            "GLIDED PAST ARMED BOUNCERS\nINTO A BILLIONAIRE PENTHOUSE",
            "LIFTING VINTAGE CHAMPAGNE\nRIGHT OFF PASSING TRAYS",
            "FORTY-FOUR FLOORS ABOVE\nCENTRAL PARK UNINVITED",
        ],
    },
    {
        "shotId": 14,
        "chapterId": 4,
        "slug": "d4_vip_suite_44_secrets",
        "sfx": "door_click",
        "text": (
            "Behind the soundproof doors of Suite Forty-Four, tech moguls, senators, and A-list stars dropped their wholesome PR personas "
            "in seconds. Insider stock tips, hush-money NDAs, secret affairs—people with nine-figure net worths talk freely "
            "when they think the room is swept for microphones, never imagining a naked woman leaning against the marble bar."
        ),
        "cues": [
            "BEHIND SOUNDPROOF DOORS IN\nPRIVATE VIP SUITE 44",
            "TECH MOGULS & POLITICIANS\nDROPPED THEIR PR MASKS",
            "INSIDER TRADES · HUSH NDAS\nAND BACKROOM SCANDALS",
            "SWEEPING FOR MICROPHONES—\nNEVER EXPECTING A GHOST",
        ],
    },
    {
        "shotId": 15,
        "chapterId": 4,
        "slug": "d4_perfume_near_miss",
        "sfx": "heartbeat_lubdub",
        "text": (
            "Then I made a rookie mistake that almost ended everything. Out of pure feminine habit before leaving home, "
            "I had spritzed vanilla-amber perfume on my neck! A former Secret Service bodyguard paused, narrowed his eyes, "
            "sniffed the empty corner, and swept his arm two inches past my bare ribs while I held my breath."
        ),
        "cues": [
            "ONE FEMININE HABIT ALMOST\nGOT ME CAUGHT INSTANTLY",
            "I HAD SPRITZED VANILLA\nPERFUME ON MY BARE NECK!",
            "A BODYGUARD STOPPED COLD\nAND SNIFFED THE EMPTY AIR",
            "HIS HAND SWEPT TWO INCHES\nPAST MY RIBS IN SILENCE",
        ],
    },
    {
        "shotId": 16,
        "chapterId": 4,
        "slug": "d4_five_physical_traps",
        "sfx": "countdown_tick",
        "text": (
            "That night I wrote down the Five Real Rules of Invisibility. No perfume or scented lotion. "
            "Stay ten feet away from guard dogs. Watch dusty carpets that print bare toes. Control cold breath vapor. "
            "And the weirdest biological catch of all: anything you eat or drink stays visible floating inside your stomach until your body digests it!"
        ),
        "cues": [
            "FIVE SURVIVAL TRAPS OF\nREAL-WORLD INVISIBILITY",
            "NO PERFUME · NO DUSTY FLOORS\nAND AVOID EVERY GUARD DOG",
            "PLUS THE WEIRDEST CATCH:\nFOOD STAYS VISIBLE INSIDE YOU",
            "FLOATING IN MID-AIR UNTIL\nYOUR STOMACH DIGESTS IT!",
        ],
    },

    # ==================== DAY 05 ====================
    {
        "shotId": 17,
        "chapterId": 5,
        "slug": "d5_presidential_suite_life",
        "sfx": "champagne_clink",
        "text": (
            "Halfway mark: Day Five, one hundred twenty hours left. By now I stopped sleeping in my tiny walk-up apartment altogether. "
            "Whenever guests checked out or went to dinner at a five-star Fifth Avenue hotel, their fifteen-thousand-dollar presidential suite "
            "became mine—marble jacuzzi tubs, panoramic skyline views, and silk sheets."
        ),
        "cues": [
            "DAY FIVE · HALFWAY MARK\n120 HOURS REMAINING",
            "DITCHED MY TINY WALK-UP FOR\n$15,000 HOTEL PENTHOUSES",
            "SOAKING IN MARBLE JACUZZIS\nWHILE GUESTS WENT TO DINNER",
            "LIVING LIKE ROYALTY IN A\nWORLD THAT COULDN'T SEE ME",
        ],
    },
    {
        "shotId": 18,
        "chapterId": 5,
        "slug": "d5_honeymoon_suite_trapped",
        "sfx": "heartbeat_lubdub",
        "text": (
            "Until Friday night—when the newlywed couple came back from dinner two hours early while I was still inside their suite! "
            "Deadbolted from the inside, I had to press my bare back against the velvet corner curtain in absolute silence "
            "as champagne corks popped ten feet away—trapped in a stranger's most intimate night with nowhere to run."
        ),
        "cues": [
            "UNTIL THE SUITE OWNERS CAME\nBACK TWO HOURS EARLY!",
            "DEADBOLTED INSIDE WITH ZERO\nWAY TO REACH THE DOOR",
            "PRESSED AGAINST THE VELVET\nCURTAIN HOLDING MY BREATH",
            "TRAPPED INSIDE STRANGERS'\nMOST INTIMATE MOMENTS",
        ],
    },
    {
        "shotId": 19,
        "chapterId": 5,
        "slug": "d5_midnight_balcony_skyline",
        "sfx": "glass_shimmer",
        "text": (
            "When they finally fell asleep at two AM, I unlatched the terrace door and stepped out onto the fortieth-floor balcony. "
            "Shivering in the warm midnight wind, looking across ten thousand glowing bedroom windows across Manhattan, "
            "it hit me how paper-thin human privacy really is—and how dangerously addictive watching from the dark had become."
        ),
        "cues": [
            "AT 2:00 AM I SLIPPED OUT\nONTO THE 40TH-FLOOR LEDGE",
            "TEN THOUSAND LIT BEDROOM\nWINDOWS GLOWING ACROSS NYC",
            "REALIZING HOW PAPER-THIN\nHUMAN PRIVACY REALLY IS",
            "AND HOW ADDICTIVE WATCHING\nFROM THE DARK HAD BECOME",
        ],
    },
    {
        "shotId": 20,
        "chapterId": 5,
        "slug": "d5_mirror_neuron_loneliness",
        "sfx": "countdown_tick",
        "text": (
            "Yet beneath the thrill, something eerie started creeping in on Day Five. "
            "For five straight days, not a single human eye had met mine. Nobody smiled when I walked by, nobody heard my voice. "
            "Neuroscientists call it sensory-social deprivation—stay unseen long enough, and you start wondering if you're still real."
        ),
        "cues": [
            "YET BENEATH THE THRILL\nSOMETHING DARK CREPT IN",
            "FIVE STRAIGHT DAYS WITHOUT\nA SINGLE HUMAN GLANCE",
            "NO EYE CONTACT · NO TOUCH\nNO VOICE ANSWERING MINE",
            "STAY UNSEEN LONG ENOUGH AND\nYOU QUESTION IF YOU'RE REAL",
        ],
    },

    # ==================== DAY 06 ====================
    {
        "shotId": 21,
        "chapterId": 6,
        "slug": "d6_corrupt_poker_penthouse",
        "sfx": "door_click",
        "text": (
            "Day Six woke me up with cold math: in four days I'd be visible again with rent overdue. "
            "Stealing from normal working people felt disgusting—so I remembered a tip I overheard in Suite Forty-Four: "
            "a corrupt hedge-fund shark running an unlicensed, cash-only high-roller poker vault in Midtown."
        ),
        "cues": [
            "DAY SIX: FOUR DAYS LEFT\nBEFORE REALITY RETURNS",
            "STEALING FROM ORDINARY PEOPLE\nWAS NEVER AN OPTION",
            "SO I TARGETED A CORRUPT\nMIDTOWN HIGH-ROLLER VAULT",
            "MILLIONS IN UNREPORTED CASH\nNOBODY COULD REPORT STOLEN",
        ],
    },
    {
        "shotId": 22,
        "chapterId": 6,
        "slug": "d6_safe_code_over_shoulder",
        "sfx": "countdown_tick",
        "text": (
            "At three-ten AM, after the last players stumbled out, I stood ten inches behind the host's shoulder "
            "as he keyed six digits into a hidden steel safe behind a Basquiat print: eight-four, one-nine, zero-six. "
            "Inside sat neatly banded bricks of untraceable hundreds and two cold-storage crypto ledgers."
        ),
        "cues": [
            "03:10 AM: PLAYERS GONE—\nI STOOD TEN INCHES BEHIND HIM",
            "WATCHED HIM KEY SIX DIGITS:\nCODE 84 · 19 · 06",
            "STACKS OF UNREPORTED $100S\nAND COLD CRYPTO DRIVES",
            "SITTING WIDE OPEN BEHIND\nA FRAMED GALLERY WALL",
        ],
    },
    {
        "shotId": 23,
        "chapterId": 6,
        "slug": "d6_laundry_cart_trick",
        "sfx": "door_click",
        "text": (
            "Here's the heist puzzle every movie gets wrong: if I stuffed cash into a duffel bag and ran, "
            "every hallway camera would film a floating bag sprinting for the elevator! Instead, I waited until the night cleaner "
            "stepped into the restroom, buried twelve cash bricks under dirty tablecloths in his rolling linen cart, and rode freight down."
        ),
        "cues": [
            "THE PUZZLE MOVIES FORGET:\nCASH DOESN'T TURN INVISIBLE!",
            "CARRY A BAG AND CAMERAS SEE\nLUGGAGE FLOATING IN MID-AIR",
            "SO I BURIED $1.2 MILLION UNDER\nLINENS IN A SERVICE CART",
            "AND ROLLED IT DOWN FREIGHT\nLIKE WIND DRIFTING WHEELS",
        ],
    },
    {
        "shotId": 24,
        "chapterId": 6,
        "slug": "d6_storage_locker_stash",
        "sfx": "glass_shimmer",
        "text": (
            "Before sunrise, one point two-four million dollars sat locked inside a twenty-four-hour self-storage unit "
            "rented online under a prepaid card. Zero witnesses, zero victims who could call the police—though I wiped every bill "
            "with alcohol, because invisible fingertips still leave very real human skin oil."
        ),
        "cues": [
            "$1,240,000 LOCKED INSIDE A\n24-HOUR STORAGE LOCKER",
            "ZERO WITNESSES · ZERO THIEVES\nWHO COULD CALL THE COPS",
            "WIPED EVERY SURFACE CLEAN\nWITH RUBBING ALCOHOL",
            "BECAUSE INVISIBLE FINGERS\nSTILL LEAVE REAL DNA & OIL",
        ],
    },

    # ==================== DAY 07 ====================
    {
        "shotId": 25,
        "chapterId": 7,
        "slug": "d7_transparent_eyelids_insomnia",
        "sfx": "heartbeat_lubdub",
        "text": (
            "By Day Seven, my body started rebelling in a way I never saw coming. "
            "Think about it: why do we close our eyes to sleep? To block light. When your eyelids are completely transparent, "
            "closing your eyes changes nothing! Streetlights and dawn sun blazed straight through my shut eyelids at four AM."
        ),
        "cues": [
            "DAY SEVEN BROUGHT THE CURSE\nNOBODY EVER THINKS ABOUT",
            "WHEN YOUR EYELIDS ARE CLEAR\nCLOSING THEM BLOCKS NOTHING!",
            "NEON SIGNS & DAWN SUNLIGHT\nBLAZE STRAIGHT THROUGH",
            "BY HOUR 160, INSOMNIA WAS\nPUSHING ME TOWARD DELIRIUM",
        ],
    },
    {
        "shotId": 26,
        "chapterId": 7,
        "slug": "d7_retina_optics_paradox",
        "sfx": "glass_shimmer",
        "text": (
            "Even weirder was how my vision shifted. Under strict optics, if light passes completely through your retinas, "
            "you'd be blind—so whatever anomaly bent visible wavelengths around me left near-infrared light hitting my optic nerves, "
            "turning night streets into a hyper-vivid, pulsing violet halo that gave me splitting migraines."
        ),
        "cues": [
            "THE OPTICS PARADOX OF\nTRANSPARENT HUMAN EYES",
            "VISIBLE LIGHT BENT AROUND ME\nWHILE NEAR-IR HIT MY RETINAS",
            "TURNING DARK CITY STREETS\nINTO A PULSING NEON HALO",
            "EVERY SUPERPOWER CARRIES\nA HIDDEN BIOLOGICAL TAX",
        ],
    },
    {
        "shotId": 27,
        "chapterId": 7,
        "slug": "d7_taxi_near_death",
        "sfx": "camera_alert",
        "text": (
            "Exhausted at noon on Seventh Avenue, I stepped off the curb—and a speeding yellow cab missed my bare hip by three inches! "
            "I froze on the median shaking. Drivers don't brake for empty air. And if a car broke my ribs, how would an ER surgeon "
            "put an IV needle or a scalpel into a woman they literally cannot see?"
        ),
        "cues": [
            "EXHAUSTED AT NOON, A TAXI\nMISSED MY HIP BY 3 INCHES!",
            "DRIVERS NEVER HIT THE BRAKES\nFOR EMPTY CROSSWALKS",
            "AND IF AN AMBULANCE CAME—\nHOW WOULD SURGEONS OPERATE?",
            "YOU CAN'T STITCH AN ARTERY\nYOU LITERALLY CANNOT SEE",
        ],
    },
    {
        "shotId": 28,
        "chapterId": 7,
        "slug": "d7_medical_hazard_hud",
        "sfx": "countdown_tick",
        "text": (
            "Suddenly, walking around a crowded metropolis naked and unseen didn't feel invincible anymore. "
            "Subway platform crowds could crush you into the tracks, revolving doors could slam on your fingers, "
            "and seventy-two hours suddenly felt like surviving a minefield."
        ),
        "cues": [
            "SUDDENLY INVINCIBILITY FELT\nLIKE WALKING A MINEFIELD",
            "CROWDS SHOVING NEAR SUBWAY\nTRACKS WITHOUT SEEING YOU",
            "AUTOMATIC DOORS & TRAFFIC\nTURNED LETHAL OVERNIGHT",
            "ONLY 72 HOURS LEFT TO MAKE\nIT BACK IN ONE PIECE",
        ],
    },

    # ==================== DAY 08 ====================
    {
        "shotId": 29,
        "chapterId": 8,
        "slug": "d8_one_last_score_mistake",
        "sfx": "door_click",
        "text": (
            "Day Eight: forty-eight hours left. Smart people quit while they're ahead—which is exactly why greed nearly ruined me. "
            "Tempted by one more corrupt lobbyist's townhouse near Upper East Side, I slipped through the service gate after midnight, "
            "not realizing private security across Manhattan was already on high alert."
        ),
        "cues": [
            "DAY EIGHT · 48 HOURS LEFT\nGREED ALMOST RUINED EVERYTHING",
            "TEMPTED BY ONE LAST SECRET\nTOWNHOUSE ON UPPER EAST SIDE",
            "SLIPPED PAST THE IRON GATE\nAT 12:40 AM IN THE DARK",
            "UNAWARE PRIVATE SECURITY\nHAD JUST UPGRADED CAMERAS",
        ],
    },
    {
        "shotId": 30,
        "chapterId": 8,
        "slug": "d8_flir_thermal_camera_reveal",
        "sfx": "camera_alert",
        "text": (
            "Halfway down the marble corridor, I glanced through the security booth glass—and my blood froze solid. "
            "Screen One showed an empty hallway. Screen Two was a military-grade FLIR thermal infrared camera—and glowing bright neon orange "
            "at ninety-eight-point-six degrees Fahrenheit was my unmistakable naked female silhouette staring right at the lens!"
        ),
        "cues": [
            "GLANCED INSIDE THE GUARD BOOTH\nAND MY BLOOD TURNED TO ICE",
            "REGULAR CCTV SCREEN ONE:\nEMPTY MARBLE CORRIDOR",
            "FLIR THERMAL CAM SCREEN TWO:\nBLAZING 98.6°F BODY HEAT!",
            "MY ENTIRE NAKED SILHOUETTE\nGLOWING ON HIS MONITOR!",
        ],
    },
    {
        "shotId": 31,
        "chapterId": 8,
        "slug": "d8_co2_extinguisher_escape",
        "sfx": "steam_hiss",
        "text": (
            "Red alarms flashed! Two guards bolted out with tactical strobes and aerosol powder canisters to coat me! "
            "Pure survival instinct took over—I wrenched a heavy carbon-dioxide fire extinguisher off the wall, "
            "blasted sub-zero white fog across the thermal lens to erase my body heat, and vaulted out the rear garden window!"
        ),
        "cues": [
            "SILENT ALARMS FLASHED RED!\nGUARDS CHARGED WITH POWDER",
            "RIPPED A CO2 EXTINGUISHER\nSTRAIGHT OFF THE WALL",
            "BLASTED SUB-ZERO WHITE FOG\nTO BLIND THE THERMAL LENS",
            "VAULTED OUT THE GARDEN GLASS\nINTO THE MIDNIGHT ALLEY",
        ],
    },
    {
        "shotId": 32,
        "chapterId": 8,
        "slug": "d8_infrared_physics_lesson",
        "sfx": "heartbeat_lubdub",
        "text": (
            "Sprinting six blocks barefoot in the dark taught me the ultimate humbling truth: "
            "you can hide from human eyes, mirrors, and regular lenses—but warm-blooded human thermodynamics never lies. "
            "Someone out there now had forty-five seconds of thermal footage proving an invisible woman existed in New York."
        ),
        "cues": [
            "SPRINTED SIX BLOCKS BAREFOOT\nHEART POUNDING IN MY THROAT",
            "YOU CAN FOOL HUMAN EYES\nAND STANDARD GLASS LENSES",
            "BUT 98.6°F THERMODYNAMICS\nNEVER LIES TO INFRARED",
            "SOMEONE NOW HAD FOOTAGE OF\nAN INVISIBLE WOMAN IN NYC",
        ],
    },

    # ==================== DAY 09 ====================
    {
        "shotId": 33,
        "chapterId": 9,
        "slug": "d9_rooftop_confession",
        "sfx": "glass_shimmer",
        "text": (
            "Day Nine: final twenty-four hours. Wrapped in a dark blanket on an empty SoHo rooftop, watching rain mist over the Empire State, "
            "two voices warred inside my head. Half of me craved putting on warm clothes, ordering coffee, and existing again. "
            "The darker half whispered how boring ordinary rules were going to feel tomorrow."
        ),
        "cues": [
            "DAY NINE · FINAL 24 HOURS\nWRAPPED IN A ROOFTOP BLANKET",
            "HALF OF ME ACHED TO WEAR\nCLOTHES AND BE SEEN AGAIN",
            "THE DARKER HALF WHISPERED:\n'RULES WILL FEEL LIKE A CAGE'",
            "ABSOLUTE UNSEEN FREEDOM\nCHANGES WHO YOU ARE INSIDE",
        ],
    },
    {
        "shotId": 34,
        "chapterId": 9,
        "slug": "d9_sisters_envelope_gift",
        "sfx": "door_click",
        "text": (
            "Before my time ran out, I made one quiet stop that wasn't selfish. I slipped into my little sister Maya's fourth-floor studio "
            "while she slept over nursing textbooks, saw ten worried missed-call alerts with my name on her phone, "
            "and tucked two hundred thousand dollars in clean bills inside her coat with a note: 'Pay off med school. I'm okay.'"
        ),
        "cues": [
            "ONE LAST STOP ON NIGHT NINE—\nNOT FOR REVENGE OR THRILLS",
            "SLIPPED INTO MY SISTER'S\nTINY STUDIO AS SHE SLEPT",
            "SAW TEN WORRIED MISSED CALLS\nWITH MY NAME ON HER SCREEN",
            "LEFT $200,000 IN HER COAT:\n'PAY OFF MED SCHOOL. LOVE YOU.'",
        ],
    },
    {
        "shotId": 35,
        "chapterId": 9,
        "slug": "d9_hand_flicker_glitch",
        "sfx": "camera_alert",
        "text": (
            "Just as my fingers touched her hallway doorknob—zap! Like a dying neon tube, my bare left hand flashed completely solid "
            "for half a second under the porch bulb, then snapped transparent again! "
            "My heart dropped. The refractive field wasn't waiting politely for seven-oh-four AM—it was destabilizing early!"
        ),
        "cues": [
            "AS I TOUCHED HER DOORKNOB—\nMY LEFT HAND FLASHED SOLID!",
            "FLICKERING LIKE A BROKEN\nHOLOGRAM UNDER THE LIGHT",
            "THE 10-DAY ANOMALY WASN'T\nFADING OUT SMOOTHLY",
            "IT WAS DESTABILIZING EARLY—\nAND I WAS MILES FROM HOME!",
        ],
    },
    {
        "shotId": 36,
        "chapterId": 9,
        "slug": "d9_exposure_panic_curve",
        "sfx": "countdown_tick",
        "text": (
            "Imagine the nightmare calculation: I was twenty-eight blocks from my apartment without a stitch of clothing on. "
            "If my invisibility collapsed on a lit avenue or inside a subway car, I'd materialize stark naked on fifty smartphones "
            "and NYPD dashcams at once!"
        ),
        "cues": [
            "THE ULTIMATE NIGHTMARE:\n28 BLOCKS FROM MY APARTMENT",
            "WITHOUT A SINGLE THREAD OF\nCLOTHING ON MY BODY",
            "COLLAPSE EARLY AND I APPEAR\nBARE ON 50 SMARTPHONES",
            "THE RACE AGAINST HOUR 240\nTURNED INTO PURE SURVIVAL",
        ],
    },

    # ==================== DAY 10 ====================
    {
        "shotId": 37,
        "chapterId": 10,
        "slug": "d10_alley_strobe_sprint",
        "sfx": "heartbeat_lubdub",
        "text": (
            "Day Ten—four minutes left! Sticking strictly to dark service alleys and shadowed scaffolding as pale dawn cracked over the East River, "
            "I sprinted barefoot like my life depended on it, my shoulders and legs strobing visible every five steps "
            "as an early-morning dog walker turned the corner!"
        ),
        "cues": [
            "DAY TEN · 00:04:12 LEFT!\nDAWN CRACKING OVER MANHATTAN",
            "SPRINTING BAREFOOT THROUGH\nSHADOWED SERVICE ALLEYS",
            "MY SKIN STROBING VISIBLE\nEVERY FIVE DESPERATE STEPS",
            "DUCKING BEHIND DUMPSTERS AS\nA DOG WALKER TURNED IN!",
        ],
    },
    {
        "shotId": 38,
        "chapterId": 10,
        "slug": "d10_final_ten_seconds",
        "sfx": "countdown_tick",
        "text": (
            "Up the fire escape, through my unlocked bedroom window with nineteen seconds on the clock! "
            "I stumbled into the bathroom, snatched my crimson silk robe off the tile floor, and gripped the sink edge "
            "as the glowing numbers on the glass ticked: three... two... one... zero."
        ),
        "cues": [
            "UP MY FIRE ESCAPE WINDOW\nWITH 19 SECONDS TO SPARE!",
            "SNATCHED MY SILK ROBE OFF\nTHE COLD BATHROOM TILE",
            "GRIPPED THE SINK WATCHING\n03... 02... 01... ZERO",
            "A WARM STATIC WAVE WASHED\nFROM MY TOES TO MY LIPS",
        ],
    },
    {
        "shotId": 39,
        "chapterId": 10,
        "slug": "d10_reflection_returns",
        "sfx": "glass_shimmer",
        "text": (
            "I exhaled—and looked up. Staring back from the mirror were my own wide hazel eyes, tousled hair, and flushed cheeks. "
            "I touched my own face and laughed out loud just to see my lips move. "
            "Ten days unseen left me a millionaire, cured me of fake friends forever, and showed me human nature naked."
        ),
        "cues": [
            "I LOOKED UP—AND MY OWN\nEYES STARED BACK AT ME",
            "FLUSHED CHEEKS · MESSY HAIR\nSOLID FLESH ONCE AGAIN",
            "RICHER BY A MILLION DOLLARS\nFREE OF EVERY FAKE FRIEND",
            "AND FOREVER HAUNTED BY WHO\nPEOPLE ARE IN THE DARK",
        ],
    },
    {
        "shotId": 40,
        "chapterId": 10,
        "slug": "d10_encrypted_text_cliffhanger",
        "sfx": "camera_alert",
        "text": (
            "At least, I thought it was over. That evening, dressed in black leather by my window, my phone buzzed with an unknown encrypted video: "
            "the thermal clip from Day Eight—followed by one message: 'Want ten more days? This time, save lives.' "
            "Subscribe for Part Two: the Superhero Edition—and tell me honestly below, what would you do on Day One?"
        ),
        "cues": [
            "THAT NIGHT MY PHONE BUZZED\nWITH AN ENCRYPTED VIDEO:",
            "THE THERMAL CLIP FROM DAY 8—\n'WANT TEN MORE DAYS?'",
            "'NEXT TIME, USE IT AS A HERO.'\nPART 2 COMING NEXT!",
            "BE HONEST IN THE COMMENTS:\nWHAT WOULD YOU DO ON DAY 1?",
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


def build_invisible_sfx_kit(rng: np.random.Generator) -> dict[str, np.ndarray]:
    kit: dict[str, np.ndarray] = {}

    # 1. Velvet Sub Chapter Boom + Shimmer Tail
    t_b = np.linspace(0, 1.75, int(1.75 * SR), dtype=np.float32)
    freq_b = 74.0 * np.exp(-t_b * 2.3) + 31.0
    boom = np.sin(2 * np.pi * np.cumsum(freq_b) / SR) * np.exp(-t_b * 2.5) * 0.62
    air_chime = np.sin(2 * np.pi * 587.33 * t_b) * np.exp(-t_b * 3.8) * 0.11
    kit["chapter_boom"] = (boom + air_chime).astype(np.float32)

    # 2. Silky Transition Whoosh
    t_w = np.linspace(0, 0.32, int(0.32 * SR), dtype=np.float32)
    env_w = np.maximum(0.0, np.sin(np.pi * (t_w / 0.32))) ** 1.8
    kit["whoosh"] = (lowpass_noise(rng, len(t_w), taps=18) * env_w * 0.20).astype(np.float32)

    # 3. Crystalline Glass-Phantom Shimmer Chime
    t_s = np.linspace(0, 1.35, int(1.35 * SR), dtype=np.float32)
    shimmer = (
        np.sin(2 * np.pi * 1174.66 * t_s) * 0.14
        + np.sin(2 * np.pi * 1479.98 * t_s) * 0.11
        + np.sin(2 * np.pi * 2217.46 * t_s) * 0.07
    ) * np.exp(-t_s * 3.1)
    kit["glass_shimmer"] = shimmer.astype(np.float32)

    # 4. Intimate Adrenaline Lub-Dub Heartbeat (2 beats)
    n_hb = int(1.25 * SR)
    hb = np.zeros(n_hb, dtype=np.float32)
    for off_s, amp in [(0.02, 0.52), (0.24, 0.38), (0.66, 0.50), (0.88, 0.36)]:
        p0 = int(off_s * SR)
        th = np.linspace(0, 0.16, int(0.16 * SR), dtype=np.float32)
        thump = np.sin(2 * np.pi * (58.0 * np.exp(-th * 8.0) + 32.0) * th) * np.exp(-th * 18.0) * amp
        hb[p0 : p0 + len(thump)] += thump
    kit["heartbeat_lubdub"] = hb

    # 5. Shower / Sauna / CO2 Steam Hiss
    t_st = np.linspace(0, 1.45, int(1.45 * SR), dtype=np.float32)
    env_st = np.maximum(0.0, np.sin(np.pi * (t_st / 1.45))) ** 1.3
    kit["steam_hiss"] = (lowpass_noise(rng, len(t_st), taps=8) * env_st * 0.22).astype(np.float32)

    # 6. Subtle Door Latch Click
    t_dc = np.linspace(0, 0.22, int(0.22 * SR), dtype=np.float32)
    click = (
        np.sin(2 * np.pi * 210.0 * t_dc) * np.exp(-t_dc * 34.0) * 0.42
        + lowpass_noise(rng, len(t_dc), taps=6) * np.exp(-t_dc * 55.0) * 0.28
    )
    kit["door_click"] = click.astype(np.float32)

    # 7. Crystal Champagne Flute Clink
    t_cc = np.linspace(0, 0.85, int(0.85 * SR), dtype=np.float32)
    clink = (
        np.sin(2 * np.pi * 2637.0 * t_cc) * np.exp(-t_cc * 6.5) * 0.16
        + np.sin(2 * np.pi * 3951.0 * t_cc) * np.exp(-t_cc * 9.0) * 0.09
    )
    kit["champagne_clink"] = clink.astype(np.float32)

    # 8. FLIR Thermal Lock-On Double Alert Beep
    n_al = int(0.75 * SR)
    al = np.zeros(n_al, dtype=np.float32)
    for b_off in [0.02, 0.22]:
        p0 = int(b_off * SR)
        tb = np.linspace(0, 0.12, int(0.12 * SR), dtype=np.float32)
        beep = np.tanh(np.sin(2 * np.pi * 1320.0 * tb) * 1.6) * np.exp(-tb * 14.0) * 0.24
        al[p0 : p0 + len(beep)] += beep
    kit["camera_alert"] = al

    # 9. Tense Countdown Clock Tick (3 ticks)
    n_tk = int(1.1 * SR)
    tk = np.zeros(n_tk, dtype=np.float32)
    for k_off in [0.02, 0.42, 0.82]:
        p0 = int(k_off * SR)
        tt = np.linspace(0, 0.05, int(0.05 * SR), dtype=np.float32)
        tick = np.sin(2 * np.pi * 1680.0 * tt) * np.exp(-tt * 85.0) * 0.22
        tk[p0 : p0 + len(tick)] += tick
    kit["countdown_tick"] = tk

    return kit


def synthesize_velvet_noir_score(total_sec: float, rng: np.random.Generator) -> np.ndarray:
    """Hypnotic Euphoria / Dark R&B Neon-Noir synth pad + sensual sub-pulse (72 -> 86 BPM)."""
    n_total = int(np.ceil(total_sec * SR)) + SR
    bed = np.zeros((n_total, 2), dtype=np.float32)

    # Lush nocturnal minor-9th / maj7 chord roots & warm fifths/thirds (F#m -> Dmaj7 -> Bm -> C#sus -> E -> C#m)
    chords = [
        (92.50, 138.59, 185.00, 220.00),   # F#m
        (73.42, 110.00, 146.83, 185.00),   # Dmaj7
        (61.74, 92.50, 123.47, 146.83),    # Bm7
        (69.30, 103.83, 138.59, 164.81),   # C#7sus
        (92.50, 138.59, 164.81, 207.65),   # F#m7
        (82.41, 123.47, 164.81, 207.65),   # Emaj7
        (73.42, 110.00, 146.83, 185.00),   # Dmaj7
        (69.30, 110.00, 138.59, 174.61),   # C#alt
    ]

    block_len = int(12.0 * SR)
    num_blocks = int(np.ceil(n_total / block_len))

    for b in range(num_blocks):
        i0 = b * block_len
        i1 = min(n_total, (b + 1) * block_len)
        m = i1 - i0
        t = np.arange(m, dtype=np.float32) / SR
        f1, f2, f3, f4 = chords[b % len(chords)]

        # Silky stereo chorus LFO
        lfo_l = 0.74 + 0.26 * np.sin(2 * np.pi * 0.11 * t)
        lfo_r = 0.74 + 0.26 * np.cos(2 * np.pi * 0.11 * t)

        left = (
            np.sin(2 * np.pi * f1 * t) * 0.082
            + np.sin(2 * np.pi * (f2 * 1.003) * t) * 0.048
            + np.sin(2 * np.pi * f3 * t) * 0.032
            + np.sin(2 * np.pi * (f4 * 0.998) * t) * 0.022
        ) * lfo_l
        right = (
            np.sin(2 * np.pi * (f1 * 0.999) * t) * 0.082
            + np.sin(2 * np.pi * f2 * t) * 0.048
            + np.sin(2 * np.pi * (f3 * 1.004) * t) * 0.032
            + np.sin(2 * np.pi * f4 * t) * 0.022
        ) * lfo_r

        # Sensual nocturnal sub-bass heartbeat groove (72 -> 86 BPM across the 10 days)
        bpm = 72.0 + 14.0 * (b / max(1, num_blocks - 1))
        p_phase = (t * (bpm / 60.0)) % 1.0
        pulse = (
            np.sin(2 * np.pi * 50.0 * (p_phase / 1.12))
            * np.minimum(1.0, p_phase * 28.0)
            * np.exp(-p_phase * 9.2)
            * 0.082
        )

        velvet_air_l = lowpass_noise(rng, m, taps=30) * 0.011
        velvet_air_r = lowpass_noise(rng, m, taps=30) * 0.011

        bed[i0:i1, 0] = left + pulse + velvet_air_l
        bed[i0:i1, 1] = right + pulse + velvet_air_r

    fi_n = min(n_total, int(0.8 * SR))
    fo_n = min(n_total, int(1.8 * SR))
    bed[:fi_n, :] *= np.linspace(0.0, 1.0, fi_n, dtype=np.float32)[:, None]
    bed[-fo_n:, :] *= np.linspace(1.0, 0.0, fo_n, dtype=np.float32)[:, None]
    return bed


async def main():
    print("[Invisible 10Days NSFW] Synthesizing 40 female-POV shots with Edge-TTS (en-US-AvaNeural)...")
    sem = asyncio.Semaphore(4)
    tasks = [synth_shot(shot, sem) for shot in SHOT_SCRIPT]
    shot_results = await asyncio.gather(*tasks)
    shot_results.sort(key=lambda r: r["shot"]["shotId"])

    raw_vo_sum = sum(r["durationSec"] for r in shot_results)
    min_target_sec = 625.0  # Guarantees 10m 25s+ for YouTube mid-roll & long-form watch time!
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
    print(f"[Invisible 10Days NSFW] Master Duration: {mins:02d}:{secs:05.2f} ({total_sec:.2f}s / {total_frames} frames @ {FPS}fps)")

    rng = np.random.default_rng(20261010)
    sfx = build_invisible_sfx_kit(rng)
    bed = synthesize_velvet_noir_score(total_sec, rng)
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
            duck[d0:d1] = np.minimum(duck[d0:d1], 0.36)

    smooth_k = np.ones(int(0.05 * SR), dtype=np.float32) / int(0.05 * SR)
    duck_s = np.convolve(duck, smooth_k, mode="same")
    bed[:, 0] *= duck_s
    bed[:, 1] *= duck_s

    sfx_events: list[tuple[float, str, float]] = []
    for i, st in enumerate(shots_timeline):
        cut_s = st["startFrame"] / FPS
        if st["isChapterStart"]:
            sfx_events.append((cut_s + 0.04, "chapter_boom", 0.70))
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
    wav_master = STUDIO_DIR / "out" / "invisible_nsfw_tmp.wav"
    pcm16 = np.clip(np.round(mix * 32767.0), -32768, 32767).astype(np.int16)
    with wave.open(str(wav_master), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

    print("[Invisible 10Days NSFW] Normalizing master broadcast audio (-16 LUFS)...")
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
    ts_content = f"""// Auto-generated by scripts/build_invisible_10days_nsfw_audio.py
import type {{ CaptionCue }} from "../ifnoir/alcatrazPilotTimeline";
import type {{ Docu10MinShotTiming, DocuChapterTiming }} from "../ifnoir/alcatraz10MinTimeline";

export const INVISIBLE_NSFW_FPS = {FPS};
export const INVISIBLE_NSFW_TOTAL_FRAMES = {total_frames};
export const INVISIBLE_NSFW_DURATION_SEC = {round(total_sec, 3)};

export const INVISIBLE_NSFW_CHAPTERS: readonly DocuChapterTiming[] = {json.dumps(chapters_timeline, indent=2)} as const;

export const INVISIBLE_NSFW_SHOTS: readonly Docu10MinShotTiming[] = {json.dumps(shots_export, indent=2)} as const;

export const INVISIBLE_NSFW_CUES: readonly CaptionCue[] = {json.dumps(all_cues, indent=2)} as const;
"""
    OUT_TIMELINE.write_text(ts_content, encoding="utf-8")
    print(f"[Invisible 10Days NSFW] Done! Saved {OUT_AUDIO.name} & {OUT_TIMELINE.name} ({len(all_cues)} cues).")


if __name__ == "__main__":
    asyncio.run(main())
