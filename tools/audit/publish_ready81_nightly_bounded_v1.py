"""Qualify exact six-wrestler results, freeze compact evidence and deliver nightly."""
from pathlib import Path
import csv,hashlib,json,os,zipfile
R=Path(__file__).resolve().parents[2]
J=R/'build/wwf-roster-native-1101-v1';N=R/'build/wwf-final-native-1101-v1'
O=R/'build/nightly-ready81-1101-v1';K=R/'docs/qa/checkpoints/2026-11-01/ready81-wwf-native-v1'
DEST=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
EXPECTED='429b9f3c3fb551ec023d997f9e83515a2c68f1447a2d4a7cad43c029ff5ee3e2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')


def bound(p,ignore_self=False):
    q=json.loads(p.read_text())
    for f,h in q['bindings'].items():
        # An iterative, unqualified linker receipt included its previous log.
        # The final immutable source stage below binds the actual log once.
        if ignore_self and Path(f).resolve()==p.resolve():continue
        assert sha(f)==h,f
    return q


def archive(p,paths):
    paths={x.resolve()for x in paths};assert len(paths)<256 and sum(x.stat().st_size for x in paths)<20_000_000
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for f in sorted(paths):z.write(f,str(f.relative_to(R)).replace('\\','/'))
    return dict(path=str(p.relative_to(R)),sha256=sha(p),bytes=p.stat().st_size,members=len(paths))


def native(p):
    ready=bound(p/'ready.json');q=json.loads((p/'capture/result.json').read_text());bind=json.loads((p/'capture/binding.json').read_text())
    assert q['passed'] and ready['ROM_sha256']==q['ROM_sha256']==bind['ROM_sha256']==EXPECTED
    assert bind['exit_code']==0 and bind['ready_sha256']==sha(p/'ready.json')
    return q


def main():
    assert not O.exists() and not K.exists() and not(J/'source-stage.json').exists()
    assert sha(J/'candidate.nes')==EXPECTED
    assembly=bound(J/'assembly-stage.json',ignore_self=True)
    controls=bound(R/'build/wwf-roster-join-controls-1101-v1/controls.json')
    music=bound(R/'build/wwf-buffered-music-1101-v1/controls.json')
    assert controls['passed'] and controls['candidate']==music['candidate']==EXPECTED and music['passed']
    assert controls['checks']['playable']==81 and controls['checks']['Start_A_cases']==688 and controls['checks']['compiled_pose_cases']==688
    names=['hogan','dibiase','bigelow','honky','savage','andre'];runs={n:native(N/n)for n in names};menu=native(N/'menu')
    for i,n in enumerate(names):
        q=runs[n];assert q['variant']==i and q['counters']['defeat']>0 and q['maximum_camera']>=257
        assert q['jumped'] and q['landed'] and q['counters']['movement']==q['counters']['source']
        assert q['APU_writes']>1000 and q['MMC5_SFX_writes']>4 and all(x in q['body_DMA']for x in ['selected','lives','game'])
    assert menu['heading_errors']==menu['visible_mask_writes']==0 and len(menu['transitions'])==120
    frames=list(csv.DictReader((N/'menu/capture/frames.csv').open()))
    assert len(frames)==2400 and len({q['header_hash']for q in frames})==1
    O.mkdir();K.mkdir(parents=True)
    dependencies={f:h for f,h in assembly['bindings'].items()if Path(f).resolve()!=(J/'assembly-stage.json').resolve()}
    dependencies[str(J/'assembly-stage.json')]=sha(J/'assembly-stage.json')
    dependencies[str(Path(__file__).resolve())]=sha(__file__)
    save(J/'source-stage.json',dict(passed=True,source=True,native=True,installed=False,candidate=EXPECTED,private_playable=81,parent=assembly['parent'],bindings=dependencies,
        scope='All six wrestler opening routes and complete 86-identity menu timing; full1-1, shortcuts, upgrades, advanced wrestling and steady60Hz remain unqualified.'))
    source={p for p in J.rglob('*')if p.is_file()and p.suffix in ['.s','.cfg','.dep','.json','.bin','.chr']and 'sideoutputs'not in p.parts}
    source|={p for p in (R/'build/wwf-hogan-natural-source-v15/joint').iterdir()if p.is_file()and p.suffix in ['.s','.inc']}
    source|={R/'tools/audit'/n for n in ['join_wwf_roster_bounded_v1.py','check_wwf_roster_join_bounded_v1.py','check_wwf_buffered_music_bounded_v1.py','prepare_wwf_roster_native_bounded_v1.py','prepare_wwf_menu_native_bounded_v1.py','run_wwf_roster_suite_bounded_v1.py','publish_ready81_nightly_bounded_v1.py']}
    source|={R/'tools/reference'/n for n in ['wwf_roster_native_support_v1.s','wwf_roster_cold_v1.s','wwf_roster_workers_v1.s','wwf_roster_pose_decoder_v1.s']}
    src=archive(K/'source.zip',source)
    files={R/'build/wwf-roster-join-controls-1101-v1/controls.json',R/'build/wwf-buffered-music-1101-v1/controls.json',N/'suite-results.json'}
    for name in [*names,'menu']:
        root=N/name;files|={root/n for n in ['ready.json','run.py','controller.lua']}
        files|={p for p in(root/'capture').iterdir()if p.is_file()and p.suffix in ['.json','.csv','.png','.log']}
    proof=archive(K/'native-results.zip',files)
    summary=dict(complete=False,ROM_sha256=EXPECTED,playable=81,total_identities=86,source=src,native=proof,
        menu=dict(transitions=120,transition_frames=2400,heading_errors=0,visible_mask_writes=0),
        source_controls=controls['checks'],music=music['rows'],
        wrestlers={n:dict(Main=q['main_updates'],frames=q['frames'],defeats=q['counters']['defeat'],maximum_camera=q['maximum_camera'],vector_returns=q['counters']['vectors'],APU_writes=q['APU_writes'],MMC5_SFX_writes=q['MMC5_SFX_writes'])for n,q in runs.items()},
        limits=['Opening routes only; full1-1, shortcuts and all powerups remain required','Basic WWF movement/jump/poses/punches/kicks; advanced wrestling and authentic endurance/upgrades remain incomplete','Six original themes and buffered register parity; no acoustic quality or constant60Hz claim','Remaining five menu identities and other goal characters/campaigns remain unfinished','Source archive is reviewed grafts and recipes, not the canonical prepared37-identity builder'])
    save(K/'handoff.json',summary)
    (K/'README.md').write_text('''# 81-character WWF nightly

The WWF slot now cycles Hogan, Ted DiBiase, Bam Bam Bigelow, Honky Tonk Man,
Randy Savage and Andre the Giant with Select. Each uses original poses,
palettes, actor routines and theme data from WWF WrestleMania. Native SMB
terrain, jump input and enemy proxies connect them to this platform game.

The exact ROM passes six cold controller routes: selection, lives, idle,
jump/landing, source punch defeating a Goomba and camera advancement across
a page. All six have displayed sprite/OAM/CHR observations, native vector
register/SMC checks and APU/shared-SFX activity. CPU tests cover688 Start/A
cases,688 linked pose/fallback cases, all16 cookie-byte rejection cases per
wrestler and600 original-versus-buffered audio ticks for each theme.

The complete menu sweep covers120 D-pad/Select transitions and2400 physical
transition frames, with no changed heading pixels or visible PPUMASK writes.

The integration fixes a17-part pose buffer overflow, per-variant cookie loop,
zero-valued palette bytes, software bank ownership after audio, and source
music initialization/channel enabling. No global/ZP allocation or ROM-size
increase was needed. Thomas's selected kernel and native import addresses
are unchanged; unused ROM tails and WWF-owned CHR pages fund the addition.

These checks do not clear full1-1, shortcuts, all upgrades, advanced wrestling,
the complete roster/campaign goal, audio listening quality or steady60Hz.
`source.zip` contains reviewed source grafts and link recipes. Existing frozen
inputs are reused; this does not replace the prepared37-identity builder.
`native-results.zip` contains bounded controllers, compact receipts and at
most four PNGs per run. No video or frame-image sequence was created.
''',encoding='utf-8')
    before=sha(DEST);temporary=DEST.with_name(DEST.name+'.publishing');assert not temporary.exists()
    temporary.write_bytes((J/'candidate.nes').read_bytes());assert sha(temporary)==EXPECTED
    os.replace(temporary,DEST);assert sha(DEST)==EXPECTED
    receipt=dict(installed=True,backup_created=False,destination=str(DEST),output_sha256=EXPECTED,replaced_sha256=before,playable_identities=81,new_identities=names[1:],checkpoint=str(K.relative_to(R)),checkpoint_sha256=sha(K/'handoff.json'),verification=summary)
    save(O/'installed.json',receipt);save(R/'docs/qa/nightly-2026-11-01-ready81.json',receipt)
    path=R/'docs/qa/continuation-current.json';handoff=json.loads(path.read_text());handoff.update(previous_goal_turn_classification='progress',goal_status='ACTIVE_INCOMPLETE',current_priority='Deliver verified81-identity WWF nightly; continue remaining five menu admissions and original full-roster/full1-1/every-powerup objective. Do not classify complete.',installed_nightly=receipt,combined81=summary)
    handoff['WWF_roster_source_next']['installed']=True
    handoff['completion']='Not complete. Five current menu identities, other goal characters, full1-1/shortcut/every-upgrade and campaigns remain.'
    save(path,handoff)
    readme=R/'README.md';text=readme.read_text()
    text=text.replace('**76 playable identities**','**81 playable identities**').replace('**10 individual identities**','**5 individual identities**').replace('**76-playable development nightly**','**81-playable development nightly**')
    text=text.replace('| WWF WrestleMania | Hulk Hogan | Ted DiBiase / Bam Bam Bigelow / Honky Tonk Man / Randy Savage / Andre the Giant |','| WWF WrestleMania | Hulk Hogan / Ted DiBiase / Bam Bam Bigelow / Honky Tonk Man / Randy Savage / Andre the Giant | — |')
    old='**Hulk Hogan** is playable in the WWF slot. His original movement, poses and punches are integrated with SMB terrain and enemies. A cold Mesen run verifies selection, lives, jumping, landing, a punch that defeats a Goomba, and scrolling across a page boundary. Full stages, advanced wrestling, original audio and upgrades remain unfinished.'
    new='**All six WWF wrestlers** are playable. Select cycles **Hogan → DiBiase → Bigelow → Honky Tonk Man → Savage → Andre**. Their original actor routines, poses, palettes and themes are integrated with SMB terrain and enemies. A jumps; B punches; Down+B kicks, and Up+B retains the original directional attack. Every wrestler passes a cold Mesen opening route through selection, lives, jump/landing, a Goomba defeat and scrolling across a page. Full stages, advanced wrestling, authentic endurance/upgrades and steady performance remain unfinished. See the [81-character verification](docs/qa/checkpoints/2026-11-01/ready81-wwf-native-v1/README.md).'
    assert old in text;text=text.replace(old,new)
    text=text.replace('SMB2J and All Night Nippon campaigns, the original Doki Doki Panic characters, Thomas and the WWF roster are still being developed. Their private source checkpoints do not add playable identities or campaigns to this build.','SMB2J and All Night Nippon campaigns and the original Doki Doki Panic characters are still being developed. Their private source checkpoints do not add playable identities or campaigns to this build.')
    readme.write_text(text,encoding='utf-8',newline='\n')
    print(json.dumps(dict(installed=True,path=str(DEST),ROM=EXPECTED,playable=81,backup=False,checkpoint=str(K))))


if __name__=='__main__':main()
