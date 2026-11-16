import csv, sys
sys.path.insert(0,'/workspace/name-index/tools')
import namelib as N
P=list(csv.DictReader(open('/workspace/name-index/data/people.csv')))
LY=[r for r in csv.DictReader(open('/workspace/name-index/data/legislator_years.csv'))]
idx={}
for p in P:
    names=[p['display_name']]+[a for a in (p['aliases'] or '').split(';') if a.strip()]
    for n in names:
        idx.setdefault(N.parse(n)['last'],[]).append((p,N.parse(n)))
YEAR='2021';DIST=''
def match(full, dist=''):
    global DIST; DIST=dist
    q=N.parse(full); c=idx.get(q['last'],[])
    exact={p['person_id'] for p,k in c if N.given_compatible(q,k) or (q['nick'] and q['nick']==k['first']) or (k['nick'] and k['nick'].split()[0]==q['first'])}
    def conflict(pid):
        for p,k in c:
            if p['person_id']!=pid or not k['middles'] or not q['middles']: continue
            if k['middles'][0][:1]!=q['middles'][0][:1]: return True
        return False
    bad={x for x in exact if conflict(x)}
    if bad and len(exact)==1: return '','middle-name conflict, needs review','; '.join(sorted(bad))
    exact-=bad
    if len(exact)==1: return exact.pop(),'name match',''
    if len(exact)>1:
        ly={r['person_id'] for r in LY if r['year']==YEAR and r['district']==DIST and r['person_id'] in exact}
        if len(ly)==1: return ly.pop(),'resolved by legislator_years','; '.join(sorted(exact))
        return '','ambiguous','; '.join(sorted(exact))
    near={p['person_id'] for p,k in c if N.first_initial_only(q,k)}
    if near: return '','first-name variant, needs review','; '.join(sorted(near))
    return '','no match in people.csv',''
if __name__=='__main__':
    A=list(csv.DictReader(open('/workspace/wyoleg/y2021/legislators_2021.csv')))
    out=[];res={}
    for r in A:
        pid,how,cand=match(r['full_name'],r['district'])
        res[r['full_name']]=pid
        if not pid or how!='name match': out.append(dict(year=2021,full_name=r['full_name'],roster_label=r['legislator'],chamber=r['chamber'],district=r['district'],reason=how,matched_person_id=pid,candidates=cand,ratings_file_person_id=r['person_id']))
        elif pid!=r['person_id']: print('DIFF from ratings-file pid',r['full_name'],pid,r['person_id'])
    print('matched',sum(1 for v in res.values() if v),'of',len(A),'unmatched',sum(1 for v in res.values() if not v),'review rows',len(out))
    lyp={(r['district'],r['roster_label']):r['person_id'] for r in LY if r['year']=='2021'}
    print('disagree with legislator_years:',[(r['full_name'],res[r['full_name']],lyp.get((r['district'],r['legislator']))) for r in A if res[r['full_name']]!=lyp.get((r['district'],r['legislator']))])
    for o in out: print(o)
    w=csv.DictWriter(open('/workspace/officials-archive/needs-review-2021.csv','w',newline=''),fieldnames=['year','full_name','roster_label','chamber','district','reason','matched_person_id','candidates','ratings_file_person_id'])
    w.writeheader(); w.writerows(out)
