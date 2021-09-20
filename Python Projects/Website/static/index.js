
  new_user = User(email=email, first_name=firstName, password=generate_password_hash(password1, method='sha256'))
  db.session.add(new_user)
  db.session.commit()
  login_user(new_user, remember=True)
  flash('Account Created', category='success')
  return redirect(url_for('views.home'))
