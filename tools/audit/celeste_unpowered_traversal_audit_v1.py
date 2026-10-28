"""Read-only full-campaign static census from actual compiled native parser.

This is an accommodation proposal, not a collision solver or a native clear.
It writes only one compact JSON and one text report; no map/game bytes change.
"""
from pathlib import Path
import collections,hashlib,itertools,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from celeste_host_controls_v4 import *

def decode(b,pointer,world=0):
 q=seed(b,0);q.m[:0x800]=[0]*0x800
 for g in b['segs'].values():
  if g.get('name')=='"SMCCODE"':
   at,n,off=[int(g[k],0)for k in['start','size','ooffs']];q.m[at:at+n]=b['raw'][off:off+n]
 q.put(AreaPointer=pointer,WorldNumber=world,Hidden1UpFlag=1)
 run(q,'GetAreaDataAddrs')
 for j in range(3):q.set('AreaObjectLength',255,j)
 columns=[]
 for x in range(400):
  run(q,'AreaParserCore');columns.append([q.get('MetatileBuffer',y)for y in range(13)]);run(q,'IncrementColumnPos')
 return columns
def jump(b):
 q=cmseed(b,0);q.put(Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,CmState=0,CmGravity=0x29,CmFallForce=0x50,Player_X_Speed=32,Player_XSpeedAbsolute=32,Player_MovingDir=1,PlayerFacingDir=1,CrouchingFlag=0)
 ys=[];xs=[]
 for t in range(90):
  q.put(SavedJoypadBits=129,A_B_Buttons=128,Left_Right_Buttons=1)
  run(q,'CmHostMovement');run(q,'CmHostAfterBG');ys.append(q.get('Player_Y_Position')-176);xs.append(q.get('Player_PageLoc')*256+q.get('Player_X_Position'))
  if t>4 and ys[-1]>=0 and q.get('Player_Y_Speed')<128:break
 return dict(launch_Y=176,maximum_rise=-min(ys),return_crossing_updates=len(ys),full_speed=2,trajectory_deltaY=ys,footprint_note='Native standing foot probes+3/+12; five-update coyote timer can extend edge launch. Same-height46-update flight92px is not the final collision gap limit. No moving support/enemy/spring boost included.')
def runs(values,predicate):
 rows=[];lo=None
 for i,v in enumerate(values+[None]):
  yes=i<len(values)and predicate(v)
  if yes and lo is None:lo=i
  if not yes and lo is not None:rows.append((lo,i));lo=None
 return rows
def main():
 out=R/'docs/qa/celeste-unpowered-traversal-2026-10-28.json';assert not out.exists()
 rom=R/'build/celeste-host-final.nes';b=scoped_load(rom)
 assert sha(rom)=='83db8bdf74dddc4055a52f5ec12526dcddc7a2fe418f24c3e9e1d5252fb6c9e0'
 md=R/'docs/qa/level-layout-audit-2026-10-22.md';mapping=[]
 for area,w,kind,num,off in re.findall(r'\| ([1-8]-[1-4][a-z]) \| (\d+) \| (Water|Ground|Underground|Castle) (\d+) \+(\d+) \|',md.read_text(encoding='utf-8')):
  mapping.append(dict(area=area,width=int(w),native_area=kind+num,offset=int(off),pointer=({'Water':0,'Ground':1,'Underground':2,'Castle':3}[kind]<<5)+int(num)-1))
 assert len(mapping)==61 and len({z['area'][:3]for z in mapping})==32
 maps={};hashes={}
 for kind,count,typ in[('Water',3,0),('Ground',22,1),('Underground',3,2),('Castle',6,3)]:
  for k in range(count):
   name=kind+str(k+1);cols=decode(b,(typ<<5)|k,7 if name=='Water3'else 0);maps[name]=cols;hashes[name]=hashlib.sha256(bytes(v for c in cols for v in c)).hexdigest()
 attrs=b['raw'][location(b,'MTileAttribute'):location(b,'MTileAttribute')+256]
 def solid(v):return bool(attrs[v]&address(b,'MTILE_SOLID'))and not attrs[v]&address(b,'MTILE_CLIMB')and v not in[0x5f,0x60,0xc5]
 def tops(col):return[(r+2)*16 for r,v in enumerate(col)if r>=2 and solid(v)and not solid(col[r-1])and not solid(col[r-2])]
 def bottom(col):
  if not solid(col[-1]):return None
  i=12
  while i and solid(col[i-1]):i-=1
  return(i+2)*16
 helpers=json.loads((R/'src/crossover_helper_data.json').read_text())['records'];assert len(helpers)==34
 trajectory=jump(b);areas=[];candidates=[]
 for spec in mapping:
  name=spec['area'];offset=spec['offset'];width=spec['width'];cols=maps[spec['native_area']][offset:offset+width];floors=[bottom(c)for c in cols];stands=[tops(c)for c in cols];items=[]
  if spec['native_area'].startswith('Water'):
   areas.append(dict(**spec,water=True,reason='Swimming uses actual native water jump/integration; dry51px/2px threshold deliberately not applied.',candidates=[]));continue
  # Every actual vertical pipe cap, not an imagined object from a raw byte.
  for i,c in enumerate(cols):
   cap=next((r for r,v in enumerate(c)if v in[0x10,0x12]),None)
   if cap is None:continue
   top=(cap+2)*16;near=[v for v in floors[max(0,i-3):i]if v is not None];base=min(near)if near else None
   rise=base-top if base is not None else None
   if rise is None or rise<=trajectory['maximum_rise']:continue
   x=(offset+i)*16;alternatives=sorted(set((offset+j)*16 for j in range(max(0,i-7),i)if any(top<t<base for t in stands[j])))
   z=dict(kind='tall_pipe',x=x,top_Y=top,approach_surface_Y=base,rise=rise,nearby_intermediate_surface_columns=alternatives,native_area=spec['native_area'],proposal=dict(actor='native vertical girder25',width_px=16,center_x=x-24,center_Y=(base+top)//2,axis=1),status='Requires actual approach/clearance and real platform carry controls before implementation; nearby intermediate tops may remove need.')
   items.append(z)
  # Ground-connected solid faces excluding already-enumerated pipe caps.
  for i in range(1,len(cols)):
   if floors[i]is None or floors[i-1]is None or floors[i]<64 or floors[i-1]-floors[i]<=trajectory['maximum_rise']:continue
   if any(v in[0x10,0x12]for v in cols[i]):continue
   x=(offset+i)*16;items.append(dict(kind='solid_rise',x=x,top_Y=floors[i],approach_surface_Y=floors[i-1],rise=floors[i-1]-floors[i],proposal=dict(actor='native vertical girder25',width_px=16,center_x=x-24,center_Y=(floors[i-1]+floors[i])//2,axis=1),status='Static face candidate; optional upper route, destruction and native lift/spring may already bypass.'))
  # Empty columns with NO landing surface, rather than calling decorative
  # mushroom stems or every missing bottom cell a pit.
  for lo,hi in runs(stands,lambda t:not t):
   if lo==0 or hi==len(cols)or hi-lo<6:continue
   left=min(stands[lo-1]);right=min(stands[hi]);gap=(hi-lo)*16;drop=right-left
   # Optimistic45+ coyote/footprint allowance is explicit, not a gameplay
   # admission. A lower far landing can extend flight beyond same-height46.
   desc=[i+1 for i,y in enumerate(trajectory['trajectory_deltaY'])if i>=24 and y>=drop]
   reach=2*desc[0]+18 if desc else None
   items.append(dict(kind='open_support_span',x=(offset+lo)*16,end_x=(offset+hi)*16,width_px=gap,near_surface_Y=left,far_surface_Y=right,optimistic_static_reach_px=reach,exceeds_optimistic_bound=reach is not None and gap>reach,proposal=dict(actor='native horizontal girder28',width_px=16,center_x=(offset*2+lo+hi)*8,top_Y=max(left,right),axis=0),status='Gap≥96px census; coyote/foot probes, fall-height, actual native actor platforms and ceiling path need continuous caller qualification.'))
  # High isolated support transitions are a separate class in3/6-platform
  # maps. List adjacent available surfaces, not a fabricated floor staircase.
  for i in range(1,len(cols)):
   if not stands[i]or not stands[i-1]:continue
   prev=min(stands[i-1]);cur=min(stands[i])
   if prev-cur<=trajectory['maximum_rise']or(floors[i]is not None and floors[i-1]is not None):continue
   if any(v in[0x10,0x12]for v in cols[i]):continue
   items.append(dict(kind='isolated_support_rise',x=(offset+i)*16,near_surface_Y=prev,far_surface_Y=cur,rise=prev-cur,proposal=dict(actor='native vertical girder25',width_px=16,center_x=(offset+i)*16-24,center_Y=(prev+cur)//2,axis=1),status='Upper-route candidate; may be avoidable below/through native moving supports.'))
  for z in items:z.update(area=name,stage=name[:3]);candidates.append(z)
  areas.append(dict(**spec,water=False,candidates=len(items),candidate_counts=dict(collections.Counter(z['kind']for z in items))))
 # Actual raw0 mask iszero even with MarioVariant4. Easy gate4 explicitly
 # admits native original-six families, bypassing that mask.
 masks=[];compiled_helper_cases=0
 for mode in[0,1]:
  admitted=[]
  for i,z in enumerate(helpers):
   gate=z['hard_gate'if mode else'easy_gate']
   if gate==4:admitted.append(dict(index=i,area=z['area'],center_x=z['center_x'],top_y=z['top_y']))
  for z in helpers:
   key=z['world_level'];q=cmseed(b,0);q.put(CrossoverBehaviorVersion=mode,WorldNumber=key//4,LevelNumber=key%4,AreaType=z['pointer']>>5,AreaAddrsLOffset=z['pointer']&31)
   run(q,'HpConfigure');want=[i for i,h in enumerate(helpers)if h['world_level']==key and h['pointer']==z['pointer']and h['hard_gate'if mode else'easy_gate']==4]
   assert q.get('HpCount')==len(want) and[q.get('HpRecord',i)for i in range(q.get('HpCount'))]==want
   compiled_helper_cases+=1
  masks.append(dict(mode=mode,raw0_HV_mask=0,unfiltered_gate4_records=admitted))
 stages=[]
 for w,l in itertools.product(range(1,9),range(1,5)):
  key=f'{w}-{l}';zs=[z for z in candidates if z['stage']==key];hs=[z for z in helpers if z['area'].startswith(key)]
  stages.append(dict(stage=key,areas=[a['area']for a in areas if a['area'].startswith(key)],candidates=len(zs),counts=dict(collections.Counter(z['kind']for z in zs)),existing_HV_source_helpers=len(hs)))
 inputs=[Path(__file__),rom,rom.with_suffix('.dbg'),md,R/'docs/qa/level-layout-audit-2026-10-22.json',R/'src/crossover_helpers.s',R/'src/crossover_helper_data.json',R/'src/crossover_helper_data.inc',R/'src/native_platform16.s',R/'src/celeste_mario_core.s',R/'src/celeste_mario_kernel.inc',R/'src/level_tiles.s',R/'src/collision.s']
 report=dict(status='READ_ONLY_PROPOSED_CENSUS_NOT_FULL_TRAVERSAL_PROOF',ROM_sha256=sha(rom),campaign_stages=32,campaign_subareas=61,native_parser_areas=34,native_parser_columns=13600,native_column_hashes=hashes,jump=trajectory,actual_existing_helper_policy=masks,compiled_helper_configure_cases=compiled_helper_cases,existing_native_helpers=helpers,stages=stages,areas=areas,proposed_candidates=candidates,counts=dict(collections.Counter(z['kind']for z in candidates)),bindings={str(p):sha(p)for p in inputs},implementation_blockers=['HpConfigure caches at most3 records per loaded area, not3 simultaneous near-camera records. An area with>3 proposed/new helpers needs an explicitly reviewed streaming/reuse design; do not merely append records that will never admit.','Raw0 has no H/V helper mask; MarioVariant4 needs exact variant admission. A tier-dependent eligibility also needs real identity-cache/lifecycle review; no helper must disappear from under a supported player on pickup.','Static columns omit real enemy-based moving platforms/springs/transport execution and castle-maze state. Lists are complete enumerations of the declared geometric candidate classes, not a proved minimal set of mandatory obstructions.','Horizontal and vertical sine support/carry must remain actual native actors25/28; proposed centers are source geometry plans, not qualified placement bytes. Actor budgets, loadedscene key and absent-slot behavior need controls.','ExistingXML alignment is historical and differs from native columns at several landmarks; output x is actual native parser x, not blindly importedXML.','HostCels tier0 has no grip; tier1walljump nativePASS does not prove tier0campaign. No jump/physics unlock or painted terrain authorized.'])
 out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 txt=R/'docs/qa/celeste-unpowered-traversal-2026-10-28.txt';lines=['Celeste tier0 -- read-only native geometry accommodation proposal','',f'Frozen83db; actual compiled native parser34areas/13,600columns, all32campaign stages/61historical subareas. {len(candidates)} geometric candidates, NOT that many proven mandatory accommodations.',f'Actual CmHostMovement+CmHostAfterBG cold tier0 full-held jump: rise{trajectory["maximum_rise"]}px; return-crossing{trajectory["return_crossing_updates"]}updates at2px/update. NoTier0wallgrip/dash.','', 'Stage | tallpipe | solidrise | supportgap | isolatedrise | existing34-records']
 for s in stages:
  c=s['counts'];lines.append(s['stage']+' | '+' | '.join(str(c.get(k,0))for k in['tall_pipe','solid_rise','open_support_span','isolated_support_rise'])+' | '+str(s['existing_HV_source_helpers']))
 lines+=['','Actual raw0/Celeste H/V mask0. Easy source gate4 still admits the three authored original-six exceptions; Hard admits none of the34 for raw0. No automatic blanketH/V change is made.','',*report['implementation_blockers'],'','The JSON contains every candidate native x/height/gap and proposed real girder center, all34 current records and exact input hashes. Before edits, select necessary placements via actual continuous BG/support controls; all32clear acceptance is still pending. No source/ROM/native change.']
 txt.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(json.dumps(dict(status=report['status'],JSON=str(out),sha256=sha(out),text_sha256=sha(txt),candidates=len(candidates),counts=report['counts'])))
if __name__=='__main__':main()
