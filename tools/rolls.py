import csv, json
W='/workspace/wyoleg'
def lean(s):
    s=float(s); return 'Conservative' if s>0 else ('Liberal' if s<0 else 'Neutral')
def build(Y, cat=None):
    Y=str(Y)
    rc=list(csv.DictReader(open(f'{W}/y{Y}/wy_{Y}_rollcalls.csv')))
    sc={r['VoteID']:r for r in csv.DictReader(open(f'{W}/y{Y}/scores_{Y}.csv'))}
    rows=[]
    for r in rc:
        k={'F':'Floor','C':'Committee'}[r['VoteType']]
        st=f"{k}: {r['Action']}"
        a=r['Amendment']
        if a and a not in r['Action']: st+=f" [{a}]"
        c=(cat or {}).get(r['VoteID'],'Uncategorized')
        rows.append((r['VoteDate'],int(r['VoteID']),[r['VoteDate'],r['Bill'],r['CatchTitle'],st,c,lean(sc[r['VoteID']]['Score'])]))
    return rows
