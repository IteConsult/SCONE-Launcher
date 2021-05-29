import sys
sys.path.append('C:/Users/admin/Documents/GitHub/LauncherClass')
from Launcher import Launcher

app = Launcher('SUPPLY CHAIN NETWORK OPTIMIZATION')
app.root.resizable(0,0)

app.add_data_lf()
app.add_model_lf('SCONetwork')

buttons_dic = {'WEEKLY DETAIL': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=60550B04C9065F71913B190BFE6EB17C;forceOpenView=true',
              'COMPARE RUNS': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=8FF50B04C900218FCE043707F07405B7;forceOpenView=true',
              'DEMAND REVIEW': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=FE0CCB026F647AA195B99C7A35307B9B',
              'HISTORICAL REVIEW': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=759BC306F395D7C284A88AC321DCE0A8',
              'FORECAST DEMAND': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=2D8B83045497F99AE31C9E42C1A5B716',
              'EDIT DEMAND': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=203D7B057DBE69F43A2E07E5112A09F6;mode=view',
              }


app.add_sac_buttons(buttons_dic)

app.root.mainloop()