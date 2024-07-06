let currentUser = '';
const userImages = {
    'Ramy Rashad': 'ramy.jpg',
    'Ahmed Elgendy': 'gendy.jpg',
    'Abdelrahman Atef': 'atef.jpg',
    'Youssef Khaled': 'youssef.jpg',
    'Ziad Hany': 'ziad.jpg',
};

const chats = {
    'Ramy Rashad': [],
    'Ahmed Elgendy': [],
    'Abdelrahman Atef': [],
    'Youssef Khaled': [],
    'Ziad Hany': [],
};

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
            senderImage: 'saged.jpg',
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
