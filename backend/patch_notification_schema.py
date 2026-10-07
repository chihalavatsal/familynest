with open("app/schemas/notification.py", "r") as f:
    content = f.read()

replacement = """class NotificationResponse(BaseModel):
    id: uuid.UUID
    notification_type: str
    title: str
    body: str
    is_read: bool
    created_at: datetime
    target_type: Optional[str] = None
    target_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)"""

content = content.replace("""class NotificationResponse(BaseModel):
    id: uuid.UUID
    notification_type: str
    title: str
    body: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)""", replacement)

with open("app/schemas/notification.py", "w") as f:
    f.write(content)
