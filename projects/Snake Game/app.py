from flask import Flask, jsonify, request, render_template
import sqlite3

# Initialize the Flask application
app = Flask(__name__)

# Initialize the database with the 'scores' table if it doesn't exist
def init_db():
    """
    Creates the 'scores' table in the SQLite database if it doesn't already exist.
    The table contains the columns:
        - id: The primary key, automatically incremented.
        - name: The name of the player (text).
        - score: The score achieved by the player (integer).
        - timestamp: The timestamp of when the score was recorded (default is the current timestamp).
    """
    conn = sqlite3.connect('scores.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        score INTEGER NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
    conn.commit()
    conn.close()

# Route for the main game page
@app.route('/')
def index():
    """
    Renders the game page where players can submit their scores.
    """
    return render_template('game.html')

# Route for the leaderboard page, showing the top scores
@app.route('/leaderboard')
def leaderboard():
    """
    Renders the leaderboard page, displaying the top 10 scores from the database.
    The scores are ordered in descending order by score.
    """
    try:
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, score, timestamp FROM scores ORDER BY score DESC LIMIT 10")
        scores = cursor.fetchall()
        conn.close()

        # Pass the top scores to the leaderboard template
        return render_template('leaderboard.html', scores=scores)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        # In case of error, render the leaderboard with an empty list
        return render_template('leaderboard.html', scores=[])

# Route to submit a player's score
@app.route('/submit_score', methods=['POST'])
def submit_score():
    """
    Accepts a POST request containing a player's score and name (in JSON format).
    The score is saved to the database, and a success or error message is returned.
    """
    data = request.json
    name = data.get('name', 'Anonymous')  # Default to 'Anonymous' if no name is provided
    score = data.get('score', 0)

    try:
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO scores (name, score) VALUES (?, ?)', (name, score))
        conn.commit()
        conn.close()

        # Return a success message with a 201 status code
        return jsonify({'message': 'Score submitted successfully'}), 201

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        # In case of error, return an error message with a 500 status code
        return jsonify({'error': 'Failed to submit score'}), 500

# Route to get the top 10 scores in JSON format
@app.route('/get_scores', methods=['GET'])
def get_scores():
    """
    Retrieves the top 10 scores from the database and returns them as a JSON response.
    Each score includes the player's name, score, and timestamp.
    """
    try:
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, score, timestamp FROM scores ORDER BY score DESC LIMIT 10')
        scores = cursor.fetchall()
        conn.close()

        # Format the rows into a list of dictionaries suitable for JSON response
        formatted_scores = [{'name': row[0], 'score': row[1], 'timestamp': row[2]} for row in scores]
        return jsonify(formatted_scores)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        # In case of error, return an error message with a 500 status code
        return jsonify({'error': 'Failed to retrieve scores'}), 500

# Run the Flask app
if __name__ == '__main__':
    init_db()  # Initialize the database when starting the application
    app.run(debug=True)
