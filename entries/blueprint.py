import os
from app import app, db
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask import g
from flask.ext.login import login_required
from werkzeug import secure_filename
from helpers import object_list
from models import Entry, Tag
from entries.forms import EntryForm, ImageForm

entries = Blueprint('entries', __name__, template_folder='templates')

def get_entry_or_404(slug, author=None):
    query = Entry.query.filter(Entry.slug == slug)
    if author:
        query = query.filter(Entry.author == author)
    else:
        query = filter_status_by_user(query)
    return query.first_or_404()

def filter_status_by_user(query):
    if not g.user.is_authenticated:
        return query.filter(Entry.status == Entry.STATUS_PUBLIC)
    else:
        return query.filter(Entry.status.in_((Entry.STATUS_PUBLIC, Entry.STATUS_DRAFT)))

def entry_list(template, query, **context):
    valid_statuses = (Entry.STATUS_PUBLIC, Entry.STATUS_DRAFT)
    query = query.filter(Entry.status.in_(valid_statuses))
    if request.args.get('q'):
        search = request.args.get('q')
        query = query.filter(
        (Entry.body.contains(search)) | (Entry.title.contains(search)))
    return object_list(template, query, **context)

def get_entry_or_404(slug):
    valid_statuses = (Entry.STATUS_PUBLIC, Entry.STATUS_DRAFT)
    (Entry.query
        .filter((Entry.slug == slug) & (Entry.status.in_(valid_statuses)))
        .first_or_404()
        )
@entries.route('/image-upload/', methods=['GET', 'POST'])
@login_required
def image_upload():
    if request.method == 'POST':
        form = ImageForm(request.form)
        if form.validate():
            image_file = request.files['file']
            filename = os.path.join(app.config['IMAGES_DIR'],
                                    secure_filename(image_file.filename))
            image_file_save(filename)
            flash('Saved {}'.format(os.path.basename(filename)), 'success')
            return redirect (url_form('entries.index'))
    else:
        form = ImageForm()

    return render_template('entries/image_upload.html', form=form)

@entries.route('/')
def index():
    entries = Entry.query.order_by(Entry.created_timestamp.desc())
    return entry_list('entries/index.html', entries)

@entries.route('/tags/')
def tag_index():
    tags = Tag.query.order_by(Tag.name)
    return object_list('entries/tag_index.html', tags)

@entries.route('/tags/<slug>/')
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug == slug).first_or_404()
    entries = tag.entries.order_by(Entry.created_timestamp.desc())
    return object_list('entries/tag_detail.html', entries, tag=tag)

from app import db
@entries.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        form = EntryForm(request.form)
        if form.validate():
            entry = form.save_entry(Entry(author=g.user))
            db.session.add(entry)
            db.session.commit()
            flash('Entry "%s" created succesfully!'% entry.title, 'success')
            return redirect(url_for('entries.detail', slug=entry.slug))
    else:
        form = EntryForm()
    return render_template('entries/create.html', form=form)

@entries.route('/<slug>/')
def detail(slug):
    # if slug is None:
    #     slug = request.args.get('slug')
    entry = get_entry_or_404(slug)
    return render_template('entries/detail.html', entry=entry)

@entries.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    entry = get_entry_or_404(slug, author=None)
    if request.method == 'POST':
        form = EntryForm(request.form, obj=entry)
        if form.validate():
            entry = form.save_entry(entry)
            db.session.add(entry)
            db.session.commit()
            flash('Entry "%s" has been edited and saved!' % entry.title, 'success')
            return redirect(url_for('entries.detail', slug=entry.slug))
    else:
        form = EntryForm(obj=entry)
    return render_template('entries/edit.html', entry=entry, form=form)

@entries.route('/<slug>/delete/', methods=['GET', 'POST'])
@login_required
def delete(slug):
    entry = get_entry_or_404(slug, author=None)
    if request.method == 'POST':
        entry.status = Entry.STATUS_DELETED
        db.session.add(entry)
        db.session.commit()
        flash('Entry "%s" has been deleted!' % entry.title, 'success')
        return redirect(url_for('entries.index'))
    return render_template('entries/delete.html', entry=entry)
