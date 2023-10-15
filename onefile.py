import pandas as pd
from flask import Flask
from flask import request,render_template,redirect
import datetime

class Database:

    def __init__(self):
        try:
            data=pd.read_csv("token.csv",index_col=0)
        except:
            data=pd.DataFrame({'name':[],'number':[],'token':[],'dr':[],'day':[],'month':[],'year':[]})
        self.data=data

    def add_token(self,patient):
        self.data=self.data.append(patient,ignore_index=True)
        self.data.to_csv("token.csv")
    
    def edit_save(self,patient):
        return

    def shar_token(self,date):
        day,month,year=date[2],date[1],date[0]
        data=self.data
        data=data[(data['day']==day) & (data['month']==month) & (data['year']==year) & (data["dr"]=='sharafudheen')].sort_values(by=['token'])
        tokens,names,numbers=data['token'].tolist(),data['name'].tolist(),data['number'].tolist()
        shar_patient_list=[]
        sdate="-".join(str(i) for i in date)
        for i,j,k in zip(tokens,names,numbers):
            shar_patient_list.append({'token':i,'name':j,'number':k,'date':sdate,'dr':'sharafudheen'})
        return shar_patient_list

    def sham_token(self,date):
        day,month,year=date[2],date[1],date[0]
        data=self.data
        data=data[(data['day']==day) & (data['month']==month) & (data['year']==year) & (data["dr"]=='shamsiya')].sort_values(by=['token'])
        tokens,names,numbers=data['token'].tolist(),data['name'].tolist(),data['number'].tolist()
        sham_patient_list=[]
        sdate="-".join(str(i) for i in date)
        for i,j,k in zip(tokens,names,numbers):
            sham_patient_list.append({'token':i,'name':j,'number':k,'date':sdate,'dr':'shamsiya'})
        return sham_patient_list


def search_fun(date,name,number):
    db=Database()
    data=db.data
    if date != '':
        date=date.split('-')
        data=data[(data['day']  == int(date[2])) & (data['month']==int(date[1])) & (data['year']==int(date[0]))]
    if name != '':
        data=data[data['name'].str.contains(name,case=False)]
    if number != '':
        data=data[data['number'].astype('str').str.contains(str(number))]
    data['date']= data['year'].astype('int').astype('str')+'-'+data['month'].astype('int').astype('str')+'-'+data['day'].astype('int').astype('str')
    data=data[['name','token','number','date','dr']]
    shamdata=data[data['dr']=='shamsiya'].to_dict(orient='records')
    shardata = data[data['dr'] == 'sharafudheen'].to_dict(orient='records')
    return shamdata,shardata


app=Flask(__name__)

@app.route('/')
def home():
    token_list=[]
    for i in range(1,50):
        token_list.append(i)
    db=Database()
    date=[datetime.date.today().year,datetime.date.today().month,datetime.date.today().day]
    dshar=db.data.loc[(db.data['dr']=='sharafudheen')&(db.data['day']==date[2])&(db.data['month']==date[1])&(db.data['year']==date[0])]
    dsham=db.data.loc[(db.data['dr']=='shamsiya')&(db.data['day']==date[2])&(db.data['month']==date[1])&(db.data['year']==date[0])]
    token_list_shar=list(set(token_list)-set(dshar['token'].tolist()))
    token_list_sham=list(set(token_list)-set(dsham['token'].tolist()))
    try: t_shar_max=max(dshar['token'].tolist()) ; t_shar_max=[t_shar_max,t_shar_max+1]
    except:t_shar_max= None
    try: t_sham_max=max(dsham['token'].tolist()) ; t_sham_max=[t_sham_max,t_sham_max+1]
    except:t_sham_max= None
    return render_template("home.html",token_list_shar=token_list_shar,token_list_sham=token_list_sham,
                           t_shar_max=t_shar_max,t_sham_max=t_sham_max
                           )

@app.route('/1', methods=['GET'])
def add_token_sham():
    if request.method == "GET":
        token=request.args['tokenlist']
        name=request.args['name']
        number=request.args['mnumber']
        dr='shamsiya'
        date=datetime.date.today()
        day,month,year=int(date.day),int(date.month),int(date.year)
        db=Database()
        patient={'name':name, 'number':number, 'token':token, 'dr':dr,'day':day,'month':month,'year':year}
        db.add_token(patient)
        return redirect('/')
    else:
        return redirect('/')

@app.route('/2', methods=['GET'])
def add_token_shar():
    if request.method == "GET":
        token=request.args['tokenlist']
        name=request.args['name']
        number=request.args['mnumber']
        dr='sharafudheen'
        date=datetime.date.today()
        day,month,year=int(date.day),int(date.month),int(date.year)
        db=Database()
        patient={'name':name, 'number':number, 'token':token, 'dr':dr,'day':day,'month':month,'year':year}
        db.add_token(patient)
        return redirect('/')
    else:
        return redirect('/')

@app.route('/today')
def today():
    db=Database()
    d=datetime.date.today()
    date=[d.year,d.month,d.day]
    shar_patient_list=db.shar_token(date)
    sham_patient_list=db.sham_token(date)
    return render_template('today.html',shar_patient_list=shar_patient_list,sham_patient_list=sham_patient_list)

@app.route('/search',methods=['GET','POST'])
def search():
    if request.method == 'POST':
        date=request.form.get('date')
        name=request.form.get('name')
        number=request.form.get('number')
        data=search_fun(date,name,number)
        return render_template('search.html',sham_patient_list=data[0],shar_patient_list=data[1])
    return render_template('search.html')

checkdata=None
@app.route('/edit',methods=['GET'])
def edit():
    global checkdata
    token_list=[]
    for i in range(1,50):
        token_list.append(i)
    db=Database()
    if request.method == 'GET':
        token,name,number,date,dr=request.args['token'],request.args['name'],request.args['number'],request.args['date'],request.args['dr']
        content={'token':int(token),'name':name,'number':int(number),'date':date,'dr':dr}
        data=db.data.to_dict(orient='records')
        date=date.split('-')
        checkdata={'token':int(token),'name':name,'number':int(number),'day':int(date[2]),'month':int(date[1]),'year':int(date[0]),'dr':dr}
        if not checkdata in data:
            return redirect('/')
        else:
            drl=db.data.loc[(db.data['dr']==dr)&(db.data['day']==int(date[2]))&(db.data['month']==int(date[1]))&(db.data['year']==int(date[0]))]   
            token_listl=list(set(token_list)-set(drl['token'].tolist()))
            token_listl.insert(0,content['token'])
            
            return render_template("edit.html",token_listl=token_listl,content=content)
            
    
    return redirect('/')

@app.route('/edit/save',methods=['GET'])
def save():
    if request.method == 'GET':
        global checkdata
        db=Database()
        token,name,number,done=int(request.args['tokenlist']),request.args['name'],int(request.args['mnumber']),request.args['done']
        if done == 'save':
            db.data=db.data.drop(db.data[(db.data['token']==checkdata['token'])&(db.data['name']==checkdata['name'])&(db.data['number']==checkdata['number'])&(db.data['day']==checkdata['day'])&(db.data['month']==checkdata['month'])&(db.data['year']==checkdata['year'])&(db.data['dr']==checkdata['dr'])].index)
            patient={'name':name, 'number':number, 'token':token, 'dr':checkdata['dr'],'day':checkdata['day'],'month':checkdata['month'],'year':checkdata['year']}
            db.add_token(patient=patient)
        if done == 'delete':
            data=db.data.drop(db.data[(db.data['token']==checkdata['token'])&(db.data['name']==checkdata['name'])&(db.data['number']==checkdata['number'])&(db.data['day']==checkdata['day'])&(db.data['month']==checkdata['month'])&(db.data['year']==checkdata['year'])&(db.data['dr']==checkdata['dr'])].index)
            data.to_csv("token.csv")
        return redirect('/')


    return redirect('/')


if __name__=='__main__':
    app.run(port=8888,host='0.0.0.0',debug=True)
