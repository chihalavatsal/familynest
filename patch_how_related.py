with open('frontend/src/components/tree/HowRelatedModal.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'import { Modal, ModalHeader } from "../ui/Dialog";',
    'import { Modal, ModalHeader, ModalBody } from "../ui/Dialog";'
)

content = content.replace(
    '<ModalHeader title="How am I related?" onClose={onClose} />\n      <div className="space-y-6">',
    '<ModalHeader title="How am I related?" onClose={onClose} />\n      <ModalBody>\n      <div className="space-y-6">'
)

content = content.replace(
    '        )}\n      </div>\n    </Modal>',
    '        )}\n      </div>\n      </ModalBody>\n    </Modal>'
)

with open('frontend/src/components/tree/HowRelatedModal.tsx', 'w') as f:
    f.write(content)
