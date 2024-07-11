let currentUser = '';
let userImages = {};  // Initialize as empty object
let chats = {};       // Initialize as empty object

// Fetch user images from Flask API
fetch('/api/user_images')
    .then(response => response.json())
    .then(data => {
        userImages = data;

        // After fetching user images, fetch chats for each user
        Object.keys(userImages).forEach(user => {
            fetchChats(user);
        });
    })
    .catch(error => console.error('Error fetching user images:', error));

// Function to fetch chats for a specific user from Flask API
function fetchChats(user) {
    fetch(`/api/chats/${user}`)
        .then(response => response.json())
        .then(data => {
            chats[user] = data;
        })
        .catch(error => console.error(`Error fetching chats for ${user}:`, error));
}

// Request notification permission
Notification.requestPermission().then(function(result) {
    console.log('Notification permission:', result);
});

function openChat(user, userImage) {
    currentUser = user;
    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML = '';

    chats[user].forEach(message => {
        appendMessage(message.text, message.sender, message.senderImage);
    });
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const messageText = messageInput.value.trim();
    if (messageText !== '' && currentUser !== '') {
        const message = {
            text: messageText,
            sender: 'Saged Ryan',
            senderImage: 'static/saged.jpg',
        };
        appendMessage(message.text, message.sender, message.senderImage);
        notifyUser(currentUser); // Notify the recipient
        chats[currentUser].push(message);
        messageInput.value = '';
    }
}

function appendMessage(message, sender, senderImage) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');

    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');

    const imageElement = document.createElement('img');
    imageElement.src = senderImage;
    imageElement.alt = sender;
    imageElement.classList.add('user-img');

    const messageTextElement = document.createElement('p');
    messageTextElement.textContent = message;

    messageContent.appendChild(imageElement);
    messageContent.appendChild(messageTextElement);
    messageElement.appendChild(messageContent);

    const messagesContainer = document.getElementById('messages');
    if (sender === 'Saged Ryan') {
        messageElement.classList.add('my-message');
        messagesContainer.appendChild(messageElement);
    } else {
        messageElement.classList.add('reply-message');
        messagesContainer.appendChild(messageElement);
    }
}

function notifyUser(sender) {
    if (Notification.permission === 'granted') {
        const notification = new Notification('New Message', {
            body: `You have a new message from ${sender}`,
            icon: 'saged.jpg' // Replace with your profile image or any other icon
        });
    }
}
