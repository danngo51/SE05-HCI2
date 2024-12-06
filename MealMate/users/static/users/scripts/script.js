function addInputField() {
    const container = document.getElementById('input-list-container');
    const lastInput = container.querySelector('.input-container:last-child .health-input');

    // Validate the last input before adding a new one
    if (lastInput && lastInput.value.trim() === '') {
        const warningMessage = container.querySelector('.input-container:last-child .warning-message');
        warningMessage.textContent = "Please fill out this field before adding another.";
        return;
    }

    // Clear the warning message if the last input is valid
    if (lastInput) {
        const warningMessage = container.querySelector('.input-container:last-child .warning-message');
        warningMessage.textContent = "";
    }

    // Create a new input field with delete functionality
    const newInputContainer = document.createElement('div');
    newInputContainer.classList.add('input-container');
    newInputContainer.innerHTML = `
        <div class="input-wrapper">
            <input type="text" name="new_health_concerns[]" placeholder="Enter your health concerns." class="health-input">
            <button type="button" class="delete-button" onclick="deleteInputField(this)">×</button>
        </div>
        <p class="warning-message"></p>
    `;

    container.appendChild(newInputContainer);
}


function addInputFieldwoWarning(button) {
    const container = button.closest('.option-section').querySelector('.input-list-container');

    // Create a new input container
    const newInputContainer = document.createElement('div');
    newInputContainer.classList.add('input-container');

    // Add new input field with a delete button
    newInputContainer.innerHTML = `
        <div class="input-wrapper">
            <input type="text" placeholder="Enter your health concerns." class="health-input">
            <button type="button" class="delete-button" onclick="deleteInputField(this)">x</button>
        </div>
    `;

    // Insert the new input field above the Add button
    container.appendChild(newInputContainer);
}

// Function to delete an input field
function deleteInputField(button) {
    const inputContainer = button.closest('.input-container');
    inputContainer.remove();
}
