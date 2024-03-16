import tkinter as tk

class RectAnimationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rectangle Animation")

        self.canvas = tk.Canvas(root, width=400, height=300, bg='white')
        self.canvas.pack()

        self.rectangles = []
        for i in range(4):
            rect = self.canvas.create_rectangle(50 + i * 100, 10, 150 + i * 100, 50, fill='blue')
            self.rectangles.append(rect)

        self.start_button = tk.Button(root, text="Start Animation", command=self.start_animation)
        self.start_button.pack(side=tk.RIGHT)

        self.animating = False  # Flag to track ongoing animation
        self.animation_done = False

    def start_animation(self):
        if not self.animating:
            self.animating = True
            self.animate_rectangles()
        else:
            self.snap_to_final_positions()
            self.animating = False
            self.ending_animation_trigger()

    def animate_rectangles(self):
        steps = 50

        for i, rect in enumerate(self.rectangles):
            self.animate_single_rectangle(rect, i)
        # initiate animation to end after set amount of time

        delay = len(self.rectangles)-1

        print(delay * steps * 50 + 50 * steps)

        self.root.after(delay * steps * 50 + 50 * steps, self.ending_animation_trigger)

    def animate_single_rectangle(self, rect, delay):
        target_y = 200  # Adjust this value based on the final position of the rectangles
        current_y = self.canvas.coords(rect)[1]
        distance = target_y - current_y

        steps = 50
        step_distance = distance / steps

        for step in range(steps):
            print(delay * steps * 50 + step * 50)
            self.root.after(delay * steps * 50 + step * 50, self.move_rect_step, rect, step_distance)

    def move_rect_step(self, rect, step_distance):
        if self.animation_done: return
        self.canvas.move(rect, 0, step_distance)

    def ending_animation_trigger(self):
        print('yes')
        self.animation_done = True

    def snap_to_final_positions(self):
        # Snap all rectangles to their final positions instantly
        for i, rect in enumerate(self.rectangles):
            target_y = 200  # Adjust this value based on the final position of the rectangles
            current_y = self.canvas.coords(rect)[1]
            distance = target_y - current_y
            self.canvas.move(rect, 0, distance)

        self.animating = False


if __name__ == "__main__":
    root = tk.Tk()
    app = RectAnimationApp(root)
    root.mainloop()
