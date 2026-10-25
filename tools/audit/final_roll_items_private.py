"""Build a private Roll single-drop-owner overlay. Never installs or runs Mesen."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

ROOT=Path(__file__).resolve().parents[2]
TARGET='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frozen',type=Path,required=True)
    p.add_argument('--expected-base-sha256',default=TARGET)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert sha(a.frozen/'candidate.nes')==a.expected_base_sha256
    a.output.mkdir(parents=True,exist_ok=False);overlay=a.output/'overlay';overlay.mkdir()
    shutil.copytree(a.frozen/'src',overlay/'src')
    shutil.copy2(ROOT/'smb1base-mmc5-expanded.cfg',overlay/'smb1base-mmc5-expanded.cfg')
    inputs=[ROOT/'build_options.ini',ROOT/'smb1base-mmc5-expanded.cfg',ROOT/'tools/build_mmc5_expanded.py']
    inputs += sorted(p for p in(ROOT/'chr').rglob('*')if p.is_file())
    dependencies={str(p.relative_to(ROOT)).replace('\\','/'):sha(p)for p in inputs}
    def build(output):
        result=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(ROOT),'--source-overlay',str(overlay),'--output',str(output)],capture_output=True,text=True)
        output.with_suffix('.driver.log').write_text(result.stdout+result.stderr,encoding='utf-8')
        assert result.returncode==0,result.stdout+result.stderr
    baseline=a.output/'baseline/candidate.nes';baseline.parent.mkdir();build(baseline);assert sha(baseline)==a.expected_base_sha256
    source=overlay/'src/roll_weapons.s';old=source.read_bytes();assert old.count(b' farcall InventoryUpdateDrops')==1
    newline=b'\r\n'if b'\r\n'in old else b'\n'
    replacement=newline.join([b' ; ProcFireball_Bubble already owns shared drop updates before weapons.',b' ; Preserve the old farcall macro span and all subsequent public PCs.',b' .res 18,$ea'])
    new=old.replace(b' farcall InventoryUpdateDrops',replacement);source.write_bytes(new)
    (a.output/'sourcepatch.patch').write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='a/src/roll_weapons.s',tofile='b/src/roll_weapons.s')),encoding='utf-8')
    candidate=a.output/'candidate.nes';build(candidate)
    assert dependencies=={n:sha(ROOT/n)for n in dependencies}
    before,after=baseline.read_bytes(),candidate.read_bytes();b=scoped_load(baseline);c=scoped_load(candidate)
    start=location(b,'RlWeapons::Done')-23;pc=address(b,'RlWeapons::Done')-23
    assert pc==0xaa3a and before[start:start+18].hex()=='8d6a01a9bf8d6c01a9b48d6d01a9bb205a01'
    assert after[start:start+18]==b'\xea'*18 and before[:start]==after[:start]and before[start+18:]==after[start+18:]
    bm={n:address(b,n)for n in b['syms']};cm={n:address(c,n)for n in c['syms']}
    assert bm.keys()==cm.keys()
    symbol_changes={n:[bm[n],cm[n]]for n in bm if bm[n]!=cm[n]}
    # This assembly-time diagnostic counts macro uses; it is not a RAM/code address.
    assert symbol_changes=={'_FARCALL_COUNT':[bm['_FARCALL_COUNT'],bm['_FARCALL_COUNT']-1]},symbol_changes
    assert all(bm[n]==cm[n]for n in bm if n!='_FARCALL_COUNT')
    result=dict(status='private_source_cpu_candidate_not_native_qualified',goal_complete=False,native_passed=False,base_sha256=a.expected_base_sha256,candidate_sha256=sha(candidate),sourcepatch_sha256=sha(a.output/'sourcepatch.patch'),changed_source=['src/roll_weapons.s'],changed_rom_span=dict(bank=119,cpu_start=pc,bytes=18,old=before[start:start+18].hex(),new=after[start:start+18].hex()),all_other_rom_bytes_identical=True,all_address_symbols_identical=True,assembly_diagnostic_constant_change=symbol_changes,RAM_layout_and_CHR_identical=True,dependencies=dependencies,scope=__doc__,defect_reference='Actual natural earned-drop trace on8ff: global owner before birth, redundant Roll-own update increments new age on birth tick. Remove only the redundant local update; do not change global order or gameplay resource policy.')
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items()if k!='dependencies'}))


if __name__=='__main__':main()
