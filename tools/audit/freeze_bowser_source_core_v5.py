"""Freeze executable two-Bowser source leaf and explicit ungranted host request."""
from pathlib import Path
import hashlib,json,re,zipfile
from PIL import Image
R=Path(__file__).resolve().parents[2];O=R/'build/bowser-source-core-v5';P=R/'build/coherent62-lives-fixes-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not(O/'handoff.json').exists();q=json.loads((O/'controls-v5.json').read_text());assert q['passed']
 for p,h in q['bindings'].items():assert sha(p)==h
 labels={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.([^\s]+)$',(O/'arena.lbl').read_text(),re.M)}
 # Honest source-palette approximation, no native RGB installation claim.
 raw=(O/'arena.bin').read_bytes();chr=(O/'bowser1.chr').read_bytes();colors=[(0,0,0,0),(0,168,0,255),(255,254,255,255),(252,152,56,255)]
 for side in ['RIGHT','LEFT']:
  at=labels['Bw1OPEN1'+side]-0x8000;n=raw[at];rec=raw[at+1:at+1+n];im=Image.new('RGBA',(32,40))
  for tile,attr,y,x in zip(rec[::4],rec[1::4],rec[2::4],rec[3::4]):
   for yy in range(16):
    row=15-yy if attr&128 else yy;off=(tile+row//8)*16+row%8
    for xx in range(8):
     bit=xx if attr&64 else 7-xx;v=(chr[off]>>bit&1)|((chr[off+8]>>bit&1)<<1)
     if v:im.putpixel((x+xx,y+yy),colors[v])
  im.save(O/('bowser1-'+side.lower()+'.png'))
 api=dict(selected_identity=dict(menu_slot=26,raw_owner=27,variants={'0':'SMB3','FmAlts08':'SMB1'}),
  source_core={'Bw3Step':'A=actualNESinput; original3 4.4 integration/jump/gravity/breath/alignment/rapidpound. World callback must genuinely consume current SMB world; AXY/P volatile.',
  'Bw1Step':'A=actualNESinput; native1 Bowser down-only gravity/jump, original20tick mouth close. Authored1px directional control; no original player-Bowser controls exist.',
  'BwWorldResolve':'Unimplemented import. Set actual grounded, settle source world/page/head/side/feet; preserve body position and detect genuine floor-smash eligibility; abstract floor176 is not host proof.',
  'BwEmit':'One-update source fire event: source3 original3F->10, source1 mouth20expiry. Actual friendly original fire pools/contact/render/audio NOT yet joined.',
  'BwImpact':'One-update source3 landing event after original10tick align/rapidfall+6. Native eligible block destruction/scoring/buffer budget NOT yet joined.'},
  planned_36service_contracts={'0':'owned movement import/export + actual source tick once','1':'graphics/body metadata publication','2':'early owner fire OAM without duplicating body0','15':'constructor AFTER realIcGlobalInit','17':'actual native DrawMetasprite on cold/lives','18':'full distinct SMB1/SMB3 names','19':'nativeJnReset once then source scene reset','24':'genuine earned item/progression','26':'deferred original bodyP0 + native universal donor','29':'once UI palette retry','30':'actual native lives text then7Bbody only','32':'genuine native world donor','34':'actual fire/contact update exactlyonce'},
  natural_routes_not_claimed=True)
 (O/'host-API-proposal.json').write_text(json.dumps(api,indent=2)+'\n')
 proposal=dict(status='REQUEST_ONLY_NO_HOST_ALLOCATION_OR_LINK',parent=sha(P/'joint/candidate.nes'),measured=q['measured'],
  requests={'CHR_body':'824..<827 three physical1KB pages, currently zero; originalpacket only proposed824..<832, no grant inferred. Reserve827..<828 only if authentic fire extraction fits/qualifies.',
  'carrier':'Eight CHR pages927..<935 proposed AFTER explicitly protectedBT915..<927 and Benj901..<915. No allocation assumed.',
  'PRG_RAM':'Request family27 temporal RAM3 after actual FF/BT retirement; code/core+fullart fit measured1356B before host adapters. Full8KB source arena to be split around existing cookieoffset1FE0..<1FF0; no old FF/BT cache reuse by wrongfamily.',
  'resident_ROM':'Provisional1280B envelope (not measuredhostfit): genuine loader/router,36service metadata, ROM-only148Bstanding descriptors for2variants×2facings, palette/menu/Start helpers. Requires root exact fragment grant; no free resident/fixed span inferred.',
  'selected_state':'34B active source fields measured; request up to64B INSIDE OWN RAM3 for actual fire/HP/progression/alternating-player persistent slots. No globalExRAM/ZP request; preserve globalRAM0/C2/RAM1.',
  'shared_transport':'No A79 growth assumed. Needs reviewed same-PC typed transport for raw27 plus actual move/draw/postterrain/feet/head/side/item/enemy/lifecycle consumers. Futuregeneric ownROMhigh-owner table may serve27/31/33; pending concrete source funding.',
  'Start_identity':'FmStartFlags currentlyclears08: preserve only08 forslot26; compose BTslot23Groups20 andCFslot30Groups18 plus existingQuick/Goku masks. Otherflags/foreignStarts unchanged. Ownresidentmasktable may fund this withoutmenu growth.'},
  cold_lifecycle=['Resolve retire oldRAM3 owner before selected27 publication; coldmenu executes ROMart only.','PostIc Fresh stores selectedvariant, resets transient,HP/progression independently perplayer.','Forcedblank screen loader invalidates fullcookie FIRST, bufferedPPUcopy+fullverify, restoresPPU/12CHR/maps/33SMC, publishesfamily27cookie LAST.','Actual row19 stillnativeJnReset exactlyonce; lives/area reset transient only, preserve earned state.','Late normalNMI may consume completed ownerOAM/queue; no sourcephysics clock inNMI and no newaudio owner by assumption.'],
  open_before_ready=['Real native world/blockbuffer/32pxbody bounds and camera/auto-control contracts','Authentic fireassets/pools/motion/contact/nativeHP/defeat/score/SFX','SMB3 eligible floorbreak/ceiling/pipe/flag/death handling','Actual allpowerups/2player lifecycle','Source portrait+menu/name/palette/current62foreign/ISR controls','Root exact nativecold/gameplay and1-1 qualification'],
  no_new_resource_used=True,no_host_native_or_admission=True)
 (O/'resource-proposal.json').write_text(json.dumps(proposal,indent=2)+'\n')
 note='''Two original NPCs, not invented original playable characters. Native
SMB3 source PRG is byte-reproduced and all9body poses use its actualCPU
renderer. Native SMB1 complete front/rear records are rebuilt from existing
genuine source: rearX +/-16, rearY+8; all11patternpairs consist of8x8halves
matching exact userWorldROM offsets. Both source palettes are0F1A3027.
This leaf preserves these assets; it does not admit either character.

Actual compiled source core688B, completebodymetadata668B, activestate34B,
bodyCHR3KB. Original3 integrator17920pairs and384allflags pairs match real
original6502outputs. Native1 gravity1960pairs match actualassembled native
MoveEnemySlowVert parameters0F/max2 acrossfraction/page/sign edges. Two180
input sequences walk/jump/land/breathe;3original3rapidpound sequences align
10updates acrosspageedges andretainimpactuntilactualabstractlanding.
Allcontacts use an explicitlyabstractfloor callback; no nativehost claim.

Controls are authored: right/left, Aedge jump, Bedge source mouth/fire
timeline, source3 Down+A align/pound. No original player-Bowser controls
exist in either donor. Core input/facing differs from native portrait flip
until host renderer joins. SMB3 originalunflippedstanding facesleft; its
nativepositive-facing1 requires authentic horizontalflip, no movementflip.

Negatives preserved: v1 control label-parser typo; v2combined-mode left
LDX changedZ so oldBNEfellthroughright; v3 uses genuineunconditionalJMP
and passesleftsequence. v4 builder textualnestedgeneration failedBEFORE
anycompiler/output; v5 directlycopies/recompiles actualsource and adds
original10tick alignment/+6rapidfall. No failedsharedROM or native test.

Resource/API JSON is an explicit UNGRANTED proposal, not a claimedfit.
Preserve currentdfdb62WIP/FFhold, rootBenj islands, newBT950B and915..<927.
No canonicalsrc/menu/PRG/CHR/Downloads/Git index/native processes changed.
'''
 (O/'HANDOFF.txt').write_text(note)
 files=set(p for p in O.glob('*')if p.is_file())
 tools=[R/'tools/audit'/n for n in ['prepare_bowser_source_core_v1.py','prepare_bowser_source_core_v2.py','prepare_bowser_source_core_v3.py','prepare_bowser_source_core_v4.py','prepare_bowser_source_core_v5.py','bowser_source_core_controls_v1.py','bowser_source_core_controls_v2.py','bowser_source_core_controls_v3.py','bowser_source_core_controls_v4.py','bowser_source_core_controls_v5.py','freeze_bowser_source_core_v5.py']];files.update(tools)
 for v in ['v1','v2','v3']:
  d=R/'build'/('bowser-source-core-'+v)
  files.update(p for p in d.glob('*')if p.suffix in ['.json','.s','.inc','.asm'])
 archive=O/'source-only.zip';members=[]
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.suffix in ['.py','.s','.inc','.asm','.cfg','.json','.txt','.dep','.chr','.png']:
    rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
 files.add(archive);files.add(P/'handoff.json')
 result=dict(status='FROZEN_SOURCE_BOTH_BOWSER_CORE_HOST_REQUEST_ONLY',source=True,host=False,native=False,admitted=False,parent=sha(P/'joint/candidate.nes'),measured=q['measured'],archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in sorted(files)})
 (O/'handoff.json').write_text(json.dumps(result,indent=2)+'\n')
 for p,h in result['bindings'].items():assert sha(p)==h
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for rel in z.namelist():assert hashlib.sha256(z.read(rel)).hexdigest()==sha(R/rel)
 print(json.dumps(dict(path=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),bindings=len(result['bindings']),archive_members=len(members),measured=q['measured'],no_host_allocation=True)))
if __name__=='__main__':main()
