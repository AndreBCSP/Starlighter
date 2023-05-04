import os
from tkinter import filedialog

import customtkinter
import starlighter as starlight
from PIL import Image

image_folder = ''
model_name = ''
model_path = ''
imagej_roi = ''
photo_number = ''



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()


        self.title("Starlighter")
        self.geometry("900x650")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "starburst.png")), size=(60, 60))
        
        self.iconbitmap(os.path.join(image_path, "starburst.ico"))
        

        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_light.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(30, 30))
        self.fdist_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "fdistari_icon.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "fdistari_icon.png")), size=(30, 30))
        self.nonap_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "nonapari_icon.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "nonapari_icon.png")), size=(30, 30))
        self.stradi_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "plot_light_icon.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "plot_light_icon.png")), size=(30, 30))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Starlighter", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=25, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)




        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event, font=customtkinter.CTkFont(size=20))
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.fdistari_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  FDistari",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.fdist_image, anchor="w", command=self.fdistari_button_event, font=customtkinter.CTkFont(size=20))
        self.fdistari_button.grid(row=2, column=0, sticky="ew")

        self.nonapari_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  NoNapari",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.nonap_image, anchor="w", command=self.nonapari_button_event, font=customtkinter.CTkFont(size=20))
        self.nonapari_button.grid(row=3, column=0, sticky="ew")

        self.stradivari_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  Stradivari",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.stradi_image, anchor="w", command=self.stradivari_button_event, font=customtkinter.CTkFont(size=20))
        self.stradivari_button.grid(row=4, column=0, sticky="ew")


        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(3, weight=1)
        self.home_frame.grid_rowconfigure(7, weight=1)

        self.home_title = customtkinter.CTkLabel(self.home_frame, text="How it works", font=customtkinter.CTkFont(size=50))
        self.home_title.grid(row=0, column=0)

        self.home_explanation_1 = customtkinter.CTkLabel(self.home_frame, text='1. Introduce the image folder and the model folder', font=customtkinter.CTkFont(size=15))
        self.home_explanation_1.grid(row=1, column=0)
        

        self.choose_image_folder_1 = customtkinter.CTkButton(self.home_frame, text='Choose image folder', command=self.get_folder1)
        self.choose_image_folder_1.grid(row=2, column=0, padx=20, pady=10)

        self.image_folder_path = customtkinter.CTkLabel(self.home_frame, text="", compound="left", fg_color=("gray75", "gray25"), font=customtkinter.CTkFont(size=10))
        self.image_folder_path.grid(row=2, column=1, padx=20, pady=20)

        self.model_name_entry = customtkinter.CTkEntry(self.home_frame, placeholder_text='Insert here the model folder name')
        self.model_name_entry.grid(row=3, column=0)

        self.model_name_entry_button = customtkinter.CTkButton(self.home_frame, text='Set', command=self.model_name_entry_get)
        self.model_name_entry_button.grid(row=4, column=0)

        self.choose_model_folder = customtkinter.CTkButton(self.home_frame, text='Choose model folder', command=self.get_folder2)
        self.choose_model_folder.grid(row=5, column=0, padx=20, pady=10)


        self.model_folder_path = customtkinter.CTkLabel(self.home_frame, text="", compound="left", fg_color=("gray75", "gray25"), font=customtkinter.CTkFont(size=10))
        self.model_folder_path.grid(row=5, column=1, padx=20, pady=20)

        self.home_explanation_2 = customtkinter.CTkLabel(self.home_frame, text='      2. Go to the menus on the left and check your options and inputs', font=customtkinter.CTkFont(size=15))
        self.home_explanation_2.grid(row=6, column=0)

        self.run_button = customtkinter.CTkButton(self.home_frame, text='Run', command=self.run_starlighter)
        self.run_button.grid(row=7, column=2)

        self.reset_button = customtkinter. CTkButton(self.home_frame, text='Reset', command=self.reset_event)
        self.reset_button.grid(row=7, column=3)



        # create second frame
        self.fdistari_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.fdistari_frame.grid_rowconfigure(5, weight=2)
        self.fdistari_frame.grid_columnconfigure(5, weight=2)


        self.check_var = customtkinter.StringVar(value='off')
        self.checkbox = customtkinter.CTkCheckBox(self.fdistari_frame, text="Export ImageJ ROIs", command=self.checkbox_imagej_roi,
                                     variable=self.check_var, onvalue="on", offvalue="off")
        self.checkbox.grid(row=1, column=1)

        self.fdistari_explanation_1 = customtkinter.CTkLabel(self.fdistari_frame, text='  Tick this box if you want the program to output ImageJ ROI files too:   ', font=customtkinter.CTkFont(size=15))
        self.fdistari_explanation_1.grid(row=1, column=0)

        self.blank_line_1 = customtkinter.CTkLabel(self.fdistari_frame, text="", font=customtkinter.CTkFont(size=5))
        self.blank_line_1.grid(row=0, column=0, padx=5, pady=5)


        # create third frame
        self.nonapari_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.nonapari_frame.grid_rowconfigure(5, weight=1)
        self.nonapari_frame.grid_columnconfigure(5, weight=1)




        self.photo_number_entry = customtkinter.CTkEntry(self.nonapari_frame, placeholder_text='Insert here the number')
        self.photo_number_entry.grid(row=3, column=0)

        self.photo_number_entry_button = customtkinter.CTkButton(self.nonapari_frame, text='Set', command=self.photo_number_entry_get)
        self.photo_number_entry_button.grid(row=4, column=0)

        self.nonapari_explanation = customtkinter.CTkLabel(self.nonapari_frame, text="  In your folder you have a Brightfield image and then the fluorescence images.", font=customtkinter.CTkFont(size=15))
        self.nonapari_explanation.grid(row=0, column=0, padx=20, pady=20)

        self.nonapari_explanation_2 = customtkinter.CTkLabel(self.nonapari_frame, text="  If you want to quantify, for example, GFP, and it is the second photo, write 2.", font=customtkinter.CTkFont(size=15))
        self.nonapari_explanation_2.grid(row=1, column=0, padx=20, pady=20)
        

        # create third frame
        self.stradivari_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
       
        # select default frame
        self.select_frame_by_name("Home")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "Home" else "transparent")
        self.fdistari_button.configure(fg_color=("gray75", "gray25") if name == "FDistari" else "transparent")
        self.nonapari_button.configure(fg_color=("gray75", "gray25") if name == "NoNapari" else "transparent")
        self.stradivari_button.configure(fg_color=("gray75", "gray25") if name == "Stradivari" else "transparent")


        # show selected frame
        if name == "Home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "FDistari":
            self.fdistari_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.fdistari_frame.grid_forget()
        if name == "NoNapari":
            self.nonapari_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.nonapari_frame.grid_forget()
        if name == "Stradivari":
            self.stradivari_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.stradivari_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("Home")

    def fdistari_button_event(self):
        self.select_frame_by_name("FDistari")

    def nonapari_button_event(self):
        self.select_frame_by_name("NoNapari")

    def stradivari_button_event(self):
        self.select_frame_by_name("Stradivari")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)



    

    def get_folder1(self):
        global image_folder
        image_folder = filedialog.askdirectory()
        self.image_folder_path.configure(text=image_folder)
        
    def get_folder2(self):
        global model_path, model_name
        model_path = filedialog.askdirectory()
        self.model_folder_path.configure(text=f'Model: {model_name}     in: {model_path}')
    
    def photo_number_entry_get(self):
            photo_number_string = self.photo_number_entry.get()
            global photo_number
            photo_number = int(photo_number_string)

    def model_name_entry_get(self):
            global model_name

            model_name = self.model_name_entry.get()
           
    def checkbox_imagej_roi(self):
            global imagej_roi
            if self.check_var.get() == 'on':
                imagej_roi = True
            elif self.check_var.get() == 'off':
                imagej_roi = False

    def run_starlighter(self):
        starlight.fdistari(image_folder, model_name, model_path, imagej_roi)
        starlight.nonapari(image_folder, photo_number)
        starlight.stradivari(image_folder)

    def reset_event(self):
        starlight.reset(image_folder)

if __name__ == "__main__":
    app = App()
    app.mainloop()



print(f'The image folder path is: {image_folder}')
print(f'The model name is : {model_name}')
print(f'The model folder path is: {model_path}')

if imagej_roi:
    print(f'ImageJ ROI will be exported')
elif not imagej_roi:
    print(f"ImageJ ROI won't be exported")

print(f'The photo number is {photo_number}')
