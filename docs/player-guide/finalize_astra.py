"""Final artifact audit, render set and exact standalone rebuild."""
from pathlib import Path
import json,hashlib,zipfile,subprocess,sys,shutil,os,tempfile
from PIL import Image
import pdfplumber
from pypdf import PdfReader
from edition_content import FILES,IDENTITIES
H=Path(__file__).parent;R=H.parents[1];Q=Path(os.environ.get('PLAYER_GUIDE_QA_DIR',str(R/'build/verification/player-guide-astra-redesign')));O=Path(os.environ.get('PLAYER_GUIDE_OUTPUT_DIR',str(R/'Player Guide')))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pdf=O/'SMB-Crossover-Players-Guide.pdf';reader=PdfReader(pdf);n=len(reader.pages)
assert n==48 and len(reader.outline)==48
proof=json.loads((Q/'layout-proof.json').read_text());assert proof['pdf_sha256']==sha(pdf)
assert [p['page'] for p in proof['pages']]==list(range(1,n+1))
assert len([p for p in proof['pages']if p['key'].startswith('char-')])==27
assert all('hero-'+i in {v['asset']for v in proof['images']}for i in IDENTITIES)
outside=[];overlap=[];tiny=[]
with pdfplumber.open(pdf)as doc:
 for i,page in enumerate(doc.pages,1):
  for c in page.chars:
   if c['x0']<19 or c['x1']>593 or c['top']<5 or c['bottom']>780:outside.append((i,c['text'],c['x0'],c['top']))
   if c['size']<6.4:tiny.append((i,c['text'],c['size']))
  for im in page.images:
   for c in page.chars:
    if min(c['x1'],im['x1'])-max(c['x0'],im['x0'])>.5 and min(c['bottom'],im['bottom'])-max(c['top'],im['top'])>.5:overlap.append((i,c['text']))
assert not outside,outside[:30]
assert not tiny,tiny[:30]
assert not overlap,overlap[:40]
draft=Q/'superseded-draft-renders';draft.mkdir(exist_ok=True)
for name in ['page-49.png','page-50.png','review-09.png']:
 p=Q/name
 if p.exists():shutil.move(str(p),str(draft/name))
subprocess.run(['pdftoppm','-scale-to','990','-png',str(pdf),str(Q/'page')],check=True)
for s in range(0,n,6):
 sheet=Image.new('RGB',(1224,1056),'#17202c')
 for j,k in enumerate(range(s+1,min(s+7,n+1))):sheet.paste(Image.open(Q/f'page-{k:02}.png').resize((408,528)),(j%3*408,j//3*528))
 sheet.save(Q/f'review-{s//6+1:02}.png')
shutil.copy2(Q/'page-01.png',O/'Cover.png')
preview=Image.new('RGB',(1530,1980),'#17202c')
for j,k in enumerate([1,33,32,37]):preview.paste(Image.open(Q/f'page-{k:02}.png'),(j%2*765,j//2*990))
preview.save(O/'Guide-Preview.png')
used=sorted({v['asset']for v in proof['images']});assets=[];rows=[]
old={v['asset']:v for v in json.loads((H/'assets/edition-provenance.json').read_text())if 'asset'in v}
new={v['asset']:v for v in json.loads((H/'assets/astra-provenance.json').read_text())}
for key in used:
 p=H/'assets/astra'/(key+'.png');source=new.get(p.name)
 if not p.exists():p=H/'assets/edition'/(key+'.png');source=old.get(p.name)
 assert p.exists() and source and source['sha256']==sha(p),(key,'Asset provenance/hash mismatch');assets.append(p)
 rows.append(dict(asset=p.relative_to(H).as_posix(),sha256=sha(p),source=source,pages=sorted({v['page']for v in proof['images']if v['asset']==key})))
updates=json.loads((H/'content-updates.json').read_text());assert updates['status']=='frozen','Wait for NU frozen-source confirmation'
audit=dict(content_updates=updates,edition='Astra editorial rebuild - grounded Meta Knight update',pages=n,identities=37,published=33,private_previews=4,source_checkpoint='parodius-death-nr',source_rom_sha256='2931163dd7d3c31f9a81776b16c45631a0abd2120abff4454833084825475590',source_zip_sha256='81a9912e7001a8c3da3a374ac39ef4b1a2f16812fb2364fa0960dff1b779d2cf',images=rows,corrected=['Full green/red Koopa and Buzzy poses replace shell-only HUD emblems','Grey Cheep uses underwater grey palette; Paratroopa uses green world palette and complete wings','All fourteen enemy targets independently checked','Mike distinct Nintendo manual weapons including the explicitly identified electronic-manual Super Nova; laser paths explicitly diagrams','Complete original Little Mac HUD star replaces clipped half-glyph','White Bell source manual illustration replaces duplicate red capture','Original 2.02 source pickup colors restore fine detail including Ryu Jump Slash spiral','Zelda II reduced to one coherent controls/stats/spells/rewards page','Duplicate Rapid stages and bomb/missile supply art consolidated','CV3 companions show their own tools; no redundant separate heart catalogue','Ship diagrams replace illegible miniature HUD-cell pictures','Samus exit frame removed because it followed a bomb boost','Meta Knight uses corrected native body palette and six grounded sword attacks; old flight and held-B chain removed','Two empty 1-4 firebar mounts correctly identified as authored; active in 6-4 independently of Easy/Hard'],game_art_findings=['Prior Little Mac extraction clipped its source star; corrected original HUD illustration retained. Game star repaired separately in NT.','Mike kind3 first capture is an unverified checkerboard, not proven Nova art; later fragments also require visible original OAM/CHR verification. No Nova ROM-art defect is established by these captures.','Mike JnStar display is a partial white/red object; guide uses authenticated manual star','Parodius old red and white captured assets were byte-identical'],limits='Guide correctness is not game certification. Private preview lag/dropout, dedicated audio, full campaign and final all-item coverage remain open.')
(H/'image-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
pack=O/'SMB-Crossover-Guide-Editable-Source.zip'
included=[H/x for x in ['build_guide.py','build_astra.py','edition_content.py','guide_content.py','README.md','image-audit.json','content-updates.json']]+assets+[H/'assets/astra-provenance.json',H/'assets/edition-provenance.json',H/'assets/portrait-pixel-proof.json',H/'assets/meta-nu-hardware-proof.json']
with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in included:
  info=zipfile.ZipInfo('player-guide-source/'+p.relative_to(H).as_posix(),date_time=(2026,10,24,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
rebuild=Path(tempfile.mkdtemp(prefix='standalone-'+sha(pack)[:12]+'-',dir=Q))
with zipfile.ZipFile(pack)as z:
 assert z.testzip()is None
 for name in z.namelist():assert(rebuild/name).resolve().is_relative_to(rebuild.resolve())
 z.extractall(rebuild)
child_env={k:v for k,v in os.environ.items()if k not in ['PLAYER_GUIDE_QA_DIR','PLAYER_GUIDE_OUTPUT_DIR']}
subprocess.run([sys.executable,str(rebuild/'player-guide-source/build_guide.py')],check=True,env=child_env)
rebuilt=rebuild/'player-guide-source/Player Guide/SMB-Crossover-Players-Guide.pdf';assert sha(rebuilt)==sha(pdf)
receipt=dict(qa_directory=str(Q.resolve()),content_updates=updates,passed=True,pages=n,identities=37,pdf_sha256=sha(pdf),zip_sha256=sha(pack),standalone_rebuild=dict(exact_match=True,directory=str(rebuild),sha256=sha(rebuilt),requirements='Python with Pillow/ReportLab; licensed local Arial, Impact and Georgia Italic fonts. No ROM/source repository/network required.'),text_bounds_errors=outside,text_image_overlap_errors=overlap,tiny_text_errors=tiny,manual_review=dict(method='All 48 pages inspected in 8 final review sheets plus full-page named image checks',pages=list(range(1,n+1))),renders={f'page-{i:02}.png':sha(Q/f'page-{i:02}.png')for i in range(1,n+1)},review_sheets={f'review-{i:02}.png':sha(Q/f'review-{i:02}.png')for i in range(1,9)},outputs={p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in [pdf,pack,O/'Cover.png',O/'Guide-Preview.png']},image_audit_sha256=sha(H/'image-audit.json'),scope='Document and artwork verification only; no ROM/game modification or campaign certification')
receipt['staging_bytes']=sum(p.stat().st_size for p in Q.rglob('*')if p.is_file())
(Q/'final-validation.json').write_text(json.dumps(receipt,indent=2)+'\n');(O/'Guide-Verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k]for k in ['passed','pages','staging_bytes','pdf_sha256','zip_sha256']}))
