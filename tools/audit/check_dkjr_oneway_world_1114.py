"""Finite actual World/Vine queries of proposed fragments, CPU RAM only."""
from collections import Counter
from hashlib import sha256
import itertools
import json

import check_dkjr_oneway_components_1114 as K
import check_dkjr_platform_query_lifecycle_1114 as Life

F,G=K.F,K.G
Q,P,H,N,W,L,C=K.Q,K.P,K.H,K.N,K.W,K.L,K.C


def main():
    parent,raw=F.load_inputs();proposal=K.M.fragments(raw);_,labels=Life.closure(raw)
    e73=F.T.Old.reverse(parent);_,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    C.SLOT=3;base=C.setup(Q.mounted(seed,raw));base.raw_page(1,3);base.raw_page(2,2)
    # Declared native vine actor in the actual source-format query window.
    for name,value in dict(Enemy_Flag=1,Enemy_ID=47,Enemy_State=0,
        Enemy_X_Position=944&255,Enemy_PageLoc=944>>8,Enemy_Y_Position=96,Enemy_Y_HighPos=1).items():
        base[W.address(base.bundle,name)+5]=value
    for name,value in dict(Vine_FlagOffset=1,Vine_ObjOffset=5,Vine_Height=48,Vine_Start_Y_Position=144).items():base[labels[name]]=value
    base[labels['Vine_ObjOffset']+1]=255
    base.ram[2][0x3e:0x42]=bytes((100,96,116,112))
    base.ram[2][0x6b]=1;base.ram[2][0x8ee]=0xa5
    H.call(base,0xb624)
    native=[];cases=0;counts=Counter();digest=sha256();differences=Counter()
    def call(changes,kind,p=0x61,proposed=False):
        m=L.clone(base)
        if proposed:K.overlay(m,proposal['fragments'])
        for at,value in changes:m[at]=value&255
        c=H.call(m,labels['DkjrNativeTerrainHook'],a=kind,x=71,y=91,p=p)
        assert(c.a,c.x,c.y,c.p,c.sp)==(kind,71,91,p|0x30,224),(kind,p,c.a,c.x,c.y,c.p,c.sp)
        data=bytearray(m.ram[2][:0x900]);data[0x8ee]=0
        return m,(c.a,c.x,c.y,c.p,c.sp,bytes(data),bytes(m[0x200:0x800]))
    def exact(changes,kind,p=0x61,category='vine'):
        nonlocal cases
        a,old=call(changes,kind,p,False);b,new=call(changes,kind,p,True)
        if old!=new:
            bad=[hex(0xc000+i)for i,(x,y)in enumerate(zip(old[5],new[5]))if x!=y]
            raise AssertionError((category,kind,p,changes,bad,old[:5],new[:5]))
        cases+=1;counts[category]+=1;digest.update(new[5][0x800:0x8c0])
        if a.ram[2][0x8ee]!=b.ram[2][0x8ee]:differences['dead_WScreenHi']+=1
        if cases%500==0:print('DKJR_WORLD_PROGRESS '+json.dumps(dict(exact_pairs=cases)),flush=True)
    for flag,kind in itertools.product(range(256),(0,1)):
        exact([(labels['Vine_FlagOffset'],flag)],kind)
    for height,flag,kind in itertools.product(range(256),(1,2),(0,1)):
        exact([(labels['Vine_FlagOffset'],flag),(labels['Vine_Height'],height)],kind)
    for p in range(256):exact([],0,p,category='all_P_V1_ABI')
    variations=[]
    for name,values in dict(Enemy_Flag=(0,1,127,128,255),Enemy_ID=(0,36,37,40,44,45,46,47,48,255),
        Enemy_Y_HighPos=(0,1,2,255),Enemy_Y_Position=(0,31,32,96,127,239,240,255),
        Enemy_PageLoc=(0,2,3,4,255),Enemy_X_Position=(0,15,16,127,176,247,248,255)).items():
        variations.extend((name,[(W.address(base.bundle,name)+5,value)])for value in values)
    for offset,second in itertools.product((0,3,4,5,6,255),(0,5,255)):
        variations.append(('vine_stack_roots',[(labels['Vine_ObjOffset'],offset),(labels['Vine_ObjOffset']+1,second),(labels['Vine_FlagOffset'],2)]))
    for name,changes in variations:
        for kind in(0,1):exact(changes,kind,category=name)
    for source,kind,acc in itertools.product((1,2,3,4,5),range(5),(0,352,600)):
        if source==3 and acc<352:continue
        exact([(0xc06b,source),(0xc082,acc&255),(0xc083,acc>>8),(0xc086,96),(0xc087,1)],kind,category='nonrising_all_kinds_states')
    # The intended change: while source3 is truly rising, an actual published
    # actor top plane is removed, and the same static-tile support remains.
    supported=0
    for kind,acc in itertools.product((3,4),(0,8,88,200,328,351)):
        changes=[(0xc06b,3),(0xc082,acc&255),(0xc083,acc>>8),(0xc086,96),(0xc087,1)]
        window=(96,136,128,136 if kind==3 else 144)
        changes.extend((0xc03e+i,value)for i,value in enumerate(window))
        with_actor,old=call(changes,kind,0x61,False)
        proposed,new=call(changes,kind,0x61,True)
        # Declared diagnostic control disables only the actor flag; this is
        # output equivalence of static terrain, not a gameplay qualification.
        control,static=call(changes+[(W.address(base.bundle,'Enemy_Flag')+3,0)],kind,0x61,False)
        assert old[5][0x800:0x8c0]!=new[5][0x800:0x8c0],('No intended plane removal',kind,acc,
            list(with_actor.ram[2][0x8da:0x8f0]),list(with_actor[0x668:0x66c]),
            list(with_actor.ram[2][0x800:0x810]),list(with_actor.ram[2][0x3e:0x42]))
        assert new[5][0x800:0x8c0]==static[5][0x800:0x8c0],('Static support changed',kind,acc)
        supported+=1
    print('DKJR_ONEWAY_WORLD '+json.dumps(dict(passed=True,parent_SHA256=F.T.PIN,
        exact_World_query_pairs=cases,category_counts=dict(counts),all256_flags_heights_and_P=True,
        exact_source_data_lists_native_data_AXYP_SP=True,allowed_dead_scratch_differences=dict(differences),
        rising_actor_plane_removed_static_support_preserved=supported,aggregate_SHA256=digest.hexdigest(),
        outputs_written=0,ROM_composed=False,
        scope='Declared current World/Vine and support-query fixtures, proposed fragments overlaid only into CPU RAM after cold. Kind4 is an extra manual ABI fixture; legal ingress and age0 scope remain the separate lifecycle proof. Not full Main/ISR/cold/native qualification.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
