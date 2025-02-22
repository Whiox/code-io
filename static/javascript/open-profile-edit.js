document.addEventListener('DOMContentLoaded', function () {
    const editButton = document.querySelector('#edit-profile');
    const modal = document.querySelector('#edit-profile-modal');
    const closeButton = document.querySelector('.modal .close');

    if (editButton && modal) {
        editButton.addEventListener('click', function () {
            modal.style.display = 'flex';
        });

        closeButton.addEventListener('click', function () {
            modal.style.display = 'none';
        });

        window.addEventListener('click', function (event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
});
