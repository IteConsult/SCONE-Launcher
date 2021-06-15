import sys
import os
import pandas as pd
from hdbcli import dbapi
from sqlalchemy import create_engine
sys.path.append(os.path.dirname(os.getcwd())+'\\LauncherClass')
from Launcher import *
import tkinter
from tkinter import ttk
import threading


def UploadToHANA():
    SCHEMA_NAME = "SAGE_1"
    HANA_USER="SAGE_1_3XGR4Y60OGD3E1YSEC5ZO3C2F_RT"
    HANA_PW="Ze4cBAy5lLA1w1ykGTWTgwoXUJpzudZ6O2T58cWMDSE1khCT0E70-7y52uDOmwEJLQUWDCb8HWUDbauBpyfHZ.NSsT1w7WtUgEvNFjcLXNOmMRAqnJTnCr9_H238tj_V"
    HANA_ADDRESS = "hana://" + HANA_USER + ":" + HANA_PW + "@8969f818-750f-468f-afff-3dc99a6e805b.hana.trial-us10.hanacloud.ondemand.com:443/?encrypt=true&validateCertificate=true&currentschema=SAGE_1"
    #HANA_ADDRESS = "hana://" + HANA_USER + ":" + HANA_PW + "@" + "8969f818-750f-468f-afff-3dc99a6e805b.hana.trial-us10.hanacloud.ondemand.com" + ":443" + "/?encrypt=true&validateCertificate=true"

    dfList = []
    plan = pd.read_excel("Model/output_table.xlsx", sheet_name="ite_snp_out_plan", dtype=str).set_axis(['Item', 'Due Date', 'Week', 'Start Date', 'Start Day', 'Start Time', 'End Date', 'End Day', 'End Time', 'Plant', 'WorkCenter', 'Production', 'BackOrder', 'Version', 'Run', 'Category', 'Entity'], axis = 1)
    print(plan)
    week = pd.read_excel("Model/output_table.xlsx", sheet_name="ite_snp_out_week", dtype=str).set_axis(['Item', 'Week', 'Month', 'Inventory', 'Safety Stock', 'Demand', 'Production', 'Amount Under SS', 'Overanticipation', 'Version', 'Run', 'Entity'], axis = 1)
    print(week)
    minrun = pd.read_excel("Model/output_table.xlsx", sheet_name="ite_snp_sol_minrun", dtype=str).set_axis(['Week', 'Month', 'Plant', 'Formula', 'Min Run', 'Version', 'Run', 'Entity'], axis = 1)
    print(minrun)
    #solver = pd.read_excel("output_table.xlsx", header=0, names=col_names, sheet_name="ite_snp_solver_output")

    dfList = { }
    dfList["SAGE.TABLES::ITE_SNP_OUT_PLAN"] = plan
    dfList["SAGE.TABLES::ITE_SNP_OUT_WEEK"] = week
    dfList["SAGE.TABLES::ITE_SNP_OUT_MINRUN"] = minrun

    engine = create_engine(HANA_ADDRESS)
    try:
        conn = engine.connect()
        for df in dfList:
            try:
                engine.execute(f"DELETE FROM \"{SCHEMA_NAME}\".\"{df}\" WHERE \"Run\" = \'{dfList[df]['Run'].iloc[0]}\'")
                dfList.get(df).to_sql(schema=SCHEMA_NAME, name=df, con=engine, index=False, if_exists='append')
                print(df + " table uploaded")
            except Exception as e:
                print('Upload failed! ' + str(e))
        conn.close()
    except Exception as e:
        print("Connection Failed!" + str(e))

    engine.dispose()

buttons_dic = {'WEEKLY DETAIL': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=60550B04C9065F71913B190BFE6EB17C;forceOpenView=true',
              'COMPARE RUNS': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=8FF50B04C900218FCE043707F07405B7;forceOpenView=true',
              'DEMAND REVIEW': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=FE0CCB026F647AA195B99C7A35307B9B',
              'HISTORICAL REVIEW': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=759BC306F395D7C284A88AC321DCE0A8',
              'FORECAST DEMAND': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=2D8B83045497F99AE31C9E42C1A5B716',
              'EDIT DEMAND': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=203D7B057DBE69F43A2E07E5112A09F6;mode=view',
              }

def UploadToHANACommand():
    loading_window = LoadingWindow(app)
    th = threading.Thread(target = UploadToHANA, daemon = True)
    th.start()
    loading_window.check(th)

app = Launcher('SUPPLY CHAIN NETWORK OPTIMIZATION')
app.root.resizable(0,0)

app.add_data_lf()

upload_frm = ttk.Frame(app.read_data_lf)
app.read_data_lf.columnconfigure(2, weight = 1, uniform = 'read_data')
upload_frm.grid(pady = 10, row = 0, column = 2, sticky = 'ew')

app.upload_btn = ttk.Button(upload_frm, width = 13, text = 'UPLOAD TO HANA', command = lambda: UploadToHANACommand())
app.upload_btn.pack(ipadx = 10, ipady = 2, padx = 20)

app.add_model_lf('SCONetwork')

app.add_sac_buttons(buttons_dic)

app.add_logo()

app.root.mainloop()