"""Observe CV3 primary requests and real inherited audio-wrapper dispatch.

Actual linked control flow, with original music decoder/graphics leaf calls
observed as opaque traps. No claim about hardware APU playback or native CV3 tone.
"""
from pathlib import Path
import argparse, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load
from robots_weapon_cpu_v1 import Arena


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    b=load(a.rom);h=hashlib.sha256(b['raw']).hexdigest()
    assert h=='f00c2a7ad0459a3cd0b369bb4fbc9f374dc27d9335b2cc1fe1867f3f98d73d23'
    rows=[]
    for variant in (1,2,3):
        q=Arena(b,char=5)
        q.put(Cv3Variant=variant,Cv3Fresh=0x40,RgAudioCharacter=5)
        q.invoke('Cv3WeaponsGate')
        request=q.get('RgSfx')
        assert request==4 and q.get('Cv3AttackAge')==(24 if variant==3 else 16)
        _,seen=q.invoke('RosterAudioUpdate',traps=('CvAudioInit','CvAudioPlay','CrossoverGraphicsBank'))
        assert 'CvAudioInit' not in seen and 'CvAudioPlay' in seen
        assert q.get('RgSfx')==0
        q.set('RgSfx',1)
        _,control=q.invoke('RosterAudioUpdate',traps=('CvAudioInit','CvAudioPlay','CrossoverGraphicsBank'))
        assert 'CvAudioInit' in control
        rows.append(dict(variant=variant,attack_request=request,observed_dispatch=seen,
                         request_after_wrapper=0,bit1_positive_control=control))
    proof=dict(passed=True,defect_reproduced=True,ROM_sha256=h,cases=rows,
        implementation_files={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
            for n in ('src/cv3_combat.s','src/roster_audio.s')},
        scope='Real Cv3WeaponsGate primary input and RosterAudioUpdate including bank selection and cleanup execute. CvAudioInit, CvAudioPlay and CrossoverGraphicsBank are observed opaque leaves. No APU rendering, timing or correct native CV3 replacement effect is asserted.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
