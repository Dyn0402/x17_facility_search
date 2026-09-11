import numpy as np
mn=939.5654; m3=2808.3913; m4=3727.3794; mX=16.8; me=0.51099895
Sn=mn+m3-m4
print("S_n (Q-value) = %.4f MeV"%Sn)
print("%6s %10s %10s %10s %10s %10s %10s %10s"%("En","sqrt(s)","E*","dE* exact","3/4En","beta_cm","EX_cm","theta_min"))
for En in [0.0,0.025e-6,0.2,0.5,1.0,2.0,5.0,14.0,20.0,40.0]:
    Etot=mn+En+m3
    pn=np.sqrt((mn+En)**2-mn**2)
    s=Etot**2-pn**2
    W=np.sqrt(s)
    Estar=W-m4
    beta=pn/Etot
    # X17 emission in 4He* rest frame
    EX=(W**2+mX**2-m4**2)/(2*W)
    pX=np.sqrt(max(EX**2-mX**2,0))
    thmin=2*np.degrees(np.arcsin(min(mX/EX,1)))
    print("%6.3f %10.3f %10.4f %10.4f %10.4f %10.5f %10.4f %10.2f"%(En,W,Estar,Estar-Sn,0.75*En,beta,EX,thmin))

print("\n--- size of the two effects on the X17 lab energy ---")
for En in [0.2,1.0,2.0]:
    Etot=mn+En+m3; pn=np.sqrt((mn+En)**2-mn**2); W=np.sqrt(Etot**2-pn**2)
    beta=pn/Etot
    EX=(W**2+mX**2-m4**2)/(2*W); pX=np.sqrt(EX**2-mX**2)
    g=1/np.sqrt(1-beta**2)
    dboost=g*beta*pX
    print("En=%4.1f: E* shift = +%.3f MeV ; max boost shift of E_X = +-%.3f MeV ; p_X(cm)=%.2f"%(
        En, W-m4-Sn, dboost, pX))

print("\n--- theta_min vs En (the observable that moves) ---")
for En in [0.0,0.2,0.5,1.0,1.5,2.0,3.0,5.0]:
    Etot=mn+En+m3; pn=np.sqrt((mn+En)**2-mn**2); W=np.sqrt(Etot**2-pn**2)
    EX=(W**2+mX**2-m4**2)/(2*W)
    print("  En=%4.1f MeV -> E*=%7.3f -> theta_min=%6.2f deg"%(En,W-m4,2*np.degrees(np.arcsin(mX/EX))))
