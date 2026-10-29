"""Measured minimal Retold layout repair; no CHR/PRG/RAM allocation edits."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import pit_retold_layout_plan_v1 as V
from sunny_integrated_controls_v1 import *
from PIL import Image
O=R/'build/pit_retold_layout_plan_v2.json'
G=V.G

def target(pose):
 if pose!='CROUCHSHOOT':return V.target(pose)
 old,new=V.source(330,'reference-combat');bb=old.getbbox();width,height=bb[2]-bb[0],bb[3]-bb[1]
 ao,an=V.source(405,'reference-combat');ab=ao.getbbox()
 arm=an.crop((ab[0]+9,ab[1]+9,ab[0]+16,ab[1]+17))
 out=Image.new('RGBA',(96,80))
 # The original builder computes center BEFORE extending its bow canvas.
 out.alpha_composite(new,(40-width//2-bb[0],64-height-bb[1]))
 out.alpha_composite(arm,(40-width//2+width-2,64-height+6))
 return out

def main():
 assert not O.exists();V.PATCH,_=V.A.ips();b=scoped_load(V.P)
 G.ROLE='PIT';G.COLORS=G.targets('PIT')
 def data(n,count):return b['raw'][location(b,n):location(b,n)+count]
 banks=data('XgPITBanks',252);mapping=data('ChrPhysicalMap',256)
 constraints={};conflicts=[];missed=[];changed_records={};source_ties=[]
 for group in range(5):
  page=mapping[213+min(group,3)]
  for t in range(0,22,2):constraints[(group,t)]=b['raw'][1048592+page*1024+t*16:1048592+page*1024+t*16+32]
 for index in range(252):
  pose=G.POSES[index%84];grid=G.layers(target(pose));group=4 if pose=='WALK3'else banks[index]-213
  ptr=data('XgPITRightLo',252)[index]+256*data('XgPITRightHi',252)[index]
  at=16+31*8192+ptr-0xc000;old=b['raw'][at:at+1+b['raw'][at]];rec=bytearray(old);covered=set()
  repair=pose in['CROUCH','DIE','CROUCHSHOOT','CROUCHATTACK1','CROUCHATTACK2','CROUCHATTACK3']
  for j in range(1,len(rec),4):
   if repair and rec[j+2]==17 and rec[j+3]in[1,9]:rec[j+2]=16
   t,a,y,x=rec[j:j+4];x=x if x<128 else x-256;y=y if y<128 else y-256;p=a&3
   values=[[0]*8 for _ in range(16)]
   for yy in range(16):
    for xx in range(8):
     tx,ty=32+x+xx,32+y+yy;sx=7-xx if a&64 else xx;sy=15-yy if a&128 else yy
     if 0<=tx<96 and 0<=ty<80:covered.add((p,tx,ty));values[sy][sx]=grid[p][ty][tx]
   raw=V.encode(values);key=(group,t)
   if key in constraints and constraints[key]!=raw:conflicts.append([index,pose,group,t])
   else:constraints[key]=raw
  if bytes(rec)!=old:changed_records.setdefault(ptr,dict(poses=[],old=old.hex(),new=bytes(rec).hex()))['poses'].append(index)
  absent=[(p,x,y)for p in grid for y in range(80)for x in range(96)if grid[p][y][x]and(p,x,y)not in covered]
  if absent:missed.append([index,pose,len(absent)])
  source_ties.append([index,pose,group,ptr])
 assert not conflicts and not missed,(conflicts,missed)
 recordbytes=sum(len(bytes.fromhex(r['new']))*2 for r in changed_records.values())
 assert recordbytes==154
 # Existing source aliases make these five records sufficient for all3powers.
 out=dict(status='MEASURED_PRIVATE_LAYOUT_PROPOSAL_PENDING_ROOT_ALLOCATION',parent=sha(V.P),
  exact_CHR_request=dict(first=808,last=812,pages=5,bytes=5120,remaining813_831_untouched=True),
  C31_request=dict(start='DDE6',end_exclusive='E000',capacity=538,verified_parent_all_FF=True,
   new_crouch_and_hammer_pose_records_both_faces=154,pointer_table_bytes=20,
   proposed_max_router_publisher_bytes=180,uncommitted_spare=184),
  proposed_cold_menu_request=dict(bank=66,start='B600',end_exclusive='B680',capacity=128),
  raw_ID=6,proposed_PitVariant='5FE0',normal_Pit_variant0_unchanged=True,
  renderer='Old C31 lease and existing record layouts; five duplicated corrected records, extra Walk3 page resolves one real shared-pattern conflict; only bodywindow0 wide-published.',
  corrected_v1_oracle='v1 crouchshot incorrectly centered the extended canvas; actual source computes center before arm extension. v2 fixes only that target reconstruction.',
  all252_power_pose_records_uncovered_pixels=missed,all252_pattern_conflicts=conflicts,
  changed_record_templates=changed_records,pose_group_pointer_map=source_ties,
  required_pattern_hashes={f'{g}:{t}':V.D.digest(v)if hasattr(V,'D')else __import__('hashlib').sha256(v).hexdigest()for(g,t),v in constraints.items()},
  code_or_CHR_written=False,native_run=False,
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),Path(V.__file__),V.P,V.P.with_suffix('.dbg'),V.P.with_suffix('.lbl'),R/'build/pit_retold_layout_plan_v1.json',R/'build/pit-retold-assets-v1/handoff.json']})
 out['proposed_cold_menu_request']['rejected_prior_guess']='81:BB10 is occupied CELESTE_MARIO_HOST, caught before any allocation/build; never used.'
 out['proposed_cold_menu_request']['verified_parent_all_FF']=b['raw'][16+66*8192+0x1600:16+66*8192+0x1680]==bytes([255])*128
 assert out['proposed_cold_menu_request']['verified_parent_all_FF']
 O.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k]for k in['status','exact_CHR_request','C31_request','proposed_cold_menu_request','all252_power_pose_records_uncovered_pixels','all252_pattern_conflicts']}))
if __name__=='__main__':main()
