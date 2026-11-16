"""Owning native life-writer instructions; no CPU/gameplay or packet mounts."""
from pathlib import Path
from hashlib import sha256
from unittest.mock import patch
import json
import current_bowser_stock_bc5_1115 as Current

def run(raw):
    b=Current.bundle(raw);life=Current.W.address(b,'NumberofLives');rows=[]
    names=[n for n in b['syms']if'::'not in n and('LoseLife'in n or'GiveOneCoin'in n or'TransposePlayersCore'in n or n=='FloateyNumbersCore')]
    for name in sorted(names):
        pc=Current.W.address(b,name)
        if pc<0x8000:continue
        at=Current.W.location(b,name);part=raw[at:at+160];writes=[]
        for op,label in((0xce,'DEC'),(0xee,'INC'),(0x8d,'STA')):
            pattern=bytes((op,life&255,life>>8));start=0
            while True:
                delta=part.find(pattern,start)
                if delta<0:break
                writes.append(dict(operation=label,PC=pc+delta,file=at+delta,bytes=part[delta:delta+8].hex()));start=delta+1
        row=dict(name=name,PC=pc,file=at,first8=part[:8].hex(),writer_candidates=writes)
        if name=='PlayerLoseLife':
            assert part[:3]==bytes.fromhex('8d6a01')and part[3]==part[8]==part[13]==0xa9
            assert part[5:8]==bytes.fromhex('8d6c01')and part[10:13]==bytes.fromhex('8d6d01')
            target=part[4]+256*part[9];tag=part[14];assert tag&128
            target_at=16+(tag&127)*8192+(target&8191);child=raw[target_at:target_at+min(160,8192-(target&8191))]
            pattern=bytes((0xce,life&255,life>>8));delta=child.find(pattern)
            assert delta>=0 and part[18]==0x10,('Actual death DEC and returned caller BPL',part[:48].hex(),child[:48].hex(),delta)
            assert child.find(bytes((0x68,0x28,0xad,life&255,life>>8,0x60)))>=0,'Death leaf restores flags then returns actual life byte'
            row['authenticated_far_target']=dict(PC=target,bank=tag&127,file=target_at,stub=part[:18].hex(),
                DEC_PC=target+delta,DEC_file=target_at+delta,DEC_leaf_bytes=child[delta:delta+22].hex(),
                caller_BPL_PC=pc+18,caller_after_far_return=part[18:34].hex())
        rows.append(row)
    sources={}
    for name in('src/player.s','src/game.s','src/screen_render.s','src/bill_native_rare.s','src/sunny.s'):
        sources[name]=sha256((Current.R/name).read_bytes()).hexdigest()
    q=dict(passed=True,ROM_SHA256=Current.PIN,owning_named_native_life_paths=rows,source_inputs=sources,
        domain='Gameplay life credits use native INC; death uses native DEC with BPL/game-over underflow; fresh setup and player swaps are construction paths',
        scope='Read-only named-path instruction/source census, not arbitrary raw alias closure or gameplay',outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest();return q

if __name__=='__main__':
    raw=Current.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Native writer census attempted output/native')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
