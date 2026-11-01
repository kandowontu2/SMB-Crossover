"""Verify installed bytes, retain CHR closure and record the next allocations."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from build_storage_guard_v1 import preflight

R=Path(__file__).resolve().parents[2];O=R/'build/kirby-delivery-finalize-1101-v2'
D=R/'docs/qa/checkpoints/2026-11-01/kirby-owner-nightly-v2'
M=R/'docs/qa/checkpoints/2026-11-01/metal-storm-chr-resources-v10'
PIN='c864e46a8f333ab7a936c8d8f330944041a3eff12bc6dd4d9ba96892144ff3c7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    preflight(private_root=O,reserved_bytes=1000000,reserved_files=10,fresh=True);O.mkdir()
    q=json.loads((D/'handoff.json').read_text());assert q['passed']and q['output_sha256']==PIN and sha(q['destination'])==PIN
    count=0
    for key in ['source','native']:
        p=R/q[key]['path'];assert sha(p)==q[key]['sha256']
        with zipfile.ZipFile(p)as z:
            manifest=json.loads(z.read('files.json'));assert len(z.namelist())==q[key]['members']
            for n,v in manifest.items():
                data=z.read(n);assert len(data)==v['bytes']and hashlib.sha256(data).hexdigest()==v['sha256'];count+=1
    archive=R/'build/metal-storm-chr-closure-1101-v10/source-proof.zip';expected='a30a18a8d840c6720d603c9456d37a978b7ebcba25f619c6c1a0783cab91ee86'
    assert sha(archive)==expected and not M.exists();M.mkdir();target=M/'source-proof.zip';shutil.copyfile(archive,target)
    grant=dict(passed=True,baseline_ROM_sha256=PIN,closure_packet=target.relative_to(R).as_posix(),closure_sha256=expected,
        accepted_existing_consumer_closure=True,CHR_pages_granted=True,
        Metal_pages=[*range(247,251),*range(494,501),*range(827,832)],Tank_pages=[501,502],Thomas511_remains_owned=True,
        PRG_gates_granted=False,RAM_runtime_lease_granted=False,menu_admitted=False,native_qualified=False,
        conditions=['Metal uses500 in place of HUD-owned1023. Keep the original sprite shape and approved player-only red/white/black adaptation; native P1/P2/P3 remain exact.',
          'Freeze code/CHR before checksums and complete owner headers. No shared callback may enter an unloaded or unauthenticated runtime image.',
          'Current PRG tail ownership, conditional work-RAM lifecycle, constructors/retirement, actual Main/ISR and native play still require qualification.',
          'This allocates only the listed CHR pages. No permission to reuse arbitrary zero/FF data or fixed mirror space.'])
    (M/'resource-grant.json').write_text(json.dumps(grant,indent=2)+'\n')
    p=R/'README.md';text=p.read_text(encoding='utf-8').replace('a3px/update speed','a 3 px/update speed').replace('steady60Hz','steady 60 Hz');p.write_text(text,encoding='utf-8',newline='\n')
    p=R/'docs/qa/continuation-current.json';state=json.loads(p.read_text())
    state.update(Mesen='All root-owned SMB native runs for c864 delivery are terminal. Other-project sessions were left untouched.',
        agents='Mario the Tank ROM-gate/loader funding; Metal Storm actual owning graft using accepted CHR resources; third worker available after completing Kirby.',
        current_priority='Delivered c864 Kirby repair and Karnov HUD. Proceed with Metal Storm owning integration and Mario the Tank ROM gates/loader; keep current Kirby override composed. Full roster/campaign/playthrough goal remains active.',
        cleanup_rejection=dict(action='Delete Mario the Tank host.o and host.dbg temporary outputs',reason='Automatic approval review blocked deletion under policy',bytes=64959,retained_within_caps=True),
        storage=preflight(fresh=True))
    state['active_source_components']['CHR_resource_grant']=dict(path=(M/'resource-grant.json').relative_to(R).as_posix(),sha256=sha(M/'resource-grant.json'))
    p.write_text(json.dumps(state,indent=2)+'\n')
    result=dict(passed=True,ROM_sha256=PIN,installed_bytes_exact=True,archive_members_verified=count,CHR_grant=grant,storage=state['storage'],
        bindings={str(p.resolve()):sha(p)for p in [Path(__file__),D/'handoff.json',R/'README.md',M/'resource-grant.json',target]})
    for p in [O/'result.json',D/'delivery-finalized.json']:p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,ROM_sha256=PIN,build_bytes=state['storage']['build_bytes'],build_files=state['storage']['build_files'])))


if __name__=='__main__':main()
