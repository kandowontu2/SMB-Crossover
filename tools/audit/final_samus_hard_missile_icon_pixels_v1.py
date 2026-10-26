"""Read-only source/OAM/actual-RGB attribution of the sampled missile HUD icon."""
from pathlib import Path
import argparse,collections,csv,hashlib,json,sys,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from final_samus_hard_gallery_source_v1 import D,ROOT,PARENT,SHA
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 n=D/'current3b112-samus-hard-outline-ready-v2/native';b=scoped_load(n/'candidate.nes');rom=b['raw'];assert sha(n/'candidate.nes')==SHA;chrbase=16+rom[4]*16384
 art=address(b,'AV_ART_SAMUSPICKUP7');fam=rom[location(b,'AvArtFamilies')+art];page=rom[location(b,'AvPhysicalBanks')+fam]|1
 ptr=rom[location(b,'AvArtRightLo')+art]+256*rom[location(b,'AvArtRightHi')+art];bank=rom[location(b,'AvArtBanks')+art];at=16+bank*8192+ptr%8192;record=list(rom[at:at+rom[at]+1]);assert(art,page,ptr,bank)==(84,229,52744,21)
 dmas=[]
 for line in(n/'ability-dma-epochs.jsonl').open():
  q=json.loads(line)
  if q['kind']=='completed-DMA-before-render-enable':dmas.append(q)
 raw=(n/'actual-ppu.argb').open('rb');results=[];sheet=Image.new('RGB',(4*272,2*300),(32,32,32));draw=ImageDraw.Draw(sheet)
 for k,frame in enumerate([1211,1230,1246,1328,1329,1368,1437,1476]):
  raw.seek((frame-1)*245760);data=raw.read(245760);im=Image.frombytes('RGBA',(256,240),data,'raw','BGRA').convert('RGB');q=next(q for q in reversed(dmas)if q['complete']['frame']<=frame)
  parts=[]
  for i in range(0,256,4):
   y,t,attr,x=q['hardware'][i:i+4]
   if t in[55,57,59,61,63]and attr&3==3 and x in[183,191,199]and y in[247,7]:parts.append(dict(slot=i//4,y=y,tile=t,attr=attr,x=x))
  mapping=collections.defaultdict(set);samples=[]
  for s in parts:
   for y in range(16):
    screenY=s['y']+1+y
    if screenY>=240:continue
    sy=15-y if s['attr']&128 else y
    for x in range(8):
     sx=7-x if s['attr']&64 else x;at=chrbase+page*1024+(s['tile']&254)*16%1024+sy//8*16+sy%8
     v=((rom[at]>>(7-sx))&1)|(((rom[at+8]>>(7-sx))&1)<<1)
     if not v:continue
     rgb=im.getpixel((s['x']+x,screenY));mapping[v].add(rgb);samples.append((s['x']+x,screenY,v,rgb))
  coherent=bool(samples)and all(len(z)==1 for z in mapping.values())and len({next(iter(z))for z in mapping.values()})==len(mapping)
  colors={str(v):list(z)for v,z in mapping.items()};results.append(dict(actual_PPU=frame,actual_raw_sha256=hashlib.sha256(data).hexdigest(),complete_DMA=q['id'],DMA_actual_start=q['start'],DMA_actual_complete=q['complete'],source_page=page,source_parts=parts,opaque_samples=len(samples),source_pattern_RGB_classes=colors,coherent_source_pattern=coherent))
  x=k%4*272;y=k//4*300;sheet.paste(im,(x,y+48));draw.text((x+2,y+1),f'Actual PPU{frame} / DMA{q["id"]}',fill='white');draw.text((x+2,y+15),f'Page229 opaque{len(samples)} coherent{coherent}',fill='white');draw.text((x+2,y+29),'Source classes; physical registers not dumped',fill='white')
 sheet.save(a.output/'actual-icon-frames.png')
 # Reconstruct the original SWF frame through the pinned existing extractor.
 sys.path.insert(0,str(ROOT/'tools/reference'));import build_remaining_art as gen
 from prepare_crossover import frames
 items=list(ET.parse(ROOT/'reference/crossover2/main.xml').getroot().iter('item'));symbols={}
 for t in items:
  if t.get('type')in('SymbolClassTag','ExportAssetsTag'):
   ids,names=t.find('tags'),t.find('names')
   if ids is not None and names is not None:symbols.update({name.text:i.text for i,name in zip(ids,names)})
 sprites={i.get('spriteId'):i for i in items if i.get('type')=='DefineSpriteTag'};source_sheet=next((ROOT/'reference/crossover2/images').glob('*_Samus000.png'));original=gen.extract(frames(sprites[symbols['SamusPickup']]),27,Image.open(source_sheet).convert('RGBA'))[6];original.save(a.output/'pinned-SamusPickup7.png')
 preview=Image.new('RGB',(5*192,192),(128,128,255));preview.paste(original.convert('RGB').resize((192,192),Image.Resampling.NEAREST),(0,0));dd=ImageDraw.Draw(preview);dd.text((2,2),'Original SWF frame7 (2x)',fill='white')
 # Actual 3b packed CHR, using the generator's declared fixed palette3.
 pal={1:(0,0,0),2:(252,216,168),3:(164,80,0)};expected=Image.new('RGB',(96,96),(128,128,255))
 for i in range(1,len(record),4):
  tile,attr,dy,dx=record[i:i+4];dy=dy-256 if dy>=128 else dy;dx=dx-256 if dx>=128 else dx
  for y in range(16):
   sy=15-y if attr&128 else y
   for x in range(8):
    sx=7-x if attr&64 else x;at=chrbase+page*1024+(tile&254)*16%1024+sy//8*16+sy%8;v=((rom[at]>>(7-sx))&1)|(((rom[at+8]>>(7-sx))&1)<<1)
    if v:expected.putpixel((48+dx+x,48+dy+y),pal[v])
 preview.paste(expected.resize((192,192),Image.Resampling.NEAREST),(192,0));dd.text((194,2),'Actual3b CHR + fixedpal3',fill='white')
 for k,frame in enumerate([1246,1328,1368]):
  raw.seek((frame-1)*245760);im=Image.frombytes('RGBA',(256,240),raw.read(245760),'raw','BGRA').convert('RGB');crop=im.crop((176,0,208,32)).resize((192,192),Image.Resampling.NEAREST);preview.paste(crop,((k+2)*192,0));dd.text(((k+2)*192+2,2),f'Actual HUD{frame} 6x',fill='white')
 preview.save(a.output/'source-and-actual-icon.png')
 proof=dict(ROM_sha256=SHA,read_only=True,native_run=False,source_art=art,source_pointer=ptr,source_bank=bank,source_family=fam,source_physical_page=page,source_record=record,source_palette_policy=gen.PALS[3],results=results,all_sampled_patterns_coherent=all(q['coherent_source_pattern']for q in results),scope='Actual RGB compared to actual ROM2bpp pattern classes at committed hardware OAM locations. Source fixed-world palette is explicitly brown/peach/black; no actual physical CHR/register/palette dump exists in this run, so register-level causal closure is not claimed. Original source frame and quantization preview are read-only; no candidate art/palette changed.',bindings=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in[Path(__file__),n/'ability-dma-epochs.jsonl',n/'actual-ppu.argb',n/'candidate.nes',ROOT/'tools/reference/build_remaining_art.py',ROOT/'reference/crossover2/main.xml',source_sheet]])
 put(a.output/'proof.json',proof);print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),all_sampled_patterns_coherent=proof['all_sampled_patterns_coherent'],results=[dict(actual_PPU=q['actual_PPU'],opaque=q['opaque_samples'],coherent=q['coherent_source_pattern'],parts=len(q['source_parts']))for q in results]),indent=2))
if __name__=='__main__':main()
