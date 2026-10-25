"""Publish the read-only level audit and full, reviewable source inventories."""
from pathlib import Path
import collections,csv,hashlib,json,math,re,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
from level_layout_inventory_agent import R,O,load,record
from level_layout_compare_agent import classify,nc
DOC=R/'docs/qa/level-layout-audit-2026-10-22.md'
EARLY=R/'reference/crossover/assets/45_com.smbc.level.LevelData_LevelDataXML.bin'
LATE=R/'reference/crossover2/extracted/binaryData/322_com.smbc.level.LevelData_LevelDataXML.bin'
S1='reference/crossover/decompiled/scripts/com/smbc/'
S2='reference/crossover2/extracted/scripts/com/smbc/'
CHARS=['Mario','Luigi','Bill','Link','MegaMan','Samus','Simon','Ryu','Sophia','Bass']
H={'Bill','Link','MegaMan','Samus','Simon','Ryu'};V={'Bill','Link','MegaMan','Sophia'}
EARLYCHARS={'Mario','Bill','Link','MegaMan','Samus','Simon'}
def elig(vi,layer,value):
 chars=EARLYCHARS if vi==0 else set(CHARS)
 if 'charHorz'in value and(vi==1 or layer=='PICKUPS'):chars=chars&H
 if 'charVert'in value and(vi==1 or layer=='MAP'):chars=chars&V
 return sorted(chars)
def helper(vi,area,layer,x,y,value):
 d=dict(version=('hosted_1x','2.02')[vi],area=area,layer=layer,tile=[x,y],NES_tile_origin=[16*x,16*y],source_raw=value,eligible_characters=elig(vi,layer,value),visibility='Object is omitted completely for ineligible characters; not merely invisible.')
 if layer=='PICKUPS':
  w=int(re.search(r'width=(\d+)',value)[1])*8;cx=x*16+8+(8 if'shiftRight'in value else 0);cy=y*16;typ=re.search('type=([^&]+)',value)[1]
  d.update(kind='moving_platform',center=[cx,cy],width=w,height=8,rectangle_at_phase_zero=[cx-w/2,cy,cx+w/2,cy+8],motion=typ,amplitude_NES_px=30 if typ=='waveHorizontal'else 75,angular_speed_rad_s=1.5 if typ=='waveHorizontal'else 1,period_s=2*math.pi/(1.5 if typ=='waveHorizontal'else 1),initial_phase_rad=0,motion_clock='Updates only while onScreen or updateOffScreen; the latter defaults false. Phase is not global time since power-on.')
 else:d.update(kind='solid_mushroom_top'if value.startswith('ground')else'decorative_mushroom_stem',rectangle=[x*16,y*16,(x+1)*16,(y+1)*16]if value.startswith('ground')else None)
 if vi==0 and layer=='PICKUPS'and'charVert'in value:d['visibility']='Hosted build does not filter PICKUPS.charVert; appears for all six characters despite the tag.'
 return d
def main():
 maps=[load(EARLY),load(LATE)];inv=json.loads((O/'xml-inventory.json').read_text());match=json.loads((O/'topology-comparison.json').read_text());align=json.loads((O/'static-column-alignments.json').read_text());bind=json.loads((O/'source-binding.json').read_text());helpers=[];objects=[]
 for vi,m in enumerate(maps):
  for area,a in m.items():
   for layer in ('MAP','PICKUPS'):
    for y,row in enumerate(a[layer]):
     for x,v in enumerate(row):
      if v=='0':continue
      objects.append(dict(version=('hosted_1x','2.02')[vi],area=area,layer=layer,x_tile=x,y_tile=y,NES_x=x*16,NES_y=y*16,raw=v))
      if 'charHorz'in v or'charVert'in v:helpers.append(helper(vi,area,layer,x,y,v))
 with(O/'all-source-cells.csv').open('w',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=objects[0].keys());w.writeheader();w.writerows(objects)
 differences=[]
 for key,a in maps[0].items():
  b=maps[1][key]
  for y,row in enumerate(a['MAP']):
   for x,v in enumerate(row):
    u=b['MAP'][y][x]
    if v==u:continue
    conditional=('charHorz'in v or'charVert'in v or'charHorz'in u or'charVert'in u)
    if conditional or classify(v)!=classify(u):
     gates=lambda s:tuple(k for k in('charHorz','charVert')if k in s)
     category='conditional_visual_rename'if conditional and classify(v)==classify(u)and gates(v)==gates(u)else'conditional_support'if conditional else'static_topology'
     differences.append(dict(area=key,layer='MAP',tile=[x,y],early=v,later=u,category=category))
  for y,row in enumerate(a['PICKUPS']):
   for x,v in enumerate(row):
    u=b['PICKUPS'][y][x]
    if v!=u:differences.append(dict(area=key,layer='PICKUPS',tile=[x,y],early=v,later=u,category='enemy_removal'if v.startswith('enemy')else'helper_platform'))
 sources=[record(p)for p in[EARLY,LATE,R/'reference/crossover/super-mario-crossover.swf',R/'reference/crossover2/source.swf',R/(S1+'level/Level.as'),R/(S2+'level/Level.as'),R/(S1+'ground/Platform.as'),R/(S2+'ground/Platform.as'),R/(S2+'data/HitTester.as'),R/(S2+'pickups/Teleporter.as'),R/(S2+'data/GameSettings.as'),R/(S2+'data/Cheats.as')]]
 for vi,folder in enumerate((S1,S2)):
  for char in CHARS:
   p=R/(folder+'characters/'+char+'.as')
   if p.exists():sources.append(record(p))
 report=dict(status='AUDIT_ONLY_NO_LEVEL_OR_GAMEPLAY_EDITS',version_contract=dict(hosted_1x='Six-character site SWF; exact1.0/1.x patch not embedded/proven. Do not label it an independently authenticated1.0 release.',later='2.02 explicitly declared by GameSettings; original2.0.0 not separately authenticated.'),sources=sources,current_binding=bind,campaign_levels=32,campaign_areas=61,later_internal_areas=['9-1a','9-2a','9-8a','9-9a'],all_source_cells_csv='build/verification/level-layout-audit-agent/all-source-cells.csv',helpers=helpers,confirmed_version_structural_differences=differences,raw_version_difference_count=len(inv['version_differences']),raw_version_differences='build/verification/level-layout-audit-agent/xml-inventory.json',NES_static_alignment='build/verification/level-layout-audit-agent/static-column-alignments.json',NES_cell_differences='build/verification/level-layout-audit-agent/topology-comparison.json',current_port_missing_campaign_helper_platforms=34,current_port_missing_conditional_mushroom_top_cells=5,limitations=['Exact1.0 and2.0.0 releases not independently authenticated.','Original means upstream SMB1Base authored streams at pinned46ff88f7d9e854db80bf8d50e5bf74340fcc64ce; no separately acquired Nintendo ROM is represented as a verified byte oracle.','The static NES column inventory executes compiled baseline6502 parser calls with authored hidden1Ups enabled, not a controller replay. It does not simulate castle loopback or transport routes.','Sequence alignments expose all literal static differences but are not approved relocation recipes; repeated empty/floor columns can have multiple equivalent alignments.','Enemy spawn groups, enemy-slot exhaustion, frenzy actors, per-world native hard flags and full runtime obstacle equivalence are not certified by the static topology comparison.','Pit/Rygar/Scrooge have no official2.02 helper-mask specification. Lance should inherit Bill only if the alternate-character contract is retained.','Current Easy/Hard mode selects behavior versions; it is not the officialFlash five-position difficulty setting.'])
 (R/'docs/qa/level-layout-audit-2026-10-22.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 transport=[z for z in objects if z['layer']=='PICKUPS'and any(s in z['raw']for s in('Transporter','teleporter','vineTransfer','platform'))]
 with(O/'platforms-and-transports.csv').open('w',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=objects[0].keys());w.writeheader();w.writerows(transport)
 lines=['# Crossover level-layout audit — 2026-10-22','','**Audit only: no game level data, gameplay code, ROM, or checkpoint was changed by this audit.** Every campaign level and subarea in both pinned XML datasets was enumerated before any proposed map implementation.','',
 'The immediate missing feature is real: Crossover authors additional moving platforms and mushroom ledges, selected by character. The current ROM retains all68 original SMB1Base level/enemy streams byte for byte on both mappers and has no corresponding character-helper dataset. These accommodations must be implemented with their source eligibility, rather than widening every gap for everyone.','',
 '## Version and evidence contract','',
 '- The hosted six-character reference is the requested site SWF, SHA-256 `46bdcf0b60721bbe0f006cdb083f503e0312feacede6f65f2942f7a5a406b1eb`. Its decompiled `StatManager.NUM_CHARACTERS` is6. No embedded release-version string was found in its game scripts. It is called **hosted1.x** here; this is not authentication of an exact1.0 release.','- The later SWF SHA-256 is `6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af`. `GameSettings.as:68` explicitly declares2.02. Exact2.0.0 has not been separately obtained/authenticated.','- The NES comparison baseline is the authored SMB1Base streams at upstream commit `46ff88f7d9e854db80bf8d50e5bf74340fcc64ce`. All34 level streams plus34 enemy streams match the baseline MMC3 and both current mapper images exactly. `source-binding.json` gives per-stream hashes and compiled offsets. This proves data identity, not that patched runtime behavior is identical to Nintendo SMB1.','- The comparison covers32 campaign levels /61 areas in each version.2.02 also embeds9-1a,9-2a,9-8a,9-9a, which are outside the32-level campaign. `CharacterSelect.FULL_LEVEL_STR` explicitly uses9-1a. They must not be imported as four new campaign levels.','- Full raw differences, including skin/name changes, are in `xml-inventory.json`. Every nonzero source tile/object from both versions is in `all-source-cells.csv`; every moving platform and transport is in `platforms-and-transports.csv`. Nothing is omitted merely because it is outside1-1/2-2.','',
 '## Exact conditional object rules','',
 '| Character | Hosted1.x horizontal / vertical family |2.02 horizontal / vertical family |','|---|---|---|']
 for c in CHARS:lines.append(f'| {c} | '+(('yes'if c in H else'no')+' / '+('yes'if c in V else'no')if c in EARLYCHARS else'not present')+' | '+('yes'if c in H else'no')+' / '+('yes'if c in V else'no')+' |')
 lines+=['','The protected booleans default to false; only the explicit constructor assignments enable them. Mario/Luigi/Bass therefore have neither family. Pit, Rygar and Scrooge were not official2.02 characters; their helper policy is undefined by that source. Our Lance alternate is not a separate2.02 class.','',
 '**Hosted1.x filtering is asymmetric.** `Level.as:1288–1295` filters `PICKUPS.charHorz` using the horizontal flag, and `MAP.charVert` using the vertical flag. It does not filter `PICKUPS.charVert`. Consequently the tagged8-1,8-2 and8-4c moving platforms appear for all six characters in that reference.2.02 `Level.as:914–934` filters both tags in both layers. Do not apply the later filtering retroactively and claim literal hosted behavior.','',
 '## Complete character-specific platform list','',
 'Coordinates below are zero-based XML tile origins and NES-normalized platform centers/top Y. Flash coordinates are twice the NES coordinates. Width is measured in8-NES-pixel units: `width=2` is16px, `width=4` is32px and `width=6` is48px; height is8px. `shiftRight` adds8px to the ordinary tile-center anchor. **These are source coordinates, not automatic NES insertion coordinates.** Native level columns sometimes differ; the1-1 example below demonstrates the necessary landmark alignment.','',
 '| Area | XML tile(x,y) | NES center/top(x,y) | Width | Motion | Hosted1.x eligibility |2.02 eligibility |','|---|---:|---:|---:|---|---|---|']
 groups={}
 for h in helpers:
  if h['kind']!='moving_platform' or h['area'].startswith('9'):continue
  groups.setdefault((h['area'],tuple(h['tile'])),{})[h['version']]=h
 for key,g in sorted(groups.items()):
  h=g.get('2.02',g.get('hosted_1x'));e=g.get('hosted_1x');late=g.get('2.02');fmt=lambda z:('all six (unfiltered tag)'if z and z['version']=='hosted_1x'and'charVert'in z['source_raw']else'H'if z and'charHorz'in z['source_raw']else'V'if z else'absent')
  lines.append('| '+h['area']+' | '+str(tuple(h['tile']))+' | '+str(tuple(h['center']))+' | '+str(h['width'])+' | '+h['motion']+' | '+fmt(e)+' | '+fmt(late)+' |')
 lines+=['','H and V mean the horizontal and vertical character sets in the preceding table. There are31 campaign moving helpers in hosted1.x and34 in2.02. All are absent from the current port. The four water helpers are not generic replacements for swimming physics: source water-mode behavior and actual moving-platform collision must both match.','',
 'Platform trajectories are `x = centerX + sin(angle)*30` NES pixels, angle increasing1.5rad/s for horizontal motion (period4.1887902s), and `y = centerY + sin(angle)*75`, angle increasing1rad/s for vertical motion (period6.2831853s), initially phase0. Their maximum speeds are45 and75 NES pixels/s respectively. The source platform is a `Ground` object in the `HT_PLATFORM` collision category, uses previous/current platform hit rectangles, and carries supported characters through their platform-ground response. It is not a coin/enemy sprite with a decorative animation. Its8px-tall rectangular hit shape is confirmed by both SWF shape bounds and the2.02HRect placement. Native8-bit phase/table quantization must be documented and tested when ported.','',
 'Hosted1.x has no platform-width difficulty shrink.2.02 nativeFlash difficulty HARD subtracts2 width units with a minimum2; VERY_HARD clamps all to2. The source selector has five positions. **Our Easy/Hard behavior toggle is a different setting** and does not by itself authorize these additional enemy/platform difficulty modifiers.','',
 '###1-1 flagpole example','',
 'The source helper is tile(192,4), center(3088,64),16×8px, horizontal sine motion, H characters only. The source flagpole is column197, but native SMB1Base uses column198 because the hosted map removes a column after the first pipe. Thus placing a helper blindly at3088 on the existing NES map would be16px left of the source-relative position. Preserving current NES geometry requires center3104,64 to retain the source64px offset before the flagpole; alternatively the entire source layout must be adopted consistently. This is why positions in the inventory are not direct patch bytes.','',
 '## Complete conditional static terrain list','',
 '| Area / versions | Source cells | What exists | Eligibility |','|---|---|---|---|','|4-3a / both |(30,7),(31,7),(32,7) | Three16×16px mushroom-top cells, rectangle480..528 ×112..128 | V |','|4-3a / both |(31,8)..(31,14) | Mushroom stems beneath that support; decorative and non-solid | V |','|3-3a /2.02 only |(34,14),(35,14) | Two16×16px mushroom-top cells, rectangle544..576 ×224..240 | H |','',
 'The4-3 helper is orange in hosted1.x and reuses themed green names in2.02. That name/color conversion is not a new ledge geometry. No other conditional static cells occur anywhere in the61 campaign areas.','',
 '## Complete structural change list between the two pinned Crossover datasets','',
 '| Area | Tile(s) | Hosted1.x →2.02 |','|---|---|---|','|1-1a |(128,12) | Remove one Goomba (`enemyGoombaBrown&&shiftRight&&`); all other pickup-layer objects remain unchanged |','|2-3a |(108,13) | Add16×8 horizontal H helper at center1744,208 |','|3-3a |(34,14),(35,14) | Add the H mushroom landing above |','|4-4a |(161,10),(225,10) | Remove two solid dungeon cells |','|7-3a |(108,13) | Add the same16×8 horizontal H helper at center1744,208 |','|8-1a |(223,13) | Platform tag charVert→charHorz; hosted constructor formerly admitted all six;2.02 admits H |','|8-1a |(316,13) | Add16×8 horizontal H helper at center5064,208 (no shiftRight) |','|8-2a |(150,12) | Platform tag charVert→charHorz; hosted constructor formerly admitted all six;2.02 admits H |','|8-4c |(23,13) | Raw object unchanged, but constructor fix changes effective admission from all six to V only |','',
 'The first eight rows cover every campaign cell whose collidable class/conditional support or pickup record differs. The final row is a runtime filtering change, so it cannot be detected by XML diff alone. All other pickup/transport/enemy records and campaign map dimensions are identical across the two XML datasets. There are many visual/theme-name changes; the full raw list is retained and must not be mistaken for thousands of new obstacles.','',
 '## NES baseline versus Crossover — every area','',
 'The following table covers every campaign subarea. `NES span` gives the corresponding authored native area and original column start. A span summary is an exact sequence alignment of solid/item/brick/hidden/spring/flag classes, excluding character helpers and scenery. Detailed source cells, raw NES tile IDs and original/replacement coordinate ranges are retained in `static-column-alignments.json`. It exposes authoring shifts and interactive-type changes; it does not infer that each ambiguous floor-column alignment is an intentional design change. Castle maze caveats follow.','',
 '| Crossover area | Width | NES span | Literal static differences / representation |','|---|---:|---|---|']
 amap={z['area']:z for z in align}
 for z in sorted(match,key=lambda z:z['area']):
  a=amap[z['area']];ops=[]
  for op in a['column_operations']:
   ops.append(op['operation']+' NES['+','.join(map(str,op['original_columns']))+') → C['+','.join(map(str,op['crossover_columns']))+')')
  text='; '.join(ops)or'No static topology/type difference in the compared span'
  if a['caveat']:text+='; native loop/transport representation differs'
  lines.append('| '+z['area']+' | '+str(a['crossover_width'])+' | '+a['original_area']+' +'+str(a['offset'])+' | '+text+' |')
 lines+=['',
 'The small one-column changes near many castles are the original breakable-brick tile used in exit artwork versus a noncollidable Crossover castle sprite, not a newly authored giant gap. The1-1,1-2,1-4,3-1,4-1 and7-3 alignments also reveal actual inserted/deleted columns and therefore shifted downstream coordinates.5-2 and6-2 contain explicit breakable-brick→unbreakable-ground representations (exact cells below). Cloud and water bonus areas sometimes omit or add trailing padding columns. These differences are fully recorded, but padding and exit-art collisions must be distinguished from an obstacle that players can actually encounter.','',
 '### Breakable/solid class replacements in unchanged spans','']
 for a in align:
  for op in a['column_operations']:
   if op['operation']!='replace' or op['original_columns'][1]-op['original_columns'][0]!=op['crossover_columns'][1]-op['crossover_columns'][0]:continue
   oc={(z['x'],z['y']):z for z in op['original_cells']};cc={(z['x'],z['y']):z for z in op['crossover_cells']};dx=op['original_columns'][0]-op['crossover_columns'][0]
   cells=[]
   for(x,y),z in cc.items():
    old=oc.get((x+dx,y))
    if old and old['value']!=z['value']:cells.append(f'({x},{y}) {old["value"]}→{z["value"]} `{z["raw_tile"]}`')
   if cells:lines.append('- '+a['area']+': '+', '.join(cells)+'.')
 lines+=['',
 'B means breakable brick; S means solid non-brick terrain. These are authored static classifications, not a promise that every current projectile already respects the distinction.','',
 '### Castle loops and shared rooms','',
 'Crossover4-4 and7-4 use explicit `teleporterCheckPoint`, `teleporterStart`, `teleporterStartOne` and `teleporterEnd` records, with extra repeated geometry laid out in the XML. Original SMB1 instead rewinds four native pages using `LoopCmdWorldNumber/PageNumber/YPosition` and multi-loop counters.8-4 splits the native castle/water route into8-4a/b/c and duplicates a64-column section in8-4a. Its source teleporter at column110,180,317 and pipe-network destinations are recorded verbatim in `platforms-and-transports.csv`. Those are representations of a maze/transport graph, not permission to append all XML columns into one native linear room. A runtime path-by-path maze parity test is required before translating those sections.','',
 'Original SMB1 shares one underground bonus-area stream across many worlds and shares main geometry for1-3/5-3,2-3/7-3,2-2/7-2,1-4/6-4 and2-4/5-4. Crossover expands them into per-level XML areas and can assign different pickups/helpers. The source area IDs must therefore remain part of a helper key; a blanket change to a shared native stream would affect unrelated worlds.','',
 '## Difficulty, skins, and other global level behavior','',
 '-2.02 has one32-level campaign XML. Map skins select graphics/music/theme conventions, not independent1.0/2.0 campaign maps. The developer explicitly announced difficulty-dependent layouts and the SMB Special campaign as **new3.0 features**: [official3.0 announcement](https://explodingrabbit.com/super-mario-crossover-3-0-trailer-304/). Lost Levels was described there as a future addition. Do not import3.x/Special/Lost Levels layouts into this2.02 audit.','- NativeFlash HARD replaces Goombas with Beetles; VERY_HARD uses SpikeTops (`Level.as:1076–1088`). Platform width changes are described above. Those settings must remain distinct from our version-behavior selector.','-2.02 allows leftward camera scrolling by default (`screenScrollsLeft = !Cheats.classicScreenScroll`, default cheat false). Native NES SMB1 permanently discards the left camera edge. This affects traversal/backtracking but is not a missing platform; adding helpers does not implement it.','- Pipe/vine/warp transport and castle checkpoint records are fully inventoried. Their XML records are identical across both pinned campaign datasets except the six pickup changes already listed; their native engine implementations differ.','- The current cannon/firebar repairs are runtime changes and do not add the authored Crossover helper platforms. Failing to clear a gap with one controller policy is not evidence that the gap should be filled. Bass has a source dash/double-jump route; the root has separately verified his current ordinary route through2-2.','',
 '## Concrete implementation checklist — review this list before changes','',
 '1. Keep this inventory/report as the pre-change evidence. Bind any implementation to the chosen pinned version per behavior mode; exact1.0/2.0.0 files remain an explicit provenance gap.','2. Add an area/world-keyed accommodation table containing all31 hosted or34 later campaign moving helpers and the conditional3-3/4-3 static supports. Include hidden/visible admission by actual constructor semantics above. Make no unrequested family assignment for Pit/Rygar/Scrooge.','3. Translate source coordinates using explicit corresponding landmarks/column mapping. Decide consistently whether to adopt the literal source column edits or retain native geometry with source-relative helper anchors; record the choice for every shifted area.1-1 is already a concrete16px discrepancy.','4. Implement real16/32/48×8 platform collision, sine trajectories, phase/timing, sprite rendering, enemy-slot behavior and camera-relative position. A helper must not consume a native enemy slot in a way that silently removes enemies/firebars. Test platform carry, top landing, side/underside contact, offscreen lifetime and pause behavior for both mappers.','5. Apply the confirmed2.02-only changes deliberately:2-3/7-3 helper additions,3-3 landing,8-1 extra helper and corrected8-1/8-2 gates,8-4c effective gate,4-4 two removed cells,1-1 Goomba removal. Do not call generic skin renames gameplay changes.','6. Review the complete native/Crossover static alignment inventory, including native shared-room effects, explicit unbreakable bricks in5-2/6-2 and moved columns in1-1/1-2/1-4/3-1/4-1/7-3. Resolve maze/transport graph equivalence before changing4-4/7-4/8-4 or blindly copying expanded XML room lengths.','7. Run ordinary controller routes through every changed accommodation for all eligible and ineligible characters, plus water-mode and native map-sharing counterexamples. Test Easy/Hard independently and retain native screenshots/replays showing platform motion and landings. Include1-1 flagpole,2-2/7-2 water gaps,2-3/7-3 bridge gap,3-3 low landing,4-3 mushroom climb,8-1 and8-2 long gaps,8-4 final gap.','8. Recheck the complete14-identity roster through2-2 and all remaining-world obstacle/maze transitions; profile dense helper+enemy scenes on MMC3/MMC5. Preserve30GB workspace cap by archiving captures outside the project.','',
 '## What this audit does not certify','',
 'This is an exhaustive authored-data inventory of both pinned XML datasets and the current68 native level/enemy streams. It is not an authenticated exact1.0-versus2.0.0 archive comparison, a liveFlash playthrough, or a completed runtime equivalence proof for every enemy/maze/transport. Native column decoding uses the actual compiled6502 parser with authored hidden1Ups enabled; those seeded static calls are map extraction and are never offered as controller clears. The diagrams are source-map schematics, not game screenshots. No level implementation has been silently bundled into this report.','']
 content='\n'.join(lines)
 content=content.replace('###1-1','### 1-1')
 content=content.replace('Native8-bit','Native 8-bit')
 content=content.replace('Native8','Native 8')
 # Keep ordinary prose readable while preserving hashes, code and level IDs.
 chunks=re.split(r'(`[^`]*`)',content)
 for j in range(0,len(chunks),2):
  chunks[j]=chunks[j].replace('SMB1Base','SMB_BASE_PROTECTED').replace('MMC3','MMC_THREE_PROTECTED').replace('MMC5','MMC_FIVE_PROTECTED')
  chunks[j]=re.sub(r'(?<=[A-Za-z])(?=\d)', ' ',chunks[j])
  chunks[j]=re.sub(r'(?<=[A-Za-z)])\.(?=\d)', '. ',chunks[j])
  chunks[j]=re.sub(r'(?m)^-(?=\d)', '- ',chunks[j])
  chunks[j]=chunks[j].replace('SMB_BASE_PROTECTED','SMB1Base').replace('MMC_THREE_PROTECTED','MMC3').replace('MMC_FIVE_PROTECTED','MMC5').replace('NativeFlash','Native Flash').replace('liveFlash','live Flash').replace('hidden 1Ups','hidden 1-up blocks')
 content=''.join(chunks)
 content=content.replace('Native 8-bit phase/table quantization must be documented and tested when ported.','Native 8-bit phase/table quantization must be documented and tested when ported. Motion updates only while the platform is on screen or requests offscreen updates; both versions default the latter flag to false. Therefore its initial phase is not measured from global power-on time.')
 DOC.write_text(content,encoding='utf-8')
 # Compact, explicitly labeled schematics for reviewing the accommodations.
 crops=[('1-1a',182,204),('2-2b',124,172),('3-3a',24,45),('4-3a',22,43),('8-1a',212,231),('8-1a',304,327),('8-2a',140,163),('8-4c',14,38)]
 image=Image.new('RGB',(1000,len(crops)*230+50),(22,25,35));d=ImageDraw.Draw(image);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15);d.text((12,10),'SOURCE-MAP SCHEMATICS - NES-normalized; not emulator screenshots',fill='white',font=font);colors={'S':'#5f7896','B':'#b77845','Q':'#ecb336','H':'#eadba9','J':'#da4545','F':'#75ba50'}
 for idx,(key,left,right)in enumerate(crops):
  y0=50+idx*230;a=maps[1][key];scale=min(20,950/(right-left));d.text((12,y0),f'2.02 {key} - columns {left}..{right-1}; magenta = conditional helper at phase 0',fill='white',font=font)
  for y,row in enumerate(a['MAP']):
   for x in range(left,min(right,len(row))):
    c=classify(row[x]);
    if c!='0':
     fill='#f14de0'if 'char'in row[x]else colors[c];x0=16+(x-left)*scale;y1=y0+25+y*11;d.rectangle((x0,y1,x0+scale-1,y1+10),fill=fill)
  for h in helpers:
   if h['version']!='2.02'or h['area']!=key or h['kind']!='moving_platform':continue
   x,y=h['center'];cx=16+(x/16-left)*scale;yy=y0+25+y/16*11
   if left<=x/16<right:
    half=h['width']/32*scale;d.rectangle((cx-half,yy,cx+half,yy+5),fill='#f14de0')
    if h['motion']=='waveHorizontal':d.line((cx-30/16*scale,yy+8,cx+30/16*scale,yy+8),fill='#f14de0')
    else:d.line((cx+half+4,yy-75/16*11,cx+half+4,yy+75/16*11),fill='#f14de0')
 image.save(O/'helper-map-schematics.png')
 total=sum(p.stat().st_size for p in O.rglob('*')if p.is_file());assert total<150_000_000
 print(json.dumps(dict(report=str(DOC),structured=str(DOC.with_suffix('.json')),source_cells=len(objects),helpers=len(helpers),campaign_later_platform_helpers=sum(z['version']=='2.02'and z['kind']=='moving_platform'and not z['area'].startswith('9')for z in helpers),confirmed_version_difference_records=len(differences),audit_bytes=total),indent=2))
if __name__=='__main__':main()
