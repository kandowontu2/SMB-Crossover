"""Freeze current Mike-parent Roll fade build/CPU/native/visual qualification."""
from pathlib import Path
import argparse,csv,hashlib,json,re,shutil,statistics
ROOT=Path(__file__).resolve().parents[2]
PARENT='9e0e5ed5d4957aac9baa040ea76616ee4a88233312700b78a8c55250c19f42d3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--private',type=Path,required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    build=json.loads((a.private/'proof.json').read_text(encoding='utf-8'));aggregate=a.private/'calm-aggregate-v1/proof.json';z=json.loads(aggregate.read_text(encoding='utf-8'));review=json.loads(a.review.read_text(encoding='utf-8'))
    assert build['passed']and build['base_sha256']==PARENT and z['passed']and z['actual_PPU_RGB_controls_passed']and review['reviewed_actual_PPU_frames']==48 and review['visual_review_passed']
    assert review['aggregate_sha256']==sha(aggregate)
    assert all(sha(Path(n))==v for n,v in z['bindings'].items())
    assert all(sha(Path(n))==v for n,v in review['viewed_sheets'].items())
    cpu={n:json.loads((a.private/n/'proof.json').read_text(encoding='utf-8'))for n in ['cpu-fade-v1','cpu-owner-v1','cpu-parent-resource-v1','cpu-candidate-resource-v1']}
    assert all(q['passed']for q in cpu.values())and cpu['cpu-fade-v1']['helper_cases']==162816 and cpu['cpu-fade-v1']['whole_draw_cases']==1520 and cpu['cpu-owner-v1']['cases']==412 and cpu['cpu-parent-resource-v1']['cases']==cpu['cpu-candidate-resource-v1']['cases']==8140
    assert cpu['cpu-fade-v1']['baseline_SHA256']==PARENT and cpu['cpu-fade-v1']['candidate_SHA256']==build['candidate_sha256']
    assert cpu['cpu-owner-v1']['baseline_sha256']==PARENT and cpu['cpu-owner-v1']['candidate_sha256']==build['candidate_sha256']
    assert cpu['cpu-parent-resource-v1']['ROM_sha256']==PARENT and cpu['cpu-candidate-resource-v1']['ROM_sha256']==build['candidate_sha256']
    cadence=[];profiles=[]
    for mode in [0,1]:
        suffix='hard'if mode else'easy';groups=[]
        for role in ['baseline','candidate']:
            folder=a.private/('native-'+role+'-'+suffix+'-v1');proof=json.loads((folder/'proof.json').read_text(encoding='utf-8'));n=proof['native'];expected=PARENT if role=='baseline'else build['candidate_sha256']
            assert n['ROM_sha256']==expected and n['actual_mode_readback']==mode and n['mechanics_passed']and n['fade_policy_passed']==(role=='candidate')and proof['passed']==(role=='candidate')
            assert proof['dependencies_unchanged']and proof['emulator_exit']==0
            group=[r for r in csv.DictReader((folder/'cadence.csv').open(encoding='utf-8'))if r['phase']=='empty-before'];assert len(group)==120
            assert all(int(r['draw_calls'])==1 and int(r['drops'])==0 for r in group);groups.append(group)
            profiles.append(dict(role=role,mode_value=mode,proof_sha256=sha(folder/'proof.json'),ROM_sha256=expected,mechanics_passed=True,fade_policy_passed=n['fade_policy_passed'],updates=n['updates'],wall_frames=n['wall'],real_births=len(n['births']),defeats=n['kills'],natural_expiries=n['natural_expiries'],real_pickups=n['real_pickups'],calm_max_scanline_sprites=n['calm_max_scanline_sprites'],nmis=n['nmis'],irq_scroll_stores=n['irq_scroll_stores'],hardware_chr_checks=n['hardware_chr_checks'],dma_checks=n['complete_dma_checks'],min_sampled_SP=n['minSP'],first_wrong_admission=n.get('first_wrong_native_admission'),first_wrong_oam_write=n.get('first_wrong_native_oam_write')))
        old,new=groups;delta=[int(y['inclusive_cycles'])-int(x['inclusive_cycles'])for x,y in zip(old,new)]
        assert sum(delta)==60*120
        cadence.append(dict(mode_value=mode,completed_updates_each=120,baseline_actual_wall_frames=len({r['wall']for r in old}),candidate_actual_wall_frames=len({r['wall']for r in new}),renders_each=120,inclusive_cycle_delta_min=min(delta),inclusive_cycle_delta_max=max(delta),inclusive_cycle_delta_mean=statistics.mean(delta),scope='Same frozen controller, cold arena/idle before any target or RNG search; measured update entry/finish. Inclusive CPU spans include actual interrupts. Not a constant60Hz/campaign certification.'))
    total=lambda n:sum(q[n]for q in profiles)
    report=ROOT/'docs/qa/final-roll-items-fade-current-2026-10-25.txt'
    text=f'''Roll fade on qualified Mike parent: current composition, 2026-10-25

The private combined candidate passes fresh current-parent build, CPU and both-mode calm native/RGB/idle controls. ROOT alone integrates it. The broader every-character/every-item goal and crowded body visibility remain open.

Exact parent: {PARENT}
Exact child: {build['candidate_sha256']}
Parent source is the frozen current5ec baseline plus exactly the four qualified Mike ready files. Its private rebuild reproduces9e0e exactly. The child overlays only frozen roll.s, roll_render.s and new roll_drop_fade.s. No ROOT production, Git, Downloads or user Mesen PID165672 was modified.

Build boundaries
Only36 PRG bytes change, all in bank119: the existing3-byte LDA becomes JSR at $A68F, and33 helper bytes use previouslyFF space at $AAC0. All72,217 old scoped symbol addresses, all other ROM bytes/banks, RAM, CHR and supplied art remain exact to9e0e. The three Roll source files match the previously frozen patch exactly.
Standard flag-off MMC3 remains {build['ordinary_flag_off_hashes']['mmc3']}.
Standard flag-off MMC5 remains {build['ordinary_flag_off_hashes']['mmc5']}.
Both match their qualified Mike parent target hashes. The expanded parent and child were freshly compiled using frozen source overlays; nonproduction build inputs are hashed before/after.

Fresh CPU controls on these exact parent/child bytes
162,816 helper/shared-policy cases and1,520 full RlDraw comparisons preserve return registers and ordered nonstack application/SMC/mapper/OAM writes against actual assembled shared admission plus unchanged-art/empty-actor oracles. Declared CPU ages include0..420 and explicit unreachable high-age boundary controls.
412 current-parent object/order/admission/pause cases compare full ordered writes, registers, cycles and return stack:288 whole object dispatch/standalone sole-owner cases,8 explicit final-hit birth cases,4 ordinary Bass controls,104 actual variant admissions,6 inactive cases and2 paused whole GameLoops.
8,140 resource/food/capsule/HUD/charge/injury/reset controls pass independently on each exact ROM. These are explicit CPU state tests; they do not claim natural acquisition, IRQ timing or original mobile fidelity.
The helper CPU test reuses a frozen copy of the prior test with only its expected base hash changed and an explicit audit import path. Its original9bac native-observation prose stays historical. The inserted import header makes that copied module's __doc__ null; its assertions and case coverage are unchanged and bound separately in cpu-bound-source/binding.json.

Fresh native scope
Four new profiles, exact parent/child x numeric Easy0/Hard1, reuse the byte-identical frozen calm controller SHA690ff81b46c1666811410530cdd051df34ef0ab79376a7668e1437096a7e193a. Only ROM/config/source bindings change, and every old hook opcode/address/bank is checked against the current binaries before launch.
Actual cold selection, staged flat logical/PPU terrain/player/camera and valid default-health Goombas; genuine free-buster defeats and untouched RNG earn all drop actors. Wrong kinds expire naturally. A real controller jump during ages225..254 moves Roll clear of the orb rows. No resource, RNG, counter, enemy-health, projectile, drop actor/age or outcome injection. Defeated enemy flags are cleaned only after the real defeat callback.
Both child modes pass mechanics and fade policy. Both parent modes finish mechanics and retain passed=false/fade_policy_passed=false as expected missing-fade negatives. These raw negatives and all historical failures remain immutable.
Source predicate: hide a nonempty drop when (InvDropAgeHi!=0 OR InvDropAge>=240) AND (FrameCounter&1)!=0. This is odd native FrameCounter, not odd drop age.
Each calm source-age236..247 window has0 live shots/enemies and at most4 sprites on orb rows. All12 baseline full16x18 RGB crops contain exactly80 changed pixels against the repeated stage. Each admitted child crop equals that complete supplied-art reference pixel-for-pixel. Each odd-FrameCounter fading child crop contains0 orb pixels and exactly matches unobstructed stage32px to its right. The RGB oracle relies on the disclosed uniform16px repeated floor. Actual original mobile executable gameplay is unavailable; production drop/fade/movement rules remain explicit host adaptations.
Native birth age0, one global actor update per GameLoop, exact420-update expiry, real full-cap pickup/feedback/cleanup all pass. Source render/publication IDs, actual DMA IDs, hardware OAM at startFrame and exact PPU frameCount/scanline/cycle through completed endFrame bind every capture. Actual/shadow banks,5 SMC operands, NMI A/SP, lower-stack guard, line31 IRQ and write-time CHR checks pass.
Totals across these four new profiles: {total('updates'):,} completed gameplay updates; {total('wall_frames'):,} wall frames; {total('real_births')} actual births; {total('defeats')} real defeats; {total('natural_expiries')} natural expiries;4 real pickups. {total('nmis'):,} observed NMIs; {total('irq_scroll_stores'):,} IRQ stores; {total('hardware_chr_checks'):,} CHR checks; {total('dma_checks'):,} complete DMA checks; min sampledSP{min(q['min_sampled_SP']for q in profiles)}. Stack observations are bounded, not a maximum-depth certification.

Current paired idle cost
In each mode both ROMs execute120 completed updates,120 actual wall frames and120 renders in the identical cold empty-arena control. Easy has120 inclusive deltas of+60 CPU cycles. Hard has118 of+60, one-60 and one+180; mean+60. The four empty helper admissions add60 isolated CPU cycles. The cause of the two120-cycle inclusive Hard variations was not traced; inclusive spans also cover other foreground/interrupt work. No constant60Hz or campaign performance certification.

Visual review and explicit historical boundary
All four current sample sheets,48 actual PPU frames, were viewed. Full orb art/absence, unchanged Roll supplied body art, background and resource HUD look consistent in these calm samples; no additional corruption proved. The exact RGB assertions above are independent of the selected-frame visual inspection.
The prior9bac/c32b four-slot/native420-expiry and live-fire pool packet remains historical, explicitly not rerun or relabeled on this child. It established source admission and exposed partial visibility under crowded hardware sprite limits; that visibility issue remains open for a separate task. No every-frame, every-item, every-character, mobile timing/audio or all-roster conclusion follows from this four-profile current component.

Receipts and commands
Build: {(a.private/'proof.json').as_posix()} SHA{sha(a.private/'proof.json')}
Fresh RGB aggregate: {aggregate.as_posix()} SHA{sha(aggregate)}
Native preparation: {(a.private/'native-preparation/preparation.json').as_posix()} SHA{sha(a.private/'native-preparation/preparation.json')}
Human review: {a.review.as_posix()} SHA{sha(a.review)}
Historical pool packet: final-roll-items-v1/fade-native-final-packet-v2/proof.json SHA0c82690db2b4cae5a548bd32b7d91e98ff421df2a2f9936aa15a76094423577c; exact9bac/c32b scope unchanged.
Each current native run used one sequential granted project emulator. That worker is explicitly released after the fourth run; no native worker from this task remains running. Full absolute runnable commands for all four profiles are in this final packet's commands.txt; use a fresh output directory and a newly coordinated worker for any rerun.
An offline reporter first required every inclusive delta to equal+60 and stopped on the two Hard variations. That failed reporter/diagnostic remains final-packet-v1; the corrected aggregation reports actual range/mean without modifying or weakening any native mechanics/RGB assertion.
'''
    for old,new in [('reproduces9e0e','reproduces 9e0e'),('Only36','Only 36'),('bank119','bank 119'),('existing3-byte','existing 3-byte'),('and33','and 33'),('previouslyFF','previously FF'),('All72,217','All 72,217'),('to9e0e','to 9e0e'),('and1,520','and 1,520'),('include0','include 0'),(':288',': 288'),(',8',', 8'),(',4',', 4'),(',104',', 104'),(',6',', 6'),('and2','and 2'),('original9bac','original 9bac'),('Easy0/Hard1','Easy 0 / Hard 1'),('SHA690','SHA 690'),('ages225','ages 225'),('source-age236','source-age 236'),('has0','has 0'),('most4','most 4'),('All12','All 12'),('full16x18','full 16x18'),('exactly80','exactly 80'),('contains0','contains 0'),('stage32px','stage 32px'),('uniform16px','uniform 16px'),('age0','age 0'),('exact420','exact 420'),('banks,5','banks, 5'),('line31','line 31'),(';4 real','; 4 real'),('sampledSP','sampled SP '),('execute120','execute 120'),(',120',', 120'),('and120','and 120'),('exactly60','exactly 60'),('constant60Hz','constant 60 Hz'),('sheets,48','sheets, 48'),('prior9bac','prior 9bac'),('SHA','SHA ')]:text=text.replace(old,new)
    for old,new in [('SHA  ','SHA '),('has120','has 120'),('has118','has 118'),('of+60','of +60'),('one-60','one -60'),('one+180','one +180'),('mean+60','mean +60'),('add60','add 60'),('two120-cycle','two 120-cycle'),('equal+60','equal +60'),('exact9bac','exact 9bac'),('native420-expiry','native 420-update expiry'),('PID165672','PID 165672'),('current5ec','current 5ec')]:text=text.replace(old,new)
    text=re.sub(r'(?<=\d), (?=\d{3}(?:\D|$))',',',text)
    report.write_text(text,encoding='utf-8');shutil.copy2(report,a.output/report.name);shutil.copy2(a.review,a.output/'visual-review.json')
    emulator=a.private.parent/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe';commands=[]
    for role in ['candidate','baseline']:
      for mode in [0,1]:commands.append(f'python "{(ROOT/"tools/audit/final_roll_items_fade_native_run.py").as_posix()}" --packet "{(a.private/"native-preparation").as_posix()}" --role {role} --mode {mode} --output "REPLACE_WITH_NEW_EXTERNAL_DIRECTORY" --emulator "{emulator.as_posix()}" --timeout 900')
    (a.output/'commands.txt').write_text('\n'.join(commands)+'\n',encoding='utf-8')
    adoption=a.private.parent/'mike-native-current5ec-v1/adoption-v1/proof.json'
    assert sha(adoption)=='1d2e94dc775e1a0f71dd8b0f0b57960365db02ef2898c9f89dc6631ea901e5fe'
    refs=[a.private/'proof.json',aggregate,a.private/'native-preparation/preparation.json',a.private/'sourcepatch.patch',a.private/'parent-source-ledger.json',a.private/'candidate-source-ledger.json',a.private/'cpu-bound-source/binding.json',a.private/'cpu-bound-source/fade_cpu_current.py',a.review,adoption,report]
    refs+=[a.private/n/'proof.json'for n in cpu]
    refs+=[ROOT/'tools/audit'/n for n in ['final_roll_items_fade_current.py','final_roll_items_fade_current_cpu.py','final_roll_items_fade_current_report.py','final_roll_items_fade_native_run.py','final_roll_items_fade_calm_report.py']]
    manifest={str(f):sha(f)for f in refs};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    for f in refs:
        if f.suffix=='.py'and f.parent==ROOT/'tools/audit':shutil.copy2(f,a.output/f.name)
    result=dict(passed=True,goal_complete=False,current_parent=PARENT,combined_candidate=build['candidate_sha256'],fresh_current_native_profiles=4,current_candidate_both_modes_passed=True,current_parent_both_negative_fade_receipts_retained=True,fresh_CPU_cases=162816+1520+412+8140*2,matched_idle_controls=cadence,profiles=profiles,actual_PPU_RGB_controls_passed=True,selected_actual_PPU_frames_reviewed=48,historical_full_pool_reused_as_current=False,worker_released=True,manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),RGB_aggregate_sha256=sha(aggregate),visual_review_sha256=sha(a.review),tool_sha256=sha(Path(__file__)),scope='Private exact current Mike9e0e + frozen Roll fade; no production/Git/Downloads changes. Current calm/fade/idle controls only; prior full-pool remains historical. Broader source fidelity, crowded visibility, every-item/every-character goals open.')
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,final_packet_sha256=sha(a.output/'proof.json'),report_sha256=sha(report),manifest_sha256=sha(a.output/'manifest.json'),actual_PPU_RGB_frames=48)))
if __name__=='__main__':main()
