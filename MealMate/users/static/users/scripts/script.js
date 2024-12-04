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

document.addEventListener('DOMContentLoaded', function () {
    const saveInfoButton = document.getElementById('save-info-button');
    const profileInfoForm = document.getElementById('profile-info-form');

    saveInfoButton.addEventListener('click', function () {
        // Debug: Ensure the button is being clicked
        console.log('Save button clicked!');

        // Validate form inputs
        const email = document.getElementById('email').value.trim();
        const firstName = document.getElementById('first-name').value.trim();
        const lastName = document.getElementById('last-name').value.trim();

        // Debug: Check input values
        console.log(`Email: ${email}, First Name: ${firstName}, Last Name: ${lastName}`);

        if (!email || !firstName || !lastName) {
            alert('Please fill out all required fields.');
            return;
        }

        // Debug: Ensure form is being submitted
        console.log('Submitting the form...');
        profileInfoForm.submit();
    });
});


    // Change Password
    changePasswordButton.addEventListener('click', function () {
        // Validate password inputs
        const password = document.getElementById('password').value;
        const newPassword = document.getElementById('new-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        if (!password || !newPassword || !confirmPassword) {
            alert('Please fill out all password fields.');
            return;
        }

        if (newPassword !== confirmPassword) {
            alert('New passwords do not match.');
            return;
        }

        // Submit the password form
        passwordForm.submit();
    });
});
