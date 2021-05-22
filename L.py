import tkinter as tk
from tkinter import ttk
from PIL import (Image, ImageTk)
from webbrowser import open as webopen

def run_experiment(experiment):
    subprocess.run(f'Model\CJFoods_windows-{experiment}.bat')

if __name__ == '__main__':
    root = tk.Tk()
    root.title('ITEconsult Launcher')
    root.iconbitmap(default = 'Resources\iteIcon.ico')
    root.configure(bg = 'grey')
    s = ttk.Style()
    # root.state("zoomed")
    s_width = root.winfo_screenwidth()
    s_height = root.winfo_screenheight()
    # root.minsize(1520, 700)
    # root.resizable(height = False, width = False)
    
    root.resizable(0,0)

    s = ttk.Style()
    s.configure('TFrame', background = 'white smoke')
    s.configure('TLabelframe', background = 'white smoke')
    s.configure('TLabelframe.Label', background = 'white smoke', foreground = 'gray40', font=('Poppins',7,'bold'))
    s.configure('TLabel', background = 'white smoke')
    s.configure('TLoadingWindow.TFrame', background = 'white smoke')
    s.configure('TButton', background = 'snow', foreground = 'gray33', font=('Poppins', 9, 'bold'))

    left_frm = ttk.Frame(root)
    left_frm.pack(side = tk.LEFT, fill = tk.Y)

    buttons_frame = ttk.Frame(left_frm)
    buttons_frame.pack(side = tk.BOTTOM, padx = 10, pady = 10, fill = tk.Y, expand = True)

    read_data_lf = ttk.LabelFrame(buttons_frame, text = 'UPDATE DATA')
    read_data_lf.pack(fill = tk.X, padx = 10, pady = 10)

    read_data_leftframe = ttk.Frame(read_data_lf)
    read_data_lf.columnconfigure(0, weight = 1, uniform = 'read_data')
    read_data_leftframe.grid(pady = 10, row = 0, column = 0, sticky = 'ew')

    update_db_from_SAGE_btn = ttk.Button(read_data_leftframe, width = 20, text = 'READ DATA', command = lambda: update_db_from_SAGE_command(), state = 'disabled')
    update_db_from_SAGE_btn.pack(ipadx = 10, ipady = 2, padx = 20)

    read_data_rightframe = ttk.Frame(read_data_lf)
    read_data_lf.columnconfigure(1, weight = 1, uniform = 'read_data')
    read_data_rightframe.grid(pady = 10, row = 0, column = 1, sticky = 'ew')

    add_manual_input_btn = ttk.Button(read_data_rightframe, width = 20, text = 'MANUAL DATA', command = lambda: add_manual_input(), state = 'disabled')
    add_manual_input_btn.pack(ipadx = 10, ipady = 2, padx = 20)

    run_model_lf = ttk.LabelFrame(buttons_frame, text = 'SELECT EXPERIMENT')
    run_model_lf.pack(fill = tk.X, padx = 10, pady = 10)

    run_model_leftframe = ttk.Frame(run_model_lf)
    run_model_lf.columnconfigure(0, weight = 1, uniform = 'fred')
    run_model_leftframe.grid(pady = 10, row = 0, column = 0, sticky = 'ew')

    run_simulation_canvas = tk.Canvas(run_model_leftframe, width = 120, height = 120, bg = 'white smoke', highlightthickness=0, borderwidth = 0)
    run_simulation_canvas.pack(pady = 15)
    simulation_img = ImageTk.PhotoImage(Image.open("Resources\sim.png").resize((120, 120), Image.ANTIALIAS))
    run_simulation_canvas.create_image(60, 60, anchor = tk.CENTER, image = simulation_img)
    run_simulation_btn = ttk.Button(run_model_leftframe, width = 20, text = 'RUN SIMULATION', command = lambda: threading.Thread(target = run_experiment, args = ('simulation',), daemon = True).start())
    run_simulation_btn.pack(ipadx = 10, ipady = 2, padx = 20)

    run_model_rightframe = ttk.Frame(run_model_lf)
    run_model_lf.columnconfigure(1, weight = 1, uniform = 'fred')
    run_model_rightframe.grid(pady = 10, row = 0, column = 1, sticky = 'ew')

    run_optimization_canvas = tk.Canvas(run_model_rightframe, width = 120, height = 120, bg = 'white smoke', highlightthickness=0, borderwidth = 0)
    run_optimization_canvas.pack(pady = 15)
    optimization_img = ImageTk.PhotoImage(Image.open("Resources\opt.png").resize((120, 120), Image.ANTIALIAS))
    run_optimization_canvas.create_image(60, 60, anchor = tk.CENTER, image = optimization_img)
    run_optimization_btn = ttk.Button(run_model_rightframe, width = 20, text = 'RUN OPTIMIZATION', command = lambda: threading.Thread(target = run_experiment, args = ('optimization',), daemon = True).start())
    run_optimization_btn.pack(ipadx = 10, ipady = 2, padx = 20)

    sac_buttons_lf = ttk.LabelFrame(buttons_frame, text = 'VIEW CLOUD STORIES')
    sac_buttons_lf.pack(fill = tk.X, padx = 10, pady = 10)

    sac_buttons_frm = ttk.Frame(sac_buttons_lf)
    sac_buttons_frm.columnconfigure(0, weight = 1, uniform = 'sac_buttons')
    sac_buttons_frm.columnconfigure(1, weight = 1, uniform = 'sac_buttons')
    sac_buttons_frm.pack(fill = tk.X)

    sac_buttons_leftframe = ttk.Frame(sac_buttons_frm)
    sac_buttons_leftframe.grid(row = 0, column = 0, sticky = 'we')

    sac_buttons_rightframe = ttk.Frame(sac_buttons_frm)
    sac_buttons_rightframe.grid(row = 0, column = 1, sticky = 'we')

    #varname: (title, link)
    buttons_dic = {'DEMAND REVIEW': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=223A9B02F4538FFC82411EFAF07F6A1D',
                  'MASTER DATA ERRORS': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=315A9B02F45146C8478A9C88FAA53442',
                  'RUN SUMMARY': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=4B636301B40D93B66DBA27FC1BF0C2C9',
                  'SCHEDULE REVIEW': 'http://www.google.com/',
                  'REPORT CATALOG': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=home;tab=catalog',
                  'SCHEDULE DETAIL': 'https://ite-consult.br10.hanacloudservices.cloud.sap/sap/fpa/ui/app.html#;view_id=story;storyId=E86A9B02F45046DC9A422670A0016DA9',
                  }

    side = lambda i: sac_buttons_leftframe if i%2 == 0 else sac_buttons_rightframe
    i = 0
    for button in buttons_dic:
        ttk.Button(side(i), width = 20, text = button, command = lambda link = buttons_dic[button]: webopen(link)).pack(padx = 20, pady = 10, ipadx = 10, ipady = 2)
        i += 1

    ite_logo_canvas = tk.Canvas(left_frm, bg = 'steel blue', height = 120, highlightthickness = 0, borderwidth = 0)
    ite_logo_canvas.pack(side = tk.TOP, fill = tk.X, padx = 10)
    img = ImageTk.PhotoImage(Image.open("Resources/newLogo.png").resize((640//3, 177//3), Image.ANTIALIAS)) 
    ite_logo_canvas.create_image(212, 60, anchor = tk.CENTER, image = img) 

    root.mainloop()