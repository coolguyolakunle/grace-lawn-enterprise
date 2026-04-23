import os
from app import db
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app.models import AdminUser, Message, GalleryItem, SiteContent
import cloudinary.uploader

admin = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'webp',
    'mp4', 'mov', 'avi', 'webm'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── AUTH ─────
@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = AdminUser.get()
        if user.username == username and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for('admin.dashboard'))
        error = 'Invalid username or password.'
    return render_template('admin/login.html', error=error)

@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


# ─── DASHBOARD ────
@admin.route('/')
@admin.route('/dashboard')
@login_required
def dashboard():
    gallery = GalleryItem.query.all()
    messages = Message.query.order_by(Message.id.desc()).all()
    unread = Message.query.filter_by(read=False).count()
    return render_template('admin/dashboard.html',
        total_messages=len(messages),
        unread_messages=unread,
        total_gallery=len(gallery),
        recent_messages=messages[:5]
    )


# ─── MESSAGES ──────────
@admin.route('/messages')
@login_required
def messages():
    msgs = Message.query.order_by(Message.id.desc()).all()
    return render_template('admin/messages.html', messages=msgs)

@admin.route('/messages/<int:msg_id>/read', methods=['POST'])
@login_required
def read_message(msg_id):
    msg = Message.query.get(msg_id)
    if msg:
        msg.read = True
        db.session.commit()
    return jsonify({'ok': True})

@admin.route('/messages/<int:msg_id>/delete', methods=['POST'])
@login_required
def del_message(msg_id):
    msg = db.session.get(Message, msg_id)
    if msg:
        db.session.delete(msg)
        db.session.commit()
    flash('Message deleted.', 'success')
    return redirect(url_for('admin.messages'))


# ─── GALLERY ───────
@admin.route('/gallery')
@login_required
def gallery():
    items = GalleryItem.query.order_by(GalleryItem.date.desc()).all()
    return render_template('admin/gallery.html', items=items)


@admin.route('/gallery/upload', methods=['POST'])
@login_required
def upload_image():
    file = request.files.get('image')
    label = request.form.get('label', 'Untitled')
    category = request.form.get('category', 'farm')
    caption = request.form.get('caption', '')

    if not file or not allowed_file(file.filename):
        flash('Invalid file.', 'error')
        return redirect(url_for('admin.gallery'))

    try:
        is_video = file.filename.lower().endswith(('mp4', 'mov', 'avi', 'webm'))

        if is_video:
            result = cloudinary.uploader.upload(
                file,
                resource_type="video",
                folder="gracelawn/gallery"
            )
        else:
            result = cloudinary.uploader.upload(
                file,
                folder="gracelawn/gallery"
            )

        item = GalleryItem(
            image_url=result.get('secure_url'),
            public_id=result.get('public_id'),
            label=label,
            category=category,
            caption=caption,
            media_type="video" if is_video else "image"
        )

        db.session.add(item)
        db.session.commit()

        flash('Upload successful!', 'success')

    except Exception as e:
        print("UPLOAD ERROR:", e)
        flash('Upload failed. Try again.', 'error')

    return redirect(url_for('admin.gallery'))


@admin.route('/gallery/<item_id>/edit', methods=['POST'])
@login_required
def edit_gallery_item(item_id):
    item = GalleryItem.query.get(item_id)

    if not item:
        flash('Item not found.', 'error')
        return redirect(url_for('admin.gallery'))

    item.label = request.form.get('label', '')
    item.category = request.form.get('category', 'farm')
    item.caption = request.form.get('caption', '')

    db.session.commit()

    flash('Image updated.', 'success')
    return redirect(url_for('admin.gallery'))


@admin.route('/gallery/<int:item_id>/delete', methods=['POST'])
@login_required
def del_gallery_item(item_id):
    item = db.session.get(GalleryItem, item_id)

    if item:
        try:
            if item.public_id:
                cloudinary.uploader.destroy(item.public_id, resource_type="video")
        except:
            pass

        db.session.delete(item)
        db.session.commit()

    flash('Image deleted.', 'success')
    return redirect(url_for('admin.gallery'))


# ─── SITE CONTENT ───────
@admin.route('/content', methods=['GET', 'POST'])
@login_required
def content():
    content = SiteContent.query.first()

    if not content:
        content = SiteContent()
        db.session.add(content)
        db.session.commit()

    if request.method == 'POST':
        content.hero_title = request.form.get('hero_title')
        content.hero_subtitle = request.form.get('hero_subtitle')
        content.hero_tagline = request.form.get('hero_tagline')
        content.about_intro = request.form.get('about_intro')
        content.phone = request.form.get('phone')
        content.email = request.form.get('email')
        content.address = request.form.get('address')
        content.facebook = request.form.get('facebook')
        content.instagram = request.form.get('instagram')
        content.whatsapp = request.form.get('whatsapp')
        content.tiktok = request.form.get('tiktok')

        hero_file = request.files.get('hero_image_file')
        if hero_file and allowed_file(hero_file.filename):
            result = cloudinary.uploader.upload(hero_file, folder="gracelawn/hero")
            content.hero_image = result.get('secure_url')

        db.session.commit()

        flash('Content updated successfully!', 'success')
        return redirect(url_for('admin.content'))

    return render_template('admin/content.html', content=content)


# ─── SETTINGS (change password) ──────
@admin.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    error = None
    success = None

    user = AdminUser.query.first()

    if request.method == 'POST':
        current_pw  = request.form.get('current_password', '')
        new_pw      = request.form.get('new_password', '')
        confirm_pw  = request.form.get('confirm_password', '')

        if not user.check_password(current_pw):
            error = 'Current password is incorrect.'

        elif len(new_pw) < 6:
            error = 'New password must be at least 6 characters.'

        elif new_pw != confirm_pw:
            error = 'Passwords do not match.'

        else:
            user.password_hash = generate_password_hash(new_pw)

            new_username = request.form.get('username', '').strip()
            if new_username:
                user.username = new_username

            db.session.commit()
            success = 'Settings updated successfully!'

    return render_template('admin/settings.html', error=error, success=success)


# ─── PUBLIC CONTACT FORM HANDLER ────
@admin.route('/submit-contact', methods=['POST'])
def submit_contact():
    data = request.get_json() or request.form.to_dict()

    if not data.get('email') or not data.get('message'):
        return jsonify({'ok': False, 'error': 'Missing required fields'}), 400

    new_message = Message(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        subject=data.get('subject'),
        message=data.get('message'),
        read=False
    )

    db.session.add(new_message)
    db.session.commit()

    return jsonify({'ok': True, 'message': 'Message received!'})

# --- EXTRA ADMIN TOOL (GENERATE RESET LINK) ─────
@admin.route('/generate-reset-link')
@login_required
def generate_reset_link():
    user = AdminUser.query.first()
    token = user.generate_reset_token()

    reset_url = url_for('admin.reset_password', token=token, _external=True)

    return f"Reset link (valid 15 mins): <a href='{reset_url}'>{reset_url}</a>"
