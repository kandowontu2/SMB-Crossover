; User-selected ordinary enemy contact policy, retained across gameplay resets.
; 0=BEHAVIOR1.0 (native descending stomp); 1=BEHAVIOR2.02 (source roster rules).
; This does not bypass GuestBodyContactBridge, hazard/water checks or injury.
.pushseg
.segment "SRAM"
CrossoverBehaviorVersion: .res 1
.popseg
