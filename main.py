import tkinter as tk
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import messagebox, ttk
from ConnDB import connection

root = tk.Tk()
root.title('Голосование за фильм')
root.geometry("600x500")
root.resizable(height=False,width=False)
label = tk.Label(text="Голосование", font=48,fg="#87F")
label.pack()
label = tk.Label(text="Выбери свой любимый фильм\n",font=48,fg="#092")
label.pack()

genres = []
with connection.cursor() as cursor:
    cursor.execute("""SELECT * FROM Genres""")
    result = cursor.fetchall()
    for i in result:
        genres.append(f"{i['id']}: {i['Name']}")

canvas = tk.Canvas(root)
canvas.pack(side="left", fill="both", expand=True)
scrollbar = tk.Scrollbar(root, command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.config(yscrollcommand=scrollbar.set)
frame = tk.Frame(canvas)
canvas.create_window(0, 0, anchor="nw", window=frame)
frame.update_idletasks()
canvas.configure(scrollregion=canvas.bbox("all"))

check = tk.IntVar()
combobox = ttk.Combobox(values=genres)
combobox["state"] = 'readonly'
combobox.pack()

def Select():
    for widget in frame.winfo_children():
        widget.destroy()
    selectstate = combobox.get()
    selectstate = selectstate.split(":")
    print(selectstate)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT * from Film WHERE Genre = {selectstate[0]}""")
            result = cursor.fetchall()
            for d, i in enumerate(result):
                bytes = i['Picture']
                radiobutton = tk.Radiobutton(frame, text=i['Name'], variable=check, value=i['id'])
                radiobutton.pack(anchor="w")
                image = Image.open(BytesIO(bytes))
                image = image.resize((50, 70), Image.LANCZOS)
                image = ImageTk.PhotoImage(image)
                picture = tk.Label(frame, image=image)
                picture.image = image
                picture.pack(anchor="w")

    except Exception as ex:
        messagebox.showerror(title="Ошибка",message=ex)

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

frame.bind("<Configure>", on_frame_configure)
combobox.bind("<<ComboboxSelected>>", lambda event: Select())

def vote():
    with connection.cursor() as cursor:
        select = check.get()
        if select < 1:
            messagebox.showwarning(title="Информация", message="Вы не выбрали фильм.")
        else:
            cursor.execute(f"""UPDATE `Film` SET `Rating` = (`Rating` + 1) WHERE id = {select}""")
            connection.commit()
            connection.close()
            messagebox.showinfo(title="Информация", message="Вы успешно проголосовали.")
            quit()

Send = tk.Button(root, text="Проголосовать", command=vote)
Send.pack(anchor='e', side='bottom')

root.mainloop()
