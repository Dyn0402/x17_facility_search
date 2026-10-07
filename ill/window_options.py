"""Entrance-window candidates on the H113 cold beam: captures per beam neutron by gamma line, scattering."""
NA=6.022e23
LAM=4.87; F=LAM/1.798          # 1/v factor vs 2200 m/s (beam mean λ, he4_bag)
# element: (sigma_abs thermal b, hardest capture gamma MeV, sigma_scatter cold b (bound/solid, approx))
EL={'H':(0.3326,2.22,110.),'C':(0.0035,4.95,5.0),'O':(0.00019,4.14,4.2),'N':(1.91,10.83,11.),
    'Be':(0.0076,6.81,None),'Al':(0.231,7.72,1.5),'F':(0.0096,6.60,4.0),'Si':(0.171,8.47,2.2)}
N_NG=0.075  # 14N (n,gamma) part of 1.91 b
MAT={ # name: (density, {el: atoms per formula}, molar mass)
 'Be':(1.848,{'Be':1},9.012),
 'Al':(2.699,{'Al':1},26.98),
 'Mylar (PET)':(1.39,{'C':10,'H':8,'O':4},192.2),
 'Kapton':(1.42,{'C':22,'H':10,'N':2,'O':5},382.3),
 'PEEK':(1.32,{'C':19,'H':12,'O':3},288.3),
 'graphite/CVD diamond':(2.2,{'C':1},12.011),
}
BE_SCAT=0.003/0.05   # Geant: 0.5 mm Be scatters ~0.3 % of the beam (SIM_STATUS)
cases=[('Be',0.5),('Be',0.25),('Be',0.1),('Al',0.1),('Mylar (PET)',0.025),('Mylar (PET)',0.05),('Kapton',0.05),('PEEK',0.05),('graphite/CVD diamond',0.1)]
print(f"{'window':24s} {'t':>6s} | {'hard (>5 MeV) capt/n':>20s} {'line':>6s} | {'soft capt/n':>11s} | {'scatter':>7s}")
for m,t_mm in cases:
    rho,form,M=MAT[m]; t=t_mm/10
    nform=rho/M*NA
    hard=soft=sc=0; hl=0
    for el,k in form.items():
        sa,g,ss=EL[el]; n=nform*k
        sa_ng = N_NG if el=='N' else sa
        p=n*sa_ng*1e-24*F*t
        if g>5: hard+=p; hl=max(hl,g)
        else: soft+=p
        if ss: sc+=n*ss*1e-24*t
    if m=='Be': sc=BE_SCAT*t
    print(f"{m:24s} {t_mm:5.3f}mm | {hard:20.2e} {hl:6.2f} | {soft:11.2e} | {sc*100:6.2f}%")
