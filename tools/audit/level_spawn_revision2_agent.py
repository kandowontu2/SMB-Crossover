"""Audit-only authored enemy/control/group and pickup comparison, revision2."""
from pathlib import Path
import collections,csv,difflib,hashlib,json,re,shutil,sys
from level_layout_inventory_agent import R,O,load,record
from level_layout_source_binding_agent import streams
from level_layout_compare_agent import classify,nc
from level_nes_columns_agent import Decode
P=O/'spawn-revision2'
NAMES={0:'KoopaGreen',1:'KoopaGreen',2:'Beetle',3:'KoopaRed',5:'HamBro',6:'Goomba',7:'Bloopa',8:'BulletBill',10:'CheepGreen',11:'CheepRed',12:'LavaFireBall',13:'Piranha',14:'WingedKoopaGreen',15:'WingedKoopaRed',16:'WingedKoopaHorizontalGreen',17:'LakituStart',18:'Spiny',20:'FlyingCheepStart',21:'BowserFireBallStart',22:'Fireworks',23:'BBill_CCheep_Frenzy',24:'FrenzyEnd',27:'FireBarRight',28:'FireBarRightFast',29:'FireBarLeft',30:'FireBarLeftFast',31:'FireBarRightLong',36:'PlatformPully',37:'PlatformWaveVertical',38:'PlatformConstantRise',39:'PlatformConstantFall',40:'PlatformWaveHorizontal',41:'PlatformStepFall',42:'PlatformCloud',43:'PlatformConstantRiseSmall',44:'PlatformConstantFallSmall',45:'Bowser',46:'PowerUp',47:'Vine',48:'FlagpoleFlag',49:'StarFlag',50:'Jumpspring',51:'BulletBillCannon',52:'WarpZoneControl',53:'Retainer'}
def parse(name,raw):
 page=sel=0;i=0;out=[]
 while i<len(raw):
  a=raw[i]
  if a==255:assert i==len(raw)-1;break
  b=raw[i+1];row=a&15
  if b&128 and not sel:page+=1;sel=1
  if row==15 and not sel:
   page=b&63;sel=1;out.append(dict(stream=name,offset=i,raw=list(raw[i:i+2]),kind='page_control',page=page));i+=2;continue
  d=dict(stream=name,offset=i,raw=list(raw[i:i+(3 if row==14 else 2)]),page=page,column=(a>>4),x=page*256+(a&240),row=row,hard_only=bool(b&64))
  if row==14:d.update(kind='transport',destination_pointer=b,world_filter=raw[i+2]>>5,entrance_page=raw[i+2]&31);i+=3
  else:
   ident=b&63;d.update(kind='group'if 55<=ident<=62 else'actor',id=ident,name=NAMES.get(ident,f'ID_{ident:02x}'))
   if d['kind']=='group':d.update(group_class='Goomba'if ident<59 else'KoopaGreen',count=2+((ident-55)&1),group_y_row=11 if not(ident-55)&2 else 7,nominal_first_x=d['x']-48,spacing=24,coordinate_caveat='Actual group origin is ScreenRight at processing; record−48 is the earliest aligned static origin, not an emulator-attained exact coordinate.')
   i+=2
  out.append(d);sel=0
 return out
def native_reexecute(parsed):
 d=Decode();cases=[]
 for name,rows in parsed.items():
  kind=re.search(r'E_(\w+)Area(\d+)',name);typ={'Water':0,'Ground':1,'Underground':2,'Castle':3}[kind[1]];pointer=typ*32+int(kind[2])-1
  for z in rows:
   if z['kind']not in('actor','group'):continue
   for primary in(0,1):
    for secondary in(0,1):
     d.area(pointer,0);d.set('PrimaryHardMode',primary);d.set('SecondaryHardMode',secondary);d.set('EnemyDataOffset',z['offset']);d.set('EnemyObjectPageLoc',z['page']);d.set('EnemyObjectPageSel',1);d.set('ObjectOffset',0);d.cpu.x=0
     # Mark the page-select side effect already applied. Normal object consumption
     # is identical thereafter; this seeded call is static decoding, not gameplay.
     right=z['x']-48;d.set('ScreenRight_X_Pos',right&255);d.set('ScreenRight_PageLoc',(right>>8)&255)
     d.call('ProcessEnemyData')
     actors=[]
     for slot in range(6):
      r=lambda n:d.mem[d.i.ram[n]+slot]
      if r('Enemy_Flag'):actors.append(dict(slot=slot,id=r('Enemy_ID'),flag=r('Enemy_Flag'),x=r('Enemy_X_Position')+256*r('Enemy_PageLoc'),y=r('Enemy_Y_Position'),high_y=r('Enemy_Y_HighPos'),bbox=r('Enemy_BoundBoxCtrl')))
     allowed=not z['hard_only']or bool(secondary)
     if not allowed:assert not actors,(name,z,actors)
     if allowed and z['kind']=='group':
      ident=2 if primary and z['group_class']=='Goomba'else 6 if z['group_class']=='Goomba'else 0
      assert [(a['id'],a['x'])for a in actors]==[(ident,right+24*n)for n in range(z['count'])],(name,z,actors)
     cases.append(dict(stream=name,offset=z['offset'],primary=primary,secondary=secondary,hard_admitted=allowed,actors=actors,EnemyDataOffset_after=d.get('EnemyDataOffset'),EnemyFrenzyBuffer_after=d.get('EnemyFrenzyBuffer')))
 return cases
def parse_level(name,raw):
 page=sel=0;out=[]
 for i in range(2,len(raw)-1,2):
  a,b=raw[i:i+2];row=a&15
  if b&128 and not sel:page+=1;sel=1
  if row==13 and not b&64 and not sel:
   page=b&31;sel=1;out.append(dict(stream=name,offset=i,kind='page_control',page=page));continue
  d=dict(stream=name,offset=i,raw=[a,b],x=page*256+(a&240),row=row,page=page)
  if row<12 and b&0x70==0x70:d['kind']='vertical_pipe'
  elif row==13 and b&64:d.update(kind='special',command=b&63)
  else:d['kind']='geometry_or_interactive'
  out.append(d);sel=0
 return out
def canon(v):
 s=v.split('&&')[0]
 if s.startswith('enemy'):
  s=s[5:];s=re.sub(r'(Brown|Blue|Gray|Black)$','',s)
  if s.startswith('Piranha'):return'Piranha'
  if s=='Koopa':return'KoopaGreen'
  if s=='WingedKoopa':return'WingedKoopaGreen'
  if s=='HamBroGreen':return'HamBro'
  if s.startswith('Cheep'):return'CheepGreen'if'Green'in s else'CheepRed'
  if s=='BowserHammer':return'Bowser'
  return s
 if s.startswith('platform'):
  if s=='platformCloud':return'PlatformCloud'
  typ=re.search('type=([^&]+)',v);return'Platform'+typ[1][0].upper()+typ[1][1:]if typ else'PlatformUnknown'
 if s.startswith('fireBar'):return s[0].upper()+s[1:]
 if s=='lavaFireBall':return'LavaFireBall'
 if s.startswith('spawnBulletBill'):return'BulletBillStart'if'Start'in s else'BulletBillEnd'
 if s in('lakituStart','lakituEnd','flyingCheepStart','flyingCheepEnd','bowserFireBallStart'):return s[0].upper()+s[1:]
 return None
def column_mapping(z,nes,maps):
 a=maps[z['area']];off=z['offset'];w=z['original_width'];old=[''.join(nc(nes['rows'][y][x+off])for y in range(13))for x in range(w)]
 new=[''.join(classify(a['MAP'][y+2][x])if'charHorz'not in a['MAP'][y+2][x]and'charVert'not in a['MAP'][y+2][x]else'0'for y in range(13))for x in range(len(a['MAP'][0]))]
 sm=difflib.SequenceMatcher(a=old,b=new,autojunk=False);mapping={}
 for typ,i,j,k,l in sm.get_opcodes():
  if typ=='equal'or typ=='replace'and j-i==l-k:
   for x in range(i,j):mapping[x+off]=k+x-i
 return mapping
def mapx(x,mapping):
 col=int(x//16);frac=x-col*16
 if col in mapping:return mapping[col]*16+frac
 # No extrapolation across a deleted native column or an expanded maze.
 return None
def native_class(raw):
 if raw==0xc1:return'question_powerup'
 if raw==0xc0:return'question_coin'
 if raw==0x5f:return'hidden_coin'
 if raw==0x60:return'hidden_1up'
 if raw in(0x55,0x5a):return'brick_powerup'
 if raw in(0x56,0x5b):return'brick_vine'
 if raw in(0x57,0x5c):return'brick_star'
 if raw in(0x58,0x5d):return'brick_multi_coin'
 if raw in(0x59,0x5e):return'brick_1up'
 if raw in(0x51,0x52,0x53):return'brick_plain'
 if raw in(0xc2,0xc3):return'free_coin'
 if raw==0xc4:return'used_block'
 if raw==0xc5:return'axe'
 if raw==0x68:return'spring'
 if raw in(0x24,0x25):return'flagpole'
 if raw in(0x10,0x11,0x12,0x13,0x14,0x15,0x1c,0x1d,0x1e,0x1f,0x20,0x21,0x6a,0x6b):return'pipe'
 if raw==0x64:return'cannon'
 if raw in(0x65,0x66):return'cannon_segment'
 if raw==0x89:return'bowser_bridge'
 if raw in(0x16,0x17,0x18,0x19,0x1a,0x1b):return'ledge'
 if raw==0x63:return'bridge'
 if raw in(0x22,0x54,0x61,0x62,0x69,0x6c,0x88):return'solid'
 return'none'
def source_class(a,x,y,version=1):
 raw=a['MAP'][y][x];v=raw.split('&&')[0];p=a['PICKUPS'][y][x]
 if 'charHorz'in raw or'charVert'in raw:return'conditional_helper'
 if 'UnbreakableBrick'in v:return'brick_single_coin'if version else'solid'
 content='powerup'if p.startswith('mushroomRed')else'1up'if p.startswith('mushroomGreen')else'star'if p.startswith('star')else'vine'if p.startswith('vineTransferStart')else'coin'if p.startswith('coin')else None
 if v.startswith('itemBlock'):
  return('hidden_'if'Invisible'in v else'question_')+(content or'coin')
 if v.startswith('brick'):return'brick_'+('multi_coin'if content=='coin'else content or'plain')
 if p.startswith('coin'):return'free_coin'
 if p.startswith('bowserAxe'):return'axe'
 if v.startswith('spring'):return'spring'
 if v.startswith('flagPole'):return'flagpole'
 if v.startswith('groundPipe'):return'pipe'
 if v=='groundCanon':return'cannon'
 if v.startswith('groundCanonSegment'):return'cannon_segment'
 if v=='bowserBridge':return'bowser_bridge'
 if v.startswith('groundMushroom'):return'ledge'
 if v=='groundRail':return'bridge'
 if v=='boxGray':return'used_block'
 if classify(raw)=='S':return'solid'
 return'none'
def generate_comparison(parsed,cases):
 maps=[load(R/'reference/crossover/assets/45_com.smbc.level.LevelData_LevelDataXML.bin'),load(R/'reference/crossover2/extracted/binaryData/322_com.smbc.level.LevelData_LevelDataXML.bin')];nes=json.loads((O/'nes-column-inventory.json').read_text())['areas'];align=json.loads((O/'static-column-alignments.json').read_text());case={(z['stream'],z['offset'],z['primary'],z['secondary']):z for z in cases};groups=[];actor_inventory=[];item_inventory=[];source_only=[];levels={k:parse_level(k,v)for k,v in streams(R/'.upstream/smb1base/src/level_tiles.s').items()if k.startswith('L_')};(P/'original-level-commands.json').write_text(json.dumps(levels,indent=2)+'\n')
 for vi,m in enumerate(maps):
  for z in align:
   area=z['area'];world,level=map(int,area[:3].split('-'));secondary=int(world>5 or world==5 and level>=3);a=m[area];n=nes[z['original_area']];cm=column_mapping(z,n,m);stream='E_'+z['original_area'].replace('Water','WaterArea').replace('Underground','UndergroundArea').replace('Ground','GroundArea').replace('Castle','CastleArea');native=[];source=[]
   for e in parsed[stream]:
    if e['kind']not in('actor','group')or e['hard_only']and not secondary:continue
    if not z['offset']*16<=e['x']<(z['offset']+z['original_width'])*16:continue
    cp=case[(stream,e['offset'],0,secondary)];cls=e['name']
    if z['offset']and e['x']<(z['offset']+16)*16:continue # Original entry seeks past records behind initial screen right.
    if e['kind']=='group':cls=e['group_class']
    if cls in('BBill_CCheep_Frenzy','LakituStart','FlyingCheepStart','BowserFireBallStart','FrenzyEnd','Fireworks','WarpZoneControl','Retainer'):
     native.append(dict(class_name=cls,record=e,compiled=cp,native_x=e['x'],native_y=e['row']*16,anchor_kind='control_record',expected_x=mapx(e['x'],cm),expected_y=None));continue
    for sub,actor in enumerate(cp['actors'][:e.get('count',1)]):
     id=actor['id'];cls=NAMES.get(id,cls)
     x=actor['x']+8;y=e.get('group_y_row',e['row'])*16+32;anchor='enemy_center_x_and_foot_y'
     if cls in('Bloopa','CheepGreen','CheepRed'):y=e['row']*16+16;anchor='floating_enemy_anchor'
     if cls.startswith('FireBar'):x=e['x']+8;y=e['row']*16+8;anchor='firebar_pivot'
     elif cls=='LavaFireBall':x=e['x']+8;y=None;anchor='lava_hazard_x_only'
     elif cls=='Bowser':x=e['x']+24;y=e['row']*16+32;anchor='bowser_body_center_x_and_foot_y'
     elif cls.startswith('Platform'):
      width=32 if n['pointer']>>5==3 or secondary else 48
      if cls.endswith('Small'):width=24
      x=actor['x']+width/2;y=actor['y'];anchor='platform_initial_center_x_and_top_y'
      if cls=='PlatformWaveHorizontal':x-=32;anchor='platform_horizontal_oscillation_center_x_and_top_y'
     native.append(dict(class_name=cls,record=e,compiled_actor=actor,subindex=sub,native_x=x,native_y=y,anchor_kind=anchor,expected_x=mapx(x,cm),expected_y=y))
   # Pipes create authored Piranhas through the level parser, outside enemy streams.
   if area!='1-1a':
    for p in levels[stream.replace('E_','L_')]:
     if p['kind']!='vertical_pipe':continue
     xx=p['x']//16;yy=p['row']+2
     if xx not in cm or not z['offset']<=xx<z['offset']+z['original_width']:continue
     native.append(dict(class_name='Piranha',record=dict(level_derived='VerticalPipe',original_tile=[xx,yy],level_command=p,slot_condition='FindEmptyEnemySlot can suppress runtime construction; warp-zone cleanup can erase plants. This is authored construction only.'),native_x=xx*16+16,native_y=yy*16,anchor_kind='pipe_center_x_and_plant_down_anchor',expected_x=mapx(xx*16+16,cm),expected_y=yy*16))
   for yy,row in enumerate(a['PICKUPS']):
    for xx,raw in enumerate(row):
     cls=canon(raw)
     if not cls:continue
     source.append(dict(class_name=cls,tile=[xx,yy],raw=raw,x=xx*16+8+(8 if'shiftRight'in raw else 0),y=yy*16+(8 if cls.startswith('FireBar')else 0 if cls.startswith('Platform')else 16),conditional='charHorz'in raw or'charVert'in raw))
   # Assignment preserves exact raw coordinates and admits bounded anchors; it
   # never silently normalizes a mismatch to a match.
   unused=set(range(len(source)));pairs=[]
   def nearest_exact(e):
    x=e['expected_x'];stem=e['class_name'].removesuffix('Small').removesuffix('Fast')
    return min((abs(s['x']-x)+(abs(s['y']-e['expected_y'])if e['expected_y']is not None else 0)for s in source if s['class_name']==stem and not s['conditional']),default=1e9)if x is not None else 1e9
   for e in sorted(native,key=nearest_exact):
    cls=e['class_name'];stem=cls.removesuffix('Small').removesuffix('Fast');candidates=[i for i in unused if source[i]['class_name']==stem and not source[i]['conditional']]
    def dist(i):
     s=source[i];x=e['expected_x'];y=e['expected_y'];return(abs(s['x']-x)if x is not None else 10000)+(abs(s['y']-y)if y is not None else 0)
    best=min(candidates,key=dist)if candidates else None
    if best is not None and dist(best)<=160:
     s=source[best];unused.remove(best);status='equal_authored_anchor'if dist(best)==0 else'authored_anchor_delta'
     if cls.endswith('Fast'):status='firebar_fast_variant_collapsed_to_uniform_source_speed'
     pairs.append(dict(status=status,native=e,source=s,delta=[s['x']-e['expected_x']if e['expected_x']is not None else None,s['y']-e['expected_y']if e['expected_y']is not None else None]))
    else:pairs.append(dict(status='native_record_without_nearby_same_class_source',native=e,source=None))
   for i in sorted(unused):pairs.append(dict(status='source_conditional_helper'if source[i]['conditional']else'source_explicit_fish_replaces_native_frenzy'if source[i]['class_name'].startswith('Cheep')and n['pointer']>>5==0 else'source_record_without_native_pair',native=None,source=source[i]))
   actor_inventory.append(dict(version=('hosted_1x','2.02')[vi],area=area,original_area=z['original_area'],primary_hard=False,secondary_hard=bool(secondary),coordinate_contract='Mapped through revision1 static column alignment. Explicit raw/native/source anchors and deltas retained; platform phase and control semantics are not normalized into runtime equivalence.',pairs=pairs))
   # Full fine-grained interactive inventory for every mapped cell, not merely
   # locations already called B->S by the coarse topology pass.
   seen=set();items=[]
   for xx,sx in sorted(cm.items()):
    for yy in range(2,15):
     nt=n['rows'][yy-2][xx];nc1=native_class(nt);sc=source_class(a,sx,yy,vi);seen.add((sx,yy))
     if nc1=='none'and sc=='none':continue
     items.append(dict(original_tile=[xx,yy],source_tile=[sx,yy],original_metatile=nt,original_class=nc1,source_class=sc,source_map=a['MAP'][yy][sx],source_pickup=a['PICKUPS'][yy][sx],equal=nc1==sc))
   extra=[dict(source_tile=[x,y],source_class=source_class(a,x,y,vi),source_map=raw,source_pickup=a['PICKUPS'][y][x])for y,row in enumerate(a['MAP'])for x,raw in enumerate(row)if y>=2 and(x,y)not in seen and source_class(a,x,y,vi)!='none']
   native_extra=[dict(original_tile=[x,y+2],original_metatile=n['rows'][y][x],original_class=native_class(n['rows'][y][x]))for x in range(z['offset'],z['offset']+z['original_width'])if x not in cm for y in range(13)if native_class(n['rows'][y][x])!='none']
   item_inventory.append(dict(version=('hosted_1x','2.02')[vi],area=area,cells=items,source_cells_in_inserted_or_unmapped_columns=extra,native_cells_in_deleted_or_unmapped_columns=native_extra))
 (P/'all-enemy-object-comparisons.json').write_text(json.dumps(actor_inventory,indent=2)+'\n')
 (P/'all-interactive-comparisons.json').write_text(json.dumps(item_inventory,indent=2)+'\n')
 print('ACTOR STATUS',collections.Counter(p['status']for g in actor_inventory if g['version']=='2.02'for p in g['pairs']))
 print('INTERACTIVE DIFFS',collections.Counter((x['original_class'],x['source_class'])for g in item_inventory if g['version']=='2.02'for x in g['cells']if not x['equal']))
 return actor_inventory,item_inventory
def finalize(parsed,cases,actors,items):
 """Preserve revision1 and publish the complete inputs, not only a diff shortlist."""
 out=[]
 for g in actors:
  for p in g['pairs']:
   n=p['native']or{};s=p['source']or{};r=n.get('record',{})
   out.append(dict(version=g['version'],area=g['area'],status=p['status'],native_class=n.get('class_name'),native_record_offset=r.get('offset'),native_record_raw=r.get('raw'),native_record_x=r.get('x'),native_record_row=r.get('row'),hard_only=r.get('hard_only'),secondary_hard=g['secondary_hard'],native_anchor=n.get('anchor_kind'),native_x=n.get('native_x'),native_y=n.get('native_y'),mapped_x=n.get('expected_x'),mapped_y=n.get('expected_y'),source_class=s.get('class_name'),source_tile=s.get('tile'),source_x=s.get('x'),source_y=s.get('y'),source_raw=s.get('raw'),delta=p.get('delta')))
 with(P/'complete-enemy-object-list.csv').open('w',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
 flat=[]
 for g in items:
  for p in g['cells']:
   if not p['equal']:flat.append(dict(version=g['version'],area=g['area'],**p))
  for p in g['source_cells_in_inserted_or_unmapped_columns']:flat.append(dict(version=g['version'],area=g['area'],original_tile=None,original_metatile=None,original_class='inserted_or_unmapped_column',**p,equal=False))
  for p in g['native_cells_in_deleted_or_unmapped_columns']:flat.append(dict(version=g['version'],area=g['area'],**p,source_class='deleted_or_unmapped_column',source_tile=None,source_map=None,source_pickup=None,equal=False))
 with(P/'complete-interactive-differences.csv').open('w',encoding='utf-8',newline='')as f:
  fields=list(dict.fromkeys(k for p in flat for k in p));w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(flat)
 hard=[]
 for g in actors:
  if g['version']!='2.02':continue
  a=g['original_area'];stream='E_'+a.replace('Underground','UndergroundArea').replace('Ground','GroundArea').replace('Water','WaterArea').replace('Castle','CastleArea');cmds=[z for z in parsed[stream]if z['kind']in('actor','group')]
  hard.append(dict(area=g['area'],native_stream=stream,secondary=g['secondary_hard'],hard_only_commands=sum(z['hard_only']for z in cmds),eligible_hard_only_commands=sum(z['hard_only']and g['secondary_hard']for z in cmds),all_commands=cmds))
 (P/'per-world-hard-gating.json').write_text(json.dumps(hard,indent=2)+'\n')
 latest=[g for g in actors if g['version']=='2.02'];cells=[g for g in items if g['version']=='2.02'];table=[]
 for g in latest:
  native=[p['native']for p in g['pairs']if p['native']];source=[p['source']for p in g['pairs']if p['source']];table.append(dict(area=g['area'],native_authored_candidates=len(native),source_explicit_actors_controls_platforms=len(source),native_firebars=sum(x['class_name'].startswith('FireBar')for x in native),source_firebars=sum(x['class_name'].startswith('FireBar')for x in source),native_platform_records=sum(x['class_name'].startswith('Platform')for x in native),source_platform_instances=sum(x['class_name'].startswith('Platform')for x in source),source_helper_instances=sum(x['conditional']for x in source)))
 custom=dict(Pit=dict(horizontal=True,vertical=False,evidence=['src/expanded.s:1219 fixed speed1.5px/update, jump−4.1667px/update, rising gravity~0.09723px/update²','src/expanded_weapons.s:3 flight requires flower power; cannot be assumed for a base-character gap'],reason='Ordinary higher jump supports the Samus/Ryu-like vertical policy; no intrinsic dash/second jump, so source horizontal gap/flag helpers are the conservative base-power accommodation.'),Rygar=dict(horizontal=True,vertical=False,evidence=['src/expanded.s:1219 speed1.5px/update, jump−5.5px/update, gravity~0.13889px/update²'],reason='Installed traversal jump is higher than Pit and ordinary Mario, but horizontal speed remains modest; use H helpers without inventing a V landing for a character whose native height already exceeds those low-jump profiles.'),Scrooge=dict(horizontal=True,vertical=True,evidence=['src/scrooge.s:115 ordinary jump is intentionally native DuckTales58px rise with release cut','src/scrooge.s:95 repeatable pogo is stronger; it still requires a separate Down+B action','src/expanded.s:1219 fixed speed1.5px/update'],reason='Ordinary jump is the lowest of these three; H and V support avoids requiring pogo mastery or a powerup for basic progression.'))
 (P/'custom-helper-policy-proposal.json').write_text(json.dumps(dict(status='RECOMMENDATION_ONLY_NO_GAME_EDITS_SOURCE_UNSPECIFIED',policy=custom,caveat='Constants and installed code support this conservative initial proposal; it is not a full-world native traversal proof or official2.02 parity. Use only authored source helpers, and validate every affected gap at base power before finalizing.'),indent=2)+'\n')
 newclasses=[dict(area=g['area'],source_tile=c['source_tile'],native=c['original_class'],later=c['source_class'],raw=c['source_map'])for g in cells for c in g['cells']if c['source_class']=='brick_single_coin'];assert len(newclasses)==16
 docs=R/'docs/qa/level-layout-audit-2026-10-22.md';old=(O/'revision1/report.md').read_text();parts=['','## Revision 2 — enemy, hazard, platform, and interactive-class census','',
 '**This section supersedes the earlier claim that the eight XML rows alone form the complete mechanical version-difference list.** Constructor behavior also matters: the 16 unbreakable-looking brick cells are ordinary `Ground` in hosted1.x, but `Brick` objects with a single-coin payload in2.02. The earlier B→S table describes the hosted build; it is incomplete for2.02. The exact original report, inventory and manifest are retained under `build/verification/level-layout-audit-agent/revision1/`, including their original hashes.','',
 'The supplementary inventory now includes every native enemy command, every source enemy/hazard/platform/control record, group expansion, per-world hard-only admission, and every mapped interactive cell. The intended source target record set is fully enumerated even where a native/Flash coordinate representation has no unique one-to-one pairing. No game edits were made.','',
 '### Original enemy parser and hard-only gating','',
 '- All34 native enemy streams were decoded:502 commands including page/transport controls, with407 actor/group records.','-1,628 actual compiled baseline `ProcessEnemyData` calls cover all407 actor/group records under all four primary/secondary-hard combinations. These are seeded static decoder checks with empty slots, not controller playthroughs. Page-select effects were set to the decoded command state; hard-only rejection, group class/count and24px spacing were asserted against compiled execution.','- Native secondary-hard admission is off for1-1 through5-2 and on from5-3 through8-4; primary hard mode, after completing the game, enables secondary hard everywhere and converts Goombas/groups to Beetles. These are separate from our version-behavior toggle and the Flash five-position difficulty selector.','- Group commands37..3a expand to two/three Goombas (Beetles under primary hard), and3b..3e to two/three Green Koopas; bit1 selects native Y=$70 rather than$b0. The actual group origin is `ScreenRight` when processed. The earliest aligned static origin is commandX−48px; the next members are+24px each. These nominal group positions must not be misrepresented as exact attained coordinates under every camera speed.','- Vertical-pipe Piranhas come from level construction, not the enemy stream. The inventory includes them separately. World1-1 disables them; empty enemy slots and later warp-zone cleanup can suppress/erase them. IntroPipe graphics are excluded because they do not call `VerticalPipe`.','',
 '### All-area actor/hazard/platform count inventory','',
 'These counts are authored records/instances, not simultaneously visible enemies. Native small lifts draw two platforms128px apart from one actor; Crossover stores separate platform instances. Native frenzy commands are generators, not one enemy. Maze-expanded duplicates and source helper platforms therefore legitimately change the number of records.','',
 '| Area | Native authored candidates | Crossover explicit records | Native / source firebars | Native / source platforms | Source helpers |','|---|---:|---:|---:|---:|---:|']
 for t in table:parts.append(f'| {t["area"]} | {t["native_authored_candidates"]} | {t["source_explicit_actors_controls_platforms"]} | {t["native_firebars"]} / {t["source_firebars"]} | {t["native_platform_records"]} / {t["source_platform_instances"]} | {t["source_helper_instances"]} |')
 parts+=['',
 '### Confirmed additional authored differences and representation changes','',
 '- **1-1:** the hosted build retains the native second Goomba of the late pair;2.02 removes it at source tile(128,12), as already listed. Source raw positions include the documented column deletion.','- **2-2 and7-2:** the native authored Blooper at original column71,row8 has no corresponding explicit Crossover Blooper. The full source Blooper list is retained; this conclusion is about authored data, not whether the native enemy survives slot admission in a particular run.','- **6-2:** native authored Goombas at original column68,row3 and one later grouped Goomba near column170.5 have no corresponding explicit source Goomba. Raw group coordinates and nominal origin are preserved; do not translate the group position into a camera-independent claim.','- **2-3:** four free coins move down one tile: source columns72,73,74,75 use rows6,5,5,6, where native rows are5,4,4,5. Other map geometry and helper changes are listed in revision1.','- **4-2:** the native plain brick at column128,row2 is absent from the source map.','- **2-4 lifts:** source tile(86,6)/(86,12) contains `type=constantFall` before a duplicate `type=constantRise`; tile(89,6)/(89,12) has the reverse order. Both constructors select the first occurrence. Thus the effective source left/right lift directions are reversed from native Up/Down, and the two source instances in each column are96px apart rather than the native small-lift drawing offset128px. **5-4** uses ordinary Rise-left/Fall-right records with128px-separated source instances. The raw duplicate properties are intentionally retained in the inventory.','- **Firebar speed:** native fast clockwise firebar ID1c at CastleArea3 column103,row11 is secondary-hard-only, so it appears in5-4, not first-quest2-4. Both pinned Flash engines use one106°/s `ROTATE_SPEED` for ordinary left/right bars. Native28/38 spin increments correspond to approximately105.47°/s and147.66°/s at60Hz. The fast5-4 variant therefore becomes the uniform source speed. Short/long direction and every explicit source bar location are listed separately.','- **Water fish:** native water fish are produced by frenzy controls, while the XML authors explicit fish positions. The supplementary list records all48 explicit fish instances across the relevant water areas; these are a generator-versus-placement change, not48 independently confirmed native missing enemies.','- **Lakitu, flying Cheeps, Bullet Bills and Bowser flames:** the source uses explicit start/end zone markers; native streams contain spawn/stop-frenzy commands, repeated Lakitu entries and area-frenzy level commands. Every marker/command is retained. Comparing the raw markerX to a native recordX is not a complete spawn-timing proof because native extended screen-right admission precedes that record.','- **Retainers and warp-zone control:** native Retainer/WarpZoneControl records are represented by source scenery/transport/state objects. The absence of a same-class source enemy record is not a removed Toad/Princess or a deleted warp zone.','- **Castle mazes:** all explicit source4-4/7-4/8-4 firebars, plants, platforms and controls are enumerated, including duplicated geometry. Extra source records in expanded sections must be mapped to loop/transport behavior; they are not automatically additional simultaneous obstacles.','',
 '### Complete interactive/payload class census','',
 'Every mapped cell was checked for plain brick, powerup brick, vine brick, star brick, multi-coin brick,1-up brick, question-coin/powerup, hidden-coin/1-up, free coin, used block, axe, spring, flagpole, pipe, cannon/stem, bridge and ordinary solid classes. Source-only inserted/unmapped columns are retained separately, not dropped from the comparison.','',
 '**All16 constructor changes:**','',
 '| Area | Source tile | Original NES | Hosted1.x |2.02 |','|---|---|---|---|---|']
 for c in newclasses:parts.append(f'| {c["area"]} | {tuple(c["source_tile"])} | Plain breakable brick | Ground / no payload | Brick / single coin |')
 parts+=['',
 'Besides those16 cells, the mapped census finds the four moved2-3 coins (old/new cells), the absent4-2 ceiling brick, the already documented4-4 removal, the12 conditional helper/stem source cells, and five underwater exit-pipe bottom cells represented by a native generic solid tile rather than a dedicated source pipe graphic/class. The underwater cells are2-2b(189,8),5-2b(62,8),6-2c(62,8),7-2b(189,8),8-4b(69,8). Their portals are not inferred solely from tile appearance; transport commands remain in the separate graph inventory.','',
 'The remainder of powerup/star/vine/1-up/question/hidden/multi-coin classifications agrees in the mapped spans. This is a class/content census, not proof of equal lifecycle timing: both Flash Brick implementations use a6000ms multi-coin timer and a14-coin cap, and native hidden1Ups have their own appearance gate. Actual item emergence, ammo inventories, pickup animation and collection behavior remain separate runtime tests.','',
 '### Complete location lists and anchor caveats','',
 '- `spawn-revision2/complete-enemy-object-list.csv`: every authored native/source enemy, hazard, platform and control, with original record bytes/offsets, native anchor, geometry-aligned anchor, exact source tile/anchor, class and hard admission.','- `spawn-revision2/all-enemy-object-comparisons.json`: the complete structured records, including group provenance and compiled initialization results.','- `spawn-revision2/complete-interactive-differences.csv` and `all-interactive-comparisons.json`: every interactive class difference, including cells in inserted/unmapped columns.','- `spawn-revision2/original-level-commands.json`: every original level command, including Piranha-producing pipes and frenzy/loop controls; `original-enemy-commands.json` retains all enemy/page/transport/group commands.','- `spawn-revision2/per-world-hard-gating.json`: each area’s native secondary-hard state and gated records.','',
 '**Candidate pairings are not silently promoted to proven moves.** Equal anchors are literal after the documented static alignment. Other rows retain their delta or remain unmatched. Moving-platform initial positions versus oscillation centers, flying-enemy launch phases, maze clones, deleted native columns, screen-right generators and source scene-graph objects can prevent a unique one-to-one association. The full source target list is still exact and available for implementation; no coordinate is invented to make a comparison pass. Runtime slot exhaustion, hidden1Up admission, frenzy timing, scrolling thresholds and maze traversal still require native playthrough evidence.','',
 '### Proposed helper masks for our custom characters','',
 'These are **port recommendations**, not official2.02 behavior, and no game changes were made. All three have installed dry horizontal speed1.5px/update. Do not require a flower or an advanced technique to clear a basic mandatory gap. Use existing authored source helpers rather than inventing new platforms.','',
 '| Custom character | Proposed H | Proposed V | Installed capability motivating the proposal |','|---|---|---|---|','| Pit | yes | no | Base jump−4.1667px/update and rising gravity≈0.09723px/update²; flower-only flight cannot be assumed |','| Rygar | yes | no | Adapted higher jump−5.5px/update and gravity≈0.13889px/update²; modest horizontal speed, no intrinsic dash/second jump |','| Scrooge | yes | yes | Ordinary jump deliberately follows the native58px rise; stronger repeatable pogo requires a separate Down+B action |','',
 'Pit/Rygar’s higher ordinary jumps support a Samus/Ryu-like vertical policy; Scrooge’s lower ordinary jump supports the Bill/Link/MegaMan-style V accommodations. These recommendations are derived from installed constants and mechanics, not verified full-world traversal bounds. Confirm at base power in both behavior modes and every affected gap before treating the masks as final.','',
 'Revision2 remains audit-only. Its decoder checks and inventories strengthen the pre-change full list; they do not finish the overarching roster/weapon/recording goal.','']
 appendix='\n'.join(parts)
 # Tidy prose without changing code, hashes, level IDs or exported evidence.
 pieces=re.split(r'(`[^`]*`)',appendix)
 for i in range(0,len(pieces),2):pieces[i]=re.sub(r'(?<=[A-Za-z])(?=\d)',' ',pieces[i]);pieces[i]=re.sub(r'(?m)^-(?=\d)','- ',pieces[i]);pieces[i]=re.sub(r'(?<=[A-Za-z)])\.(?=\d)', '. ',pieces[i])
 appendix=''.join(pieces)
 notice='> **Revision 2:** The enemy/object and interactive census below supersedes revision1’s coarse B→S interpretation for2.02 and its XML-only completeness statement. Original revision1 files/hashes are preserved in the evidence history.\n\n'
 docs.write_text(old.replace('\n\n','\n\n'+notice,1)+appendix,encoding='utf-8')
 inventory=R/'docs/qa/level-layout-audit-2026-10-22.json';j=json.loads((O/'revision1/inventory.json').read_text());j['revision']=2;j['revision2']=dict(path=P.relative_to(R).as_posix(),compiled_spawn_calls=len(cases),all_34_enemy_streams_decoded=True,enemy_commands=sum(map(len,parsed.values())),actor_group_records=len(cases)//4,interactive_constructor_changes=newclasses,custom_helper_recommendation=custom,comparison_limits='Complete authored source/native records; candidate coordinate pairing is not runtime spawn/collision equivalence. Exact records remain available even when alignment/phase/maze semantics are ambiguous.');inventory.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
 manifest=dict(revision=2,status='AUDIT_ONLY_COMPLETE_AUTHORED_SPAWN_AND_INTERACTIVE_CENSUS',game_code_changed=False,ROM_changed=False,compiled_spawn_calls=len(cases),source_fingerprints=record(R/'reference/crossover2/source.swf'),prior_manifest=record(O/'revision1/manifest.json'),files=[record(p)for p in sorted(P.rglob('*'))if p.is_file()]+[record(docs),record(inventory),record(Path(__file__))],goal_complete=False)
 (O/'revision2-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 total=sum(p.stat().st_size for p in O.rglob('*')if p.is_file());assert total<150_000_000
 print('REVISION2 SAVED',len(cases),'compiled cases, bytes',total,'REPORT SHA',record(docs)['sha256'])
def main():
 P.mkdir(exist_ok=True)
 history=O/'revision1'
 if not history.exists():
  history.mkdir()
  for src,dst in[(R/'docs/qa/level-layout-audit-2026-10-22.md','report.md'),(R/'docs/qa/level-layout-audit-2026-10-22.json','inventory.json'),(O/'summary.json','summary.json')]:shutil.copyfile(src,history/dst)
  (history/'manifest.json').write_text(json.dumps(dict(files=[record(p)for p in history.iterdir()if p.is_file()]),indent=2)+'\n')
 ss=streams(R/'.upstream/smb1base/src/level_tiles.s');parsed={k:parse(k,v)for k,v in ss.items()if k.startswith('E_')};(P/'original-enemy-commands.json').write_text(json.dumps(parsed,indent=2)+'\n')
 cache=P/'compiled-spawn-decoder.json'
 cases=json.loads(cache.read_text())if cache.exists()else native_reexecute(parsed)
 cache.write_text(json.dumps(cases,indent=2)+'\n')
 actors,items=generate_comparison(parsed,cases);finalize(parsed,cases,actors,items)
if __name__=='__main__':main()
