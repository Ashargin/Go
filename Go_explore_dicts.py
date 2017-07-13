import marshal
N=2
version='v1'
n_sim_min=5000
afficher_détails='oui'
if version=='v1' :
    D=marshal.load(open('train_v1_'+str(N),'rb'))
elif version=='v2' :
    D=marshal.load(open('train_v2_'+str(N),'rb'))
D2={}
Pos={}
for i in range(1,N**2) :
    D2[i]={}
    Pos[i]=0
for i in D :
    P=i[0]
    res=D[i]
    n_win=res[0]
    n_tot=res[1]
    n=0
    for j in range(N) :
        for k in range(N) :
            if P[j][k]>0 :
                n=n+1
    Pos[n]=Pos[n]+1
    if n_tot in D2[n] :
        D2[n][n_tot]=D2[n][n_tot]+1
    else :
        D2[n][n_tot]=1
for n in D2 :
    c=0
    c2=0
    print('Pour '+str(n)+' cases occupées :')
    for n_tot in D2[n] :
        p=n_tot*D2[n][n_tot]
        c=c+p
        if n_tot<n_sim_min :
            c2=c2+p
    if afficher_détails=='oui' :
        for n_tot in D2[n] :
            print(str(n_tot)+' itérations : '+str(100*n_tot*D2[n][n_tot]/c)+'%).')
    print(' ')
    print('Moins de '+str(n_sim_min)+' itérations : '+str(100*c2/c)+'%.')
    print('Positions évaluées : '+str(Pos[n]))
    print(' ')
