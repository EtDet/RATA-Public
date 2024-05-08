import tkinter as tk
from PIL import Image, ImageTk

class DraggableObject():
    def __init__(self, master, canvas, identifier, bg_image, icon_image):

        self.canvas = canvas
        self.identifier = identifier

        # Load and store images
        self.bg_image = ImageTk.PhotoImage(Image.open(bg_image))
        self.icon_image = ImageTk.PhotoImage(Image.open(icon_image))

        # Create background image
        self.bg_item = canvas.create_image(0, 0, anchor="center", image=self.bg_image, tags=identifier)

        # Create icon image
        self.icon_item = canvas.create_image(5, 5, anchor="center", image=self.icon_image, tags=identifier)

        # Create text labels
        self.label1 = canvas.create_text(30, 30, text="Label 1", anchor="center", tags=identifier)
        self.label2 = canvas.create_text(5, 85, text="Label 2", anchor="center", tags=identifier)

        # Create progress bar rectangles
        self.bar_bg = canvas.create_rectangle(50, 85, 90, 90, fill="gray", tags=identifier)
        self.bar_fg = canvas.create_rectangle(50, 85, 50, 90, fill="green", tags=identifier)

        # Create bottom right image
        self.bottom_image = None

        # Bind mouse events for dragging
        self.canvas.bind("<B1-Motion>", self.on_motion)

        self.x_pos = 0
        self.y_pos = 0

    def on_motion(self, event):
        delta_x = event.x - self.x_pos
        delta_y = event.y - self.y_pos
        #self.canvas.place(x=self.canvas.winfo_x() + delta_x, y=self.canvas.winfo_y() + delta_y)
        self.canvas.move(self.identifier, delta_x, delta_y)

        self.x_pos = event.x
        self.y_pos = event.y

    def set_label1_text(self, text):
        self.canvas.itemconfigure(self.label1, text=text)

    def set_label2_text(self, text):
        self.canvas.itemconfigure(self.label2, text=text)

    def set_progress(self, progress):
        # Assuming progress is a value between 0 and 1
        self.canvas.coords(self.bar_fg, 50, 85, 50 + (40 * progress), 90)

    def set_bottom_image(self, image_path):
        if self.bottom_image:
            self.canvas.delete(self.bottom_image)
        if image_path:
            image = ImageTk.PhotoImage(Image.open(image_path))
            self.bottom_image = self.canvas.create_image(70, 85, anchor="nw", image=image)

    def grayscale_bg(self):
        # Convert background image to grayscale
        grayscale_image = ImageTk.PhotoImage(Image.open("Sprites//Death Knight.png").convert("L"))
        self.canvas.itemconfigure(self.bg_item, image=grayscale_image)
        self.bg_image = grayscale_image

curImage = Image.open("Sprites//E!Ike.png")
modifier = curImage.height/85
resized_image = curImage.resize((int(curImage.width / modifier), 85), Image.LANCZOS)
#curPhoto = ImageTk.PhotoImage(resized_image)

# Usage example
root = tk.Tk()
main_canvas = tk.Canvas(root, width=400, height=400)
main_canvas.pack()
obj1 = DraggableObject(root, main_canvas, "tag1", "Sprites//Death Knight.png", "Sprites//E!Ike.png")
#obj1.place(x=10, y=10)

obj2 = DraggableObject(root, main_canvas, "tag2", "Sprites//Death Knight.png", "Sprites//Anna.png")
#obj2.place(x=100, y=20)

# Update labels
obj1.set_label1_text("2")
obj1.set_label2_text("21")

# Update progress bar
obj1.set_progress(0.75)

root.mainloop()

# I don't think I need to create a new object, just modify the code to select the hero based on the tile clicked
# instead of finding the overlapping image. And drag all elements when overlapped, like I could even have the
# grayscale image there and remain invisible because the component ID is unrelated, man I am a genius.