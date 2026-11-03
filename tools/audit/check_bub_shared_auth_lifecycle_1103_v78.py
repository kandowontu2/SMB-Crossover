"""Actual typed contact and trapped-AI retirement for the shared-auth factor."""
import json
from pathlib import Path
import check_bub_shared_auth_contracts_1103_v77 as P
O,R,N,Q,address,sha=P.O,P.R,P.N,P.Q,P.address,P.sha


def main():
    dst=O/'shared-auth-v78-lifecycle.json';assert not dst.exists()
    old,new,route,q,manifest,ol,nl,patches,refs=P.P.build()
    CPU=N.NesMPU;captures=[];contacts=[];retire=[]
    for identity in [0,1]:
        pair=[];states=[];epochs=[]
        for bb in [old,new]:
            m,epoch,saved=Q.Q.trap(bb,route,identity)
            P.C.clear(m);pair.append(m);states.append(saved);epochs.append(epoch)
        assert epochs[0]==epochs[1]and states[0]==states[1]
        assert pair[0].ram==pair[1].ram and pair[0].rawtags==pair[1].rawtags
        assert pair[0].ram[2][0x320]and N.get(pair[0],'Enemy_Flag')==128
        captures.append(dict(identity=identity,source_capture_epoch=epochs[0],saved_native_fields=states[0]))
        out=[]
        for m in pair:
            N.put(m,SelectedCharacter=0);out.append(P.public(m,0xae0b))
        P.parity(*pair,out)
        for m in pair:
            for name,value in states[0].items():
                if name!='Enemy_ID':assert N.get(m,name)==value,(identity,name,value,N.get(m,name))
            assert not m.ram[2][0x320]and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
        repeated=[P.public(m,0xae0b)for m in pair];P.parity(*pair,repeated)
        retire.append(dict(identity=identity,all_saved_native_fields_restored=True,positive_flag=states[0]['Enemy_Flag'],repeat_retire_exact=True))
        # Enter the real native body consumer with a legitimate constructed
        # actor and native Goomba. Its typed37 inputs come from native code.
        pair=[Q.Q.fresh(bb,route,identity)for bb in [old,new]];out=[];counts=[]
        for m in pair:
            Q.L.E.main_fields(m);Q.Q.Q.enemy(m,x=56,y=184,slot=0)
            N.invoke(m,'InitGoomba',x=0);N.put(m,ObjectOffset=0,Enemy_X_Speed=0,
                Enemy_CollisionBits=0,EnemyOffscrBitsMasked=0,InjuryTimer=0,CrossoverBehaviorVersion=1)
            count=0
            class Trace(CPU):
                def step(self):
                    nonlocal count
                    if self.pc==0xb029 and self.memory.rawtags[1]==193:count+=1
                    return super().step()
            N.NesMPU=Trace
            try:
                z=[]
                for epoch in range(3):
                    N.put(m,FrameCounter=epoch,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0)
                    z.append(N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x21))
                out.append(z[-1]);counts.append(count)
            finally:N.NesMPU=CPU
        P.parity(*pair,out);assert counts[0]==counts[1]and counts[0]>0,('Actual typed37 native entry',identity,counts)
        contacts.append(dict(identity=identity,actual_native_B029_calls=counts[0],source_private_native_AXYP_SP_SMC_maps_exact=True))
    # This is a bound literal inventory, not an unproved all-pointer census.
    # Recompiled owner/extra instructions and unchanged public entry points
    # are separately bound by76/77. Source callers are checked before grant.
    literals=[]
    for name,target in [('CoCheckCode',ol['CoCheckCode']),('CoCheckHeaders',ol['CoCheckHeaders']),
            ('CoRetireOwners',ol['CoRetireOwners']),('CoSmc',ol['CoSmc']),('ShCheckCode',0xa800)]:
        bank=old['raw'][16+65*8192:16+66*8192]
        for offset in range(8190):
            if bank[offset]in[0x20,0x4c,0xad,0xbd,0xb9,0xbc]and bank[offset+1:offset+3]==target.to_bytes(2,'little'):
                literals.append(dict(symbol=name,CPU=0xa000+offset,compiled=bank[offset:offset+3].hex(),
                    inside_recompiled_owner=0xe00<=offset<0x1013,
                    inside_recompiled_extra=0xb72<=offset<0xbce,
                    inside_replaced_Sh_check=0x800<=offset<0x849))
    result=dict(passed=True,CPU_only=True,CPU_qualified=False,candidate_allowed=False,ROM_written=False,
        original_captures=captures,actual_foreign_selected_retirement=retire,actual_native_typed37=contacts,
        bank65_bound_literal_references=literals,scope='Real original shot/capture plus native EnemiesAndLoopsCore, full authenticated foreign-selected retirement restores every saved native field before invalidating both headers; repeat retire cannot restore twice. Real complete Main invokes typed37 through native body contact, with both identities and unchanged source/native output. No fabricated direct virtual37 caller or seeded trap token.',
        remaining=['Complete source binding for every actual external internal-helper/cookie/SMC reference, not merely literal matches.',
            'Real IRQ/FF/NMI/nested cuts at all reached changed Sh/Bub/cold/Fresh/retire seams.',
            'Pending Prince/DK composition and root native candidate review; no admission or native cadence claim.'],
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),Path(P.__file__),
            O/'shared-auth-v76-funding.json',O/'shared-auth-v77-contracts.json',O/'shared-auth-v76.s',
            O/'shared-auth-v76.bin',O/'shared-auth-v76-extra.bin',O/'shared-auth-v76-Sh.bin']})
    dst.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['passed','original_captures','actual_foreign_selected_retirement','actual_native_typed37']}))


if __name__=='__main__':main()
