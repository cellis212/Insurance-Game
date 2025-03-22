# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

import os
import sys
import shutil
import webbrowser
import http.server
import socketserver
import threading
import time

def copy_files_for_debug():
    """Copy main game files to a debug directory with added logging."""
    print("Setting up debug environment...")
    
    # Create debug directory
    if os.path.exists("debug"):
        shutil.rmtree("debug")
    os.makedirs("debug")
    
    # Copy all .py files and modify them to add logging
    for root, dirs, files in os.walk("."):
        # Skip debug directory, __pycache__ and any other hidden folders
        if "/." in root or root.startswith("./.") or "/__" in root or "/debug" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                src_path = os.path.join(root, file)
                if root == ".":
                    dst_path = os.path.join("debug", file)
                else:
                    subdir = root[2:]  # Remove ./ from path
                    os.makedirs(os.path.join("debug", subdir), exist_ok=True)
                    dst_path = os.path.join("debug", subdir, file)
                
                # Read the file and add logging
                with open(src_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add console.log for browser debugging
                if "main.py" in src_path:
                    # Add extra logging to main.py
                    content = content.replace('print("Game initialized successfully!")',
                                             'print("Game initialized successfully!")\n    import javascript\n    javascript.console.log("Game initialized in browser!")')
                    
                    # Add error logging for browser
                    content = content.replace('except Exception as e:',
                                             'except Exception as e:\n            import javascript\n            javascript.console.error(f"Error: {str(e)}")')
                
                # Write the modified file
                with open(dst_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    # Copy non-py files as-is
    for root, dirs, files in os.walk("."):
        # Skip debug directory, __pycache__ and any other hidden folders
        if "/." in root or root.startswith("./.") or "/__" in root or "/debug" in root:
            continue
            
        for file in files:
            if not file.endswith(".py") and not file.endswith(".pyc"):
                src_path = os.path.join(root, file)
                if root == ".":
                    dst_path = os.path.join("debug", file)
                else:
                    subdir = root[2:]  # Remove ./ from path
                    os.makedirs(os.path.join("debug", subdir), exist_ok=True)
                    dst_path = os.path.join("debug", subdir, file)
                
                # Copy the file
                shutil.copy2(src_path, dst_path)
    
    print("Debug environment created in the 'debug' directory")

def start_server(port=8080):
    """Start a simple HTTP server to serve the debug files."""
    os.chdir("debug")
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    print(f"Serving debug version at http://localhost:{port}")
    httpd.serve_forever()

def main():
    """Main entry point for the debug script."""
    # Setup debug environment
    copy_files_for_debug()
    
    # Start server in a separate thread
    port = 8080
    server_thread = threading.Thread(target=start_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()
    
    # Open browser
    time.sleep(1)  # Wait for server to start
    webbrowser.open(f"http://localhost:{port}")
    
    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main() 