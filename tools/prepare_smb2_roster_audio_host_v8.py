"""Append only owned A74 adapter to immutable6305; no common hook/mixer edit."""
from pathlib import Path
import hashlib,json,subprocess
import prepare_smb2_roster_palette_lifecycle_v7 as B
R=B.R;OLD=B.O;O=R/'build/smb2-roster-audio-host-v8';bind=B.bind
PARENT='188c0c32b770dc192533c79eb6ce46d99845b703d240d89f94e904a7e6859331'

def main():
 assert not(O/'handoff.json').exists(),'frozen output must never be mutated'
 assert bind(OLD/'handoff.json')['sha256']==PARENT
 h=json.loads((OLD/'handoff.json').read_text())
 for k in ['owned_files','input_bindings','output_bindings']:
  for row in h[k]:assert bind(row['path'])==row
 a=(OLD/'candidate.nes').read_bytes();start=16+74*8192+0x1cb7
 assert a[start:16+75*8192]==bytes([255])*841
 O.mkdir(exist_ok=True);obj=O/'objects';obj.mkdir(exist_ok=True)
 entry=(OLD/'objects/entrypoint.s').read_text()+'\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "smb2_roster_audio_host_v8.s"\n.endif\n'
 (obj/'entrypoint.s').write_text(entry,newline='\n')
 cmd=json.loads((OLD/'build-proof.json').read_text())['command']
 cmd=[s.replace(str(OLD/'objects/entrypoint.s'),str(obj/'entrypoint.s')).replace(str(OLD/'candidate.'),str(O/'candidate.'))for s in cmd]
 p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/'launcher.txt').write_text(p.stdout+p.stderr)
 assert not p.returncode,p.stderr[-3000:]
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,O/'candidate.nes');raw=bytearray((O/'candidate.nes').read_bytes());fixed=raw[16+127*8192:16+128*8192]
 plan=json.loads((R/'build/smb2-roster-audio-plan-v1.json').read_text());original=B.B.P.M.F.P.A.S.ROM.read_bytes()
 for clone in plan['samples']:
  copy=bytearray(fixed)
  for row in clone['entries']:
   at=int(row['target'],16)-0xe000;p=int(row['source'],16);n=row['bytes'];blob=original[16+114688+p-0xc000:16+114688+p-0xc000+n]
   assert hashlib.sha256(blob).hexdigest()==row['sha256'];copy[at:at+n]=blob
  raw[16+clone['bank']*8192:16+(clone['bank']+1)*8192]=copy
 (O/'candidate.nes').write_bytes(raw)
 diff=[i for i,(x,y)in enumerate(zip(a,raw))if x!=y]
 assert diff and all(start<=i<16+75*8192 for i in diff),'only owned A74 tail may differ'
 proof=dict(status='PRIVATE_SOURCE_ADAPTER_UNQUALIFIED_NO_COMMON_HOOK_NO_NATIVE',candidate=bind(O/'candidate.nes'),parent=bind(OLD/'candidate.nes'),parent_handoff=bind(OLD/'handoff.json'),command=cmd,tool=bind(__file__),leaf=bind(R/'src/smb2_roster_audio_host_v8.s'),changed_bytes=len(diff),all_prior_ROM_bytes_exact=True)
 (O/'build-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(proof['candidate']))
if __name__=='__main__':main()
