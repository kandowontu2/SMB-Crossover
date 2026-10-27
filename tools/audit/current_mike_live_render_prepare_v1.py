"""Bounded passive live Mike rendering diagnostic; source-only preparation."""
from pathlib import Path
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import current_mike_earned_remainder_prepare_v2 as previous

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
FIXTURE=R/'tests/current-mike-render-diagnostic-v3.lua'
HELPER=R/'tools/audit/current_mike_live_render_diagnostic_v1.lua'
CODEC=R/'tools/audit/final_inventory_compact_capture_v1.lua'


def main():
    out=R/'build/current-ab221-mike-live-render-diagnostic-v1'
    assert not out.exists()or all(p.name.startswith('source-negative-')for p in out.iterdir())
    original=previous.NEW
    assert sha(original)=='73646982ed71bb549dab544fe99823d852fdaa3ae9db5bb01a2f35ac84f29989'
    marker='-- All callback registration is startup-static. No callback adds/removes callbacks.'
    before=original.read_text();helper=HELPER.read_text();assert before.count(marker)==1
    after=before.replace(marker,helper+'\n'+marker)
    assert after.replace(helper+'\n','')==before,'Only additive read-only diagnostic, original fixture unchanged'
    assert helper.count('emu.write')==0 and helper.count('setInput')==0
    if FIXTURE.exists():
        assert (R/'build/current_mike_live_render_preparation_negative_v1.json').is_file(),'Only the unbound first preparation failure can be corrected'
    FIXTURE.write_text(after,newline='\n')
    code=previous.change(previous.OLD.read_text(),previous.PY_PAIRS)
    old="fixture=R/'tests/current-mike-powerups-v2.lua'"
    assert code.count(old)==1;code=code.replace(old,"fixture=R/'tests/current-mike-render-diagnostic-v3.lua'")
    old="if n in ['Collect','Injury','Defeat','Reflect','DropCollect']"
    assert code.count(old)==1
    code=code.replace(old,"if n in ['Collect','Injury','Defeat','Reflect','DropCollect','RenderShotCall','RenderShotReturn']")
    old='        if rec is not None and n:'
    assert code.count(old)==1;code=code.replace(old,'        source_render_step(q,c,n)\n'+old)
    old='        original(c)'
    assert code.count(old)==1
    code=code.replace(old,"        source_start=len(q.m.writes);source_pc=c.pc\n        original(c)\n        source_render_writes(q,source_pc,bank,q.m.writes[source_start:])")
    old='    cfg=dict(ROM_sha256=EXPECTED'
    assert code.count(old)==1;code=code.replace(old,'    cfg=dict(render_diagnostic=render_metadata(b),ROM_sha256=EXPECTED')
    ns={'__file__':str(Path(__file__)),'__name__':'_mike_live_render_v1'}
    exec(compile(code,str(previous.OLD),'exec'),ns)
    inherited=ns['hooks_for'];pending={};stats={}
    def meta(b):
        address,location=ns['address'],ns['location']
        owner=(location(b,'JnArtStart')-16)//8192;start=address(b,'JnArtStart');off=location(b,'JnArtStart')
        lo=location(b,'JnShotAllLo');hi=location(b,'JnShotAllHi');rows=[]
        for i in range(52):
            ptr=b['raw'][lo+i]+256*b['raw'][hi+i];pos=off+ptr-start
            assert start<=ptr<start+8192 and(pos-16)//8192==owner
            size=b['raw'][pos];assert size%4==0 and size<128
            rows.append(dict(pointer=ptr,bank=owner,header=size,record_sha256=hashlib.sha256(b['raw'][pos:pos+size+1]).hexdigest()))
        return dict(codec=str(CODEC.resolve()).replace('\\','/'),records=rows,
            scope='Passive actual shot emission, complete Main image, exact source-page DMA linkage and whole PPU. No visibility inference from allocation alone.',
            caps=dict(container_bytes=134217728,container_records=3000,diagnostic_bytes=67108864,diagnostic_rows=12000))
    def hooks(b):
        h,sfx=inherited(b);address,location=ns['address'],ns['location']
        pc=address(b,'JnDraw::Next');off=location(b,'JnDraw::Next');dest=address(b,'JnDraw::Draw')
        assert b['raw'][off-3:off]==bytes([32,dest&255,dest>>8])
        owner=(off-16)//8192
        h['RenderShotCall']=dict(pc=pc-3,banks=[owner],bytes=list(b['raw'][off-3:off]),source_symbol='JnDraw::Next',source_delta=-3)
        h['RenderShotReturn']=dict(pc=pc,banks=[owner],bytes=list(b['raw'][off:off+3]),source_symbol='JnDraw::Next',source_delta=0)
        return h,sfx
    bundle=ns['scoped_load'](R/'build/mega_proto_body_palette_9ea.nes');rows=meta(bundle)['records']
    def source_step(q,c,n):
        if n=='RenderShotCall':
            assert not pending
            slot=c.x;assert 0<=slot<6 and q.get('JnSavedY')==slot
            kind=q.get('JnShotKind',slot);age=q.get('JnShotAge',slot);vx=q.get('JnShotVX',slot)
            assert 1<=kind<=13
            pose=kind-1+(13 if vx>=128 or vx==0 and q.get('PlayerFacingDir')==2 else 0)+(26 if age&4 else 0)
            row=rows[pose];ptr=q.get('R0')+256*q.get('R1')
            assert c.y==pose and ptr==row['pointer']and q.m.banks[2]==row['bank']and q.m[ptr]==row['header']
            pending.update(kind=kind,pose=pose,header=row['header'],writes=[])
        elif n=='RenderShotReturn':
            if not pending:return # Next is also the exact empty-slot branch target.
            kind=pending['kind'];a=stats.setdefault(str(kind),dict(calls=0,nonempty_emissions=0,max_source_writes=0,poses=[]))
            a['calls']+=1;a['nonempty_emissions']+=bool(pending['writes']);a['max_source_writes']=max(a['max_source_writes'],len(pending['writes']))
            assert len(pending['writes'])<=pending['header'],'Real renderer never writes more than source record parts'
            if pending['pose']not in a['poses']:a['poses'].append(pending['pose'])
            pending.clear()
    def source_writes(q,pc,bank,writes):
        if pending:pending['writes'].extend((at,v)for at,v in writes if 0x200<=at<0x300)
    ns.update(hooks_for=hooks,render_metadata=meta,source_render_step=source_step,source_render_writes=source_writes)
    argv=sys.argv;sys.argv=[str(Path(__file__)),'--identity','mike','--output',str(out)]
    try:ns['main']()
    finally:sys.argv=argv
    assert not pending and set(stats)=={str(i)for i in range(1,14)}
    assert all(r['calls']>0 for r in stats.values())
    controls=out/'live-render-source-controls.json'
    put(controls,dict(passed=True,native_run=False,Lua_VM_executed=False,kind_controls=stats,
        scope='Fresh full53-case assembled source campaign including every real shot draw JSR/return, pose-table pointer, actual physical C owner/header and exact OAM source writes. Does not qualify native pixels or callback semantics.'))
    ready=out/'prepared-not-run.json';z=json.loads(ready.read_text())
    priorready=R/'build/current-ab221-mike-hard-items-v2/prepared-not-run.json'
    priorresult=R/'build/current-ab221-mike-hard-items-v2/native/result.json'
    paths={Path(d['path'])for d in z['bindings']}|{HELPER,CODEC,Path(__file__),
        Path(previous.__file__),previous.OLD,previous.FIXTURE,previous.NEW,priorready,priorresult,controls,
        R/'tools/audit/final_inventory_compact_capture_v1.py',R/'src/mike_jones_render.s',R/'src/mike_jones_art.inc',
        R/'build/current_mike_live_render_preparation_negative_v1.json'}
    z.update(status='PASSIVE_RENDER_DIAGNOSTIC_PREPARED_NATIVE_UNRUN',Lua_VM_executed=False,native_run=False,
        prior_native_pass_scope='Existing Mike v2 all53 mechanics passed; unchanged8 screenshots often contain popup after shot disappears, so no sprite appearance claim.',
        diagnostic='Additional startup-static read-only exact shot JSR/return hooks, source OAM writes, completed Main pages and real all256 DMA data. Capture actual whole PPU for weapon intervals into one capped NESPPU01 stream. No original assertion/control/cap/resource setup changes.',
        additional_caps=dict(container_bytes=134217728,records=3000,diagnostic_bytes=67108864,diagnostic_rows=12000,extra_PNGs=0))
    z['bindings']=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]
    put(ready,z)
    put(out/'diagnostic-only-delta.json',dict(native_run=False,Lua_VM_executed=False,
        exact_reverse_original_fixture=True,original=dict(path=str(original),sha256=sha(original)),helper=dict(path=str(HELPER),sha256=sha(HELPER)),
        records=meta(bundle)['records'],source_controls=dict(path=str(controls),sha256=sha(controls)),
        limits='Whole-page source matches and retained emitted bytes are explicit observations. No sprite opacity/fairness or art fidelity verdict before real capture/pixel review; unmatched epochs are retained, not invented.'))
    assert all(sha(Path(d['path']))==d['sha256']for d in z['bindings'])
    print(json.dumps(dict(ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),kinds=len(stats),source_draws=sum(r['calls']for r in stats.values()),native_run=False)))


if __name__=='__main__':main()
