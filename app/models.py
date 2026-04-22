from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


# ─────────────────────────────────────────────
# ADMIN USER
# ─────────────────────────────────────────────
class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get():
        user = AdminUser.query.first()
        if not user:
            user = AdminUser(username="admin")
            user.set_password("admin123")
            db.session.add(user)
            db.session.commit()
        return user


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


# ─────────────────────────────────────────────
# MESSAGES (CONTACT FORM)
# ─────────────────────────────────────────────
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)

    read = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


def save_message(data):
    msg = Message(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        email=data.get("email"),
        phone=data.get("phone"),
        subject=data.get("subject"),
        message=data.get("message"),
    )
    db.session.add(msg)
    db.session.commit()
    return msg


def mark_message_read(msg_id):
    msg = Message.query.get(msg_id)
    if msg:
        msg.read = True
        db.session.commit()


def delete_message(msg_id):
    msg = Message.query.get(msg_id)
    if msg:
        db.session.delete(msg)
        db.session.commit()


# ─────────────────────────────────────────────
# SITE CONTENT (SINGLE ROW TABLE)
# ─────────────────────────────────────────────
class SiteContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    hero_title = db.Column(db.String(255))
    hero_subtitle = db.Column(db.String(255))
    hero_tagline = db.Column(db.Text)
    hero_image = db.Column(db.String(255))

    about_intro = db.Column(db.Text)

    phone = db.Column(db.String(100))
    email = db.Column(db.String(120))
    address = db.Column(db.String(255))

    facebook = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    whatsapp = db.Column(db.String(255))
    tiktok = db.Column(db.String(255))


DEFAULT_CONTENT = {
    "hero_title": "Grace Lawn",
    "hero_subtitle": "Enterprise",
    "hero_tagline": "First-class pig farming rooted in excellence...",
    "hero_image": "",
    "about_intro": "Gracelawn is a first-class pig farm in Lagos.",
    "phone": "tel:+2348137561656",
    "email": "gracelawn@yahoo.com",
    "address": "Badagry, Lagos State, Nigeria",
    "facebook": "https://facebook.com/gracelawnenterprise",
    "instagram": "https://instagram.com/gracelawnenterprise",
    "whatsapp": "https://wa.me/2348137561656",
    "tiktok": "https://tiktok.com/@gracelawnenterprise",
}


def get_content():
    content = SiteContent.query.first()
    if not content:
        content = SiteContent(**DEFAULT_CONTENT)
        db.session.add(content)
        db.session.commit()
    return content


def save_content(data):
    content = get_content()

    for key, value in data.items():
        if hasattr(content, key):
            setattr(content, key, value)

    db.session.commit()


# ─────────────────────────────────────────────
# GALLERY (CLOUDINARY BASED)
# ─────────────────────────────────────────────
class GalleryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    image_url = db.Column(db.Text, nullable=False)
    public_id = db.Column(db.String(255), nullable=False)

    label = db.Column(db.String(255))
    category = db.Column(db.String(100))
    caption = db.Column(db.Text)

    date = db.Column(db.DateTime, default=datetime.utcnow)


def get_gallery():
    return GalleryItem.query.order_by(GalleryItem.date.desc()).all()


def add_gallery_item(image_url, public_id, label, category, caption=""):
    item = GalleryItem(
        image_url=image_url,
        public_id=public_id,
        label=label,
        category=category,
        caption=caption,
    )
    db.session.add(item)
    db.session.commit()
    return item


def update_gallery_item(item_id, label, category, caption):
    item = GalleryItem.query.get(item_id)
    if item:
        item.label = label
        item.category = category
        item.caption = caption
        db.session.commit()


def delete_gallery_item(item_id):
    item = GalleryItem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return item
    return None