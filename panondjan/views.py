from django.shortcuts import render
from django.views.generic.edit import FormView
from .forms import DataManageForm
from io import TextIOWrapper
import csv
import pandas as pd
import numpy as np
from pprint import pprint 

# Create your views here.
class DataManage(FormView):
    template_name = "panondjan/data_manage.html"
    form_class = DataManageForm
    success_url = '/demo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # 入力したデータと変換したデータを["context"]に設定
            context["post_data"] = self.request.session['post_data']
            context["transfmd_data"] = self.request.session['transfmd_data']
            
            # ["data"]の中に["index"]を入れる　（テーブル描画のため）
            for d, i in zip(context["post_data"]["data"], context["post_data"]["index"]):
                d.insert(0,i)

            # ["data"]の中に["index"]を入れる　（テーブル描画のため）
            for d, i in zip(context["transfmd_data"]["data"], context["transfmd_data"]["index"]):
                d.insert(0,i) 

            # 変換方法の説明を取得し["context"]に設定
            way = self.request.session['trasform_type']
            explain = self.get_explain(way)
            context["des"] = explain['des']
            context["code"] = explain['code']
        except:
            pass

        return context

    # This method is called when valid form data has been POSTed.
    def form_valid(self, form): 
        # save input date as dict
        df = self.save_data(form.cleaned_data['data'])
        # transform data along with selected way
        way = form.cleaned_data['trasform_type']
        self.transform_data(way, df)
        # save trasform_type in session
        self.request.session['trasform_type'] = way

        return super().form_valid(form)
    
    def save_data(self, ojct):
        data = TextIOWrapper(ojct)
        csv_file = csv.reader(data)
        with open('/tmp/buff.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerows(csv_file)
        
        df = pd.read_csv('/tmp/buff.csv')
        df = df.astype({'orderid': str})
        df.set_index('orderid', inplace=True)

        # make dict from df, and save it in session
        self.request.session['post_data'] = df.to_dict('split')

        
        return df

    # 本来はデータの変換等はこのクラスでやるべきではない。フォームクラスが行うのが適切?
    def transform_data(self, way, ojct):
        df = ojct

        if way == 'srt':
            df = df.sort_values(by=['amount'])

        if way == 'sri':
            df = df.sort_index(axis=1)

        if way == 'ctt':
            df = pd.concat([df, df])

        if way == 'map':
            df['amount'] = df['amount'].map(lambda x: 'kuishinbo' if x > 20 else '')
            df = df[{'customer','amount'}]

        if way == 'aap':
            df = df.applymap(lambda x: 'suji' if str(x).isdecimal() else 'mojiretu')

        if way == 'pop':
            df = df.loc['3':'5',['customer','totalprice']]

        if way == 'rpc':
            df['product'] = df['product'].str.replace('tai', 'MAdai')

        if way == 'ist':        
            df.insert( loc=0, column='inserted', value='1' )

        if way == 'dpt':        
            df = df[df.duplicated(subset='customer')]

        if way == 'ddp':        
            df = df.drop_duplicates(subset='customer')
        
        elif way == 'pvt':
            df = pd.pivot_table(df, values='totalprice', index=['customer'], 
                                columns=['product'], aggfunc=np.sum,
                                margins=True )
        elif way == 'grp':
            df = df.groupby(["customer"]).sum()

        self.request.session['transfmd_data'] = df.to_dict('split')

    #was not suitable way  
    def get_explain(self, way):
        # des means description
        des = ""
        code = ""
        
        if way == 'srt':
            des = '数量順で並び替え'
            code = "df.sort_values(by=['amount'])"

        if way == 'sri':
            des = '列名順で並び替え'
            code = "df = df.sort_index(axis=1)"

        if way == 'ctt':
            des = 'dfとdfをつなげる'
            code = "df = pd.concat([df, df])"

        if way == 'map':
            des = '各列、行に関数を適用する'
            code = """df['amount'] = df['amount'].map(lambda x: 'kuishinbo' if x > 20 else '')
df = df[{'customer','amount'}]"""

        if way == 'aap':
            des = 'dataframe全体に関数を適用する'
            code = "df = df.applymap(lambda x: 'suji' if str(x).isdecimal() else 'mojiretu')"
        
        if way == 'rpc':
            des = '列中の値を置換'
            code = "df['product'] = df['product'].str.replace('tai', 'MAdai')"
        
        if way == 'pop':
            des = "orderidが3〜5の行と、列名が'customer'と'totalprice'の列を抽出"
            code = "df = df.loc['3':'5',['customer','totalprice']]"

        elif way == 'ist':
            des = '列を挿入する'
            code = "df.insert( loc=0, column='inserted', value='1' )"

        elif way == 'dpt':
            des = '重複を抽出する。(customerの重複行を抽出)'
            code = "df = df[df.duplicated(subset='customer')]"

        elif way == 'ddp':
            des = '重複をドロップする。(customerの重複を削除)'
            code = "df = df.drop_duplicates(subset='customer')"

        elif way == 'pvt':
            des = 'ピボットテーブルをつくる'
            code = """df = pd.pivot_table(df, values='totalprice', index=['customer'], 
                    columns=['product'], aggfunc=np.sum,
                    margins=True )"""

        if way == 'grp':
            des = '顧客別に集計'
            code = "df.groupby(['customer'].sum()"

        explain = {'des':des, 'code':code}
        return explain


                
