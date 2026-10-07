import os

f = "frontend/index.html"
with open(f, "r") as file:
    content = file.read()

script = """
    <script>
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(function(registrations) {
          for(let registration of registrations) {
            registration.unregister();
          }
        });
      }
    </script>
"""

if "registration.unregister();" not in content:
    content = content.replace("</head>", f"{script}</head>")
    with open(f, "w") as file:
        file.write(content)

print("Done")
