import tkinter as tk


def create_point():
    # Create the main application window
    window = tk.Tk()

    # Create Label widgets
    label_name = tk.Label(window, text="Name")
    label_x = tk.Label(window, text="X Position")
    label_y = tk.Label(window, text="Y Position")

    # Create Entry widgets
    entry_name = tk.Entry(window)
    entry_x = tk.Entry(window)
    entry_y = tk.Entry(window)

    # Create a list to store the values
    values = []

    # Function to handle button click
    def on_create_click():
        name = entry_name.get()
        x = entry_x.get()
        y = entry_y.get()
        window.destroy()
        # Store the values in the list
        values.extend([name, int(x), int(y)])

    # Create Button widget
    button_create = tk.Button(window, text="Create", command=on_create_click)

    # Define the layout of the widgets
    label_name.grid(row=0, column=0)
    entry_name.grid(row=0, column=1)
    label_x.grid(row=1, column=0)
    entry_x.grid(row=1, column=1)
    label_y.grid(row=2, column=0)
    entry_y.grid(row=2, column=1)
    button_create.grid(row=3, column=0, columnspan=2)

    # Start the Tkinter event loop
    window.mainloop()

    # Return the values
    return values

print(create_point())
