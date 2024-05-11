// Copyright 2024 Google LLC
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//  https://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("chat-form").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the form from submitting via HTTP
    let userInput = document.getElementById("chat-input");
    let message = userInput.value.trim();


    if (message) {
      addMessage("user", message);
      fetch("/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: message }),
      })
      .then(response => response.json())
      .then(data => {
        if (data.response) { // Handle response based on updated Flask app structure
          addMessage("bot", data.response.replace(/\*\*/g, '')); // Display bot response without asterisks
        } else {
          addMessage("bot", "Sorry, I couldn't process that."); // Fallback message
        }
      })
      .catch(error => {
        console.error("Error:", error);
        addMessage("bot", "An error occurred."); // Show error message in chat
      });
    }
    userInput.value = ""; // Clear input field after sending
  });
});


function addMessage(sender, message) {
  let chatBox = document.getElementById("chat-box");
  let containerDiv = document.createElement("div");
  containerDiv.classList.add(`${sender}-container`);


  let label = document.createElement("div");
  label.textContent = sender.charAt(0).toUpperCase() + sender.slice(1) + ":";
  label.classList.add("label");


  let messageDiv = document.createElement("div");
  messageDiv.classList.add("message", `${sender}-message`);


  // Handle new lines and bullet points
  const lines = message.split('\n');
  const formattedMessage = document.createDocumentFragment();


  lines.forEach((line) => {
    if (line.trim().startsWith('*')) {
      const bulletPointText = line.trim().substring(1).trim().replace(/\*\*/g, ''); // remove the asterisks
      const bulletPoint = document.createElement('li');
      bulletPoint.textContent = bulletPointText;
      formattedMessage.appendChild(bulletPoint);
    } else {
      const textNode = document.createTextNode(line.replace(/\*\*/g, '')); // remove the asterisks
      formattedMessage.appendChild(textNode);
    }
    formattedMessage.appendChild(document.createElement('br'));
  });


  // Check if any bullet points exist
  if (formattedMessage.querySelector('li')) {
    const ul = document.createElement('ul');
    ul.appendChild(formattedMessage);
    messageDiv.appendChild(ul);
  } else {
    messageDiv.appendChild(formattedMessage);
  }


  containerDiv.appendChild(label);
  containerDiv.appendChild(messageDiv);
  chatBox.appendChild(containerDiv);
  chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom
}

