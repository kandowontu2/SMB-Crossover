"""An editorial rebuild: interleaved character features and illustrated toolkits."""
from pathlib import Path
from PIL import Image
import json,math,hashlib,argparse,os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from xml.sax.saxutils import escape
from edition_content import FILES,CATALOGUES,IDENTITIES
import re
H=Path(__file__).parent; ROOT=H.parents[1] if (H.parents[1]/'src/entrypoint.s').exists() else H
OUT=Path(os.environ.get('PLAYER_GUIDE_OUTPUT_DIR',str(ROOT/'Player Guide')));OUT.mkdir(parents=True,exist_ok=True)
Q=Path(os.environ.get('PLAYER_GUIDE_QA_DIR',str(ROOT/'build/verification/player-guide-astra-redesign' if ROOT!=H else H/'validation')));Q.mkdir(parents=True,exist_ok=True)
INK=HexColor('#141d2d');BLUE=HexColor('#1654bb');RED=HexColor('#e83331');GOLD=HexColor('#ffcf20');TEAL=HexColor('#007d78');PALE=HexColor('#e8edf4');CREAM=HexColor('#fff8e8')
C=None;N=0;META=[];CHECKS=[];USED=[];DEST={};SAMPLE=False
def clean(s):
 s=re.sub(r'([a-zA-Z])(\d)',r'\1 \2',s);s=re.sub(r'(\d)([a-zA-Z])',r'\1 \2',s);return s.replace(' / ', ' / ')
def box(x,y,w,h,col):C.setFillColor(col);C.rect(x,y,w,h,fill=1,stroke=0)
def txt(s,x,y,size=11,font='Body',color=INK):C.setFillColor(color);C.setFont(font,size);C.drawString(x,y,clean(s))
def rule(x,y,w,col=INK):box(x,y,w,.7,col)
def para(s,x,top,w,size=10.4,leading=None,color=INK,font='Body',bottom=40):
 p=Paragraph(clean(s),ParagraphStyle('p',fontName=font,fontSize=size,leading=leading or size*1.25,textColor=color));_,h=p.wrap(w,792)
 assert top-h>=bottom,(N,s[:90],top-h,bottom)
 p.drawOn(C,x,top-h);CHECKS.append(dict(page=N,text=s,x=x,y=top-h,w=w,h=h,size=size));return top-h
def height(s,w,size,font='Body'):
 return Paragraph(clean(escape(s)),ParagraphStyle('h',fontName=font,fontSize=size,leading=size*1.27)).wrap(w,792)[1]
def art(key,x,y,w,h,matte=None):
 p=H/'assets/astra'/(key+'.png')
 if not p.exists():p=H/'assets/edition'/(key+'.png')
 assert p.exists(),key
 im=Image.open(p).convert('RGBA'); scale=min(w/im.width,h/im.height)
 # Pixel art is enlarged with a nearest-neighbor raster; original manual art stays smooth.
 if max(im.size)<300:
  sc=max(1,math.ceil(scale));im=im.resize((im.width*sc,im.height*sc),Image.Resampling.NEAREST)
 iw,ih=im.width,im.height;scale=min(w/iw,h/ih);iw*=scale;ih*=scale
 if matte:
  rgb=tuple(round(v*255)for v in (matte.red,matte.green,matte.blue));flat=Image.new('RGBA',im.size,rgb+(255,));flat.alpha_composite(im);im=flat.convert('RGB')
 C.drawImage(ImageReader(im),x+(w-iw)/2,y+(h-ih)/2,iw,ih,mask='auto');USED.append(dict(page=N,asset=key,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),x=x+(w-iw)/2,y=y+(h-ih)/2,w=iw,h=ih))
def begin(key,section,color=BLUE):
 global N;N+=1;DEST[key]=N;META.append(dict(page=N,key=key,section=section));C.bookmarkPage(key);C.addOutlineEntry(section,key,0,False)
 box(0,0,612,792,white);box(0,758,612,34,INK);txt('CROSSOVER',30,769,15,'Head',white);txt('PLAYER\'S GUIDE',138,770,8,'Bold',GOLD)
 C.setFillColor(white);C.setFont('Bold',8);C.drawRightString(582,771,section.upper())
 box(30,36,552,2,color);txt('POWER PLAY  /  UNOFFICIAL NES FIELD GUIDE',30,23,7,'Bold',INK);C.setFont('Head',13);C.drawRightString(582,21,str(N).zfill(2))
def title(big,deck=None,color=BLUE):
 sz=min(48,552/pdfmetrics.stringWidth(big,'Head',1));txt(big,30,700,sz,'Head',color)
 if deck:para(deck,32,685,548,11,14,bottom=636)
def end():C.showPage()
def eyebrow(s,x,y,col=RED):txt(s,x,y,9,'Bold',col)
def mike_arsenal():
 begin('mike-arsenal','MIKE JONES / THE SPECIALS',RED);title('PACK A BETTER PUNCH.','Ten specials. Choose with Select; attack with B. Learn the silhouette, then watch your stock.',RED)
 rows=[('mike-bat','BASEBALL BAT','A close swing. Step into range before you spend a shot.'),('mike-fire','FIRE','A forward flame attack. Give it a clear lane.'),('mike-sling','SLINGSHOT','A compact ranged shot for enemies ahead.'),('mike-bola','BOLA','A spinning thrown weapon. Keep room while it travels.'),('mike-mirror','MIRACLE MIRROR','A contacting Bill or Bowser flame can become a reflected laser.'),('mike-asterisk','ASTERISK','Throw with B. A fresh second B splits the flying blades.'),('mike-spikes','SPIKES','A bounded screen attack against eligible enemies.'),('mike-baseball','BASEBALL','A thrown ball. Its stock is separate from the slingshot.')]
 for i,(img,name,body) in enumerate(rows):
  x=30+(i%2)*282;top=622-(i//2)*113
  art(img,x,top-82,92,84);eyebrow(str(i+1).zfill(2),x,top+7,RED);txt(name,x+103,top-4,11,'Bold');para(body,x+103,top-17,167,10.2,13,bottom=top-96);rule(x,top-99,270,PALE)
 # The source reuses a tiny projectile; trajectories communicate the actual one/two beam distinction.
 box(30,83,552,100,INK)
 for x,name,key,ys in [(42,'SUPER LASER','mike-shot-12',[132]),(324,'MEGA LASER','mike-shot-13',[123,142])]:
  txt(name,x,160,12,'Bold',GOLD)
  for y in ys:
   C.setStrokeColor(HexColor('#8cdcf6'));C.setLineWidth(2);C.line(x+4,y,x+94,y);C.line(x+94,y,x+86,y+4);C.line(x+94,y,x+86,y-4)
  art(key,x+102,120,33,26,INK);para('One forward beam.' if len(ys)==1 else 'Two separated beams.',x+145,143,108,10.2,13,color=white,bottom=102)
 txt('ATTACK PATH DIAGRAMS',42,94,7.3,'Bold',white)
 para('Weapon illustrations: original StarTropics manual. They identify the tools, not distinct block-pickup icons. Laser paths are diagrams; small sprites are the installed projectiles.',30,70,552,7.7,9.5,bottom=43)
 end()
def zelda_rewards():
 begin('char-zelda2','ZELDA II LINK / GROWTH & MAGIC',TEAL);title('ZELDA II LINK.','Three stats, eight spells and two sword thrusts. Select on Link\'s portrait to choose this separate hero.',TEAL)
 box(30,476,552,159,INK);art('hero-zelda-ii-link',39,498,84,114,INK)
 txt('ATTACK',141,611,17,'Head',GOLD);para('Raises primary strength.',141,598,124,10.2,color=white,bottom=556)
 txt('MAGIC',288,611,17,'Head',GOLD);para('Changes spell costs.',288,598,121,10.2,color=white,bottom=556)
 txt('LIFE',435,611,17,'Head',GOLD);para('Reduces incoming damage.',435,598,124,10.2,color=white,bottom=556)
 para('A jumps; B attacks. Hold Up/Down in the air for a learned thrust. Start pauses: Left/Right changes panels, Up/Down chooses; A buys a stat level (1-8). Buying Life/Magic also refills HP/MP.',141,552,416,10.3,13,color=white,bottom=489)
 para('<b>EASY:</b> ordinary stomps. <b>HARD:</b> attack before body contact. Full health enables sword beams.',44,492,524,9.1,11,color=white,bottom=477)
 eyebrow('THE SPELLBOOK',30,451,TEAL);txt('Choose while paused. Cast with Select.',30,431,16,'Head')
 spells=[('JUMP','Increases your jump height.'),('SHIELD','Halves ordinary damage while active.'),('LIFE','Queues health recovery.'),('FAIRY','Flight transformation; allow clearance.'),('FIRE','Sword attacks launch fire.'),('REFLECT','Shield-area contact can reflect Bowser flames.'),('SPELL','Turns eligible enemies into Goombas.'),('THUNDER','Screen attack on eligible active enemies.')]
 for i,(name,body) in enumerate(spells):
  x=30+(i%2)*282;y=402-i//2*45;txt(name,x,y,10.3,'Bold',TEAL);para(body,x+79,y+9,188,9.6,11.7,bottom=y-29);rule(x,y-31,270,PALE)
 txt('FOLLOW THE REWARD TRAIL',30,204,18,'Head',TEAL)
 para('Blocks teach Jump > Downthrust > Upthrust > Fairy > Shield > Life > Fire > Reflect > Spell > Thunder > Handy Glove, then add capacity. The Glove breaks bricks; HP and MP capacity each cap at 8 containers. Owned or pending unique rewards are skipped.',30,192,552,10.2,13,bottom=139)
 rule(30,135,552,TEAL)
 for x,key,name,body in [(30,'z2-blue','MAGIC JARS','Restore MP.'),(216,'z2-heart','HEART CAPACITY','Up to 8 containers.'),(402,'z2-bag','EXP BAGS','Add experience.')]:
  box(x,66,45,57,INK);art(key,x+4,71,37,47,INK);txt(name,x+55,112,8.5,'Bold');para(body,x+55,99,120,9.1,11,bottom=65)
 end()
def cover():
 begin('cover','THE COMPLETE PLAYER COMPANION',RED)
 box(0,38,612,720,INK);box(0,432,612,215,BLUE)
 txt('SUPER MARIO BROS.',30,710,27,'Head',GOLD);txt('CROSSOVER',25,635,98,'Head',white)
 for i,key in enumerate(['mario','samus','mega-man','link','kirby','simon']):art('hero-'+key,28+i*94,452,86,161,BLUE)
 txt('EVERY HERO.',30,390,54,'Head',white);txt('A NEW WAY TO PLAY.',30,338,48,'Head',GOLD)
 para('Your controls. Your powerups. Your next clever move.',32,310,530,18,23,color=white,bottom=266)
 rule(30,248,552,GOLD)
 for x,big,small in [(30,'33','PUBLISHED HEROES'),(220,'4','PRIVATE PREVIEWS'),(410,'2','BEHAVIOR SETTINGS')]:txt(big,x,184,54,'Head',white);txt(small,x,163,10,'Bold',GOLD)
 para('A practical illustrated field guide to the NES adaptation. Learn one character, find your tools, then take the route your way.',30,124,552,13,17,color=white,bottom=64)
 end()
def start():
 begin('start','START HERE',RED);title('YOUR FIRST FIVE MINUTES.','Set the rules. Pick a favorite. Learn one special before you race ahead.',RED)
 box(30,363,256,256,INK);art('character-select',30,371,256,240)
 for y,n,h,body in [(613,'01','CHOOSE THE RULES','Title > Options: choose Easy or Hard. Player Shadows controls the extra dark outline and defaults off.'),(521,'02','PICK A PORTRAIT','Use the D-pad. Select cycles alternates; A or a fresh Start confirms. B returns.'),(429,'03','LEARN THE EXCEPTION','A usually jumps and B usually attacks. Read the controls for your hero before relying on a button combination.')]:
  txt(n,311,y-3,28,'Head',RED);txt(h,356,y,14,'Head');para(body,356,y-10,224,10.4,13.5,bottom=y-81)
 txt('START PAUSES. SELECT HAS A JOB.',30,326,24,'Head',BLUE)
 para('Select changes a portrait at the menu. During play it can switch a weapon, cast a spell or use a special. It does not swap your live character. Some guests choose equipment while paused.',30,307,552,11.5,15,bottom=240)
 box(30,91,552,134,CREAM);txt('PRACTICE THE HARD PART',44,201,21,'Head',RED)
 para('Options > Cheats lets you choose a starting stage from 1-1 through 8-4. Up/Down selects an option; Left/Right changes it. The setting applies to the next start.',44,184,522,11,14,bottom=132)
 para('Invincibility defaults off. It does not save you from a pit or timeout. Reset restores the defaults.',44,124,522,10.5,13,bottom=95)
 end()
def modes():
 begin('modes','EASY & HARD',BLUE);title('SAME KINGDOM. NEW RULES.','The six original heroes change most. Later guests keep their own systems.')
 for x,label,body,col in [(30,'EASY','Classic growth ladders and ordinary stomps on eligible enemies. Extra guests retain their own health, weapons and movement.',TEAL),(312,'HARD','Separate gear for the original guests. Ordinary body landings are dangerous except for the Mario brothers. Attack before contact.',RED)]:
  box(x,465,270,167,col);txt(label,x+14,594,36,'Head',white);para(body,x+14,578,242,12,16,color=white,bottom=476)
 txt('THE CLASSIC POWER LADDERS',30,430,23,'Head',BLUE)
 ladders=[('mario','Mario / Luigi','Small > Large > Fire'),('mega-man','Mega Man / Proto Man','Buster > Charge > Stronger shot'),('samus','Samus','Short > Long > Wave Beam'),('bill','Bill / Lance','Normal > Machine Gun > Spread'),('link','Link','Basic sword > Stronger > Beams'),('simon','Simon','Short whip > Morning Star > Flame')]
 for i,(key,name,ladder) in enumerate(ladders):
  y=375-i*43;box(30,y-5,40,39,INK);art('hero-'+key,33,y-2,34,33,INK);txt(name,82,y+16,10.6,'Bold');txt(ladder,293,y+16,10.3);rule(82,y-4,500,PALE)
 para('A growth pickup advances one tier below the cap. A flower does not skip an unpowered classic hero straight to the final tier.',30,105,552,10.5,13.5,bottom=68)
 para('Spiny enemies, armor and hazards retain their own rules. A sword thrust, pogo or Screw Attack must already be active when it connects.',30,66,552,9,11.2,bottom=40);end()
def directory():
 begin('directory','CONTENTS',RED);title('FIND YOUR FAVORITE.','Each character feature is followed by its relevant equipment. Shared arsenals are cross-referenced.',RED)
 ordered=[a for a in FILES if not a['preview']]+[a for a in FILES if a['preview']]
 for i,a in enumerate(ordered):
  x=30+i//9*188;y=616-i%9*58
  matte=HexColor('#a7bed0')if a['key']=='meta' else INK
  box(x,y-27,39,43,matte);art('hero-'+a['heroes'][0],x+3,y-24,33,37,matte)
  name=a['name'].replace(' & ',' / ');sz=min(9.6,133/pdfmetrics.stringWidth(name,'Bold',1));txt(name,x+46,y+6,sz,'Bold',BLUE)
  dest='char-'+a['key'];pg=PAGE_PLAN.index(dest)+1 if dest in PAGE_PLAN else 0
  txt(('PREVIEW / 'if a['preview']else'PAGE ')+str(pg),x+46,y-11,8,'Bold',RED if a['preview']else INK)
  C.linkRect('',dest,(x,y-30,x+180,y+19),thickness=0)
 box(30,61,552,43,INK);para('START HERE  2     EASY & HARD  4     SHARED PICKUPS  5',43,89,526,11,font='Bold',color=white,bottom=65);end()
def character(a,variant):
 key=a['key'];col=RED if a['preview']else [BLUE,TEAL,RED][variant%3]
 begin('char-'+key,('PRIVATE PREVIEW / 'if a['preview']else'CHARACTER / ')+a['name'],col)
 name=a['name'];sz=min(48,552/pdfmetrics.stringWidth(name,'Head',1));txt(name,30,702,sz,'Head',col)
 para(a['intro'],32,686,548,11,14,bottom=624)
 top=609
 if key in ('grant','sypha','alucard','roll'):
  box(30,427,552,182,INK);art('hero-'+a['heroes'][0],40,444,101,151,INK)
  it={'grant':[('cv1-27','DAGGER'),('cv1-23','AXE'),('cv1-40','STOPWATCH')],'sypha':[('cv2-1f','FLAME'),('cv2-23','ICE'),('cv2-27','LIGHTNING')],'alucard':[('cv3-22','FIREBALL'),('cv1-07','HEARTS'),('mushroom','RECOVERY')],'roll':[('roll-health-small','SMALL HP'),('roll-health-large','LARGE HP'),('roll-energy-small','SMALL ENERGY'),('roll-energy-large','LARGE ENERGY')]}[key]
  width=425/len(it)
  txt('SOURCE ATTACK / REWARD ART' if key!='roll' else 'HEALTH & ENERGY SUPPLIES',153,591,9,'Bold',GOLD)
  for j,(img,label)in enumerate(it):art(img,153+j*width,478,width-12,83,INK);txt(label,153+j*width,455,8.3,'Bold',white)
 elif key=='samus':
  box(30,427,552,182,INK);art('hero-'+a['heroes'][0],40,448,116,142,INK)
  acts=[('action-samus-upright','UPRIGHT'),('action-samus-ball','DOWN: MORPH')]
  for i,(im,cap)in enumerate(acts):art(im,175+i*132,459,119,110);txt(cap,175+i*132,444,8,'Bold',GOLD)
  if key=='samus':para('A exits the ball when there is room. It does not launch a jump.',445,562,124,11.5,15,color=white,bottom=449)
 elif len(a['heroes'])>=3:
  box(30,427,552,182,col)
  for i,hero in enumerate(a['heroes']):
   w=552/len(a['heroes']);art('hero-'+hero,30+i*w+4,465,w-8,130,col);txt(hero.upper().replace('-',' '),38+i*w,444,9.5,'Bold',white)
 elif variant%3==0:
  box(30,427,196,182,INK)
  for i,hero in enumerate(a['heroes']):art('hero-'+hero,36+i*184/len(a['heroes']),443,184/len(a['heroes']),151,INK)
  eyebrow('TRY THIS FIRST',246,592,col);para(a['tip'],246,579,333,18,23,color=col,font='Serif',bottom=432)
 elif variant%3==1:
  box(30,427,552,182,col)
  for i,hero in enumerate(a['heroes']):art('hero-'+hero,40+i*90,447,84,145,col)
  x=152 if len(a['heroes'])==1 else 235;eyebrow('THE ADVANTAGE',x,590,GOLD);para(a['tip'],x,574,570-x,16,20,color=white,font='Serif',bottom=438)
 else:
  box(30,427,180,182,INK)
  for i,hero in enumerate(a['heroes']):art('hero-'+hero,35+i*170/len(a['heroes']),442,170/len(a['heroes']),153,INK)
  scene='scene-'+a['heroes'][0]
  if (H/'assets/edition'/(scene+'.png')).exists():art(scene,226,427,192,180)
  eyebrow('FIELD NOTE',434,591,col);para(a['tip'],434,577,148,10.5,13.4,bottom=433)
 # Commands and modes share a spread, with open rules instead of card grids.
 txt('AT THE CONTROLS',30,403,19,'Head',col);rule(30,394,272,col)
 y=383
 cs=12.3
 while sum(height(l,270,cs-.3,'Bold')+height(v,270,cs)+12 for l,v in a['controls'])>231:cs-=.2
 for label,body in a['controls']:
  label=label.replace('Select at character select','Select on portrait').replace('Select at Kirby portrait','Select on Kirby')
  y=para(escape(label),30,y,270,cs-.3,(cs-.3)*1.27,color=col,font='Bold',bottom=148)-3
  y=para(escape(body),30,y,270,cs,cs*1.27,bottom=147)-9
 ms=12.3
 while height(a['easy'],255,ms)+height(a['hard'],255,ms)+38>241:ms-=.2
 txt('EASY',327,403,19,'Head',TEAL);hy=para(a['easy'],327,388,255,ms,ms*1.27,bottom=210)
 txt('HARD',327,hy-24,19,'Head',RED);hy=para(a['hard'],327,hy-38,255,ms,ms*1.27,bottom=146)
 low=134
 rule(30,low,552,col);txt('POWERUP PLAN',30,low-23,16,'Head',col)
 copy=a['upgrade'].replace('see the image-backed copy guide','see the enemy field guide');ps=11.5
 while height(copy,552,ps)>54:ps-=.2
 para(copy,30,low-32,552,ps,ps*1.27,bottom=46)
 end()
def toolkit(key):
 if key=='contra':return contra_gear()
 if key=='vic':return ship_gear()
 g=dict(next(x for x in CATALOGUES if x['key']==key));rows=[dict(i)for i in g['items']]
 for r in rows:r['effect']=r['effect'].replace('Shared family artwork is shown as installed.','')
 if key=='common':rows[-1]['effect']='Adds 1 uppercut star, capped at 3. Shown: complete original Punch-Out!! HUD symbol; not SMB invincibility.'
 if key=='contra':rows=[rows[0]]+rows[2:];rows[0]['name']='Rapid / Rapid 2';rows[0]['effect']='Two successive bullet-speed upgrades. Both use this winged R; the current gun stays equipped.'
 if key=='cv3':rows=rows[:-1]
 if key=='link':
  rows[3]['effect']='Select spends one bomb. Stock and refills cap at 20. Give your own blast room until Blue Ring is owned.';rows=rows[:-1]
 if key=='sophia':
  rows[1]['effect']='Select launches a triplet for 3 stock. This picture also marks refills; maximum 60.'
  rows[2]['effect']='Select fires one for 1 stock. This picture also marks homing refills; separate maximum 20.';rows=rows[:-2]
 # One picture per genuinely useful identity; avoid duplicate supply padding.
 if key=='preview':
  rows=rows[5:]
  next(r for r in rows if r['name']=='White Bell')['image']='pn-white-source'
  g['title']='PARODIUS: CHASE THE BELL';g['note']='Private development preview. Shoot a Bell to change it, then collect it. A Gold Bell needs four hits to change; special colors need one.'
 begin('gear-'+key,g['title'],TEAL);title(g['title'].replace('THE ','',1),g['note'].replace('Shared family artwork is shown as installed.',''),TEAL)
 count=len(rows);cols=2 if count>4 else 1;rh=min(122,538/math.ceil(count/cols));tw=270 if cols==2 else 552
 for i,r in enumerate(rows):
  x=30+(i%cols)*282;top=614-(i//cols)*rh
  box(x,top-61,65,65,INK);art(r['image'],x+6,top-56,53,53,INK)
  titleh=para(escape(r['name']),x+77,top+2,tw-79,11.4,13.5,font='Bold',color=TEAL,bottom=top-35)
  para(r['effect'],x+77,titleh-6,tw-79,10.1,12.6,bottom=top-rh+9);rule(x,top-rh+5,tw,PALE)
 if key in ('mega','samus','contra','link','simon','ryu','sophia'):para('Pickup illustrations use the original 2.02 source colors for recognition. Cartridge colors can differ; the corresponding equipment and controls are described above.',30,65,552,8.5,10.6,bottom=42)
 if key=='preview':
  txt('THREE DISTINCT LOADOUTS',30,223,20,'Head',TEAL)
  for y,name,body in [(196,'OCTOPUS','2-Way missiles; Tailgun / Ripple; up to 4 Options; O-Trap.'),(159,'TWINBEE','Returning Rocket Punch; Tailgun / 3-Way; up to 3 Options; Force Field.'),(122,'PENTAROU','Piercing Potion; Double / Spread; up to 3 Options; Bubble shield.')]:
   txt(name,30,y,10,'Bold',TEAL);para(body,130,y+9,452,10.3,13,bottom=y-20)
  para('Four source speed levels. The sixth bar cell, RST, removes upgrades; the final cell buys defense. White Bell uses the original manual illustration; other Bell images are cartridge captures.',30,78,552,9,11.5,bottom=43)
 if key=='smb3':
  box(30,84,552,151,INK);txt('THE RACCOON / TANOOKI FLIGHT DRILL',44,208,21,'Head',GOLD)
  for x,n,head,body in [(44,'1','RUN','Build the P meter on a clear runway.'),(225,'2','JUMP','Take off with full P and room ahead.'),(406,'3','FLAP','Press A repeatedly to fly; plan the landing.')]:
   txt(n,x,160,32,'Head',GOLD);txt(head,x+32,173,14,'Head',white);para(body,x+32,158,136,10.5,13.5,color=white,bottom=97)
 end()
def contra_gear():
 begin('gear-contra','CONTRA / THE GUN RULES',RED);title('KNOW WHAT THE BLOCK GIVES.','Bill and Lance share the same guns. The way you earn them depends on the behavior setting.',RED)
 box(30,450,552,181,INK);txt('EASY: THE THREE-STEP LADDER',44,603,23,'Head',GOLD)
 for x,img,label in [(44,'hero-bill','NORMAL'),(231,'mushroom','MACHINE GUN'),(418,'flower','SPREAD')]:
  art(img,x+39,508,78,78,INK);txt(label,x+12,481,13,'Head',white)
 for x in [202,389]:txt('>',x,540,26,'Head',GOLD)
 txt('HARD: COLLECT THE GUN ITSELF',30,419,23,'Head',RED)
 rows=[('av_art_billpickup2','MACHINE GUN','Hold B for automatic fire.'),('av_art_billpickup6','SPREAD','A fan of bullets covers more of the lane.'),('av_art_billpickup8','LASER','Four connected segments. A fresh burst replaces the old one.'),('av_art_billpickup10','FLARE','Fire circles around a moving center.')]
 for i,(im,name,body)in enumerate(rows):
  x=30+i%2*282;y=390-i//2*113;box(x,y-66,75,75,INK);art(im,x+5,y-61,65,65,INK);txt(name,x+88,y-3,15,'Head',RED);para(body,x+88,y-14,181,11.2,14,bottom=y-85);rule(x,y-92,270,PALE)
 art('av_art_billpickup4',34,99,80,66);txt('RAPID, THEN RAPID 2',132,160,20,'Head',BLUE);para('Two speed upgrades, independent of the equipped gun. Both use the winged R. Hard gun pickups replace one another; there is no retained weapon wheel.',132,144,450,11.5,15,bottom=88)
 para('Winged-letter illustrations use original 2.02 source colors. Mushroom and flower show the native shared pickups.',30,65,552,8.5,10.6,bottom=42);end()
def ship_gear():
 begin('gear-vic','VIC VIPER / THE POWER BAR',BLUE);title('BUY THE ROUTE YOU NEED.','Touch a capsule to advance the cursor. Press B to buy the selected cell.')
 box(30,516,552,112,INK);art('vic-capsule',40,538,72,66,INK);para('The capsule is the physical pickup. Equipment is selected on the bar. Buy only the speed you can control.',129,602,429,14,18,color=white,bottom=537)
 cells=['SPEED','MISSILE','DOUBLE','LASER','OPTION','SHIELD']
 for i,label in enumerate(cells):
  x=30+i*92;box(x,470,87,28,BLUE);txt(label,x+8,479,10,'Bold',white)
 txt('POWER BAR: READING DIAGRAM',30,455,8,'Bold',BLUE)
 diagrams=[('DOUBLE','Forward and diagonal fire; replaces Laser.'),('LASER','A focused forward primary; replaces Double.'),('OPTION','Up to two followers repeat your fire.')]
 for i,(head,body)in enumerate(diagrams):
  y=406-i*90;box(30,y-56,220,69,INK);art('hero-vic-viper',103,y-43,70,40,INK)
  if i==2:
   for x in [48,78]:C.setStrokeColor(GOLD);C.setLineWidth(2);C.circle(x,y-22,8,stroke=1,fill=0)
  C.setStrokeColor(GOLD);C.setLineWidth(2);C.line(177,y-22,239,y-22)
  if i==0:C.line(177,y-22,222,y+1)
  txt(head,269,y-4,19,'Head',BLUE);para(body,269,y-18,313,11.4,14.7,bottom=y-58)
 para('Attack / follower diagrams use the native ship sprite. Paths and rings explain the equipment; they are not pickup artwork.',30,142,552,8.5,10.6,bottom=112)
 para('<b>MISSILE:</b> floor-crawling support. <b>SHIELD:</b> absorbs five enemy contacts; solid terrain still kills. The Parodius previews use a related bar with their own guns and an extra reset cell.',30,99,552,11.1,14.2,bottom=50);end()
def field():
 begin('field','FIELD SCHOOL / ROUTES',RED);title('THE ROUTE IS YOUR TOOL.','Read the ground before you spend the extra jump, flight or weapon stock.',RED)
 for x,img,head,body in [(30,'mario-first-pipes','PIPES: SAVE A MOVE','Simon and Bass need a fresh second A. Sypha and Alucard commit to their launch direction. Line up before the jump.'),(312,'mario-gap-course','GAPS: FIND A RUNWAY','Mario and the SMB3 brothers need room to build speed. Pit spends limited flight; landing restores it. Ships keep scrolling.')]:
  art(img,x,367,256,240);txt(head,x,345,17,'Head',RED);para(body,x,330,264,11,14,bottom=256)
 rule(30,244,552,RED);txt('BLOCKS: LET THE REWARD RISE',30,216,25,'Head',BLUE)
 para('Many Hard rewards are separate physical items. Let them rise before collecting. A buster pellet may need two hits on a brick. Pipes, spent blocks and the foundation are not ordinary breakable masonry.',30,196,552,12,16,bottom=124)
 box(30,59,552,52,GOLD);para('Practice one character and one behavior setting at a time. Change the method before you change the hero.',42,97,528,13,17,font='Bold',bottom=63);end()
def water():
 begin('water','FIELD SCHOOL / WATER & HAZARDS',BLUE);title('A DIFFERENT KIND OF JUMP.','The best land habit can be the wrong underwater habit.')
 art('mario-water-coral',30,363,256,240);art('bass-firebars',312,363,256,240)
 for x,head,body in [(30,'KEEP THE SWIM RHYTHM','Most ground heroes use repeated A strokes in water. Samus has her ball tools; Frog form and ships have their own directional movement. Pit\'s flower flight is disabled underwater.'),(312,'CONTACT HAS CONDITIONS','Varia covers firebars. The two empty mounts shown in 1-4 are intentional; they become active in 6-4, regardless of Easy or Hard. Other hazards keep their own contact rules.')]:
  txt(head,x,337,18,'Head',BLUE);para(body,x,320,264,11.3,15,bottom=211)
 rule(30,190,552,BLUE);txt('KEEP A RESERVE FOR THE RETURN',30,163,24,'Head',RED)
 para('Do not spend every heart, missile or energy unit crossing the first obstacle. Alucard pays for bat flight; the buster guests have separate weapon pools; Mike\'s strong primary depends on filled hearts. Read the meter before choosing the route.',30,142,552,12,16,bottom=66);end()
def meta_knight():
 begin('char-meta','META KNIGHT / PRIVATE NU UPDATE',TEAL);title('THE GROUNDED SWORDSMAN.',"Select on Kirby's portrait to choose Meta Knight. These repaired moves require the private NU build.",TEAL)
 box(30,486,552,145,INK);box(39,498,130,121,HexColor('#a7bed0'));art('hero-meta-knight',43,506,120,106,HexColor('#a7bed0'))
 txt('ONE JUMP. SIX SWORD ATTACKS.',182,604,24,'Head',GOLD)
 para('A makes a fixed jump. A second A or Up gives no extra lift. Get close on the ground, then choose a sword move for the space ahead.',182,585,382,12,15,color=white,bottom=516)
 txt('NES boss poses adapted for play; sword audio uses an SMB fallback.',182,503,9,'Body',white)
 moves=[('slash','B / ON GROUND','SWORD SLASH','A close swing. Face the enemy before attacking.'),('triple','UP + B / ON GROUND','TRIPLE SLASH','Three strokes from one command. Leave room for the sequence.'),('charge','LEFT / RIGHT + B','CHARGING SWORD','A moving ground attack. Check the runway before committing.'),('lunge','SELECT / ON GROUND','LUNGE','A low forward thrust. Use it when the enemy is already in reach.'),('spin','B / IN THE AIR','AIR SPIN','An aerial sword sweep. Jump first, then press B.'),('plunge','DOWN + B / IN THE AIR','DOWNWARD STRIKE','Holds briefly in the air, then drops. Choose safe ground below.')]
 for i,(key,control,name,body) in enumerate(moves):
  x=30+i%2*282;top=463-i//2*113
  art('meta-nu-'+key,x,top-82,92,83);txt(name,x+102,top-3,12,'Head',TEAL)
  para(control,x+102,top-12,167,8.1,10,font='Bold',bottom=top-38)
  para(body,x+102,top-40,167,10.2,13,bottom=top-99);rule(x,top-103,270,PALE)
 txt('Actual private-build practice views, cropped without altering game pixels.',30,126,7.8,'Body')
 rule(30,116,552,TEAL)
 para('<b>FOOD:</b> six health points. Alternating mushroom/flower food heals 2, up to 6; no copy powers or weapon tiers. The sword activates question blocks and breaks eligible bricks.',30,104,552,10,12.8,bottom=62)
 para('<b>EASY:</b> ordinary stomps. <b>HARD:</b> body contact hurts. Sword moves and health stay the same.',30,60,552,9.4,12,bottom=40);end()

def mike_primary():
 a=next(x for x in FILES if x['key']=='mike');begin('char-mike','MIKE JONES / THE ISLAND ADVENTURER',RED);title('HEARTS MAKE THE HERO.','A returning primary, ten stocked specials and a health meter that changes what you can throw.',RED)
 art('mike-batter',32,391,186,242);box(245,430,337,190,INK);txt('A: JUMP   B: ATTACK',260,592,20,'Head',GOLD);para('Select cycles stocked specials, then returns to the unlimited primary. Watch the weapon name and your filled hearts.',260,573,306,12,15,color=white,bottom=510);para('Easy allows ordinary stomps. Hard makes body contact dangerous. Hearts and weapon stocks work in both modes.',260,505,306,11,14,color=white,bottom=442)
 eyebrow('THE PRIMARY LADDER',30,373,RED)
 for x,img,name,body in [(30,'mike-yoyo','ISLAND YO-YO','Your unlimited starting primary.'),(218,'mike-shooting','SHOOTING STAR','Own the upgrade and keep 6 hearts filled.'),(406,'mike-nova-source','SUPER NOVA','Own the upgrade and keep 11 hearts filled.')]:
  if img=='mike-nova-source':box(x,280,171,77,INK)
  art(img,x,284,171,69,INK if img=='mike-nova-source' else None);txt(name,x,264,12,'Head',RED);para(body,x,251,171,10.5,13.5,bottom=210)
 rule(30,198,552,RED)
 for x,img,name,body in [(30,'mike-bigheart','BIG HEART','Adds capacity and refills health; maximum 22.'),(218,'mike-heart','SMALL HEART','Restores one filled heart.'),(406,'mike-star','STAR','Every five collected restore one filled heart.')]:
  art(img,x,116,52,65);txt(name,x+62,172,11,'Head',RED);para(body,x+62,160,109,10,12.5,bottom=109)
 para('Special stock clears at life loss or a new level; ordinary pipe areas preserve it. Capacity and owned primary upgrades persist. When health falls below a threshold, the primary falls back.',30,96,552,9.8,12.5,bottom=54)
 txt('Nintendo manual illustrations, including Super Nova; not installed pickup screenshots.',30,44,7.6,'Body');end()
def notes():
 begin('notes','EDITION & ART NOTES',BLUE);title('KNOW YOUR EDITION.','This guide covers the published roster and clearly marked private previews.')
 txt('33 PUBLISHED IDENTITIES',30,617,27,'Head',BLUE);para('The published full-roster MMC3 and MMC5 editions contain 33 identities, including Meta Knight. Smaller original-roster cartridges contain 14. An alternate is selected from its portrait before play. Meta Knight\'s repaired grounded moves and native palette on page 33 require the private NU update.',30,597,552,11.2,14,bottom=526)
 box(30,317,552,196,INK);txt('FOUR PRIVATE PREVIEWS',44,484,27,'Head',GOLD)
 for i,k in enumerate(['roll','octopus','twinbee','pentarou']):art('hero-'+k,44+i*134,399,121,66,INK)
 para('Roll and the three Parodius pilots require the private development MMC5 build. Native Parodius death art is present. Lag/dropout, dedicated audio, full-campaign validation and final all-item coverage remain open.',44,386,524,11,14,color=white,bottom=326)
 txt('ABOUT THE PICTURES',30,283,23,'Head',BLUE);para('Enemy portraits use native world poses and palettes. Mike\'s marked illustrations come from Nintendo\'s StarTropics manuals; laser paths are diagrams. Other item pictures use original 2.02 source colors or installed art, as captioned. Exact origins and image hashes are in the editable pack.',30,264,552,11,14.5,bottom=182)
 txt('A FIELD GUIDE, STILL IN DEVELOPMENT',30,155,22,'Head',RED);para('Planned abilities are not presented as complete. Mike\'s original utility magic and a turtle enemy-drop subweapon inventory are not implemented. This guide does not certify a complete campaign or source-game-perfect physics and audio.',30,137,552,10.5,13.5,bottom=75)
 para('Unofficial fan guide inspired by classic game magazines. Characters and source artwork belong to their creators. Source references: NR baseline plus the frozen NU Meta Knight update; earlier field captures retain their recorded origins.',30,65,552,8.2,10.2,bottom=40);end()
INSERT={'megaman':'mega','samus':'samus','bill':'contra','link':'link','simon':'simon','ryu':'ryu','sophia':'sophia','darkwing':'darkwing','smb3':'smb3','vic':'vic'}
def plan():
 seq=[('cover',cover),('start',start),('directory',directory),('modes',modes),('gear-common',lambda:toolkit('common'))]
 ordered=[a for a in FILES if not a['preview']]+[a for a in FILES if a['preview']]
 for i,a in enumerate(ordered):
  seq.append(('char-'+a['key'],meta_knight if a['key']=='meta' else mike_primary if a['key']=='mike' else zelda_rewards if a['key']=='zelda2' else lambda a=a,i=i:character(a,i)))
  if a['key'] in INSERT:
   k=INSERT[a['key']];seq.append(('gear-'+k,lambda k=k:toolkit(k)))
  if a['key']=='kirby':seq.append(('kirby-copy',kirby_powers))
  if a['key']=='mike':seq.append(('mike-arsenal',mike_arsenal))
  if a['key']=='parodius':seq.append(('gear-preview',lambda:toolkit('preview')))
 seq += [('field',field),('water',water),('notes',notes)]
 return seq
def kirby_powers():
 begin('kirby-copy','KIRBY / ENEMY FIELD GUIDE',RED);title('A KINGDOM OF NEW TRICKS.','Inhale with B. Swallow with Down. B uses your new power; Select lets it go.',RED)
 rows=next(g for g in CATALOGUES if g['key']=='kirby')['items']
 for i,item in enumerate(rows):
  x=30+(i%2)*282;top=622-(i//2)*78;name,power=item['name'].split(': ',1)
  matte=HexColor('#a7bed0') if i in (3,13) else INK
  box(x,top-57,56,59,matte);art('enemy-'+str(i+1),x+4,top-53,48,51,matte)
  txt(name.upper().replace('RED / FLYING CHEEP','RED CHEEP'),x+67,top-1,9.1,'Bold',RED)
  txt(power.upper(),x+67,top-16,14,'Head');para(item['effect'],x+67,top-24,202,9.4,11.4,bottom=top-67);rule(x,top-70,270,PALE)
 para('Enemy portraits show native world poses and colors. These are copy targets, not collectible items. Swallow to keep a power; spit with B for an immediate star attack instead.',30,64,552,8.2,10,bottom=41)
 end()
PAGE_PLAN=[s[0]for s in plan()]
def run(samples=False):
 global C,SAMPLE;SAMPLE=samples
 for name,file in [('Body','arial.ttf'),('Bold','arialbd.ttf'),('Head','impact.ttf'),('Serif','georgiai.ttf')]:pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
 path=Q/'design-samples.pdf' if samples else OUT/'SMB-Crossover-Players-Guide.pdf'
 C=canvas.Canvas(str(path),pagesize=(612,792),invariant=1,pageCompression=1);C.setTitle('SMB Crossover - Players Guide');C.setAuthor('Unofficial player guide')
 if samples:mike_arsenal();zelda_rewards();kirby_powers()
 else:
  for key,fn in plan():fn()
 C.save()
 (Q/'layout-proof.json').write_text(json.dumps(dict(pages=META,paragraphs=CHECKS,images=USED,pdf_sha256=hashlib.sha256(path.read_bytes()).hexdigest()),indent=2))
 print(path)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--samples',action='store_true');a=p.parse_args();run(a.samples)
