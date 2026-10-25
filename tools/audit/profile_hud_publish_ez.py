"""Measure compiled numeric production plus actual primary-queue publication."""
from pathlib import Path
import importlib.util
import argparse
import json
import traceback

R=Path(__file__).resolve().parents[2]
O=R/'build/verification/hud-publish-cost-ez'
sp=importlib.util.spec_from_file_location('hud_ez',R/'tools/audit/review_hud_tail_ek.py')
t=importlib.util.module_from_spec(sp)
sp.loader.exec_module(t)
m=t.m


def publish(im, raw):
    raw=bytearray(raw)
    data=t.h.queue(im,raw)
    i,count=0,0
    while data[i]:
        flags=data[i+2]
        i+=3+(1 if flags&64 else flags&63)
        count+=1
    assert i==len(data)-1
    for n,v in [('NmiR0',im.ram['VRAM_Buffer1']&255),('NmiR1',im.ram['VRAM_Buffer1']>>8)]:
        raw[t.h.at(im.ram[n])]=v
    raw[0x1ef]=255
    raw[0x1f0]=0x5c
    reads=[dict(address=0x2002,value=0)for _ in range(count+1)]
    q=m.execute(im,raw,[0,0,0,1,238],{0x8000:62,0xa000:3,0xc000:32,0xe000:63},im.hook('UpdateScreen')['address'],0x5d00,240,hardware=reads)
    return dict(cycles=q['cycles'],packets=count,PPUDATA_writes=sum(z[2]==0x2007 for z in q['trace']))


def main():
    global O
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,default=R/'build/verification/hud-tail-dz/source')
    parser.add_argument('--tag',default='hud-publish-cost-ez')
    args=parser.parse_args()
    O=R/'build/verification'/args.tag
    assert not O.exists()
    O.mkdir()
    report=dict(status='REVIEWING',groups=[],goal_complete=False,
        scope='Matched compiled component CPU cycles. Every normal queue packet and UpdateScreen instruction executes; PPUSTATUS read values are authored zero because this routine uses them only to reset the PPU latch. No elapsed-frame or whole-game lag claim. This adds the same full queue publication to each numeric call only as a local counterexample/gating test; do not sum these per-call publication costs over a frame.')
    try:
        for mapper in ('mmc3','mmc5'):
            ims=[m.q.Image(R/f'build/checkpoints/water-visible-cw/build/smb-crossover-{mapper}.nes'),m.q.Image(args.candidate/f'build/smb-crossover-{mapper}.nes')]
            folder=R/f'build/verification/hud-tail-native-er/CW-{mapper}/native'
            events=[json.loads(x)for x in(folder/'caller.jsonl').read_text().splitlines()]
            raw=(folder/'caller-ram.bin').read_bytes()
            group=dict(mapper=mapper,cases=[])
            report['groups'].append(group)
            for e in events:
                if e['event']!='entry':
                    continue
                z=next(z for z in events if z['event']=='return'and z['id']==e['id'])
                regs=[e[n]for n in ('A','X','Y','P','SP')]
                banks={ad:e[n]for ad,n in((0x8000,'bank8'),(0xa000,'bankA'),(0xc000,'bankC'),(0xe000,'bankE'))}
                qs=[m.execute(im,m.snapshot(raw,e),regs,banks,e['PC'],z['PC'],z['SP'])for im in ims]
                if t.h.queue(ims[0],qs[0]['ram'])==t.h.queue(ims[1],qs[1]['ram']):
                    continue
                costs=[publish(im,q['ram'])for im,q in zip(ims,qs)]
                producer=[q['cycles']for q in qs]
                total=[p+c['cycles']for p,c in zip(producer,costs)]
                group['cases'].append(dict(id=e['id'],native_frame=e['frame'],producer_cycles=producer,publication=costs,
                                          composed_cycles=total,delta=total[1]-total[0],same_PPU_image=True))
            print(mapper,[(z['native_frame'],z['delta'])for z in group['cases']],flush=True)
        deltas=[z['delta']for g in report['groups']for z in g['cases']]
        report.update(status='MEASURED_PRIVATE_HUD_PRODUCER_AND_PUBLICATION',all_sampled_composed_calls_no_slower=all(d<=0 for d in deltas))
    except Exception as error:
        report.update(status='FAILURE_RETAINED',error=repr(error),traceback=traceback.format_exc())
        raise
    finally:
        (O/'summary.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
