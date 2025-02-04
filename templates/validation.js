document.getElementById("botForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const bio = document.getElementById("bio").value;
    const tweet = document.getElementById("tweet").value;
    const resultDiv = document.getElementById("result");
    const invalidDiv = document.getElementById("invalid");
    const videoContainer = document.getElementById("videoContainer");
    const botVideo = document.getElementById("botVideo");
    const verify_container = document.getElementById("verify-container");
    const verified_user = document.getElementById("verified-user");
    const verified_bot = document.getElementById("verified-bot");
    const name = document.getElementById("name").value;
    const x = document.querySelector(".xClass");

    x.style.display = "none";
    resultDiv.textContent = "Checking...";
    resultDiv.classList.add("loading");
    invalidDiv.textContent = "Checking...";
    invalidDiv.classList.add("loading");

    try {
        // Check if user exists in the dataset
        const userResponse = await fetch('/get_user_info', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        const userData = await userResponse.json();

        if (!userResponse.ok || userData.status === "not found") {
            invalidDiv.textContent = "User not found ";
            invalidDiv.classList.add("error");
            document.getElementById("botForm").style.display = "block";
            return;
        }
        container.style.display = "none";  // Hide the form

        // Display user information if found
        document.getElementById("infoUsername").textContent = userData.username;
        document.getElementById("infoUserId").textContent = userData.user_id;
        document.getElementById("infoCreationDate").textContent = userData.creation_date;
        document.getElementById("infoFollowingCount").textContent = userData.following_count;
        document.getElementById("infoFollowerCount").textContent = userData.follower_count;
        document.getElementById("infoTweetTimeStamp").textContent = userData.tweet_timestamp;
        document.getElementById("infoLocation").textContent = userData.location;
        document.getElementById("userInfoContainer").style.display = "block";

        // Existing bot prediction logic
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bio, tweet })
        });

        if (!response.ok) {
            throw new Error("Server error: " + response.statusText);
        }

        const data = await response.json();
        resultDiv.classList.remove("loading");
        resultDiv.classList.remove("error");
        
        resultDiv.textContent = data.result;
        resultDiv.style.fontSize = "20px";
        resultDiv.style.fontWeight = "bold";
        resultDiv.style.fontFamily = "Arial, sans-serif";
        resultDiv.style.color = data.result === 'Spam Bot Detected' ? 'red' : 'green';

        // Play corresponding video based on prediction result
        videoContainer.style.display = "block";
        
        if (data.result === 'Spam Bot Detected') {
            botVideo.src = "{{ url_for('static', filename='Robotics.mp4') }}";
            verified_user.style.display = "none";
            verified.src="{{url_for('static', filename='unverified.gif') }}";

        } else {
            botVideo.src = "{{ url_for('static', filename='HumanVideo.mp4') }}";
            verified_bot.style.display = "none";
            verified_user.src="{{url_for('static', filename='verified.gif') }}";
        }
        botVideo.play();
    } catch (error) {
        resultDiv.classList.remove("loading");
        resultDiv.classList.add("error");
        resultDiv.textContent = "An error occurred: " + error.message;
    }
});
function goBack() {
            const formContainer = document.getElementById("container");
            const userInfoContainer = document.getElementById("userInfoContainer");
            const x = document.querySelector(".xClass");
            formContainer.style.display = "block";  // Show the form again
            userInfoContainer.style.display = "none";  // Hide the user info
            x.style.display = "block";  // Show the "X" button
        }
        document.addEventListener("DOMContentLoaded", function () {
    const labels = document.querySelectorAll("label");

    // Get the maximum label width and apply it to all labels
    let maxWidth = 0;
    labels.forEach(label => {
      const labelWidth = label.offsetWidth;
      if (labelWidth > maxWidth) {
        maxWidth = labelWidth;
      }
    });

    // Apply the max width to all labels for consistent alignment
    labels.forEach(label => {
      label.style.minWidth = maxWidth + "px";
    });
  });
      
