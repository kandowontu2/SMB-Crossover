"""Measure pure ROM stale-P1 repair; no cartridge link or resource adoption."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
O=R/'build/contra-force-p1-native-restore-proposal-v1';P=R/'build/contra-force-p1-cart-v2';S=R/'tools/reference/contra_force_p1_native_restore_proposal_v1.s'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();parent=json.loads((P/'source-stage.json').read_text())
 for f,h in parent['bindings'].items():assert sha(f)==h,f
 b=qualified(P/'joint/candidate.nes');src=R/'build/cf-cold-warm-palette-source-v1/joint/ff-palette-lifecycle.s';old=src.read_text()
 needle=' MP_FAR MoveAllSpritesOffscreen,jsr\n ldx SmFreezePaletteControl'
 assert old.count(needle)==1
 zero=old.replace(needle,' MP_FAR MoveAllSpritesOffscreen,jsr\n.export FwMuxNativeSelect\nFwMuxNativeSelect:\n ldx SmFreezePaletteControl')
 (O/'ff-palette-lifecycle-zero-export.s').write_text(zero)
 at=address(b,'Retire')+37;pos=location(b,'Retire')+37
 assert b['raw'][pos:pos+3]==bytes([174,address(b,'SmFreezePaletteControl')&255,address(b,'SmFreezePaletteControl')>>8])
 ca=R/'tools/Windows/cc65/bin/ca65.exe';od=ca.with_name('od65.exe');models={};logs=[]
 for name,defines in [('any_A_ROM',[]),('same_physical93',['-D','SAME_PHYSICAL_93=1'])]:
  cmd=[str(ca),'--cpu','6502x','-g',*defines,'--create-full-dep',str(O/(name+'.dep')),'--listing',str(O/(name+'.lst')),'-o',str(O/(name+'.o')),str(S)]
  guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);logs.append(dict(command=cmd,guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));assert z.returncode==0,z.stderr
  q=subprocess.run([str(od),'--dump-segments',str(O/(name+'.o'))],capture_output=True,text=True);assert q.returncode==0;(O/(name+'-segments.txt')).write_text(q.stdout)
  size=int(re.search(r'Name:\s+"CF_P1_ROM_RESTORE_PROPOSAL"[\s\S]*?Size:\s+(\d+)',q.stdout)[1]);models[name]=dict(bytes=size,near_native_packet=name=='same_physical93')
 assert models['any_A_ROM']['bytes']==67 and models['same_physical93']['bytes']==52,models
 (O/'commands.json').write_text(json.dumps(logs,indent=2)+'\n')
 q=dict(source=True,native=False,adopted=False,resource_granted=False,ready=False,parent=parent['candidate'],measured=models,
  zero_byte_entry=dict(label='FwMuxNativeSelect',physical_bank=93,PC=at,source=str(src),actual_original_opcode=b['raw'][pos:pos+3].hex(),scope='Immediately AFTER original MoveAllSpritesOffscreen farcall; reads only native Control/Area, builds7B native C0 packet. Does not touchState/OAM/Turn.'),
  proposed_changes=['Retarget selected31-only late SFC target inside existing59B from B020+18 to CfP1NativeRestore; no shared span growth','Export genuine zero-byte FwMuxNativeSelect in physical93 producer','New52B A-ROM worker if physical93 is granted; otherwise67B in any new A-ROM span. Neither interval is allocated/adopted here.'],
  policy=['Only LastC0/C1 (CF-owned) is repaired; Samus0/1 and FF80 are untouched','ClearPending FIRST; setLastC0; genuine native packet publishesC0 LAST; keepTurn to retain fairalternation','Restore originalAXYP before genuine service6 B020 callback; invalid auth returns with nativeP1 restore and native OAM retained; valid late callback can replace with exactCF80 epoch','NativeC0 preflush remains BEFORE original native palettequeue, so sameMain Axe/Bowser/text publishers win; validCF80 stayspostqueue','No State/Control/bodyACK/newRAM/CHR/OAM writes; no firstA2 without fullcookie/class guard'],
  candidate_only_interval=dict(physical_bank=93,start_offset=0xfa7,end_offset=0xfdb,bytes=52,status='NOT_GRANTED; root must close current68/future ownership, not merely fill'),
  remaining_controls=['Actual valid/invalid DrawAll once+paired normalNMI/stalehardware','OriginalAXYP/outputC+all33SMC/livepage1/maps and realISR','Fullqueue/late-native/pause/lag/abandon/acquire/retire/current66foreign before readiness'])
 files=[Path(__file__),S,P/'source-stage.json',P/'joint/candidate.nes',src,R/'build/contra-force-p1-native-first-controls-v3/controls.json',R/'build/contra-force-p1-stale-palette-ppu-v1/controls.json',R/'build/contra-force-p1-stale-palette-ppu-v2/controls.json',*[p for p in O.iterdir()if p.is_file()]]
 q['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'proposal.json';p.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),measured=models)),flush=True)
if __name__=='__main__':main()
