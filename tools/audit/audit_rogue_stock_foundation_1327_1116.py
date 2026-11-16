"""Read-only actual1327 Rogue menu/cold and retained stock-policy binding.

No item route or candidate code is executed. The existing Jay inverse supplies
reference symbol metadata only; every modeled Rogue CPU fetch owns raw1327.
"""
from collections import Counter
from hashlib import sha256
import argparse,json,re
from pathlib import Path
from unittest.mock import patch
from py65.assembler import Assembler
import current_jay_status_size_publication_00bb_1116 as Current

R,ROM,N,W,Frames=Current.R,Current.ROM,Current.N,Current.W,Current.Frames
PIN='13272464e34237f09c7fce87ac276b20da299f8028640cc51155759d6c642a4d'
CURRENT_SHA='ffe06f7b53421b24a07da2918b846a67a3de28469ee7eed2d7e67d42816bf8f3'
COMPOSER_SHA='7f1c0eab5a08a7a7e3fbf922aaff1a1c2b8b7513c9c3bd11ed8eee50d01e8d0c'
SOURCES={
 'rogue_dawn_host_services.s':'e43f538e3dd25b4fa0e791b549731e51d22a2ccf8e2b698fd06702599f699fa8',
 'rogue_dawn_host_items.s':'9f2730fbc953faa4c34a5e5f321a4d9d4a704c26e30ff1d3608037d9fa04af56',
 'rogue_dawn_host_items_gate.s':'2bd617636de5cb4cba9eb2571c994010da27ca85565ea7c01d8d665974199bd3',
 'rogue_dawn_host_transactions.s':'1e7c66ddaf782b198dcc8cc8c01f2bf0003bf0d0a0311c482c347d964134c63d',
 'rogue_dawn_host_lifecycle.s':'1b61f71e77495fc3c90d8b7615c39758f4d21430238e543aae97b98975fb34a0',
 'rogue_dawn_host_pipeline.s':'9d799b64cb644edd21255dc3d91f3d689a406e90144805e9d7bd534f7768caa7',
 'rogue_dawn_state.inc':'f91a3dae3adabbf8231a9c446e09e07d1ce232e352a663b48f15ed0792336134',
 'rogue_dawn_host_weapons_gate.s':'a3187b1502706579bfe39daf4522127ef07d4fadbadeff4295dc36afed888cfb',
 'rogue_dawn_core.s':'3324311bf4cde2845871aa5f3970e0222b5b76f77f64854f44b2d32ecb5cda4a'}
WEAPON_RECIPE_SHA='22678db1fe52f1c75478aaccc230c746ccbd62ccb5365fbef6eb9e9c2e2822c4'
POLICY={
 'RdHsRewardForRaw':'rogue_dawn_host_services.s',
 'RdHsPrepareActor':'rogue_dawn_host_services.s',
 'RdHsCollectActor':'rogue_dawn_host_services.s',
 'RdHsGrantType':'rogue_dawn_host_services.s',
 'RdTxPrepareActor':'rogue_dawn_host_transactions.s',
 'RdItPrepare':'rogue_dawn_host_items_gate.s',
 'RdItSyncStatus':'rogue_dawn_host_items_gate.s',
 'RdItPickup':'rogue_dawn_host_items.s',
 'RdItCollision':'rogue_dawn_host_items.s',
 'RdLifePrepareMain':'rogue_dawn_host_lifecycle.s',
 'RdLifeMovement':'rogue_dawn_host_lifecycle.s',
 'RdAddMissileTank':'rogue_dawn_core.s'}
HOOKS=('RdHostEnabled','RdControlStep','RdLifeMovement','RdTxMovement',
 'RdHsRewardForRaw','RdHsPrepareActor','RdHsCollectActor','RdHsGrantType',
 'RdItPrepare','RdItPickup','RdItCollision','RdItSyncStatus','RdLifeFresh',
 'RdLifeArea','RdWxMovementPipeline','RdAddMissileTank','RdHostInput','RdHostTickAfter','SetupPowerUp',
 'HandlePowerUpCollision','SetupFloateyNumber','MarioSourcePowerupCollision',
 'EraseEnemyObject','AddToScore','RdHostBridgeStart','RdHostBridgeEnd')


def H(data):return sha256(data).hexdigest()


def bindings(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN
    assert H(Path(Current.__file__).read_bytes())==CURRENT_SHA
    assert H(Path(Current.C.__file__).read_bytes())==COMPOSER_SHA
    b=Current.bindings(raw)['bundle'];assert b['raw']is raw
    for name,pin in SOURCES.items():assert H((R/'src'/name).read_bytes())==pin,name
    rows={}
    for name in HOOKS:
        pc,at=W.address(b,name),W.location(b,name);bank=(at-16)//8192
        rows[name]=dict(PC=pc,file=at,physical_PRG_bank=bank,tag=128+bank,
            first16=raw[at:at+16].hex(),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))
    for name in ('RdHsServices','RdLife','RdBody','RdIt','RdHostBridge'):
        lo,hi=W.location(b,name+'Start'),W.location(b,name+'End')
        assert lo<=hi
        rows[name+'Span']=dict(file_start=lo,file_end_exclusive=hi,bytes=hi-lo,SHA256=H(raw[lo:hi]))
    return b,rows


def source_bytes(b,name,source):
    """Assemble the current retained simple source procedure in memory.

    This is source reconstruction, never a CPU component invocation. The one
    genuine source-leaf farcall is expanded from its retained macro verbatim.
    """
    text=(R/'src'/source).read_text()
    match=re.search(r'^\.proc '+re.escape(name)+r'\b[^\n]*\n(.*?)^\.endproc',text,re.M|re.S)
    assert match,name
    body=match[1]
    if name=='RdLifeMovement':
        producer=R/'tools/prepare_rogue_dawn_host_weapons_v1.py'
        assert H(producer.read_bytes())==WEAPON_RECIPE_SHA
        assert "proc(proc(s,'RdLifeMovement','jsr RdTxMovement','jsr RdWxMovementPipeline')"in producer.read_text()
        assert body.count('jsr RdTxMovement')==1
        body=body.replace('jsr RdTxMovement','jsr RdWxMovementPipeline')
    lines=[]
    for line in body.splitlines():
        line=line.split(';',1)[0].strip()
        if not line:continue
        if line.startswith(('RdHsLeaf ','WxFar ','WxTail ')):
            target=line.split()[1]
            tail=line.startswith('WxTail ')
            bank=124 if line.startswith('RdHsLeaf ')else((W.location(b,target)-16)//8192)
            lines.extend(('sta SafecallA_SMC+1','lda #<'+target,'sta FarcallJmpTarget_SMC+1',
                'lda #>'+target,'sta FarcallJmpTarget_SMC+2','lda #$%02x'%(128+bank),
                ('jmp 'if tail else'jsr ')+'FarCallCommon'))
        else:lines.append(line)
    asm=Assembler(N.NesMPU());origin=W.address(b,name);labels={}
    def value(token,trial=False):
        token=token.strip();part=re.fullmatch(r'([A-Za-z_][\w:]*)((?:[+-]\d+)?)',token)
        if part:
            key,offset=part.groups()
            if key in labels:v=labels[key]
            else:
                try:v=W.address(b,key)
                except KeyError:
                    assert trial,('Missing source symbol',key,name)
                    v=origin
            return(v+int(offset or 0))&65535
        return int(token[1:],16)if token.startswith('$')else int(token)
    def instruction(line,pc,trial):
        if line.startswith('.byte '):return [value(s,trial)&255 for s in line[6:].split(',')]
        parts=line.split(None,1)
        if len(parts)==1:return asm.assemble(line,pc)
        op,operand=parts
        if operand.lower()=='a':return asm.assemble(line,pc)
        immediate=operand.startswith('#');operand=operand.lstrip('#');select=''
        if operand.startswith(('<','>')):select,operand=operand[0],operand[1:]
        indexed=operand[-2:]if operand[-2:].lower()in(',x',',y')else''
        if indexed:operand=operand[:-2]
        v=value(operand,trial)
        if select:v=(v&255)if select=='<'else(v>>8)
        rendered=op+' '+('#$%02x'%(v&255)if immediate else '$%04x'%v)+indexed
        return asm.assemble(rendered,pc)
    result=b''
    for trial in(True,False):
        pc=origin;out=[]
        for line in lines:
            label=re.match(r'^([A-Za-z_]\w*):',line)
            if label:
                if trial:labels[label[1]]=pc
                else:assert labels[label[1]]==pc
                line=line[label.end():].strip()
                if not line:continue
            chunk=instruction(line,pc,trial);out.extend(chunk);pc+=len(chunk)
        result=bytes(out)
    return result


def policy(raw,b):
    assert W.address(b,'RD_LEAF_ADD_MISSILE_TANK')==W.address(b,'RdAddMissileTank')
    rows=[]
    for name,source in POLICY.items():
        code=source_bytes(b,name,source);at=W.location(b,name)
        actual=raw[at:at+len(code)]
        assert actual==code,('Source/current mismatch',name,at,code.hex(),actual.hex())
        rows.append(dict(name=name,source=source,PC=W.address(b,name),file=at,
            bytes=len(code),SHA256=H(code),source_reassembled_byte_exact=True))
    return rows


def state(m):
    names=('SelectedCharacter','CrossoverMenuIndex','RdVariant','RdAction','RdRadiusX','RdRadiusY',
        'RdHealthLo','RdHealthHi','RdGear','RdMissiles','RdMaxMissiles','RdTanks','PlayerStatus',
        'NumberofLives','GameEngineSubroutine','CheatInvincible','CheatStartLevel','RdHeld','RdFresh')
    q={n:N.get(m,n)for n in names}
    q.update(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'))
    return q


def cold16(raw,b,hooks):
    counts=Counter();pending={};first=[]
    points={(hooks[n]['tag'],hooks[n]['PC']):n for n in('RdLifeMovement','RdControlStep')}
    def observe(m,c):
        assert m.bundle['raw']is raw
        for name,(pc,sp)in list(pending.items()):
            if(c.pc,c.sp)==(pc,sp):counts[name+'_returned']+=1;del pending[name]
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        name=points.get((tag,c.pc))
        if name:
            assert name not in pending,('Unexpected recursive worker',name)
            return_pc=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1)&65535
            pending[name]=(return_pc,(c.sp+2)&255);counts[name+'_entered']+=1
            if len(first)<4:first.append(dict(name=name,tag=tag,PC=c.pc,SP=c.sp,return_PC=return_pc,return_SP=(c.sp+2)&255))
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for bits in(1,1,32):W.UI.key(m,bits)
    menu=dict(name=W.UI.menu_name(m)[0],slot=N.get(m,'CrossoverMenuIndex'),raw=N.get(m,'SelectedCharacter'),variant=N.get(m,'RdVariant'))
    assert menu==dict(name='ROGUE DAWN',slot=2,raw=2,variant=1),menu
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True)
    else:raise AssertionError('Actual Rogue cold/Start bound')
    before=state(m);assert before['RdVariant']==1 and before['SelectedCharacter']==2
    for _ in range(16):m.controller_pad=0;Frames.frame(m,observe,whole_pass=True)
    after=state(m)
    assert not pending and counts['RdControlStep_entered']==counts['RdControlStep_returned']==16,counts
    assert counts['RdLifeMovement_entered']==counts['RdLifeMovement_returned']==16,counts
    assert after['NumberofLives']==2 and after['CheatInvincible']==after['CheatStartLevel']==0
    assert after['RdHealthLo']+256*after['RdHealthHi']>0 and after['x']==before['x']
    assert tuple(after[n]for n in('RdGear','RdMissiles','RdMaxMissiles','RdTanks','PlayerStatus'))==(0,0,0,0,0)
    return dict(actual_menu=menu,neutral_completed_host_passes=16,actual_worker_counts=dict(counts),
        first_dynamic_PC_SP_return_tokens=first,cold_passes=tick,before=before,after=after,
        no_item_route=True,no_resource_or_actor_seeds=True)


def run(raw,cold=False):
    b,hooks=bindings(raw);source=policy(raw,b)
    row=dict(passed=True,owning_SHA256=PIN,typed_reference_only_SHA256=Current.Previous.PIN,
        source_procedures=source,hooks=hooks,source_pins=SOURCES,
        metadata_installed_UI_CPU=True,actual_owning_Rogue_CPU=cold,candidate_CPU=False,
        all_four_natural_stock_families_open=True,item_route_executed=False,Mesen=False,outputs=0,
        exact_retained_weapon_recipe_SHA256=WEAPON_RECIPE_SHA,
        initial_binding_negative='Untransformed retained lifecycle source calls RdTxMovement; actual linked owner calls RdWxMovementPipeline. Exact retained producer substitution now authenticated, no game difference.')
    if cold:row['cold16']=cold16(raw,b,hooks)
    row['receipt_SHA256']=H(json.dumps(row,sort_keys=True,separators=(',',':')).encode())
    return row


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cold16',action='store_true');a=p.parse_args()
    raw=ROM.read_bytes();assert H(raw)==PIN
    row=run(raw,a.cold16)
    compact=dict(row)
    compact['hooks']={name:{k:v for k,v in item.items()if k not in('bank_SHA256','first16')}
        for name,item in row['hooks'].items()}
    compact['source_pins_count']=len(compact.pop('source_pins'))
    print(json.dumps(compact,separators=(',',':')),flush=True)
