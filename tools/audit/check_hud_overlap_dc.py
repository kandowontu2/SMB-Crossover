"""Compare real compiled numeric producers with foreign writes before/after."""
from pathlib import Path
import hashlib,importlib.util,json,traceback
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'hud-foreign-overlap-dd'
p=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py';spec=importlib.util.spec_from_file_location('hud_dc_model',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def at(ad):return ad if ad<2048 else ad-0x6000+2048
def put(im,raw,name,value,i=0):raw[at(im.ram[name]+i)]=value
def call(im,raw,name,A=0):
    raw=bytearray(raw);hook=im.hook(name);bank=hook['physical_bank']
    put(im,raw,'CurrentBank',bank|(128 if im.mapper==5 else 0))
    raw[0x1ef]=0xff;raw[0x1f0]=0x5c
    return m.execute(im,raw,[A,17,99,1,238],{0x8000:62,0xa000:bank,0xc000:12,0xe000:63},hook['address'],0x5d00,240)
def append(im,raw,data):
    raw=bytearray(raw);off=raw[at(im.ram['VRAM_Buffer1_Offset'])]
    for i,value in enumerate(data+[0]):put(im,raw,'VRAM_Buffer1',value,off+i)
    put(im,raw,'VRAM_Buffer1_Offset',off+len(data));return raw
def packets(im,raw):
    off=raw[at(im.ram['VRAM_Buffer1_Offset'])];return list(raw[at(im.ram['VRAM_Buffer1']):at(im.ram['VRAM_Buffer1'])+off+1])
def physical(address):
    address&=0x3fff
    if 0x2000<=address<0x3f00:
        address=0x2000+(address-0x2000)%0x1000
        return 0x2000+((address-0x2000)&0x7ff)
    return address
def output(data):
    image={};i=0
    while data[i]:
        address=(data[i]<<8|data[i+1])&0x3fff;length=data[i+2];count=length&63;inc=32 if length&128 else 1
        assert count>0;i+=3
        for j in range(count):image[physical(address+j*inc)]=data[i if length&64 else i+j]
        i+=1 if length&64 else count
    assert i==len(data)-1
    return image
def main():
    assert not O.exists();O.mkdir();report=dict(status='REVIEWING',groups=[],goal_complete=False)
    snapshot=R/'build/roster-through-2-2/specialist-h-rygar-hud-ac-candidate-mmc3-7-v0-mmc3/live-queue-consumer-1.ram'
    fixtures={'partial-score':[0x20,0x63,1,9],'exact-score':[0x20,0x62,6,9,9,9,9,9,9],
        'vertical-score':[0x20,0x43,0x82,9,9],'mirrored-score':[0x28,0x63,1,9],
        'partial-coins':[0x20,0x6e,1,9],'nonoverlap':[0x20,0x90,3,9,8,7],'palette':[0x3f,0x11,3,0x16,0x30,0x27]}
    try:
        for mapper in('mmc3','mmc5'):
            ims=[m.q.Image(R/'build'/f'smb-crossover-{mapper}.nes'),m.q.Image(V/'hud-current-cy/source/build'/f'smb-crossover-{mapper}.nes')]
            group=dict(mapper=mapper,ROMs=[sha(im.path)for im in ims],cases=[]);report['groups'].append(group)
            for name,foreign in fixtures.items():
                for order in('before','after'):
                    qs=[]
                    for candidate,im in enumerate(ims):
                        raw=bytearray(snapshot.read_bytes());assert len(raw)==10240
                        for seg in im.segs.values():
                            if seg['name']=='SMCCODE':raw[seg['start']:seg['start']+seg['size']]=im.raw[seg['ooffs']:seg['ooffs']+seg['size']]
                        for n,value in dict(VRAM_Buffer1_Offset=0,VRAM_Buffer1=0,ObjectOffset=1,SelectedCharacter=7,CheatInvincible=0,CheatStartLevel=0,NmiDisable=255).items():put(im,raw,n,value)
                        if candidate:put(im,raw,'HudStatusPending',0)
                        for n,values in [('Player1ScoreDisplay',[0,0,1,2,5,0]),('Player1CoinDisplay',[1,4]),('TopScoreDisplay',[0,0,0,9,9,9]),('GameTimerDisplay',[3,8,6])]:
                            for i,value in enumerate(values):put(im,raw,n,value,i)
                        if order=='before':raw=append(im,raw,foreign)
                        q=call(im,raw,'UpdateNumber',0x02);raw=q['ram']
                        if order=='after':raw=append(im,raw,foreign)
                        if candidate:
                            assert raw[at(im.ram['HudStatusPending'])]==10
                            q=call(im,raw,'HudFlushPending');raw=q['ram'];assert raw[at(im.ram['HudStatusPending'])]==0
                        qs.append(packets(im,raw))
                    images=list(map(output,qs));difference=[dict(address=hex(ad),expected=images[0].get(ad),actual=images[1].get(ad))for ad in sorted(set(images[0])|set(images[1]))if images[0].get(ad)!=images[1].get(ad)]
                    group['cases'].append(dict(foreign=name,order=order,equal=not difference,difference=difference,old_queue=qs[0],candidate_queue=qs[1]))
            print(mapper,'differences',sum(not z['equal']for z in group['cases']),'/',len(group['cases']),flush=True)
        # Positive controls: unrelated writes and foreign-before-numeric order.
        assert all(z['equal']for g in report['groups']for z in g['cases']if z['foreign']in('nonoverlap','palette'))
        assert all(not z['equal']for g in report['groups']for z in g['cases']if z['order']=='after'and z['foreign']in('partial-score','vertical-score','partial-coins','mirrored-score'))
        report.update(status='CONFIRMED_PRIVATE_DEFERRED_HUD_FOREIGN_ORDER_DEFECT_NOT_ADOPTED',snapshot_sha256=sha(snapshot),
            conclusion='The native busy guard alone is insufficient. Deferred numeric packets are appended after foreign writes that originally followed them. Exact target compaction also cannot identify numeric versus foreign producers. Preserve packet ordering before adopting any deferred implementation.',
            next_design='Queue full-size marked numeric placeholders at each original request position, coalesce only older marked placeholders of the same target when a later numeric request supersedes them, then fill digits in place before publication. Validate marker ownership, capacity, original queue consumers, direct callers and nested interrupts before any implementation is admitted.')
    except Exception as error:report.update(status='HARNESS_OR_REVIEW_FAILURE_RETAINED',error=repr(error),traceback=traceback.format_exc());raise
    finally:(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
