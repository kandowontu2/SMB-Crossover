"""Read-only current-source Arthur/Quick admission and composition inventory.

No compiler, emulator, cart writes, or source changes. Lag is reported rather
than used as an unlock gate. All evidence is written to a new private packet.
"""
from pathlib import Path
import difflib, hashlib, importlib.util, json, sys, traceback

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import current_quick_transport_controls_v4 as T
S=T.S
O=R/'build/arthur-quick-functional-admission-v1'
P=R/'build/celeste-menu-name-current-v2/joint'
N=R/'build/current-character-quick-ui-v13/joint'
COUNTS=[5,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,2,4,4,2,2,4,1,1,4,1,2,1,6,2,4,1]
RAW=[0,1,2,3,4,5,6,7,12,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
FLAGS=[v for v in range(256)if v&48==48]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,d):(O/n).write_text(json.dumps(d,indent=2)+'\n',newline='\n')
def put(m,**kw):
 for n,v in kw.items():m.set(n,v)
def fresh(path,slot):
 m=T.bus(path)
 put(m,OperMode=0,FamilyMainCommit=1,CrossoverMenuState=2,CrossoverMenuIndex=slot,CrossoverMenuButtons=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0,MarioVariant=0)
 for n in ['FmAlts','FmGroups','RlVariant','RdVariant','ProtoVariant','DwVariant','Smb2Class']:
  if n in m.lab:m.set(n,0)
 return m
def call(m,name):return S.execute(m,name)
def button(m,bits):
 put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=bits,SavedJoypad2Bits=0)
 return call(m,'CrossoverMenuInput')
def commands(m):
 start=m.lab['VRAM_Buffer1'];raw=list(m.ram[start:start+m.get('VRAM_Buffer1_Offset')+1]);i=0;rows=[]
 while i<len(raw)and raw[i]:
  length=raw[i+2]&63;rows.append(dict(address=raw[i]*256+raw[i+1],data=raw[i+3:i+3+length]));i+=3+length
 return rows

def bindings():
 rows=[]
 for h in [P.parent/'handoff.json',N.parent/'handoff.json',N.parent/'native-qualified/handoff.json',R/'build/arthur-physical-clock-v2/handoff.json',R/'build/arthur-physical-clock-v2/native-handoff-v3.json']:
  d=json.loads(h.read_text());bad=[]
  for path,digest in d['bindings'].items():
   p=Path(path)
   if not p.is_file()or sha(p)!=digest:bad.append(path)
  rows.append(dict(path=str(h),sha256=sha(h),bindings=len(d['bindings']),mismatches=bad))
 save('preimage-bindings.json',dict(passed=not any(q['mismatches']for q in rows),receipts=rows))
 assert not any(q['mismatches']for q in rows),rows
 return rows

def start_boundary(m,key,p):
 """Actual input entry through the same pre-Cheats launch boundary as v1."""
 put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0)
 c=T.C.H.N.NesMPU(memory=m,pc=m.lab['CrossoverMenuInput'])
 m.page(1,m.bank('CrossoverMenuInput'));m.set('CurrentBank',m.tags[1])
 c.a=0x49;c.x=0x73;c.y=0x97;c.p=p;c.sp=0xfd;c.stPushWord(0x5aff)
 target=m.lab['CheatsApplyStartingLevel'];bank=m.bank('CheatsApplyStartingLevel')|128
 for _ in range(100000):
  if c.pc==target and m.tags[1]==bank:return dict(launch=True,A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp)
  if c.pc==0x5b00:return dict(launch=False,A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp)
  m.pc=c.pc;assert m[c.pc]!=0,('BRK',hex(c.pc),m.tags);c.step()
 raise AssertionError(('menu timeout',hex(c.pc),m.tags))

def menus():
 rows=[];cases=0
 for slot,count in enumerate(COUNTS):
  mm=[fresh(path,slot)for path in [P,N]]
  for m in mm:call(m,'MenuResolveCharacter');call(m,'QueueSelection')
  for variant in range(count):
   if variant:
    for m in mm:button(m,32)
   rr=[call(m,'FmPending')[0]for m in mm]
   pending=[bool(q['P']&1)for q in rr]
   expected=RAW[slot]if not(slot==0 and variant==1)else 8
   for m,q,blocked in zip(mm,rr,pending):
    assert q['X']==slot
    assert m.get('SelectedCharacter')==(0 if blocked else expected),(slot,variant,q,m.get('SelectedCharacter'),expected)
   intended=(slot,variant)in[(9,2),(31,0)]
   assert pending==([True,False]if intended else[pending[0],pending[0]]),(slot,variant,pending)
   # Actual menu input prefix, both Start and A, all 64 live flag patterns.
   for key in [16,128]:
    for p in FLAGS:
     pair=[T.fork(m)for m in mm]
     zz=[start_boundary(m,key,p)for m in pair]
     assert all(z['launch']!=blocked for z,blocked in zip(zz,pending))
     if not intended:
      assert zz[0]==zz[1],('foreign launch AXYP/SP',slot,variant,key,p,zz)
      assert pair[0].get('FmAlts')==pair[1].get('FmAlts')==0 or pending[0]
     elif slot==9:
      assert pair[1].get('FmAlts')==32 and pair[1].get('FmGroups')==0
     cases+=1
   rows.append(dict(menu_index=slot,variant=variant,menu_raw=RAW[slot],resolved=[m.get('SelectedCharacter')for m in mm],pending=pending,FmPending_A=[q['A']for q in rr],name_packets=[q for q in commands(mm[1])if q['address']==0x2328],source_Start_A_all64flags=True))
 ready=[sum(not r['pending'][i]for r in rows)for i in [0,1]]
 assert ready==[52,54],ready
 result=dict(passed=True,native=False,profiles=80,ready_counts=ready,pending_counts=[80-n for n in ready],source_input_cases=cases,only_new_ready_profiles=[[9,2,9,'Quick Man'],[31,0,32,'Arthur']],all_52_previous_ready_preserved=True,MenuCharacters_label='X5MenuCharacters (actual NrMenuCharacter load)',actual_MenuCharacters=RAW,rows=rows)
 save('actual-menu-readiness.json',result)
 return result

def inventory():
 suffix={'.s','.inc','.cfg','.asm'};rows=[];patch=[]
 for p in sorted(N.rglob('*')):
  if not p.is_file()or p.suffix.lower()not in suffix:continue
  rel=p.relative_to(N);prior=P/rel
  if prior.is_file():
   old=prior.read_text(errors='replace');new=p.read_text(errors='replace')
   old=old.replace(str(P),'<JOINT>').replace(P.as_posix(),'<JOINT>')
   new=new.replace(str(N),'<JOINT>').replace(N.as_posix(),'<JOINT>')
   if old==new:continue
   delta=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='installed-a7cc/'+rel.as_posix(),tofile='native-Quick-Arthur-v13/'+rel.as_posix()))
   if rel.as_posix()in['src/full_roster_menu.s','src/character_select.s','src/new_roster_dispatch.s','union.s','generation-shared.s','screen_render.s','src/x5_bounce.s']:patch.append(delta)
  rows.append(dict(path=rel.as_posix(),kind='changed'if prior.is_file()else'added',prior_sha256=sha(prior)if prior.is_file()else None,sha256=sha(p)))
 save('source-composition-inventory.json',dict(candidate=sha(N/'candidate.nes'),installed_source=sha(P/'candidate.nes'),source_changes=rows,source_comparison_normalizes_only_own_absolute_joint_root=True))
 (O/'shared-source-overlaps.patch').write_text(''.join(patch),newline='\n')
 return rows

def main():
 assert not O.exists();O.mkdir()
 d=dict(passed=False,native=False,installed=False)
 try:
  verified=bindings();menu=menus();changes=inventory()
  d.update(passed=True,installed_base=sha(P/'candidate.nes'),preferred_candidate=sha(N/'candidate.nes'),ready=54,pending=26,
   policy='Functional WIP eligibility; measured lag is disclosed rather than a lock. No all1-1/earned-powerups/CXaudio claim.',
   identity_correction='Arthur is menu31/raw32. Menu25 is Gimmick raw26; both were executed through genuine MenuResolveCharacter and FmPending.',
   pending_gate_changes_already_in_candidate={'Quick':'FmPending index9/FmAlts20 -> A31, CLC','Arthur':'FmPending index31 -> A30, CLC'},
   additional_menu_source_changes_required=False,
   cold_chains={'menu':'MenuResolveCharacter -> QwMenuResolve -> QwMenuRetire -> ArGenResolve -> FmResolve -> HuResolve',
    'fresh':'MaaFresh/NrFreshGameInit -> IcGlobalInit once -> typed service15 -> Quick QwConstruct or Arthur ArGenConstruct; QwBoot calls SunnyGlobalInit exactly once after Ic clear',
    'scene':'InitScreen -> QwSceneInit -> ArGenSceneInit -> FwSceneInit -> native MoveAllSpritesOffscreen once',
    'clock':'actual normal/lag GmFamilyNmiGate -> ArGenClockIngress -> GmNmiClock -> genuine RdsNmiGate, FamilyMainCommit busy retained'},
   foreign_contracts='Existing 52 launch identities/ready predicates and actual menu Start/A register contracts preserved; detailed Main/ISR/source/native receipts remain separately bound.',
   overlaps={'RCR':'Root repair is NOT present; adopt its actual frozen source into a new successor, preserving current RCR sources until then.',
    'FF':'Current FF upper/window5-7 cookie6/nativeflash/terrain/combat source exists pending. FF3754 own lifecycle must tail current QwMenuResolve, and preserve QwSceneInit/ArGenSceneInit/FwSceneInit chain; no wholesale common copy.',
    'SMB2':'No S2 or Roll relocation in v13. Genuine own producer/reassembled Roll imports and raw25 common capacity still require source composition. Current A79 2591/2592, common502/512; cannot overlay old 68B/359B shared cohorts.',
    'frontend':'Preserve a7cc exact CELESTE MARIO name, DK/ContraForce gameplay art, Kama native skin,80identity variants; Quick Start keeps only bit20 on slot9.',
    'resources':'No new grants. Preserve Quick251..255,Ar868..883,Quick884..892,FF893..900,Benj901..914 and current selected-owner RAM/C2 protocol.'},
   next_stage='A NEW genuine source successor may combine root RCR repair and peer FF/S2 deltas. Preferred functional base keeps native-qualified v13 PCs; v14/v15 not adopted.',
   native_scope='Arthur1437 400game doublejump/lance controller/graphics pass; Quick7a9e220game genuinecold/menu/loader/HP40/UI/body/fan/scroll pass. No native run from this audit.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc())
 d['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),P/'candidate.nes',P/'candidate.dbg',N/'candidate.nes',N/'candidate.dbg']+list(O.glob('*'))if p.is_file()}
 save('proposal.json',d)
 print(json.dumps({k:v for k,v in d.items()if k not in['bindings','cold_chains','overlaps']}))
 assert d['passed'],d.get('error')
if __name__=='__main__':main()
