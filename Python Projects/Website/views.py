from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.sql.expression import update
from sqlalchemy.sql.functions import user
from .models import Note
from . import db
import json
from werkzeug.wrappers import request
views = Blueprint('views', __name__)
up = True
data = ''
@views.route('/')
def home():
    return render_template("home.html", index = "index.js", user=current_user)

@views.route('/delete-note/<noteId>', methods=['POST', 'GET'])
def delete_note(noteId):
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
              db.session.delete(note)
              db.session.commit()
    return redirect(url_for('auth.notes'))

