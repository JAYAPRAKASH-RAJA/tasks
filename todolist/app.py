
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import os

tasks = []
editing_task = None  # Tracks the task being edited
DIST_DIR = './dist'

os.makedirs(DIST_DIR, exist_ok=True)  # Ensure dist directory exists

class TodoHandler(BaseHTTPRequestHandler):
    def render(self):
        with open(os.path.join(DIST_DIR, "index.html"), "r") as file:
            html = file.read()

        task_list = ""
        for task in tasks:
            if task == editing_task:
                task_list += f"""
                <li>
                    <form action="/save" method="post" style="display:flex; align-items:center;">
                        <input type="hidden" name="old_task" value="{task}">
                        <input type="text" name="new_task" value="{task}" class="task-input" required>
                        <button type="submit" class="save-btn">Save</button>
                        <a href="/" class="cancel-btn" style="margin-left: 10px;">Cancel</a>
                    </form>
                </li>
                """
            else:
                task_list += f"""
                <li>
                    <span class="task">{task}</span>
                    <form action="/edit" method="post" style="display:inline;">
                        <input type="hidden" name="task" value="{task}">
                        <button type="submit" class="edit-btn">Edit</button>
                    </form>
                    <form action="/delete" method="post" style="display:inline;">
                        <input type="hidden" name="task" value="{task}">
                        <button type="submit" class="delete-btn">Delete</button>
                    </form>
                </li>
                """

        html = html.replace("<!-- Tasks will be dynamically rendered here -->", task_list)
        return html

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.render().encode())
        elif self.path == "/styles.css":
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            with open(os.path.join(DIST_DIR, "styles.css"), "r") as file:
                self.wfile.write(file.read().encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global editing_task

        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = parse_qs(post_data.decode())

        if self.path == "/add":
            task = data.get("task", [""])[0]
            if task:
                tasks.append(task)
            self.redirect("/")

        elif self.path == "/delete":
            task = data.get("task", [""])[0]
            if task in tasks:
                tasks.remove(task)
            self.redirect("/")

        elif self.path == "/edit":
            editing_task = data.get("task", [""])[0]
            self.redirect("/")

        elif self.path == "/save":
            old_task = data.get("old_task", [""])[0]
            new_task = data.get("new_task", [""])[0]
            if old_task in tasks and new_task:
                tasks[tasks.index(old_task)] = new_task
            editing_task = None
            self.redirect("/")

    def redirect(self, location):
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()


if __name__ == "__main__":
    PORT = 8000
    server = HTTPServer(("0.0.0.0", PORT), TodoHandler)
    print(f"Server running at http://localhost:{PORT}")
    server.serve_forever()
