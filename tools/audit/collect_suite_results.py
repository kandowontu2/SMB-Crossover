"""Validate full-suite logs after focused reruns, bound to the current ROM CRCs.

Every case must have a passing emulator log and the exact current ROM CRC.
This never converts failed output into a pass. The original full-run log is
retained, including failures subsequently corrected in the test fixtures.
"""
from pathlib import Path
import argparse,hashlib,json,re,zlib
ROOT=Path(__file__).resolve().parents[2]

def main():
    p=argparse.ArgumentParser();p.add_argument('run_log',type=Path);a=p.parse_args()
    log=a.run_log.read_text();cases=[];roms={}
    names=sorted(set(re.findall(r'Full emulator log: .*?(smb-crossover-mmc(?:3-baseline|3|5)-[^\r\n]+\.log)',log)))
    assert names,'No completed test cases in the full-run log'
    for name in names:
        m=re.fullmatch(r'(smb-crossover-mmc(?:3-baseline|3|5))-(.+)\.log',name);assert m,name
        rom,test=m.groups();path=ROOT/'build/verification'/name;raw=path.read_text()
        data=(ROOT/'build'/f'{rom}.nes').read_bytes()
        crc=re.search(r'File CRC32: 0x([0-9A-Fa-f]+)',raw)
        assert crc and int(crc[1],16)==zlib.crc32(data),f'{name}: stale ROM capture'
        assert 'PASS ' in raw and not re.search(r'\bFAIL\b|Lua error',raw),f'{name}: failed emulator log'
        roms[rom]=hashlib.sha256(data).hexdigest()
        cases.append({'test':test,'rom':rom,'result':'passed','log_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    baseline=ROOT/'build/verification/smb-crossover-mmc3-baseline-mario-trace.csv'
    native=ROOT/'build/verification/smb-crossover-mmc3-mario-trace.csv'
    assert baseline.read_bytes()==native.read_bytes(),'Mario baseline diverged'
    assert len(baseline.read_text().splitlines())==521,'Expected 521 Mario updates (no CSV header)'
    report={'result':'passed','emulator':'Mesen 2','hardware_tested':False,
            'method':'Full suite plus focused reruns; each raw log checked for PASS, no FAIL and current ROM CRC.',
            'initial_run_log':str(a.run_log),'initial_run_log_sha256':hashlib.sha256(a.run_log.read_bytes()).hexdigest(),
            'mario_replay':{'frames':521,'fields':19,'identical':True},'cases':cases,
            'roms':{k.removeprefix('smb-crossover-'):v for k,v in roms.items()}}
    out=ROOT/'build/verification/summary.json';out.write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS all {len(cases)} current-ROM emulator cases, including focused fixture reruns; {out}')
    return 0

if __name__=='__main__':raise SystemExit(main())
