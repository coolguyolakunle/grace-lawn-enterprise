from flask import Blueprint, render_template
from app.models import SiteContent, get_gallery

main = Blueprint('main', __name__)


def get_site_content():
    """Always fetch latest site content safely"""
    return SiteContent.query.first()


@main.route('/')
def index():
    return render_template(
        'main/index.html',
        content=get_site_content()
    )


@main.route('/about')
def about():
    return render_template(
        'main/about.html',
        content=get_site_content()
    )


@main.route('/gallery')
def gallery():
    return render_template(
        'main/gallery.html',
        items=get_gallery(),
        content=get_site_content()
    )


@main.route('/contact')
def contact():
    return render_template(
        'main/contact.html',
        content=get_site_content()
    )


@main.route('/terms')
def terms():
    return render_template(
        'main/terms.html',
        content=get_site_content()
    )