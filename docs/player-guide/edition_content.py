"""Player-facing copy for the33-character edition plus4 marked previews.

This is a controls/reference guide, not a claim of final campaign certification.
All item rows require an authentic image; shared icons are explicit.
"""
from guide_content import PROFILES as ORIGINAL_FILES
import copy
FILES=[]
CATALOGUES=[]
def item(image,name,effect):return dict(image=image,name=name,effect=effect)
def cat(key,title,note,rows):
 CATALOGUES.append(dict(key=key,title=title,note=note,items=[item(*r) for r in rows]))
def add(key,name,heroes,intro,controls,easy,hard,upgrade,tip,catalogue=None,preview=False,sources=None):
 FILES.append(dict(key=key,name=name,heroes=heroes,intro=intro,controls=controls,easy=easy,hard=hard,upgrade=upgrade,tip=tip,catalogue=catalogue,preview=preview,sources=sources or []))
def legacy(key,heroes,catalogue=None):
 p=copy.deepcopy(next(p for p in ORIGINAL_FILES if p['key']==key))
 add(key,p['name'],heroes,p['intro'],p['controls'],p['easy'],p['hard'],p['upgrades'],p['tips'][0][1],catalogue,sources=p['sources'])

cat('common','THE SHARED PICKUPS','These are the actual native item pictures. A mushroom or flower can mean growth, equipment or health: read your character file. A picture is an identification aid, not a promise that every hero receives every item.',[
 ('mushroom','Mushroom','Growth for the classic power ladder. Health-based guests use it for recovery or a custom reward.'),
 ('flower','Fire Flower','Next classic tier, a separate weapon, a form or recovery. The reward depends on the character and behavior setting.'),
 ('star','Super Star','Temporary native invincibility for ground characters. Do not use it as protection from a pit or timeout.'),
 ('1up','1-UP Mushroom','Adds a life. It does not refill every separate weapon pool.'),
 ('mm-energy-small','Small weapon energy','Mega Man / Proto Man / Bass: restore8 of112 energy units. Energy Balancer can redirect the refill.'),
 ('mm-energy-large','Large weapon energy','Mega Man / Proto Man / Bass: restore40 of112 energy units. Also used by block refills.'),
 ('mac-star','Little Mac: uppercut star','Flower replacement. Adds1 super-punch star, capped at3. This is separate from SMB invincibility.')])
cat('mega','THE BUSTER WORKSHOP','Mega Man and Proto Man use this inventory in Hard. Bass uses it in both settings, except Rush. Select cycles owned weapons back to normal. Paused Left/Right moves either way; paused Select returns to the buster. Each weapon has its own energy supply.',[
 ('mm-arm','Super Arm','Keep8 energy in reserve. Hold B beside liftable empty masonry; B again throws it and spends8.'),
 ('mm-metal','Metal Blade','B plus a direction aims in eight ways. Costs4.'),
 ('mm-knuckle','Hard Knuckle','Launch with B, then steer Up/Down after startup. Costs8.'),
 ('mm-pharaoh','Pharaoh Shot','B fires a small shot; hold and release to charge. Costs4 small /8 charged.'),
 ('mm-kick','Charge Kick','Select it, then Down+A. The paid sliding attack costs4.'),
 ('mm-flame','Flame Blast','B launches a seed that grows into a surface flame. Costs4.'),
 ('mm-water','Water Shield','B summons orbiting balls. A fresh B after formation sends them outward. Costs16 to summon.'),
 ('mm-rush','Rush Coil','Mega Man / Proto Man only. B summons; Up+B places him higher. Needs4 to appear; a spring spends12.'),
 ('mm-balance','Energy Balancer','Passive. Routes energy to an eligible owned weapon; no attack or equip command.'),
 ('mushroom','Buster upgrade','Mega Man / Proto Man: charge becomes available. Bass: ordinary on-screen shot cap rises from3 to4.')])
cat('samus','SAMUS: GEAR & SUPPLIES','The distinct equipment icons below are Hard-mode items. Easy follows Short Beam > Long Beam > Wave Beam and starts with Morph Ball/bombs.',[
 ('mushroom','Long Beam','The first Hard growth upgrade extends the starting beam.'),
 ('av_art_samuspickup5','Morph Ball','Down again after crouching transforms. A exits the ball when there is room.'),
 ('av_art_samuspickup7','Missiles','Acquire missile ability and stock. Select fires; Down+Select toggles B missile mode. Maximum20.'),
 ('av_art_samuspickup3','Ice Beam','Freezes eligible surviving enemies; they can become temporary footholds.'),
 ('av_art_samuspickup4','Wave Beam','Changes the beam pattern. Beam equipment replaces the other beam choice.'),
 ('av_art_samuspickup1','Varia','Protection against firebars. It is not invincibility against every hazard.'),
 ('av_art_samuspickup10','Screw Attack','Attack during the spinning jump. Ordinary standing or non-spinning contact is different.'),
 ('av_art_samuspickup11','Missile refill','Restores missile stock up to the20 maximum. Morph Ball B plants bombs without spending missiles.')])
cat('contra','CONTRA: KNOW YOUR GUN','Bill and Lance share these rules. In Easy, mushroom grants Machine Gun and flower grants Spread. Hard gun pickups replace the current gun; they are not a permanent weapon wheel.',[
 ('av_art_billpickup4','Rapid','First bullet-speed upgrade. Independent of which gun is equipped.'),
 ('av_art_billpickup4','Rapid2','Second speed upgrade. Uses the same actual winged Rapid icon.'),
 ('av_art_billpickup2','Machine Gun','Hold B for automatic fire. Easy mushroom / separate Hard gun pickup.'),
 ('av_art_billpickup6','Spread','A fan of bullets. Easy flower / separate Hard gun pickup.'),
 ('av_art_billpickup8','Laser','Four connected segments. A new burst replaces the previous burst.'),
 ('av_art_billpickup10','Flare','Fire travels around a moving center. Plan its path rather than treating it like a straight bullet.')])
cat('link','LINK: SWORD & SATCHEL','These are original Link items. Zelda II Link has a separate spell/EXP system. Select uses the chosen special; B always keeps the sword.',[
 ('mushroom','Sword growth / boomerang','Easy advances the sword tier. Hard mushroom adds the short boomerang.'),
 ('flower','Top sword tier','Easy reaches sword beams. Hard blocks supply separate equipment instead.'),
 ('av_art_linkpickup6','Short / Magic Boomerang','Short is the initial special; Magic upgrades it. Both share the actual returning-boomerang icon.'),
 ('av_art_linkpickup3','Bombs','Select uses one. Stock maximum20. Give your own blast room until Blue Ring is owned.'),
 ('av_art_linkpickup2','Bow','Select fires an arrow. Separate arrow stock, maximum20.'),
 ('av_art_linkpickup7','Red Ring','Improves the powered sword state.'),
 ('av_art_linkpickup8','Blue Ring','Protection from Link\'s own bomb blast.'),
 ('av_art_linkpickup9','Arrow refill','Restores arrows up to the cap.'),
 ('av_art_linkpickup10','Bomb refill','Restores bombs up to the cap.')])
cat('simon','SIMON: WHIP & SUBWEAPONS','Easy advances Short Whip > Morning Star > Flame Whip and supplies free axes. Hard uses a heart pool (maximum99) and separate equipment. Pause + Left/Right chooses; Select or Up+B uses the subweapon.',[
 ('mushroom','Morning Star','The first whip upgrade uses the actual mushroom reward. It is not the Triple Shot icon.'),
 ('av_art_simonpickup6','Flame Whip','Further whip upgrade. Whipping itself spends no hearts.'),
 ('av_art_simonpickup1','Cross','Returning subweapon; costs1 heart.'),
 ('av_art_simonpickup3','Dagger','Straight forward throw; costs1 heart.'),
 ('av_art_simonpickup4','Holy Water','A ground-level flame tool; costs1 heart.'),
 ('av_art_simonpickup5','Stopwatch','Stops enemy movement for about3 seconds of game updates; costs5 hearts.'),
 ('av_art_simonpickup2','Axe','Arcing throw; costs1 heart in Hard. Free in Easy.'),
 ('av_art_simonpickup7','Double Shot','Raises the simultaneous subweapon allowance.'),
 ('av_art_simonpickup8','Triple Shot','Further raises the allowance. Shared family artwork is shown as installed.'),
 ('av_art_simonpickup11','Small heart','Restores1 heart.'),
 ('av_art_simonpickup10','Large heart','Restores5 hearts.')])
cat('ryu','RYU: NINJITSU','The ordinary sword is free. Specials share one ninjitsu pool:50 maximum, or99 with the scroll. Pause + Left/Right chooses an owned attack; Select or Up+B uses it.',[
 ('av_art_ryupickup2','Shuriken','Straight throw; costs3 ninjitsu.'),
 ('av_art_ryupickup4','Fire Wheel','Protective rotating fire attack; costs5.'),
 ('av_art_ryupickup5','Windmill Shuriken','Returning spinning weapon; costs5.'),
 ('av_art_ryupickup7','Fire Dragon Ball','Flame attack; costs5.'),
 ('av_art_ryupickup3','Jump Slash','With it selected, press B in the air for the spinning blade; costs5.'),
 ('av_art_ryupickup8','Sword Extension','Improves the ordinary sword. It is separate from ninjitsu selection.'),
 ('av_art_ryupickup1','Ninjitsu Scroll','Raises maximum ninjitsu to99.'),
 ('av_art_ryupickup10','Small refill','Restores5 ninjitsu.'),
 ('av_art_ryupickup9','Large refill','Restores10 ninjitsu.')])
cat('sophia','SOPHIA: BUILD THE ROUTE','Sophia keeps her equipment in both modes. B stays the main cannon. Pause + Left/Right chooses the missile type; Select fires it. Separate stocks are shown in the HUD.',[
 ('mushroom','Hyper cannon','The first growth upgrade strengthens the main cannon.'),
 ('av_art_sophiapickup7','Standard Missiles','Select launches a triplet for3 stock. Maximum60.'),
 ('av_art_sophiapickup6','Homing Missiles','Select fires a homing missile for1. Separate maximum20.'),
 ('av_art_sophiapickup3','Hover','A fresh A in the air starts it; hold to sustain while fuel lasts. Eight-unit reserve regenerates when inactive.'),
 ('av_art_sophiapickup2','Crusher','Further main-cannon upgrade.'),
 ('av_art_sophiapickup4','Wall Climbing','Up attaches at an eligible wall. This is separate from ceiling travel.'),
 ('av_art_sophiapickup5','Ceiling Travel','Up attaches at an eligible ceiling after the required upgrade. A releases.'),
 ('av_art_sophiapickup10','Missile refill','Refills the standard stock.'),
 ('av_art_sophiapickup9','Homing refill','Refills the homing stock.')])
cat('darkwing','DARKWING: GAS, GEAR & RECOVERY','Adaptor pickups replace the carried adaptor. Select changes between the normal gas gun and the owned adaptor. B fires; the normal gas shot is free.',[
 ('dw-22','Small health','Restores1 health point, capped at4.'),
 ('dw-23','Full health','Restores all4 health points. Some blocks become recovery while health is low.'),
 ('dw-24','Large gas','Restores10 special gas, up to99.'),
 ('dw-25','Small gas','Restores1 special gas.'),
 ('dw-26','Arrow Gas','Fires a platform-forming arrow; costs3 gas.'),
 ('dw-27','Heavy Gas','Ground-spreading shot; costs2 gas.'),
 ('dw-28','Thunder Gas','Multi-direction electric shot; costs2 gas.'),
 ('star','Super Star','Uses the native SMB temporary-invincibility rule; not a new adaptor.')])
cat('zelda2','ZELDA II LINK: LEARNED REWARDS','A spell may share another spell\'s actual reward picture. These are the installed illustrations, not invented unique icons. Rewards are acquired physically; unique owned or pending rewards are skipped.',[
 ('z2-magic','Jump','First learned spell. Select casts it for the current Magic-level cost.'),
 ('z2-sword','Downthrust','Learn, then hold Down in the air to point the sword below.'),
 ('z2-sword','Upthrust','Learn, then hold Up in the air. Same actual sword reward icon.'),
 ('z2-fairy','Fairy','Learn the flight transformation. Cast with clearance and enough MP.'),
 ('z2-magic','Shield','Halves ordinary damage while active; changes the tunic. Shared magic picture.'),
 ('z2-heart','Life','Queues recovery using the native meter refill. MP cost depends on Magic level.'),
 ('z2-fire','Fire','Sword attacks launch the learned fire projectile.'),
 ('z2-magic','Reflect','Can reflect contacting Bowser flames through the shield area.'),
 ('z2-magic','Spell','Turns eligible SMB enemies into Goombas.'),
 ('z2-magic','Thunder','Screen attack against eligible active enemies.'),
 ('z2-glove','Handy Glove','Learned brick-breaking upgrade.'),
 ('z2-heart','Heart Container','Adds health capacity, to8 containers.'),
 ('z2-magic','Magic Container','Adds magic capacity, to8 containers.'),
 ('z2-blue','Blue magic jar','Physical MP recovery. Native refill amounts and meter cadence are retained.'),
 ('z2-red','Red magic jar','Larger MP recovery. Jar colors vary with the shared area palette.'),
 ('z2-bag','EXP bag','Adds experience; enemy classes use this adaptation\'s rewards.')])
cat('mike','MIKE: EVERY WEAPON','Select cycles stocked specials and returns to the unlimited primary. Filled hearts control the effective primary: Shooting Star needs6, Super Nova needs11. Owning an upgrade alone is not enough.',[
 ('mike-bigheart','Big Heart','Block reward: adds1 full-heart capacity and refills health, maximum22.'),
 ('mike-2','Shooting Star','First primary upgrade. Falls back when fewer than6 hearts are filled.'),
 ('mike-3','Super Nova','Next primary upgrade. Needs11 filled hearts.'),
 ('mike-4','Baseball Bat','Stocked special. B swings it.'),
 ('mike-5','Slingshot','Stocked ranged special.'),
 ('mike-6','Fire','Stocked fire attack. Shares the installed source-family icon shown.'),
 ('mike-7','Miracle Mirror','A contacting Bill or Bowser flame can become a reflected laser.'),
 ('mike-8','Asterisk','Press B again while blades fly to split the two tracks.'),
 ('mike-9','Bola','Stocked special; keep clear of enemies while it travels.'),
 ('mike-10','Spikes','Bounded screen attack against eligible enemies.'),
 ('mike-11','Baseball','Stocked thrown weapon. Its actual item art is shared with another tool.'),
 ('mike-12','Super Laser','Stocked beam. Shared actual item shape; read the HUD name.'),
 ('mike-13','Mega Laser','Two separated beams. Shared actual item shape; read the HUD name.'),
 ('mike-heart','Small heart','Restores1 full heart, capped at capacity.'),
 ('mike-star','Star','Every5 collected restore1 full heart. This small source star is not the SMB Super Star.')])
cat('kirby','KIRBY: THE COPY FIELD GUIDE','Hold B to inhale, Down to swallow, or B again to spit a star. Once a power is copied, B uses it and Select discards it. These are actual copy HUD emblems. Enemy-to-power assignments are SMB adaptations.',[
 ('kirby-copy-1','Goomba: Charge','A grounded forward body charge.'),
 ('kirby-copy-2','Green Koopa: Shell','Fires a green shell-type projectile.'),
 ('kirby-copy-3','Red Koopa: Shell','Fires the red shell-type variant.'),
 ('kirby-copy-4','Buzzy Beetle: Guard','Hold B on the ground to guard; it does not protect from every hazard.'),
 ('kirby-copy-5','Hammer Bro: Hammer','An arcing hammer projectile.'),
 ('kirby-copy-6','Bloober: Jet','An upward attack projectile.'),
 ('kirby-copy-7','Grey Cheep: Bubble','A slower horizontal bubble.'),
 ('kirby-copy-8','Red / flying Cheep: Shot','A faster fish-family shot.'),
 ('kirby-copy-9','Paratroopa: High Jump','B launches the rising body attack.'),
 ('kirby-copy-10','Lakitu: Cloud','Hold B to suspend vertical fall during the active ability.'),
 ('kirby-copy-11','Spiny: Needles','Fires a three-needle fan.'),
 ('kirby-copy-12','Piranha Plant: Bite','A close body/contact attack.'),
 ('kirby-copy-13','Podoboo: Fire','Rapid fire-family projectile.'),
 ('kirby-copy-14','Bullet Bill: Dash','A forward aerial body dash.')])
cat('cv3','CASTLEVANIA III: FIELD EQUIPMENT','The companions carry one subweapon rather than Simon\'s full pause inventory. Flowers rotate Grant/Sypha\'s carried choices and add5 hearts; Alucard flowers upgrade his fireballs. Attack graphics are also their actual block-reward illustrations.',[
 ('mushroom','Companion recovery','Mushroom restores16 of64 health units. Alucard at maximum fireball power can also receive healing.'),
 ('cv1-27','Grant: Dagger','Up+B, or B while clinging. Costs1 heart.'),
 ('cv1-23','Grant: Axe','Arcing subweapon; costs1 heart.'),
 ('cv1-40','Grant: Stopwatch','Stops enemies; costs5 hearts.'),
 ('cv2-1f','Sypha: Flame','Expanding ground-directed flame. Uses the carried spell.'),
 ('cv2-23','Sypha: Ice','Multi-direction ice. Frozen eligible enemies can support a landing; staff shatters them.'),
 ('cv2-27','Sypha: Lightning','Three seeking orbs with native steering.'),
 ('cv3-22','Alucard: Fireball power','Two upgrades add upward/downward diagonal fireballs. Ordinary B fire is free.'),
 ('cv1-07','Grant / companions: heart','Small and large drops restore1 /5 hearts. Maximum99. Shown: one source phase.'),
 ('cv2-07','Sypha heart phase','The source heart can use a different character palette. Same supply, not a separate currency.')])
cat('smb3','SMB3: PICK YOUR FORM','A small character receives a mushroom. Once powered, a flower-class block can randomly give any of the five normal forms below. Repeats are possible. This block roulette is specific to the adaptation.',[
 ('smb3-1','Super Mushroom','Small > Super. B runs; A jumps.'),
 ('smb3-2','Fire Flower','B throws fireballs. Normal fireballs preserve masonry.'),
 ('smb3-3','Super Leaf','Raccoon form: B tail attack; repeated A slows descent. Full P plus a running jump starts flight.'),
 ('smb3-4','Frog Suit','Land hops and dedicated underwater movement.'),
 ('smb3-5','Tanooki Suit','Raccoon moves plus Down+B statue. Release Down to return.'),
 ('smb3-6','Hammer Suit','B throws hammers with inherited movement. Hammers pass through terrain.')])
cat('preview','PREVIEW: ROLL & PARODIUS','These4 guests require the private development MMC5 version. Bell pictures show Octopus colors. Native pilot death art is present. Substantial lag/dropout, dedicated audio and campaign checks remain unfinished.',[
 ('mushroom','Roll: mushroom / flower','Both restore28 health and28 energy. They do not unlock Bass weapons.'),
 ('roll-health-small','Roll: small health','Restores2 HP, capped at28.'),
 ('roll-health-large','Roll: large health','Restores10 HP.'),
 ('roll-energy-small','Roll: small energy','Restores2 energy, capped at28.'),
 ('roll-energy-large','Roll: large energy','Restores10 energy.'),
 ('pn-gold','Gold Bell','Shot repeatedly to change it. Score streak:500,1000,2500,5000,10000.'),
 ('pn-blue','Blue Bell','Super Bomb clears eligible enemies and flashes the screen.'),
 ('pn-red','Red Bell','Three powerful crest shots.'),
 ('pn-white','White Bell','Awards a life.'),
 ('pn-big','Flashing / Big Bell','Temporary giant invincibility; cannot fire while Big. The flashing phase is shown.')])
cat('vic','THE SHIP POWER BARS','A physical capsule advances the cursor; B buys the selected cell. Equipment is not dropped as separate weapon icons. Labels shown below are actual HUD pictures. Parodius inserts its reset cell before the final defense cell.',[
 ('vic-capsule','Power capsule','Physical contact advances the bar. Growth blocks supply capsules for ships. Shown: Vic Viper\'s actual capsule.'),
 ('vic-bar-1','Speed Up','Vic Viper: increase speed. Parodius: four source speed levels; do not buy speed you cannot control.'),
 ('vic-bar-2','Missile','Vic: floor-crawling missile. Octopus:2-Way. TwinBee: returning Rocket Punch. Pentarou: piercing Potion.'),
 ('vic-bar-3','Double / Tailgun','Vic and Pentarou: Double. Octopus and TwinBee: Tailgun. Replaces the other primary upgrade.'),
 ('vic-bar-4','Laser / alternate gun','Vic: Laser. Octopus: growing Ripple. TwinBee:3-Way. Pentarou: Spread explosion.'),
 ('vic-bar-5','Option','Vic: up to2 followers. Octopus: up to4. TwinBee / Pentarou: up to3.'),
 ('vic-bar-6','Vic Viper: Shield','Five enemy contacts absorbed; solid terrain still kills.'),
 ('pn-bar-reset','Parodius: RST reset','The sixth cell removes upgrades. It is not a random prize.'),
 ('pn-bar-defenses','Parodius: defenses','Final cell. Top: Octopus O-Trap. Middle: TwinBee Force Field. Bottom: Pentarou Bubble shield.')])

legacy('mario',['mario','luigi'],'common')
legacy('megaman',['mega-man','proto-man'],'mega')
FILES[-1]['name']='MEGA MAN & PROTO MAN';FILES[-1]['intro']='Two buster heroes share the same movement and weapon lineup. Highlight Mega Man and press Select for Proto Man. Mega Man starts helmetless; charging arrives with the first growth upgrade.'
FILES[-1]['upgrade']='Easy: buster > charge > stronger fire-colored shots. Hard: charge, eight active tools and Energy Balancer. Proto Man uses the same moves and upgrades.'
FILES[-1]['hard']='The 2.02 movement path adds the walking startup step and allows a jump out of a clear slide. Mushroom grants charging; later blocks reveal individual weapons, including Rush Coil for this shared moveset.'
legacy('bass',['bass'],'mega')
add('roll','ROLL',['roll'],'A separate mobile-inspired buster guest. Highlight Bass and press Select. Roll has her own health and energy instead of Bass\'s weapon wheel.', [('A','Jump; release for a shorter rise.'),('B','Fire up to3 ordinary shots.'),('Hold B','Automatically charge/fire after60 game updates; costs4 energy.'),('Select in play','No Bass weapon cycling, dash or double jump.')], 'Ordinary stomps are allowed. Movement uses the installed Mega Man Easy profile.','Use the buster or avoid body contact. Movement uses the installed Mega Man Hard profile.','28 HP /28 energy. Mushroom and flower refill both; physical enemy capsules restore2 or10. Charge, damage scaling and recovery are adaptation rules.','Keep room to retreat while charging. A full projectile pool delays the charge without spending its energy.','preview',True,['src/roll.s','src/roll_weapons.s','docs/qa/roll-mobile-private-implementation-2026-10-23.md'])
legacy('samus',['samus'],'samus')
legacy('bill',['bill','lance'],'contra')
legacy('link',['link'],'link')
add('zelda2','ZELDA II LINK',['zelda-ii-link'],'A different Link with health, magic and experience. Select on Link\'s portrait changes to this separate adventure-style moveset.',[('A / B','Jump / timed sword attack.'),('Air Up / Down','Use the corresponding thrust after learning it.'),('Select','Cast the selected learned spell; spends MP.'),('Start','Pause. Up/Down chooses; Left/Right switches spell/stat panels. A buys an affordable stat level.')],'Ordinary stomps are available alongside sword and spells.','Ordinary body landings hurt; use the sword, thrusts or spells.','Attack/Magic/Life levels1-8. Full health enables a sword beam. Upgrade blocks teach abilities in order, then add containers; enemies supply EXP and recovery.','Buy the stat that solves your current problem. Magic level changes spell costs; primary strength follows Attack.','zelda2',sources=['src/zelda2_link_rpg.s','src/zelda2_link_rewards.s','docs/qa/zelda2-link-private-implementation-2026-10-23.md'])
legacy('simon',['simon'],'simon')
FILES[-1]['controls'][-1]=('Select at Simon portrait','Cycle Simon > Grant > Sypha > Alucard.')
add('grant','GRANT DANASTY',['grant'],'Quick movement, a close knife and walls that can become routes. Select on Simon\'s portrait cycles to Grant.',[('A / B','Jump / close knife.'),('Toward a wall','Air contact grabs an eligible wall; keep holding toward it. Up/Down climbs.'),('Up at a ceiling','Attach; Left/Right crawls. A releases or leaps away.'),('Up+B / clinging B','Use the carried dagger, axe or stopwatch.')],'Ordinary enemy stomps are allowed. Wall and weapon systems remain.','Ordinary landings hurt. Knife, subweapons and climbing remain.','64 health units; hearts cap99. Mushrooms heal16. Flowers rotate dagger > axe > stopwatch and add5 hearts.','A wall grab is an opportunity to plan the next jump. It is not protection from enemies.','cv3',sources=['src/cv3_core.s','src/cv3_pickups.s','docs/qa/cv3-alternates-implementation-2026-10-23.md'])
add('sypha','SYPHA BELNADES',['sypha'],'A short staff for nearby targets and three distinct spells. Her jump commits to its starting direction.',[('A / B','Jump / staff.'),('Down+B','Crouching staff attack.'),('Up+B','Use carried Flame, Ice or Lightning.'),('Select at Simon portrait','Cycle to Sypha before starting.')],'Ordinary stomps are allowed. Spell and health systems remain.','Ordinary body contact hurts. Freeze a valid enemy for a temporary foothold, or attack before landing.','64 health;99-heart cap. Mushrooms heal16; flowers cycle Flame > Ice > Lightning and add5 hearts. Her jump is enlarged for SMB terrain.','Ice is a route tool. Land on an admitted frozen enemy, then use the staff if you want to shatter it.','cv3',sources=['src/cv3_core.s','src/cv3_combat.s','src/cv3_pickups.s'])
add('alucard','ALUCARD',['alucard'],'Fireballs and bat flight trade close-range agility for new routes. His ordinary jump also keeps its launch direction.',[('A / B','Jump / free fireball.'),('Down+B','Crouched fireball.'),('Down+A','Transform into or out of a bat; allow room to stand.'),('Bat D-pad','Fly; cannot fire. Entry costs1 heart, then1 per60 game updates.')],'Ordinary stomps are allowed outside his special movement.','Ordinary body landings hurt. Use fireballs and flight to keep distance.','64 health;99 hearts maximum. Mushrooms heal16. Two flower upgrades add upward and downward fireball diagonals; later flowers heal.','Bat flight is paid travel. A pipe transition keeps your supply, but life loss resets the companion record.','cv3',sources=['src/cv3_core.s','src/cv3_combat.s','src/cv3_pickups.s'])
legacy('pit',['pit'],'common');FILES[-1]['intro']='A bow, a hammer and a limited burst of wing flight. Pit is an added guest with his own three-tier progression in both behavior settings.'
legacy('rygar',['rygar'],'common')
legacy('ryu',['ryu'],'ryu')
legacy('sophia',['sophia'],'sophia')
legacy('scrooge',['scrooge'],'common');FILES[-1]['controls'][-1]=('Select at Scrooge portrait','Switch to Darkwing Duck; his moveset is separate.')
FILES[-1]['upgrade']='Mushroom and flower advance the normal power state. Cane and pogo are available from the start; neither pickup adds a separate weapon inventory or the original DuckTales treasure/health system.'
add('darkwing','DARKWING DUCK',['darkwing'],'Scrooge\'s alternate brings a gas gun, cape guard and ledge hanging. Select on Scrooge\'s portrait to switch.',[('A / B','Jump / fire gas gun.'),('Up on the ground','Raise the cape guard.'),('Jump to an edge','Hang where admitted; Up climbs, Down drops, A jumps away.'),('Select','Toggle normal gas / the currently owned adaptor.')],'Ordinary stomps are allowed. Four-health-point and gas systems remain.','Ordinary body landings hurt. Use the cape or gun when their contact rules apply.','Arrow, Heavy or Thunder adaptor; one at a time. Arrow costs3 gas; Heavy/Thunder2. Enemy supplies restore gas/health; maximum99 gas.','Arrow Gas can form a temporary foothold on an eligible wall. Check the landing before spending the next shot.','darkwing',sources=['src/darkwing_core.s','src/darkwing_weapons.s','src/darkwing_pickups.s'])
add('kirby','KIRBY',['kirby'],'Inhale, swallow and borrow an enemy\'s trick. Mushroom and flower are food; Kirby has six health points rather than Mario growth.',[('A / Up','Jump; a new air press starts floating. Hold to rise.'),('B with an empty mouth','Hold to inhale eligible enemies.'),('Down / B with a full mouth','Swallow for the copy power / spit the enemy as a star.'),('B with a power / Select','Use the copied ability / discard it.')],'Ordinary stomps are allowed. The six-point health and copy systems remain.','Ordinary contact costs health; use inhale, copy attacks or avoidance.','Mushroom and flower restore2 HP. Fourteen SMB enemy families provide distinct copy attacks; see the image-backed copy guide.','Spitting and swallowing are a choice. A star clears a lane now; a useful copy can solve the next obstacle.','kirby',sources=['src/kirby_core.s','src/kirby_weapons.s'])
add('meta','META KNIGHT',['meta-knight'],"Kirby's Select alternate is a grounded swordsman. The repaired native palette and six attacks described here require the private NU update.",[('A','Fixed ballistic jump; no second-A or Up flight.'),('Ground B / Up+B','Sword slash / triple slash.'),('Ground Left/Right+B / Select','Charging sword / lunge.'),('Air B / Down+B','Spin / brief airborne hold, then downward strike.')],'Ordinary stomps are allowed. Sword moves and six-point health remain.','Ordinary body contact hurts. Sword moves and health are unchanged.','Alternating mushroom and flower food heals 2, capped at 6 HP. No copy powers or weapon tiers. Sword attacks activate question blocks and break eligible bricks.','Choose safe landing ground before beginning the downward strike.','common',sources=['src/meta_knight.s','reference/meta-knight/art-manifest.json','build/verification/meta-knight-source-nu/art-independent-v5.json'])
add('chip','CHIP & DALE',['chip','dale'],'The Rescue Rangers turn crates into weapons and cover. Select changes Chip to Dale on their portrait; controls and health match.',[('A','Jump; release shortens the rise.'),('B nearby','Pick up a crate or an eligible loose brick. B again throws it.'),('Up+B while carrying','Throw upward.'),('Down while carrying','Hide in the crate. An eligible ordinary enemy can break it instead of hurting you.')],'Ordinary stomps are allowed alongside crates.','Ordinary body contact hurts. Carry a crate before closing the distance.','Three health points. Mushroom heals1; flower restores all3. A visible entrance crate starts each area. These pickups do not grant new weapon tiers.','You can lift breakable empty masonry, not pipes, question blocks or the foundation. Losing a crate means finding another.','common',sources=['src/chip_dale_core.s','src/chip_dale_boxes.s','docs/qa/chip-dale-private-implementation-2026-10-23.md'])
add('mac','LITTLE MAC',['little-mac'],'Run the kingdom in the training tracksuit. This side-view boxing adaptation uses hearts for fighting spirit and stars for uppercuts.',[('A / Down','Jump / duck.'),('B','Punch; Down+B attacks low.'),('Up+B','Spend1 star for an uppercut.'),('No hearts: duck','Duck for30 game updates to recover20 hearts.')],'Ordinary stomps are allowed. Boxing health, spirit and star rules remain.','Ordinary landings hurt. Time a punch or super before contact.','96 HP,20 starting hearts. A missed punch costs1 heart; a hit refunds it. Mushrooms heal24. Flowers become visible stars; carry at most3.','Save a star for an armored target. Normal punches cannot defeat a Buzzy Beetle; the uppercut can.','common',sources=['src/little_mac_core.s','src/little_mac_combat.s','docs/qa/little-mac-implementation-2026-10-23.md'])
add('mike','MIKE JONES',['mike-jones'],'The island adventurer brings a returning primary, a bag of special weapons and an important rule: a strong primary needs enough filled hearts.',[('A / B','Jump / use the selected weapon.'),('Select','Cycle stocked specials, then back to the unlimited primary.'),('Asterisk: fresh second B','Split the flying blades into two tracks.'),('Watch HP and the name','Below6 or11 filled hearts, the primary falls back even if the stronger weapon is owned.')],'Ordinary stomps are allowed. Hearts and special-ammo systems remain.','Ordinary body contact hurts. Attack or retrieve supplies before committing.','Big Hearts increase capacity; Shooting Star and Super Nova upgrade the primary. Ten stocked specials follow. Small hearts and five collected stars restore health.','Special stock clears at life loss or a new level; ordinary pipe areas preserve it. Capacity and owned primary upgrades persist.','mike',sources=['src/mike_jones_core.s','src/mike_jones_weapons.s','src/mike_jones_pickups.s'])
add('smb3','SMB3 MARIO & LUIGI',['smb3-mario','smb3-luigi'],'A second Mario slot with the original SMB3 movement and form repertoire. Select changes the brother; these are separate from the original Mario/Luigi slot.',[('A / B','Jump / run. At fire or hammer power, a fresh B throws.'),('Raccoon / Tanooki B','Tail attack. Repeated A slows descent.'),('Full P, jump, repeated A','Launch from a run and flap to fly.'),('Tanooki Down+B','Become a statue; release Down to return.')],'Both brothers retain SMB3 forms and ordinary enemy stomps.','Both retain their forms and ordinary stomps; this slot does not become a gunner-style no-stomp character.','Mushroom grows; later blocks randomly provide Fire, Leaf, Frog, Tanooki or Hammer. Higher suit damage drops to Super, then small.','The P meter rewards a runway. Charge it before a gap, and keep enough space to start the jump at speed.','smb3',sources=['src/smb3_mario_core.s','src/smb3_mario_pickups.s','src/smb3_mario_world.s'])
add('vic','VIC VIPER',['vic-viper'],'A scrolling shooter inside the Mushroom Kingdom. The camera advances automatically during ordinary flight until the level\'s end lock.',[('D-pad','Fly in four directions.'),('A','Fire the main gun, missiles and equipped Options.'),('B','Buy the highlighted power-bar cell.'),('Capsules','Physical contact advances the bar. Choose when to buy instead of spending immediately.')],'Flight and shield rules remain; there is no ordinary foot stomp.','The same ship rules remain. Solid terrain is fatal even with a shield.','Speed Up, Missile, Double, Laser, up to2 Options and Shield. Double and Laser replace each other. Shield absorbs5 enemy contacts; the sixth is fatal.','An Option follows your recent path. Move around an obstacle before firing so it gains a useful angle.','vic',sources=['src/vic_viper.s','src/vic_gear.s','docs/qa/vic-viper-implementation-2026-10-23.md'])
add('parodius','THE PARODIUS PILOTS',['octopus','twinbee','pentarou'],'Three playful Vic Viper alternates. Select on the ship portrait cycles Vic Viper > Octopus > TwinBee > Pentarou.',[('D-pad / A','Fly / fire the owned ensemble.'),('B','Buy the highlighted power-bar cell.'),('Capsules','Advance the7-cell power bar; spending is a separate B press.'),('Bells','Shoot to change the color, then physically collect the reward.')],'These remain aircraft-style guests, with shield/terrain rules rather than foot stomps.','Same native equipment and Bell systems. Contact still requires the ship\'s defense rules.','Octopus uses Tailgun / Ripple; TwinBee uses Tailgun /3-Way; Pentarou uses Double / Spread. Each has its own missile/Option art, speed limits and shield.','A Gold Bell needs4 hits to change; the special colors need1. Choose the next shot before chasing the Bell.','preview',True,['src/parodius.s','src/parodius_bells.s','docs/qa/parodius-integration-2026-10-23.md'])
add('turtles','TEENAGE MUTANT NINJA TURTLES',['leonardo','raphael','michelangelo','donatello'],'Leonardo: katanas. Raphael: sai. Michelangelo: nunchaku. Donatello: bo. The four original NES fighters share a slot; Select cycles the brothers before starting.',[('A','Jump; hold for the native variable rise.'),('B','Use the selected turtle\'s weapon.'),('Up+B / Down+B','Attack high / low; Down also crouches on land.'),('Select at character select','Leonardo > Raphael > Michelangelo > Donatello.')],'Ordinary stomps are allowed. Melee attacks and native turtle health remain.','Ordinary body landings hurt. Use the weapon\'s reach and direction.','Each turtle has128 health units. Mushroom restores32 and flower64. The four primary weapons differ in reach, speed and power; there is no implemented enemy-drop subweapon inventory.','Donatello\'s bo reaches far; Raphael must close in. Attack before your body overlaps the target.','common',sources=['src/tmnt_core.s','src/tmnt_combat.s','src/tmnt_dispatch.s'])

IDENTITIES={h for p in FILES for h in p['heroes']}
assert len(IDENTITIES)==37,len(IDENTITIES)
assert len(FILES)==27,len(FILES)
