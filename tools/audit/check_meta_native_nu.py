from pathlib import Path
import csv,json,hashlib
from PIL import Image,ImageDraw
import argparse
args=argparse.ArgumentParser();args.add_argument('--rom',type=Path,required=True);args.add_argument('--source',type=Path,default=Path("C:/NES/Kirby's Adventure (USA) (Rev 1).nes"));args.add_argument('--oracle',type=Path,required=True);args.add_argument('--output',type=Path,required=True);args.add_argument('--runs',nargs='+',required=True);a=args.parse_args();O=a.output;O.mkdir(parents=True,exist_ok=True);oracle=json.loads(a.oracle.read_text());source=a.source.read_bytes();assert hashlib.sha256(source).hexdigest()==oracle['source_sha256'];original_chr=source[16+524288:];rom=a.rom.read_bytes();assert hashlib.sha256(rom).hexdigest()==oracle['ROM_sha256'];PORT_CHR=rom[16+1048576:]
assert all(r['descriptor_forward']for r in oracle['original_hardware_order'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def pixels(raw,attr):
 for y in range(16):
  sy=15-y if attr&128 else y;a=sy//8*16+sy%8
  for x in range(8):
   bit=x if attr&64 else 7-x;q=(raw[a]>>bit&1)+2*(raw[a+8]>>bit&1)
   if q:yield x,y,q

def expected(pose):
 out={}
 for p in oracle['poses'][pose]['native']:
  raw=original_chr[0xa4*1024+(p['tile']-128)*16:0xa4*1024+(p['tile']-128)*16+32]
  colors=[0x36,0x14,0x0f]if p['attr']&3==3 else[0x30,0x27,0x16]
  for x,y,q in pixels(raw,p['attr']):out.setdefault((p['dx']+8+x,p['dy']+25+y),colors[q-1])
 return out
reports={};first=None
for run in a.runs:
 mode,folder=run.split('=',1);folder=Path(folder);rows=list(csv.DictReader((folder/'hardware.csv').open()));oam=(folder/'oam.bin').read_bytes();palettes=(folder/'palettes.bin').read_bytes();assert len(oam)==len(rows)*256 and len(palettes)==len(rows)*32
 mapping={int(p.stem.split('-')[-1]):p.read_bytes()for p in folder.glob('physical-*.bin')}
 for page,raw in mapping.items():assert raw==PORT_CHR[page*1024:page*1024+1024]
 bad=[];part_checks=0;all_visible={};maxline=0;examples={}
 for j,row in enumerate(rows):
  pose=int(row['pose']);p=oracle['poses'][pose];ox=int(row['originX']);oy=int(row['originY'])-256;atr=int(row['attribute']);page=int(row['page0']);raw=oam[j*256:(j+1)*256];pal=palettes[j*32:(j+1)*32];assert page==p['page']and list(pal[17:20])==[0x36,0x14,0x0f]and list(pal[25:28])==[0x16,0x30,0x27]
  records=[tuple(raw[i:i+4])for i in range(0,256,4)];expected_records=[]
  for index,a in enumerate(p['parts']):
   x=(ox+a['dx'])%65536;y=oy+a['dy'];attr=(a['attr']|atr)&0xf3
   if x<256 and 0<=y<240:expected_records.append((index,(y,a['tile'],attr,x)))
  matched=[];used=set()
  for index,quad in expected_records:
   candidates=[i for i,q in enumerate(records)if q==quad and i not in used];assert candidates,(mode,j,row,quad,'Missing actual Meta part');slot=candidates[0];used.add(slot);matched.append((slot,index,quad));part_checks+=1
  matched.sort();actual={};lines={};eligible={i:False for i,_ in expected_records}
  for slot,q in enumerate(records):
   y,t,attr,x=q
   if y>=240:continue
   winners=set()
   for yy in range(y+1,min(240,y+17)):
    if lines.get(yy,0)<8:winners.add(yy)
    lines[yy]=lines.get(yy,0)+1;maxline=max(maxline,lines[yy])
   if slot not in used:continue
   index=next(v[1]for v in matched if v[0]==slot);data=mapping[page][t*16:t*16+32]
   for xx,yy,qcolor in pixels(data,attr):
    color=pal[16+(attr&3)*4+qcolor];actual.setdefault((x-ox+xx,y-oy+yy),color)
    if y+1+yy in winners:eligible[index]=True
  for i,value in eligible.items():
   key=(pose,int(row['face']),i);all_visible[key]=all_visible.get(key,False)or value
  want=expected(pose);diff={xy:(want.get(xy),actual.get(xy))for xy in set(want)|set(actual)if want.get(xy)!=actual.get(xy)}
  if diff:
   entry=dict(row=j+1,wall=int(row['wall']),pose=pose,face=int(row['face']),combo=int(row['combo']),tick=int(row['tick']),different_pixels=len(diff),actual_descriptor_indices_by_hardware_slot=[(s,i)for s,i,q in matched]);bad.append(entry)
   if first is None:first=dict(**entry,mode=mode,want=want,actual=actual,diff=diff,folder=str(folder));first_raw=raw;first_pal=pal
   examples.setdefault((pose,int(row['face'])),entry)
 report=dict(rows=len(rows),all_parts_present=True,actual_part_checks=part_checks,physical_pages=sorted(mapping),physical_bytes_exact_linked_ROM=True,body_palette_exact=True,sword_declared_palette=True,priority_mismatch_frames=len(bad),priority_mismatch_poses=sorted({v['pose']for v in bad}),first_mismatches=bad[:8],all_observed_pose_facing_parts_receive_native_scanline_eligibility=all(all_visible.values()),ineligible_parts=[list(k)for k,v in all_visible.items()if not v],maximum_hardware_sprites_on_scanline=maxline,hardware_csv_sha256=sha(folder/'hardware.csv'),oam_sha256=sha(folder/'oam.bin'),palettes_sha256=sha(folder/'palettes.bin'))
 reports[mode]=report
print(json.dumps(reports,indent=2))
assert all(r['all_observed_pose_facing_parts_receive_native_scanline_eligibility']for r in reports.values()),'Every observed body/sword part must receive native scanline eligibility'
if first is None:
 report=dict(passed=True,status='LIVE_PORT_COMPOSITION_AND_HARDWARE_ADMISSION_PASS',ROM_sha256=oracle['ROM_sha256'],original_source_sha256=oracle['source_sha256'],original_hardware_forward_cases=len(oracle['original_hardware_order']),cases=reports,checker_sha256=sha(Path(__file__)),scope='Read-only native DMA observer on separately seeded component arenas. All body/sword records, actual physical CHR, body/declaration palettes and per-pixel intrinsic body composite match original source priority; each observed part receives nontransparent hardware scanline eligibility. This is not a campaign clear or an audio parity proof.')
 (O/'proof.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS_PROOF',sha(O/'proof.json'));raise SystemExit(0)
# Verification atlas only; actual frame screenshots remain separate.
colors={0x36:(254,204,197),0x14:(131,25,153),0x0f:(0,0,0),0x16:(181,49,32),0x30:(255,254,255),0x27:(254,174,50)}
canvas=Image.new('RGB',(3*192,192),(76,88,100));draw=ImageDraw.Draw(canvas)
for panel,(title,data)in enumerate([('Original hardware order',first['want']),('Port actual DMA order',first['actual']),('Different pixels',first['diff'])]):
 draw.text((panel*192+3,3),title,fill='white')
 for (x,y),v in data.items():
  col=(255,0,255)if panel==2 else colors[v];xx=panel*192+(x+20)*3;yy=24+(y+10)*3
  if panel*192<=xx<(panel+1)*192-2 and 24<=yy<190:draw.rectangle((xx,yy,xx+2,yy+2),fill=col)
canvas.save(O/'v5-priority-negative-atlas.png');(O/'v5-negative-oam.bin').write_bytes(first_raw);(O/'v5-negative-palette.bin').write_bytes(first_pal)
witness={k:v for k,v in first.items()if k not in ['want','actual','diff']};witness['different_pixel_examples']=[dict(position=list(xy),expected=a,actual=b)for xy,(a,b)in list(first['diff'].items())[:12]]
report=dict(passed=False,status='ACTUAL_PORT_PRIORITY_ORDER_DIFFERS_FROM_ORIGINAL_HARDWARE',ROM_sha256=oracle['ROM_sha256'],original_source_sha256=oracle['source_sha256'],original_hardware_forward_cases=len(oracle['original_hardware_order']),scope='Read-only observer on separately seeded native component arenas; original35 hardware captures establish descriptor-forward priority. No observer state writes. Membership, CHR and declared colors pass; actual per-pixel composite fails due reversed part order.',cases=reports,first_witness=witness,checker_sha256=sha(Path(__file__)))
(O/'negative-proof.json').write_text(json.dumps(report,indent=2)+'\n');print('NEGATIVE_PROOF',sha(O/'negative-proof.json'))

raise SystemExit(1)  # An actual negative proof must also fail the command.
