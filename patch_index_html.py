with open("frontend/index.html", "r") as f:
    content = f.read()

# Make sure Apple touch icon and basic PWA stuff is there
head_injection = """
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="FamilyNest">
    <link rel="apple-touch-icon" href="/icons/icon-192x192.png">
"""

if "apple-mobile-web-app-capable" not in content:
    content = content.replace("</head>", head_injection + "</head>")

with open("frontend/index.html", "w") as f:
    f.write(content)
