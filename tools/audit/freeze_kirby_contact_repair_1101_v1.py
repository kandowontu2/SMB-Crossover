"""Freeze one compact current-source Kirby repair packet, without ROM/objects."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/kirby-inhale-shell-fix-1101-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    receipts=['current-witness.json','native-box-witness.json','baseline-assembly.json','baseline-negative.json','repair-proposal.json','fixed-assembly.json','repair-CPU.json'];checked={}
    for name in receipts:
        j=json.loads((O/name).read_text());assert j['passed'],name
        for p,h in j.get('bindings',{}).items():assert sha(p)==h,(name,p);checked[p]=h
    cpu=json.loads((O/'repair-CPU.json').read_text());assert cpu['CPU_executions']==45296 and cpu['budget']['projected_full_abilities_bytes']==8187
    (O/'HANDOFF.md').write_text((R/'tools/reference/kirby_inhale_shell_fix_1101_v1.md').read_text())
    tools=['prepare_kirby_inhale_shell_fix_1101_v1.py','assemble_kirby_inhale_shell_fix_1101_v1.py','capture_kirby_native_boxes_1101_v1.py','check_kirby_inhale_shell_fix_1101_v1.py','prepare_kirby_contact_repair_1101_v1.py','assemble_kirby_contact_repair_1101_v1.py','check_kirby_contact_repair_1101_v1.py','freeze_kirby_contact_repair_1101_v1.py']
    sources={str(p.relative_to(R)).replace('\\','/'):p for p in[R/'tools/audit'/n for n in tools]+[R/'tools/reference/kirby_shell_contact_1101_v1.inc',R/'tools/reference/kirby_inhale_shell_fix_1101_v1.md']}
    output_names=receipts+['current-kirby-code.bin','baseline.s','baseline.cfg','baseline-weapons.inc','baseline.bin','baseline.dbg','fixed-source.s','fixed.s','fixed.cfg','fixed-weapons.inc','fixed.bin','fixed.dbg','HANDOFF.md']
    for n in output_names:sources['proof/'+n]=O/n
    manifest={n:dict(bytes=p.stat().st_size,sha256=sha(p))for n,p in sources.items()}
    packet=O/'source-proof.zip'
    with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,p in sources.items():z.write(p,n)
        z.writestr('manifest.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(packet)as z:
        assert z.testzip()is None
        for n,info in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==info['sha256']
    report=dict(passed=True,frozen=True,production_modified=False,native=False,installed=False,packet=dict(path=str(packet),bytes=packet.stat().st_size,members=len(manifest)+1,sha256=sha(packet)),CPU_executions=cpu['CPU_executions'],budget=cpu['budget'],binding_entries_checked=len(checked),bindings={str(p.resolve()):sha(p)for p in[Path(__file__),packet,O/'repair-CPU.json',O/'HANDOFF.md']})
    (O/'binding.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
