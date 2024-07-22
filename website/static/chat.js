let currentUser = '';
let currentUserId = '';
let userImages = {};  // Initialize as empty object
let chats = {};       // Initialize as empty object

// Request notification permission on page load
Notification.requestPermission().then(function(result) {
    console.log('Notification permission:', result);
    if (result === 'granted') {
        console.log('Notification permission granted.');
    } else {
        console.log('Notification permission denied.');
    }
});



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
            fetchChats(userId);  // Fetch initially
        });
        setInterval(() => {
            if (currentUserId) {
                fetchChats(currentUserId);
            }
        }, 1000);  // Fetch every second
    })
    .catch(error => console.error('Error fetching user images:', error));



// Function to fetch chats for a specific user from Flask API
function fetchChats(userId) {
    console.log(`Fetching chats for userId: ${userId}`);
    fetch(`/api/chats/${userId}`)
        .then(response => response.json())
        .then(data => {
            console.log(`Chats fetched for userId: ${userId}`, data);
            if (!chats[userId]) {
                chats[userId] = [];
            }

            // Check for new messages
            const newMessages = data.filter(message => !chats[userId].some(existingMessage => existingMessage.message === message.message));

            // Store messages in chats object
            chats[userId] = data;

            // Notify user only if there are new messages
            if (newMessages.length > 0) {
                console.log(`Notifying user about new message from senderId: ${newMessages[newMessages.length - 1].sender_id}`);
                notifyUser(newMessages[newMessages.length - 1].sender_id);  // Notify with the sender of the latest new message
            }

            // Update the chat display if it's the current user's chat
            if (userId === currentUserId) {
                updateChatDisplay(false);  // Update the display if it's the current user's chat
            }
        })
        .catch(error => console.error(`Error fetching chats for user ${userId}:`, error));
}




document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('messageInput');

    // Adjust textarea height dynamically on input
    messageInput.addEventListener('input', () => {
        adjustTextareaHeight(messageInput);
    });

    // Allow Enter key to create new lines and adjust height
    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Prevent default Enter key behavior (submitting form or creating new line)
            sendMessage(); // Call sendMessage function
        }
    });

});

function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto'; // Reset height to auto to calculate the correct scrollHeight
    textarea.style.height = textarea.scrollHeight + 'px'; // Set the height to the scrollHeight
}

function updateChatDisplay(shouldScroll = false) {
    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML = '';

    if (chats[currentUserId]) {
        chats[currentUserId].forEach(chat => {
            const sender = chat.sender_id === currentUserId ? currentUser : 'Me';
            const senderImage = userImages[sender];
            appendMessage(chat.message, sender, senderImage);
        });
    }

    // Scroll to the bottom of the messages container if shouldScroll is true
    if (shouldScroll) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}


function openChat(user, userId) {
    currentUser = user;
    currentUserId = userId;
    updateChatDisplay(true);  // Pass true to scroll to the bottom
}


function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    let messageText = messageInput.value.trim();
    messageText = messageText.replace(/\n/g, '<br>');
    if (messageText !== '' && currentUser !== '') {
        const senderImage = userImages[currentUserId] ? `/user_images/${currentUserId}` : '';

        // Insert newline characters (\n) every 50 characters for display
        const chunkSize = 50;
        let chunkedMessage = '';
        for (let i = 0; i < messageText.length; i += chunkSize) {
            chunkedMessage += messageText.substr(i, chunkSize) + '\n';
        }

        // Update the message display in real-time
        //updateMessageDisplay(chunkedMessage);
        chunkedMessage = chunkedMessage.replace(/\n/g, '<br>');
        // Send the chunked message to the backend
        fetch(`/api/chats`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                receiver_id: currentUserId,
                message: chunkedMessage,
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
                    message: chunkedMessage,
                    sender_id: currentUser.id,
                    receiver_id: currentUserId,
                    timestamp: new Date()  // Use current date as timestamp
                });
                appendMessage(chunkedMessage, 'Me', senderImage);  // Ensure message is appended correctly
                const messagesContainer = document.getElementById('messages');
                //messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else {
                console.error('Error sending message:', data.error);
            }
        })
        .catch(error => console.error('Error sending message:', error));

        // Clear input after sending
        messageInput.value = '';
        adjustTextareaHeight(messageInput);
    }
}

// Function to update message display in real-time
function updateMessageDisplay(message) {
    const messagesContainer = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', 'my-message');

    // Replace \n characters with <br> tags for HTML display
    messageElement.innerHTML = message.replace(/\n/g, '<br>');

    messagesContainer.appendChild(messageElement);
}

function appendMessage(message, sender, senderImage) {
    const messagesContainer = document.getElementById('messages');

    // Create message container
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');

    // Determine message sender
    const isMe = sender === 'Me';

    // Create message content container
    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');
    messageContent.innerHTML = message; // Use innerHTML to interpret <br> tags

    // Append message content to message element
    messageElement.appendChild(messageContent);

    // Apply styles based on sender
    if (isMe) {
        messageElement.classList.add('my-message');
    } else {
        messageElement.classList.add('reply-message');
    }

    // Append message element to messages container
    messagesContainer.appendChild(messageElement);

    // Scroll to the bottom of the messages container
    //messagesContainer.scrollTop = messagesContainer.scrollHeight;
}


function notifyUser(senderId) {
    const sender = senderId === currentUserId ? currentUser : 'Someone'; // Replace 'Someone' with appropriate logic to fetch sender's name
    if (Notification.permission === 'granted') {
        console.log(`Creating notification for senderId: ${senderId}, sender: ${sender}`);
        try {
            const notification = new Notification('New Message', {
                body: `You have a new message from ${sender}`,
                icon: userImages[senderId] ? `/user_images/${senderId}` : '', // Use sender's image URL if available
            });

            // Add event listener to notification for additional debugging
            notification.onclick = () => {
                console.log('Notification clicked');
            };

            // Add an error listener to catch issues with the notification
            notification.onerror = (error) => {
                console.error('Notification error:', error);
            };
        } catch (error) {
            console.error('Error creating notification:', error);
        }
    } else {
        console.log('Notification permission not granted or denied');
    }
}







