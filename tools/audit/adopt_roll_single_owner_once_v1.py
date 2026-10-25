"""Install only the independently checked Roll drop-owner repair, with rollback."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/final-roll-items-v1')
BASE='4c70fe485f73fb8d437fae2e79ae8ddad83908dc26d4008f21e0a2abeccee2da'
FINAL='9bac46e934d3301e378139783febf2d54c4fd5753a62e082f2d7e6580946d58c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=D/'adoption-single-owner-v1';assert not out.exists(),'One-shot adoption already started.'
    default=ROOT/'build/smb-crossover-mmc5-expanded.nes'
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    assert sha(default)==sha(installed)==BASE
    packet_path=D/'native-packet-single-owner4c70-v1/proof.json'
    assert sha(packet_path)=='6488f944a0bd9ba553a76a87ea6ab4362e8f400fc41846014e5cbd2ab4bf391e'
    packet=json.loads(packet_path.read_text());assert packet['lifecycle_passed']and packet['ROM_sha256']==FINAL
    for name,digest in packet['refs'].items():assert sha(D/name)==digest,name
    for p in [D/'root-single-owner-cpu-v1/proof.json',D/'root-aggregate-v1/proof.json']:
        q=json.loads(p.read_text());assert q['passed']and q.get('candidate_SHA256',q.get('ROM_sha256'))==FINAL
    report=ROOT/'docs/qa/final-roll-items-2026-10-25.txt'
    assert sha(report)=='2000db335445521de6169a734f23ae7c84f86c48b4d57c0b5b003388c32bc636'
    candidate=D/'drop-single-owner-private4c70-v1/candidate.nes';assert sha(candidate)==FINAL
    source=ROOT/'src/roll_weapons.s';newsource=D/'drop-single-owner-private4c70-v1/overlay/src/roll_weapons.s'
    old=source.read_bytes();new=newsource.read_bytes()
    assert old.count(b' farcall InventoryUpdateDrops')==1 and new.count(b' .res 18,$ea')==1
    assert new==old.replace(b' farcall InventoryUpdateDrops',b' ; ProcFireball_Bubble already owns shared drop updates before weapons.\n ; Preserve the old farcall macro span and all subsequent public PCs.\n .res 18,$ea')
    out.mkdir();shutil.copy2(installed,out/'previous-MMC5.nes');(out/'previous-roll_weapons.s').write_bytes(old)
    try:
        source.write_bytes(new)
        with(out/'fresh-ROOT-build.log').open('w')as log:
            subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--output',str(out/'candidate.nes')],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
        assert sha(out/'candidate.nes')==FINAL,'Fresh canonical compile differs from qualified build'
    except BaseException:
        source.write_bytes(old);raise
    suffixes=['.nes','.dbg','.lbl','.map','.build.json','.build.log','.cv3-mirror.json']
    previous=out/'previous-default';previous.mkdir()
    for ext in suffixes:
        p=default.with_suffix(ext)
        if p.exists():shutil.copy2(p,previous/p.name)
    staging=installed.with_name(installed.stem+'.staging-'+FINAL[:8]+'.nes');assert not staging.exists()
    shutil.copy2(out/'candidate.nes',staging);assert sha(staging)==FINAL;staging.replace(installed)
    for ext in suffixes:shutil.copy2((out/'candidate.nes').with_suffix(ext),default.with_suffix(ext))
    assert sha(default)==sha(installed)==FINAL
    proof=dict(adopted=True,goal_complete=False,ROM_sha256=FINAL,baseline_ROM_sha256=BASE,changed_source='src/roll_weapons.s',
               installed=str(installed),fresh_canonical_ROOT_compile_exact=True,all_other_ROM_bytes_identical=True,
               repaired='Remove redundant local shared-drop update; object dispatcher remains sole owner before Roll attack/drop birth.',
               root_checks=dict(cpu_cases=412,independently_reaggregated_modes=2,native_steps=72,actual_defeats=624,natural_drops=139,raw_captures=427),
               refs={str(p):sha(p)for p in [packet_path,D/'root-single-owner-cpu-v1/proof.json',D/'root-aggregate-v1/proof.json',report]},
               rollback=str(out),remaining=['Confirmed missing late-life capsule fade remains open.','Mobile executable/timing/audio parity unavailable.','No all37 current-hash campaign/every-item/performance/MMC3 qualification.','Hard419 raw label overwritten by420 inside frozen fixture; chronology retained. Distinct Easy/Hard fixture hashes explicit.'])
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    dest=ROOT/'build/verification/roll-single-owner';dest.mkdir(exist_ok=True);shutil.copy2(out/'proof.json',dest/'proof.json')
    print(json.dumps(proof))


if __name__=='__main__':main()
