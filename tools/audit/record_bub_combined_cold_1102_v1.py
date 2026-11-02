"""Keep real cold passes separate from the current global-palette failure."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import sha
O=R/'build/bub-menu-candidate-1102-v2'
PIN='00971c9fa4906440e1f52d37ca76b7adde287e902a31e72982dee171b35bfa60'

def main():
    rows=[];inputs=[Path(__file__),O/'combined.json',O/'combined-metadata-repair-v2.json']
    for label,folder,frames in[('Bub','native-combined2-bub-cold',700),('Bob','native-combined3-bob-cold',660)]:
        c=O/folder/'capture';result=json.loads((c/'result.json').read_text());binding=json.loads((c/'binding.json').read_text())
        assert result['passed'] and result['controller_only'] and result['gameplay_launch']
        assert result['frames']==frames and not result['full_stage'] and result['screenshots']==1
        assert result['active_data_writes']==0 and result['late_enables']==0
        assert binding['exit_code']==0 and binding['ROM_sha256']==PIN
        rows.append(dict(character=label,packet=folder,cold_handoff_passed=True,
            frames=frames,Fresh_identity_ready_and_active_engine_asserted=True,
            gameplay_controls_or_combat_qualified=False,PNG_count=1))
        inputs +=[c/'result.json',c/'binding.json',c/'active-owner.png']
    q=dict(passed=False,cold_handoff_passed=True,ROM_SHA256=PIN,installed=False,
        production_admitted=False,full_stage=False,helpers_added=False,
        actual_cold_runs=rows,
        visual_negative=dict(scope='Global palette; not a failed menu/Fresh identity handoff',
            evidence='Bub active-owner screenshot has black sky and green HUD instead of native blue sky/white HUD',
            source_body_shape_and_distinct_Bub_Bob_colors='Body appearance alone does not qualify global palette',
            status='Backend owner tracing actual palette ingress and first writes; no ROM change justified by screenshot alone'),
        preserved_negatives=['native-menu importer before Lua','native-menu2 original Select-before-confirm observer expectation',
            'native-combined-bub-cold importer constants/key2 before Lua'],
        unexecuted_blocked_packet='native-combined2-bob-cold has a missing superseded scaffold binding; no Mesen/gameplay result',
        next='Root qualifies a source-proven palette successor before affected regressions and source controls/combat',
        bindings={p.relative_to(R).as_posix():sha(p)for p in inputs})
    target=O/'combined-cold-native-v1.json';assert not target.exists();target.write_text(json.dumps(q,indent=2)+'\n')
    source=['persist_bub_menu_frontend_1102_v4.py','plan_bub_combined_frontend_1102_v1.py','compose_bub_combined_1102_v1.py',
        'prepare_bub_combined_native_1102_v1.py','repair_bub_combined_symbols_1102_v2.py','prepare_bub_combined_native_1102_v3.py',Path(__file__).name]
    (O/'commit-files-combined-v1.txt').write_text('\n'.join('tools/audit/'+n for n in source)+'\n')
    own=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in own)<32000000 and len(own)<=128
    print(json.dumps(dict(cold_handoff_passed=True,global_palette_qualified=False,installed=False,
        runs=rows,bytes=sum(p.stat().st_size for p in own),files=len(own))))

if __name__=='__main__':main()
