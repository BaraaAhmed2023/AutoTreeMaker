import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import json, os

class ProfessionalTreeFolderMaker:
    def __init__(self, root):
        # Root
        self.root = root
        self.root.title("ProfessionalTreeFolderMaker")
        self.root.geometry("700x500")

        # Icons
        self.folder_icon = tk.PhotoImage(file="folder_icon.png")  # put your own small PNG
        self.file_icon = tk.PhotoImage(file="file_icon.png")      # put your own small PNG

        # Style
        style = ttk.Style(root)
        style.configure("Treeview", font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        style.map("Treeview", background=[('selected', '#6cace4')], foreground=[('selected', 'white')])

        # Tree
        self.tree = ttk.Treeview(root, selectmode="extended")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.tree.bind("<B1-Motion>", self.on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self.on_drag_release)

        # Scrollbar
        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Root node
        self.root_node = self.tree.insert("", tk.END, text="Project", open=True, image=self.folder_icon)

        # Context menu
        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="Add Folder", command=self.add_folder)
        self.menu.add_command(label="Add File", command=self.add_file)
        self.menu.add_command(label="Rename", command=self.rename_item)
        self.menu.add_command(label="Delete", command=self.delete_item)
        self.menu.add_separator()
        self.menu.add_command(label="Export to Disk", command=self.export_tree)
        self.menu.add_command(label="Save Tree", command=self.save_tree)
        self.menu.add_command(label="Load Tree", command=self.load_tree)

        # Drag variables
        self.dragging_item = None

    # Drag-and-drop handlers
    def on_drag_start(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.dragging_item = item

    def on_drag_motion(self, event):
        if self.dragging_item:
            self.tree.selection_set(self.dragging_item)

    def on_drag_release(self, event):
        if self.dragging_item:
            target = self.tree.identify_row(event.y)
            if target and target != self.dragging_item:
                self.move_item(self.dragging_item, target)
            self.dragging_item = None

    def move_item(self, item, parent):
        text = self.tree.item(item, "text")
        image = self.tree.item(item, "image")
        new_item = self.tree.insert(parent, tk.END, text=text, image=image)
        for child in self.tree.get_children(item):
            self.move_item(child, new_item)
        self.tree.delete(item)

    # Context menu
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    # Tree operations
    def add_folder(self):
        selected = self.tree.selection() or (self.root_node,)
        name = simpledialog.askstring("Folder Name", "Enter folder name:")
        if name:
            self.tree.insert(selected[0], tk.END, text=name, image=self.folder_icon)

    def add_file(self):
        selected = self.tree.selection() or (self.root_node,)
        name = simpledialog.askstring("File Name", "Enter file name:")
        if name:
            self.tree.insert(selected[0], tk.END, text=name, image=self.file_icon)

    def rename_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        name = simpledialog.askstring("Rename", "Enter new name:")
        if name:
            self.tree.item(selected[0], text=name)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this item?")
        if confirm:
            for item in selected:
                self.tree.delete(item)

    # Save/load tree as JSON
    def tree_to_dict(self, node):
        children = self.tree.get_children(node)
        result = {}
        for child in children:
            text = self.tree.item(child, "text")
            if self.tree.item(child, "image") == str(self.file_icon):
                result[text] = "file"
            else:
                result[text] = self.tree_to_dict(child)
        return result

    def dict_to_tree(self, parent, structure):
        for name, content in structure.items():
            if content == "file":
                self.tree.insert(parent, tk.END, text=name, image=self.file_icon)
            else:
                node = self.tree.insert(parent, tk.END, text=name, image=self.folder_icon)
                self.dict_to_tree(node, content)

    def save_tree(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json")
        if file_path:
            structure = self.tree_to_dict(self.root_node)
            with open(file_path, "w") as f:
                json.dump(structure, f, indent=4)
            messagebox.showinfo("Saved", f"Tree saved to {file_path}")

    def load_tree(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "r") as f:
                structure = json.load(f)
            self.tree.delete(*self.tree.get_children())
            self.root_node = self.tree.insert("", tk.END, text="Project", open=True, image=self.folder_icon)
            self.dict_to_tree(self.root_node, structure)

    # Export tree to disk
    def export_tree(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self._export_node(self.root_node, folder_path)
            messagebox.showinfo("Exported", f"Tree exported to {folder_path}")

    def _export_node(self, node, path):
        for child in self.tree.get_children(node):
            text = self.tree.item(child, "text")
            image = self.tree.item(child, "image")
            if str(image) == str(self.file_icon):
                with open(os.path.join(path, text), "w") as f:
                    f.write("")  # empty file
            else:
                new_path = os.path.join(path, text)
                os.makedirs(new_path, exist_ok=True)
                self._export_node(child, new_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalTreeFolderMaker(root)
    root.mainloop()
