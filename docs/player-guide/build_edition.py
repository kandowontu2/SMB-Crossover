"""Editable, image-backed player's guide. No ROM is needed to rebuild the PDF."""
from pathlib import Path
from xml.sax.saxutils import escape
import hashlib,json,math,re
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from edition_content import FILES,CATALOGUES,IDENTITIES
HERE=Path(__file__).parent; ASSETS=HERE/'assets/edition'
ROOT=HERE.parents[1] if (HERE.parents[1]/'src/entrypoint.s').exists() else HERE
OUT=ROOT/'Player Guide';OUT.mkdir(exist_ok=True)
QA=ROOT/'build/verification/player-guide-nq-refresh-2026-10-24' if ROOT!=HERE else HERE/'validation'
QA.mkdir(parents=True,exist_ok=True)
PDF=OUT/'SMB-Crossover-Players-Guide.pdf'
INK=HexColor('#142735');CREAM=HexColor('#faf5e8');RED=HexColor('#cf3839');TEAL=HexColor('#087e8b');GOLD=HexColor('#f7c945');PALE=HexColor('#e5ece8');GRAY=HexColor('#526574')
W,H,M=612,792,36;PW=W-2*M
CHECKS=[];LINKS=[];PAGE_META=[];c=None;page=0
TARGET_PAGES={'cover':1,'start':2,'modes':3,'directory':4,'power-index':5}
TARGET_PAGES.update({p['key']:6+i for i,p in enumerate(FILES)})
_cursor=6+len(FILES)
for _group in CATALOGUES:
 TARGET_PAGES['cat-'+_group['key']]=_cursor
 _cursor+=math.ceil(len(_group['items'])/12)
TARGET_PAGES.update(field=_cursor,edition=_cursor+1)
def register_fonts():
 for n,f in [('Body','arial.ttf'),('Bold','arialbd.ttf'),('Italic','arialbi.ttf'),('Display','impact.ttf')]:
  path=Path('C:/Windows/Fonts')/f
  if not path.exists():raise RuntimeError('Install licensed Arial/Impact fonts, or edit register_fonts() to use available equivalents.')
  pdfmetrics.registerFont(TTFont(n,str(path)))
def clean(t):
 # Editorial spacing: compact source notes used forms such as "restores2".
 t=re.sub(r'([A-Za-z])(\d)',r'\1 \2',t)
 t=re.sub(r'(\d)([A-Za-z])',r'\1 \2',t)
 t=re.sub(r'([,;])(?=\w)',r'\1 ',t)
 t=t.replace('page 8','the Buster Workshop').replace('page8','the Buster Workshop')
 return t
def rect(x,y,w,h,col,stroke=None):
 c.setFillColor(col);c.setStrokeColor(stroke or col);c.rect(x,y,w,h,fill=1,stroke=bool(stroke))
def txt(t,x,y,size=10,font='Body',color=INK):
 c.setFillColor(color);c.setFont(font,size);c.drawString(x,y,clean(t))
def para(t,x,top,w,size=10,leading=None,color=INK,font='Body',bottom=43):
 t=clean(t);style=ParagraphStyle('p',fontName=font,fontSize=size,leading=leading or size*1.3,textColor=color)
 p=Paragraph(t,style);_,h=p.wrap(w,H)
 assert top-h>=bottom,(page,t[:65],round(top-h,1),bottom)
 p.drawOn(c,x,top-h);CHECKS.append(dict(page=page,text=t,left=x,right=x+w,top=top,bottom=top-h,font_size=size));return top-h
def measure(t,w,size=10):
 p=Paragraph(clean(escape(t)),ParagraphStyle('m',fontName='Body',fontSize=size,leading=size*1.3));return p.wrap(w,H)[1]
def image(key,x,y,w,h=None):
 p=ASSETS/(key+'.png');im=Image.open(p);h=h or w*im.height/im.width
 # Pixel data, rather than the absolute filename, supplies the PDF image key.
 # This keeps a rebuild from the editable ZIP byte-identical in a new folder.
 c.drawImage(ImageReader(im),x,y,width=w,height=h,mask='auto',preserveAspectRatio=True)
def fit(key,x,y,w,h,max_scale=5):
 im=Image.open(ASSETS/(key+'.png'));scale=min(w/im.width,h/im.height,max_scale);iw,ih=im.width*scale,im.height*scale
 image(key,x+(w-iw)/2,y+(h-ih)/2,iw,ih)
def pill(t,x,y,col=TEAL):
 w=pdfmetrics.stringWidth(clean(t),'Bold',8)+16;rect(x,y-3,w,17,col);txt(t,x+8,y+2,8,'Bold',white)
def begin(key,section,title=None,sub=None,col=TEAL,dark=False):
 global page
 page+=1;PAGE_META.append(dict(page=page,key=key,section=section,title=title or section));c.bookmarkPage(key)
 c.addOutlineEntry(title or section,key,level=0,closed=False)
 rect(0,0,W,H,INK if dark else CREAM);rect(0,775,W,17,col)
 txt('POWER PLAY',M,751,11,'Bold',GOLD if dark else INK)
 txt('/  SMB CROSSOVER',119,751,8.5,'Bold',white if dark else GRAY)
 c.setFont('Bold',8);c.setFillColor(white if dark else GRAY);c.drawRightString(W-M,751,section.upper())
 if title:
  size=min(36,PW/pdfmetrics.stringWidth(clean(title),'Display',1));txt(title,M,701,size,'Display',GOLD if dark else col)
 if sub:para(sub,M,680,PW,10.2,color=white if dark else GRAY)
 rect(M,36,PW,0.7,GRAY);txt('UNOFFICIAL PLAYER\'S GUIDE  /  OCTOBER 2026',M,23,7.5,'Bold',white if dark else GRAY)
 c.setFont('Bold',9);c.setFillColor(white if dark else INK);c.drawRightString(W-M,22,str(page).zfill(2))
def end():c.showPage()
def link(label,target,x,y,w,size=9.5):
 txt(label,x,y,size,'Bold',TEAL);c.linkRect('',target,(x,y-4,x+w,y+13),relative=0,thickness=0);LINKS.append(dict(page=page,target=target,label=label))
def box(title,body,x,top,w,h,col=TEAL,size=10):
 rect(x,top-h,w,h,white);rect(x,top-23,w,23,col);txt(title,x+11,top-16,9,'Bold',white)
 para(body,x+11,top-33,w-22,size,bottom=top-h+9)
def cover():
 begin('cover','PLAYER\'S GUIDE',dark=True)
 txt('THE KINGDOM IS OPEN.',M,704,24,'Display',GOLD)
 txt('SMB',M,612,90,'Display',white);txt('CROSSOVER',M,535,76,'Display',white)
 pill('PICK A HERO. LEARN THE TOOLS. CLEAR THE ROUTE.',M,501,RED)
 image('mario-first-pipes',M,222,300,281)
 rect(350,222,226,281,TEAL)
 txt('33 HEROES',364,470,30,'Display',GOLD);txt('+ 4 DEVELOPMENT PREVIEWS',364,448,10,'Bold',white)
 featured=['mario','mega-man','samus','bill','link','simon','bass','kirby']
 for i,k in enumerate(featured):fit('hero-'+k,364+(i%4)*50,370-(i//4)*58,44,56,3)
 para('Every character.<br/>Easy and Hard, side by side.<br/>Real powerup pictures.<br/>Controls you can find fast.',364,290,194,10.1,14,color=white,bottom=227)
 txt('SWORDS  /  BUSTERS  /  FLIGHT  /  POGO  /  COPY POWERS',M,184,11,'Bold',GOLD)
 para('A practical companion to the NES adaptation. Start with a character file, then use the illustrated powerup catalogue when an unfamiliar item appears.',M,157,PW,12,16,color=white,bottom=99)
 para('Includes the published full-roster edition and clearly marked previews of Roll, Octopus, TwinBee and Pentarou.',M,79,PW,9.5,color=white,bottom=47);end()
def start():
 begin('start','START HERE','THE FOUR-BUTTON PLAN.','Set the rules, choose the hero, then learn one special at a time.')
 box('1  TITLE > OPTIONS','Choose Easy or Hard before starting. Player Shadows defaults OFF. It changes the extra dark outline layer, not enemy difficulty.',M,646,264,100,TEAL)
 box('2  TITLE > START','D-pad chooses a portrait. Select cycles that portrait\'s alternates. A or a fresh Start confirms; B returns.',312,646,264,100,RED)
 rect(M,324,256,201,INK);image('character-select',M+21,326,214,200)
 txt('A / B',316,514,18,'Display',TEAL)
 para('For most ground heroes: A jumps and B attacks. The character files explain exceptions and combinations.',316,491,260,10.5,bottom=435)
 txt('START',316,417,18,'Display',TEAL)
 para('Pauses during play. Inventory guests may offer selection controls while paused.',316,394,260,10.5,bottom=350)
 box('SELECT HAS TWO DIFFERENT JOBS','<b>Before play:</b> changes the highlighted portrait\'s alternate. <b>During play:</b> uses a special or changes weapons, depending on the hero. It never swaps your live character.',M,305,PW,83,RED,10.3)
 box('PRACTICE FROM OPTIONS > CHEATS','Invincibility defaults OFF. Start Level selects 1-1 through 8-4 for your next start. Up/Down selects a setting; Left/Right changes it. Invincibility does not save you from pits or timeouts. Reset returns defaults.',M,207,PW,93,TEAL,10)
 para('<b>Reading the controls:</b> "fresh A" means release A, then press it again. "Up+B" means hold Up while pressing B. Timed durations count game updates; heavy scenes may run slower.',M,96,PW,10,bottom=49);end()
def modes():
 begin('modes','KNOW THE RULES','EASY OR HARD?','Behavior changes the hero\'s toolkit and contact rules.')
 box('EASY','The six original heroes use their simpler growth ladders. Ground guests can stomp ordinary eligible enemies. Later guests keep their own equipment or health systems.',M,645,264,113,TEAL,10.5)
 box('HARD','The original guests gain later inventory rules. Except the Mario brothers, ordinary body landings are dangerous: attack first. Ships keep their own shield and terrain rules.',312,645,264,113,RED,10.5)
 rows=[('Mario / Luigi','Small > Large > Fire'),('Mega Man / Proto Man','Buster > charge > stronger fire shots'),('Samus','Short Beam > Long Beam > Wave Beam'),('Bill / Lance','Normal gun > Machine Gun > Spread'),('Link','Basic sword > stronger sword > beams'),('Simon','Short Whip > Morning Star > Flame Whip')]
 pill('THE EASY GROWTH LADDERS',M,504)
 for i,(n,v) in enumerate(rows):
  y=460-i*37;rect(M,y-9,PW,34,white if i%2==0 else PALE);txt(n,M+10,y+2,10,'Bold');txt(v,M+196,y+2,10)
 para('A growth pickup advances one tier when you are below the cap. A flower does not jump an unpowered classic hero straight to the final tier.',M,235,PW,10.4,bottom=195)
 box('A STOMP IS NOT EVERY FALLING ATTACK','Spiny enemies, sides, armor and hazards still have their own rules. A sword thrust, Scrooge\'s pogo, Screw Attack and a charged body move are distinct attacks. In Hard, equip or start the move before touching the target.',M,178,PW,95,RED,10.3)
 para('The character files state both modes directly. Guests added for this ROM do not have imaginary Crossover 1.0 versions.',M,68,PW,9.5,bottom=46);end()
def directory():
 begin('directory','FIND YOUR HERO','THE CHARACTER FILES.','Every identity appears under the moveset it actually uses.')
 for i,p in enumerate(FILES):
  col=i//14;row=i%14;x=M+col*276;y=630-row*38
  label=p['name'];label=label if len(label)<28 else 'THE FOUR NINJA TURTLES'
  fit('hero-'+p['heroes'][0],x,y-5,27,29,2)
  link(label,p['key'],x+36,y+12,224,8.7 if len(label)>22 else 9.5)
  c.setFillColor(TEAL);c.setFont('Bold',9.5);c.drawRightString(x+262,y+12,str(TARGET_PAGES[p['key']]))
  preview='  [PREVIEW]' if p['preview'] else ''
  subtitle='FOUR TURTLES / SELECT TO CYCLE' if p['key']=='turtles' else (' / '.join(p['heroes'])).replace('-',' ').upper()[:38]+preview
  txt(subtitle,x+36,y-2,6.7,'Body',GRAY)
 para('<b>Published roster:</b> 33 identities in the full-roster editions. <b>Preview:</b> Roll and the three Parodius pilots require the private development MMC5 build. The smaller original-roster cartridges contain only the original 14 identities.',M,91,PW,9.5,bottom=47);end()
def catalogue_index():
 begin('power-index','FIND AN ITEM','THE PICTURE INDEX.','Look up the picture, then read the effect for your character and mode.')
 for i,p in enumerate(CATALOGUES):
  x=M+(i%2)*276;y=624-(i//2)*61
  rect(x,y-25,264,54,white);rect(x+6,y-21,42,42,INK);fit(p['items'][0]['image'],x+9,y-18,36,36,3)
  name=p['title'].split(':')[0];link(name,'cat-'+p['key'],x+54,y+8,198,9)
  txt(str(len(p['items']))+' entries  /  PAGE '+str(TARGET_PAGES['cat-'+p['key']]),x+54,y-8,8.5,'Body',GRAY)
 box('SHARED PICTURES ARE LABELED','Some spells and stock weapons genuinely reuse a source icon. The guide shows that same image with each name and effect. A power-bar label or copy emblem is identified as such; it is not presented as a physical block pickup.',M,122,PW,71,TEAL,9.6);end()
def character(p):
 col=RED if p['preview'] else TEAL
 begin(p['key'],'CHARACTER FILE',p['name'],col=col)
 if p['preview']:pill('DEVELOPMENT PREVIEW',M,673,RED)
 top=646 if p['preview'] else 660
 para(p['intro'],M,top,343,11,bottom=571)
 rect(397,563,179,115,INK)
 n=len(p['heroes']);cw=179/n
 for i,k in enumerate(p['heroes']):
  if n==4:fit('hero-'+k,399+(i%2)*88,568+(1-i//2)*55,84,51,4)
  else:fit('hero-'+k,399+i*cw,571,cw-4,99,4)
 y=551
 for label,body in p['controls']:
  label=label.replace('Select at character select','Select on portrait')
  h=max(34,measure(label,123,9.3)+12,measure(body,386,9.6)+12)
  rect(M,y-h,PW,h-1,white)
  para(escape(label),M+10,y-7,123,9.3,font='Bold',color=TEAL,bottom=y-h+3)
  para(escape(body),M+144,y-7,386,9.6,bottom=y-h+3);y-=h
 assert y>=369,(p['key'],y)
 y=min(y-12,392)
 box('EASY',p['easy'],M,y,264,119,TEAL,9.5)
 box('HARD',p['hard'],312,y,264,119,RED,9.5)
 u=y-132;box('POWERUP PLAN',p['upgrade'],M,u,PW,85,INK,10)
 t=u-99;txt('TRY THIS',M,t,11,'Bold',TEAL);para(p['tip'],M+79,t+9,PW-79,10.1,bottom=t-48)
 catkey=p.get('catalogue') or 'common';cat=next(v for v in CATALOGUES if v['key']==catkey)
 # Three real pictures make each file useful before a reader follows the index.
 featured=cat['items'][:3]
 if p['key']=='sypha':featured=[cat['items'][i] for i in [0,4,5]]
 if p['key']=='alucard':featured=[cat['items'][i] for i in [0,7,8]]
 if p['key']=='parodius':featured=[cat['items'][i] for i in [5,6,7]]
 if p['key']=='mac':featured=[item for item in cat['items'][:2]]+[dict(image='mac-star',name='Uppercut star')]
 if p['key'] in ['pit','rygar','chip','turtles','scrooge','meta']:featured=cat['items'][:2]
 for i,it in enumerate(featured):
  x=M+i*116;rect(x,50,107,45,INK);fit(it['image'],x+4,54,31,37,2)
  para(escape(it['name']),x+39,84,64,7.8,color=white,bottom=53)
 link('PICTURES / PAGE '+str(TARGET_PAGES['cat-'+catkey])+' >','cat-'+catkey,403,65,173,9)
 end()
def catalogue_pages(group):
 rows=group['items'];chunk_size=math.ceil(len(rows)/math.ceil(len(rows)/12));chunks=[rows[i:i+chunk_size]for i in range(0,len(rows),chunk_size)]
 for ix,chunk in enumerate(chunks):
  key='cat-'+group['key']+('' if ix==0 else '-'+str(ix+1))
  title=group['title'];begin(key,'POWERUP CATALOGUE',title,('CONTINUED  /  ' if ix else '')+'Real game art. Names and effects are listed separately.',col=TEAL)
  para(group['note'],M,648,PW,10.1,bottom=585)
  stride=115 if len(chunk)<=8 else 98 if len(chunk)<=10 else 83
  height=stride-8
  for i,it in enumerate(chunk):
   x=M+(i%2)*276;top=568-(i//2)*stride
   rect(x,top-height,264,height,white);rect(x+7,top-66,50,57,INK);fit(it['image'],x+11,top-62,42,49,3)
   size=11 if len(it['name'])<27 else 10
   bottom=para(escape(it['name']),x+66,top-8,189,size,font='Bold',color=TEAL,bottom=top-35)
   body_size=10 if stride>=98 else 9
   para(escape(it['effect']),x+66,bottom-5,189,body_size,body_size*1.28,bottom=top-height+4)
  txt('IDENTIFY THE PICTURE  /  CHECK THE MODE  /  USE THE CORRECT BUTTON',M,52,8,'Bold',GRAY)
  end()
def field():
 begin('field','FIELD NOTES','A SMARTER FIRST RUN.','World 1-1 teaches the route; your hero changes the method.')
 image('mario-first-pipes',M,420,256,240);image('mario-gap-course',320,420,256,240)
 box('PIPES: SAVE YOUR EXTRA MOVE','Simon and Bass need a fresh second A. Sypha and Alucard commit to a jump direction. Use the helper platforms already provided on eligible routes; do not force a weak jump from a bad takeoff.',M,411,264,126,TEAL,10)
 box('GAPS: TAKE OFF WITH ROOM','Mario, Luigi and the SMB3 brothers need a runway. Pit spends limited flight; landing restores it. A ship can fly, but the world keeps scrolling while you decide.',312,411,264,126,RED,10)
 box('BLOCKS: WATCH WHAT ACTUALLY EMERGES','Many Hard rewards are separate physical items. The item must rise and reach you before it is collected. A buster pellet can need two hits on a brick. Pipes, spent blocks and the foundation are not ordinary breakable masonry.',M,268,PW,92,INK,10.1)
 box('WATER: RELEARN THE RHYTHM','Most ground heroes use repeated A strokes rather than a land jump. Samus can still use her ball tools; Pit\'s flower flight is disabled underwater. Frog form and ships have their own directional movement. Plan the exit before spending a special.',M,161,PW,92,TEAL,10.1)
 para('Practice one character and one mode at a time. If you use Cheats, reset before recording a normal clear.',M,54,PW,9,bottom=42);end()
def notes():
 begin('edition','ABOUT THIS EDITION','WHAT THIS GUIDE COVERS.','A player reference to implemented behavior, with honest version labels.')
 box('THE MAIN EDITION','The published full-roster MMC3 and MMC5 versions contain33 selectable identities, including Meta Knight. The original smaller cartridges contain14. A guide page does not add a character to an older cartridge.',M,645,PW,90,TEAL,10.4)
 box('FOUR PREVIEW GUESTS','Roll, Octopus, TwinBee and Pentarou require the private development MMC5 build. Their controls and items work as described. Dedicated audio, original Parodius death effects, substantial lag/dropout and final campaign checks still need work.',M,540,PW,101,RED,10.4)
 txt('BUILT FROM THE GAME',M,412,16,'Display',TEAL)
 para('Character portraits are real selection previews. Item pictures come from the installed NES graphics and their actual sprite records, or from isolated rendered item captures. Pixel art is enlarged with hard edges. Shared pictures, world-palette examples, copy emblems and power-bar labels are explicitly identified.',M,390,PW,10.5,bottom=315)
 txt('WHAT WAS LEFT OUT',M,288,16,'Display',TEAL)
 para('Planned moves are not written as completed features. This guide does not promise perfect source-game physics or audio for every guest, a complete original-game inventory, every-level compatibility, or a finished final playthrough certification. In particular, Mike\'s original utility magic and a turtle subweapon-drop inventory are not implemented.',M,266,PW,10.5,bottom=190)
 txt('CREDITS & SOURCE RECORD',M,164,16,'Display',TEAL)
 para('Super Mario Bros., the guest characters and their artwork belong to their respective creators. This is an unofficial fan-project guide inspired by classic game magazines. The editable pack includes the source/art mapping, exact build hashes, item-image manifest and coverage audit. It contains no game ROMs or redistributed commercial fonts.',M,142,PW,10.3,bottom=62)
 end()
def main():
 global c
 register_fonts();c=canvas.Canvas(str(PDF),pagesize=(W,H),pageCompression=1,invariant=1)
 c.setTitle('SMB Crossover - Player\'s Guide');c.setAuthor('SMB Crossover fan project');c.setSubject('33-character edition with4 marked development previews. Illustrated controls and powerup reference.')
 cover();start();modes();directory();catalogue_index()
 for p in FILES:character(p)
 for group in CATALOGUES:catalogue_pages(group)
 field();notes();c.save()
 rec=dict(pdf_sha256=hashlib.sha256(PDF.read_bytes()).hexdigest(),pages=PAGE_META,identity_count=len(IDENTITIES),character_files=len(FILES),catalogues=len(CATALOGUES),catalogue_entries=sum(len(v['items'])for v in CATALOGUES),layout_checks=CHECKS,links=LINKS)
 (QA/'layout-proof.json').write_text(json.dumps(rec,indent=2)+'\n')
 print(json.dumps({k:rec[k] for k in ['pdf_sha256','identity_count','character_files','catalogues','catalogue_entries']}));print('Pages',len(PAGE_META),'bytes',PDF.stat().st_size)
if __name__=='__main__':main()
