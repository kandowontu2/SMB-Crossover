"""Compose qualified disjoint weapon repairs and verify every resulting PRG bank."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    parent=D/'zelda2-platform-late-candidate-v4/adoption-v1/candidate.nes'
    rs=D/'ryu-sophia-native-v1/composition-v2'
    smb3=D/'smb3-projectiles-native-v1/composed49-v2'
    assert sha(parent)=='49d980e564abfb8bfc71bf0c69d5f25c91afed0968d231f959252fa53552b174'
    assert sha(rs/'candidate.nes')=='15392a62b9a6978e9090459b4d899ac8cc0274ffb5e01d80a3082e9aeb8fbc60'
    assert sha(smb3/'candidate.nes')=='7d43c1bdbe1941e150575f6ea52b4b3c8f00ddc36674fe749d53d3a3c4fb82c3'
    source=out/'source';shutil.copytree(rs/'source',source)
    shutil.copy2(smb3/'source/src/smb3_mario_combat.s',source/'src/smb3_mario_combat.s')
    shutil.copy2(smb3/'source/src/smb3_projectile_damage.s',source/'src/smb3_projectile_damage.s')
    entry=source/'src/entrypoint.s';text=entry.read_text()
    for old,new in [('cv3_ryu_audit_sword_guard.s','ryu_primary_gate.s'),
                    ('audit_sophia_triplet_gate.s','sophia_missile_capacity.s')]:
        assert text.count(old)==1
        text=text.replace(old,new)
        (source/'src'/old).rename(source/'src'/new)
    text+='\n.if ::ENABLE_MMC5_EXPANDED\n.include "smb3_projectile_damage.s"\n.endif\n'
    entry.write_text(text)
    rom=out/'candidate.nes'
    with(out/'host-build.log').open('w')as log:
        subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),
                        '--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),
                        '--output',str(rom)],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
    raw=rom.read_bytes();old=parent.read_bytes();r=rs.joinpath('candidate.nes').read_bytes();m=smb3.joinpath('candidate.nes').read_bytes()
    assert raw[:16]==old[:16]and raw[16+1048576:]==old[16+1048576:]
    for bank in range(128):
        donor=r if bank in [6,37]else m if bank==90 else old
        sl=slice(16+bank*8192,16+(bank+1)*8192)
        assert raw[sl]==donor[sl],bank
    labels=lambda path:{q[2]:q[1]for line in path.read_text().splitlines()if len(q:=line.split())==3}
    before,after=labels(parent.with_suffix('.lbl')),labels(rom.with_suffix('.lbl'))
    assert all(after.get(n)==v for n,v in before.items())
    files={};patch=''
    for name in ['expanded_weapons.s','remaining_weapons.s','smb3_mario_combat.s','entrypoint.s',
                 'ryu_primary_gate.s','sophia_missile_capacity.s','smb3_projectile_damage.s']:
        target=source/'src'/name;original=ROOT/'src'/name
        oldtext=original.read_text()if original.exists()else ''
        patch+=''.join(difflib.unified_diff(oldtext.splitlines(True),target.read_text().splitlines(True),
                       fromfile='a/src/'+name if oldtext else '/dev/null',tofile='b/src/'+name))
        files['src/'+name]=dict(before_sha256=sha(original)if original.exists()else None,after_sha256=sha(target))
    (out/'implementation.patch').write_text(patch)
    q=dict(passed=True,adopted=False,goal_complete=False,ROM_sha256=sha(rom),parent_ROM_sha256=sha(parent),
           changed_PRG_banks=[6,37,90],changed_bytes=sum(x!=y for x,y in zip(old,raw)),
           all_preexisting_exported_addresses_exact=True,header_and_CHR_exact=True,
           exact_complete_bank_donors={'6,37':sha(rs/'candidate.nes'),'90':sha(smb3/'candidate.nes')},
           source_files=files,implementation_patch_sha256=sha(out/'implementation.patch'),
           scope='Fresh combined build: each repaired complete PRG bank exactly matches its native-qualified donor; all other bytes equal current49. Current-hash native rerun and flag-off verification remain required before adoption.')
    (out/'build-proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
