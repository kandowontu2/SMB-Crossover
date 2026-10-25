"""Install the exact qualified one-file P-bar ownership correction once."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/m3-hud-timing-v1')
BASE='9bac46e934d3301e378139783febf2d54c4fd5753a62e082f2d7e6580946d58c'
FINAL='5ec81c9250c20aee31af0d3b98c241932c72b3147e05702de70e266f3c854893'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=D/'adoption-owner-v1';assert not out.exists(),'One-shot adoption already started.'
    default=ROOT/'build/smb-crossover-mmc5-expanded.nes';installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    assert sha(default)==sha(installed)==BASE
    qualified=D/'final-native-v1/proof.json';q=json.loads(qualified.read_text())
    assert q['passed']and q['ROM_sha256']==FINAL and q['affected_identity_routes']==11
    for n,v in(q['refs']|q['tools']).items():assert sha(Path(n))==v,n
    for r in q['native']:assert sha(D/'final-native-v1'/r['name']/'proof.json')==r['proof_sha256']
    private=D/'private-owner-v2';proposal=json.loads((private/'proof.json').read_text())
    assert proposal['candidate_sha256']==FINAL and proposal['all_preexisting_symbol_values_identical']and proposal['RAM_CHR_identical']
    assert proposal['changed_bytes']==16
    for mapper,expected in [('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        assert sha(private/('ordinary-'+mapper+'.nes'))==expected
    source=ROOT/'src/x5_bounce.s';new=private/'overlay/src/x5_bounce.s'
    assert sha(source)==proposal['baseline_source_sha256']and sha(new)==proposal['candidate_source_sha256']
    out.mkdir();shutil.copy2(installed,out/'previous-MMC5.nes');shutil.copy2(source,out/'previous-x5_bounce.s')
    try:
        shutil.copy2(new,source)
        with(out/'fresh-ROOT-build.log').open('w')as log:
            subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--output',str(out/'candidate.nes')],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
        assert sha(out/'candidate.nes')==FINAL
    except BaseException:
        shutil.copy2(out/'previous-x5_bounce.s',source);raise
    suffixes=['.nes','.dbg','.lbl','.map','.build.json','.build.log','.cv3-mirror.json']
    previous=out/'previous-default';previous.mkdir()
    for ext in suffixes:
        p=default.with_suffix(ext)
        if p.exists():shutil.copy2(p,previous/p.name)
    stage=installed.with_name(installed.stem+'.staging-'+FINAL[:8]+'.nes');assert not stage.exists()
    shutil.copy2(out/'candidate.nes',stage);assert sha(stage)==FINAL;stage.replace(installed)
    for ext in suffixes:shutil.copy2((out/'candidate.nes').with_suffix(ext),default.with_suffix(ext))
    assert sha(default)==sha(installed)==FINAL
    result=dict(adopted=True,goal_complete=False,ROM_sha256=FINAL,baseline_ROM_sha256=BASE,
                installed=str(installed),fresh_canonical_ROOT_compile_exact=True,changed_source='src/x5_bounce.s',source_sha256=sha(source),
                all_preexisting_symbol_values_exact=True,new_RAM_CHR_banks=0,changed_ROM_bytes=16,bank=86,
                native_qualification_sha256=sha(qualified),native=q['native'],affected_routes=11,CPU_cases=1600,
                maximum_other_leaf_overhead_CPU_cycles=19,rollback=str(out),
                remaining='A focused HUD ownership fix, not universal lag removal or every-item/source-perfect/all37-current-native/MMC3 expanded certification. Roll fade, authentic Mike/Parodius music and remaining CV3 effects remain open.')
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    dest=ROOT/'build/verification/m3-hud-owner';dest.mkdir(exist_ok=True);shutil.copy2(out/'proof.json',dest/'proof.json')
    print(json.dumps(result))


if __name__=='__main__':main()
