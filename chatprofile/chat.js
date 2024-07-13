// Notification permission request
Notification.requestPermission().then(function(result) {
  console.log('Notification permission:', result);
});

// Function to notify user of new message
function notifyUser(sender) {
  if (Notification.permission === 'granted') {
    const notification = new Notification('New Message', {
      body: `You have a new message from ${sender}`,
      icon: 'saged.jpg' // Replace with your profile image or any other icon
    });
  }
}

// Function to open profile settings modal
function openProfileSettings() {
  var modal = document.getElementById('profileSettingsModal');
  modal.style.display = 'block';
}

// Function to close profile settings modal
function closeProfileSettings() {
  var modal = document.getElementById('profileSettingsModal');
  modal.style.display = 'none';
}

// Function to open friends list modal
function openFriendsList() {
  var modal = document.getElementById('friendsListModal');
  modal.style.display = 'block';
}

// Function to close friends list modal
function closeFriendsList() {
  var modal = document.getElementById('friendsListModal');
  modal.style.display = 'none';
}

// Function to block user
function blockUser() {
  var modal = document.getElementById('confirmationModal');
  modal.style.display = 'block';
}

// Function to close confirmation modal
function closeConfirmation() {
  var modal = document.getElementById('confirmationModal');
  modal.style.display = 'none';
}

// Function to confirm blocking user
function confirmBlock() {
  var modal = document.getElementById('confirmationModal');
  modal.style.display = 'none';
  alert('User blocked successfully!'); // Replace with actual blocking logic
}

// Function to open delete chat confirmation modal
function confirmDeleteChat() {
  var modal = document.getElementById('deleteChatModal');
  modal.style.display = 'block';
}

// Function to close delete chat confirmation modal
function closeDeleteChatConfirmation() {
  var modal = document.getElementById('deleteChatModal');
  modal.style.display = 'none';
}

// Dummy function for opening chat, replace with actual functionality
function openChat(user, userImage) {
  const chatWindow = document.getElementById('messages');
  chatWindow.innerHTML = `<h3>Chat with ${user}</h3>`;
  closeFriendsList(); // Close friends list modal after selecting a user
}

// Dummy function for sending message, replace with actual functionality
function sendMessage() {
  const messageInput = document.getElementById('messageInput');
  const message = messageInput.value.trim();

  if (message !== '') {
    const chatWindow = document.getElementById('messages');
    const newMessage = document.createElement('div');
    newMessage.classList.add('message', 'my-message');
    newMessage.innerHTML = `
      <div class="message-content">
        <img src="saged.jpg" alt="Saged Ryan" class="user-img">
        <p>${message}</p>
      </div>`;

    chatWindow.appendChild(newMessage);
    messageInput.value = '';

    // Notify user of new message
    notifyUser('Sender');
  }
}

// Close the modal if the user clicks outside of it
window.onclick = function(event) {
  var modals = document.getElementsByClassName('modal');
  for (var i = 0; i < modals.length; i++) {
    if (event.target == modals[i]) {
      modals[i].style.display = 'none';
    }
  }
};
