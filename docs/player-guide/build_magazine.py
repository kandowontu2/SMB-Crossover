"""Magazine edition: real sprite pixels, strong contrast and scene-led pages."""
from pathlib import Path
import math,json,hashlib,argparse
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.lib.utils import ImageReader
import build_edition as b
from edition_content import FILES,CATALOGUES,IDENTITIES
from xml.sax.saxutils import escape
HERE=Path(__file__).parent
NAVY=HexColor('#101d35');BLUE=HexColor('#164ca4');PAPER=HexColor('#fff7df');YELLOW=HexColor('#ffdb35');RED=HexColor('#e43a35');TEAL=HexColor('#007d83')
Q=b.ROOT/'build/verification/player-guide-magazine-2026-10-24' if b.ROOT!=HERE else HERE/'validation'
Q.mkdir(parents=True,exist_ok=True)
SAMPLES=False
def rr(x,y,w,h,col,stroke=None):b.rect(x,y,w,h,col,stroke)
def t(s,x,y,size=10,font='Body',color=NAVY):b.txt(s,x,y,size,font,color)
def p(s,x,top,w,size=10,leading=None,color=NAVY,font='Body',bottom=43):return b.para(s,x,top,w,size,leading,color,font,bottom)
def line(x,y,w,col=NAVY):rr(x,y,w,.7,col)
def art(key,x,y,w,h,scale=9,matte=(16,29,53)):
 """Bake onto RGB: the PDF cannot substitute a white transparency matte."""
 src=Image.open(b.ASSETS/(key+'.png')).convert('RGBA');s=max(1,min(int(w/src.width),int(h/src.height),scale));src=src.resize((src.width*s,src.height*s),Image.Resampling.NEAREST)
 tile=Image.new('RGB',(math.ceil(w),math.ceil(h)),matte);tile.paste(src,((tile.width-src.width)//2,(tile.height-src.height)//2),src)
 b.c.drawImage(ImageReader(tile),x,y,width=w,height=h)
def ribbon(label,x,y,w,col=RED):
 rr(x,y,w,22,col);t(label,x+9,y+6,9,'Bold',white)
def begin(key,section,title=None,sub=None,col=TEAL,dark=False):
 b.page+=1;b.PAGE_META.append(dict(page=b.page,key=key,section=section,title=title or section));b.c.bookmarkPage(key);b.c.addOutlineEntry(title or section,key,0,False)
 rr(0,0,612,792,NAVY if dark else PAPER);rr(0,763,612,29,col);t('POWER PLAY',36,773,12,'Display',YELLOW)
 b.c.setFillColor(white);b.c.setFont('Bold',8);b.c.drawRightString(576,774,section.upper())
 if title:
  size=min(38,540/b.pdfmetrics.stringWidth(b.clean(title),'Display',1));t(title,36,709,size,'Display',white if dark else col)
 if sub:p(sub,36,687,540,10.1,13,color=white if dark else NAVY,bottom=642)
 line(36,35,540,TEAL);t('UNOFFICIAL PLAYER\'S GUIDE  /  OCTOBER 2026',36,23,7.5,'Bold',white if dark else NAVY)
 b.c.setFillColor(YELLOW if dark else NAVY);b.c.setFont('Display',13);b.c.drawRightString(576,21,str(b.page).zfill(2))
def jump(label,target,x,y,w,size=9):
 if SAMPLES:t(label,x,y,size,'Bold',TEAL)
 else:b.link(label,target,x,y,w,size)
def character(a):
 col=RED if a['preview'] else BLUE
 begin(a['key'],'FIELD FILE / '+('DEVELOPMENT PREVIEW' if a['preview'] else 'CHARACTER DOSSIER'),col=col)
 rr(0,644,612,119,NAVY)
 # Slanted yellow tab breaks the rectangular rhythm without touching game art.
 b.c.setFillColor(YELLOW);path=b.c.beginPath();path.moveTo(0,644);path.lineTo(211,644);path.lineTo(228,655);path.lineTo(0,655);path.close();b.c.drawPath(path,fill=1,stroke=0)
 name=a['name'];size=min(40,540/b.pdfmetrics.stringWidth(b.clean(name),'Display',1));t(name,36,711,size,'Display',white)
 p(a['intro'],36,692,540,10.1,13,color=white,bottom=657)
 # Family-specific compositions share typography and color, not a fixed grid.
 n=len(a['heroes']);command_top=365
 if a['key']=='turtles':
  rr(32,316,548,318,YELLOW);rr(36,320,540,310,NAVY)
  labels=['LEONARDO / KATANAS','RAPHAEL / CLOSE RANGE','MICHELANGELO / NUNCHAKU','DONATELLO / LONG REACH']
  for i,k in enumerate(a['heroes']):
   x=40+(i%2)*268;y=345+(1-i//2)*144
   art('hero-'+k,x,y,264,123,3);t(labels[i],x+9,y-11,9.2,'Bold',white)
  command_top=293
 elif a['key']=='meta':
  rr(32,386,548,248,YELLOW);rr(36,390,540,240,NAVY)
  art('hero-meta-knight',43,495,246,127,9)
  t('SWORD FIRST.',311,604,25,'Display',YELLOW);t('THEN TAKE THE SKY.',311,578,25,'Display',white)
  p(a['tip'],311,559,247,10.4,13.5,color=white,bottom=509)
  for i,(name,label)in enumerate([('meta-slash','B: SWORD'),('meta-chain','HOLD B: CHAIN'),('meta-flight','A / UP: FLIGHT')]):
   x=48+i*179;b.image('action-'+name,x,411,128,80);t(label,x,397,9,'Bold',YELLOW)
 elif a['key']=='samus':
  rr(32,386,268,248,YELLOW);rr(36,390,260,240,NAVY);t('THE BOUNTY HUNTER',48,614,11,'Display',YELLOW)
  art('hero-samus',43,450,246,153,8);rr(43,397,246,47,col);p(a['tip'],51,433,230,9.3,12,color=white,bottom=400)
  t('A SMALLER WAY THROUGH',320,616,16,'Display',BLUE)
  for x,name,label in [(320,'samus-exit','UPRIGHT'),(448,'samus-ball','DOWN: MORPH')]:
   b.image('action-'+name,x,470,128,128);t(label,x+4,452,8.8,'Bold',BLUE)
  p('Easy begins with Morph Ball. In Hard, collect it first, then press Down again after crouching.',320,435,256,9.5,12,bottom=393)
 elif a['key']=='parodius':
  rr(32,386,548,248,YELLOW);rr(36,390,540,240,NAVY)
  t('THREE PILOTS. THREE ENSEMBLES.',48,614,16,'Display',YELLOW)
  for i,k in enumerate(a['heroes']):
   x=43+i*177;art('hero-'+k,x,467,171,134,6);t(k.upper(),x+8,452,11,'Bold',white)
  rr(43,397,526,43,RED);p(a['tip'],51,430,510,10,13,color=white,bottom=401)
 else:
  rr(32,386,268,248,YELLOW);rr(36,390,260,240,NAVY);t('MEET YOUR HERO',48,614,10,'Display',YELLOW)
  for i,k in enumerate(a['heroes']):art('hero-'+k,43+i*246/n,470,246/n,133,9)
  rr(43,397,246,62,col);t('PRO TIP',51,446,9,'Display',YELLOW);p(a['tip'],51,438,230,9,11,color=white,bottom=400)
  scene='scene-'+a['heroes'][0]
  if not (b.ASSETS/(scene+'.png')).exists():scene='mario-first-pipes'
  b.image(scene,320,390,256,240);ribbon('IN THE FIELD  /  WORLD 1-1',320,390,256,RED if a['preview'] else TEAL)
 # Compact open rulebook, rather than white cards.
 t('THE COMMAND CENTER',36,command_top,16,'Display',col);line(36,command_top-7,540,col)
 top=command_top-14
 for label,body in a['controls']:
  label=label.replace('Select at character select','Select on portrait').replace('Select at Kirby portrait','Select on Kirby')
  h=max(27,b.measure(label,132,8.8)+6,b.measure(body,388,9.2)+6)
  p(escape(label),43,top,129,8.8,10.5,color=col,font='Bold',bottom=top-h+1)
  p(escape(body),184,top,388,9.2,11.5,bottom=top-h+1)
  line(36,top-h+1,540,HexColor('#cabf9f'));top-=h
 assert top>=165,(a['key'],'controls',top)
 # Modes use a colored editorial comparison band with readable body copy.
 top=min(226,top-7);height=max(b.measure(a['easy'],248,9.1),b.measure(a['hard'],248,9.1))+37
 height=min(108,max(57,height))
 rr(36,top-height,540,height,HexColor('#e9dfbd'))
 for x,label,body,color in [(36,'EASY',a['easy'],TEAL),(312,'HARD',a['hard'],RED)]:
  ribbon(label,x,top-22,264,color)
  p(body,x+8,top-29,248,9.1,11.1,bottom=top-height+5)
 # Powerup plan plus one relevant, authentic visual example.
 y=top-height-19;t('POWERUP PLAN',36,y,12,'Display',col)
 p(a['upgrade'],36,y-8,450,9.3,11.5,bottom=49)
 cat=next(v for v in CATALOGUES if v['key']==(a.get('catalogue')or'common'))
 idx=4 if a['key']=='sypha' else 7 if a['key']=='alucard' else 5 if a['key']=='parodius' else 0
 it=cat['items'][min(idx,len(cat['items'])-1)];art(it['image'],503,max(59,y-57),73,40 if a['key']=='turtles' else 51,3)
 jump('ITEM PICTURES / '+str(b.TARGET_PAGES['cat-'+cat['key']])+' >','cat-'+cat['key'],397,42,179,8)
 b.end()
def cover():
 begin('cover','THE UNOFFICIAL PLAYER\'S GUIDE',col=RED,dark=True)
 t('THE KINGDOM',36,696,47,'Display',white);t('IS OPEN.',36,646,47,'Display',YELLOW)
 rr(330,641,246,93,BLUE);t('33 HEROES',342,694,33,'Display',white);t('+ FOUR DEVELOPMENT PREVIEWS',342,673,9,'Bold',YELLOW)
 t('SMB CROSSOVER',36,577,73,'Display',white)
 rr(0,352,612,205,BLUE)
 # Authentic portraits are deliberately larger than surrounding copy.
 for i,key in enumerate(['mega-man','samus','mario','bass','kirby','link']):
  art('hero-'+key,12+i*99,375,96,161,8,(22,76,164))
 rr(36,333,540,31,YELLOW);t('PICK A HERO. LEARN THE TOOLS. CLEAR THE ROUTE.',49,343,13,'Display',NAVY)
 t('THE COMPLETE FIELD MANUAL',36,298,25,'Display',YELLOW)
 for i,(big,small)in enumerate([('27','CHARACTER FILES'),('37','IDENTITIES COVERED'),('157','PICTURE LEGENDS')]):
  x=36+i*184;t(big,x,239,44,'Display',white);t(small,x,219,10,'Bold',YELLOW)
 p('Find your controls in seconds. Compare Easy and Hard. Identify the real pickups, then put each new move to work.',36,187,540,14,18,color=white,bottom=130)
 line(36,113,540,BLUE)
 p('Includes all 33 published full-roster identities. Roll, Octopus, TwinBee and Pentarou are marked development previews throughout.',36,95,540,10.5,14,color=white,bottom=48)
 b.end()
def start():
 begin('start','GET READY','YOUR FIRST FIVE MINUTES.','Choose the rules first. Learn the special controls second.',col=RED)
 rr(36,392,274,245,NAVY);b.image('character-select',45,397,256,240)
 ribbon('1  OPTIONS',330,610,246,BLUE)
 p('Choose Easy or Hard before starting. Player Shadows defaults OFF; it controls the extra dark outline layer.',330,598,246,11,14,bottom=527)
 ribbon('2  START',330,498,246,RED)
 p('D-pad moves between portraits. Select cycles the highlighted hero\'s alternates. A or a fresh Start confirms. B returns.',330,486,246,11,14,bottom=407)
 t('THE FOUR-BUTTON PLAN',36,365,24,'Display',BLUE)
 for y,label,body in [(324,'A / B','For most ground heroes: A jumps and B attacks. Check the file for combinations and exceptions.'),(260,'START','Pauses play. Inventory guests may offer selection controls while paused.'),(196,'SELECT','On the portrait: alternate character. During play: a special or weapon change. It never swaps your live hero.')]:
  rr(36,y-39,98,48,NAVY);t(label,47,y-14,17,'Display',YELLOW);p(body,150,y+7,426,11,14,bottom=y-38)
 rr(36,60,540,77,YELLOW);t('PRACTICE: OPTIONS > CHEATS',47,119,14,'Display',NAVY)
 p('Invincibility defaults OFF. Start Level chooses 1-1 through 8-4 for your next start. Up/Down selects; Left/Right changes. Invincibility does not save you from pits or timeouts. Reset restores defaults.',47,108,518,10.1,13,bottom=63)
 b.end()
def modes():
 begin('modes','KNOW THE RULES','CHOOSE YOUR CHALLENGE.','Behavior changes enemy contact and the classic guests\' equipment.',col=BLUE)
 for x,label,body,col in [(36,'EASY','The six original heroes use simpler growth ladders. Ground guests can stomp ordinary eligible enemies. Later guests keep their own equipment or health systems.',TEAL),(312,'HARD','The original guests gain later inventory rules. Except the Mario brothers, ordinary body landings are dangerous. Attack first. Ships keep their own shields and terrain rules.',RED)]:
  rr(x,494,264,151,NAVY);ribbon(label,x,616,264,col);p(body,x+12,602,240,11,14,color=white,bottom=507)
 t('THE EASY POWER LADDERS',36,464,24,'Display',BLUE)
 rows=[('mario','Mario / Luigi','Small > Large > Fire'),('mega-man','Mega Man / Proto Man','Buster > charge > stronger shots'),('samus','Samus','Short > Long > Wave Beam'),('bill','Bill / Lance','Normal > Machine Gun > Spread'),('link','Link','Basic sword > stronger > beams'),('simon','Simon','Short > Morning Star > Flame Whip')]
 for i,(hero,name,ladder)in enumerate(rows):
  y=408-i*44;art('hero-'+hero,36,y-5,43,39,2);t(name,91,y+14,10.2,'Bold',BLUE);t(ladder,289,y+14,10.2);line(91,y-2,485,HexColor('#cabf9f'))
 p('A growth pickup advances one tier below the cap. A flower does not jump an unpowered classic hero directly to the final tier.',36,149,540,10.8,14,bottom=109)
 rr(36,51,540,54,YELLOW);t('A STOMP IS NOT EVERY FALLING ATTACK',45,88,12,'Display',NAVY)
 p('Spiny enemies, armor and hazards retain their own rules. A sword thrust, pogo or Screw Attack is a separate move: start it before contact in Hard.',45,78,522,9.5,12,bottom=53)
 b.end()
def directory():
 begin('directory','FIND YOUR HERO','THE ROSTER.','Find the portrait family. Turn to the printed page or click its name.',col=BLUE)
 for i,a in enumerate(FILES):
  col=i//9;row=i%9;x=36+col*184;y=626-row*57
  art('hero-'+a['heroes'][0],x,y-33,43,45,3)
  title='NINJA TURTLES' if a['key']=='turtles' else a['name']
  title=title.replace('MARIO / LUIGI','MARIO / LUIGI')
  size=min(9.6,119/b.pdfmetrics.stringWidth(b.clean(title),'Bold',1))
  jump(title,a['key'],x+51,y,126,size)
  label='PREVIEW' if a['preview'] else 'CHARACTER FILE'
  t(label,x+51,y-13,6.8,'Bold',RED if a['preview'] else NAVY)
  t(str(b.TARGET_PAGES[a['key']]).zfill(2),x+145,y-29,15,'Display',BLUE);line(x+51,y-34,121,HexColor('#cabf9f'))
 rr(36,59,540,58,NAVY);t('READ THE EDITION LABEL',47,98,12,'Display',YELLOW)
 p('The full-roster editions contain 33 identities. Four previews require the private development MMC5 build. Smaller original-roster cartridges contain the original 14 identities.',47,87,518,10,13,color=white,bottom=60)
 b.end()
def catalogue_index():
 begin('power-index','THE PICTURE INDEX','WHAT DID I JUST PICK UP?','Real item art, copy emblems and equipment-bar labels. Each is identified.',col=TEAL)
 for i,g in enumerate(CATALOGUES):
  x=36+(i%2)*276;y=626-(i//2)*62
  art(g['items'][0]['image'],x,y-32,49,49,3)
  name=g['title'].split(':')[0];sz=min(10.3,200/b.pdfmetrics.stringWidth(b.clean(name),'Bold',1));jump(name,'cat-'+g['key'],x+58,y,206,sz)
  t(str(len(g['items']))+' ENTRIES',x+58,y-16,7.5,'Bold',NAVY);t(str(b.TARGET_PAGES['cat-'+g['key']]).zfill(2),x+234,y-24,18,'Display',TEAL);line(x+58,y-33,206,HexColor('#cabf9f'))
 rr(36,55,540,57,YELLOW);t('SAME PICTURE? CHECK THE NAME.',46,94,12,'Display',NAVY)
 p('Some spells or weapons genuinely share a source icon. A copy emblem or power-bar label is marked as such: it is not a separate physical pickup.',46,83,520,10,13,bottom=56)
 b.end()
def catalogue_pages(group):
 rows=group['items'];chunk_size=math.ceil(len(rows)/math.ceil(len(rows)/12));chunks=[rows[i:i+chunk_size]for i in range(0,len(rows),chunk_size)]
 for ix,chunk in enumerate(chunks):
  key='cat-'+group['key']+(''if ix==0 else '-'+str(ix+1));begin(key,'EQUIPMENT ATLAS',col=TEAL)
  rr(0,629,612,134,NAVY);title=group['title'];size=min(36,540/b.pdfmetrics.stringWidth(b.clean(title),'Display',1));t(title,36,712,size,'Display',YELLOW)
  note=('CONTINUED / 'if ix else '')+group['note'];p(note,36,691,540,10.4,13.1,color=white,bottom=640)
  stride=129 if len(chunk)<=8 else 103 if len(chunk)<=10 else 86
  top0=607
  for i,it in enumerate(chunk):
   x=36+(i%2)*276;top=top0-(i//2)*stride
   rr(x,top-69,67,67,TEAL);art(it['image'],x+3,top-66,61,61,4)
   num=ix*chunk_size+i+1;t(str(num).zfill(2),x+52,top-80,9,'Display',TEAL)
   size=10.5 if len(it['name'])<27 else 9.7
   end=p(escape(it['name']),x+77,top,187,size,12,font='Bold',color=BLUE,bottom=top-29)
   body_size=10.1 if stride>=103 else 9.1;p(escape(it['effect']),x+77,end-6,187,body_size,body_size*1.24,bottom=top-stride+7)
   line(x,top-stride+2,264,HexColor('#cabf9f'))
  t('IDENTIFY THE PICTURE. CHECK YOUR MODE. USE THE RIGHT BUTTON.',36,53,9,'Display',TEAL)
  b.end()
def field():
 begin('field','FIELD NOTES','MAKE THE KINGDOM WORK FOR YOU.','The route is familiar. Your character changes the method.',col=RED)
 b.image('mario-first-pipes',36,409,256,240);b.image('mario-gap-course',320,409,256,240)
 for x,title,body,col in [(36,'PIPES: SAVE YOUR EXTRA MOVE','Simon and Bass need a fresh second A. Sypha and Alucard commit to a jump direction. Use the helper platforms on eligible routes.',BLUE),(312,'GAPS: TAKE OFF WITH ROOM','Mario and the SMB3 brothers need a runway. Pit spends limited flight; landing restores it. A ship keeps scrolling while you decide.',TEAL)]:
  ribbon(title,x,383,264,col);p(body,x,370,264,10.4,13.5,bottom=300)
 line(36,295,540,RED)
 t('BLOCKS: LET THE ITEM COME TO YOU',36,271,19,'Display',RED)
 p('Many Hard rewards are separate physical items. Let them rise before collecting. A buster pellet may need two hits on a brick. Pipes, spent blocks and the foundation are not ordinary breakable masonry.',36,253,540,11,14,bottom=186)
 t('WATER: RELEARN THE RHYTHM',36,166,19,'Display',BLUE)
 p('Most ground heroes use repeated A strokes rather than a land jump. Samus can use her ball tools. Pit\'s flower flight is disabled underwater. Frog form and ships have their own directional movement.',36,148,540,11,14,bottom=82)
 rr(36,50,540,25,YELLOW);t('PRACTICE ONE CHARACTER AND ONE MODE AT A TIME.',45,58,12,'Display',NAVY);b.end()
def notes():
 begin('edition','ABOUT THIS GUIDE','THE EDITION CHECK.',col=BLUE)
 t('THE PUBLISHED ROSTER',36,645,24,'Display',BLUE)
 p('The published full-roster MMC3 and MMC5 versions contain 33 identities, including Meta Knight. The smaller original cartridges contain 14. A guide page does not add a character to an older cartridge.',36,625,540,11,14,bottom=563)
 rr(36,351,540,199,NAVY);t('FOUR DEVELOPMENT PREVIEWS',48,526,24,'Display',YELLOW)
 for i,k in enumerate(['roll','octopus','twinbee','pentarou']):art('hero-'+k,48+i*129,430,117,77,4)
 p('Roll and the three Parodius pilots require the private development MMC5 build. Native Parodius death art is now present, within the adapted SMB lifecycle. Substantial lag/dropout, dedicated audio and final campaign checks remain open.',48,419,516,10.5,13.5,color=white,bottom=359)
 t('REAL PIXELS. CLEAR LIMITS.',36,321,22,'Display',BLUE)
 p('Portrait transparency comes from actual sprite patterns, preserving every opaque pixel. Each portrait is shown on a dark RGB-backed panel. Item pictures come from installed graphics and sprite records, or native captures. Shared icons, palette examples and HUD emblems are labeled honestly.',36,300,540,10.6,14,bottom=225)
 p('Planned moves are not written as completed features. This guide does not promise perfect source-game physics/audio or a completed campaign certification. Mike\'s original utility magic and a turtle enemy-drop subweapon inventory are not implemented.',36,215,540,10.6,14,bottom=148)
 t('UNOFFICIAL. MADE FOR PLAYERS.',36,127,17,'Display',TEAL)
 p('Characters and artwork belong to their creators. This fan guide is inspired by classic game magazines. The editable pack includes exact reference hashes, image origins and a coverage audit, with no ROMs or commercial fonts. Preview reference: immutable NR; earlier item captures retain their own source pins.',36,110,540,9.7,12.5,bottom=48)
 b.end()
def main():
 global SAMPLES
 ap=argparse.ArgumentParser();ap.add_argument('--samples',action='store_true');args=ap.parse_args();SAMPLES=args.samples
 b.register_fonts();out=Q/'three-magazine-samples.pdf' if SAMPLES else b.PDF
 b.c=canvas.Canvas(str(out),pagesize=(612,792),pageCompression=1,invariant=1)
 b.c.setTitle('SMB Crossover - Power Play Magazine Guide');b.c.setAuthor('SMB Crossover fan project')
 if SAMPLES:
  for a in FILES:
   if a['key']in['samus','meta','turtles']:character(a)
 else:
  cover();start();modes();directory();catalogue_index()
  for a in FILES:character(a)
  for g in CATALOGUES:catalogue_pages(g)
  field();notes()
 b.c.save();(Q/('magazine-layout.json'if SAMPLES else 'layout-proof.json')).write_text(json.dumps(dict(pdf_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),pages=b.PAGE_META,layout_checks=b.CHECKS,links=b.LINKS,identity_count=len(IDENTITIES),character_files=len(FILES),catalogues=len(CATALOGUES),catalogue_entries=sum(len(v['items'])for v in CATALOGUES)),indent=2));print(out)
if __name__=='__main__':main()
