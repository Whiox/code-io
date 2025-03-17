document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".star").forEach(function (star) {
        star.addEventListener("click", function () {
            let courseId = this.dataset.courseId;
            let img = this;

            fetch(`/courses/add-star/${courseId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status) {
                    img.src = "/static/assets/star-fill.png";
                } else {
                    img.src = "/static/assets/star-empty.svg";
                }
            });
        });
    });
});

function getCSRFToken() {
    return document.cookie.split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
}

