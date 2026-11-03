"""Verify compact helper milestones with explicit remaining native blockers."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/helper-freeze-root-1103-v89'
JOBS=[('dkjr-score-tail-v59','build/dkjr-native-source-1102-v2/native-score-tail-v59.json','f64a968c9cbdddd0e4636aaed957ce7f99f05fd0c127d475445f44f64771b1eb'),('prince-current-v115','build/prince-actor-1101-v1/current-checkpoint-v115.json','50052ec19203fc81506b4e74cf0d594429da8e62850b6b22d008954d73c211d5')]
def main():
    O.mkdir(exist_ok=True);rows=[];sources=[]
    for name,path,pin in JOBS:
        manifest=R/path;q=json.loads(manifest.read_text());archive=R/q['archive']
        assert q['passed']and not q['ROM_written']and not q['installed']
        assert archive.stat().st_size==q['archive_bytes']<400000 and sha(archive)==q['archive_SHA256']==pin
        records=q['members']
        if isinstance(records,list):records={m['path']:m for m in records}
        with zipfile.ZipFile(archive)as z:
            assert set(z.namelist())==set(records)
            for rel,m in records.items():
                data=z.read(rel);assert len(data)==m['bytes'] and hashlib.sha256(data).hexdigest()==m['SHA256']
                assert not Path(rel).is_absolute() and '..'not in Path(rel).parts
                assert Path(rel).suffix.lower()not in ['.nes','.dbg','.o','.png','.mp4']
            files=q.get('source_files_to_commit')or[f['path']for f in q['source_files']]
            for rel in files:assert z.read(rel)==(R/rel).read_bytes();sources.append(rel)
        dest=R/'docs/qa/checkpoints/2026-11-03'/name;dest.mkdir(parents=True)
        (dest/'inputs.zip').write_bytes(archive.read_bytes());(dest/'helper-manifest.json').write_bytes(manifest.read_bytes())
        correction=('The predecessor50 helper manifest is actually named helper-manifest.json in its retained checkpoint; inherited59 refers to manifest.json. The predecessor archive hash is correct. No historical input was rewritten.'if name.startswith('dkjr')else'Frontend proposal only; actual114 earned-strike native defeat corrupts live SMC under FF lag NMI. No menu/gameplay admission.')
        receipt=dict(passed=True,private_checkpoint_only=True,installed=False,ROM_written=False,archive_SHA256=pin,archive_bytes=archive.stat().st_size,members=len(records),source_files=files,scope_correction=correction,bindings={str(p.relative_to(R)):sha(p)for p in[Path(__file__),manifest,dest/'inputs.zip',dest/'helper-manifest.json']})
        (dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');rows.append(dict(checkpoint=dest.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,members=len(records),source_files=len(files)))
    (O/'receipt.json').write_text(json.dumps(dict(passed=True,rows=rows,source_files=sources),indent=2)+'\n')
    handoff=R/'docs/qa/continuation-current.json';h=json.loads(handoff.read_text())
    h['dkjr_current_source_1102']['checkpoints'].append(rows[0]['checkpoint'])
    h['dkjr_current_source_1102']['latest_unfrozen']='Frozen59 source-owned score tail: same original point popup/AXYP, native AddToScore after donor phase returns before owning Main returns.144 point/248 actualMain comparisons;725IRQ+725genuineFF and4044 nestedIRQ pass,minimumSP128; full packet/indirect writer closure.8032Bbody/128spare,metadataD77B/133spare. Retains53 true SMC negative;17 APIs and actual current shared integration/native admission remain unfinished.'
    prince=h['prince_current_source_1102']if'prince_current_source_1102'in h else next(v for k,v in h.items()if k.startswith('prince')and isinstance(v,dict)and'latest_private'in v)
    prince['current_checkpoint']=rows[1]['checkpoint']
    prince['latest_private']='Frozen115 preserves97 currentcold/respawn/foreign/render and actual102FF/104nested scopes;112 explicitly measures zeroI1. Frontend109 same-footprint26changedbytes:93 uniqueprofiles/94machine states, correct raw38/alt16 confirmations/blank disabled marker/exact assembled resolver/masks. Actual114 original-earned native enemy defeat corrupts live SMC atFF NMI/FarCallCommon SP130. This blocks native admission; helper measuring source-owned shallower defeat delivery, no waiver.'
    bub=h['bub_original_upgrades_current_1102'];bub['latest_candidate']=dict(candidate='build/bub-initial-tier-1103-v87/bub-initial-tier.nes',ROM_SHA256='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd',cookie='a72701f3691d419fd9ae7473840ce393',installed=False,fully_qualified=False,source_gap_remaining=528,native_progress='Both actual88 controller-only earned firstmushrooms pass, native60update/source01/lives2. Bub full1-1 passes13460frames/5195Main/61053checks; Bob full run inprogress. Root87 fixes real SMB2 preview inheritednativeStatus1 via10B owner cold/newlife leaf atB320, no extra stack/warm changes;18paired lifetimecases+10IRQ+10genuineFF new-instruction cuts pass. Parent61 expanded posthead/nested mapper oracle review pending; no release claim.')
    handoff.write_text(json.dumps(h,indent=2)+'\n');print(json.dumps(dict(passed=True,rows=rows)))
if __name__=='__main__':main()
