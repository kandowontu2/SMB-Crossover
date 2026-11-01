"""Preserve compact upcoming integration evidence without granting a carrier."""
from pathlib import Path
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2]
D=R/'docs/qa/checkpoints/2026-11-01/karnov-next-integration-v3'
O=R/'build/karnov-next-integration-handoff-1101-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    O.mkdir(exist_ok=True)
    if D.exists():
        # Finish only the index publication after a prior output-root failure;
        # never replace the already frozen checkpoint files.
        result=json.loads((D/'handoff.json').read_text())
        for key in ['pickups','carrier']:
            assert sha(D/result[key]['archive'])==result[key]['sha256']
        publish(result)
        return
    carrier=R/'build/karnov-combat-carrier-design-1101-v3'
    publication=json.loads((carrier/'publication.json').read_text())
    assert publication['passed']and not publication['carrier_granted']
    assert sha(carrier/'source-and-proof.zip')==publication['sha256']
    for n,h in publication['source_files'].items():assert sha(R/n)==h,n
    pickup=R/'build/karnov-pickup-host-component-1101-v3'
    q=json.loads((pickup/'integration.json').read_text())
    assert q['passed']and q['pure_source_transform']and q['frozen_split_bytes_compared']==818
    for n,h in q['bindings'].items():assert sha(n)==h,n
    files={n:pickup/n for n in ['integration.json','fragments.cfg','main-fragments.s','kernel-fragments.s','native-symbols.s','kr-pickup-kernel-v3.inc','kr-pickup-rom-align-v3.inc','kr-pickup-rom-context-v3.inc','kr-pickup-rom-tail-v3.inc']}
    for n in ['prepare_karnov_pickup_host_1101_v3.py','preserve_karnov_next_integrations_1101_v3.py']:
        files['tools/audit/'+n]=R/'tools/audit'/n
    D.mkdir()
    archive=D/'pickup-host-source-and-proof.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,p in sorted(files.items()):z.writestr(n,p.read_bytes())
        z.writestr('files.json',json.dumps({n:dict(bytes=p.stat().st_size,sha256=sha(p))for n,p in files.items()},indent=2)+'\n')
    shutil.copyfile(carrier/'source-and-proof.zip',D/'carrier-source-and-proof.zip')
    shutil.copyfile(carrier/'HANDOFF.md',D/'CARRIER-HANDOFF.md')
    result=dict(passed=True,installed=False,ROM_modified=False,carrier_granted=False,
        current_installed_ROM='e8d35a95ffe8e396dc1d8b32ca78d57d376fc14de9a2f4b37754012448fde09a',
        pickups=dict(archive=archive.name,sha256=sha(archive),bytes=archive.stat().st_size,frozen_split_bytes=818,tail_thunks=36,added_kernel_bytes=78,fully_composed=False),
        carrier=dict(archive='carrier-source-and-proof.zip',sha256=sha(D/'carrier-source-and-proof.zip'),bytes=(D/'carrier-source-and-proof.zip').stat().st_size,granted=False,body_spare_bytes=448,proposed_CHR_pages=[1019,1020],proposed_code_bytes=1040,source_units=690,writer_units=76,closed_selector_groups=15),
        next=['Integrate pickup source transformer, requalify native item emergence/contact/progression and actual Main interrupts before delivery.','Before allocating combat carrier, close Arthur201 descriptor headers/fallbacks plus generic CHR shadows/overrides across scenes; zero-fill/partial table bounds are insufficient.','Then compose real cold copy/readback before both cookies, native combat ingress and actual Main stack depth. Service-level ISR reserve is not a Main proof.'])
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n')
    publish(result)


def publish(result):
    (O/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    p=R/'docs/qa/continuation-current.json';state=json.loads(p.read_text())
    state['Karnov_current']['next_integration_checkpoint']=D.relative_to(R).as_posix()
    state['Karnov_current']['carrier_policy']='Carrier remains ungranted. Body spare is448B, not~2864. Proposed1019/1020 requires remaining Arthur201 descriptor/fallback and generic shadow/override scene ownership closure. Compact evidence is frozen; never expand the690-file dependency graph.'
    p.write_text(json.dumps(state,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
