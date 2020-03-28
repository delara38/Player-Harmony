import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder
from sklearn.linear_model import Ridge, BayesianRidge

def createCombos(x):
    matches = []
    for i in range(len(x)):
        for j in range(i+1,len(x)):
            matches.append("{}-{}".format(*sorted([int(x[i]),int(x[j])])))
    return tuple(matches)


data = pd.read_csv('five_year_shifts.csv')

del data['Unnamed: 0']
del data['Unnamed: 0.1']

print('starting')
Y = data.pop('PTS/100')


data['oPairs'] = data.apply(lambda x: createCombos([x['offence1'],x['offence2'],x['offence3'],x['offence4'],x['offence5']]), axis=1)
data['dPairs'] = data.apply(lambda x: createCombos([x['defence1'],x['defence2'],x['defence3'],x['defence4'],x['defence5']]), axis=1)
print('got pairs')
offence = data.apply(lambda x: tuple((x['offence1'],x['offence2'],x['offence3'],x['offence4'],x['offence5'])), axis=1)
defence = data.apply(lambda x: tuple((x['defence1'],x['defence2'],x['defence3'],x['defence4'],x['defence5'])), axis=1)

#data we dont need to perform more pre-processing on
non_cats = data[['isHome','time','startsBall']]

print('actually pre-processing')


mlb_op = MultiLabelBinarizer()
oPairs = pd.DataFrame(mlb_op.fit_transform(data['oPairs']), columns=["{}O".format(x) for x in mlb_op.classes_]).reset_index()

print('yeeee')
mlb_dp = MultiLabelBinarizer()
dPairs = pd.DataFrame(mlb_dp.fit_transform(data['dPairs']), columns=["{}D".format(x) for x in mlb_dp.classes_]).reset_index()

print('finished mlb on pairs')

pDiff = data[['possession_diff']]
ohe_pdif = OneHotEncoder(sparse=False)
pDiff = pd.DataFrame(ohe_pdif.fit_transform(pDiff), columns=ohe_pdif.categories_[0]).reset_index()


print('finished point diff')
mlb_o = MultiLabelBinarizer()
offense = pd.DataFrame(mlb_o.fit_transform(offence), columns=["{}O".format(x) for x in mlb_o.classes_]).reset_index()

mlb_d = MultiLabelBinarizer()
defence = pd.DataFrame(mlb_d.fit_transform(defence), columns=["{}D".format(x) for x in mlb_d.classes_]).reset_index()

print('finished single player')

d1 = pd.merge(non_cats, pDiff, left_index=True, right_index=True)
d2 = pd.merge(offense, defence, left_index=True, right_index=True)
d3 = pd.merge(oPairs, dPairs, left_index=True, right_index=True)

X = pd.concat((d1,d2,d3))

#X = pd.concat((non_cats, pDiff, offense, defence, oPairs, dPairs), axis=1)

pd.concat((X,Y), axis=1).to_csv('readyToTrain.csv')
'''
print('got X and Y training now')

model = Ridge(alpha=10000)

model.fit(X,Y)


print('done training')
coefs = model.coef_


coefi = []
cols = X.columns.tolist()
for i in range(len(coefs)):
    co = {}
    co['name'] = cols[i]
    co['coef'] = coefs[i]
    coefi.append(co)

coefs = pd.DataFrame(coefi)

coefs.to_csv('results.csv')

#print(data.head(4))
'''