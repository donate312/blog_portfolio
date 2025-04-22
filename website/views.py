from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, BlogPost
from . import db
from .forms import BlogPostForm
import json
import os
import logging
from datetime import datetime

views = Blueprint('views', __name__)
blog = Blueprint('blog', __name__)

logging.basicConfig(level=logging.INFO)

def list_files_in_directory(directory_path):
    try:
        if os.path.exists(directory_path):
            return os.listdir(directory_path)
        else:
            logging.warning(f'Directory {directory_path} does not exist.')
    except Exception as e:
        logging.error(f'Error accessing directory {directory_path}: {e}')
    return []

@views.route('/', methods=['GET', 'POST'])
def home():
    if not current_user.is_authenticated:
        return render_template("home.html", user=None)

    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added', category='success')

    return render_template("home.html", user=current_user)

@views.route('/images')
@login_required
def images():
    image_folder = os.path.join(os.getcwd(), 'static', 'images')
    image_list = list_files_in_directory(image_folder)
    return render_template("images.html", images=image_list, user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    note_id = note.get('noteId')
    note = Note.query.get(note_id)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            logging.info(f'Note {note_id} deleted by user {current_user.id}')
            return jsonify({'success': True, 'message': 'Note deleted successfully'})
    logging.warning(f'Unauthorized delete attempt for note {note_id} by user {current_user.id}')
    return jsonify({'success': False, 'message': 'Note not found or unauthorized'}), 404

@views.route('/certs')
def certs():
    certs_folder = os.path.join(os.getcwd(), 'static', 'images')
    certs_list = list_files_in_directory(certs_folder)
    return render_template('certs.html', images=certs_list, user=None)

@blog.route('/post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = BlogPostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            content=form.content.data,
            author=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Blog post created successfully!', category='success')
        return redirect(url_for('blog.view_posts'))
    return render_template('create_post.html', form=form)

@blog.route('/view_posts')
def view_posts():
    # Fetch all blog posts from the database
    posts = BlogPost.query.order_by(BlogPost.id.desc()).all()
    return render_template('view_posts.html', posts=posts)

@blog.route('/delete_post/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    # Delete the post
    db.session.delete(post)
    db.session.commit()
    return '', 204  # Return a 204 No Content response

@blog.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    # Ensure the current user is the author of the post
    if post.author != current_user.id:
        flash('You are not authorized to edit this post.', category='error')
        return redirect(url_for('blog.view_posts'))

    if request.method == 'POST':
        # Update the post with the new data
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        db.session.commit()
        flash('Post updated successfully!', category='success')
        return redirect(url_for('blog.view_posts'))

    return render_template('edit_post.html', post=post)