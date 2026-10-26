"""Qualify immutable Parodius death records and actual compiled owner paths.

Source/isolated-CPU evidence only. Never runs Mesen or changes game source.
The original native failures did not log the missing pointer; CPU reproduction
below must not be represented as recovery of that unrecorded native state.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, sys
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = '5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'
BASE = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def module(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def invoke(q, name):
    """Execute unchanged linked code; only observe entry/owner/record events."""
    b = q.b; at = location(b, name); pc = address(b, name)
    window = (pc-0x8000)//8192; q.m.page(window, (at-16)//8192)
    if window in (1, 2): q.set('CurrentBank' if window == 1 else 'CurrentBankC', q.m.banks[window] | 128)
    c = NesMPU(memory=q.m, pc=pc); c.p=0x30; c.sp=0xfd; c.stPushWord(0x5aff)
    q.m.writes=[]; rows=[]; owner=None
    names = ['VvGraphics', 'PnDeathGraphics', 'PnGraphics', 'DrawMetasprite', 'MetaspriteRenderLoop', 'PnDeathDraw']
    hooks = {(address(b,n), (location(b,n)-16)//8192):n for n in names}
    for _ in range(100000):
        if c.pc == 0x5b00: break
        physical=q.m.banks[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
        label=hooks.get((c.pc, physical))
        if label:
            if label=='DrawMetasprite': owner=c.y
            row=dict(entry=label, PC=c.pc, bank=physical, SP=c.sp, owner=owner)
            if label=='MetaspriteRenderLoop':
                ptr=q.get('R0')+256*q.get('R1'); bank=q.m.banks[(ptr-0x8000)//8192]
                row.update(pointer=ptr, record_bank=bank, key=f'{bank}:{ptr}', bytes=list(q.m[ptr:ptr+q.m[ptr]+1]),
                           origin=[q.get(n)for n in ['R4','R5','R6','R7']], attribute=q.get('R3'))
            rows.append(row)
        c.step()
    else: raise AssertionError(('Unbounded source CPU',name,hex(c.pc),q.m.banks))
    assert c.sp==0xfd
    return dict(events=rows, cycles=c.processorCycles, SP=c.sp, banks=q.m.banks[:],
                OAM_writes=sum(0x200<=p<0x300 for p,v in q.m.writes))


def setup(b, variant, mode=0):
    q=Arena(b,18)
    q.put(VvVariant=variant,CrossoverBehaviorVersion=mode,VvInitialized=0x76,VvLife=2,VvAlive=1,
          PnInitialized=0x50,NumberofLives=2,OperMode_Task=3,DisableScreenFlag=0,
          InvHudActive=3,InvHudPhysical=140,X5HudChrUpper=0x85)
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['candidate','baseline','source','live-aliases','output']: p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=False)
    assert sha(a.candidate)==EXPECTED and sha(a.baseline)==BASE
    sys.path.insert(0,str(ROOT/'tools/reference'))
    art=module(ROOT/'tools/reference/export_parodius_art.py','death_source_art')
    raw,cpu=art.native.source_cpu(); native=art.records(raw); animations=art.native.native_animations(cpu)
    b=scoped_load(a.candidate); baseline=a.baseline.read_bytes()
    manifest=json.loads((a.source/'reference/parodius-nes/art/packed/manifest.json').read_text())
    live=json.loads(a.live_aliases.read_text())['body_sources']; assert len(live)==131
    prg_bytes=b['raw'][4]*16384; chr_start=16+prg_bytes
    assert prg_bytes==1048576 and baseline[:16]==b['raw'][:16]
    death={}; asset_rows=[]; selected=[]; chronological=[]; draws=[]; hidden=[]
    palettes={1:[0x30,0x15,0x08],2:[0x30,0x28,0x06],3:[0x21,0x03,0x06]}
    try:
        for v,page in enumerate([892,956,1020],1):
            anim=cpu.memory[0x932e+v]; frames=sorted(set(animations[anim]['data'][:-1:2])); pool=[]
            detail=manifest['death']['variants'][str(v)]
            assert detail['frames']==frames and detail['animation']==anim and detail['source_animation_data']==animations[anim]['data']
            mapping={c:(0,i+1)for i,c in enumerate(palettes[v])}
            if v==3:mapping.update({0x30:(2,2),0x28:(2,3)})
            for f in frames:
                parts=[]
                for part in native[f]['parts']:
                    pixels=art.pixels(raw[131088:],part['tile'],[10,4,11,5,0,0,0,0])
                    colors=art.PALETTES[1 if v==2 else part['attr']&3]
                    for plane in sorted({mapping[colors[x]][0]for row in pixels for x in row if x}):
                        layer=[[mapping[colors[x]][1]if x and mapping[colors[x]][0]==plane else 0 for x in row]for row in pixels]
                        tile=bytes(sum(((layer[y+8*k][x]>>bit)&1)<<(7-x)for x in range(8))for k in range(2)for bit in range(2)for y in range(8))
                        if tile not in pool:pool.append(tile)
                        parts.append([pool.index(tile)*2,(part['attr']&0xc0)|plane,(part['dy']+8)&255,(part['dx']+8)&255])
                assert detail['records'][str(f)]==parts
                name='PnDeathPose'+str(f); at=location(b,name); ptr=address(b,name); bank=(at-16)//8192
                data=bytes([len(parts)*4]+[x for part in parts for x in part]);key=f'{bank}:{ptr}'
                assert b['raw'][at:at+len(data)]==baseline[at:at+len(data)]==data
                assert key not in live and bank==76
                death[key]=dict(label=name,bank=bank,pointer=ptr,variant=v,frame=f,parts=parts,bytes=list(data),
                                body_family='native-death',skin=10,group=0,animation=anim,physical_chr=page)
                asset_rows.append(dict(variant=v,frame=f,label=name,key=key,source_record=native[f],compiled_bytes=list(data),
                                       compiled_and_manifest_and_regenerated_original_equal=True,unchanged_from50b5=True))
            generated=b''.join(pool).ljust(1024,b'\0');at=chr_start+page*1024
            assert len(generated)==1024 and b['raw'][at:at+1024]==baseline[at:at+1024]==generated
            selected.append(dict(variant=v,physical_chr=page,CHR_sha256=hashlib.sha256(generated).hexdigest(),pairs=len(pool),frames=frames))
        assert len(death)==13 and len({(r['bank'],r['pointer'])for r in death.values()})==13
        for mode in [0,1]:
            for v in [1,2,3]:
                q=setup(b,v,mode); q.invoke('KillPlayer')
                assert q.get('MmDeathFlag')==1 and q.get('PnSkin')==10 and q.get('GameEngineSubroutine')==11
                states=[]
                for tick in range(120):
                    g=invoke(q,'VvGraphics'); ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1)
                    key=f'{q.m.banks[2]}:{ptr}'; record=death.get(key)
                    assert record and record['variant']==v and record['frame']==q.get('PnFrame')
                    assert [r['entry']for r in g['events']][:2]==['VvGraphics','PnDeathGraphics']
                    assert q.get('SmChrBank')==[124,188,252][v-1] and q.get('ObjectMetasprite')==233
                    states.append(dict(tick=tick,frame=q.get('PnFrame'),animation=q.get('PnAnimation'),key=key,
                                       game_engine=q.get('GameEngineSubroutine'),skin=q.get('PnSkin')))
                    q.invoke('VvDeathUpdate')
                assert q.get('GameEngineSubroutine')==6 and q.get('VvDeathAge')==120
                chronological.append(dict(mode=mode,variant=v,states=states,original_live_map_rejects_every_death_key=True,
                                          final_engine=6,source_only=True))
        for key,record in death.items():
            for face in [1,2]:
                for xpos in [0,96,248]:
                    q=setup(b,record['variant']);q.invoke('KillPlayer')
                    q.put(PnFrame=record['frame'],PlayerFacingDir=face,Player_X_Position=xpos,Player_PageLoc=1,
                          ScreenLeft_PageLoc=1,ScreenLeft_X_Pos=0)
                    invoke(q,'VvGraphics');d=invoke(q,'DrawAllMetasprites')
                    emitted=[e for e in d['events']if e['entry']=='MetaspriteRenderLoop' and e['owner']==0]
                    assert len(emitted)==1 and emitted[0]['key']==key and emitted[0]['bytes']==record['bytes']
                    assert any(e['entry']=='PnDeathDraw'for e in d['events'])
                    # Foreground publishes the existing CHR shadows; hardware
                    # publication belongs to later NMI BankSwitchCHR, not this call.
                    assert q.get('CurrentCHRBank')==record['physical_chr']%256
                    assert q.get('X5ChrMode')==0x83 and q.get('X5WideChrActive')==1 and q.get('ReloadCHRBank')!=0
                    draws.append(dict(variant=record['variant'],frame=record['frame'],face=face,x=xpos,key=key,**d))
        for v in [1,2,3]:
            frames=manifest['death']['variants'][str(v)]['frames']
            for f in [(frames[0]-1)&255,(frames[-1]+1)&255]:
                q=setup(b,v);q.invoke('KillPlayer');q.set('PnFrame',f);g=invoke(q,'VvGraphics')
                assert q.get('ObjectMetasprite')==0
                hidden.append(dict(variant=v,frame=f,ObjectMetasprite=0,source_only_invalid_frame_control=True))
    except Exception as ex:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(ex),assets=len(asset_rows),chronologies=len(chronological),draws=draws,hidden=hidden),indent=2)+'\n');raise
    for name,data in [('death-sources',death),('assets',asset_rows),('CHR',selected),('chronologies',chronological),('draws',draws),('hidden',hidden)]:
        (a.output/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    bindings=[Path(__file__),a.candidate,a.candidate.with_suffix('.dbg'),a.candidate.with_suffix('.lbl'),a.baseline,a.live_aliases,
              art.native.SOURCE,ROOT/'tools/reference/prepare_parodius_death.py',ROOT/'tools/reference/export_parodius_art.py',
              ROOT/'tools/reference/build_parodius_native.py',ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',
              ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/verify_native_relocation.py']
    bindings += [a.source/'src'/n for n in ['parodius_death.s','parodius_death_art.inc','vic_render.s','vic_adapter.s','metasprite_engine.s','parodius_render.s']]
    bindings += [a.source/'reference/parodius-nes/art/packed/manifest.json',a.source/'chr/characters/parodius.chr']
    ledger={str(f.resolve()):sha(f)for f in bindings}
    (a.output/'manifest.json').write_text(json.dumps(ledger,indent=2)+'\n')
    proof=dict(passed=True,native_run=False,ROM_sha256=EXPECTED,baseline_sha256=BASE,original_ROM_sha256=art.native.SHA,
               death_records=13,live_records_retained=131,death_keys_disjoint_from_live=True,compiled_death_draws=len(draws),
               compiled_death_update_chronologies=len(chronological),compiled_death_updates=720,hidden_controls=len(hidden),
               immutable_record_and_CHR_regeneration=True,all_death_data_unchanged_from50b5=True,
               missing_native_pointer_recovered=False,observer_changed=False,
               adaptation='Octopus/Twinbee original indexed colors preserved. Pentarou original yellow28 uses declared shared-world yellow27; other four colors preserved. Existing +8 coordinates/record splitting retained.',
               limits='Isolated explicit CPU initialization and frame/position/facing controls; no natural reachability, PPU/DMA timing, eight-sprite visibility, actual death/new-life image or native pass. Original native guard failures stay false.',
               files={f.name:sha(f)for f in a.output.glob('*.json')})
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n'); print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
