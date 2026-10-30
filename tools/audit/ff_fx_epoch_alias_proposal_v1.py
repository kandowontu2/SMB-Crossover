"""Read-only current-producer/consumer closure for proposed FF epoch aliases.

No new runtime state is installed. Current real lifecycle and alternating-player
consumers run against the frozen marker predecessor; saved fixtures are explicit.
"""
from pathlib import Path
import collections,itertools,json,re,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_fx_palette_lifecycle_controls_v5 as L
from check_tmnt_render_oa import address,location
H,M,T,Q,V=L.H,L.M,L.T,L.Q,L.V
P=R/'build/ff-fx-world-marker-proposal-v2';H.O=P/'joint'
O=R/'build/ff-fx-epoch-alias-proposal-v1'
FIELDS=['SmFreezePalettePacket','SmFreezePalettePending','SmFreezeLastBlue',
        'SmFreezeTurn','SmFreezeRenderState','SmFreezePaletteControl','FfPaletteAck']

def debug_rows(path):
    out=collections.defaultdict(list)
    for line in path.read_text().splitlines():
        if '\t' not in line:continue
        typ,body=line.split('\t',1)
        if typ in ['file','line','span','seg']:
            out[typ].append(dict(re.findall(r'(\w+)=("[^"]*"|[^,]+)',body)))
    return out

def references(b):
    d=debug_rows(P/'joint/candidate.dbg');spans={s['id']:s for s in d['span']};segs={s['id']:s for s in d['seg']}
    lines=collections.defaultdict(list)
    for l in d['line']:
        for sid in l.get('span','').split('+'):
            if sid in spans:
                s=spans[sid];g=segs[s['seg']]
                lines[(l['file'],int(l['line']))].append(dict(segment=g['name'].strip('"'),
                    address=int(g['start'],0)+int(s['start'],0),bytes=int(s['size'],0),
                    ROM_offset=int(g.get('ooffs','0'),0)+int(s['start'],0)))
    refs={n:[]for n in FIELDS};used=set()
    for f in d['file']:
        path=Path(f['name'].strip('"'))
        if path.suffix.lower()not in['.s','.inc']or not path.is_file():continue
        for line,text in enumerate(path.read_text(errors='replace').splitlines(),1):
            for name in FIELDS:
                if re.search(r'\b'+name+r'\b',text):
                    refs[name].append(dict(path=str(path.resolve()),line=line,text=text.strip(),
                        actual_emitted_spans=lines.get((f['id'],line),[])))
                    used.add(path)
    return refs,used

def transpose(b):
    rows=[]
    for current,p in itertools.product([0,1],[0x30,0x71]):
        m=M.setup(b);L.put_owner(m,owner=0x85,pending=0x80)
        H.put(m,SmFreezeTurn=4,NumberOfPlayers=1,CurrentPlayer=current,OffScr_NumberofLives=2)
        old={n:list(m[address(b,n):address(b,n)+(7 if n=='SmFreezePalettePacket'else 1)])for n in FIELDS}
        selected=H.get(m,'SelectedCharacter');m.writes.clear()
        c,low=H.invoke(m,'TransposePlayers',p=p)
        assert H.get(m,'CurrentPlayer')==current^1 and not c.p&1
        assert H.get(m,'SelectedCharacter')==selected==22
        assert all(list(m[address(b,n):address(b,n)+len(v)])==v for n,v in old.items())
        # Actual next scene reconstructs display resource state, without a
        # second per-player palette context or lost earned class/power state.
        H.put(m,Mirror_PPUMASK=0,DisableScreenFlag=1,NmiDisable=255,ScreenRoutineTask=0)
        m.writes.clear();H.invoke(m,'InitScreen')
        assert H.get(m,'SmFreezeTurn')==0 and H.get(m,'SmFreezeLastBlue')==128
        assert H.get(m,'SmFreezePalettePending')==192 and H.get(m,'SmFreezeRenderState')==0
        rows.append(dict(prior_player=current,flags=p,selected_shared=selected,
            real_transpose_does_not_touch_aliases=True,next_real_scene_reinitializes_aliases=True,minimum_SP=low))
    return rows

def inventory(b):
    m=M.setup(b)
    for name in FIELDS:
        for i in range(7 if name=='SmFreezePalettePacket'else 1):m[address(b,name)+i]=0xa5
    H.invoke(m,'InventoryInit')
    names=[n for n in FIELDS if n!='FfPaletteAck']
    assert all(all(m[address(b,n)+i]==0 for i in range(7 if n=='SmFreezePalettePacket'else 1))for n in names)
    return dict(genuine_InventoryInit_SamusFreezeInit_clears_all_mailbox_and_owner_fields=True,
        FfPaletteAck_not_aliased_or_modified_by_proposal=True)

def palette_publishers(b):
    rows=[]
    for name in ['WaterPaletteData','GroundPaletteData','UndergroundPaletteData','CastlePaletteData',
                 'BowserPaletteData','DaySnowPaletteData','NightSnowPaletteData','MushroomPaletteData']:
        at=location(b,name);raw=b['raw'];p=at;writes=[]
        while raw[p]:
            dest=raw[p]*256+raw[p+1];count=raw[p+2];assert not count&0xc0
            for j,value in enumerate(raw[p+3:p+3+count]):writes.append((dest+j,value))
            p+=3+count
        p1={a:v for a,v in writes if 0x3f15<=a<=0x3f17}
        rows.append(dict(name=name,actual_ROM_bytes=list(raw[at:p+1]),P1_writes=p1))
    assert [list(r['P1_writes'].values())for r in rows[:5]]==[
        [0x10,0x30,0x27],[0x1a,0x30,0x27],[0x1c,0x36,0x17],[0x1c,0x36,0x17],[0x1a,0x30,0x27]]
    assert all(not r['P1_writes']for r in rows[5:])
    return rows

def main():
    O.mkdir(exist_ok=False);p=dict(passed=False,proposal_only=True,aliases_installed=False,native=False,admitted=False)
    files={Path(__file__),Path(L.__file__),Path(M.__file__),Path(H.__file__),Path(T.__file__),
        P/'handoff.json',P/'source-closure.json',P/'joint/candidate.nes',P/'joint/candidate.dbg',
        R/'build/ff-fx-palette-lifecycle-v8/handoff.json',R/'build/ff-fx-epoch-oracle-v3/controls.json',
        R/'docs/qa/checkpoints/2026-10-30/ff-source-epoch-reservations/receipt.json'}
    try:
        closure=json.loads((P/'source-closure.json').read_text())
        for path,sha in closure['bindings'].items():assert L.sha(path)==sha,path
        b=H.C.qualified(P/'joint/candidate.nes');refs,used=references(b);files|=used
        p.update(addresses={n:address(b,n)for n in FIELDS},all_current_DBG_source_references=refs,
            runtime_aliases_requested={
                'SmFreezeTurn':'Existing SRAM byte: next family cursor0..5. Advance only after completed native DrawAll; initialize0 in existing actual Scene/Inventory/Retire.',
                'SmFreezeLastBlue':'Existing SRAM byte:80|last completed family0..5. Highbit remains FF validity; publish after packet/OAM and before final Pending80. Native Samus writes only0/1.',
                'SmFreezePalettePacket':'Existing7B BSS packet [3F,15,3,c1,c2,c3,0], exact original NMI consumer.',
                'SmFreezePalettePending':'Existing BSS byte: clear FIRST while rebuilding;80 complete active packet after native queue, C0 frozen native retirement before queue.',
            },not_repurposed={
                'SmFreezeRenderState':'Always0 under acquired FF; no epoch or ack use. Genuine Samus freeze admission/render remain original.',
                'SmFreezePaletteControl':'Read-only exact original native area/Bowser control; all native stores unchanged.',
                'FfPaletteAck':'Exclusively original body-P0 commit cache; never FX state.',
            },transient_scratch='Borrow native R0..R7 only after actual DrawAll returns; save/restore exact original8bytes and returnedAXYP on CPU stack. No FF target/rect/renderbuffer mutation, no new RAM.',
            lifecycle={
                'newgame':'Actual InventoryInit tails SamusFreezeInit: all aliases/packet/state/control0.',
                'scene_life_area_player':'Actual InitScreen→ArGenSceneInit→FwSceneInit→FwMuxScene clears Pending/Last/State/Turn FIRST, prepares C0 exact area restore, publishesLast80 LAST. Original source Ensure/life/AreaReset/earned gear unchanged.',
                'retirement':'Actual MenuResolve→FwMuxMenu→Retire clears Pending/Last/Turn/State FIRST, clears all prior FF OAM, publishes full nativeC0 before actual ArGenResolve/FmResolve writesSelected. Exact current chain remains; future Quick must be appended via its genuine new resolve helper.',
                'death':'Display resource aliases are not source health/gear: stale packet remains paired with prior complete OAM until real nextScene or menu retirement. No scheduler advancement without a completed draw; heartbeat does not advancecursor.',
                'pause_skip':'Real row29 runs before native Pause/GamePause/ShouldSkipDrawSprites branch. Original body tick first; ready selectedFF heartbeat reissues LAST completed nonnative palette but does not change cursor/OAM. New draw may overwrite same complete packet before Main commits0.',
                'NMI':'Frozen exactC0 preflush before native→PN→Ar chain; original ASL Pending handles only complete80 after native queue. Lag path neither flushes nor DMA; Main holds negative NmiDisable during all packet/OAM changes.',
                'Samus_exclusion':'FF acquisition clears staleSmFreezeRenderState. Genuine FF nativeflash adapter bypasses Samus coloractor; current FwNativeDrawAll calls SamusRenderFinish only when entryState!=0. Real FF combat/pickup never writes thisstate.',
                'cold':'Full current FwCheck cookie before any new FF epoch/heartbeat worker. Unready/foreign has no access or alias writes. Existing forcedblankScene may prepare nativeC0 without executing RAM3.',
                'malformed':'New code validatesLast80..85, cursor0..5; invalid aliases fall back nativefamily0 without source gameplay access. FrozenC0 malformedpacket reject unchanged.',
                'runtime_fields_added':0,
            },actual_alternating_player_controls=transpose(b),actual_newgame_control=inventory(b),
            actual_native_static_palette_publishers=palette_publishers(b),
            implementation_obligations=[
                'Actual emitted epoch code still requires grant for this exact reuse before installation/execution.',
                'Reissue nativefamily0 too when priorFXfamily changed; do not let fullnativequeue preserve priorFX colors.',
                'Audit native variable palette queue writes under selectedFF; generic VRAMcontrol0/5/6/7 are queues, not a literal newP1 vector.',
                'Use only families observed in actual admitted completedOAM; preserve body0 and unrelatedP2/P3; always clear metadata beforeDMA.',
                'Full heartbeat/paused/skippedMain/normal-lagIRQ/cold-fullcookie/lateCFQuickScene controls remain required on actual new sourcecartridge.',
            ])
        p['passed']=True
    except Exception as e:p.update(error=repr(e),traceback=traceback.format_exc())
    p['bindings']={str(f.resolve()):L.sha(f)for f in sorted(files)}
    out=O/('proposal.json'if p['passed']else'negative.json');out.write_text(json.dumps(p,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=p['passed'],path=str(out),sha256=L.sha(out),error=p.get('error'))),flush=True)
    assert p['passed']

if __name__=='__main__':main()
