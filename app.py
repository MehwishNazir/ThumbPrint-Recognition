import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session
from User import User
from DBHandler import DBHandler

app = Flask(__name__)
app.secret_key = 'abc123'

def perform_fingerprint_matching(user_uploaded_file):
    file_content = user_uploaded_file.read()
    nparr = np.frombuffer(file_content, np.uint8)
    sample = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    best_score = 0
    filename = None
    image = None
    kp1, kp2, mp = None, None, None

    # Read the user uploaded fingerprint image and convert it to a NumPy array
    for file in [file for file in os.listdir("SOCOFing/Real")][:1000]:
        # Read the fingerprint image from the "SOCOFing\\Real" directory
        fingerprint_image = cv2.imread("SOCOFing/Real/" + file)
        sift = cv2.SIFT_create()

        keypoints_1, descriptors_1 = sift.detectAndCompute(sample, None)
        keypoints_2, descriptors_2 = sift.detectAndCompute(fingerprint_image, None)

        matches = cv2.FlannBasedMatcher({'algorithm': 1, 'trees': 10}, {}).knnMatch(descriptors_1, descriptors_2, k=2)
        # Perform ratio test on matches
        good_matches = []
        for p, q in matches:
            if p.distance < 0.7 * q.distance:
                good_matches.append(p)

        # Calculate the matching score
        matching_score = len(good_matches) / max(len(keypoints_1), len(keypoints_2)) * 100

        # Update best match if a better match is found
        if matching_score > best_score:
            best_score = matching_score
            filename = file
            image = fingerprint_image
            kp1, kp2, mp = keypoints_1, keypoints_2, good_matches

    if best_score > 0:
        result = cv2.drawMatches(sample, kp1, image, kp2, mp, None)
        result = cv2.resize(result, None, fx=4, fy=4)

        # Save the result image to a file
        result_filename = "result_image.jpg"
        cv2.imwrite(os.path.join("static", result_filename), result)

        return result_filename, result, filename, best_score
    else:
        return None, None, None, None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        usr = User(username, password)
        hdlr = DBHandler("localhost", "root", "333", "fingerprint_recognition_system")
        flag = hdlr.login(usr)
        if flag:
            session['logged_in'] = True
            return render_template("index.html")
        else:
            session['logged_in'] = False
            message = "Login failed"
            return render_template("login.html", message=message)

    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            result_filename, result, filename, score = perform_fingerprint_matching(file)
            if result_filename is not None:
                return render_template('result.html', result_filename=result_filename, result=result, filename=filename, score=score)
            else:
                message = "No match found or image not found"
                return render_template('index.html', message=message)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
