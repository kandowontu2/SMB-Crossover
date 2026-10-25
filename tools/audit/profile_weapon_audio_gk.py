"""Matched actual GF quiet audio entries against GA, without ISR service."""
from pathlib import Path
import hashlib,importlib.util,json,traceback
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'weapons-audio-cost-gk'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
model=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py'
sp=importlib.util.spec_from_file_location('gk_audio_model',model);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)


def main():
    assert not O.exists();O.mkdir()
    report=dict(passed=False,cases=[],scope='Matched compiled full AudioUpdate calls with actual GF entry RAM/registers and captured hardware reads. ISR service removed from both. Song-start variants explicitly author song/current/start and zero Land aliases; no gameplay elapsed-frame or waveform identity claim.',goal_complete=False)
    try:
        for mapper in ('mmc3','mmc5'):
            old=m.q.Image(R/f'build/smb-crossover-{mapper}.nes');new=m.q.Image(V/f'weapons-current-gf/source/build/smb-crossover-{mapper}.nes')
            p=V/'weapons-land-gg'/('V-mmc3-normal-y'if mapper=='mmc3'else'V-mmc5-normal-aa')/'native-output'
            rows=[json.loads(z)for z in(p/'caller.jsonl').read_text().splitlines()];raw=(p/'caller-ram.bin').read_bytes();hw=[json.loads(z)for z in(p/'caller-hardware.jsonl').read_text().splitlines()]
            pairs={}
            for z in rows:
                if z['event']in('entry','return'):pairs.setdefault(z['id'],{})[z['event']]=z
            def at(n):
                a=new.ram[n];return a if a<2048 else a-0x6000+2048
            for pair in list(pairs.values())[::7]:
                e,z=pair['entry'],pair['return'];v=m.snapshot(raw,e)
                if any(v[at(n)]for n in ('MmRushLandRequest','MmRushLandActive','MmRushLandPreviousMask')):continue
                ir=m.irq_records(rows,raw,e,z)
                reads=[h for h in hw if e['cycle']<h['cycle']<z['cycle']and not any(i['entry']['cycle']<=h['cycle']<=i['preRTI']['cycle']+6 for i in ir)]
                banks={a:e[n]for a,n in ((0x8000,'bank8'),(0xa000,'bankA'),(0xc000,'bankC'),(0xe000,'bankE'))}
                for song in (1,2):
                    for mode in (0,1):
                        initial=bytearray(v)
                        initial[at('MmAudioDesiredSong')]=song;initial[at('MmAudioCurrentSong')]=song;initial[at('MmAudioStart')]=1;initial[at('CrossoverBehaviorVersion')]=mode
                        qs=[m.execute(im,initial,[e[n]for n in ('A','X','Y','P','SP')],banks,e['PC'],z['PC'],z['SP'],hardware=reads)for im in (old,new)]
                        a,b=qs
                        for k in ('regs','ports','banks','selector'):assert a[k]==b[k],(mapper,song,mode,k)
                        differences=[]
                        for i,(av,bv)in enumerate(zip(a['ram'],b['ram'])):
                            if av==bv:continue
                            assert 0x100<=i<0x100+z['SP'],(mapper,song,mode,'non-popped-stack difference',i,av,bv)
                            aw=next((t for t in reversed(a['trace'])if t[3]==i),None);bw=next((t for t in reversed(b['trace'])if t[3]==i),None)
                            assert bw and bw[1]in(0x20,0x48,0x08)and(aw is None or aw[1]in(0x20,0x48,0x08)),(i,aw,bw)
                            differences.append(dict(address=i,old=av,new=bv,old_last_writer=aw,new_last_writer=bw))
                        report['cases'].append(dict(mapper=mapper,entry_frame=e['frame'],song=song,mode=mode,cycles=[a['cycles'],b['cycles']],delta=b['cycles']-a['cycles'],registers_ports_banks_selector_and_live_RAM_equal=True,individually_traced_popped_stack_differences=differences))
            print(mapper,sorted({z['delta']for z in report['cases']if z['mapper']==mapper}),flush=True)
        assert report['cases']
        report['passed']=True
    except Exception as ex:report.update(error=repr(ex),traceback=traceback.format_exc());raise
    finally:(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
