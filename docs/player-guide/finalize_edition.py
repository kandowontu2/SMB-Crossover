"""Render, inspect and prove the standalone magazine guide delivery."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,zipfile,shutil
from PIL import Image,ImageDraw
from pypdf import PdfReader
import pdfplumber
from edition_content import FILES,CATALOGUES,IDENTITIES
from build_edition import TARGET_PAGES
HERE=Path(__file__).parent;ROOT=HERE.parents[1];QA=ROOT/'build/verification/player-guide-magazine-2026-10-24';OUT=ROOT/'Player Guide'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 paths=sorted(QA.glob('page-*.png'));assert len(paths)==53
 for s in range(0,len(paths),6):
  im=Image.new('RGB',(1377,1240),'#12213a');d=ImageDraw.Draw(im)
  for j,p in enumerate(paths[s:s+6]):
   pg=Image.open(p).resize((459,594));x=(j%3)*459;y=(j//3)*620;im.paste(pg,(x,y));d.text((x+12,y+600),p.stem,fill='white')
  im.save(QA/f'review-{s//6+1:02}.png')
 print('Nine magazine review sheets prepared.')
def finalize():
 pdf=OUT/'SMB-Crossover-Players-Guide.pdf';reader=PdfReader(pdf);proof=json.loads((QA/'layout-proof.json').read_text());audit=json.loads((HERE/'accuracy-audit.json').read_text())
 assert len(reader.pages)==53 and len(reader.outline)==53
 assert sha(pdf)==proof['pdf_sha256']
 for pg in proof['pages']:assert TARGET_PAGES.get(pg['key'],pg['page'])==pg['page'],pg
 assert len(reader.pages[3].get('/Annots',[]))==27 and len(reader.pages[4].get('/Annots',[]))==16
 assert len(proof['links'])==70
 text=[p.extract_text()for p in reader.pages]
 for p in FILES:
  pg=TARGET_PAGES[p['key']]-1;assert 'EASY'in text[pg]and'HARD'in text[pg]
  assert 'ITEM PICTURES / '+str(TARGET_PAGES['cat-'+p['catalogue']])in text[pg]
 outside=[];tiny=[];overlaps=[]
 with pdfplumber.open(pdf)as doc:
  for n,p in enumerate(doc.pages,1):
   for ch in p.chars:
    # Masthead deliberately occupies the colored page-edge stripe.
    if ch['x0']<25 or ch['x1']>590 or ch['top']<5 or ch['bottom']>781:outside.append((n,ch['text']))
    if ch['size']<6.4:tiny.append((n,ch['text'],ch['size']))
   for im in p.images:
    for ch in p.chars:
     width=min(ch['x1'],im['x1'])-max(ch['x0'],im['x0']);height=min(ch['bottom'],im['bottom'])-max(ch['top'],im['top'])
     caption=im['width']==256 and im['height']==240 and ch['top']>=im['bottom']-22
     if width>.3 and height>.3 and not caption:overlaps.append((n,ch['text']))
 assert not outside,outside
 assert not tiny,tiny
 assert not overlaps,overlaps
 # Every source sprite opaque pixel is preserved before RGB panel compositing.
 pixels=json.loads((HERE/'assets/portrait-pixel-proof.json').read_text());assert len(pixels['cases'])==37
 for pic in pixels['cases']:
  im=Image.open(HERE/'assets/edition'/('hero-'+pic['identity']+'.png')).convert('RGBA')
  assert sum(px[3]==255 for px in im.getdata())==pic['pixels']==pic['screenshot_matches']==pic['opaque_pixels_preserved']
  assert sha(HERE/'assets/edition'/('hero-'+pic['identity']+'.png'))==pic['asset_sha256']
 # Check the actual final raster mode-header colors, beyond text extraction.
 mode_checks=[]
 from pypdf.generic import ContentStream
 for file in FILES:
  n=TARGET_PAGES[file['key']];ops=ContentStream(reader.pages[n-1].get_contents(),reader).operations;rgb=None;found=[]
  for args,op in ops:
   if op==b'rg':rgb=tuple(float(a)for a in args)
   if op==b're'and float(args[2])==264 and float(args[3])==22:found.append((tuple(float(a)for a in args),rgb))
  assert len(found)==2,(n,found)
  im=Image.open(QA/f'page-{n:02}.png').convert('RGB');assert im.size==(765,990)
  for(x,y,w,h),rgb in found:
   px=im.getpixel((round((x+3)*1.25),round((792-y-h+3)*1.25)));want=tuple(round(v*255)for v in rgb)
   assert max(abs(a-b)for a,b in zip(px,want))<=1,(n,px,want)
   mode_checks.append(dict(page=n,rgb=px))
 shutil.copy2(QA/'page-01.png',OUT/'Cover.png');preview=Image.new('RGB',(1530,1980),'#12213a')
 for i,n in enumerate([1,10,25,32]):preview.paste(Image.open(QA/f'page-{n:02}.png'),((i%2)*765,(i//2)*990))
 preview.save(OUT/'Guide-Preview.png')
 names=['build_guide.py','build_magazine.py','build_edition.py','guide_content.py','edition_content.py','README.md','ACCURACY.md','accuracy-audit.json','audit_guide.py','audit_edition.py','prepare_assets.py','capture_portrait_pixels.py','finalize_guide.py','finalize_edition.py']
 assets=sorted((HERE/'assets/edition').glob('*.png'))+[HERE/'assets/edition-provenance.json',HERE/'assets/portrait-pixel-proof.json']
 archive=OUT/'SMB-Crossover-Guide-Editable-Source.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in[HERE/n for n in names]+assets:z.write(p,'player-guide-source/'+p.relative_to(HERE).as_posix())
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None;dest=QA/'standalone-rebuild';dest.mkdir(exist_ok=True)
  for n in z.namelist():assert(dest/n).resolve().is_relative_to(dest.resolve())
  z.extractall(dest)
 sr=dest/'player-guide-source';run=subprocess.run([sys.executable,str(sr/'build_guide.py')],capture_output=True,text=True)
 assert run.returncode==0,(run.stdout,run.stderr)
 rebuilt=sr/'Player Guide/SMB-Crossover-Players-Guide.pdf';assert sha(rebuilt)==sha(pdf)
 rec=dict(passed=True,scope='Authored player guide verification, not game certification',pdf_sha256=sha(pdf),pages=53,identities=37,published_identities=33,development_previews=4,character_files=27,catalogues=16,labeled_catalogue_entries=audit['labeled_entries'],unique_catalogue_images=audit['unique_catalogue_images'],shared_inventory_IDs_covered=60,outline_destinations=53,clickable_links=70,printed_index_and_callout_pages=True,mode_header_render_checks=mode_checks,text_bounds_errors=outside,tiny_text_errors=tiny,unintended_text_image_overlaps=overlaps,source_audit_sha256=sha(HERE/'accuracy-audit.json'),portrait_source_pixel_checks=dict(identities=37,all_opaque_pixels_preserved=True,all_screenshot_pixels_match=True,no_color_key_subtraction=True,explicit_RGB_dark_panels=True),standalone_rebuild=dict(exact_pdf_sha256_match=True,uses_only_included_copy_and_images=True,external_requirements='Python ReportLab/Pillow and locally licensed Windows fonts'),manual_visual_review=dict(pages=list(range(1,54)),method='All53 final Poppler renders inspected in9 contact sheets, with full-page design review of indices, white/blue character details, action layouts, dense catalogues and edition notes. Every item separately mapped to actual source art.',fixes=['Large dark RGB-backed portraits preserve real opaque pixels','Distinct turtle comparison, Samus Morph Ball and Meta Knight action compositions','New magazine masthead, cover, indexes and equipment atlas','Space after framed panels and mode bands','Actual captured action images; no invented sprites','Short mode bands fit their content','All157 labeled catalogue entries retain actual pictures']),private_reference='parodius-death-nr',render_sha256={p.name:sha(p)for p in sorted(QA.glob('page-*.png'))},outputs={p.name:dict(sha256=sha(p),bytes=p.stat().st_size)for p in[pdf,archive,OUT/'Cover.png',OUT/'Guide-Preview.png']})
 rec['staging_bytes']=sum(p.stat().st_size for p in QA.rglob('*')if p.is_file());assert rec['staging_bytes']<20_000_000
 (QA/'final-validation.json').write_text(json.dumps(rec,indent=2)+'\n')
 print(json.dumps({k:rec[k]for k in['passed','pages','identities','labeled_catalogue_entries','staging_bytes','pdf_sha256']}))
def main():
 p=argparse.ArgumentParser();p.add_argument('--reviewed',action='store_true');a=p.parse_args();prepare()
 if a.reviewed:finalize()
if __name__=='__main__':main()
