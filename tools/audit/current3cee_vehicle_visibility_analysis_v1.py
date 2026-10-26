"""Bound physical first-eight omissions to actual OAM/CHR/flags and RGB."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,json,traceback
from PIL import Image,ImageDraw
SHA='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def lines(p):return[json.loads(l)for l in p.open()]
signed=lambda v:v if v<128 else v-256
TARGETS={'octopus':[939,1423,1907,2150,2151,2160,2392,2876,3360], 'sophia':[948,1523,2037,2551,3063,3064,3065,3066,3067,3580]}
CONTROLS={'octopus':[939,2392,2876], 'sophia':[948,1523,2037,2551]}
class Probe:
 def __init__(self,root,case,raw):
  self.root=root;self.native=root/case/'native';self.case=case;self.raw=raw
  self.frames={(z['phase'],z['ppu']['frame']):z for z in lines(self.native/'visibility-frames.jsonl')}
  self.pubs={z['id']:z for z in lines(self.native/'visibility-publications.jsonl')};self.bus=lines(self.native/'visibility-bus.jsonl')
  self.dmas={z['data']['id']:z['data']for z in self.bus if z['kind']=='DMA-start'}
  self.physical={int(f.stem.split('-')[-1]):f.read_bytes()for f in self.native.glob('physical-chr-*.bin')}
 def sample(self,frame):
  s=self.frames['startFrame',frame];e=self.frames['endFrame',frame];pub=self.pubs[e['publication']];b=pub['body'];assert b
  assert s['publication']==e['publication']and s['DMA']==e['DMA']
  assert s['hardware']==e['hardware']==pub['oam']
  assert s['chr_banks'][:8]==e['chr_banks'][:8]and s['ctrl']==e['ctrl']and s['mask']==e['mask']
  assert s['DMA_writes']==e['DMA_writes']==256 and s['DMA_exact']and e['DMA_exact']
  assert s['DMA_complete']['cpu']<s['ppu']['cpu']<e['ppu']['cpu']and pub['ppu']['cpu']<=s['DMA_ppu']['cpu']
  assert not any(z['kind']in['DMA-start','direct-OAMDATA']and s['ppu']['cpu']<z['ppu']['cpu']<e['ppu']['cpu']for z in self.bus)
  assert s['palette']==e['palette']and s['mask']&16 and s['ctrl']&32
  assert b['vflip']==0 and b['header_admitted']and b['length']//4==len(b['indices'])
  record=bytes.fromhex(b['record']);at=16+b['record_bank']*8192+b['pointer']%8192
  assert self.raw[at:at+len(record)]==record
  parts=[record[i:i+4]for i in range(1,len(record),4)];expected=[]
  for tile,attr,dy,dx in reversed(parts):
   x,y=b['x']+signed(dx),b['y']+signed(dy);a=((b['attr']&252)|attr)if attr&4 else b['attr']|attr
   assert 0<=x<256 and 256<=y<512,'Selected sample is fully onscreen'
   expected.append(bytes([y&255,tile,a&243,x]).hex())
  assert expected==b['actual_parts']
  o=bytes.fromhex(e['hardware']);oam=[list(o[i:i+4])for i in range(0,256,4)]
  assert [bytes(oam[i]).hex()for i in b['indices']]==b['actual_parts']
  palette=bytes.fromhex(e['palette']);im=Image.open(self.native/'frames'/f'{frame:06d}.png').convert('RGB')
  return dict(frame=frame,start=s,end=e,pub=pub,body=b,oam=oam,palette=palette,image=im,banks=e['chr_banks'][:8])
 def pattern(self,q,tile,row,x):
  at=(tile&1)*4096+(tile&254)*16+(row//8)*16+row%8;page=q['banks'][at//1024];offset=at%1024
  data=self.physical[page];lo,hi=data[offset],data[offset+8]
  return((lo>>(7-x))&1)|(((hi>>(7-x))&1)<<1),dict(page=page,offset=offset,lo=lo,hi=hi,bit=7-x)
 def render(self,q,limit):
  out={};selection={}
  for y in range(240):
   allslots=[i for i,s in enumerate(q['oam'])if s[0]<240 and s[0]+1<=y<s[0]+17];slots=allslots[:limit];selection[y]=(allslots,slots)
   for i in slots:
    top,tile,attr,left=q['oam'][i];row=y-top-1;row=15-row if attr&128 else row
    for dx in range(8):
     x=left+dx
     if x>=256 or(x<8 and not(q['end']['mask']&4))or(x,y)in out:continue
     v,source=self.pattern(q,tile,row,7-dx if attr&64 else dx)
     if not v:continue
     pal=0x10+(attr&3)*4+v;out[x,y]=dict(slot=i,body=i in q['body']['indices'],tile=tile,attr=attr,value=v,palette_address=pal,NES_color=q['palette'][pal]&63,pattern=source)
  return out,selection
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 try:
  ready=get(a.packet/'readiness.json');execution=get(a.packet/'execution.json');assert execution['passed']and execution['worker_released'];raw=Path(ready['rom']).read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA
  reports=[];bindings={str(Path(__file__).resolve()):sha(__file__),str(a.packet/'readiness.json'):sha(a.packet/'readiness.json'),str(a.packet/'execution.json'):sha(a.packet/'execution.json')}
  for case,frames in TARGETS.items():
   probe=Probe(a.packet,case,raw);samples={f:probe.sample(f)for f in sorted(set(frames+CONTROLS[case]))};cal=defaultdict(Counter)
   for f in CONTROLS[case]:
    q=samples[f];limited,_=probe.render(q,8)
    for (x,y),v in limited.items():
     if y>=40 and not(v['attr']&32):cal[(q['end']['mask']&225,v['NES_color'])][q['image'].getpixel((x,y))]+=1
   colors={key:c.most_common(1)[0][0]for key,c in cal.items()if sum(c.values())>=5 and c.most_common(1)[0][1]/sum(c.values())>=.98}
   calibration=[dict(mask=key[0],NES_color=key[1],RGB=list(c.most_common(1)[0][0]),samples=sum(c.values()),majority=c.most_common(1)[0][1],accepted=key in colors)for key,c in sorted(cal.items())]
   rows=[]
   sheet=Image.new('RGB',(1024,260*((len(frames)+3)//4)),'#202020');draw=ImageDraw.Draw(sheet)
   for index,f in enumerate(frames):
    q=samples[f];eight,selection=probe.render(q,8);full,_=probe.render(q,64);body8={xy:v for xy,v in eight.items()if v['body']};body64={xy:v for xy,v in full.items()if v['body']};witness=[];unknown=0;contradictions=[]
    sky=Counter(q['image'].getdata()).most_common(1)[0][0];heldout_match,heldout_bad=0,[]
    for xy,v in eight.items():
     key=(q['end']['mask']&225,v['NES_color'])
     if xy[1]>=40 and not(v['attr']&32)and key in colors:
      if q['image'].getpixel(xy)==colors[key]:heldout_match+=1
      else:heldout_bad.append(dict(x=xy[0],y=xy[1],slot=v['slot'],actual=list(q['image'].getpixel(xy)),expected=list(colors[key])))
    for xy,v in body64.items():
     if xy in body8:continue
     y=xy[1];allslots,first8=selection[y]
     # Only a real body sprite outside the actual first8 can be an omission.
     if v['slot']in first8:continue
     assert len(first8)==8 and v['slot']in allslots
     key=(q['end']['mask']&225,v['NES_color']);present=eight.get(xy);actual=q['image'].getpixel(xy)
     expected=colors.get((q['end']['mask']&225,present['NES_color']))if present else sky
     own=colors.get(key)
     if own is None or expected is None or(v['attr']&32):unknown+=1;continue
     if own==expected:continue
     detail=dict(x=xy[0],y=xy[1],body_slot=v['slot'],tile=v['tile'],attr=v['attr'],opaque_value=v['value'],source_pattern=v['pattern'],source_NES_color=v['NES_color'],source_RGB=list(own),actual_RGB=list(actual),limited_RGB=list(expected),first_eight_slots=first8,all_row_slots=allslots,first_eight_owners=['body'if i in q['body']['indices']else'pre-body actor/projectile'if(((i*4-q['body']['rotation'])&255)<q['body']['logical_start'])else'world/score/other'for i in first8])
     if actual==expected:witness.append(detail)
     else:contradictions.append(detail)
    assert not heldout_bad,dict(case=case,frame=f,admitted_pixel_mismatches=heldout_bad[:12])
    assert not contradictions,dict(case=case,frame=f,omission_pixel_mismatches=contradictions[:12])
    b=q['body'];r=dict(actual_PPU_frame=f,publication=q['pub']['id'],DMA=q['end']['DMA'],actual_start=q['start']['ppu'],actual_end=q['end']['ppu'],DMA_started=q['start']['DMA_ppu'],DMA_completed=q['start']['DMA_complete'],hardware_exact_source256=True,completed_DMA_writes=256,no_OAM_change_between_start_and_end=True,actual_pattern_pages=q['banks'],palette=q['end']['palette'],body_record_bank=b['record_bank'],body_record_pointer=b['pointer'],body_record=b['record'],body_tuple_projection_exact=True,body_part_count=b['length']//4,body_physical_indices=b['indices'],body_wraps=any(y<x for x,y in zip(b['indices'],b['indices'][1:])),flags_at_body=b['ram'],flags_at_publication=q['pub']['ram'],flags_at_DMA=probe.dmas[q['end']['DMA']]['ram'],source_body_pixels_unlimited=len(body64),model_body_pixels_first8=len(body8),RGB_verified_admitted_sprite_pixels=heldout_match,RGB_verified_omitted_body_pixels=len(witness),uncalibrated_omission_pixels=unknown,omission_witnesses=witness,actual_whole_PPU_path=str(probe.native/'frames'/f'{f:06d}.png'),actual_whole_PPU_sha256=sha(probe.native/'frames'/f'{f:06d}.png'))
    rows.append(r);x,y=index%4*256,index//4*260;sheet.paste(q['image'],(x,y+20));draw.text((x,y),case+' '+str(f)+' body '+str(len(body8))+'/'+str(len(body64)),fill='white')
    bindings[r['actual_whole_PPU_path']]=r['actual_whole_PPU_sha256']
   sheet.save(a.output/(case+'-actual-PPU.png'));put(a.output/(case+'-attribution.json'),dict(passed=True,case=case,calibration_frames=CONTROLS[case],calibration=calibration,findings=rows,limits='Bounded hardware OAM8-sprite admission/pattern/opaqueRGB witnesses. No source/art/priority repair, all-frame fidelity or global visibility verdict. Exact source bodies can still be unreadable under this policy.'))
   reports.append(dict(case=case,frames=len(rows),verified_omission_pixels=sum(z['RGB_verified_omitted_body_pixels']for z in rows),admitted_pixel_checks=sum(z['RGB_verified_admitted_sprite_pixels']for z in rows),path=str(a.output/(case+'-attribution.json')),sha256=sha(a.output/(case+'-attribution.json'))))
   for directory in[a.packet/case,probe.native]:bindings.update({str(f):sha(f)for f in directory.iterdir()if f.is_file()and(f.suffix in['.json','.jsonl','.bin']or f.name=='direct-frame-index.csv')})
  put(a.output/'bindings.json',bindings);put(a.output/'proof.json',dict(passed=True,ROM_sha256=SHA,offline_only=True,native_workers_released=True,cases=reports,bindings_sha256=sha(a.output/'bindings.json'),body_visibility_problem_remains_open=True,no_game_changes=True,source_owner='DrawAllMetasprites reserves body after weapon/actor list; KbOamPriority rotates the entire used hardwareOAM ring. Source palettes/records are intact; observed late/wrapped bodyparts can fall outside physicalfirst8.',scope='Two exact current-ROM read-only probes and19selected physical pattern/RGB attribution epochs only. No repair or extra native scope.'))
  print(json.dumps(dict(passed=True,cases=reports,proof_sha256=sha(a.output/'proof.json')),indent=2))
 except BaseException as error:
  put(a.output/'failure.json',dict(passed=False,offline_only=True,error=repr(error),traceback=traceback.format_exc(),tool_sha256=sha(__file__),native_untouched=True));(a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise
if __name__=='__main__':main()
