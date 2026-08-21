# DOOM Bible

by Tom Hall

Revision Number 0.2
Date: 11/28/92

*A production of The Tom Hall Press, Inc. All rights reserved.*

*This is the original DOOM design document — the 1992 design bible by Tom
Hall (id Software), digitized from the Internet Archive (OCR). Added to the
classroom corpus as a curated teaching source: a masterclass in worldbuilding,
systems design, and writing a game that people remember.*

---

## Table of Contents

- Game Specs Section
  - Doom Command Line Parameters — 1
  - Intro and Demo Loop — 2
  - Control Panel — 3
  - Play Loop — 4
  - End of game — 5
- Game Info
  - Characters — 6
  - Episode 1 — 7 (Story 7.1, Actors 7.2, Unique Bits 7.3, Maps 7.4)
  - Episode 2 — 8
  - Episode 3 — 9
  - Episode 4 — 10
  - Episode 5 — 11
  - Episode 6 — 12
  - Commercial — 13
  - Stuff: Weapons, Items, Etc. — 14
  - DOOM Press release — 15
  - Random Notes — 16
  - DOOM Calendar — 17
- Appendices
  - Glossary — A
  - File Extensions — B
  - Utilities — C
  - Random Extremely Important Info Too Small to Rate Having its Own Section — D
  - Known and Unfixed Bugs — E

---

## Section 1 — DOOM Command Line Parameters

You can run Doom with the following parameters:

- DOOM /bugs — All debug keys enabled
- DOOM /mem — Show mem readout in scope or report window
- DOOM /EPISODE=x — Run episode number x (must have /bugs)
- DOOM /LEVEL=x — Run absolute level x (must have /bugs)
- DOOM /END=x — Go to end cinematic of episode x
- DOOM /lothar — Run Ep 1, Level 1 in god mode w/ ∞ shots
- DOOM /backdoor — Skip copy protection on commercial
- DOOM /instore — Runs demo loop until turned off
- DOOM /follow — Routine names printed in readout window
- DOOM /diagnostic — Upper two windows show diagnostic info
- DOOM /bubbles — Replace all actors with naked women
- DOOM /prude — Cancels effects of bubbles parameters
- DOOM /drunk — Occasionally invokes the bubbles mode

## Section 2 — Intro and Demo Loop

Demo Loop: Title and Credits; Demon face and credits; Cinematic; Demo; High Scores.

## Section 3 — Control Panel

Work on clever, integral menu. Choice of trainer (commercial only, has own WAD).

## Section 4 — Play Loop

New 3-D engine.

## Section 5 — End of Game

Each game can end three ways: User Abort, player death with no lives left, and player victory. Each is covered here.

- END OF GAME: USER ABORT — the guy dies in maze and control panel appears.
- END OF GAME: DEATH — pull back to see self die, view remains in maze. Window over view of dead guy — choice to continue. If you don't, Control Panel over view.
- END OF GAME: WIN — cinematic, similar for all characters, showing how the player's character reacts — in one of two small face reaction shots plus individual text.

## Section 6 — Characters

These are the four characters in Doom:

**Lorelei Chen** — Age: 27, Weight: 151, Height: 5'10". Muscular, tall woman, attractive, but with strangely too-intense eyes. Oriental featured in the brown eyes and black hair, drawn back into a large knot. Scar on left shoulder from rock-climbing accident. Fiercely competitive, Lorelei intimidates most people. She won her troop boxing championship. Lost a bet that meant she had to pull her application for a glory post. Married for six months once; husband divorced her for irreconcilable differences. From European Alliance. No one calls her Lorelei. Advantages: Fast. Crack shot with pistol. Disadvantages: Once wounded, she still tends to push herself to compensate, so wounds can keep ticking off more. Not used to bayonet.

**John "Petro" Pietrovich** — Age: 34, Weight: 190, Height: 5'9". Black balding man with thick eyebrows. Missing last joint of right ring finger. Brown eyes. Former head of security at AWR (Advanced Weapons Research) Labs; grew tired of the overwhelming bureaucracy of the UAAF. His insubordination cost him his rank; his assignment on Tei Tenga was his request, made to get away from the epicenter of annoyance while finishing his term of duty. Advantages: Good with standard shell weapons. Can take damage. Disadvantages: Average speed. Not used to missile weapons.

**Dimitri Paramo** — Age: 37, Weight: 191, Height: 5'11". Bulky, slightly overweight Greek-Spaniard with swarthy but unkempt looks. Frizzly dark brown hair. Basically stuck in the low ranks of the military, but that suits him just fine. He wants nothing more from life: give him a clear objective and the chance to release aggression through the freely available high-powered firearms, and he's happy. Advantages: Very good with all weapons. Can take a lot of damage. Disadvantages: Slow.

**Thi Barrett** — Age: 22, Weight: 130, Height: 5'6". Red-haired and trim, Thi (pronounced "Tee") has piercing blue eyes, and is stout but gorgeous. Father was a sergeant in the UAAF; gave Thi a strong sense of duty and honor. Medalist in unarmed combat. She volunteered for this post because no one wanted it. Advantages: Faster than average. Hard to hit. Does incredible damage with bayonet. Disadvantages: Low hit points.

And of course, there's... **Buddy Dacote: the guy that dies** — Age: 29, Weight: 202, Height: 6'2". Very fit and powerful; always wears a hat that says "BEOS" which stands for "Butt End of Space." Popular and courageous; got sent to Tei Tenga Darkside for showing up a superior officer. Inside info: Dacote stands for "Dies at conclusion of this episode."

Other names: Roland Trague, Warren Apisa, Taradina Cassatt, Melanie "Butch" Bucelli, Janella Sabando.

## Section 7 — Episode One

This must be kept small and powerful. It is limited to a 700K download size.

### 7.1 Story — Episode One: "Evil Unleashed" or "All Hell Breaks Loose"

You are a soldier in the UAAF (United Aerospace Armed Forces) assigned to the secondary military research base on the darkside of the giant moon Tei Tenga (nicknamed "the Butt End of Space"). You and four friends are having a game of cards in the hangar bay. One of your friends leaves to go on shift.

Meanwhile, the research team are doing experiments at the anomalies found on the moon. There is a flash of horrible light and energy and two gates open at equidistant points on the moon's surface, the larger of the two at the lightside. Every awake is quickly killed. One reaching for the alarm button has his hand chopped off. Briefly your friend is grabbed, his hat falling off in the lab. Then they spread out through the airducts and possessing sleeping people with magic.

A short while later, a strange alien creature bursts into the room. ("What the hell?") A fight ensues. Whoever's left in your squad investigates the base, where a dark tale begins to unfold. A bunch of small hostile alien creatures have invaded the base. Strange symbols are drawn everywhere in the blood of dead soldiers and scientists. The more you go forward, the stranger and grosser the walls become. On your way, you find your friend's cap.

After you make it to the control lab, you find a gate to another place in the wreckage of what was a containment chamber. On the other side, you find two huge beasts in a circular natural rock canyon and the remains of the lab team. Between the beasts is your friend and they quarter him. You defeat the beasts, turn to leave, only to find the hole closing! You're trapped here! You climb the rock walls, and look at your surroundings from the top of this extinct volcano: "Oh, hell..."

### 7.2 Actors — Episode One

- **Other players** — suits of different colors; other color changes reflect different weapons.
- **Demon-Possessed Humans** — possessed in their sleep; uniforms palette-changed to reflect different behavior.
- **Flying Imps** — annoying little bastards, in different flavors, with later ones firing spikes and fire.
- **Demon Troops** — a lot of damage up close; later Troops cast magic.
- **Demon Sergeants** — a lot more damage up close; later sergeants cast floor-boiling magic.
- **Bruiser Brothers** — twin terrors at the end of episode one.

### 7.3 Unique Bits

The bases on the planet Tei Tenga used to be the glory posts, but lack of progress with the research has caused money to be funneled away. The two bases are Lightside and Darkside: the planet does not rotate, so there is no day or night. The anomalies being studied are on the planet's magnetic poles.

**Intro Cinematic**: View from space of planet (ballmapped); military research base, moon Tei Tenga (rotates); zoom into room with live guys playing cards. Dacote: "I'm out. I gotta go on duty anyway. See you guys." Petro: "Pay-up or die, Buddy." ... The hand reaching for the alarm is chopped off. Buddy looks back and forth in strobe, sees a demon claw behind him. Credits roll over demon face.

**End Cinematic**: the dead twin demons; cut to close-up of player atop the cliff: "Oh, hell..." Short credit-like roll hyping Doom 2 over a scary demon lord's face; big word "Doom" appears masked over it. Fade to black. Go to high scores, then Demo Loop.

**Solution**: Go through Depot 2, Mess to Officers' Quarters. Get a Colonel's Hand. Use the Colonel's Hand to get into the control center. Get through Power Plant maze and trip the breakers. Power turns on. Use the Colonel's hand to gain access to the Lab (through monorail system, which is dangerous, or through main lab entrance). Fight your way through the lab to the Anomaly passage, using the Colonel's Hand. Go down there, and kick some twin demon butt.

### 7.3.1 DOOM Buildings and Areas

Every area should have interesting stuff to go and explore, if not vital stuff to obtain. Otherwise, why is it there? Why isn't something cool there instead?

**Styles**: Old (pre-... pressurized buildings, shabby, Jabba places in Star Wars, Aliens); UAC (bright shiny, high-tech buildings by StarStruct, Inc. — 2001 and Star Wars' Imperial stuff); Mine (shabby, old, sturdy supports in an energy-carved mine, gray/red/brown granites); Demonic (demons have made this place home — art deco darkness with tortured souls).

**Buildings described in detail**: Hangar Two (secondary hangar, cards room, storage), Basement (large storage area, toilet with a peeing easter egg, elevator with "Please do not loiter on the elevator" voice), Supply Depot Two (monorail switcher, storekeeper's office), Waste Processing Facility (splits waste into water, nutrients for the lab's gardens, solid fuel), Enlisted Quarters (murphy beds, showers, tons of possessed humans, massacre in the shower), Tower (communications tower, dangerous tech for service robots only), Recreation and Training Center (chapel/theater with hourly sermons of different religions, enlisted club with video games, officers' club requiring the Colonel's Hand, shooting range where shooting makes demons come out, therapist hot tubs, simulator), Mess (kitchens, freezer with frozen guys who froze to death hiding, laundry with huge demon/human melee), Officers' Quarters (nicer, massacre with hands impaled on a pike under a light — these are the Colonels' Hands), Personal Storage (cheesecake calendars, the sawed-off shotgun), Control Center/Power Plant (the gateway to the restricted side), Lab (Fire Dust study, experiments best carried out away from the mainstream, gardens both hydroponic and terraformed), Observatory (nasty demons and lots of treasure), Supply Depot One (main supply depot, big crate maze), Anomaly (the cave of Tei Tenga where Fire Dust was first found, the gate and the hell canyon, the two Bruiser Brothers), Main Hangar.

### 7.3.2 DOOM Object Graphics

Lists all things to be drawn: Screens/Pix (title screen, credits, moon surface, four players playing cards, close-ups of eyes, hell skyline); Weapons (knife, machine pistol, officer's pistol, shotgun, sawed-off shotgun, automatic machine gun, missile launcher, ammo clips); Gettable Items (stim-pack, medikit, blood receptacle, dagger, chi gem, unholy bible, soul sphere, infrared scanner, sonar, three levels of armor, four shield packs, the lacerated bloody hand); Object Sprites (Rollee chairs, storage canister that collapses revealing contents, crane, dangling wires, electrical zapper); Animations (smoke and crate chunks, beefy chunklets off missile-exploded enemies, shield hit, gate, spinning black demon head); Patches (demon hieroglyphics, wall damage, bloodstains, bloody handprints, switches, hand access pads, nudie calendar on wall); Extruded Shapes (storage crates, bathroom, desks, control consoles, NeXTs, beds, washers/dryers); Floors, Ceilings, Walls (UAC metal walls with big UAAF logo, monorail tunnel walls, throbbing power core-type walls, mine concrete walls, moon canyon walls, starry sky, hell canyon walls); Doors (double door ten feet wide, three-feet wide, two-feet wide, elevator split doors, toilet swinging doors); Actors and Related Sprites (player, possessed human, massacred humans, pile of hands with pike through the center, imp, demon 1, demon 2, boss).

### 7.3.3 DOOM Sounds

Knife swipe/hit, pistol shot, shotgun blast, automatic machine gun burp, missile launch, bullet hits wall/metal/glass, item blows up, shot hits monster, door open/close, elevator at floor, switch flip, walking on gravel, player hit, Rollee chair rolling, warning klaxon, demon roars, big demon hooves walking, demon dies, guy dies, the sound of Buddy being ripped in two, elevator hum. Speech (the NeXT lady): "Access Denied — Officers and Essential Personnel Only", "Access Granted", "You are here.", "Power Failure. Please send a maintenance supervisor to the power plant.", "Danger — This area is unsafe.", "Warning: radiation leak. Please call HM team.", "Second Floor", "Ground Floor", "Basement".

### 7.4 Maps

Level One: Secondary Hangar — start of level, two Dehuman, Demon troop, Switch, Demon troop, Shotgun.

## Section 8 — Episode Two

### 8.1 Story — "Lost in Hell" or "To Hell and Back"

You explore. In the distance you see a great dark edifice. You must make your way there and try to find a way to escape. You fight your way through many aliens. Once you reach the edifice, you find a gate guarded by a forcefield. You lead a big boss guy there and shoot him, buffeting him backward into the beam, destroying it. You go through the door and get to the gate. You storm through and make it back to your own universe, only to find you're back on Tei Tenga, and the demonic aliens have taken over the lightside base.

## Section 9 — Episode Three

### 9.1 Story — "Knee-deep in the Dead"

All-out war ensues. You battle your way toward the hangar. Once there, you take off in an old attack cruiser. You get powerful readings from the gate area and decide to bomb the gate. You do, and both gates flash and break up. Then earthquakes begin. Lava spouts erupt all over. The moon turns into a ruined, fiery ball as you speed off toward the nearest civilized outpost.

## Section 10 — Episode Four

### 10.1 Story — "Armed Assault"

Your team is in jail for destroying the planet: the officials denied tampering with the forces. You've been promised release as soon as it blows over. Then they recruit you to explore another gate that the military has opened on the small moon. The squads they've sent in have lost to the forces there. Demons from the gate have stolen a new weapon and you've got to get it back. Once there, you travel hell and find the weapon... and it's attached to a huge techno-demon. You defeat him and cut the weapon off, and find its energy systems non-functional. You go outside and head for the gate. When you return to the moon, the entire base is covered with grotesque demonic goo.

## Section 11 — Episode Five

### 11.1 Story — "Base Instinct"

You fight for control of the base. At the end you want to get to the ship and get the weapon back. In your way is some awful demon deal which you have to be clever to defeat. You are ready to take off, but decide to do something more permanent. You put a warhead on a troop carrier with a delayed detonation, and send it through the gate. It blows and nukes a good bit of Hell. The big General Demon shakes his head and touches his strange-shaped tactical board, changing that area to the color of our dimension.

## Section 12 — Episode Six

### 12.1 Story — "The Final Gate"

You get back and ask the military if there are any more of these holes. They say, well, one more, but it is too small to be significant. You ask to check it out, and want to go in prepared, just in case. You hit the planet, your pilot is killed by a demon. You battle strange new demons, and in the end meet the General Demon, who totally slaughters you if you try to attack him. You can find a secret way to get behind him and blow up his machine. You run out and the "cavalry" has arrived. You take off as you order them to nuke the gate and the planet. We see the General Demon angry as the radiation blast flies past him, bathed in its light, threatening to awaken the ancient ones.

## Section 13 — Commercial Game

### 13.1 Story — "Chaos Awake"

At the start of the game, we see our team on a reunion vacation. Meanwhile the General Demon is awaking the ancient demons. Back on Earth, they see the horizon change color. Switch to the General arriving with floods of demons, telling his children to go play. As the world is fighting them, you are sent as a strike team. You fight your way to the demon's palace and confront him; he announces his plans and throws you in a cage to watch the destruction. The player must shoot a machine nearby which explodes and knocks the cage from its perch. The General Demon's gate opening machine is there. You can see a gauge which he demonstrated how he can play with the aperture with a giant control atop the machine, but he only messed with it in one direction. There is a gap in the machine which sparks intermittently. If you shoot a projectile into the gap, it sparks constantly and the readout starts moving to the inverse side, the General goes "What?" as the gate closes and the dimension starts bending inward. The Ancients are sucked into the machine, and the General is sucked in after trying to fire magic at it, all with horrible gibletty mess. The dimension is pulled into the machine. Once it touches the machine, the machine starts to blow. Briefly, you see the aperture gauge opening again, then there is a flash. On Earth, where the gate was, we see a big gibletty squirt from the gate which flashes from existence. After a long pause, we see the team break the surface, covered with gibs. They look at each other and say something incredibly funny. At the last, we see them horribly be-medalled, then back on vacation. See flash on horizon, they look at each other, then rain starts falling. They laugh. The end.

## Section 14 — Stuff: Weapons, Items, Etc.

### 14.1 Weapons

- **Knife** (gray) — attachment to the machine pistol. Minimum damage, more on back attack.
- **Machine Pistol** (violet) — one shot at a time, knife attachment for close combat.
- **Shotgun** (blue) — one shot at a time, much more powerful, wider target range, heavy recoil.
- **Automatic machine gun** (green) — multiple shots of pistol-level damage.
- **Missile launcher** (yellow) — very damaging missiles, large recoil.
- Episode 2: **Dark Claw** (black) — demon weapon that casts a dark cloud of tortured essence.
- Episode 3: **Probiectile** (orange) — minimal damage, gives readout on enemy.
- Doom 4-6: **Spray rifle** (brown) — multiple shots in a 60° arc; **BFG 2704** (red) — "Big Fucking Gun," horrible hallway-scouring weapon.
- Commercial: **Unmaker** (white) — demon-tech weapon that hurts pure demons a lot, demon-humans very little, made of demon bones.

Ammo: Bullets (pistol, shotgun, machine gun, spray rifle), Cells (plasma gun, BFG), Grenades, Missiles, Killed humans (the Dark Claw and Unmaker feed on human souls).

### 14.2 Useful Items

Healing: **Stim-Pack** (small boost), **Medikit** (good bonus), **Soul Sphere** (the life energy of a human soul — a 1-Up).
Treasure: **Blood Receptacle** (gold bowl used in sacrifices), **Dagger** (black and red, used in sacrifices), **Chi Gem** (drops from true demons once they die; colors denote aura magnitude; a pun — "Chi" is pronounced "key"), **Unholy Bible** (found only in Hell, a tome of great evil).
Powerups: **AutoMap**, **Infrared Scanner** (see enemies through walls), **Sonar** (see all exits); Armor: Duty, Guard, Battle, **Demon armor** (takes all damage but a bit of health leaves at every hit); Energy shields: Beam, Disruptor, Deflector, **Ban shield** (prevents all solid weapons from hitting); Other: **Shockshield**, **Shadow Cloak**, **Chaos Field** (makes monsters nearby fight each other).

### 14.3 Interesting Items

Episodes 2-6 and the commercial game will have items that fill out the story: memos, notes, clothes, signs of inhabitance, junk, familiar but damaged items.

## Section 15 — DOOM Press Release

### 15.1 Blurb

DOOM (Requires 386sx, VGA, 2 Meg) — It's a real-time, three-dimensional, 256-color, fully texture-mapped, multi-player battle from the safe shores of our universe into the horrifying depths of the netherworld! Choose one of four characters and you're off to war with hideous hellish hulks bent on chaos and death! See your friends bite it! Cause your friends to bite it! Bite it yourself! And if you won't bite it, there are plenty of demonic denizens to bite it for you!

DOOM — where the sanest place is behind a trigger.

### 15.2 General Press Release

Coming in 1993: DOOM. You are one of four off-duty soldiers suddenly thrown into the middle of an interdimensional war. Program features: fully texture-mapped walls, floors, and ceilings; light diminishing and light sourcing; 256-color VGA graphics; status readouts in your helmet; tons of powerups and wicked weapons; a seamless world, inside and outside; movie-like cinematic sequences; four players at once on LANs, two by modem; six exciting episodes of violent mayhem.

Produced by id Software, creators of Wolfenstein 3-D. Requires a 386sx PC compatible or better; VGA graphics; 2 Megabytes of memory.

John Carmack, id's Technical Director: "Wolfenstein is primitive compared to DOOM. We're doing DOOM the right way this time. The game runs fine on a 386sx, and on a 486/33, we're talking 35 frames per second, fully texture-mapped at normal detail, for a large area of the screen. That's the fastest texture-mapping around — period."

An Overview of DOOM Features: Texture-mapped environment; non-orthogonal walls (any angle, any thickness, see-through areas); light diminishing/light sourcing; variable height floors and ceilings; environment animation and morphing (walls can move, ceilings can crush you); palette translation (monsters of many colors, infrared sensors); multiple players (LAN + modem); smooth, seamless gameplay (everything actual size, high frame rate, immersion).

Shareware distributor: Apogee Software. Commercial distributor: FormGen, Inc. DOOM, Id, and Wolfenstein are trademarks of id Software, Inc.

## Section 16 — Random Notes

Marketing ideas: "Welcome to Tei Tenga Base" or "Join the UAF" fliers. Military type caps: DOOM, BEOS, UAF. Uniforms for shows. Rate it "PR" for "Parental Restriction."

## Appendix A — Glossary

- **Aardwolf** — a maned striped mammal (Proteles cristatus) of southern and eastern Africa that resembles the related hyenas and feeds chiefly on carrion and insects. The aardwolf has sort of become the mascot of id.
- **And** — logical operation that evaluates to true only if both operators are true. So if Tom and John are in the office, it is true that no work gets done.
- **Blit** — in general, stuff data somewhere, but usually means draw to screen. Often implies as fast as possible.
- **Deice** — Alfonso's utility to shab together and decompress a file that has been Ice-d onto a bunch of disks.
- **DeltaFrac** — cool people know what this means.
- **DoomEd** — Tom's name for the Doom Map Editor.
- **Exclusive-Or** — logical operation that evaluates to true only if only one or the other of the operators are true. So if either Tom or John are in the office — but not both of them — it is true that someone may be masturbating in the office bathroom.
- **Hag Spot** — location of the oldest member of id. Related to the "Tag Spot" and the "Shag Spot."
- **Ice** — John Romero's dandy Installation Creation Editor.
- **IGrab** — you grab, we all grab with IGrab. Seventeen projects later, IGrab lies with four stakes and ten silver bullets in its heart.
- **Lumpy** — at 2:03am, Oct 20, 1992, we were trying to think of a new name for SGrab, our VGA graphic grabber. Romero said "Lumpy," and it was love.
- **Muse** — torture in the form of an executable.
- **Pneumonoultramicroscopicsilicovolcanoconiosis** — the longest word in the English language. It means "Black lung," the disease miners get from inhaling coal dust.
- **SpeedView** — view a text file, examine it as hex, search for keywords, view multiple files.
- **Ted** — the Tilemap EDitor, laid to rest in 1992, after five resurrections. Ted was used in an amazing fifteen id projects. "Ted is like an old friend that passed away... Ted popped my id development tool cherry."
- **WAD** — composite data file. Means "Where's All the Data?"

## Appendix B — File Extensions

- .DMx — File for Doom Episode x
- .LMP — Individual Lump file
- .LSC — Script file for Lumpy the grabber
- .WAD — Composite datafile made of lumps
- .WLK — Link script used by WadLink

## Appendix C — Utilities

**Lumpy** — grabs and links together lumps of related graphics. Script invocation: `lumpy [-s] [-p] filename`. Grab commands: RAW, PALETTE, PIC, LPIC, FONT, PATCH, PATCH255.

**WadLink** — links together lumps from Lumpy and WADs previously "wadded up" by WadLink. Invocation: `wadlink [-b] [-source path] [-dest path] [-script file]`. Script commands: $OUTNAME, $OPENWAD, $CLOSEWAD, $LABEL.

**DoomEd** — edits maps used with the Doom engine. Based on the NeXT demo "Draw."

**Other Command Line Utilities**: SpitWad (spits out information contained in a WAD to text screen), ViewDo (takes the Doom viewscreen and finds the exact boundaries). Names for a utility John never wrote: Checurve, RuleView, Raterra, CurveCop, Anglathe, OhTopos, SeeSlope, Scangle, Scanc, Testcurv, Contrace, Slopehed, Curvalid, Polisher, Lathe, Sculptor, Slopeval, Topolish.

**Fuzzy Pumper Palette Shop** — convert captured video images and other NeXT-generated images into VGA format.

**Scripto** — generates grab scripts for use with Lumpy.

## Appendix D — Random Extremely Important Info Too Small to Rate Having its Own Section

Sandwich Hall hours, Pizza Hut hours, deli hours, Ni's hours... known application bugs (don't use these functions: Image, resize selection — leaves white rectangle, no resize done).

## Appendix E — Known and Unfixed Bugs

We know these exist, but have not tracked them down yet.

---

*A production of The Tom Hall Press, Inc. All writes reserved.*

*Did ancient architects worship Pi?*
