"""Freeze the finite private Luigi dry-profile source/CPU/build packet; no native."""
from pathlib import Path
import hashlib
import json
import sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
P=D/'luigi-mario-profile731-v3'
SHA='641460e2646806c03fb98cf84f8a8c2e8de99c74dac8c5876c50f05ef1eb512c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(Path(p).read_text())
def main():
    assert sha(P/'candidate.nes')==sha(P/'canonical.nes')==SHA
    assert sha(P/'ordinary-mmc3.nes')=='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'
    assert sha(P/'ordinary-mmc5.nes')=='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'
    sys.path.insert(0,str(ROOT/'tools/audit'))
    from luigi_mario_profile731_prepare_v1 import derive
    assert (P/'source/src/luigi_source_profile.s').read_text()==derive(BASE/'source')
    before=get(BASE/'source-manifest.json');after=get(P/'source-manifest.json')
    changed=get(P/'preparation.json')['changed_source'];assert len(changed)==4
    for n,h in before.items():assert sha(BASE/'source'/n)==h
    assert set(after)==set(before)|{'src/luigi_source_profile.s'}
    actual=[n for n,h in after.items() if before.get(n)!=h];assert set(actual)==set(changed)
    for n,h in after.items():assert sha(P/'source'/n)==h,n
    eols=[]
    for n in changed[:-1]:
        old=(BASE/'source'/n).read_bytes();new=(P/'source'/n).read_bytes()
        if b'\r\n'not in old:assert b'\r\n'not in new
        elif old.count(b'\n')==old.count(b'\r\n'):assert new.count(b'\n')==new.count(b'\r\n')
        eols.append(dict(file=n,before_LF=old.count(b'\n'),before_CRLF=old.count(b'\r\n'),after_LF=new.count(b'\n'),after_CRLF=new.count(b'\r\n')))
    receipts=[P/'cpu-v2/proof.json',P/'traits-v1/proof.json',P/'handoffs-v1/proof.json']
    for f in receipts:
        q=get(f);assert q['passed'] and q['ROM_sha256']==SHA and not q.get('native_executed',True)
        for p,h in q.get('bindings',{}).items():assert sha(p)==h,p
    bindings={str(P/'source'/n):h for n,h in after.items()}
    bindings.update({str(BASE/'source'/n):h for n,h in before.items()})
    for f in P.rglob('*'):
        if f.is_file() and not f.is_relative_to(P/'source'):bindings[str(f)]=sha(f)
    for old in [D/'luigi-mario-profile731-v1/assembly-error-freeze-v1',D/'luigi-mario-profile731-v2/assembly-error-freeze-v1']:
        for f in old.rglob('*'):
            if f.is_file():bindings[str(f)]=sha(f)
    for name in ['luigi_mario_profile731_prepare_v1.py','luigi_mario_profile731_cpu_v1.py',
        'luigi_mario_profile731_traits_v1.py','luigi_mario_profile731_handoffs_v1.py','luigi_mario_profile731_ready_v1.py',
        'mario_luigi731_coefficients_v1.py','robots_weapon_cpu_v1.py','check_tmnt_render_oa.py',
        'check_tmnt_audio_fallback_oc.py','verify_native_relocation.py','luigi_flower731_rg_prepare_v1.py']:
        f=ROOT/'tools/audit'/name;bindings[str(f)]=sha(f)
    for name in ['cl65.exe','ca65.exe','cc65.exe','ld65.exe']:
        f=ROOT/'tools/Windows/cc65/bin'/name;bindings[str(f)]=sha(f)
    report=ROOT/'docs/qa/luigi-mario-profile731-source-2026-10-26.txt';bindings[str(report)]=sha(report)
    out=P/'source-ready-v1';out.mkdir(exist_ok=False)
    q=dict(passed=True,status='SOURCE_CPU_READY_NATIVE_UNRUN',adopted=False,native_executed=False,native_grant=False,
        ROM_sha256=SHA,parent_ROM_sha256=sha(BASE/'candidate.nes'),source_files=len(after),changed_source_files=changed,
        changed_PRG_banks=get(P/'preparation.json')['changed_PRG_banks'],preserved_EOL_evidence=eols,
        canonical_and_both_flagoffs_pass=True,all_other_source_header_CHR_PRG_and_RAM_exact=True,
        genuine_private_symbol_exceptions=['LuigiNativeTraction::Brake','LuigiNativeTraction::Leftward','_FARCALL_COUNT metadata'],
        foreign_complete_movement_cases=114,foreign_cycle_delta=0,actual_PlayerCtrl_input_cases=60,
        actual_PlayerCtrl_collision_history_cases=18,actual_IRQ_RTI_injections=428,
        jump_comparisons=18,braking_formula_cases=96,shared_dry_field_cases=40,
        native_handoff_cases=30,new_live_farcall_operands_fully_disclosed=True,
        legacy_water_climb_spring_stomp_gap_policy_unchanged=True,
        limitations='No new native/cadence/PPU/audio/natural-item/1-1 result. Different new live farcall operands are disclosed for some Luigi legacy handoffs, not silently called identical. No production changes.',
        bindings=bindings)
    (out/'readiness.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,bindings=len(bindings),readiness_sha256=sha(out/'readiness.json'),ROM_sha256=SHA),indent=2))


if __name__=='__main__':main()
