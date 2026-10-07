import os

f = "frontend/src/components/ui/Dialog.tsx"
with open(f, "r") as file:
    content = file.read()

# Add import for createPortal
if "createPortal" not in content:
    content = content.replace("import { useEffect, useRef } from 'react';", "import { useEffect, useRef } from 'react';\nimport { createPortal } from 'react-dom';")

# For ConfirmDialog
content = content.replace(
    "if (!isOpen) return null;\n\n  return (",
    "if (!isOpen) return null;\n\n  return createPortal("
)

# Replace the closing div of ConfirmDialog
content = content.replace(
    "      </div>\n    </div>\n  );\n}\n\ninterface ModalProps",
    "      </div>\n    </div>,\n    document.body\n  );\n}\n\ninterface ModalProps"
)

# For Modal
content = content.replace(
    "if (!isOpen) return null;\n\n  return (\n    <div\n      role=\"dialog\"",
    "if (!isOpen) return null;\n\n  return createPortal(\n    <div\n      role=\"dialog\""
)

# Replace the closing div of Modal
content = content.replace(
    "        {title ? <ModalBody>{children}</ModalBody> : children}\n      </div>\n    </div>\n  );\n}",
    "        {title ? <ModalBody>{children}</ModalBody> : children}\n      </div>\n    </div>,\n    document.body\n  );\n}"
)

with open(f, "w") as file:
    file.write(content)
print("Done")
