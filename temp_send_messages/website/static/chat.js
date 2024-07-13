let currentUser = '';
let currentUserId = '';
let userImages = {};  // Initialize as empty object
let chats = {};       // Initialize as empty object

// Fetch user images from Flask API
fetch('/api/user_images')
    .then(response => response.json())
    .then(data => {
        userImages = data;

        // Log IDs and image URLs for all users
        console.log('User IDs and Image URLs:');
        Object.keys(userImages).forEach(userId => {
            console.log(`User ID: ${userId}, Image URL: ${userImages[userId]}`);
        });

        // After fetching user images, fetch chats for each user
        Object.keys(userImages).forEach(userId => {
            fetchChats(userId);  // Update to pass userId instead of userImages[user]
        });
    })
    .catch(error => console.error('Error fetching user images:', error));

// Function to fetch chats for a specific user from Flask API
function fetchChats(userId) {
    fetch(`/api/chats/${userId}`)
        .then(response => response.json())
        .then(data => {
            chats[userId] = data;  // Store messages in chats object
        })
        .catch(error => console.error(`Error fetching chats for user ${userId}:`, error));
}


// Request notification permission
Notification.requestPermission().then(function(result) {
    console.log('Notification permission:', result);
});

function openChat(user, userId) {
    currentUser = user;
    currentUserId = userId;
    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML = '';

    // Display stored messages if available
    if (chats[currentUserId]) {
        chats[currentUserId].forEach(chat => {
            const sender = chat.sender_id === currentUserId ? currentUser : 'Me';
            const senderImage = userImages[sender];
            appendMessage(chat.message, sender, senderImage);
        });
    } else {
        // Fetch messages for the selected user from the backend if not already stored
        fetch(`/api/chats/${userId}`)
            .then(response => response.json())
            .then(data => {
                chats[currentUserId] = data;
                data.forEach(chat => {
                    const sender = chat.sender_id === currentUserId ? currentUser : 'Me';
                    const senderImage = userImages[sender];
                    appendMessage(chat.message, sender, senderImage);
                });
            })
            .catch(error => console.error(`Error fetching chats for user ${userId}:`, error));
    }
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const messageText = messageInput.value.trim();

    if (messageText !== '' && currentUser !== '') {
        const senderImage = userImages[currentUserId] ? `/user_images/${currentUserId}` : '';

        // Send the message to the backend
        fetch(`/api/chats`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                receiver_id: currentUserId,
                message: messageText,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Message sent successfully');
                // Store the new message in chats object
                if (!chats[currentUserId]) {
                    chats[currentUserId] = [];
                }
                chats[currentUserId].push({
                    message: messageText,
                    sender_id: currentUser.id,
                    receiver_id: currentUserId,
                    timestamp: new Date()  // Use current date as timestamp
                });
                appendMessage(messageText, 'Me', senderImage);  // Ensure message is appended correctly
            } else {
                console.error('Error sending message:', data.error);
            }
        })
        .catch(error => console.error('Error sending message:', error));

        // Clear input after sending
        messageInput.value = '';
    }
}

function appendMessage(message, sender, senderImage) {
    console.log('Sender Image:', senderImage); // Debugging line

    const messageElement = document.createElement('div');
    messageElement.classList.add('message');

    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');

    const imageElement = document.createElement('img');
    imageElement.alt = sender;
    imageElement.classList.add('user-img');

    // Check if senderImage is defined and not empty before setting src
    if (senderImage && senderImage !== '') {
        imageElement.src = senderImage;
    } else {
        imageElement.src = 'static/default.jpg'; // Set a default image if senderImage is undefined or empty
    }

    const messageTextElement = document.createElement('p');
    messageTextElement.textContent = message;

    messageContent.appendChild(imageElement);
    messageContent.appendChild(messageTextElement);
    messageElement.appendChild(messageContent);

    const messagesContainer = document.getElementById('messages');
    if (sender === 'Me') {
        messageElement.classList.add('my-message');
    } else {
        messageElement.classList.add('reply-message');
    }

    messagesContainer.appendChild(messageElement);
}



function notifyUser(sender) {
    if (Notification.permission === 'granted') {
        const notification = new Notification('New Message', {
            body: `You have a new message from ${sender}`,
            icon: userImages[currentUserId] ? `/user_images/${currentUserId}` : '', // Ensure senderImage is not empty
        });
    }
}
