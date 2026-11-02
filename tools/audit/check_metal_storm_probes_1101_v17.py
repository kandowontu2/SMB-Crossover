"""Compare actual routed head/side queries with native block-buffer contracts."""
from pathlib import Path
import itertools,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_metal_storm_probes_1101_v17 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
def main():
    b=scoped_load(P.O/'candidate.nes');seed=M.fresh(b);cases=0
    for head,x,y,probe in itertools.product([True,False],[0,15,40,127,240,255],[32,80,144,176],[30,33,34,35,36]):
        if head and probe!=30:continue
        if not head and probe==30:continue
        a=M.fork(seed);M.put(a,SelectedCharacter=35,Player_X_Position=x,Player_PageLoc=1,Player_Y_Position=y,Player_Y_HighPos=1)
        start=address(b,'Block_Buffer_1')
        for i in range(416):a[start+i]=0x61 if i%3==0 else 0
        z=M.fork(a)
        left=M.invoke(a,'HuHead' if head else 'HuSide',a=176,y=probe)
        right=M.invoke(z,'BlockBufferColli_Head' if head else 'BlockBufferColli_Side',a=176,y=probe)
        assert tuple(left[n] for n in ['A','X','Y','P'])==tuple(right[n] for n in ['A','X','Y','P']),(head,x,y,probe,left,right)
        assert bytes(a[:11])==bytes(z[:11])
        assert a.ram==z.ram
        cases+=1
    run=P.O/'native-smoke';native=json.loads((run/'capture/result.json').read_text());binding=json.loads((run/'capture/binding.json').read_text())
    assert native['passed'] and native['world_x']==73 and binding['exit_code']==0 and binding['ROM_sha256']==P.P.P.sha(P.O/'candidate.nes')
    q=dict(passed=True,installed=False,ROM_sha256=binding['ROM_sha256'],native_probe_contract_cases=cases,native=native,
           fixed='Head/side queries returned incoming A through a rejection callback, falsely reporting solid tiles. Canonical native ROM probes now return real tile and coordinate outputs.',
           limits='Native screenshot shows black sky: world-palette callback unfinished. Health/combat/audio, full-stage and broader native regressions remain incomplete. Do not publish yet.')
    (P.O/'probe-CPU.json').write_text(json.dumps(q,indent=2)+'\n')
    d=R/'docs/qa/checkpoints/2026-11-01/metal-storm-probes-v17';d.mkdir(exist_ok=True)
    files=[P.O/'assembly.json',P.O/'probe-CPU.json',P.O/'metal_storm_native_transport.inc',run/'controller.lua',run/'ready.json',run/'capture/result.json',run/'capture/binding.json',run/'capture/walking.png']
    packet=d/'source-and-native.zip'
    with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED) as archive:
        for f in files:archive.write(f,f.relative_to(R).as_posix())
    q['packet_sha256']=P.P.P.sha(packet);q['packet_bytes']=packet.stat().st_size
    (d/'receipt.json').write_text(json.dumps(q,indent=2)+'\n')
    path=R/'docs/qa/continuation-current.json';c=json.loads(path.read_text())
    c['previous_goal_turn_classification']='progress'
    c['metal_storm_spawn_fix']=dict(checkpoint=str(d.relative_to(R)),candidate=str(P.O/'candidate.nes'),installed=False)
    c['current_priority']='Metal Storm spawn/idle shove fixed by actual head/side query contracts; native moves X40→73. Fix black sky from missing world-palette callback, then health/combat/audio and broader native checks. Public7ec9 unchanged; full roster goal incomplete.'
    path.write_text(json.dumps(c,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
