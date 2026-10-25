"""Independently qualify current529+Mac source, full audio, and native cadence."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import subprocess
import sys
from check_tmnt_render_oa import load
from robots_weapon_cpu_v1 import Arena
from cv3_dmc_cpu_v1 import diff, regs, apu

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = '52918588bab0eec3f3a1f857bf084d2d799e88a5c781c75233c098ccc5f54f3f'
FINAL = '8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def ordinary(prepared, out):
    old, new = [load(prepared/name) for name in ['baseline.nes','candidate.nes']]
    count, costs = 0, []
    for char, variant, effect in itertools.product((2,3,4,5), range(4), range(27)):
        if char!=5 and variant:
            continue
        if effect==26 and (char,variant)!=(5,3):
            continue
        qs = [Arena(b,char) for b in [old,new]]
        for q in qs:
            q.put(Cv3Variant=variant,AreaMusicQueue=1)
        for tick in range(32):
            for q in qs:
                q.put(GamePauseStatus=int(tick in (16,17)),AvAudioRequest=effect if tick==8 else 0)
                if tick==20:
                    q.m[0x4015]=15
            cs = [q.invoke('AudioUpdate')[0] for q in qs]
            assert apu(qs[0])==apu(qs[1]), (char,variant,effect,tick)
            diff(qs)
            assert regs(cs[0])==regs(cs[1]) and qs[0].m.banks==qs[1].m.banks
            costs.append(cs[1].processorCycles-cs[0].processorCycles)
            count += 1
    result=dict(passed=True,ROM_sha256=FINAL,baseline_ROM_sha256=PARENT,
                full_AudioUpdate_cases=count,added_CPU_cycle_range=[min(costs),max(costs)],
                ordered_APU_RAM_registers_mapper_exact=True,
                scope='Bill, Samus, Link and four CV3 variants; typed effects, pause/resume, ended DMC. CPU outcomes only, no native cadence or waveform claim.')
    (out/'ordinary-audio.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepared',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    out=a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    assert sha(a.prepared/'baseline.nes')==PARENT and sha(a.prepared/'candidate.nes')==FINAL
    assert sha(ROOT/'build/smb-crossover-mmc5-expanded.nes')==PARENT
    tools=[ROOT/('tools/audit/'+name) for name in [
        'mac_native_music_cpu.py','mac_native_music_native.py','mac_native_music_native.lua',
        'mac_native_music_performance.py','vehicles_audio_wiring_guards.lua',
        'tmnt_performance_observer.lua','chr_commit_observer.lua',
        'observe_chip_committed_write.py','run_mesen_isolated.py']]
    hashes={str(path):sha(path) for path in tools}
    gold=D/'mac-native-music-v1/source-probe-v1'
    emulator=D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe'
    def run(name, tool, args):
        with (out/(name+'-host.log')).open('w',encoding='utf-8') as log:
            subprocess.run([sys.executable,str(ROOT/'tools/audit'/tool)]+list(map(str,args)),cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
        print(json.dumps(dict(phase=name,passed=True)),flush=True)
    run('source-cpu','mac_native_music_cpu.py',[
        '--rom',a.prepared/'candidate.nes','--baseline',a.prepared/'baseline.nes',
        '--gold',gold,'--output',out/'source-cpu-v1'])
    controls=ordinary(a.prepared,out)
    print(json.dumps(dict(phase='ordinary-full-audio',**controls)),flush=True)
    for name, rom in [('parent',a.prepared/'baseline.nes'),('candidate',a.prepared/'candidate.nes')]:
        run(name+'-performance','mac_native_music_native.py',[
            '--rom',rom,'--output',out/('native-'+name+'-performance'),
            '--mode','performance','--hard','--run','--emulator',emulator])
    run('performance-compare','mac_native_music_performance.py',[
        '--baseline',out/'native-parent-performance','--candidate',out/'native-candidate-performance',
        '--output',out/'performance.json'])
    run('candidate-music','mac_native_music_native.py',[
        '--rom',a.prepared/'candidate.nes','--output',out/'native-candidate-music',
        '--mode','music','--hard','--gold',gold,'--run','--emulator',emulator])
    source=json.loads((out/'source-cpu-v1/proof.json').read_text())
    perf=json.loads((out/'performance.json').read_text())
    native=json.loads((out/'native-candidate-music/native-result.json').read_text())
    assert source['passed'] and perf['passed'] and native['passed']
    assert native['ROM_sha256']==FINAL and native['config']['hard']==1 and native['config']['music']==1
    assert all(sha(Path(name))==expected for name,expected in hashes.items())
    receipts=[a.prepared/'proof.json',out/'source-cpu-v1/proof.json',out/'ordinary-audio.json',
              out/'performance.json',out/'native-candidate-music/native-result.json',
              out/'native-parent-performance/native-result.json',out/'native-candidate-performance/native-result.json']
    proof=dict(passed=True,adopted=False,goal_complete=False,ROM_sha256=FINAL,parent_ROM_sha256=PARENT,
               composition=str(a.prepared/'proof.json'),
               retained_PC_RAM_CHR_fixed_DPCM_exact=True,new_RAM_bytes=0,new_CHR_bytes=0,
               original_source_CPU_calls=sum(row['source_calls_compared']for row in source['source_music_comparison']),
               full_ordinary_AudioUpdate=controls,
               native_music=native['proof.json'],native_guards=native['ownership-guards.json'],
               native_chr=native['chr-commit.json'],matched_performance=perf,
               tools=hashes,receipts={str(path):sha(path) for path in receipts},
               scope='Independent current529 composition qualification. Nine authentic Punch-Out tracks/14 request selections and matched staged600-update Hard arenas, not natural earning/full campaign, universal lag removal, original waveform identity, or whole-roster completion.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in proof.items()if k not in ['tools','receipts','native_music','native_guards','native_chr','matched_performance']},indent=2))


if __name__=='__main__':
    main()
