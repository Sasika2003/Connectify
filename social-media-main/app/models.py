from app import mysql
import MySQLdb

def create_user(username, password, email):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
    mysql.connection.commit()
    cur.close()

def get_user(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    return user

def create_post(user_id, content):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO posts (user_id, content) VALUES (%s, %s)", (user_id, content))
    mysql.connection.commit()
    cur.close()

def get_posts(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts WHERE user_id = %s", (user_id,))
    posts = cur.fetchall()
    cur.close()
    return posts

def update_user_profile(user_id, phone_number, bio):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET phone_number = %s, bio = %s WHERE id = %s", (phone_number, bio, user_id))
    mysql.connection.commit()
    cur.close()

def get_user_info(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT username, email, phone_number, bio FROM users WHERE id = %s", (user_id,))
    user_info = cur.fetchone()
    cur.close()
    if user_info:
        user_info_dict = {
            'username': user_info[0],
            'email': user_info[1],
            'phone_number': user_info[2],
            'bio': user_info[3]
        }
        return user_info_dict
    else:
        return None

def get_posts_except_user_with_username(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT posts.*, users.username FROM posts INNER JOIN users ON posts.user_id = users.id WHERE posts.user_id != %s", (user_id,))
    posts = cur.fetchall()
    cur.close()
    
    # Convert posts to list of dictionaries and add comments for each post
    posts_with_comments = []
    for post in posts:
        post_dict = {
            'id': post[0],
            'user_id': post[1],
            'content': post[2],
            'username': post[-1],
            'comments': get_comments(post[0])  # Get comments for this post
        }
        posts_with_comments.append(post_dict)
    
    return posts_with_comments

def perform_user_search(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT users.*, GROUP_CONCAT(posts.content SEPARATOR ' ') AS all_posts FROM users LEFT JOIN posts ON users.id = posts.user_id WHERE username LIKE %s GROUP BY users.id", ('%' + username + '%',))
    users_data = cur.fetchall()
    cur.close()
    return users_data

def add_comment(post_id, user_id, comment_text):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO comments (post_id, user_id, comment) VALUES (%s, %s, %s)",
                (post_id, user_id, comment_text))
    mysql.connection.commit()
    cur.close()

def get_comments(post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT comments.id, users.username, comments.comment FROM comments JOIN users ON comments.user_id = users.id WHERE post_id = %s ORDER BY comments.id ASC",
                (post_id,))
    comments = cur.fetchall()
    cur.close()
    
    # Convert to list of dictionaries for easier template access
    comments_list = []
    for comment in comments:
        likes, dislikes = get_comment_reactions(comment[0])
        comment_dict = {
            'id': comment[0],
            'user': comment[1],
            'content': comment[2],
            'likes': likes,
            'dislikes': dislikes
        }
        comments_list.append(comment_dict)
    
    return comments_list

def like_comment(comment_id, user_id):
    cur = mysql.connection.cursor()
    cur.execute("REPLACE INTO comment_likes_dislikes (comment_id, user_id, is_like) VALUES (%s, %s, 1)",
                (comment_id, user_id))
    mysql.connection.commit()
    cur.close()

def dislike_comment(comment_id, user_id):
    cur = mysql.connection.cursor()
    cur.execute("REPLACE INTO comment_likes_dislikes (comment_id, user_id, is_like) VALUES (%s, %s, 0)",
                (comment_id, user_id))
    mysql.connection.commit()
    cur.close()

def get_comment_reactions(comment_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT is_like, COUNT(*) FROM comment_likes_dislikes WHERE comment_id = %s GROUP BY is_like",
                (comment_id,))
    results = cur.fetchall()
    cur.close()
    likes = sum(count for is_like, count in results if is_like == 1)
    dislikes = sum(count for is_like, count in results if is_like == 0)
    return likes, dislikes

def like_post(post_id, user_id):
    cur = mysql.connection.cursor()
    cur.execute("REPLACE INTO likes_dislikes (post_id, user_id, is_like) VALUES (%s, %s, 1)",
                (post_id, user_id))
    mysql.connection.commit()
    cur.close()

def dislike_post(post_id, user_id):
    cur = mysql.connection.cursor()
    cur.execute("REPLACE INTO likes_dislikes (post_id, user_id, is_like) VALUES (%s, %s, 0)",
                (post_id, user_id))
    mysql.connection.commit()
    cur.close()

def get_post_reactions(post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT is_like, COUNT(*) FROM likes_dislikes WHERE post_id = %s GROUP BY is_like",
                (post_id,))
    results = cur.fetchall()
    cur.close()
    likes = sum(count for is_like, count in results if is_like == 1)
    dislikes = sum(count for is_like, count in results if is_like == 0)
    return likes, dislikes