"""Detached marker plan's own compiled entrants/data references; no CPU/mount."""
from pathlib import Path
from unittest.mock import patch
import json
import plan_contra_force_p1_work_marker_1116 as Plan

C=Plan.C
PLAN_SHA='e8747d78a3d307449d2c3458869df880f361b5e4efb868fd37f36347ee50ccd3'


def inspect(raw):
    assert C.H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    z,s=Plan.inputs(raw);d=Plan.descriptor(raw);lines={};symbols={};segments={}
    for line in(Plan.Audit.P.KERNEL/'runtime.dbg').read_text().splitlines():
        if not line.startswith(('line\t','sym\t','seg\t')):continue
        kind=line.split('\t',1)[0];row=Plan.Audit.P.fields(line)
        {'line':lines,'sym':symbols,'seg':segments}[kind][int(row['id'])]=row
    new_renderer=d['fragments'][0]['labels'];new_late=d['fragments'][2]['labels'];new_early=d['fragments'][1]['labels']
    remapped={};removed={}
    for sym in symbols.values():
        if'val'not in sym or'seg'not in sym:continue
        seg=segments[int(sym['seg'])];pc=int(sym['val'],0)
        if seg.get('oname')!='ram3.bin':continue
        target=None
        if 0xb3c4<pc<0xb5c8:
            target=new_renderer.get(f'Old_{pc:04X}')
            # Replaced loop/prefix interiors have only local source readers;
            # their old labels disappear, rather than becoming public aliases.
            if target is None:removed[sym['name']]=pc
        elif sym['name']=='CfP1Late':target=new_late['Leaf']
        elif sym['name']=='CfNativeP1MaskReadEnd':target=new_early['NativeMaskReadEnd']
        elif sym['name']=='Bits'and pc==0xbe4f:removed[sym['name']]=pc
        if target is not None and target!=pc:remapped[sym['name']]=(pc,target)
    refs=[]
    for sym in symbols.values():
        own=sym
        if'val'not in own and'exp'in own:own=symbols[int(own['exp'])]
        name=own['name']
        if name not in remapped and name not in removed:continue
        expected_file=8 if 0xb3c4<(remapped.get(name,(removed.get(name),0))[0])<0xb5c8 else 15
        for rid in map(int,filter(None,sym.get('ref','').split('+'))):
            row=lines[rid];assert int(row['file'])==expected_file,(name,row,'External private moved-label reader')
            refs.append(dict(symbol=name,old_PC=remapped[name][0]if name in remapped else removed[name],
                new_PC=remapped[name][1]if name in remapped else None,source_file_id=expected_file,
                line=int(row['line']),kind='instruction_or_data'if'span'in row else'export_declaration'))
    for name in('CfHostRenderBody','CfHostRenderShot','CfP1Late','CfNativeP1MaskReadEnd'):
        assert name in remapped,(name,'Expected moved consumer domain missing')
    ownlo=8192+(s['CfOwnLo']&8191);ownhi=8192+(s['CfOwnHi']&8191);carrier=z['q']['carrier']
    targets=[carrier[ownlo+i]+256*carrier[ownhi+i]for i in range(36)]
    moved_old={pc for pc,_ in remapped.values()}|set(removed.values())
    assert not set(targets)&moved_old,('Moved interior has a private service vector',set(targets)&moved_old)
    assert all(z['q']['carrier'][8192+0x1e00+i*3:8192+0x1e03+i*3]==bytes.fromhex('4c6ebe')for i in range(36))
    anchored={name:s[name]for name in('CfHostVisible','CfHostGraphics','CfHostDraw','CfHostPortrait','CfHostRenderAll',
        'CfSourceWindowHigh','CfP1EarlyTag','CfNativeP1MaskRead','CfP1LateEntry','CfP1Heartbeat','CfP1Acquire','CfP1PacketGate','CfHostAreaReset','CfHostImport')}
    assert d['fragments'][0]['new_hex'][-64:]==d['fragments'][0]['old_hex'][-64:]
    old_late=bytes.fromhex(d['fragments'][2]['old_hex']);new_late_bytes=bytes.fromhex(d['fragments'][2]['new_hex'])
    assert old_late[0xbed0-0xbe53:]==new_late_bytes[0xbed0-0xbe53:]
    # This inventory explicitly admits the existing owning actor-index domain;
    # it does not mask a poisoned arbitrary private internal call.
    host=(C.R/'build/contra-force-world-roles-1031-v2/kernel/host-runtime.s').read_text()
    assert 'ldx #0\n jsr CfHostCallInput\n ldx #0\n jsr CfHostCallBody'in host
    boundary=C.R/'build/contra-force-projectile-contact-1031-v3/kernel/boundaries.s'
    data=boundary.read_bytes();source=data.decode()
    assert 'ldx #10\nCfHostNextShot:'in source and 'ldx CfShotSlot\n inx\n cpx #22\n bcc CfHostNextShot'in source
    return dict(owning_ROM_SHA256=C.H(raw),descriptor_receipt='d2a7ed8772c20ea2933dc9913f9b94c409a886bca6e1154861d68cbb36971c03',
        compiled_private_moved_and_removed_label_references=refs,moved_labels=remapped,removed_internal_labels=removed,
        anchored_entries_and_table=anchored,all36_private_targets=targets,
        all36_A2_veneers_and_targets_unchanged=True,no_moved_interior_in_authoritative_service_vector=True,
        source_window_table32_and_full_paint44_plus_final_gate_JMP_exact=True,
        original_actor_boundary=dict(player_X=0,shot_X_half_open=[10,22],shot_scope_source=str(boundary.relative_to(C.R)),shot_scope_SHA256=C.H(data)),
        arbitrary_poisoned_private_actor_X139_not_admitted=True,
        scope='Compiled owning-source reader + authoritative36vector domain; no blanket PRG/CHR byteword-absence claim',
        actual_foreign_public_full_guard_transport_ISR_lifecycle_pending_after_source_lease=True,
        new_code_execution_mount_ROM_native_delivery=False,outputs=0)


if __name__=='__main__':
    raw=C.ROM.read_bytes();reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'No mutable Nightly reread'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Read-only ingress audit attempted files/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=inspect(raw)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
