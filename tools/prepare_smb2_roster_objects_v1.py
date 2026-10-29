"""Project genuine SMB2 carry geometry and object fractional integrators."""
import json
from py65.devices.mpu6502 import MPU
import prepare_smb2_roster_native_v1 as D


def main():
    _,l,_,_,addresses=D.graph();a,_,_=D.ram_map(addresses,l)
    m=D.original(1);cpu=MPU(memory=m)
    a[2]=('S2Math2',0x5c7c)
    a[l['EnemyMovementDirection']]=('S2ObjectFacing0',0x5c76)
    # NonSticky is only cleared by horizontal physics. This supported object's
    # lift timer is already zero before physics; the two zero states overlap.
    a[l['ObjectNonSticky']]=('S2ObjectLift',a[l['ObjectBeingCarriedTimer']][1])
    external={0x966e:'S2CarryGeometryReturn'}
    seeds=[l['CarryObject'],l['ApplyObjectPhysicsY'],l['ApplyObjectPhysicsX']]
    code={};todo=list(seeds)
    while todo:
        p=todo.pop()
        if p in external or p in code:continue
        assert 0x960f<=p<0x966e or 0x9e4b<=p<0x9ef0,hex(p)
        op,mode=cpu.disassemble[m[p]]
        n={'imp':1,'acc':1,'imm':2,'zpg':2,'zpx':2,'zpy':2,'inx':2,'iny':2,'rel':2,'abs':3,'abx':3,'aby':3,'ind':3}[mode]
        code[p]=(op,mode,n)
        if mode=='rel':todo.append((p+2+(m[p+1]if m[p+1]<128 else m[p+1]-256))&65535)
        elif op in ['JMP','JSR']:todo.append(m[p+1]|m[p+2]<<8)
        if op not in ['JMP','RTS','RTI']:todo.append(p+n)
    lines=['; Genuine ROM1 carry position prefix and full object integrators.',
        '; Carry stops BEFORE original enemy animation/render (host owns it).',
        '.pushseg','.segment "PARODIUS_BELLS"']
    branches={'BCC':'jcc','BCS':'jcs','BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl'}
    for p,(op,mode,n)in sorted(code.items()):
        arg='';s=op.lower()
        if mode=='rel':arg='S2O%04X'%((p+2+(m[p+1]if m[p+1]<128 else m[p+1]-256))&65535);s=branches[op]
        elif mode=='imm':arg='#$%02x'%m[p+1]
        elif mode=='acc':arg='a'
        elif mode!='imp':
            t=m[p+1]|(m[p+2]<<8 if n==3 else 0)
            if op in ['JMP','JSR']:arg=external.get(t,'S2O%04X'%t)
            elif t==0x7eff:arg='S2CarryOffsets'
            elif t==0x7f0d:arg='S2CarryOffsets+14'
            elif t==0x9607:arg='S2CarryCrouch'
            else:assert t in a,(hex(p),hex(t));arg=a[t][0]
            if mode in ['zpx','abx']:arg+=',x'
            elif mode in ['zpy','aby']:arg+=',y'
        if op=='ADC'and mode=='aby'and t in [0x7eff,0x7f0d]:
            lines.append('S2O%04X: jsr %s ; authentic class-patched carry table'%(p,'S2CarryAddLo'if t==0x7eff else'S2CarryAddHi'))
        elif op=='STY'and mode=='zpx':
            lines.append('S2O%04X: pha\n tya\n sta %s\n pla ; original STY zp,X; next LDA defines NZ'%(p,arg))
        else:lines.append('S2O%04X: %s %s ;1:%04X %s'%(p,s,arg,p,m[p:p+n].hex()))
        if p+n in external and op not in ['JMP','RTS','RTI']:lines.append(' jmp '+external[p+n])
    offsets=[]
    for char in range(4):
        block=bytearray(m[l['ItemCarryYOffsets']:l['ItemCarryYOffsets']+28])
        for i,n in [(0,'CarryYOffsetBigLo'),(7,'CarryYOffsetSmallLo'),(14,'CarryYOffsetBigHi'),(21,'CarryYOffsetSmallHi')]:block[i]=m[l[n]+char]
        offsets.extend([0]+list(block))
    lines+=['S2CarryGeometryReturn: rts','S2CarryOffsets: .byte '+','.join(map(str,offsets)),
        'S2CarryCrouch: .byte '+','.join(str(v)for v in m[0x9607:0x960f]),'.popseg']
    out=D.ROOT/'src/smb2_roster_objects_native.inc';out.write_text('\n'.join(lines)+'\n')
    stats=D.original(2)
    # Original stats live in pair5? Source address authenticated by audit.
    raw=D.ROM.read_bytes(); stats=bytearray(65536);stats[0x8000:0xc000]=raw[16+5*16384:16+6*16384]
    blocks=[stats[p:p+23]for p in [0x83cd,0x83fb,0x83e4,0x8412]]
    assert [b[6]for b in blocks]==[0xb0,0xd6,0xb2,0xb3]
    q=D.ROOT/'src/smb2_roster_stats.inc';q.write_text('S2OriginalStats: .byte '+','.join(str(v)for b in blocks for v in b)+'\n')
    p=D.OUT/'object-projection.json';p.write_text(json.dumps(dict(original=D.binding(D.ROM),instructions=len(code),outputs=[D.binding(out),D.binding(q)],
        contract='Three owned records; CarryObject actual geometry ends966E. ObjectNonSticky0 aliases lift0 only for non-carried physics. Actor epochs require real spawn/erase/reset callback, not EnemyFlag inference.',tool=D.binding(__file__)),indent=2)+'\n')
    print(json.dumps(D.binding(p)))


if __name__=='__main__':main()
