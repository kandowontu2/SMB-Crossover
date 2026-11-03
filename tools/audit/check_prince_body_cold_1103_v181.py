"""Complete current83 source-backed constructors and original renderer oracle."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_body_backing_1103_v180 as M
import check_prince_body_owner_1103_v179 as H
V,N,I,O=M.V,M.V.N,M.V.I,M.O
C=V.C


def loaded(base):
    m,out=C.cold(base,38)
    N.put(m,NmiDisable=1,DisableScreenFlag=0,TimerControl=0,AreaType=1,Player_Rel_XPos=48,Player_Rel_YPos=176,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Mirror_PPUMASK=30)
    m[0x2001]=30
    return base,m,json.loads((V.O/'native-labels-v153.json').read_text())


def first8(base):
    prior=V.loaded;V.loaded=lambda:loaded(base)
    try:return V.first8()
    finally:V.loaded=prior


def raw_pose_fixture(base):
    _,m,lab=loaded(base)
    return V.environment(),m,lab


def main():
    base,q=M.image();parent=dict(base,raw=M.PARENT.read_bytes());seeds={};rows=[]
    if '--renderer-only'in sys.argv:
        source=inspect.getsource(main)
        a=source.rindex('    text=inspect.getsource(H.main)');z=source.index('    result=dict(passed=True,CPU_only=True',a)
        env=dict(globals(),base=base,parent=parent)
        exec(compile('def finish_renderer():\n'+source[a:z],str(Path(__file__)),'exec'),env)
        return env['finish_renderer']()
    old_cookie=bytes.fromhex(q['old_Prince_cookie']);new_cookie=bytes.fromhex(q['Prince_cookie'])
    runtime,meta,state=M.images();live=(V.O/'native-live-v149.bin').read_bytes();runtime=bytearray(runtime);runtime[0x1fa3:0x1fd8]=live
    for owner in [37,38,39,40]:
        print('Actual181 full source-backed cold',owner,flush=True)
        m,out=C.cold(base,owner);old,previous=C.cold(parent,owner)
        assert out['regs']==previous['regs']
        if owner!=38:
            assert all(bytes(a)==bytes(b)for a,b in zip(m.ram,old.ram)),('Foreign cold private parity',owner)
        else:
            assert bytes(m.ram[3][:len(runtime)])==runtime
            assert bytes(m.ram[2][0x800:0x800+len(meta)])==meta
            assert bytes(m.ram[2][:0x766])==bytes(old.ram[2][:0x766])
            expected=bytearray(state[1375:1529]);expected[:25]=(V.O/'native-installer-v153.bin').read_bytes()
            assert bytes(m.ram[2][0x766:0x800])==expected
            assert bytes(m.ram[2][0x200:0x235])==bytes(53)
            assert bytes(m.ram[2][0x1fe0:0x1ff0])==bytes(m.ram[3][0x1fe0:0x1ff0])==new_cookie
        seeds[owner]=m
        rows.append(dict(owner=owner,CPU=out['CPU'],minimum_SP=out['minSP'],full_foreign_AXYP_SP_private_parity=owner!=38))
    transitions=[]
    for previous in [37,38,39,40]:
        for owner in [37,38,39,40]:
            print('Actual181 transition',previous,owner,flush=True)
            m=N.fork(seeds[previous]);C.fields(m,owner);out=I.invoke(m,193,0xae00,(83,71,109,0x21))
            assert out['regs'][3]&1
            assert all(bytes(m.ram[k][0x1fe0:0x1ff0])==bytes(seeds[owner].ram[k][0x1fe0:0x1ff0])for k in [2,3])
            if owner==38:
                assert bytes(m.ram[3][:len(runtime)])==runtime and bytes(m.ram[2][0x200:0x235])==bytes(53)
            transitions.append(dict(previous=previous,owner=owner,CPU=out['CPU'],minimum_SP=out['minSP']))
        m=N.fork(seeds[previous]);N.put(m,SelectedCharacter=0);out=I.invoke(m,193,0xae0b,(83,71,109,0x21))
        assert out['regs'][3]&1 and out['regs'][:3]==[83,71,109]
        assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
        if previous==38:assert m.ram[2][0xaa]==m.ram[2][0xab]==0
    rejects=0
    for owner in [37,38,39,40]:
        for bank in [2,3]:
            for index in range(16):
                m=N.fork(seeds[owner]);m.ram[bank][0x1fe0+index]^=1;before=[bytes(a)for a in m.ram]
                out=I.invoke(m,193,0xb08c,(83,71,109,0x21));assert not out['regs'][3]&1 and before==[bytes(a)for a in m.ram]
                rejects+=1
    fresh=[]
    for row in [15,36]:
        m=N.fork(seeds[38]);m.ram[2][0x6cf]=2;m.ram[2][0x6ee]=2;before=bytes(m.ram[3])
        I.invoke(m,193,0xb08c+3*row)
        assert bytes(m.ram[3])==before and m.ram[2][0x6cf]==5 and m.ram[2][0x6ee]==0
        fresh.append(row)
    (O/'source-cold-prefix-v181.json').write_text(json.dumps(dict(passed=True,source_code_injected=False,memory_SHA256=q['expected_memory_only_SHA256'],cold=rows,transitions=transitions,foreign_selected_retirements=4,bad_header_bytes_rejected=rejects,warm_Fresh_rows=fresh,complete_runtime_metadata_state_exact=True,packet_zero_before_live=True),indent=2)+'\n')
    # Reuse179's full408-pose differential, replacing its injected candidate
    # with genuinely decoded current181 and its reference with actual80d3.
    text=inspect.getsource(H.main)
    old="e,seed,lab=V.first8();e['run'](seed,'GameLoop',lab)"
    assert old in text
    text=text.replace(old,"e,seed,lab=NEW_RAW();_,oldseed,_=OLD_RAW()")
    assert text.count('old=N.fork(seed);new=N.fork(seed);patch(new)')==2
    text=text.replace('old=N.fork(seed);new=N.fork(seed);patch(new)','old=N.fork(oldseed);new=N.fork(seed)')
    # The successor source-declares code in the former high-byte table;
    # the independent expected values must come from the old source table.
    text=text.replace('old_lo=bytes(seed.ram[3]', 'old_lo=bytes(oldseed.ram[3]').replace('old_hi=bytes(seed.ram[3]', 'old_hi=bytes(oldseed.ram[3]')
    # The two real preceding GameLoops intentionally differ in native OAM,
    # scratch and SMC because the corrected descriptor skips legacy rendering.
    # Supply equal arbitrary caller inputs only for the standalone pose-leaf
    # differential. The later complete GameLoop retains actual native state.
    marker="        for m in [old,new]:\n"
    assert text.count(marker)==1
    text=text.replace(marker,marker+"            m[3:11]=oldseed[3:11]\n            m[0x200:0x300]=bytes([0xf8])*256\n            m[0x15a:0x17b]=oldseed[0x15a:0x17b]\n")
    marker="        first=I.invoke(old,3,lab['PpHostDraw'],(83,71,109,0x61))"
    assert text.count(marker)==1
    text=text.replace(marker,"        for m in [old,new]:\n            I.invoke(m,3,lab['PpHostProject'],(83,71,109,0x61))\n            I.invoke(m,3,0xc383,(83,71,109,0x61)) # Actual unchanged HostExport supplies render anchors.\n"+marker)
    text=text.replace('allow={2:set(),3:set()}','allow={2:set(range(0x1fe0,0x1ff0)),3:set(range(0x1fe0,0x1ff0))}')
    text=text.replace('code_injected_fixture=True,source_backed_new_cold_pending=True','code_injected_fixture=False,source_backed_new_cold_pending=False')
    marker='old=N.fork(oldseed);new=N.fork(seed)'
    a=text.rindex(marker)
    text=text[:a]+"_,old,_=OLD_FIRST8();_,new,_=NEW_FIRST8()"+text[a+len(marker):]
    text=text.replace("'renderer-CPU-v179.json'","'renderer-source-CPU-v181.json'")
    env=dict(H.__dict__,__file__=str(Path(__file__)),NEW_RAW=lambda:raw_pose_fixture(base),OLD_RAW=lambda:raw_pose_fixture(parent),NEW_FIRST8=lambda:first8(base),OLD_FIRST8=lambda:first8(parent))
    exec(compile(text,str(Path(H.__file__)),'exec'),env);env['main']()
    result=dict(passed=True,CPU_only=True,source_code_injected=False,ROM_written=False,
                parent_SHA256=q['parent_SHA256'],memory_SHA256=q['expected_memory_only_SHA256'],Prince_cookie=q['Prince_cookie'],
                cold=rows,transitions=transitions,foreign_selected_retirements=4,bad_header_bytes_rejected=rejects,
                warm_Fresh_rows=fresh,complete_runtime_metadata_state_exact=True,packet_zero_before_live=True,
                unchanged_shared83_instructions=True,all408_original_renderers_and_pattern_bytes_exact=True,
                stable_zero_header_address=0x6e1,retained_fixture_negative='181 first standalone differential inherited different legitimate native scratch/OAM from preceding old versus corrected GameLoops. Equal caller-input preconditions now supplied for the standalone leaf only; complete later native GameLoop is not normalized.',required='Explicit late unbanked native-reader mapping trace and actual newpath IRQ/genuineFF/nested; root private resource/manifest review then native hardware body probe.',
                bindings={str(p.relative_to(R)):M.B.sha(p)for p in [Path(__file__),Path(M.__file__),Path(H.__file__),O/'body-manifest-v180.json',O/'renderer-source-CPU-v181.json',O/'body-pool.bin',O/'body-worker.s',O/'body-worker.bin',R/'docs/qa/allocations/combined-owner-auth-1103-v116.json']})
    (O/'source-cold-CPU-v181.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ['bindings','transitions']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        if not (O/'source-cold-negative-v181.json').exists():
            (O/'source-cold-negative-v181.json').write_text(json.dumps(dict(passed=False,error=repr(error)),indent=2)+'\n')
        raise
