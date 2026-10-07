import re

with open("src/pages/Register/RegisterPage.tsx", "r") as f:
    content = f.read()

# Let's completely rewrite the render part of RegisterPage.tsx
content = re.sub(r'\{showOtp \? \((.*?)\) : \(\s+<form onSubmit=\{handleSubmit\}(.*?)Google\n              </Button>\n            </form>\n            \)\}', 
                 r'{showOtp ? (\1) : (<form onSubmit={handleSubmit}\2Google\n              </Button>\n            </form>)}', 
                 content, flags=re.DOTALL)

with open("src/pages/Register/RegisterPage.tsx", "w") as f:
    f.write(content)

print("Fixed")
