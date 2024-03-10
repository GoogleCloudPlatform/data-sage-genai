document.getElementById('chat-form').onsubmit = (e) => {
    e.preventDefault();

    const inputField = document.getElementById('chat-input');
    const userInput = inputField.value.trim();

    if(userInput) {
        // Send the userInput to your backend
        // Display it in chat, etc...
    }

    inputField.value = '';
};
