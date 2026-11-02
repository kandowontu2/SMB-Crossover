"""Emit the CPU-qualified two-byte owned policy repair and unchanged routes."""
from pathlib import Path
import hashlib,json
import check_arthur_maturity_fix_1102_v12 as Q
from prepare_selected_native_packet_v1 import prepare
C=Q.C;P=Q.P;O=Q.O


def main():
 proof=O/'maturity-fix-CPU.json';q=json.loads(proof.read_text());assert q['passed']
 for p,h in q['bindings'].items():assert P.sha(P.R/p)==h,p
 raw=bytearray(Q.BASE.read_bytes());at=C.location(C.scoped_load(Q.BASE),'ArOwnServices')+3*23
 original=bytes(raw[at:at+3]);replacement=(O/'maturity-entry.bin').read_bytes();raw[at:at+3]=replacement
 rom=O/'maturity-candidate.nes';digest=hashlib.sha256(raw).hexdigest();assert digest==q['candidate_sha256']
 delta=[dict(file_offset=i,old=a,new=b)for i,(a,b)in enumerate(zip(Q.BASE.read_bytes(),raw))if a!=b]
 assert [v['file_offset']for v in delta]==q['changed_bytes']==[580950,580951]
 rom.write_bytes(raw)
 for ext in ['.dbg','.lbl']:rom.with_suffix(ext).write_bytes(Q.BASE.with_suffix(ext).read_bytes())
 receipt=dict(prepared=True,installed=False,native=False,ROM_sha256=digest,base_sha256=P.sha(Q.BASE),only_physical_PRG_bank=70,owned_table_row=23,owned_CPU_half_open=['BD45','BD48'],old_JMP=original.hex(),new_JMP=replacement.hex(),delta=delta,no_new_PRG_CHR_RAM=True,existing_target='Actual v3-source ArOwnSet9 BDBF -> pure SEC ArMergeLocalVisible BEB8 -> original complete policy return. ArHostCollect retains maturity authority for0/1;>=2 uses genuine MarioSource.',bindings={str(p.relative_to(P.R)):P.sha(p)for p in [Path(__file__),Q.SOURCE,proof,rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl')]})
 (O/'maturity-candidate.json').write_text(json.dumps(receipt,indent=2)+'\n')
 for name,ref,timeout,scope in [
  ('flower-maturity',O/'flower-landwalk/controller.lua',150,'Exact unchanged valid parkedflower-landwalk controller and strong genuine originaltorch/no-life-loss assertions on the owned policy23 repair. BBox/physics/controller unchanged; no RAM seeds/helpers.'),
  ('full11-maturity',O/'full11-near/controller.lua',240,'Exact unchanged near17+40/combat controller on the owned policy23 repair; retain all4pipes/3gaps/actual1-2/no-life-loss assertions and originalinjuryobserver. No RAM seeds/helpers; earlier negative preserved.')]:
  prepare(O/name,rom,ref.read_text(),[Path(__file__),ref,proof,O/'maturity-candidate.json'],expected=digest,timeout=timeout,scope=scope,allow_interactive=True)
 print(json.dumps(receipt))


if __name__=='__main__':main()
