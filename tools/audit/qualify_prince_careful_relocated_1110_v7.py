"""Actual vectors at the final funded careful132 and compact PointRead PCs."""
import json
import check_prince_wall_sweep_1110_v6 as V
import qualify_prince_careful_support_1110_v5 as Previous
import check_prince_climb_funded_irq_1109_v2 as Async


def main():
    result=V.proposal();seed,_=V.Q.actual_cold(result[1],result[2],result[3],result[4]);rows=[]
    for mode,kind in ((1,'cap'),(255,'cap'),(255,'empty')):
        m=Previous.fixture(seed,mode=mode,kind=kind)
        rows.append(Async.stress('final careful mode'+str(mode)+' '+kind,m,
            lambda q:V.I.invoke(q,3,0xd6d1,(83,71,109,0x61))['regs'],
            [(2,0xd6d1,0xd755),(3,0xb310,0xb369)]))
    print('CAREFUL_FINAL_VECTORS '+json.dumps(dict(SHA256=result[3]['in_memory_SHA256'],
        source132_same_as_v5=True,results=rows,outputs_written=0),separators=(',',':')),flush=True)


if __name__=='__main__':main()
