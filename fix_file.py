with open("frontend/src/pages/Register/RegisterPage.tsx", "r") as f:
    code = f.read()
code = code.replace("                    \n                  </button>", "                    )}\n                  </button>")
code = code.replace("            \n            ) : (<form", "            ) : (<form")
with open("frontend/src/pages/Register/RegisterPage.tsx", "w") as f:
    f.write(code)
