"""Fresh unchanged earned-arsenal profiles for the private two-repair union."""
from pathlib import Path
import argparse,json,sys
import current_mega_arsenal_prepare_v1 as inherited

R=Path(__file__).resolve().parents[2];B=R/'build'
EXPECTED='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
ROM=B/'mega_proto_body_palette_9ea.nes';sha=inherited.sha

def verify(bindings):
    if isinstance(bindings,dict):assert all(sha(p)==v for p,v in bindings.items())
    else:assert all(sha(x['path'])==x['sha256']for x in bindings)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--identity',choices=['megaman','proto'],required=True)
    ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve()
    assert not out.exists()and sha(ROM)==EXPECTED
    union=B/'mega_proto_body_palette_9ea_build.json';z=json.loads(union.read_text());verify(z['bindings'])
    assert z['candidate_sha256']==EXPECTED and z['exact_disjoint_union']and z['changed_bytes']==58
    handoff=B/'mm_player_prg_owner_handoff.json';h=json.loads(handoff.read_text());verify(h['bindings'])
    assert sha(handoff)=='ce6f5d982abd79e4892dd57b9bae93737cf6ddc8046062375bd23c91ac571ce6'
    original=B/('current-9ea-'+a.identity+'-hard-arsenal-v1')
    previous=json.loads((original/'prepared-not-run.json').read_text());verify(previous['bindings'])
    old_constant=inherited.EXPECTED
    # This is a fresh execution of the unchanged source campaign and producer,
    # using the real combined ROM and real compiled metadata. No old proof is
    # relabeled and no frozen shared tool/Lua is edited.
    inherited.EXPECTED=EXPECTED
    sys.argv=[str(Path(inherited.__file__)), '--identity',a.identity,'--rom',str(ROM),'--output',str(out)]
    inherited.main()
    cfg=json.loads((out/'config.json').read_text());oldcfg=json.loads((original/'config.json').read_text())
    normalized=dict(cfg,ROM_sha256=old_constant);assert normalized==oldcfg,'Only target ROM metadata may change'
    prior_command=json.loads((original/'command.json').read_text())['argv']
    current_command=json.loads((out/'command.json').read_text())['argv']
    command_normalized=[x.replace(str(out),str(original)).replace(str(ROM),str(B/'bill_early_cache.nes'))for x in current_command]
    assert command_normalized==prior_command,'Actual controller/runtime/caps/CLI stay literal'
    source=json.loads((out/'source-controls.json').read_text())
    assert source['ROM_sha256']==EXPECTED and source['passed']and source['complete_GameLoop_calls']==2195
    ready_path=out/'prepared-not-run.json';ready=json.loads(ready_path.read_text())
    paths=[Path(__file__),union,handoff,B/'mm_player_prg_owner_controls.json',B/'mm_player_prg_owner_pose_controls.json',
           B/'proto_normal_palette_ack_9ea_build.json',B/'proto_normal_palette_ack_9ea_cpu.json',B/'proto_normal_palette_ack_9ea_caller.json',B/'proto_normal_palette_ack_9ea_flagoff.json',
           B/'mm_player_prg_owner_metasprite_engine.s',B/'mm_player_prg_owner_megaman_weapons.s',B/'proto_normal_palette_ack_9ea_source.s',
           B/'mega_proto_body_palette_9ea_entrypoint.s',R/'tools/audit/mega_proto_body_palette_9ea_build_v1.py']
    existing={x['path']for x in ready['bindings']}
    ready['bindings'] +=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in paths if str(p.resolve())not in existing]
    ready.update(exact_disjoint_union_source_receipt_sha256=sha(union),native_run=False,
                 reused_frozen_mechanics_sha256=sha(R/'tools/audit/current_mega_arsenal_v1.lua'),
                 deliberate_identity_delta='None versus the same identity original9ea profile; actual numericHard1/ProtoVariant is retained.',
                 source_overlay=z['source_overlay'],source_binding_role='Existing canonical leaf bindings retain parent provenance; the three explicit leaf overlays and genuine linked ROM/DBG are the actual candidate inputs.',
                 source_execution='Fresh2195 completeGameLoops on the real combined bundle per identity; unchanged inherited campaign with EXPECTED parameter rebound only in this new process.',
                 limits=ready['limits']+' Candidate source costs remain explicit: body ownership repair+25Mega/+27Proto vs correct-bank reference; foreign indirect player+9/world+1. Successful normalProto acknowledgment+4 foregroundCPU, removes only redundant six-byte palette command; observed152NMI-cycle saving projects14CPU guard margin only, not native/global closure. Original9ea Proto deadlineFALSE and Mega missing-body evidence remain unchanged.')
    inherited.put(ready_path,ready);verify(ready['bindings'])
    print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',identity=a.identity,ROM_sha256=EXPECTED,ready=str(ready_path),sha256=sha(ready_path),bindings=len(ready['bindings']),fresh_GameLoop_calls=source['complete_GameLoop_calls'])))

if __name__=='__main__':main()
