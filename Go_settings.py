##Importations
import copy #pour les deepcopies
import marshal #pour les sauvegardes locales
from random import* #pour les tests aléatoires
import time

##Class settings
class settings : ###création de la classe settings pour l'attribution des variables utiles pour l'IA. Les autres variables qui ne servent qu'au joueur, le côté du joueur et le handicap, sont saisies au début de Go_main.py###
    def __init__(self,N) :
        self.N=N #taille du goban
        P=[[0 for i in range(N)] for j in range(N)]
        self.P=P #matrice d'état du plateau : 0 pour vide, 1 pour noir, 2 pour blanc
        self.Pos=[copy.deepcopy(P)] #liste des positions P déja atteintes (pour la règle du ko)
        self.Chaines={} #les chaînes formées. Chaines est construite de cette manière (IMPORTANT) : c'est un dictionnaire qui à chaque case (i,j) du plateau associe [[libertés de la chaîne], case_1_de_la_chaîne, ..., dernière_case_de_la_chaîne]. Par exemple, pour une chaîne de 2 cases avec (1,1) et (1,2), Chaîne={(1, 1): [[(2, 1), (2, 2), (1, 3)], (1, 1), (1, 2)], (1, 2): [[(2, 1), (2, 2), (1, 3)], (1, 1), (1, 2)]}
        self.Cases=[(i+1,j+1) for i in range(N) for j in range(N)] #cases vides
        self.Komi={2: 1.5, 3: 8.5, 4: 2.5, 5: 24.5, 6: 4.5, 7: 9.5, 8: 7.5, 9: 7.5, 10: 7.5, 11: 7.5, 12: 7.5, 13: 7.5, 14: 7.5, 15: 7.5, 16: 7.5, 17: 7.5, 18: 7.5, 19: 7.5} #valeur du komi selon la taille du goban en area scoring

##Structures des coups
def coup_humain(var,humain) : ###structure du coup du joueur humain###
    test=1
    for case in var.Cases :
        if est_valide(var,case,humain)[0]==True :
            test=0
    if test==1 : #il n'y a aucun coup possible
        ans='Passer'
        print('Pas de coup possible.')
        var.Cases=[]
    else :
        print('Coup?') #on demande le coup voulu
        error_check=1
        while error_check!=0 : #on vérifie si le coup est possible
            coup_str=input()
            error_check=0
            Coups_comprehensibles=[str((i+1,j+1)).replace(' ','') for i in range(var.N) for j in range(var.N)]+['Passer']+['passer'] #coups compréhensibles
            if coup_str not in Coups_comprehensibles : #le coup est-il compris?
                error_check=1
                print('Coup non reconnu. Saisir le coup une nouvelle fois.')
            elif coup_str not in ('Passer','passer') : #le coup est compris et le joueur ne passe pas
                i=int(coup_str[1])
                j=int(coup_str[3])
                valide=est_valide(var,(i,j),humain) #fonction est_valide en bas (partie 1 du coup)
                if (i,j) not in var.Cases : #case déja occupée
                    error_check=1
                    print('Case déja occupée. Choisir une autre case.')
                elif valide[0]==False : #le coup n'est PAS valide (False)
                    error_check=1
                    print(valide[4])
        if coup_str in ('Passer','passer') : #le coup est valide et le joueur a passé
            ans='Passer'
            var.Cases=[] #la partie s'arrête
        else : #le coup est valide et le joueur n'a pas passé
            ans=(i,j)
            jouer_coup(var,valide,ans,humain) #fonction jouer_coup en bas (partie 2 du coup)
    return(ans)

def coup_IA_alea(var,IA) : ###structure du coup de l'IA (joue aléatoirement)###
    Cases_copy=[k for k in var.Cases] #copie pour tester les cases valides sans modifer var.Cases
    n=int(random()*len(Cases_copy)) #case aléatoire
    coup=Cases_copy[n]
    valide=est_valide(var,coup,IA) #fonction est_valide en bas (partie 1 du coup)
    while valide[0]==False and len(Cases_copy)>=2 : #si la case n'est pas valide et s'il en reste, on en reprend une autre
        Cases_copy.remove(coup) #on enlève le coup non valide pour ne pas le reprendre
        n=int(random()*len(Cases_copy)) #et on en reprend un
        coup=Cases_copy[n]
        valide=est_valide(var,coup,IA) #fonction est_valide en bas (partie 1 du coup)
    if valide[0]==False : #si aucun coup n'est valide
        ans='pas de coup possible.'
        var.Cases=[] #la partie s'arrête
    else : #si le coup est valide
        ans=coup
        jouer_coup(var,valide,ans,IA) #fonction jouer_coup en bas (partie 2 du coup)
    return(ans)

def coup_IA_semialea(var,IA,D_prev,seuil) : ###structure du coup de l'IA semi-aléatoire (sert pour l'entraînement en versions v2 et plus)###
    Value=[] #liste des "valeurs" des coups (% de victoire estimé après ce coup)
    Cases_valides=[]
    for k in range(len(var.Cases)) :
        coup=var.Cases[k]
        valide=est_valide(var,coup,IA) #fonction est_valide en bas (partie 1 du coup)
        if valide[0]==True : #si le coup est valide, on prend sa "value"
            Cases_valides.append(coup)
            var_copy=copy.deepcopy(var)
            jouer_coup(var_copy,valide,coup,IA)  #fonction jouer_coup en bas (partie 2 du coup)
            if indice(var_copy.P,3-IA) in D_prev :
                (n_win,n_tot)=D_prev[indice(var_copy.P,3-IA)]
                value_coup=1-n_win/n_tot
                Value.append(value_coup)
            else :
                Value.append(-1)
        else :
            Value.append(-1)
    M=max(Value)
    if Cases_valides==[] : #si aucun coup n'est valide
        ans='pas de coup possible.'
        var.Cases=[] #la partie s'arrête
    elif M==-1 : #s'il n'y a pas eu de tests pour cette position
        n=int(random()*len(Cases_valides)) #case aléatoire
        ans=Cases_valides[n]
        valide=est_valide(var,ans,IA) #fonction est_valide en bas (partie 1 du coup)
        jouer_coup(var,valide,ans,IA) #fonction jouer_coup en bas (partie 2 du coup)
    else : #s'il y a un coup valide qui a été testé
        Coups_corrects=[]
        for k in range(len(var.Cases)) :
            if Value[k]>=seuil*M :
                Coups_corrects.append(var.Cases[k])
        n=int(random()*len(Coups_corrects)) #case aléatoire parmi les coups corrects
        ans=Coups_corrects[n]
        valide=est_valide(var,ans,IA) #fonction est_valide en bas (partie 1 du coup)
        jouer_coup(var,valide,ans,IA) #fonction jouer_coup en bas (partie 2 du coup)
    return(ans)

def coup_IA(var,IA,D) : ###structure du coup de l'IA (joue à partir des tests contenus dans D)###
    meilleur_coup='' #meilleur coup retenu
    value=-1 #"valeur" de ce coup (% de victoire estimé après ce coup)
    Cases_valides=[]
    for k in range(len(var.Cases)) :
        coup=var.Cases[k]
        valide=est_valide(var,coup,IA) #fonction est_valide en bas (partie 1 du coup)
        if valide[0]==True : #si le coup est valide, on prend sa "value"
            Cases_valides.append(coup)
            var_copy=copy.deepcopy(var)
            jouer_coup(var_copy,valide,coup,IA)  #fonction jouer_coup en bas (partie 2 du coup)
            if indice(var_copy.P,3-IA) in D :
                (n_win,n_tot)=D[indice(var_copy.P,3-IA)]
                value_coup=1-n_win/n_tot
                if value_coup>value :
                    value=value_coup
                    meilleur_coup=coup
    if Cases_valides==[] : #si aucun coup n'est valide
        ans='pas de coup possible.'
        var.Cases=[] #la partie s'arrête
    elif meilleur_coup=='' : #s'il n'y a pas eu de tests pour cette position
        n=int(random()*len(Cases_valides)) #case aléatoire
        ans=Cases_valides[n]
        valide=est_valide(var,ans,IA) #fonction est_valide en bas (partie 1 du coup)
        jouer_coup(var,valide,ans,IA) #fonction jouer_coup en bas (partie 2 du coup)
    else : #s'il y a un coup valide qui a été testé
        ans=meilleur_coup
        valide_meilleur=est_valide(var,ans,IA) #fonction est_valide en bas (partie 1 du coup)
        jouer_coup(var,valide_meilleur,ans,IA) #fonction jouer_coup en bas (partie 2 du coup)
    return(ans)

def coup_IA_comp(var,IA,D,D_comp) : ###structure du coup de l'IA plus rapide (avec le dictionnaire compressé)###
    if indice(var.P,IA) in D_comp :
        ans=D_comp[indice(var.P,IA)]
        if ans=='pas de simulations' :
            ans=coup_IA(var,IA,D)
        elif ans=='pas de coup possible.' :
            var.Cases=[] #la partie s'arrête
        else : #ans est un coup
            valide=est_valide(var,ans,IA) #fonction est_valide en bas (partie 1 du coup)
            if valide[0]==False : #il faut revérifier la validité du coup (D_comp ne vérifie pas la règle du ko/superko car il n'a pas les positions précédentes)
                ans=coup_IA(var,IA,D)
            else : #le coup donné par D_comp est valide
                jouer_coup(var,valide,ans,IA) #fonction jouer_coup en bas (partie 2 du coup)
    else :
        ans=coup_IA_alea(var,IA)
    return(ans)

def coup_IA_train(version,var,IA,n_sim,n_sim_min,D,D_prev,seuil,alea) : ###structure du coup de l'IA pour l'entraînement (dirigé vers les positions les plus probables)###
    meilleur_coup='' #meilleur coup retenu
    value=-1 #"valeur" de ce coup (% de victoire estimé après ce coup)
    Cases_valides=[]
    D_coup={}
    for k in range(len(var.Cases)) :
        coup=var.Cases[k]
        valide=est_valide(var,coup,IA) #fonction est_valide en bas (partie 1 du coup)
        if valide[0]==True : #si le coup est valide, on cherche sa "value"
            Cases_valides.append(coup)
            var_copy=copy.deepcopy(var)
            jouer_coup(var_copy,valide,coup,IA)  #fonction jouer_coup en bas (partie 2 du coup)
            n_win=0
            n_tot=0
            if indice(var_copy.P,3-IA) in D :
                (n_win,n_tot)=D[indice(var_copy.P,3-IA)]
            if n_tot<n_sim_min : #si on veut faire plus de simulations pour cette position
                c=0
                for l in range(n_sim) :
                    var_2=copy.deepcopy(var_copy)
                    if version=='v1' :
                        if partie('alea',var_2,3-IA,D_prev,seuil)==IA :
                            c=c+1
                    elif version=='v2' :
                        if partie('semialea',var_2,3-IA,D_prev,seuil)==IA :
                            c=c+1
                D_coup[indice(var_copy.P,3-IA)]=n_sim-c #on sauvegarde les tests
                value_coup=c/n_sim
            else : #on a assez de simulations
                value_coup=n_win/n_tot
            if value_coup>value : #si le coup est meilleur que celui qu'on avait retenu :
                meilleur_coup=coup #il devient le meilleur coup
                value=value_coup
    if Cases_valides==[] : #si aucun coup n'est valide
        ans='pas de coup possible.'
        var.Cases=[] #la partie s'arrête
    elif alea==0 : #s'il y a un coup valide et alea=0
        ans=meilleur_coup
        valide_meilleur=est_valide(var,ans,IA) #fonction est_valide en bas (partie 1 du coup)
        jouer_coup(var,valide_meilleur,ans,IA) #fonction jouer_coup en bas (partie 2 du coup)
    else : #s'il y a un coup valide et alea=1
        n=int(len(Cases_valides)*random())
        ans=Cases_valides[n]
        valide=est_valide(var,ans,IA) #fonction est_valide en bas (partie 1 du coup)
        jouer_coup(var,valide,ans,IA) #fonction jouer_coup en bas (partie 2 du coup)
    return(ans,D_coup)

##Exécution des coups
def est_valide(var,coup,joueur) : ###le coup est-il valide? on ne vérifie que les conditions pour l'IA. Les autres du joueur (coup reconnu? et case occupée?) sont vérifiées au début de coup_joueur###
    ans=True
    i=int(coup[0])
    j=int(coup[1])
    Adj_joueur=[] #cases adjacentes qui appartiennent au joueur qui joue
    Adj_ennemi=[] #cases adjacentes qui appartiennent au joueur opposé
    Adj_vides=[] #cases adjacentes vides
    error=''
    if i!=1 : #on construit ces 3 listes
        if var.P[i-2][j-1]==joueur :
            Adj_joueur.append((i-1,j))
        elif var.P[i-2][j-1]==3-joueur :
            Adj_ennemi.append((i-1,j))
        else :
            Adj_vides.append((i-1,j))
    if i!=var.N : #de même
        if var.P[i][j-1]==joueur :
            Adj_joueur.append((i+1,j))
        elif var.P[i][j-1]==3-joueur :
            Adj_ennemi.append((i+1,j))
        else :
            Adj_vides.append((i+1,j))
    if j!=1 : #de même
        if var.P[i-1][j-2]==joueur :
            Adj_joueur.append((i,j-1))
        elif var.P[i-1][j-2]==3-joueur :
            Adj_ennemi.append((i,j-1))
        else :
            Adj_vides.append((i,j-1))
    if j!=var.N : #de même
        if var.P[i-1][j]==joueur :
            Adj_joueur.append((i,j+1))
        elif var.P[i-1][j]==3-joueur :
            Adj_ennemi.append((i,j+1))
        else :
            Adj_vides.append((i,j+1))
    test=1
    for case in Adj_ennemi :
        if len(var.Chaines[case][0])==1 :
            test=0 #test=0 si ce coup capture au moins une chaîne, dans ce cas pas de suicide
    if test==1 and len(Adj_vides)==0 : #sinon :
        for case in Adj_joueur :
            if len(var.Chaines[case][0])>1 :
                test=0 #test=0 si la case est liée à une chaîne alliée d'au moins 2 libertés
        if test==1 : #si non..
            ans=False
            error='Suicide. Choisir une autre case.' #..c'est un suicide
    if ans==True : #s'il n'y a pas de suicide
        P_save=[[var.P[a][b] for b in range(var.N)] for a in range(var.N)] #pour ne pas modifier P
        P_save[i-1][j-1]=joueur
        for case in Adj_ennemi :
            i2=case[0]
            j2=case[1]
            if len(var.Chaines[case][0])==1 and P_save[i2-1][j2-1]==3-joueur :
                for case_chaine in var.Chaines[case][1:] :
                    i3=case_chaine[0]
                    j3=case_chaine[1]
                    P_save[i3-1][j3-1]=0
        if P_save in var.Pos : #la position a-t-elle déja été atteinte?
            ans=False
            if var.Pos[len(var.Pos)-2]==P_save :
                error='Position déja atteinte (ko)' #si oui, non valide (règle du ko)
            else :
                error='Position déja atteinte (superko)' #(ou du superko)
    return(ans,Adj_joueur,Adj_ennemi,Adj_vides,error) #on renvoie les valeurs dont on a besoin dans les coups du joueur et de l'IA

def jouer_coup(var,valide,ans,joueur) : ###le coup est joué et les variables sont modifées (effet de bord)###
    Adj_joueur=valide[1] #comme avant
    Adj_ennemi=valide[2] #comme avant
    Adj_vides=valide[3] #comme avant
    var.Cases.remove(ans) #ans n'est plus vide
    var.P[ans[0]-1][ans[1]-1]=joueur #P change
    var.Chaines[ans]=[[k for k in Adj_vides],ans]
    save=[k for k in Adj_ennemi]
    for case in save :
        if len(var.Chaines[case][0])==1 and case in Adj_ennemi : #si la chaîne est capturée :
            for case_2 in save :
                if case_2 in var.Chaines[case][1:] :
                    Adj_ennemi.remove(case_2) #on adapte les listes
                    Adj_vides.append(case_2)
            save_2=[k for k in var.Chaines[case][1:]]
            for case_chaine in save_2 : #et on adapte Chaines (des cases deviennent libre donc il y a de nouvelles libertés)
                var.Chaines[case_chaine]=[[]]
                var.Cases.append(case_chaine)
                i2=case_chaine[0]
                j2=case_chaine[1]
                var.P[i2-1][j2-1]=0
                if i2!=1 and var.P[i2-2][j2-1]==joueur :
                    for case_chaine_2 in var.Chaines[(i2-1,j2)][1:] :
                        var.Chaines[case_chaine_2][0].append(case_chaine)
                if i2!=var.N and var.P[i2][j2-1]==joueur and case_chaine not in var.Chaines[(i2+1,j2)][0] :
                    for case_chaine_2 in var.Chaines[(i2+1,j2)][1:] :
                        var.Chaines[case_chaine_2][0].append(case_chaine)
                if j2!=1 and var.P[i2-1][j2-2]==joueur and case_chaine not in var.Chaines[(i2,j2-1)][0] :
                    for case_chaine_2 in var.Chaines[(i2,j2-1)][1:] :
                        var.Chaines[case_chaine_2][0].append(case_chaine)
                if j2!=var.N and var.P[i2-1][j2]==joueur and case_chaine not in var.Chaines[(i2,j2+1)][0] :
                    for case_chaine_2 in var.Chaines[(i2,j2+1)][1:] :
                        var.Chaines[case_chaine_2][0].append(case_chaine)
    var.Pos.append(copy.deepcopy(var.P)) #P devient une position atteinte (deepcopy obligatoire ici)
    for case in Adj_ennemi :
        if ans in var.Chaines[case][0] :
            for case_2 in var.Chaines[case][1:] :
                var.Chaines[case_2][0].remove(ans) #la case n'est plus une liberté des chaînes adjacentes
    for case in Adj_joueur :
        if case not in var.Chaines[ans][1:] : #on regroupe les deux chaînes en une seule
            for case_2 in var.Chaines[case][1:] :
                var.Chaines[case_2][0].remove(ans) #la case n'est plus une liberté de la chaîne 2
            for case_2 in var.Chaines[ans][0] :
                if case_2 not in var.Chaines[case][0] :
                    for case_chaine in var.Chaines[case][1:] :
                        var.Chaines[case_chaine][0].append(case_2) #on rajoute les libertés de la chaîne 1 à celles de la chaîne 2
            for case_2 in var.Chaines[case][0] :
                if case_2 not in var.Chaines[ans][0] :
                    for case_chaine in var.Chaines[ans][1:] :
                        var.Chaines[case_chaine][0].append(case_2) #on rajoute les libertés de la chaîne 2 à celles de la chaîne 1
            save_1=[k for k in var.Chaines[case][1:]] #besoin de sauvegardes ici pour ne pas modifier
            save_2=[k for k in var.Chaines[ans][1:]]
            for case_1 in save_1 :
                for case_2 in save_2 :
                    var.Chaines[case_1].append(case_2) #on rajoute les cases de la chaîne 1 à la chaîne 2
                    var.Chaines[case_2].append(case_1) #on rajoute les cases de la chaîne 2 à la chaîne 1

##Fin de la partie
def area(P) : ###fonction pour compter les points (en area scoring)###
    N=len(P)
    area_noir=0
    area_blanc=0
    for i in range(1,N+1) :
        for j in range(1,N+1) :
            if P[i-1][j-1]==1 :
                area_noir=area_noir+1
            elif P[i-1][j-1]==2 :
                area_blanc=area_blanc+1
    territory=liste_chaines(P,0) #chaines de cases vides
    for chaine in territory :
        Cases_adj=[] #on construit la liste des cases adjacentes aux cases de la chaîne
        for case in chaine :
            i=case[0]
            j=case[1]
            if i!=1 :
                if P[i-2][j-1]!=0 :
                    Cases_adj.append(P[i-2][j-1])
            if i!=N :
                if P[i][j-1]!=0 :
                    Cases_adj.append(P[i][j-1])
            if j!=1 :
                if P[i-1][j-2]!=0 :
                    Cases_adj.append(P[i-1][j-2])
            if j!=N :
                if P[i-1][j]!=0 :
                    Cases_adj.append(P[i-1][j])
        joueur=Cases_adj[0]
        test=joueur
        k=1
        while test==joueur and k<len(Cases_adj) : #et on regarde si la chaîne est un territoire
            if Cases_adj[k]!=joueur :
                test=0
            k=k+1
        if test==1 : #territoire noir
            area_noir=area_noir+len(chaine)
        elif test==2 : #territoire blanc
            area_blanc=area_blanc+len(chaine)
    return(area_noir,area_blanc)

##Entraînement
def partie(version,var,joueur,D_prev,seuil) : ###simulation d'une partie entre IAs qui jouent aléatoirement###
    while var.Cases!=[] : #tant qu'il reste des cases vides
        if version=='alea' :
            coup_IA_alea(var,joueur) #joueur joue
        elif version=='semialea' :
            coup_IA_semialea(var,joueur,D_prev,seuil)
        if len(var.Cases)>=1 : #s'il reste une case vide
            if version=='alea' :
                coup_IA_alea(var,3-joueur) #l'autre joueur joue
            elif version=='semialea' :
                coup_IA_semialea(var,3-joueur,D_prev,seuil)
    Area=area(var.P)
    Score=[Area[0],Area[1]+var.Komi[var.N]]
    if Score[0]>Score[1] :
        return(1)
    elif Score[0]<Score[1] :
        return(2)

def indice(P,joueur) : ###fonction pour faciliter l'écriture des indices pour les dictionnaires sauvegardés###
    return((tuple([tuple(P[i]) for i in range(len(P))]),joueur))
    
def train() : ###pour simuler des parties aléatoires et sauvegarder les résultats localement###
    print('Version?')
    version=input()
    print(' ')
    print('Taille du goban?')
    N=int(input())
    print(' ')
    print('Temps de simulation (minutes)?')
    temps=float(input())
    print(' ')
    print('Nombre de simulations par coup?')
    n_sim=int(input())
    print(' ')
    print('Nombre de coups avant de commencer l entraînement?')
    coups_avant_train=int(input())
    print(' ')
    print('Nombre de simulations minimales voulues par position?')
    n_sim_min=int(input())
    print(' ')
    print('Parties dirigées aléatoirement?')
    alea=input()
    if alea in ('alea','Alea','1','Oui','oui') :
        alea=1
    else :
        alea=0
    D=marshal.load(open('learned_dicts\train_'+version+'_'+str(N),'rb')) #on récupère les tests qu'on a déja faits s'il y en a pour ne pas les perdre
    if version=='v1' :
        D_prev={}
        seuil=0
    elif version=='v2' :
        D_prev=marshal.load(open('learned_dicts\train_v1_'+str(N),'rb')) #dictionnaire de la version précédene
        print(' ')
        print('Seuil de prise en compte des coups?')
        seuil=float(input())
    t_init=time.time()
    t=time.time()
    while t-t_init<=60*temps :
        var=settings(N) #on réinitialise var pour la partie suivante
        c=0
        while var.Cases!=[] : ###déroulement de la partie###
            if c<coups_avant_train :
                if alea==0 :
                    coup_IA(var,1,D) #coup de Noir
                else :
                    coup_IA_alea(var,1)
                D_coup={}
            else :
                coup_1=coup_IA_train(version,var,1,n_sim,n_sim_min,D,D_prev,seuil,alea) #coup de Noir
                D_coup=coup_1[1]
            for ind in D_coup :
                if ind in D :
                    (n_win,n_tot)=D[ind]
                    n_win=n_win+D_coup[ind]
                    n_tot=n_tot+n_sim
                    D[ind]=(n_win,n_tot)
                else :
                    D[ind]=(D_coup[ind],n_sim)
            c=c+1
            if len(var.Cases)>=1 : #s'il reste une case vide pour Blanc
                if c<coups_avant_train :
                    if alea==0 :
                        coup_IA(var,2,D) #coup de Blanc
                    else :
                        coup_IA_alea(var,2)
                    D_coup={}
                else :
                    coup_2=coup_IA_train(version,var,2,n_sim,n_sim_min,D,D_prev,seuil,alea) #coup de Blanc
                    D_coup=coup_2[1]
                for ind in D_coup :
                    if ind in D :
                        (n_win,n_tot)=D[ind]
                        n_win=n_win+D_coup[ind]
                        n_tot=n_tot+n_sim
                        D[ind]=(n_win,n_tot)
                    else :
                        D[ind]=(D_coup[ind],n_sim)
                c=c+1
        t=time.time()
    marshal.dump(D,open('learned_dicts\train_'+version+'_'+str(N),'wb')) #on sauvegarde les données

##Compression des dictionnaires locaux
def liste_chaines(P,joueur) : ###fonction pour construire la liste des chaines de cases du joueur en argument dans P (joueur=0 pour les cases vides)###
    chaines=[] #on construit la liste des chaînes de cases vides de la gauche vers la droite et du haut vers le bas
    N=len(P)
    for i in range(1,N+1) :
        for j in range(1,N+1) :
            if P[i-1][j-1]==joueur :
                c_haut=0 #indicateurs
                c_gauche=0
                if i!=1 :
                    if P[i-2][j-1]==joueur :
                        c_haut=1 #si la case de gauche est vide
                if j!=1 :
                    if P[i-1][j-2]==joueur :
                        c_gauche=1 #si la case du haut est vide
                if c_haut==0 and c_gauche==0 :
                    chaines.append([(i,j)]) #création d'une nouvelle chaîne
                elif c_haut==1 and c_gauche==0 :
                    chaines[indice_chaine(chaines,(i-1,j))].append((i,j)) #on lie la case à la chaîne du haut
                elif c_haut==0 and c_gauche==1 :
                    chaines[indice_chaine(chaines,(i,j-1))].append((i,j)) #on lie la case à la chaîne de gauche
                else : #les cases du haut et de gauche sont au joueur
                    k1=indice_chaine(chaines,(i-1,j))
                    k2=indice_chaine(chaines,(i,j-1))
                    if k1==k2 :#les cases du haut et de gauche sont dans le même chaîne
                        chaines[k1].append((i,j))
                    else :
                        for case in chaines[k2] :
                            chaines[k1].append(case)
                        chaines[k1].append((i,j))
                        chaines.remove(chaines[k2])
    return(chaines)

def indice_chaine(chaines,case) : ###fonction pour trouver de quelle chaîne de cases vides fait partie la case###
    ans=-1
    k=0
    while ans==-1 :
        if case in chaines[k] :
            ans=k
        k=k+1
    return(ans)

def dict_chaines(P) : ###fonction pour construire l'attribut Chaines de settings à partir de P###
    N=len(P)
    chaines=liste_chaines(P,1)+liste_chaines(P,2) #chaînes noires et blanches
    Chaines={}
    for chaine in chaines :
        libertés=[]
        for case in chaine : #on construit les libertés
            i=case[0]
            j=case[1]
            if i!=1 :
                if P[i-2][j-1]==0 and (i-1,j) not in libertés :
                    libertés.append((i-1,j))
            if i!=N :
                if P[i][j-1]==0 and (i+1,j) not in libertés :
                    libertés.append((i+1,j))
            if j!=1 :
                if P[i-1][j-2]==0 and (i,j-1) not in libertés :
                    libertés.append((i,j-1))
            if j!=N :
                if P[i-1][j]==0 and (i,j+1) not in libertés :
                    libertés.append((i,j+1))
        for case in chaine : #et on construit le dictionnaire
            Chaines[case]=[copy.copy(libertés)]+chaine
    return(Chaines)

def compress(N,version) : ###fonction pour "compresser" le dictionnaire local : on associe à chaque position le meilleur coup possible pour ne pas le faire pendant le coup de l'IA###
    D=marshal.load(open('learned_dicts\train_'+version+'_'+str(N),'rb')) #on récupère les tests qu'on a déja faits
    D[indice([[0 for j in range(N)] for i in range(N)],1)]=(0,0) #il faut avoir la position initiale en indice de D...
    D_comp={}
    c=0
    p=-1
    n=len(D)
    for ind in D : #...pour qu'ind prenne cette valeur et que D_comp contienne la solution au coup initial
        if int(100*c/n)>p :
            print(str(int(100*c/n))+'%')
            p=int(100*c/n)
        meilleur_coup='' #meilleur coup retenu
        value=-1 #"valeur" de ce coup (% de victoire estimé après ce coup)
        var=settings(N)
        var.P=[[ind[0][i-1][j-1] for j in range(1,N+1)] for i in range(1,N+1)]
        var.Chaines=dict_chaines(var.P)
        var.Cases=[]
        for i in range(1,N+1) :
            for j in range(1,N+1) :
                if var.P[i-1][j-1]==0 :
                    var.Cases.append((i,j))
        Cases_valides=[]
        IA=ind[1]
        for k in range(len(var.Cases)) :
            coup=var.Cases[k]
            valide=est_valide(var,coup,IA) #fonction est_valide en bas (partie 1 du coup)
            if valide[0]==True : #si le coup est valide, on prend sa "value"
                Cases_valides.append(coup)
                var_copy=copy.deepcopy(var)
                jouer_coup(var_copy,valide,coup,IA)  #fonction jouer_coup en bas (partie 2 du coup)
                if indice(var_copy.P,3-IA) in D :
                    (n_win,n_tot)=D[indice(var_copy.P,3-IA)]
                    value_coup=1-n_win/n_tot
                    if value_coup>value :
                        value=value_coup
                        meilleur_coup=coup
        if Cases_valides!=[] and meilleur_coup=='' : #s'il n'y a pas eu de simulations pour cette position
            ans='pas de simulations'
        elif Cases_valides==[] : #si aucun coup n'est valide
            ans='pas de coup possible.'
        else : #s'il y a un coup valide ayant été testé
            ans=meilleur_coup
        D_comp[ind]=ans
        c=c+1
    print('100%')
    marshal.dump(D_comp,open('learned_dicts\train_'+version+'_'+str(N)+'_comp','wb'))

##Interface
def show_goban(a): ###fonction pour afficher le goban de manière lisible###
    res = "   "
    for i in range(len(a[0])) :
        res += str(i+1)+" " #pour afficher les colonnes
    res += "\n"
    for i in range(len(a)):
        res += str(i+1) + " " #pour afficher les lignes
        for j in range(len(a[i])):
            res += "|"
            if (a[i][j] == 1):
                res += "X" #cases noires
            elif (a[i][j] == 2):
                res += "0" #cases blanches
            else:
                res += "_" #cases vides
        res += "|\n"
    print(res)