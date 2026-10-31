"""Measure the unresolved genuine-import CF/BT ROM guard; no ROM allocation."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
from private_build_outputs_v1 import validate
O=R/'build/contra-force-rom-guard-proposal-v1'
P=R/'build/contra-force-loader-cart-v4'
H=R/'tools/reference/contra_force_rom_guard_v1.s'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 assert not O.exists();O.mkdir()
 stage=json.loads((P/'source-stage.json').read_text())
 for p,h in stage['bindings'].items():assert sha(p)==h,p
 (O/'guard.s').write_bytes(H.read_bytes());(O/'cf-cookie.bin').write_bytes((P/'joint/cf-cookie.bin').read_bytes())
 ca=R/'tools/Windows/cc65/bin/ca65.exe';od=ca.with_name('od65.exe')
 cmd=[str(ca),'--cpu','6502x','-g','-I',str(O),'--create-full-dep',str(O/'guard.dep'),'-o',str(O/'guard.o'),str(O/'guard.s')]
 guard=validate(cmd,O,cwd=O);p=subprocess.run(cmd,cwd=O,capture_output=True,text=True)
 log=dict(command=cmd,cwd=str(O),output_guard=guard,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
 (O/'compile.json').write_text(json.dumps(log,indent=2)+'\n');assert p.returncode==0,log
 d=subprocess.run([str(od),'--dump-segments',str(O/'guard.o')],cwd=O,capture_output=True,text=True);assert d.returncode==0,d.stderr
 (O/'segments.txt').write_text(d.stdout)
 blocks=d.stdout.split('Name:');row=next(x for x in blocks if '"CF_ROM_GUARD"'in x)
 size=int(re.search(r'Size:\s*(\d+)',row)[1]);assert size<=185
 result=dict(passed=True,source=True,unresolved_object_measurement=True,native=False,ROM_granted=False,shared_changes=False,
  actual_bytes=size,proposed_only=dict(physical_bank=69,start_offset='1F47',end_offset_exclusive='2000',available=185,remaining_if_granted=185-size),
  CF_contract='Preserves original A=3*service, X/Y/P except resultC; full16/class cookie; rawC stacked/restored; no SMC/guestRAM/protection writes; no rawA2 opcode before returnC1',
  BT_contract='Restores originalA/P then tails genuine BtCheck through genuine SFC with true .bank relocation; actual target remains an unresolved import for the shared owner, not a guessed address',
  expected_cookie=(O/'cf-cookie.bin').read_bytes().hex(),payload_sha256=stage['payload_sha256'],
  obligations=['Root grant/source preimage/future-owner exclusion for proposed185B','Shared owner links true BtCheck/native imports and exact bank metadata','Actual emitted guard/allflag/normal-lagISR/first-opcode-failure controls before adoption'],
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),H,P/'source-stage.json',P/'joint/cf-cookie.bin',ca,od,R/'tools/audit/private_build_outputs_v1.py',*[p for p in O.iterdir()if p.is_file()]]})
 path=O/'proposal.json';path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(path=str(path),sha256=sha(path),bytes=size,remaining=185-size)),flush=True)

if __name__=='__main__':main()
