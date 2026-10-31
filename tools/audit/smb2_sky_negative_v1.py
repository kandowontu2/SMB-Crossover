"""Retain the actual native palette/upload first-black and missing restore witness."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
O=R/'build/smb2-sky-negative-v1';J=R/'build/functional-roster-coherent62-v4/joint'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();sp=importlib.util.spec_from_file_location('single_sky_actual_factory',R/'build/smb2-natural-current-audio-v20/controls.py');A=importlib.util.module_from_spec(sp);sp.loader.exec_module(A);C=A.C;M=A.M
 m=M.fresh(0,0);old=C.O;C.O=J
 try:b=C.Bus()
 finally:C.O=old
 m.bundle=b.bundle;m.ROM_banks=b.ROM_banks;m.lab=b.lab
 C.invoke(m,'GetAreaPalette');A.interrupt(m,0)
 for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,n)
 A.interrupt(m,0);M.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',A=0)
 m.palette_writes.clear();events=[]
 for age in range(1500):
  previous=len(m.palette_writes);ni=A.interrupt(m,0);writes=m.palette_writes[previous:]
  z=C.invoke(m,'GameLoop');calls=[name for name in ['GetAreaPalette','GetPlayerColors','S2HostForcePalette','S2MainPalette']if any(pc==m.lab[name]and tags[(pc-32768)//8192]==m.bank(name)|128 for tags,pc in z['trace']if pc>=32768)]
  if calls or any(w['canonical']==0x3f00 for w in writes):events.append(dict(age=age,task=m.get('ScreenRoutineTask'),mode_task=m.get('OperMode_Task'),calls=calls,canonical_BG=m.vram[0x3f00],writes=writes,queue_offset=m.get('VRAM_Buffer1_Offset')))
  if m.get('OperMode_Task')==3 and m.get('GameEngineSubroutine')==8:break
 else:raise AssertionError('Full cold parser did not reach control')
 A.interrupt(m,0);assert m.vram[0x3f00]==15 and m.get('AreaType')==1 and m.get('BackgroundColorCtrl')==0
 # Observe the exact current body callback; it ALREADY skips universal.
 M.put(m,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,S2PaletteAck=255);C.invoke(m,'GetPlayerColors')
 at=m.lab['VRAM_Buffer1'];packet=list(m.ram[at:at+7]);assert packet==[63,17,3,1,22,39,0]
 first=next(w for w in m.palette_writes if w['canonical']==0x3f00 and w['value']==15)
 nativebg=m.bundle['raw'];from check_tmnt_render_oa import location
 expected=list(nativebg[location(m.bundle,'BackgroundColors'):location(m.bundle,'BackgroundColors')+8]);assert expected[1]==34
 neg=dict(passed=True,product_negative_reproduced=True,native=False,candidate=sha(J/'candidate.nes'),actual_cold_Main=age+1,
  first_black_PPU_write=first,actual_scene_events=events,entered_BG=15,genuine_native_expected_BG=34,
  original_S2MainPalette_packet=packet,body_writer_ALREADY_3F11_only=True,
  cause='Actual native area bulk writes3F00=0F. Selected S2 GetPlayerColors replaces the native background restore with only3F11..13, leaving black. No S2 source3F10 write was observed; removing one would be a blind wrong fix.',
  expected_native_BackgroundColors=expected)
 p=O/'negative.json';p.write_text(json.dumps(neg,indent=2)+'\n',encoding='utf-8',newline='\n')
 imports={};objects=[x for x in json.loads((J.parent/'final-link.json').read_text())['command']if x.endswith('.o')]
 for name in objects:
  txt=subprocess.check_output([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-imports',name],text=True)
  assert '"S2PalettePointerC"'not in txt,name;imports[str(Path(name).resolve())]=sha(name)
 proof=dict(passed=True,retired_own_unused_ABI_proposal='S2PalettePointerC physical118:B89E..<B8CB45B',actual_final_object_consumers=0,actual_objects=imports,
  replacement='Same-bank41B source-exact header/background helper +4Bpad, clones native8B BackgroundColors and selection logic. S2MainPalette keeps74B publicspan by replacing17Bheader with3BJSR+14Bendpad; threshold78→77 for complete7Bpacket.',
  no_public_PC_Ram_lease_growth=True,bindings={str(Path(__file__).resolve()):sha(__file__),str(p.resolve()):sha(p),str((J/'candidate.nes').resolve()):sha(J/'candidate.nes'),str((J/'candidate.dbg').resolve()):sha(J/'candidate.dbg'),str((J/'src/characters.s').resolve()):sha(J/'src/characters.s')})
 out=O/'consumer-proposal.json';out.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps(dict(passed=True,negative=str(p),sha256=sha(p),proposal=str(out),proposal_sha256=sha(out))),flush=True)
if __name__=='__main__':main()
