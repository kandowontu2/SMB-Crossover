"""Actual dual-ready menu -> post-Ic Fresh -> forced-blank source loading.

Uses the current cart's genuine callers. No RAM kernel/state preloading,
emulator launch, forced source-clock Due, or source edits.
"""
from pathlib import Path
import inspect,json,sys,traceback,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import arthur_quick_functional_admission_v1 as A
import quickman_wram_palette_controls_v6 as C
import current_quick_transport_controls_v4 as T
N=A.N;O=A.O/'cold';C.O=N;C.CODE=(N/'code.bin').read_bytes();C.DATA=(N/'data.bin').read_bytes()

# Native scene/menu callbacks deliberately publish C. Retain the existing
# actual mapped-C publication checks; only these genuine API endpoints differ
# from the default stricter all-bank-restore helper contract.
s=inspect.getsource(C.invoke)
old="if requested!='GameLoop':assert m.tags==incoming,('public mapper restore',requested,m.tags,incoming)"
new="if requested not in ['GameLoop','QueueSelection','InitializeArea','LoadAreaPointer','DrawSelectionPreview','PrimaryGameSetup','SecondaryGameSetup','Entrance_GameTimerSetup','PlayerEntrance']:assert m.tags==incoming,('public mapper restore',requested,m.tags,incoming)"
assert s.count(old)==1;exec(compile(s.replace(old,new),__file__,'exec'),C.__dict__)

def put(m,**kw):
 for n,v in kw.items():m.set(n,v)
def call(m,name):
 r=C.invoke(m,name)
 names=['IcGlobalInit','SunnyGlobalInit','QwBoot','QwConstruct','QhConstruct','QuickManInit','ArGenConstruct','ArHostConstruct','ArCacheLoad','ArHostEnsure','ArGenSceneInit','FwSceneInit','MoveAllSpritesOffscreen']
 counts={}
 for n in names:
  if n not in m.lab:continue
  tag=1 if n in['QhConstruct','QuickManInit']else m.bank(n)|128
  counts[n]=sum(pc==m.lab[n]and tags[(pc-32768)//8192]==tag for tags,pc in r['trace']if pc>=32768)
 return dict(entry=name,registers=r['registers'],CPU=r['CPU'],counts=counts,Selected=m.get('SelectedCharacter'),FmAlts=m.get('FmAlts'),ArReady=m.get('ArHostReady'),HP=m.get('QmField_06C0'),PPU_reads=m.ppu_reads,active_PPU_reads=m.PPU_active_reads,RAM_exec=len(m.executed_RAM),cookie=list(m.wram[2][0x1fe0:0x1ff0]))
def fresh(slot):
 b=C.H.U.scoped_load(N/'candidate.nes');base=C.H.U.setup(b,slot);m=C.Bus();m.ram[:0x8000]=bytes(base.m[:0x8000]);m.wram=[bytearray(8192)for _ in range(4)]
 put(m,CurrentBank=m.tags[1],CurrentBankC=m.tags[2],SelectedCharacter=0,FmAlts=0,RlVariant=0,CrossoverMenuIndex=slot,CrossoverMenuState=2,CrossoverMenuButtons=0,CrossoverContinue=0,OperMode=0,DisableScreenFlag=0,Mirror_PPUMASK=24,Mirror_PPUCTRL=160,NmiDisable=255,FamilyMainCommit=1,VRAM_Buffer1_Offset=0)
 m.ppu_ctrl=160;m.ppu_mask=24;m.sync_chr11();m.ram[0x5102]=2;m.ram[0x5103]=1;m.ram[0x5113]=0
 C.invoke(m,'PrimaryGameSetup')
 put(m,OperMode=0,CrossoverMenuState=2,DisableScreenFlag=0,Mirror_PPUMASK=24,FamilyMainCommit=1)
 return m

def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,native=False,candidate=A.sha(N/'candidate.nes'),cases=[])
 try:
  tab=T.bus(N);at=tab.lab['X5MenuCharacters'];bank=tab.bank('X5MenuCharacters');actual=list(tab.ROM_banks[bank][at&8191:(at&8191)+32]);assert actual==A.RAW
  d['actual_MenuCharacters']=dict(label='X5MenuCharacters',physical_bank=bank,CPU_address=at,bytes=actual,Arthur_index=31,Arthur_raw=32,Quick_index=9,Quick_raw=9)
  for slot,raw in[(31,32),(9,9)]:
   m=fresh(slot);rows=[]
   for name in['MenuResolveCharacter','QueueSelection']:rows.append(call(m,name))
   if slot==9:
    for _ in range(2):
     put(m,SavedJoypad1Bits=32,SavedJoypad2Bits=0,CrossoverMenuButtons=0,VRAM_Buffer1_Offset=0);rows.append(call(m,'CrossoverMenuInput'))
   assert m.get('SelectedCharacter')==raw and (m.get('FmAlts')==32 if raw==9 else True)
   put(m,VRAM_Buffer1_Offset=0);rows.append(call(m,'DrawSelectionPreview'))
   assert not m.ppu_reads and not m.executed_RAM,'Cold menu must not execute WRAM or load CHR carrier'
   put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0,VRAM_Buffer1_Offset=0)
   start=call(m,'CrossoverMenuInput');rows.append(start)
   assert start['counts']['IcGlobalInit']==start['counts']['SunnyGlobalInit']==start['counts']['QwBoot']==1,start
   assert start['counts']['QwConstruct'if raw==9 else'ArGenConstruct']==1,start
   assert m.get('SelectedCharacter')==raw and m.get('CrossoverMenuState')==0 and m.get('DisableScreenFlag')==1
   assert not m.ppu_reads and not m.executed_RAM,'Post-Ic visible-menu Fresh only resets until real forced blank'
   put(m,OperMode=1,OperMode_Task=0,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,FamilyMainCommit=1);m.ppu_mask=0
   for name in['LoadAreaPointer','InitializeArea']:rows.append(call(m,name))
   put(m,ScreenRoutineTask=0,VRAM_Buffer1_Offset=0)
   scene=call(m,'InitScreen');rows.append(scene)
   assert scene['counts']['ArGenSceneInit']==scene['counts']['FwSceneInit']==scene['counts']['MoveAllSpritesOffscreen']==1,scene
   assert not m.PPU_active_reads
   if raw==9:
    C.exact_cache(m)
    assert scene['counts']['QhConstruct']==scene['counts']['QuickManInit']==1 and m.get('QmField_06C0')==40 and m.ppu_reads==18450,scene
   else:
    p=m.lab['ArCacheSignature'];signature=bytes(m.ROM_banks[m.bank('ArCacheSignature')][p&8191:(p&8191)+16])
    assert bytes(m.wram[2][0x1fe0:0x1ff0])==signature and m.get('ArHostReady')==167,scene
    assert scene['counts']['ArCacheLoad']==scene['counts']['ArHostEnsure']==1,scene
   for name in['SecondaryGameSetup','Entrance_GameTimerSetup','PlayerEntrance']:rows.append(call(m,name))
   assert m.get('GameEngineSubroutine')==8 and m.get('SelectedCharacter')==raw
   d['cases'].append(dict(menu_index=slot,raw=raw,real_menu_Ready=True,no_kernel_preload=True,source_Fresh_once=True,actual_native_entrance_state=8,rows=rows))
  d['passed']=True
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc())
 d['limits']=['Source CPU genuine caller sequence, not an additional native run. Previously frozen native Quick220game and Arthur400game witnesses remain separate.','No source Due/Pad/HP/actor writes; no full1-1, earned upgrades, CXaudio, or constant60Hz claim.']
 d['bindings']={str(p.resolve()):A.sha(p)for p in[Path(__file__),Path(A.__file__),A.O/'proposal.json',N/'candidate.nes',N/'candidate.dbg',N/'code.bin',N/'data.bin',N/'quick/cookie.bin']}
 (O/'actual-cold-chains.json').write_text(json.dumps(d,indent=2)+'\n',newline='\n')
 print(json.dumps(dict(passed=d['passed'],error=d.get('error'),cases=[{k:v for k,v in q.items()if k!='rows'}for q in d['cases']])))
 assert d['passed'],d.get('error')
if __name__=='__main__':main()
