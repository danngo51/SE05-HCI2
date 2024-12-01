function navigateTo(page) {
    window.location.href = page;
}

function addInputField() {
    const container = document.getElementById('input-list-container');
    const lastInput = container.lastElementChild.querySelector('.health-input');
    const warningMessage = container.lastElementChild.querySelector('.warning-message');

    // Check if the last input is empty
    if (lastInput.value.trim() === '') {
        warningMessage.textContent = "Please fill out this field before adding another.";
        return;
    }

    // Clear the warning message
    warningMessage.textContent = "";

    // Create a new input container
    const newInputContainer = document.createElement('div');
    newInputContainer.classList.add('input-container');

    // Add new input field with a delete button
    newInputContainer.innerHTML = `
        <div class="input-wrapper">
            <input type="text" placeholder="Enter your health concerns." class="health-input">
            <button type="button" class="delete-button" onclick="deleteInputField(this)">x</button>
        </div>
        <p class="warning-message"></p>
    `;

    // Insert the new input field above the Add button
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

function setActiveDot(currentPageIndex) {
    const dots = document.querySelectorAll('.page-dots .dot');
    dots.forEach((dot, index) => {
        if (index === currentPageIndex) {
            dot.classList.add('active');
        } else {
            dot.classList.remove('active');
        }
    });
}


function validateInputs(event) {
    event.preventDefault(); // Prevent default anchor behavior

    let allValid = true;

    // Check if the page contains text inputs
    const inputList = document.querySelectorAll('.health-input');
    inputList.forEach(input => {
        const warningMessage = input.closest('.input-container').querySelector('.warning-message');

        if (input.value.trim() === '') {
            warningMessage.textContent = "This field cannot be empty.";
            allValid = false; // Set validation to false if any input is empty
        } else {
            warningMessage.textContent = ""; // Clear warning message if input is valid
        }
    });

    // Check if the page contains radio buttons
    const radioInputs = document.querySelectorAll('input[name="budget"]');
    if (radioInputs.length > 0) {
        const radioWarningMessage = document.querySelector('.radio-warning-message');
        const selectedRadio = document.querySelector('input[name="budget"]:checked');

        if (!selectedRadio) {
            radioWarningMessage.textContent = "Please select a budget option.";
            radioWarningMessage.style.color = "red";
            allValid = false;
        } else {
            radioWarningMessage.textContent = "";
        }
    }

    // Navigate only if all inputs are valid
    if (allValid) {
        const nextButton = event.target;
        const nextUrl = nextButton.getAttribute('data-next-url');
        if (nextUrl) {
            window.location.href = nextUrl;
        }
    }
}