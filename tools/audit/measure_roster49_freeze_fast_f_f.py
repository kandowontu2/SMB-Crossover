"""Measure matched old/new leaf costs on fresh actual F start states."""
from pathlib import Path
import collections,hashlib,importlib.util,json,statistics
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-freeze-render-fast-f'
E=V/'root49-ice-integrated-e';A=V/'agent49-samus-bill-arsenal-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'matched-native-cost-f.json';assert not out.exists()
    sp=importlib.util.spec_from_file_location('original_native_cpu',A/'palette_native_model_cu.py')
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    groups=[]
    for mp in ['mmc3','mmc5']:
        old=m.q.Image(R/'build/checkpoints/roster-audit-v49-ice-over-sophia-e'/f'smb-crossover-{mp}.nes')
        new=m.q.Image(H/'source/build'/f'smb-crossover-{mp}.nes');O=H/('state-cm-'+mp)
        ev=[json.loads(x)for x in(O/'trace.jsonl').read_text().splitlines()];raw=(O/'ram.bin').read_bytes();pairs={}
        for q in ev:
            if q['event']in ['entry','return']:pairs.setdefault(q['id'],{})[q['event']]=q
        costs=[]
        for ident,p in pairs.items():
            e,z=p['entry'],p['return']
            if e['name']!='SamusFreezeRenderFinish':continue
            initial=m.snapshot(raw,e);regs=[e[n]for n in ['A','X','Y','P','SP']]
            banks={a:e[n]for a,n in [(0x8000,'bank8'),(0xa000,'bankA'),(0xc000,'bankC'),(0xe000,'bankE')]}
            a=m.execute(old,initial,regs,banks,old.hook('SamusFreezeRenderFinish')['address'],z['PC'],z['SP'])
            b=m.execute(new,initial,regs,banks,e['PC'],z['PC'],z['SP'])
            assert a['regs']==b['regs']and a['ram']==b['ram']and a['banks']==b['banks']and a['selector']==b['selector']
            assert[(v[2],v[4])for v in a['trace']]==[(v[2],v[4])for v in b['trace']]
            costs.append(dict(id=ident,case=e['case'],E_cycles=a['cycles'],F_cycles=b['cycles'],saved=a['cycles']-b['cycles']))
        def opportunities(folder):
            ct=json.loads((folder/'state-lifecycle-protocol-review-ct.json').read_text())
            g=next(z for z in ct['groups']if z['mapper']==mp);counts=collections.defaultdict(collections.Counter)
            for z in g['lease']:
                q=counts[z['case']];q['draws']+=1;q['blue']+=z['blue'];q['ordinary']+=1-z['blue'];q['tagged_sprites']+=z['tagged'];q['conflicting_sprites']+=z['conflicting']
            return{k:dict(v)for k,v in counts.items()}
        groups.append(dict(mapper=mp,matched_actual_F_start_states=len(costs),costs=costs,
          summary=dict(E_median=statistics.median(z['E_cycles']for z in costs),F_median=statistics.median(z['F_cycles']for z in costs),
            saved_min=min(z['saved']for z in costs),saved_median=statistics.median(z['saved']for z in costs),saved_max=max(z['saved']for z in costs)),
          actual_scene_opportunities=dict(E=opportunities(E/'root-review-az'),F=opportunities(H/'native-review-e'))))
    result=dict(status='PASS_MATCHED_F_NATIVE_START_STATES_IDENTICAL_OUTPUT_LOWER_ACTIVE_LEAF_CYCLES',
      script_sha256=sha(__file__),groups=groups,native_review_sha256=sha(H/'native-review-e/review.json'),
      interpretation='Same captured actual F complete start RAM/registers/banks, isolated E and F leaf execution without ISR injection or DMA stalls. Fresh full actual native interrupt closure is separately reexecuted by original models. No changed output/write masks.',
      limitations=['Only the active palette leaf changes. All other ROM bytes are literal E; inactive/Easy paths retain their earlier costs and open route negatives.',
        'Scene opportunities are actual observed counts, with changed physical cadence. These are not identical physical-frame windows, a universal FPS claim, or every-enemy/item/arsenal fidelity.',
        'Palette contention intentionally alternates frozen/ordinary chances; optimization does not eliminate NES scanline limits.'],main_changed=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],sha(out),[(g['mapper'],g['summary'])for g in groups],flush=True)
if __name__=='__main__':main()
