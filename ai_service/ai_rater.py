import os
import time
import random
from flask import Flask, request, jsonify

# Flask application setup
app = Flask(__name__)

# Define the possible, random ratings
POSSIBLE_SCORES = list(range(1, 6)) # [1, 2, 3, 4, 5]
POSSIBLE_RATINGS = ["G", "PG", "NSFW"]

# Mock AI Service: The Black Box
@app.route('/rate_joke', methods=['POST'])
def rate_joke():
    """
    Mocks an AI service call. It expects a JSON body with a 'joke_text' field
    and returns a random rating and score for the joke.
    """
    
    # 1. Enforce content type
    if not request.is_json:
        # 400 Bad Request
        return jsonify({"error": "Request must contain JSON payload."}), 400

    data = request.get_json()
    # Accept either 'joke_text' or 'body' to be compatible with the main app
    joke_text = data.get('joke_text') or data.get('body') or 'No joke provided'

    # Simulate network/processing latency to be more realistic
    time.sleep(0.05) 

    # --- NEW RANDOM LOGIC ---
    # Randomly select a score (1-5) and a rating (G, PG, NSFW)
    random_score = random.choice(POSSIBLE_SCORES)
    random_rating = random.choice(POSSIBLE_RATINGS)
    # -------------------------

    # Log the request details for debugging in the Docker logs
    print(f"--- Mock AI Service received request from client ---")
    print(f"--- Joke: '{joke_text[:75]}{'...' if len(joke_text) > 75 else ''}'")

    # 2. Mock AI Logic: Return a consistent result for deterministic testing
    mock_rating = {
        "score": random_score,  # Random 1-5
        "rating": random_rating, # Random G, PG, or NSFW (new key: 'rating')
        "analysis": f"AI decided: Score {random_score} and Rating {random_rating}. Integration successful!"
    }

    # 3. Return the rating as JSON
    # 200 OK
    return jsonify(mock_rating), 200

# The service listens on port 5002 internally (app.run below).
# Docker Compose service name `ai-service` will be used by the web container
# to reach this service at `http://ai-service:5002`.
if __name__ == '__main__':
    # Use 0.0.0.0 for access within the Docker network
    app.run(debug=False, host='0.0.0.0', port=5002)
