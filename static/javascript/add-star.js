document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".star").forEach(function (star) {
        star.addEventListener("click", function () {
            let courseId = this.dataset.courseId;
            let img = this;

            fetch(`/courses/add-star/${courseId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
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

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
