from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app
from app.models import create_user, get_user, create_post, get_posts, update_user_profile, get_user_info, perform_user_search, get_posts_except_user_with_username
from app.models import add_comment, like_post, dislike_post, like_comment, dislike_comment

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and user[2] == password:  # Assuming password is at index 2
            session['user_id'] = user[3]  # Assuming user_id is at index 3
            return redirect(url_for('profile'))
        else:
            return render_template('login.html', error=True)
    return render_template('login.html', error=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if get_user(username):
            return render_template('register.html', error=True)
        create_user(username, password, email)
        return redirect(url_for('login'))
    return render_template('register.html', error=False)

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        user_info = get_user_info(user_id)
        
        # Fetch all posts except those of the current user, with usernames and comments
        all_posts_except_user = get_posts_except_user_with_username(user_id)
        username = user_info['username']
        return render_template('profile.html', all_posts_except_user=all_posts_except_user, welcome_message=f"Welcome, {username}!", user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = session['user_id']
        content = request.form['content']
        create_post(user_id, content)
        flash('Post successfully created!', 'success')
        return redirect(url_for('my_posts'))
    
    # GET request - show the create post form
    user_id = session['user_id']
    user_info = get_user_info(user_id)
    return render_template('create.html', user_info=user_info)

@app.route('/my_posts')
def my_posts():
    if 'user_id' in session:
        user_id = session['user_id']
        user_info = get_user_info(user_id)
        
        # Fetch previous posts of the current user
        previous_posts = get_posts(user_id)
        username = user_info['username']
        return render_template('my_posts.html', previous_posts=previous_posts, welcome_message=f"Welcome, {username}!", user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/add_post', methods=['POST'])
def add_post():
    if 'user_id' in session:
        user_id = session['user_id']
        content = request.form['content']
        create_post(user_id, content)
        flash('Post successfully created!', 'success')
        return redirect(url_for('my_posts'))
    else:
        return redirect(url_for('login'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' in session:
        user_id = session['user_id']
        phone_number = request.form['phone_number']
        bio = request.form['bio']
        update_user_profile(user_id, phone_number, bio)
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    else:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

@app.route('/about')
def about():
    if 'user_id' in session:
        user_id = session['user_id']
        user_info = get_user_info(user_id)
        return render_template('about.html', welcome_message="Welcome to the About page!", user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/search')
def search_user():
    username = request.args.get('username')
    if username:
        users_data = perform_user_search(username)
        if users_data:
            return render_template('search_results.html', users_data=users_data)
    flash('No user found.', 'error')
    return redirect(url_for('profile'))

@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    if 'user_id' in session:
        # Changed to match the template form field name
        comment_text = request.form['comment_content']  # This now matches the template
        user_id = session['user_id']
        add_comment(post_id, user_id, comment_text)
        flash('Comment added successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/like/<int:post_id>', methods=['POST'])
def like(post_id):
    if 'user_id' in session:
        user_id = session['user_id']
        like_post(post_id, user_id)
    return redirect(url_for('profile'))

@app.route('/dislike/<int:post_id>', methods=['POST'])
def dislike(post_id):
    if 'user_id' in session:
        user_id = session['user_id']
        dislike_post(post_id, user_id)
    return redirect(url_for('profile'))

@app.route('/like_comment/<int:comment_id>', methods=['POST'])
def like_comment_route(comment_id):
    if 'user_id' in session:
        user_id = session['user_id']
        like_comment(comment_id, user_id)
        return jsonify({'success': True, 'message': 'Comment liked successfully'})
    return jsonify({'success': False, 'message': 'User not logged in'}), 401

@app.route('/dislike_comment/<int:comment_id>', methods=['POST'])
def dislike_comment_route(comment_id):
    if 'user_id' in session:
        user_id = session['user_id']
        dislike_comment(comment_id, user_id)
        return jsonify({'success': True, 'message': 'Comment disliked successfully'})
    return jsonify({'success': False, 'message': 'User not logged in'}), 401