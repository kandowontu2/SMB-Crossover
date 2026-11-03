"""Retain finite public Mini and private Prince/DK work, with active handoff."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib,subprocess
import build_storage_guard_v1 as G
R=Path(__file__).resolve().parents[2]
O=R/'build/roster-resume-checkpoint-root-1103-v62'
C=R/'docs/qa/checkpoints/2026-11-03/roster-resume-v62'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def archive(name,files):
    files=sorted(set(files));dest=O/name
    assert len(files)<120
    with ZipFile(dest,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            assert p.is_file() and p.suffix.lower() not in ['.nes','.dbg','.o','.exe'],p
            z.write(p,p.relative_to(R).as_posix())
    return dict(archive=name,bytes=dest.stat().st_size,SHA256=sha(dest),members={p.relative_to(R).as_posix():sha(p) for p in files})

def packet(root,extra=()):
    return [root/p for p in ['ready.json','controller.lua','run.py','capture/result.json','capture/binding.json',*extra]]

def main():
    G.preflight(private_root=O,reserved_bytes=6_000_000,reserved_files=10,fresh=True)
    assert not C.exists();O.mkdir(exist_ok=False)
    power=R/'build/mini-mario-power-contract-1103-v51'
    delivery=R/'build/mini-power-delivery-root-1103-v61'
    d=read(delivery/'verified-delivery.json');pin=d['ROM_SHA256']
    assert d['Downloads_launch_verified'] and d['IPS_roundtrip'] and sha(Path(d['destination']))==pin
    f=read(R/'build/mini-power-regression-root-1103-v60/full49/capture/result.json')
    assert f['passed'] and f['full_stage'] and f['ROM_sha256']==pin
    release=json.loads(subprocess.check_output(['gh','api','repos/kandowontu2/SMB-Crossover/releases/latest'],text=True))
    assert release['tag_name']=='Current' and len(release['assets'])==1
    assert release['assets'][0]['digest']=='sha256:'+d['IPS_SHA256']
    manifest=read(power/'mini-native-power-v59.json')
    root_sources=[R/'tools/audit'/name for name in [
        'compose_mini_power_root_1103_v56.py','qualify_mini_power_cold_root_1103_v58.py',
        'prepare_mini_power_regression_root_1103_v60.py','deliver_mini_power_root_1103_v61.py',Path(__file__).name]]
    mini=[power/'mini-native-power-v59.json',power/'mini-native-power-v59.zip',*root_sources,
        *[R/n for n in manifest['git_source_files']],R/'build/mini-power-candidate-root-1103-v56/candidate.json',
        R/'build/mini-power-cold-root-1103-v58/receipt.json',delivery/'verified-delivery.json',
        delivery/'SMB-Crossover-Latest-WIP-MMC5.ips',delivery/'release-notes.txt']
    mini+=packet(power/'earned-mushroom58',['capture/mini-earned-mushroom.png'])
    mini+=packet(delivery/'downloads-smoke')
    mini+=packet(R/'build/mini-power-regression-root-1103-v60/full49',['capture/mini-active-1-2.png'])
    mini_archive=archive('mini-public.zip',mini)
    body=R/'build/prince-pose-reservation-1103-v185';stage=read(body/'source-stage.json')
    prince=[body/'source-stage.json',*[R/n for n in stage['bindings']],
        R/'build/prince-body-current-candidate-root-1103-v186/candidate.json']
    # Only new source inputs and retained compact payloads; do not expand a
    # historical dependency tree or copy an original game/ROM/debug bundle.
    prince=[p for p in prince if p.is_relative_to(body) or p.is_relative_to(R/'tools/audit') or p.name=='candidate.json']
    prince+=[R/'tools/audit'/n for n in ['compose_prince_body_current_root_1103_v186.py',
        'prepare_prince_current_body_root_1103_v185.py','prepare_prince_idle_jump_root_1103_v188.py',
        'prepare_prince_source_hop_root_1103_v189.py','prepare_prince_first_pipe_1103_v189.py','prepare_prince_first_pipe_1103_v193.py']]
    for name in ['prince-body-current-native-root-1103-v187','prince-source-hop-root-1103-v189']:
        prince+=packet(R/'build'/name,['capture/prince-diagnostic.json'])
    prince+=[R/'build/prince-body-current-native-root-1103-v187/capture/prince-after-draw-DMA.png']
    for number in [189,193]:
        p=R/f'build/prince-first-pipe-1103-v{number}/native'
        # These terminal negative runs intentionally lack result.json.
        prince+=[p/n for n in ['ready.json','controller.lua','run.py','capture/binding.json','capture/prince-diagnostic.json','capture/source-phases.csv']]
    prince+=[R/'build/prince-control-recipe-1103-v190'/n for n in ['control-recipe.json','run-jump.json']]
    prince_archive=archive('prince-private.zip',prince)
    dk=R/'build/dkjr-menu-ca90-1103-v11'
    dk_archive=archive('dkjr-study.zip',[p for p in dk.iterdir() if p.is_file()]+[R/'tools/audit'/n for n in ['assess_dkjr_menu_current_1103_v11.py','measure_dkjr_menu_glue_1103_v12.py']])
    receipt=dict(passed=True,goal_complete=False,goal_status='active',installed_ROM_SHA256=pin,
        IPS_SHA256=d['IPS_SHA256'],Downloads_verified=True,Latest_release_digest_verified=True,backup_created=False,
        Mini=dict(earned_mushroom=True,full_nonshortcut_1_1=True,active_1_2=True,physical_frames=f['physical_frames'],lives=[2,2],helpers_added=False,
            remaining='Original30/35 transition timing/type-specific target rules, ChangeSize clips, fireballs, other source abilities/audio/performance.'),
        Prince=dict(publicly_playable=False,private_SHA256='199d89a4a1c7747946154b5f6c5b079f90b9292aff0831a49cbb4303a130820a',
            body_DMA_menu_movement_and_original_standing_hop=True,first_pipe=False,
            remaining='Ordinary native side-floor snag confirmed; source-funded filter in progress. Original unarmed defender contact is fatal; first enemy stops routes189/193. Easy stomp/native source bounce bridge unqualified. Rebase any later private candidate over delivered9d291, preserving Mini5115.'),
        DK_Jr=dict(publicly_playable=False,reason='Current Mini menu occupies old proposal. Independent164B adapter; verified source factoring leaves7B. More legal source funding needed; no admission.'),
        archives=[mini_archive,prince_archive,dk_archive])
    (O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    C.mkdir(parents=True)
    for name in ['mini-public.zip','prince-private.zip','dkjr-study.zip','receipt.json']:(C/name).write_bytes((O/name).read_bytes())
    hpath=R/'docs/qa/continuation-current.json';h=read(hpath)
    h['goal_status']='ACTIVE_INCOMPLETE'
    h['installed_nightly'].update(ROM_sha256=pin,IPS_SHA256=d['IPS_SHA256'],checkpoint=C.relative_to(R).as_posix(),verification_scope=d['verification_scope'])
    m=h['mini_mario_priority_1103'];m.update(status='DELIVERED_EARNED_MUSHROOM_FULL11_ACTIVE',checkpoint=C.relative_to(R).as_posix(),root_queue='FREE after Mini actual Downloads pickup/full1-1 verification. Root owns queue; Prince/DK source followup continues.')
    m['remaining']=[receipt['Mini']['remaining'],receipt['Prince']['remaining'],receipt['DK_Jr']['reason'],'All original full-roster stage/powerup/Kirby audit requirements remain open.']
    h['roster_resume_1103_v62']=dict(checkpoint=C.relative_to(R).as_posix(),Prince=receipt['Prince'],DK_Jr=receipt['DK_Jr'])
    hpath.write_text(json.dumps(h,indent=2)+'\n')
    print(json.dumps(dict(passed=True,checkpoint=str(C),archives=[{k:v for k,v in q.items()if k!='members'}for q in receipt['archives']],storage=G.preflight(fresh=True))))

if __name__=='__main__':main()
