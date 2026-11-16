"""Detached Rogue2B over leased Mini9826: exact bytes/provenance, no CPU."""
from pathlib import Path
from hashlib import sha256
import json
import compose_mini_weapon_owner_a2_1116 as Mini
import compose_sonic_ceiling_complete_1327_1116 as Sonic
import compose_rogue_missile_dispatch_1327_1116 as Rogue
import check_ff_white_mushroom_current_1110 as W

R,ROM,H=Rogue.R,Rogue.ROM,Rogue.H
PINS={Mini:'c644e50735327826d2f6de932954d501283ca963b4fc12d8408ae75519750a8c',
 Sonic:'c4456eb759fd35f48022fee64a24b05e37b4968a1ddaf139dceebad154187413',
 Rogue:'3b4b914ff59acb3f7779cd1f8237289664ce13e83578245f9db8b0fb1fb84a14'}
CONSUMERS={
 'missile':dict(path='replay_rogue_earned_missile54b_1116.py',factory='a1f9a70d72e839c4393818a271cd7a6f0be7a78b2c3ea2dae0e90d8937dc3cec',lua='ff662f77a42b60e6136b9d1c9b8259c412dbfbaa24e9ad3e4e8e9e553abaaee2'),
 'full11':dict(path='replay_rogue_full11_54b_1116.py',factory='045fd3a05cce718c21e84599599abbb0c644d741a7a1756b96bf7a2e1a5692ed',lua='1555f19bc2fd6d92c12d4364d7cb7c021d184981f438eb4184038a3745778114')}


def predicted(raw):
    h=sha256();h.update(raw[:Rogue.AT]);h.update(Rogue.NEW);h.update(raw[Rogue.AT+2:]);return h.hexdigest()


def descriptor(raw9826):
    for mod,pin in PINS.items():assert H(Path(mod.__file__).read_bytes())==pin
    Mini.lease();Rogue.lease();assert H(raw9826)==Mini.CANDIDATE
    rawa2=Mini.inverse(raw9826);base=Sonic.inverse(rawa2);assert H(base)==Rogue.PIN
    ro=set(range(Rogue.AT,Rogue.AT+2));mi={i for at,old,_ in Mini.SPANS for i in range(at,at+len(old))}
    so={i for at,old,_ in Sonic.spans()for i in range(at,at+len(old))}
    assert(len(ro),len(mi),len(so))==(2,20,94)and not(ro&mi or ro&so or mi&so)
    assert raw9826[Rogue.AT:Rogue.AT+2]==Rogue.OLD
    for at,old,new in Mini.SPANS:assert raw9826[at:at+len(new)]==new
    for at,old,new in Sonic.spans():assert raw9826[at:at+len(new)]==new
    # Only tiny read-only hook fragments are projected; no compound game image
    # or CPU is constructed. All real owning execution awaits a new lease.
    def project(raw,at,size):
        q=bytearray(raw[at:at+size])
        for i,v in enumerate(Rogue.NEW):
            if at<=Rogue.AT+i<at+size:q[Rogue.AT+i-at]=v
        return bytes(q)
    b=W.Symbols.bundle();names=('GameLoop','RdControlStep','RdControlDispatch','RdLifeMovement',
        'HandlePowerUpCollision','RdHsCollectActor','RdHsGrantType','RdItPickup','RdItPrepare','AddToScore',
        'RdWxSpawn','RdWxUpdateSlot','RdWxCell','RdWxMove','RdAnimateProjectile','RdWpRender',
        'SetupFloateyNumber','EraseEnemyObject','PlayerHeadCollision','DecNumTimer','FlagpoleRoutine')
    hooks={}
    for name in names:
        at=W.location(b,name);pc=W.address(b,name);bank=(at-16)//8192
        current=raw9826[at:at+32];old_versioned=project(base,at,32);proposed=project(raw9826,at,32)
        assert proposed==old_versioned,(name,'Hook changed outside own2B')
        hooks[name]=dict(PC=pc,file=at,bank=bank,current_preimage=current.hex(),projected_preimage=proposed.hex(),
            exact_versioned54b_preimage=True,overlaps_own_operand=bool(set(range(at,at+32))&ro),
            parent9826_bank_SHA256=H(raw9826[16+bank*8192:16+(bank+1)*8192]),
            reference1327_bank_SHA256=H(base[16+bank*8192:16+(bank+1)*8192]))
    at=W.location(b,'IdleLoop');pc=W.address(b,'IdleLoop');call=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    returns=[i+3 for i in range(61)if raw9826[at+i:at+i+3]==call];assert len(returns)==2 and returns[0]==12
    for i,delta in enumerate(returns):
        assert raw9826[at+delta:at+delta+8]==base[at+delta:at+delta+8]
        hooks['GameLoopReturn'+str(i)]=dict(PC=pc+delta,file=at+delta,preimage=raw9826[at+delta:at+delta+8].hex(),unchanged=True)
    for item in CONSUMERS.values():assert H((R/'tools/audit'/item['path']).read_bytes())==item['factory']
    for bank in(94,95,121,124):assert raw9826[16+bank*8192:16+(bank+1)*8192]==base[16+bank*8192:16+(bank+1)*8192]
    result=dict(passed=True,detached_only=True,parent_SHA256=Mini.CANDIDATE,parent_a2_SHA256=Mini.PARENT,
        reference1327_SHA256=Rogue.PIN,versioned54b_SHA256=Rogue.CANDIDATE,predicted_SHA256=predicted(raw9826),
        spans=[dict(file=Rogue.AT,bytes=2,old_hex=Rogue.OLD.hex(),new_hex=Rogue.NEW.hex())],
        owned_bytes=2,changed_bytes=1,Sonic94_and_Mini20_exact_disjoint=True,
        total_union_owned_over1327=116,total_union_changed_over1327=112,
        native_Rogue_banks94_95_121_124_exact_parent=True,cookies_headers_art_helpers_proposed_changes=0,
        consumer_bindings=CONSUMERS,hooks=hooks,
        transfer_scope=['Unchanged action/classifier and all255 non11 paths;510 fullcaller comparisons',
         'Exact same native121 fragment and source leaves;22IRQ+22busyNMI component proof',
         'GenuineMF/motion/offscreen/expiry25 and full1-1/grounded25 policies remain frozen'],
        remaining_owning_gates=['NEW strict9826 composer/inverse/facade; old APIs stay strict',
         'Execute actual new owning image cold and production callback; update only config/hash pins',
         'Preserve fullSonic94 andMini20 runtime/cookie/auth contexts; meaningful foreign/public continuation',
         'Current source full-stage endpoint and root-only native/private/delivery review'],
        game_CPU=False,metadata_UI_CPU=False,compound_Rogue_image_composed=False,
        leased_Mini9826_input_may_be_composed_in_memory=True,outputs=0,native=False)
    result['receipt_SHA256']=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    actual=ROM.read_bytes();pin=H(actual)
    if pin==Mini.PARENT:raw=Mini.proposal(actual)[0]
    else:assert pin==Mini.CANDIDATE;Mini.inverse(actual);raw=actual
    result=descriptor(raw);result['actual_input_SHA256']=pin
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
